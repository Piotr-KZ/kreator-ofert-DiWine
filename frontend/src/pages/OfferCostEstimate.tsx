import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOfferStore } from '@/store/offerStore';
import OfferStepper from '@/components/offer/OfferStepper';
import axios from 'axios';

const API = '/api/v1/offers';

export default function OfferCostEstimate() {
  const { offerId } = useParams<{ offerId: string }>();
  const nav = useNavigate();
  const { offer, products, packagings, loadOffer, loadCatalog } = useOfferStore();
  const [activeIdx, setActiveIdx] = useState(0);
  const [building, setBuilding] = useState(false);

  useEffect(() => { loadCatalog(); if (offerId) loadOffer(offerId); }, [offerId]);
  if (!offer) return <div className="p-8 text-gray-400">Ładowanie...</div>;

  const getPkg = (id?: string | null) => packagings.find(p => p.id === id);
  const getProd = (id?: string | null) => products.find(p => p.id === id);
  const grandTotal = offer.sets.reduce((s, x) => s + x.total_price, 0);
  const set = offer.sets[activeIdx];
  const TL: Record<string, string> = { wine: 'Wino', sweet: 'Słodycze', decoration: 'Dodatek', personalization: 'Personalizacja' };

  const handleNext = async () => {
    setBuilding(true);
    try {
      const { data } = await axios.post(`${API}/${offerId}/build-page`, { template_id: 'standard' });
      localStorage.setItem('_offer_context', JSON.stringify({ offer_id: offerId }));
      nav(`/lab/${data.project_id}/step/3`);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Błąd budowania strony');
    } finally {
      setBuilding(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
      <nav className="bg-gray-950 px-6 py-2.5 flex items-center gap-3">
        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
        <span className="text-white font-bold text-sm">OfferCreator</span>
        <span className="text-gray-500 text-xs">/ {offer.client_name} / {offer.offer_number}</span>
      </nav>
      <OfferStepper current={4} maxReached={4} onNavigate={s => {
        if (s === 3) nav(`/offer/${offerId}`);
      }} />

      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto py-6 px-6">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Kosztorys oferty</h2>
          <p className="text-gray-500 text-sm mb-5">
            {offer.sets.length} zestaw{offer.sets.length !== 1 ? 'y' : ''} • {offer.quantity} szt. • {offer.offer_number}
          </p>

          {offer.sets.length > 1 && (
            <div className="flex gap-1 mb-4">
              {offer.sets.map((s, i) => (
                <button key={s.id} onClick={() => setActiveIdx(i)}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold ${activeIdx === i ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 border border-gray-200'}`}>
                  {s.name}
                </button>
              ))}
            </div>
          )}

          {set && (() => {
            const pkg = getPkg(set.packaging_id);
            return (
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-4">
                <div className="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
                  <div>
                    <h3 className="font-bold text-gray-900 text-lg">{set.name}</h3>
                    {set.budget_per_unit && (
                      <span className={`text-xs mt-1 inline-block px-2 py-0.5 rounded-full font-medium ${set.unit_price <= set.budget_per_unit ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        Budżet: {set.budget_per_unit} zł — {set.unit_price <= set.budget_per_unit ? 'W budżecie' : 'Ponad budżet'}
                      </span>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-indigo-700">{set.unit_price.toFixed(2)} zł</div>
                    <div className="text-xs text-gray-400">za sztukę netto</div>
                  </div>
                </div>
                <table className="w-full text-sm">
                  <thead><tr className="border-b">
                    <th className="text-left p-4 text-xs text-gray-500">Pozycja</th>
                    <th className="text-left p-4 text-xs text-gray-500">Typ</th>
                    <th className="text-right p-4 text-xs text-gray-500">Cena / szt.</th>
                    <th className="text-right p-4 text-xs text-gray-500">× {offer.quantity}</th>
                  </tr></thead>
                  <tbody>
                    {pkg && <tr className="border-b bg-gray-50/50">
                      <td className="p-4 font-medium">{pkg.name}</td>
                      <td className="p-4 text-gray-400">Opakowanie</td>
                      <td className="p-4 text-right font-semibold">{pkg.price.toFixed(2)} zł</td>
                      <td className="p-4 text-right text-gray-500">{(pkg.price * offer.quantity).toFixed(0)} zł</td>
                    </tr>}
                    {set.items.map(item => {
                      const prod = getProd(item.product_id);
                      return (
                        <tr key={item.id} className="border-b last:border-0">
                          <td className="p-4 font-medium">{prod?.name || '?'}{item.color_code && <span className="text-xs text-gray-400 ml-1">({item.color_code})</span>}</td>
                          <td className="p-4 text-gray-400">{TL[item.item_type] || item.item_type}</td>
                          <td className="p-4 text-right font-semibold">{item.unit_price.toFixed(2)} zł</td>
                          <td className="p-4 text-right text-gray-500">{(item.unit_price * offer.quantity).toFixed(0)} zł</td>
                        </tr>
                      );
                    })}
                  </tbody>
                  <tfoot><tr className="bg-indigo-50">
                    <td colSpan={2} className="p-4 font-bold">RAZEM za zestaw</td>
                    <td className="p-4 text-right font-bold text-indigo-700">{set.unit_price.toFixed(2)} zł</td>
                    <td className="p-4 text-right font-bold text-indigo-700">{set.total_price.toFixed(0)} zł</td>
                  </tr></tfoot>
                </table>
              </div>
            );
          })()}

          {offer.sets.length > 1 && (
            <div className="bg-gray-900 rounded-xl p-5 flex items-center justify-between text-white mb-4">
              <div>
                <div className="text-sm text-gray-300">Suma wszystkich zestawów</div>
                <div className="text-xs text-gray-500">{offer.sets.map(s => s.name).join(' + ')}</div>
              </div>
              <div className="text-2xl font-bold">{grandTotal.toFixed(0)} zł netto</div>
            </div>
          )}

          <div className="flex items-center gap-3 mt-6 pt-4 border-t border-gray-200">
            <button onClick={() => nav(`/offer/${offerId}`)}
              className="px-4 py-2 text-sm font-semibold bg-white text-gray-700 border border-gray-200 rounded-lg">← Wróć do zestawów</button>
            <div className="flex-1" />
            <button onClick={handleNext} disabled={offer.sets.length === 0 || building}
              className={`px-6 py-2.5 text-sm font-bold text-white rounded-lg ${offer.sets.length === 0 || building ? 'bg-gray-300' : 'bg-indigo-600 hover:bg-indigo-700'}`}>
              {building ? 'Przygotowuję...' : 'Dalej — buduj ofertę'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
