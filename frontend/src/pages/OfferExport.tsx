/**
 * Step 6: Export — PDF, link, wyślij.
 */

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOfferStore } from '@/store/offerStore';
import OfferStepper from '@/components/offer/OfferStepper';
import OfferNavButtons from '@/components/offer/OfferNavButtons';
import ProformaModal from '@/components/offer/ProformaModal';
import axios from 'axios';

const API = '/api/v1/offers';

export default function OfferExport() {
  const { offerId } = useParams<{ offerId: string }>();
  const navigate = useNavigate();
  const { offer, loadOffer } = useOfferStore();
  const [proformaOpen, setProformaOpen] = useState(false);

  useEffect(() => { if (offerId) loadOffer(offerId); }, [offerId]);
  if (!offer) return <div className="p-8 text-gray-400">Ładowanie...</div>;

  const nav = navigate;
  const navTo = (s: number) => {
    if (s === 3) navigate(`/offer/${offerId}`);
    if (s === 4) navigate(`/offer/${offerId}/cost`);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
      <nav className="bg-gray-950 px-6 py-2.5 flex items-center gap-3">
        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
        <span className="text-white font-bold text-sm">OfferCreator</span>
        <span className="text-gray-500 text-xs">/ {offer.client_name} / {offer.offer_number}</span>
      </nav>
      <OfferStepper current={8} maxReached={8} onNavigate={navTo} />

      <div className="flex-1 overflow-auto">
        <div className="max-w-3xl mx-auto py-6 px-6">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Eksport oferty</h2>
          <p className="text-gray-500 text-sm mb-6">{offer.offer_number} — gotowa do wysłania</p>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <button onClick={() => window.open(`${API}/${offerId}/pdf`, '_blank')}
              className="bg-gray-900 text-white rounded-xl p-5 text-left hover:bg-gray-800 transition-all">
              <div className="font-bold mb-1">Pobierz PDF</div>
              <div className="text-xs text-gray-400">Kosztorys do maila lub wydruku</div>
            </button>
            <button onClick={() => window.open(`${API}/${offerId}/page-preview`, '_blank')}
              className="bg-indigo-600 text-white rounded-xl p-5 text-left hover:bg-indigo-700 transition-all">
              <div className="font-bold mb-1">Link dla klienta</div>
              <div className="text-xs text-indigo-200">Strona ofertowa online</div>
            </button>
            <button onClick={() => setProformaOpen(true)}
              className="bg-amber-600 text-white rounded-xl p-5 text-left hover:bg-amber-700 transition-all">
              <div className="font-bold mb-1">Proforma w Fakturowni</div>
              <div className="text-xs text-amber-200">Generuj proformę z zestawów</div>
            </button>
            <button onClick={async () => {
                try {
                  const { data } = await axios.get(`${API}/${offerId}`);
                  if (data.project_id) nav(`/lab/${data.project_id}/step/3`);
                  else alert('Wróć do kosztorysu i kliknij "Dalej — buduj ofertę"');
                } catch {}
              }}
              className="bg-white text-gray-700 border border-gray-200 rounded-xl p-5 text-left hover:border-gray-300 transition-all">
              <div className="font-bold mb-1">Edytuj stronę</div>
              <div className="text-xs text-gray-400">Wróć do edytora klocków</div>
            </button>
          </div>

          <div className="bg-gray-50 rounded-xl p-4 text-center text-sm text-gray-500">
            Oferta {offer.offer_number} gotowa. Możesz cofnąć się i poprawić w dowolnym momencie.
          </div>

          <OfferNavButtons
            onBack={() => navigate(`/offer/${offerId}/cost`)}
            backLabel="← Wróć do kosztorysu"
          />
        </div>
      </div>

      <ProformaModal open={proformaOpen} onClose={() => setProformaOpen(false)} />
    </div>
  );
}
