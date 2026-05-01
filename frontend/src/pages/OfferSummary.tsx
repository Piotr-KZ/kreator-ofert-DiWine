/**
 * Step 5: Podsumowanie — preview całej oferty, ostatni moment na cofnięcie.
 */

import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOfferStore } from '@/store/offerStore';
import OfferStepper from '@/components/offer/OfferStepper';
import OfferNavButtons from '@/components/offer/OfferNavButtons';

const API = '/api/v1/offers';

export default function OfferSummary() {
  const { offerId } = useParams<{ offerId: string }>();
  const navigate = useNavigate();
  const { offer, products, packagings, loadOffer, loadCatalog } = useOfferStore();

  useEffect(() => { loadCatalog(); if (offerId) loadOffer(offerId); }, [offerId]);
  if (!offer) return <div className="p-8 text-gray-400">Ładowanie...</div>;

  const getPkg = (id?: string | null) => packagings.find(p => p.id === id);
  const getProd = (id?: string | null) => products.find(p => p.id === id);
  const grandTotal = offer.sets.reduce((s, x) => s + x.total_price, 0);

  const navTo = (s: number) => {
    if (s === 3) navigate(`/offer/${offerId}`);
    if (s === 4) navigate(`/offer/${offerId}/content`);
    if (s === 6) navigate(`/offer/${offerId}/export`);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
      <nav className="bg-gray-950 px-6 py-2.5 flex items-center gap-3">
        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
        <span className="text-white font-bold text-sm">OfferCreator</span>
        <span className="text-gray-500 text-xs">/ {offer.client_name} / {offer.offer_number}</span>
      </nav>
      <OfferStepper current={5} maxReached={5} onNavigate={navTo} />

      <div className="flex-1 overflow-auto">
        <div className="max-w-3xl mx-auto py-6 px-6">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Podsumowanie oferty</h2>
          <p className="text-gray-500 text-sm mb-5">Sprawdź wszystko przed wysłaniem. Możesz cofnąć i poprawić.</p>

          {/* Preview iframe */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-gray-500">PODGLĄD STRONY OFERTOWEJ</span>
              <button onClick={() => window.open(`${API}/${offerId}/page-preview`, '_blank')}
                className="text-xs text-indigo-600 font-semibold hover:text-indigo-700">Otwórz w nowej karcie ↗</button>
            </div>
            <iframe src={`${API}/${offerId}/page-preview`} className="w-full rounded-lg border border-gray-200" style={{ height: 400 }} title="Podgląd oferty" />
          </div>

          {/* Kosztorys */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-4">
            <div className="px-5 py-3 bg-gray-50 border-b">
              <span className="text-xs font-bold text-gray-500">KOSZTORYS</span>
            </div>
            {offer.sets.map(s => {
              const pkg = getPkg(s.packaging_id);
              return (
                <div key={s.id} className="border-b last:border-0">
                  <div className="flex items-center justify-between px-5 py-3">
                    <div>
                      <span className="font-bold text-gray-900 text-sm">{s.name}</span>
                      {s.budget_per_unit && (
                        <span className={`ml-2 text-[10px] px-2 py-0.5 rounded-full font-medium ${s.unit_price <= s.budget_per_unit ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {s.unit_price <= s.budget_per_unit ? 'W budżecie' : 'Ponad budżet'}
                        </span>
                      )}
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-bold text-indigo-700">{s.unit_price.toFixed(2)} zł</span>
                      <span className="text-xs text-gray-400 ml-2">× {offer.quantity} = {s.total_price.toFixed(0)} zł</span>
                    </div>
                  </div>
                  <div className="px-5 pb-3">
                    <div className="flex flex-wrap gap-1.5">
                      {pkg && <span className="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{pkg.name} ({pkg.price} zł)</span>}
                      {s.items.map(item => {
                        const prod = getProd(item.product_id);
                        return <span key={item.id} className="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{prod?.name || '?'} ({item.unit_price.toFixed(0)} zł)</span>;
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
            <div className="px-5 py-3 bg-indigo-50 flex items-center justify-between">
              <span className="text-sm font-bold text-gray-700">Suma</span>
              <span className="text-lg font-bold text-indigo-700">{grandTotal.toFixed(0)} zł netto</span>
            </div>
          </div>

          {/* Dane klienta */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="text-xs font-bold text-gray-500 mb-2">KLIENT</div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div><span className="text-gray-400">Firma:</span> <b>{offer.client_name}</b></div>
              <div><span className="text-gray-400">Ilość:</span> <b>{offer.quantity} szt.</b></div>
              <div><span className="text-gray-400">Okazja:</span> <b>{offer.occasion_code}</b></div>
              {offer.deadline && <div><span className="text-gray-400">Termin:</span> <b>{offer.deadline}</b></div>}
              {offer.delivery_address && <div className="col-span-2"><span className="text-gray-400">Dostawa:</span> <b>{offer.delivery_address}</b></div>}
            </div>
          </div>

          <OfferNavButtons
            onBack={() => navigate(`/offer/${offerId}/content`)}
            backLabel="← Popraw treść"
            onNext={() => navigate(`/offer/${offerId}/export`)}
            nextLabel="Wszystko OK — eksport"
          />
        </div>
      </div>
    </div>
  );
}
