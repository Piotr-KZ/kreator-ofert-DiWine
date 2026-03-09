import { useEffect, useState } from 'react';
import { useOrgStore } from '@/store/orgStore';
import { organizationsApi } from '@/api/organizations';
import { Btn, Fld, SectionCard } from '@/components/ui';
import GUSLookup from '@/components/shared/GUSLookup';
import type { GUSData } from '@/api/gus';

const legalForms = [
  'Sp. z o.o.', 'JDG', 'S.A.', 'Sp. jawna', 'Sp. komandytowa',
  'Sp. cywilna', 'Sp. partnerska', 'Sp. komandytowo-akcyjna',
  'Fundacja', 'Stowarzyszenie', 'Inna',
];

export default function CompanyTab() {
  const { organization, fetchOrganization, updateOrganization } = useOrgStore();
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState('');

  // Form fields
  const [name, setName] = useState('');
  const [nip, setNip] = useState('');
  const [regon, setRegon] = useState('');
  const [krs, setKrs] = useState('');
  const [legalForm, setLegalForm] = useState('');
  const [website, setWebsite] = useState('');
  const [street, setStreet] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('Polska');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [rodoName, setRodoName] = useState('');
  const [rodoEmail, setRodoEmail] = useState('');

  useEffect(() => {
    fetchOrganization();
  }, []);

  useEffect(() => {
    if (organization) {
      setName(organization.name || '');
      setNip(organization.nip || '');
      setRegon(organization.regon || '');
      setKrs(organization.krs || '');
      setLegalForm(organization.legal_form || '');
      setWebsite(organization.website || '');
      setStreet(organization.billing_street || '');
      setPostalCode(organization.billing_postal_code || '');
      setCity(organization.billing_city || '');
      setCountry(organization.billing_country || 'Polska');
      setEmail(organization.email || '');
      setPhone(organization.phone || '');
      setRodoName(organization.rodo_inspector_name || '');
      setRodoEmail(organization.rodo_inspector_email || '');
      setLogoPreview(organization.logo_url || '');
    }
  }, [organization]);

  const handleGUSData = (data: GUSData) => {
    if (data.name) setName(data.name);
    if (data.regon) setRegon(data.regon);
    if (data.krs) setKrs(data.krs);
    if (data.legal_form) setLegalForm(data.legal_form);
    if (data.street) setStreet(data.street);
    if (data.city) setCity(data.city);
    if (data.postal_code) setPostalCode(data.postal_code);
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      setMsg('Logo max 2MB');
      return;
    }
    setLogoFile(file);
    setLogoPreview(URL.createObjectURL(file));
  };

  const save = async () => {
    if (!organization) return;
    setLoading(true);
    setMsg('');
    try {
      if (logoFile) {
        await organizationsApi.uploadLogo(organization.id, logoFile);
      }
      await updateOrganization({
        name, nip, regon, krs, legal_form: legalForm, website,
        billing_street: street, billing_postal_code: postalCode,
        billing_city: city, billing_country: country,
        email, phone,
        rodo_inspector_name: rodoName, rodo_inspector_email: rodoEmail,
      });
      setMsg('Zapisano');
      setLogoFile(null);
    } catch {
      setMsg('Błąd podczas zapisu');
    } finally {
      setLoading(false);
    }
  };

  const isBusiness = organization?.type === 'business' || !organization?.type;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">
        {isBusiness ? 'Firma' : 'Dane osobowe'}
      </h2>

      {isBusiness ? (
        <>
          <SectionCard title="Dane firmy">
            <div className="space-y-4">
              <GUSLookup initialNip={nip} onResult={handleGUSData} />
              <Fld label="Nazwa firmy" value={name} onChange={setName} />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Forma prawna</label>
                <select
                  value={legalForm}
                  onChange={(e) => setLegalForm(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                >
                  <option value="">Wybierz</option>
                  {legalForms.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Fld label="REGON" value={regon} onChange={setRegon} />
                <Fld label="KRS" value={krs} onChange={setKrs} placeholder="Opcjonalne" />
              </div>
              <Fld label="Strona www" type="url" value={website} onChange={setWebsite} placeholder="https://" />
            </div>
          </SectionCard>

          <SectionCard title="Adres">
            <div className="space-y-4">
              <Fld label="Ulica i numer" value={street} onChange={setStreet} />
              <div className="grid grid-cols-2 gap-4">
                <Fld label="Kod pocztowy" value={postalCode} onChange={setPostalCode} placeholder="00-000" />
                <Fld label="Miasto" value={city} onChange={setCity} />
              </div>
              <Fld label="Kraj" value={country} onChange={setCountry} />
            </div>
          </SectionCard>

          <SectionCard title="Kontakt firmowy">
            <div className="space-y-4">
              <Fld label="Email firmowy" type="email" value={email} onChange={setEmail} />
              <Fld label="Telefon firmowy" type="tel" value={phone} onChange={setPhone} placeholder="+48 123 456 789" />
            </div>
          </SectionCard>

          <SectionCard title="Logo firmy">
            <div className="flex items-center gap-4">
              {logoPreview ? (
                <img src={logoPreview} alt="Logo" className="w-20 h-20 rounded-xl object-contain border border-gray-200 p-1" />
              ) : (
                <div className="w-20 h-20 rounded-xl bg-gray-100 flex items-center justify-center text-gray-400 text-xs">
                  Brak logo
                </div>
              )}
              <label className="cursor-pointer">
                <span className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">Zmień logo</span>
                <input type="file" accept="image/jpeg,image/png,image/svg+xml,image/webp" className="hidden" onChange={handleLogoChange} />
              </label>
            </div>
            <p className="text-xs text-gray-400 mt-2">JPG, PNG, SVG, WebP — max 2 MB</p>
          </SectionCard>

          <SectionCard title="Inspektor Ochrony Danych (RODO)">
            <div className="space-y-4">
              <p className="text-sm text-gray-500">
                Jeśli Twoja firma ma wyznaczonego Inspektora Ochrony Danych, podaj jego dane kontaktowe.
              </p>
              <Fld label="Imię i nazwisko IOD" value={rodoName} onChange={setRodoName} />
              <Fld label="Email IOD" type="email" value={rodoEmail} onChange={setRodoEmail} />
            </div>
          </SectionCard>
        </>
      ) : (
        <SectionCard title="Dane osobowe">
          <div className="space-y-4">
            <Fld label="Imię i nazwisko" value={name} onChange={setName} />
            <Fld label="Adres" value={street} onChange={setStreet} placeholder="Opcjonalne" />
            <Fld label="Telefon" type="tel" value={phone} onChange={setPhone} />
          </div>
        </SectionCard>
      )}

      {msg && (
        <p className={`text-sm ${msg.includes('Błąd') ? 'text-red-600' : 'text-green-600'}`}>{msg}</p>
      )}
      <Btn onClick={save} loading={loading}>Zapisz wszystko</Btn>
    </div>
  );
}
