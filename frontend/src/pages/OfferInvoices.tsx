import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = '/api/v1/offers';

const KIND_LABELS: Record<string, { label: string; color: string }> = {
  proforma: { label: 'Proforma', color: 'bg-blue-100 text-blue-700' },
  vat: { label: 'VAT', color: 'bg-green-100 text-green-700' },
  estimate: { label: 'Wycena', color: 'bg-gray-100 text-gray-600' },
};

export default function OfferInvoices() {
  const nav = useNavigate();
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    axios.get(`${API}/invoices/list`)
      .then(r => setInvoices(r.data))
      .catch(e => setError(e.response?.data?.detail || 'Nie udało się pobrać faktur. Sprawdź konfigurację Fakturowni w Ustawieniach.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />

      <nav className="bg-gray-950 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => nav('/offer')} className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
            <span className="text-white font-bold">DiWine</span>
          </button>
          <span className="text-gray-600 text-sm">/ Faktury</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => nav('/offer/list')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Oferty</button>
          <button onClick={() => nav('/offer/orders')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Zamówienia</button>
          <button className="px-4 py-1.5 text-sm text-white bg-white/10 rounded-lg">Faktury</button>
          <button onClick={() => nav('/offer/settings')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Ustawienia</button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Faktury i proformy</h2>
          <div className="text-xs text-gray-400">Dane z Fakturowni — generuj proformę/VAT w kroku Eksport oferty</div>
        </div>

        {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{error}</div>}

        {loading ? (
          <div className="text-gray-400 text-sm">Ładowanie z Fakturowni...</div>
        ) : invoices.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
            Brak faktur. Wygeneruj pierwszą proformę w kroku Eksport oferty.
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b">
                  <th className="text-left p-3 text-xs text-gray-500">Numer</th>
                  <th className="text-center p-3 text-xs text-gray-500">Typ</th>
                  <th className="text-left p-3 text-xs text-gray-500">Klient</th>
                  <th className="text-left p-3 text-xs text-gray-500">Data</th>
                  <th className="text-right p-3 text-xs text-gray-500">Netto</th>
                  <th className="text-right p-3 text-xs text-gray-500">Brutto</th>
                  <th className="text-center p-3 text-xs text-gray-500">Status</th>
                  <th className="text-center p-3 text-xs text-gray-500">PDF</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv: any) => {
                  const kl = KIND_LABELS[inv.kind] || KIND_LABELS.estimate;
                  return (
                    <tr key={inv.id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="p-3 font-bold text-gray-900">{inv.number}</td>
                      <td className="p-3 text-center">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${kl.color}`}>{kl.label}</span>
                      </td>
                      <td className="p-3 font-medium">{inv.buyer_name || '—'}</td>
                      <td className="p-3 text-gray-500">{inv.issue_date || '—'}</td>
                      <td className="p-3 text-right">{inv.total_net?.toFixed(2)} zł</td>
                      <td className="p-3 text-right font-semibold">{inv.total_gross?.toFixed(2)} zł</td>
                      <td className="p-3 text-center">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${inv.paid ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                          {inv.paid ? 'Opłacona' : 'Nieopłacona'}
                        </span>
                      </td>
                      <td className="p-3 text-center">
                        {inv.pdf_url ? (
                          <a href={inv.pdf_url} target="_blank" rel="noopener" className="text-indigo-600 text-xs font-semibold hover:text-indigo-700">PDF</a>
                        ) : '—'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
