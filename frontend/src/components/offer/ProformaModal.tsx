/**
 * ProformaModal — generate proforma or VAT invoice in Fakturownia from selected offer sets.
 * Two invoice kinds: proforma / vat. Two position modes: Szczegółowe / Marketing.
 */

import { useState, useEffect } from 'react';
import { useOfferStore } from '@/store/offerStore';
import { generateProforma, generateVat } from '@/api/offerClient';
import type { OfferSetData } from '@/types/offer';

interface Props {
  open: boolean;
  onClose: () => void;
}

interface ProformaResult {
  invoice_id: string;
  invoice_number: string;
  pdf_url: string;
  view_url: string;
  total_net: number;
  total_gross: number;
}

type Step = 'config' | 'sending' | 'success' | 'error';

export default function ProformaModal({ open, onClose }: Props) {
  const { offer } = useOfferStore();

  const [selectedSetIds, setSelectedSetIds] = useState<string[]>([]);
  const [invoiceKind, setInvoiceKind] = useState<'proforma' | 'vat'>('proforma');
  const [asMarketing, setAsMarketing] = useState(false);
  const [paymentDays, setPaymentDays] = useState(14);
  const [notes, setNotes] = useState('');
  const [step, setStep] = useState<Step>('config');
  const [result, setResult] = useState<ProformaResult | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Reset on open
  useEffect(() => {
    if (open && offer) {
      const allIds = offer.sets.map(s => s.id!).filter(Boolean);
      setSelectedSetIds(allIds);
      setInvoiceKind('proforma');
      setAsMarketing(false);
      setPaymentDays(14);
      setNotes('');
      setStep('config');
      setResult(null);
      setErrorMsg('');
    }
  }, [open, offer]);

  // VAT defaults to marketing mode
  useEffect(() => { if (invoiceKind === 'vat') setAsMarketing(true); }, [invoiceKind]);

  if (!open || !offer) return null;

  const toggleSet = (id: string) => {
    setSelectedSetIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const selectedTotal = offer.sets
    .filter(s => s.id && selectedSetIds.includes(s.id))
    .reduce((sum, s) => sum + s.total_price, 0);

  const handleGenerate = async () => {
    if (selectedSetIds.length === 0) return;
    setStep('sending');
    try {
      const payload = {
        set_ids: selectedSetIds,
        as_marketing: asMarketing,
        payment_days: paymentDays,
        notes: notes || undefined,
      };
      const { data } = invoiceKind === 'vat'
        ? await generateVat(offer.id, payload)
        : await generateProforma(offer.id, payload);
      setResult(data);
      setStep('success');
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || 'Nieznany błąd';
      setErrorMsg(msg);
      setStep('error');
    }
  };

  const kindLabel = invoiceKind === 'vat' ? 'Faktura VAT' : 'Proforma';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40" />
      <div
        className="relative bg-white rounded-2xl shadow-2xl w-[560px] max-h-[90vh] overflow-y-auto p-6"
        onClick={e => e.stopPropagation()}
      >
        {/* ─── CONFIG STEP ─── */}
        {step === 'config' && (
          <>
            <h3 className="font-bold text-lg mb-1">Generuj dokument w Fakturowni</h3>
            <div className="flex gap-2 mb-4">
              <button onClick={() => setInvoiceKind('proforma')} className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${invoiceKind === 'proforma' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'}`}>Proforma</button>
              <button onClick={() => setInvoiceKind('vat')} className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${invoiceKind === 'vat' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>Faktura VAT</button>
            </div>

            {/* Set selection */}
            <div className="mb-4">
              <label className="text-xs font-medium text-gray-500 block mb-2">
                Zestawy do uwzględnienia
              </label>
              <div className="space-y-1.5">
                {offer.sets.map((s: OfferSetData) => (
                  <button
                    key={s.id}
                    onClick={() => s.id && toggleSet(s.id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg border text-sm transition-all ${
                      s.id && selectedSetIds.includes(s.id)
                        ? 'border-amber-400 bg-amber-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                        s.id && selectedSetIds.includes(s.id)
                          ? 'border-amber-500 bg-amber-500'
                          : 'border-gray-300'
                      }`}>
                        {s.id && selectedSetIds.includes(s.id) && (
                          <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </div>
                      <span className="font-medium">{s.name}</span>
                      <span className="text-[10px] text-gray-400">{s.items.length} poz.</span>
                    </div>
                    <span className="font-bold text-gray-700">{s.total_price.toFixed(2)} zł</span>
                  </button>
                ))}
              </div>
              {selectedSetIds.length > 0 && (
                <div className="text-right text-xs text-gray-500 mt-1">
                  Razem netto: <span className="font-bold text-gray-800">{selectedTotal.toFixed(2)} zł</span>
                  {' '}x {offer.quantity} szt.
                </div>
              )}
            </div>

            {/* Mode toggle */}
            <div className="mb-4">
              <label className="text-xs font-medium text-gray-500 block mb-2">
                Tryb pozycji na fakturze
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setAsMarketing(false)}
                  className={`px-3 py-2.5 rounded-lg border-2 text-sm text-left transition-all ${
                    !asMarketing
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                      : 'border-gray-200 text-gray-600 hover:border-gray-300'
                  }`}
                >
                  <div className="font-bold">Szczegółowe</div>
                  <div className="text-[11px] opacity-70">Każdy produkt osobno</div>
                </button>
                <button
                  onClick={() => setAsMarketing(true)}
                  className={`px-3 py-2.5 rounded-lg border-2 text-sm text-left transition-all ${
                    asMarketing
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                      : 'border-gray-200 text-gray-600 hover:border-gray-300'
                  }`}
                >
                  <div className="font-bold">Marketing</div>
                  <div className="text-[11px] opacity-70">Jedna pozycja zbiorcza</div>
                </button>
              </div>
            </div>

            {/* Payment + Notes */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">
                  Termin płatności (dni)
                </label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-indigo-400 outline-none"
                  value={paymentDays}
                  onChange={e => setPaymentDays(Number(e.target.value) || 14)}
                  min={1}
                  max={90}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">
                  Notatka (opcjonalnie)
                </label>
                <input
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-indigo-400 outline-none"
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  placeholder="np. rabat 10%"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-2 mt-2">
              <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm text-gray-500">
                Anuluj
              </button>
              <button
                disabled={selectedSetIds.length === 0}
                onClick={handleGenerate}
                className={`px-5 py-2.5 rounded-lg text-sm font-bold text-white ${
                  selectedSetIds.length === 0 ? 'bg-gray-300' : 'bg-amber-600 hover:bg-amber-700'
                }`}
              >
                Generuj {kindLabel.toLowerCase()}
              </button>
            </div>
          </>
        )}

        {/* ─── SENDING ─── */}
        {step === 'sending' && (
          <div className="py-12 text-center">
            <div className="inline-block w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mb-4" />
            <div className="font-bold text-gray-900">Generuję {kindLabel.toLowerCase()}...</div>
            <div className="text-sm text-gray-500 mt-1">Wysyłam dane do Fakturowni</div>
          </div>
        )}

        {/* ─── SUCCESS ─── */}
        {step === 'success' && result && (
          <div className="py-6">
            <div className="text-center mb-5">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-green-100 mb-3">
                <svg className="w-7 h-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="font-bold text-lg text-gray-900">{kindLabel} wygenerowana</h3>
              <p className="text-sm text-gray-500 mt-1">{result.invoice_number}</p>
            </div>

            <div className="bg-gray-50 rounded-xl p-4 mb-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Netto</span>
                <span className="font-bold">{result.total_net.toFixed(2)} zł</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Brutto</span>
                <span className="font-bold">{result.total_gross.toFixed(2)} zł</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 mb-4">
              <a
                href={result.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg text-sm font-bold hover:bg-gray-800"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Pobierz PDF
              </a>
              <a
                href={result.view_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 px-4 py-2.5 bg-amber-600 text-white rounded-lg text-sm font-bold hover:bg-amber-700"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Otwórz w Fakturowni
              </a>
            </div>

            <div className="flex justify-end">
              <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900">
                Zamknij
              </button>
            </div>
          </div>
        )}

        {/* ─── ERROR ─── */}
        {step === 'error' && (
          <div className="py-6">
            <div className="text-center mb-5">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-red-100 mb-3">
                <svg className="w-7 h-7 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h3 className="font-bold text-lg text-gray-900">Błąd generowania</h3>
              <p className="text-sm text-red-600 mt-2 max-w-sm mx-auto">{errorMsg}</p>
            </div>
            <div className="flex justify-center gap-2">
              <button
                onClick={() => setStep('config')}
                className="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Wróć do ustawień
              </button>
              <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm text-gray-500">
                Zamknij
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
