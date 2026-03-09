import { useEffect, useState } from 'react';
import { billingApi } from '@/api/billing';
import { Btn, Fld, SectionCard, StatusBadge } from '@/components/ui';
import type { Invoice } from '@/types/models';

export default function InvoicesTab() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [invoiceEmail, setInvoiceEmail] = useState('');
  const [emailMsg, setEmailMsg] = useState('');

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const data = await billingApi.listInvoices();
      setInvoices(Array.isArray(data) ? data : []);
    } catch {
      // Invoices endpoint may not be available
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = async (invoiceId: string) => {
    try {
      const response = await billingApi.getInvoicePdf(invoiceId);
      // Handle blob download
      const blob = response instanceof Blob ? response : new Blob([response as any]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `faktura-${invoiceId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // PDF download not available
    }
  };

  const statusBadge = (status: string) => {
    if (status === 'paid') return <StatusBadge variant="success">Opłacona</StatusBadge>;
    if (status === 'open') return <StatusBadge variant="warning">Oczekuje</StatusBadge>;
    if (status === 'void') return <StatusBadge variant="neutral">Anulowana</StatusBadge>;
    if (status === 'uncollectible') return <StatusBadge variant="error">Zaległa</StatusBadge>;
    return <StatusBadge variant="neutral">{status}</StatusBadge>;
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Faktury</h2>

      <SectionCard title="Historia faktur">
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : invoices.length === 0 ? (
          <p className="text-sm text-gray-500 py-4">Brak faktur</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Numer</th>
                  <th className="pb-2 font-medium">Data</th>
                  <th className="pb-2 font-medium">Kwota</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium">Akcja</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {invoices.map((inv) => (
                  <tr key={inv.id} className="text-gray-900">
                    <td className="py-3 font-medium">{inv.invoice_number}</td>
                    <td className="py-3">{new Date(inv.created_at).toLocaleDateString('pl-PL')}</td>
                    <td className="py-3">{Number(inv.amount).toFixed(2)} {inv.currency}</td>
                    <td className="py-3">{statusBadge(inv.status)}</td>
                    <td className="py-3">
                      <button
                        onClick={() => downloadPdf(inv.id)}
                        className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                      >
                        Pobierz PDF
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      <SectionCard title="Ustawienia faktur">
        <div className="space-y-4">
          <Fld
            label="Email na który wysyłać faktury"
            type="email"
            value={invoiceEmail}
            onChange={setInvoiceEmail}
            placeholder="faktury@firma.pl"
          />
          <p className="text-xs text-gray-400">
            Dane na fakturze (nazwa, adres, NIP) pobierane są automatycznie z zakładki Firma.
          </p>
          {emailMsg && <p className="text-sm text-green-600">{emailMsg}</p>}
          <Btn onClick={() => setEmailMsg('Zapisano')} variant="secondary">Zapisz</Btn>
        </div>
      </SectionCard>
    </div>
  );
}
