import { useEffect, useState } from 'react';
import { paymentsApi, type PaymentRecord } from '@/api/account';
import { SectionCard, StatusBadge } from '@/components/ui';

const DUNNING_TIMELINE = [
  { day: 0, type: 'payment', label: 'Automatyczna próba pobrania płatności', color: 'bg-indigo-500' },
  { day: 0, type: 'email', label: 'Email: Termin płatności dziś', color: 'bg-amber-500' },
  { day: 1, type: 'payment', label: 'Druga próba pobrania płatności', color: 'bg-indigo-500' },
  { day: 3, type: 'email', label: 'Email: Płatność zaległa', color: 'bg-amber-500' },
  { day: 7, type: 'payment', label: 'Trzecia próba pobrania płatności', color: 'bg-indigo-500' },
  { day: 10, type: 'block', label: 'Ograniczenie dostępu do read-only', color: 'bg-red-500' },
  { day: 14, type: 'block', label: 'Wyłączenie opublikowanych stron', color: 'bg-red-500' },
  { day: 21, type: 'block', label: 'Zablokowanie dostępu (tylko billing)', color: 'bg-red-500' },
  { day: 30, type: 'email', label: 'Email: Ostateczne ostrzeżenie', color: 'bg-amber-500' },
  { day: 45, type: 'block', label: 'Anulowanie subskrypcji + downgrade', color: 'bg-red-500' },
];

export default function PaymentsTab() {
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);

  useEffect(() => {
    loadPayments();
  }, [page]);

  const loadPayments = async () => {
    setLoading(true);
    try {
      const data = await paymentsApi.list(10, page * 10);
      setPayments(data);
    } catch {
      // API may not be available yet
    } finally {
      setLoading(false);
    }
  };

  const statusBadge = (status: string) => {
    if (status === 'completed') return <StatusBadge variant="success">Zapłacono</StatusBadge>;
    if (status === 'failed') return <StatusBadge variant="error">Odrzucona</StatusBadge>;
    if (status === 'pending') return <StatusBadge variant="warning">Oczekuje</StatusBadge>;
    if (status === 'refunded') return <StatusBadge variant="info">Zwrot</StatusBadge>;
    return <StatusBadge variant="neutral">{status}</StatusBadge>;
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Płatności</h2>

      <SectionCard title="Historia płatności">
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : payments.length === 0 ? (
          <p className="text-sm text-gray-500 py-4">Brak płatności</p>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2 font-medium">Data</th>
                    <th className="pb-2 font-medium">Opis</th>
                    <th className="pb-2 font-medium">Kwota</th>
                    <th className="pb-2 font-medium">Metoda</th>
                    <th className="pb-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {payments.map((p) => (
                    <tr key={p.id} className="text-gray-900">
                      <td className="py-3">{new Date(p.created_at).toLocaleDateString('pl-PL')}</td>
                      <td className="py-3">{p.description || '-'}</td>
                      <td className="py-3 font-medium">{(p.amount / 100).toFixed(2)} {p.currency}</td>
                      <td className="py-3 text-gray-600">{p.payment_method_details || p.payment_method || '-'}</td>
                      <td className="py-3">{statusBadge(p.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex gap-2 mt-4">
              {page > 0 && (
                <button onClick={() => setPage(page - 1)} className="text-sm text-indigo-600 hover:text-indigo-700">
                  Poprzednia
                </button>
              )}
              {payments.length === 10 && (
                <button onClick={() => setPage(page + 1)} className="text-sm text-indigo-600 hover:text-indigo-700 ml-auto">
                  Następna
                </button>
              )}
            </div>
          </>
        )}
      </SectionCard>

      <SectionCard title="Ścieżka postępowania przy braku płatności">
        <div className="relative pl-6">
          <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gray-200" />
          {DUNNING_TIMELINE.map((step, i) => (
            <div key={i} className="relative flex items-start gap-3 mb-4 last:mb-0">
              <div className={`absolute -left-4 w-3 h-3 rounded-full ${step.color} ring-2 ring-white`} style={{ top: '4px' }} />
              <div className="ml-2">
                <span className="text-xs font-medium text-gray-400">Dzień {step.day}</span>
                <p className="text-sm text-gray-700">{step.label}</p>
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-4">Ta ścieżka jest definiowana w ustawieniach systemu.</p>
      </SectionCard>
    </div>
  );
}
