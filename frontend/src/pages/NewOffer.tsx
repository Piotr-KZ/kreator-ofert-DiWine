/**
 * New Offer page — single entry point for creating an offer.
 * Collects client + order basics, creates both via API, redirects to configurator.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOfferStore } from '@/store/offerStore';
import * as offerApi from '@/api/offerClient';
import type { OccasionItem } from '@/types/offer';

export default function NewOffer() {
  const navigate = useNavigate();
  const store = useOfferStore();
  const { occasions, catalogLoaded } = store;

  const [companyName, setCompanyName] = useState('');
  const [nip, setNip] = useState('');
  const [contactPerson, setContactPerson] = useState('');
  const [email, setEmail] = useState('');
  const [quantity, setQuantity] = useState(50);
  const [occasionCode, setOccasionCode] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    store.resetOffer();   // clear any previous offer from store
    store.loadCatalog();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim()) {
      setError('Podaj nazwę firmy');
      return;
    }
    if (quantity < 1) {
      setError('Ilość musi być większa od 0');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // 1. Create client
      const { data: client } = await offerApi.createClient({
        company_name: companyName.trim(),
        nip: nip.trim() || undefined,
        contact_person: contactPerson.trim() || undefined,
        email: email.trim() || undefined,
      });

      // 2. Create offer
      const { data: offer } = await offerApi.createOffer({
        client_id: client.id,
        quantity,
        occasion_code: occasionCode || undefined,
      });

      // 3. Redirect to configurator
      navigate(`/offer/${offer.id}`);
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || 'Błąd tworzenia oferty';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />

      {/* Nav */}
      <nav className="bg-gray-950 px-6 py-2.5 flex items-center gap-3">
        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
        <span className="text-white font-bold text-sm">OfferCreator</span>
        <span className="text-gray-500 text-xs">/ Nowa oferta</span>
      </nav>

      {/* Form */}
      <div className="flex-1 flex items-start justify-center pt-16">
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-lg space-y-5">
          <h1 className="text-xl font-bold text-gray-900 mb-1">Nowa oferta</h1>
          <p className="text-sm text-gray-500 mb-4">Podaj dane klienta i parametry zamówienia.</p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-2 text-sm">
              {error}
            </div>
          )}

          {/* Company name */}
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1">Nazwa firmy *</label>
            <input
              type="text"
              value={companyName}
              onChange={e => setCompanyName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              placeholder="np. ABC Sp. z o.o."
            />
          </div>

          {/* NIP */}
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1">NIP</label>
            <input
              type="text"
              value={nip}
              onChange={e => setNip(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              placeholder="np. 1234567890"
              maxLength={10}
            />
          </div>

          {/* Contact + Email row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-700 mb-1">Osoba kontaktowa</label>
              <input
                type="text"
                value={contactPerson}
                onChange={e => setContactPerson(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                placeholder="Jan Kowalski"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                placeholder="jan@firma.pl"
              />
            </div>
          </div>

          {/* Quantity + Occasion row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-gray-700 mb-1">Ilość zestawów *</label>
              <input
                type="number"
                min={1}
                value={quantity}
                onChange={e => setQuantity(parseInt(e.target.value) || 1)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-700 mb-1">Okazja</label>
              <select
                value={occasionCode}
                onChange={e => setOccasionCode(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none bg-white"
              >
                <option value="">— bez okazji —</option>
                {catalogLoaded && occasions.map((o: OccasionItem) => (
                  <option key={o.code} value={o.code}>{o.name}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {submitting ? 'Tworzenie...' : 'Utwórz ofertę'}
          </button>
        </form>
      </div>
    </div>
  );
}
