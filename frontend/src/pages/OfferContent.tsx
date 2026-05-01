/**
 * Step 4: Treść oferty — wybór szablonu, edycja tekstów i zdjęć.
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOfferStore } from '@/store/offerStore';
import OfferStepper from '@/components/offer/OfferStepper';
import OfferNavButtons from '@/components/offer/OfferNavButtons';
import axios from 'axios';

const API = '/api/v1/offers';

const TEMPLATES = [
  { id: 'standard', name: 'Standard', desc: 'Nagłówek, powitanie, zestawy, dlaczego my, CTA' },
  { id: 'premium', name: 'Premium', desc: 'Rozbudowana z ciekawostkami i zdjęciami' },
  { id: 'quick', name: 'Szybka wycena', desc: 'Minimum — same zestawy i CTA' },
  { id: 'presentation', name: 'Prezentacyjna', desc: 'Na spotkanie — duże zdjęcia, pełne opisy' },
];

const TEXT_BLOCKS = [
  { type: 'greeting', label: 'Powitanie' },
  { type: 'why_us', label: 'Dlaczego my' },
  { type: 'fun_fact', label: 'Ciekawostka' },
  { type: 'closing', label: 'Zakończenie' },
];

export default function OfferContent() {
  const { offerId } = useParams<{ offerId: string }>();
  const navigate = useNavigate();
  const { offer, loadOffer } = useOfferStore();

  const [selectedTemplate, setSelectedTemplate] = useState('standard');
  const [pageBuilt, setPageBuilt] = useState(false);
  const [building, setBuilding] = useState(false);
  const [error, setError] = useState('');

  // Text variants loaded from API
  const [textVariants, setTextVariants] = useState<Record<string, any[]>>({});
  const [selectedTexts, setSelectedTexts] = useState<Record<string, string>>({});

  // Photos
  const [photos, setPhotos] = useState<any[]>([]);
  const [selectedPhoto, setSelectedPhoto] = useState('');

  useEffect(() => {
    if (offerId) loadOffer(offerId);
  }, [offerId]);

  // Load text variants when template selected
  useEffect(() => {
    const loadTexts = async () => {
      const occ = offer?.occasion_code || '';
      const results: Record<string, any[]> = {};
      for (const block of TEXT_BLOCKS) {
        try {
          const { data } = await axios.get(`${API}/ai/text-templates`, {
            params: { block_type: block.type, occasion_code: occ || undefined },
          });
          results[block.type] = data;
          // Auto-select first variant
          if (data.length > 0 && !selectedTexts[block.type]) {
            setSelectedTexts(prev => ({ ...prev, [block.type]: data[0].id }));
          }
        } catch { /* ignore */ }
      }
      setTextVariants(results);
    };
    if (offer) loadTexts();
  }, [offer?.id]);

  // Load photos for category
  useEffect(() => {
    const loadPhotos = async () => {
      const category = selectedTemplate === 'standard' ? 'christmas'
        : selectedTemplate === 'premium' ? 'gift'
        : selectedTemplate === 'quick' ? 'wine'
        : 'lifestyle';
      try {
        const { data } = await axios.get(`${API}/photos/picker`, { params: { category, limit: 8 } });
        setPhotos(data);
        const def = data.find((p: any) => p.is_default);
        if (def) setSelectedPhoto(def.id);
        else if (data.length) setSelectedPhoto(data[0].id);
      } catch { /* ignore */ }
    };
    loadPhotos();
  }, [selectedTemplate]);

  if (!offer) return <div className="p-8 text-gray-400">Ładowanie...</div>;

  const handleBuildPage = async () => {
    setBuilding(true);
    setError('');
    try {
      await axios.post(`${API}/${offerId}/build-page`, { template_id: selectedTemplate });
      setPageBuilt(true);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Błąd budowania strony');
    } finally {
      setBuilding(false);
    }
  };

  const navTo = (s: number) => {
    if (s === 3) navigate(`/offer/${offerId}`);
    if (s === 5) navigate(`/offer/${offerId}/summary`);
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
      <OfferStepper current={4} maxReached={pageBuilt ? 5 : 4} onNavigate={navTo} />

      <div className="flex-1 overflow-auto">
        <div className="max-w-3xl mx-auto py-6 px-6">
          <h2 className="text-xl font-bold text-gray-900 mb-1">Treść oferty</h2>
          <p className="text-gray-500 text-sm mb-5">Wybierz szablon, dopasuj teksty i zdjęcia.</p>

          {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{error}</div>}

          {/* Szablon */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="text-xs font-bold text-gray-500 mb-3">SZABLON STRONY</div>
            <div className="grid grid-cols-2 gap-3">
              {TEMPLATES.map(t => (
                <button key={t.id} onClick={() => { setSelectedTemplate(t.id); setPageBuilt(false); }}
                  className={`text-left p-3 rounded-xl border transition-all ${selectedTemplate === t.id ? 'border-indigo-400 bg-indigo-50' : 'border-gray-200 hover:border-gray-300'}`}>
                  <div className="text-sm font-bold text-gray-900">{t.name}</div>
                  <div className="text-xs text-gray-400 mt-0.5">{t.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Teksty */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="text-xs font-bold text-gray-500 mb-3">TEKSTY OFERTOWE</div>
            <div className="space-y-3">
              {TEXT_BLOCKS.map(block => {
                const variants = textVariants[block.type] || [];
                const selected = selectedTexts[block.type];
                return (
                  <div key={block.type}>
                    <div className="text-xs font-medium text-gray-700 mb-1.5">{block.label}</div>
                    {variants.length > 0 ? (
                      <div className="space-y-1">
                        {variants.map((v: any) => (
                          <button key={v.id} onClick={() => setSelectedTexts(prev => ({ ...prev, [block.type]: v.id }))}
                            className={`w-full text-left px-3 py-2 rounded-lg border text-xs transition-all ${selected === v.id ? 'border-indigo-400 bg-indigo-50' : 'border-gray-200 hover:border-gray-300'}`}>
                            <div className="flex items-center justify-between mb-0.5">
                              <span className="font-semibold text-gray-900">{v.name}</span>
                              <span className="text-[10px] text-gray-400">{v.tone}</span>
                            </div>
                            <div className="text-gray-500 line-clamp-2">{v.template_text.substring(0, 120)}...</div>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="text-xs text-gray-400 py-2">Brak szablonów dla tej okazji</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Zdjęcie nagłówka */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="text-xs font-bold text-gray-500 mb-3">ZDJĘCIE NAGŁÓWKA</div>
            {photos.length > 0 ? (
              <div className="grid grid-cols-4 gap-2">
                {photos.map((p: any) => (
                  <button key={p.id} onClick={() => setSelectedPhoto(p.id)}
                    className={`rounded-lg overflow-hidden border-2 transition-all aspect-video ${selectedPhoto === p.id ? 'border-indigo-500 ring-2 ring-indigo-200' : 'border-transparent hover:border-gray-300'}`}>
                    <img src={p.thumbnail_url || p.url} alt="" className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-xs text-gray-400 py-2">Brak zdjęć. Uruchom /download-lifestyle na backendzie.</div>
            )}
          </div>

          {/* Buduj / Preview */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-gray-900">{pageBuilt ? 'Strona gotowa' : 'Zbuduj stronę ofertową'}</div>
                <div className="text-xs text-gray-400 mt-0.5">{pageBuilt ? 'Możesz przejść do podsumowania lub zmienić ustawienia' : 'System złoży stronę z wybranych elementów'}</div>
              </div>
              <div className="flex gap-2">
                {pageBuilt && (
                  <button onClick={() => window.open(`${API}/${offerId}/page-preview`, '_blank')}
                    className="px-4 py-2 text-sm font-semibold bg-white text-gray-700 border border-gray-200 rounded-lg">Podgląd</button>
                )}
                <button onClick={handleBuildPage} disabled={building}
                  className={`px-4 py-2 text-sm font-bold text-white rounded-lg ${building ? 'bg-gray-300' : pageBuilt ? 'bg-gray-700 hover:bg-gray-800' : 'bg-indigo-600 hover:bg-indigo-700'}`}>
                  {building ? 'Buduję...' : pageBuilt ? 'Przebuduj' : 'Zbuduj stronę'}
                </button>
              </div>
            </div>
          </div>

          <OfferNavButtons
            onBack={() => navigate(`/offer/${offerId}`)}
            onNext={() => navigate(`/offer/${offerId}/summary`)}
            nextLabel="Dalej — podsumowanie"
            nextDisabled={!pageBuilt}
          />
        </div>
      </div>
    </div>
  );
}
