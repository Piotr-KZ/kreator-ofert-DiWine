/**
 * Create Offer — 2-step flow:
 * Step 1: Paste client email → AI parses it
 * Step 2: Verify/edit parsed data → create offer
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOfferStore } from '@/store/offerStore';
import axios from 'axios';

const API = '/api/v1/offers';

const OCCASIONS = [
  { code: 'christmas', name: 'Boże Narodzenie' },
  { code: 'easter', name: 'Wielkanoc' },
  { code: 'birthday', name: 'Urodziny' },
  { code: 'universal', name: 'Uniwersalny' },
  { code: 'other', name: 'Inna okazja' },
];

const LEGAL_FORMS = [
  'Sp. z o.o.', 'S.A.', 'Sp.j.', 'Sp.k.', 'Sp. komandytowa',
  'Spółka jawna', 'JDG', 'S.C.', 'Fundacja', 'Stowarzyszenie',
];

const SAMPLE_EMAIL = `Dzień dobry,

Proszę o ofertę na 100 prezentów świątecznych do 150 zł netto za sztukę.
Prezent powinien zawierać wino, piernik, słodycze czekoladowe i ozdobny dodatek.
Opakowanie eleganckie z nadrukiem naszego logo.
Personalizacja na ekokorku.

Termin realizacji: do 20 listopada 2026.
Dostawa: Warszawa, ul. Marszałkowska 10.

Z poważaniem,
Anna Kowalska
Dyrektor HR
FirmaTech Sp. z o.o.
NIP: 5272876543
tel. 501-234-567
anna.kowalska@firmatech.pl`;

interface ParsedData {
  client: {
    company_name?: string;
    legal_form?: string;
    contact_person?: string;
    contact_role?: string;
    email?: string;
    phone?: string;
    nip?: string;
    website?: string;
    address?: {
      street?: string;
      number?: string;
      city?: string;
      postal_code?: string;
    };
  };
  order: {
    quantity?: number;
    budget_per_unit?: number;
    occasion?: string;
    deadline?: string;
  };
  delivery?: {
    recipient_name?: string;
    company_name?: string;
    street?: string;
    number?: string;
    city?: string;
    postal_code?: string;
  };
  requested_items: string[];
  vague_requests: string[];
  personalization: {
    logo_on_packaging?: boolean;
    engraving_on_cork?: boolean;
  };
  missing_info: string[];
  confidence: number;
}

// Shared input style
const INP = 'w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400 bg-white';
const LBL = 'text-[11px] text-gray-600 font-medium block mb-0.5';

export default function CreateOffer() {
  const navigate = useNavigate();
  const { loadCatalog } = useOfferStore();

  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState('');
  const [parsing, setParsing] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  // Dane rejestrowe
  const [companyName, setCompanyName] = useState('');
  const [legalForm, setLegalForm] = useState('');
  const [nip, setNip] = useState('');
  const [regCity, setRegCity] = useState('');
  const [regPostal, setRegPostal] = useState('');
  const [regStreet, setRegStreet] = useState('');
  const [regNumber, setRegNumber] = useState('');

  // Dane teleadresowe (mogą być inne niż rejestrowe)
  const [addrSameAsReg, setAddrSameAsReg] = useState(true);
  const [addrCity, setAddrCity] = useState('');
  const [addrPostal, setAddrPostal] = useState('');
  const [addrStreet, setAddrStreet] = useState('');
  const [addrNumber, setAddrNumber] = useState('');
  const [companyPhone, setCompanyPhone] = useState('');
  const [companyEmail, setCompanyEmail] = useState('');
  const [companyWww, setCompanyWww] = useState('');

  // Osoba kontaktowa
  const [contactFirstName, setContactFirstName] = useState('');
  const [contactLastName, setContactLastName] = useState('');
  const [contactRole, setContactRole] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [contactEmail, setContactEmail] = useState('');

  // GUS
  const [nipSource, setNipSource] = useState('');
  const [gusLoading, setGusLoading] = useState(false);
  const [gusError, setGusError] = useState('');

  // Zakładka aktywna
  const [activeTab, setActiveTab] = useState<'reg' | 'addr' | 'person' | 'order'>('reg');

  // Order data
  const [quantity, setQuantity] = useState(100);
  const [budget, setBudget] = useState(150);
  const [occasion, setOccasion] = useState('christmas');
  const [deadline, setDeadline] = useState('');
  const [requestedItems, setRequestedItems] = useState<string[]>([]);
  const [vagueRequests, setVagueRequests] = useState<string[]>([]);
  const [missingInfo, setMissingInfo] = useState<string[]>([]);
  const [confidence, setConfidence] = useState(0);

  // Dane adresowe do wysyłki — tryb
  const [deliveryMode, setDeliveryMode] = useState<'office' | 'reg' | 'custom'>('office');
  const [customDeliveryRecipient, setCustomDeliveryRecipient] = useState('');
  const [customDeliveryCompany, setCustomDeliveryCompany] = useState('');
  const [customDeliveryStreet, setCustomDeliveryStreet] = useState('');
  const [customDeliveryNumber, setCustomDeliveryNumber] = useState('');
  const [customDeliveryCity, setCustomDeliveryCity] = useState('');
  const [customDeliveryPostal, setCustomDeliveryPostal] = useState('');

  // ─── Step 1: Parse email ───

  const handleParseEmail = async () => {
    if (!email.trim()) return;
    setParsing(true);
    setError('');
    try {
      const { data } = await axios.post(`${API}/ai/parse-email`, { email_text: email });
      const d = data as ParsedData;

      // ── Firma ──
      if (d.client?.company_name) setCompanyName(d.client.company_name);
      if (d.client?.legal_form) setLegalForm(d.client.legal_form);

      // ── Adres z emaila → dane teleadresowe ──
      if (d.client?.address) {
        if (d.client.address.street) { setAddrStreet(d.client.address.street); setAddrSameAsReg(false); }
        if (d.client.address.number) setAddrNumber(d.client.address.number);
        if (d.client.address.city) setAddrCity(d.client.address.city);
        if (d.client.address.postal_code) setAddrPostal(d.client.address.postal_code);
      }
      if (d.client?.email) setCompanyEmail(d.client.email);
      if (d.client?.phone) setCompanyPhone(d.client.phone);
      if (d.client?.website) setCompanyWww(d.client.website);

      // ── Osoba kontaktowa ──
      if (d.client?.contact_person) {
        const parts = d.client.contact_person.trim().split(/\s+/);
        if (parts.length >= 2) {
          setContactFirstName(parts[0]);
          setContactLastName(parts.slice(1).join(' '));
        } else {
          setContactFirstName(d.client.contact_person);
        }
      }
      if (d.client?.contact_role) setContactRole(d.client.contact_role);
      if (d.client?.email) setContactEmail(d.client.email);
      if (d.client?.phone) setContactPhone(d.client.phone);

      // ── Zamówienie ──
      if (d.order?.quantity) setQuantity(d.order.quantity);
      if (d.order?.budget_per_unit) setBudget(d.order.budget_per_unit);
      if (d.order?.occasion) setOccasion(d.order.occasion);
      if (d.order?.deadline) setDeadline(d.order.deadline);

      // ── Dostawa — AI decyduje tryb ──
      if (d.delivery && (d.delivery.street || d.delivery.city)) {
        // Sprawdź czy adres dostawy = adres z emaila (biuro)
        const delivAddr = [d.delivery.street, d.delivery.number, d.delivery.city].filter(Boolean).join(' ').toLowerCase();
        const clientAddr = [d.client?.address?.street, d.client?.address?.number, d.client?.address?.city].filter(Boolean).join(' ').toLowerCase();
        if (clientAddr && delivAddr === clientAddr) {
          setDeliveryMode('office');
        } else {
          setDeliveryMode('custom');
          if (d.delivery.recipient_name) setCustomDeliveryRecipient(d.delivery.recipient_name);
          if (d.delivery.company_name) setCustomDeliveryCompany(d.delivery.company_name);
          if (d.delivery.street) setCustomDeliveryStreet(d.delivery.street);
          if (d.delivery.number) setCustomDeliveryNumber(d.delivery.number);
          if (d.delivery.city) setCustomDeliveryCity(d.delivery.city);
          if (d.delivery.postal_code) setCustomDeliveryPostal(d.delivery.postal_code);
        }
      }

      // ── Oczekiwania ──
      if (d.requested_items) setRequestedItems(d.requested_items);
      if (d.vague_requests) setVagueRequests(d.vague_requests);
      if (d.missing_info) setMissingInfo(d.missing_info);
      if (d.confidence) setConfidence(d.confidence);

      setStep(2);

      // ── Async: dane rejestrowe + www ──
      const parsedNip = d.client?.nip;
      const parsedName = d.client?.company_name;
      const parsedEmail = d.client?.email;

      // Background: szukaj www
      if (!d.client?.website && (parsedEmail || parsedName)) {
        axios.post(`${API}/ai/find-website`, {
          company_name: parsedName || '',
          email: parsedEmail || '',
        }).then(({ data: wwwResult }) => {
          if (wwwResult.found && wwwResult.website) setCompanyWww(wwwResult.website);
        }).catch(() => {});
      }

      // Background: dane rejestrowe
      if (parsedNip) {
        setNip(parsedNip);
        axios.post(`${API}/ai/gus-lookup`, { nip: parsedNip.replace(/[- ]/g, '') })
          .then(({ data: gus }) => { if (gus.found) fillFromGus(gus); })
          .catch(() => {});
      } else if (parsedName) {
        // 1. Szukaj w bazie
        axios.post(`${API}/ai/search-client-db`, { name: parsedName }).then(async ({ data: dbResult }) => {
          if (dbResult.found && dbResult.nip) {
            setNip(dbResult.nip);
            const { data: gus } = await axios.post(`${API}/ai/gus-lookup`, { nip: dbResult.nip });
            if (gus.found) fillFromGus(gus);
            return;
          }
          // 2. Szukaj w rejestrach (KRS/GUS) po nazwie
          const { data: regResult } = await axios.post(`${API}/ai/search-registry-by-name`, { name: parsedName });
          if (regResult.found && regResult.nip) {
            setNip(regResult.nip);
            const { data: gus } = await axios.post(`${API}/ai/gus-lookup`, { nip: regResult.nip });
            if (gus.found) fillFromGus(gus);
          }
        }).catch(() => {});
      }
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Błąd parsowania emaila');
    } finally {
      setParsing(false);
    }
  };

  /** Fill registration fields from GUS/MF lookup result */
  const fillFromGus = (gus: any) => {
    // Map GUS uppercase forms → select values
    const FORM_MAP: Record<string, string> = {
      'SP. Z O.O.': 'Sp. z o.o.', 'SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ': 'Sp. z o.o.',
      'S.A.': 'S.A.', 'SP.J.': 'Sp.j.', 'SPÓŁKA JAWNA': 'Spółka jawna',
      'SP.K.': 'Sp.k.', 'SP. KOMANDYTOWA': 'Sp. komandytowa',
    };

    if (gus.name) {
      const name = gus.name;
      let foundForm = '';
      let cleanName = name;
      for (const [pattern, selectVal] of Object.entries(FORM_MAP)) {
        if (name.toUpperCase().includes(pattern)) {
          foundForm = selectVal;
          cleanName = name.toUpperCase().replace(pattern, '').trim().replace(/^["\s-]+|["\s-]+$/g, '');
          break;
        }
      }
      setCompanyName(cleanName || name);
      if (foundForm) setLegalForm(foundForm);
    }
    if (gus.nip) setNip(gus.nip);
    if (gus.street) setRegStreet(gus.street);
    if (gus.building_number) setRegNumber(gus.building_number);
    if (gus.city) setRegCity(gus.city);
    if (gus.postal_code) setRegPostal(gus.postal_code);
    setNipSource(gus.source || 'MF / GUS');
  };

  // ─── GUS Lookup ───

  const handleGusLookup = async () => {
    if (!nip.replace(/[- ]/g, '').trim()) return;
    setGusLoading(true);
    setGusError('');
    try {
      const { data } = await axios.post(`${API}/ai/gus-lookup`, { nip: nip.replace(/[- ]/g, '') });
      if (data.found) {
        fillFromGus(data);
      } else {
        setGusError(data.error || 'Nie znaleziono w rejestrze. Wypełnij ręcznie.');
      }
    } catch {
      setGusError('Błąd połączenia z rejestrem. Wypełnij dane ręcznie.');
    } finally {
      setGusLoading(false);
    }
  };

  // ─── Create offer ───

  const handleCreate = async () => {
    if (!companyName || !quantity) return;
    setCreating(true);
    setError('');
    try {
      const fullRegAddress = [regStreet, regNumber].filter(Boolean).join(' ');
      const fullRegLine = [fullRegAddress, regPostal, regCity].filter(Boolean).join(', ');

      // Delivery address based on selected mode
      let deliveryLine = '';
      if (deliveryMode === 'office') {
        deliveryLine = [
          [addrSameAsReg ? regStreet : addrStreet, addrSameAsReg ? regNumber : addrNumber].filter(Boolean).join(' '),
          [addrSameAsReg ? regPostal : addrPostal, addrSameAsReg ? regCity : addrCity].filter(Boolean).join(' '),
        ].filter(Boolean).join(', ');
      } else if (deliveryMode === 'reg') {
        deliveryLine = fullRegLine;
      } else {
        deliveryLine = [
          customDeliveryRecipient,
          customDeliveryCompany,
          [customDeliveryStreet, customDeliveryNumber].filter(Boolean).join(' '),
          [customDeliveryPostal, customDeliveryCity].filter(Boolean).join(' '),
        ].filter(Boolean).join(', ');
      }

      const { data: client } = await axios.post(`${API}/clients`, {
        company_name: [companyName, legalForm].filter(Boolean).join(' '),
        nip: nip || undefined,
        contact_person: [contactFirstName, contactLastName].filter(Boolean).join(' ') || undefined,
        contact_role: contactRole || undefined,
        email: contactEmail || companyEmail || undefined,
        phone: contactPhone || companyPhone || undefined,
        address: fullRegLine || undefined,
        delivery_address: addrSameAsReg
          ? fullRegLine
          : [addrStreet, addrNumber, addrPostal, addrCity].filter(Boolean).join(', ') || undefined,
      });

      const { data: offer } = await axios.post(API, {
        client_id: client.id,
        occasion_code: occasion,
        quantity,
        deadline: deadline || undefined,
        delivery_address: deliveryLine || undefined,
        source_email: email || undefined,
      });

      await loadCatalog();
      navigate(`/offer/${offer.id}`);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Błąd tworzenia oferty');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />

      <nav className="bg-gray-950 px-6 py-2.5 flex items-center gap-3">
        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
        <span className="text-white font-bold text-sm">OfferCreator</span>
        <span className="text-gray-500 text-xs">/ Nowa oferta</span>
      </nav>

      <div className="max-w-3xl mx-auto py-8 px-6">

        {/* Error */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
            {error}
            <button onClick={() => setError('')} className="ml-2 text-red-500 font-bold">×</button>
          </div>
        )}

        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setStep(1)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${step === 1 ? 'bg-indigo-50 text-indigo-700' : 'text-green-600'}`}>
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${step === 1 ? 'bg-indigo-500 text-white' : 'bg-green-500 text-white'}`}>{step > 1 ? '✓' : '1'}</span>
            Email klienta
          </button>
          <div className="w-6 h-px bg-gray-200" />
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${step === 2 ? 'bg-indigo-50 text-indigo-700' : 'text-gray-400'}`}>
            <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${step === 2 ? 'bg-indigo-500 text-white' : 'bg-gray-200 text-gray-500'}`}>2</span>
            Weryfikacja danych
          </div>
          <div className="w-6 h-px bg-gray-200" />
          <span className="text-[10px] text-gray-300">3. Zestawy (konfigurator)</span>
        </div>

        {/* ═══ STEP 1: Email ═══ */}
        {step === 1 && (
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-1">Wczytaj zapytanie od klienta</h2>
            <p className="text-gray-500 text-sm mb-4">Wklej treść maila — AI przeanalizuje i wyciągnie dane do formularza.</p>

            <textarea
              rows={16}
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="Wklej tutaj treść maila od klienta..."
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 outline-none resize-none font-mono leading-relaxed"
            />

            <div className="flex items-center gap-3 mt-4">
              <button
                onClick={() => setEmail(SAMPLE_EMAIL)}
                className="px-4 py-2 text-sm font-semibold bg-white text-gray-700 border border-gray-200 rounded-lg hover:border-gray-300"
              >
                Wczytaj przykład
              </button>
              <button
                onClick={() => { setStep(2); }}
                className="px-4 py-2 text-sm font-semibold bg-white text-gray-700 border border-gray-200 rounded-lg hover:border-gray-300"
              >
                Pomiń — wypełnię ręcznie
              </button>
              <div className="flex-1" />
              <button
                onClick={handleParseEmail}
                disabled={!email.trim() || parsing}
                className={`px-5 py-2.5 text-sm font-bold text-white rounded-lg ${!email.trim() || parsing ? 'bg-gray-300' : 'bg-indigo-600 hover:bg-indigo-700'}`}
              >
                {parsing ? 'Analizuję...' : 'Analizuj z AI'}
              </button>
            </div>
          </div>
        )}

        {/* ═══ STEP 2: Verification ═══ */}
        {step === 2 && (
          <div>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-xl font-bold text-gray-900">Weryfikacja danych</h2>
              {confidence > 0 && (
                <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${confidence > 80 ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                  AI pewność: {confidence}%
                </span>
              )}
            </div>
            <p className="text-gray-500 text-sm mb-5">Sprawdź i uzupełnij dane wyciągnięte z emaila.</p>

            <div className="space-y-4">
              {/* Tabs */}
              <div className="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
                <div className="flex border-b bg-white">
                  {([
                    { id: 'reg' as const, label: 'Dane rejestrowe' },
                    { id: 'addr' as const, label: 'Dane teleadresowe' },
                    { id: 'person' as const, label: 'Osoba kontaktowa' },
                    { id: 'order' as const, label: 'Parametry zapytania' },
                  ]).map(tab => (
                    <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                      className={`flex-1 px-4 py-2.5 text-xs font-semibold transition-all ${
                        activeTab === tab.id
                          ? 'text-indigo-700 border-b-2 border-indigo-500 bg-indigo-50/50'
                          : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                      }`}>
                      {tab.label}
                    </button>
                  ))}
                </div>

                <div className="p-4">
                  {/* TAB: Dane rejestrowe */}
                  {activeTab === 'reg' && (
                    <div className="space-y-3">
                      <div className="grid grid-cols-3 gap-3">
                        <div className="col-span-2">
                          <label className={LBL}>Nazwa firmy *</label>
                          <input className={INP} value={companyName} onChange={e => setCompanyName(e.target.value)} />
                        </div>
                        <div>
                          <label className={LBL}>Forma prawna</label>
                          <select className={INP} value={legalForm} onChange={e => setLegalForm(e.target.value)}>
                            <option value="">— wybierz —</option>
                            {LEGAL_FORMS.map(f => <option key={f} value={f}>{f}</option>)}
                          </select>
                        </div>
                      </div>
                      <div>
                        <label className={LBL}>NIP</label>
                        <div className="flex gap-2">
                          <input className={`flex-1 ${INP}`} value={nip} onChange={e => setNip(e.target.value)} placeholder="5272876543" />
                          <button onClick={handleGusLookup} disabled={gusLoading || !nip.replace(/[- ]/g, '').trim()}
                            className={`px-3 py-1.5 text-xs font-semibold rounded-lg border whitespace-nowrap ${gusLoading ? 'bg-gray-100 text-gray-400 border-gray-200' : 'bg-white text-indigo-700 border-indigo-200 hover:bg-indigo-50'}`}>
                            {gusLoading ? 'Szukam...' : 'Pobierz z rejestru'}
                          </button>
                        </div>
                        {nipSource && <span className="text-[10px] text-green-600 font-medium mt-0.5 inline-block">✓ {nipSource}</span>}
                        {gusError && <span className="text-[10px] text-amber-600 mt-0.5 inline-block">{gusError}</span>}
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Ulica</label>
                          <input className={INP} value={regStreet} onChange={e => setRegStreet(e.target.value)} />
                        </div>
                        <div>
                          <label className={LBL}>Numer</label>
                          <input className={INP} value={regNumber} onChange={e => setRegNumber(e.target.value)} placeholder="10/5" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Miasto</label>
                          <input className={INP} value={regCity} onChange={e => setRegCity(e.target.value)} />
                        </div>
                        <div>
                          <label className={LBL}>Kod pocztowy</label>
                          <input className={INP} value={regPostal} onChange={e => setRegPostal(e.target.value)} placeholder="00-000" />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB: Dane teleadresowe */}
                  {activeTab === 'addr' && (
                    <div className="space-y-3">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" checked={addrSameAsReg} onChange={e => {
                          setAddrSameAsReg(e.target.checked);
                          if (e.target.checked) {
                            setAddrStreet(regStreet); setAddrNumber(regNumber);
                            setAddrPostal(regPostal); setAddrCity(regCity);
                          }
                        }} className="rounded border-gray-300" />
                        <span className="text-sm text-gray-700">Adres taki sam jak rejestrowy</span>
                      </label>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Ulica</label>
                          <input className={`${INP} ${addrSameAsReg ? '!bg-gray-100' : ''}`} value={addrSameAsReg ? regStreet : addrStreet} onChange={e => setAddrStreet(e.target.value)} disabled={addrSameAsReg} />
                        </div>
                        <div>
                          <label className={LBL}>Numer</label>
                          <input className={`${INP} ${addrSameAsReg ? '!bg-gray-100' : ''}`} value={addrSameAsReg ? regNumber : addrNumber} onChange={e => setAddrNumber(e.target.value)} disabled={addrSameAsReg} />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Miasto</label>
                          <input className={`${INP} ${addrSameAsReg ? '!bg-gray-100' : ''}`} value={addrSameAsReg ? regCity : addrCity} onChange={e => setAddrCity(e.target.value)} disabled={addrSameAsReg} />
                        </div>
                        <div>
                          <label className={LBL}>Kod pocztowy</label>
                          <input className={`${INP} ${addrSameAsReg ? '!bg-gray-100' : ''}`} value={addrSameAsReg ? regPostal : addrPostal} onChange={e => setAddrPostal(e.target.value)} disabled={addrSameAsReg} />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Email firmowy</label>
                          <input className={INP} value={companyEmail} onChange={e => setCompanyEmail(e.target.value)} />
                        </div>
                        <div>
                          <label className={LBL}>Strona www</label>
                          <input className={INP} value={companyWww} onChange={e => setCompanyWww(e.target.value)} placeholder="https://" />
                        </div>
                      </div>
                      <div>
                        <label className={LBL}>Telefon firmowy</label>
                        <input className={INP} value={companyPhone} onChange={e => setCompanyPhone(e.target.value)} />
                      </div>
                    </div>
                  )}

                  {/* TAB: Osoba kontaktowa */}
                  {activeTab === 'person' && (
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Imię</label>
                          <input className={INP} value={contactFirstName} onChange={e => setContactFirstName(e.target.value)} />
                        </div>
                        <div>
                          <label className={LBL}>Nazwisko</label>
                          <input className={INP} value={contactLastName} onChange={e => setContactLastName(e.target.value)} />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Email</label>
                          <input className={INP} value={contactEmail} onChange={e => setContactEmail(e.target.value)} />
                        </div>
                        <div>
                          <label className={LBL}>Telefon</label>
                          <input className={INP} value={contactPhone} onChange={e => setContactPhone(e.target.value)} />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Stanowisko</label>
                          <input className={INP} value={contactRole} onChange={e => setContactRole(e.target.value)} />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB: Parametry zapytania */}
                  {activeTab === 'order' && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className={LBL}>Ilość prezentów *</label>
                          <input type="number" className={`${INP} font-bold`} value={quantity} onChange={e => setQuantity(parseInt(e.target.value) || 0)} />
                        </div>
                        <div>
                          <label className={LBL}>Budżet netto / szt.</label>
                          <input type="number" className={`${INP} font-bold`} value={budget} onChange={e => setBudget(parseFloat(e.target.value) || 0)} />
                        </div>
                        <div>
                          <label className={LBL}>Okazja</label>
                          <select className={INP} value={occasion} onChange={e => setOccasion(e.target.value)}>
                            {OCCASIONS.map(o => <option key={o.code} value={o.code}>{o.name}</option>)}
                          </select>
                        </div>
                        <div>
                          <label className={LBL}>Termin realizacji</label>
                          <input type="date" className={INP} value={deadline} onChange={e => setDeadline(e.target.value)} />
                        </div>
                      </div>

                      {/* Dane adresowe do wysyłki — checkboxy */}
                      <div>
                        <div className="text-xs font-bold text-gray-500 mb-2 mt-2">ADRES WYSYŁKI</div>
                        <div className="space-y-2">
                          <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg hover:bg-white">
                            <input type="radio" name="delivery" checked={deliveryMode === 'office'} onChange={() => setDeliveryMode('office')} className="text-indigo-600" />
                            <div>
                              <span className="text-sm text-gray-800 font-medium">Adres biura</span>
                              {(addrSameAsReg ? regStreet : addrStreet) && (
                                <span className="text-xs text-gray-400 ml-2">
                                  ({[addrSameAsReg ? regStreet : addrStreet, addrSameAsReg ? regNumber : addrNumber].filter(Boolean).join(' ')}, {addrSameAsReg ? regCity : addrCity})
                                </span>
                              )}
                            </div>
                          </label>
                          <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg hover:bg-white">
                            <input type="radio" name="delivery" checked={deliveryMode === 'reg'} onChange={() => setDeliveryMode('reg')} className="text-indigo-600" />
                            <div>
                              <span className="text-sm text-gray-800 font-medium">Adres rejestrowy</span>
                              {regStreet && (
                                <span className="text-xs text-gray-400 ml-2">
                                  ({[regStreet, regNumber].filter(Boolean).join(' ')}, {regCity})
                                </span>
                              )}
                            </div>
                          </label>
                          <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg hover:bg-white">
                            <input type="radio" name="delivery" checked={deliveryMode === 'custom'} onChange={() => setDeliveryMode('custom')} className="text-indigo-600" />
                            <span className="text-sm text-gray-800 font-medium">Inny adres</span>
                          </label>
                          {deliveryMode === 'custom' && (
                            <div className="space-y-3 ml-6 mt-1">
                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className={LBL}>Imię i nazwisko odbiorcy</label>
                                  <input className={INP} value={customDeliveryRecipient} onChange={e => setCustomDeliveryRecipient(e.target.value)} />
                                </div>
                                <div>
                                  <label className={LBL}>Nazwa firmy</label>
                                  <input className={INP} value={customDeliveryCompany} onChange={e => setCustomDeliveryCompany(e.target.value)} />
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className={LBL}>Ulica</label>
                                  <input className={INP} value={customDeliveryStreet} onChange={e => setCustomDeliveryStreet(e.target.value)} />
                                </div>
                                <div>
                                  <label className={LBL}>Numer</label>
                                  <input className={INP} value={customDeliveryNumber} onChange={e => setCustomDeliveryNumber(e.target.value)} />
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className={LBL}>Miasto</label>
                                  <input className={INP} value={customDeliveryCity} onChange={e => setCustomDeliveryCity(e.target.value)} />
                                </div>
                                <div>
                                  <label className={LBL}>Kod pocztowy</label>
                                  <input className={INP} value={customDeliveryPostal} onChange={e => setCustomDeliveryPostal(e.target.value)} placeholder="00-000" />
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Oczekiwania klienta */}
                      {requestedItems.length > 0 && (
                        <div>
                          <div className="text-xs font-bold text-gray-500 mb-2">OCZEKIWANIA KLIENTA</div>
                          {requestedItems.map((item, i) => (
                            <div key={i} className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-lg mb-1 text-sm text-gray-800">
                              <span className="text-green-500 text-xs">✓</span>{item}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Do doprecyzowania */}
                      {vagueRequests.length > 0 && (
                        <div className="bg-amber-50 rounded-lg border border-amber-200 p-3">
                          <div className="text-xs font-bold text-amber-700 mb-1">DO DOPRECYZOWANIA</div>
                          {vagueRequests.map((v, i) => (
                            <div key={i} className="text-sm text-amber-800 py-0.5 ml-3">— {v}</div>
                          ))}
                        </div>
                      )}

                      {/* Brakujące info */}
                      {missingInfo.length > 0 && (
                        <div className="bg-blue-50 rounded-lg border border-blue-200 p-3">
                          <div className="text-xs font-bold text-blue-700 mb-1">BRAKUJĄCE INFORMACJE</div>
                          {missingInfo.map((m, i) => (
                            <div key={i} className="text-sm text-blue-800 py-0.5 ml-3">— {m}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3 mt-6">
              <button
                onClick={() => setStep(1)}
                className="px-4 py-2 text-sm font-semibold bg-white text-gray-700 border border-gray-200 rounded-lg"
              >
                ← Wróć do emaila
              </button>
              <div className="flex-1" />
              <button
                onClick={handleCreate}
                disabled={!companyName || !quantity || creating}
                className={`px-6 py-2.5 text-sm font-bold text-white rounded-lg ${!companyName || !quantity || creating ? 'bg-gray-300' : 'bg-indigo-600 hover:bg-indigo-700'}`}
              >
                {creating ? 'Tworzę...' : 'Utwórz ofertę → konfigurator'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
