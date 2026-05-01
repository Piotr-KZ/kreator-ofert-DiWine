import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = '/api/v1/offers';

export default function OfferHome() {
  const navigate = useNavigate();
  const [winePhoto, setWinePhoto] = useState('');

  useEffect(() => {
    axios.get(`${API}/photos/default?category=wine`).then(r => {
      if (r.data?.url) setWinePhoto(r.data.url);
    }).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-gray-50" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />

      <nav className="bg-gray-950 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
          <span className="text-white font-bold">DiWine</span>
          <span className="text-gray-600 text-sm">System Ofertowy</span>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => navigate('/offer/list')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Oferty</button>
          <button onClick={() => navigate('/offer/orders')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Zamówienia</button>
          <button onClick={() => navigate('/offer/invoices')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Faktury</button>
          <button onClick={() => navigate('/offer/settings')} className="px-4 py-1.5 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">Ustawienia</button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 flex items-center justify-center" style={{ minHeight: 'calc(100vh - 56px)' }}>
        <div className="flex items-center gap-16">
          <div className="flex-shrink-0 w-56">
            {winePhoto ? (
              <img src={winePhoto} alt="DiWine" className="w-full rounded-2xl shadow-xl" />
            ) : (
              <div className="w-full aspect-[3/4] bg-gradient-to-b from-gray-200 to-gray-100 rounded-2xl" />
            )}
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-900 leading-tight mb-2">
              SYSTEM OFERTOWY<br /><span className="text-indigo-600">DIWINE</span>
            </h1>
            <p className="text-gray-500 text-lg mb-8">Od zapytania klienta po gotową ofertę prezentową.</p>
            <button onClick={() => navigate('/offer/create')}
              className="px-8 py-4 bg-indigo-600 text-white rounded-xl text-lg font-bold hover:bg-indigo-700 shadow-lg shadow-indigo-200">
              + Nowe zapytanie
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
