import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = '/api/v1/offers';

const STATUS: Record<string, { label: string; color: string }> = {
  draft: { label: 'Szkic', color: 'bg-gray-100 text-gray-600' },
  sent: { label: 'Wysłana', color: 'bg-blue-100 text-blue-700' },
  viewed: { label: 'Wyświetlona', color: 'bg-indigo-100 text-indigo-700' },
  accepted: { label: 'Zaakceptowana', color: 'bg-green-100 text-green-700' },
  rejected: { label: 'Odrzucona', color: 'bg-red-100 text-red-700' },
  expired: { label: 'Wygasła', color: 'bg-gray-100 text-gray-400' },
};

export default function OfferList() {
  const navigate = useNavigate();
  const [offers, setOffers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    axios.get(API).then(r => setOffers(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />

      <nav className="bg-gray-950 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/offer')} className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
            <span className="text-white font-bold">DiWine</span>
          </button>
          <span className="text-gray-600 text-sm">/ Oferty</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => navigate('/offer/list')} className="px-4 py-1.5 text-sm text-white bg-white/10 rounded-lg">Oferty</button>
          <button onClick={() => navigate('/offer/settings')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Ustawienia</button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Oferty ({offers.length})</h2>
          <button onClick={() => navigate('/offer/create')}
            className="px-5 py-2 text-sm font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            + Nowe zapytanie
          </button>
        </div>

        {loading ? (
          <div className="text-gray-400 text-sm">Ładowanie...</div>
        ) : offers.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
            Brak ofert. Kliknij "Nowe zapytanie" aby utworzyć pierwszą.
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b">
                  <th className="text-left p-3 text-xs text-gray-500">Nr oferty</th>
                  <th className="text-left p-3 text-xs text-gray-500">Firma</th>
                  <th className="text-left p-3 text-xs text-gray-500">Osoba</th>
                  <th className="text-left p-3 text-xs text-gray-500">Przygotowana</th>
                  <th className="text-left p-3 text-xs text-gray-500">Eksport</th>
                  <th className="text-center p-3 text-xs text-gray-500">Status</th>
                  <th className="text-right p-3 text-xs text-gray-500">Ilość</th>
                  <th className="text-right p-3 text-xs text-gray-500">Wartość</th>
                  <th className="text-center p-3 text-xs text-gray-500">Akcje</th>
                </tr>
              </thead>
              <tbody>
                {offers.map((o: any) => {
                  const st = STATUS[o.status] || STATUS.draft;
                  const totalValue = (o.sets || []).reduce((s: number, x: any) => s + (x.total_price || 0), 0);
                  return (
                    <tr key={o.id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="p-3 font-bold text-gray-900">{o.offer_number}</td>
                      <td className="p-3 font-medium">{o.client_name || '—'}</td>
                      <td className="p-3 text-gray-500">{o.contact_person || '—'}</td>
                      <td className="p-3 text-gray-500 text-xs">{o.created_at?.substring(0, 10) || '—'}</td>
                      <td className="p-3 text-gray-500 text-xs">{o.exported_at?.substring(0, 10) || '—'}</td>
                      <td className="p-3 text-center">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${st.color}`}>{st.label}</span>
                      </td>
                      <td className="p-3 text-right">{o.quantity} szt.</td>
                      <td className="p-3 text-right font-semibold">{totalValue > 0 ? `${totalValue.toFixed(0)} zł` : '—'}</td>
                      <td className="p-3 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <button onClick={() => navigate(`/offer/${o.id}`)}
                            className="px-2 py-1 text-[10px] font-semibold text-indigo-700 bg-indigo-50 rounded hover:bg-indigo-100">Edytuj</button>
                          <button onClick={() => window.open(`${API}/${o.id}/pdf`, '_blank')}
                            className="px-2 py-1 text-[10px] font-semibold text-gray-600 bg-gray-100 rounded hover:bg-gray-200">PDF</button>
                        </div>
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
