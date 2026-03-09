import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Btn, Fld, Tile } from '@/components/ui';
import { APP_CONFIG } from '@/config/app.config';
import GUSLookup from '@/components/shared/GUSLookup';
import type { GUSData } from '@/api/gus';

type AccountType = 'business' | 'individual' | null;
type Step = 1 | 2 | 3;

const LEGAL_FORMS = [
  'Osoba fizyczna',
  'Sp. cywilna',
  'Sp. z o.o.',
  'Sp. jawna',
  'Sp. komandytowa',
  'S.A.',
  'Sp. komandytowo-akcyjna',
  'Sp. partnerska',
  'Jednoosobowa działalność gospodarcza',
];

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<Step>(1);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Step 1
  const [accountType, setAccountType] = useState<AccountType>(null);

  // Step 2A — business
  const [companyName, setCompanyName] = useState('');
  const [nip, setNip] = useState('');
  const [regon, setRegon] = useState('');
  const [krs, setKrs] = useState('');
  const [legalForm, setLegalForm] = useState('');
  const [street, setStreet] = useState('');
  const [city, setCity] = useState('');
  const [postalCode, setPostalCode] = useState('');

  // Step 2B — individual
  const [fullName, setFullName] = useState('');

  // Step 3
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);

  const handleGUSResult = (data: GUSData) => {
    setCompanyName(data.name || '');
    setNip(data.nip || '');
    setRegon(data.regon || '');
    setKrs(data.krs || '');
    setLegalForm(data.legal_form || '');
    setStreet(data.street || '');
    setCity(data.city || '');
    setPostalCode(data.postal_code || '');
  };

  const validateStep2 = () => {
    const errors: Record<string, string> = {};
    if (accountType === 'business') {
      if (!companyName) errors.companyName = 'Podaj nazwę firmy';
    } else {
      if (!fullName) errors.fullName = 'Podaj imię i nazwisko';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateStep3 = () => {
    const errors: Record<string, string> = {};
    if (!email) errors.email = 'Podaj adres email';
    else if (!/\S+@\S+\.\S+/.test(email)) errors.email = 'Podaj poprawny adres email';
    if (!password) errors.password = 'Podaj hasło';
    else if (password.length < 8) errors.password = 'Hasło musi mieć min. 8 znaków';
    else {
      if (!/[A-Z]/.test(password)) errors.password = 'Hasło musi zawierać wielką literę';
      else if (!/[a-z]/.test(password)) errors.password = 'Hasło musi zawierać małą literę';
      else if (!/\d/.test(password)) errors.password = 'Hasło musi zawierać cyfrę';
    }
    if (!acceptTerms) errors.terms = 'Musisz zaakceptować regulamin';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const goToStep2 = () => {
    if (!accountType) return;
    setFormErrors({});
    setStep(2);
  };

  const goToStep3 = () => {
    if (!validateStep2()) return;
    setFormErrors({});
    setStep(3);
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateStep3()) return;
    setLoading(true);
    clearError();
    try {
      const data: any = { email, password };
      if (accountType === 'business') {
        data.full_name = companyName;
        data.organization_name = companyName;
        data.account_type = 'business';
        data.nip = nip || undefined;
        data.regon = regon || undefined;
        data.krs = krs || undefined;
        data.legal_form = legalForm || undefined;
        data.street = street || undefined;
        data.city = city || undefined;
        data.postal_code = postalCode || undefined;
      } else {
        data.full_name = fullName;
        data.organization_name = fullName;
        data.account_type = 'individual';
      }
      await register(data);
      navigate('/onboarding');
    } catch {
      // error handled by store
    } finally {
      setLoading(false);
    }
  };

  const stepIndicator = (
    <div className="flex items-center justify-center gap-2 mb-6">
      {[1, 2, 3].map((s) => (
        <div key={s} className="flex items-center gap-2">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${
              s === step
                ? 'bg-indigo-600 text-white'
                : s < step
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-200 text-gray-500'
            }`}
          >
            {s < step ? '✓' : s}
          </div>
          {s < 3 && <div className={`w-8 h-0.5 ${s < step ? 'bg-green-500' : 'bg-gray-200'}`} />}
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <div className="bg-white rounded-2xl shadow-md w-full max-w-md p-8">
        <div className="text-center mb-4">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${APP_CONFIG.logo.gradient} flex items-center justify-center mx-auto mb-3`}>
            <span className="text-white font-extrabold text-lg">{APP_CONFIG.logo.icon}</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900">Utwórz konto</h1>
          <p className="text-sm text-gray-500 mt-1">
            {step === 1 && 'Wybierz typ konta'}
            {step === 2 && (accountType === 'business' ? 'Dane firmy' : 'Dane osobowe')}
            {step === 3 && 'Dane logowania'}
          </p>
        </div>

        {stepIndicator}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4 flex items-center justify-between">
            <p className="text-sm text-red-700">{typeof error === 'string' ? error : 'Rejestracja nie powiodła się.'}</p>
            <button onClick={clearError} className="text-red-400 hover:text-red-600 ml-2 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        )}

        {/* Step 1: Account type */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Tile on={accountType === 'business'} onClick={() => setAccountType('business')}>
                <div className="text-center">
                  <div className="text-2xl mb-1">🏢</div>
                  <div className="font-semibold text-sm">Firma</div>
                  <p className="text-xs text-gray-500 mt-1">Konto firmowe z NIP</p>
                </div>
              </Tile>
              <Tile on={accountType === 'individual'} onClick={() => setAccountType('individual')}>
                <div className="text-center">
                  <div className="text-2xl mb-1">👤</div>
                  <div className="font-semibold text-sm">Osoba prywatna</div>
                  <p className="text-xs text-gray-500 mt-1">Konto indywidualne</p>
                </div>
              </Tile>
            </div>
            <Btn onClick={goToStep2} disabled={!accountType} className="w-full">
              Dalej
            </Btn>
          </div>
        )}

        {/* Step 2A: Business */}
        {step === 2 && accountType === 'business' && (
          <div className="space-y-4">
            <GUSLookup onResult={handleGUSResult} initialNip={nip} />
            <Fld label="Nazwa firmy" placeholder="np. Firma Sp. z o.o." value={companyName} onChange={setCompanyName} error={formErrors.companyName} />
            <div className="grid grid-cols-2 gap-3">
              <Fld label="REGON" placeholder="123456789" value={regon} onChange={setRegon} />
              <Fld label="KRS" placeholder="0000123456" value={krs} onChange={setKrs} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Forma prawna</label>
              <select
                value={legalForm}
                onChange={(e) => setLegalForm(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none transition-all focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
              >
                <option value="">— wybierz —</option>
                {LEGAL_FORMS.map((f) => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
            </div>
            <Fld label="Ulica" placeholder="ul. Przykładowa 10" value={street} onChange={setStreet} />
            <div className="grid grid-cols-2 gap-3">
              <Fld label="Kod pocztowy" placeholder="00-000" value={postalCode} onChange={setPostalCode} />
              <Fld label="Miasto" placeholder="Warszawa" value={city} onChange={setCity} />
            </div>
            <div className="flex gap-3">
              <Btn variant="ghost" onClick={() => setStep(1)} className="flex-1">Wstecz</Btn>
              <Btn onClick={goToStep3} className="flex-1">Dalej</Btn>
            </div>
          </div>
        )}

        {/* Step 2B: Individual */}
        {step === 2 && accountType === 'individual' && (
          <div className="space-y-4">
            <Fld label="Imię i nazwisko" placeholder="Jan Kowalski" value={fullName} onChange={setFullName} error={formErrors.fullName} />
            <div className="flex gap-3">
              <Btn variant="ghost" onClick={() => setStep(1)} className="flex-1">Wstecz</Btn>
              <Btn onClick={goToStep3} className="flex-1">Dalej</Btn>
            </div>
          </div>
        )}

        {/* Step 3: Credentials */}
        {step === 3 && (
          <form onSubmit={onSubmit} className="space-y-4">
            <Fld label="Email" type="email" placeholder="ty@firma.pl" value={email} onChange={setEmail} error={formErrors.email} />
            <Fld label="Hasło" type="password" placeholder="Min. 8 znaków, wielka litera, cyfra" value={password} onChange={setPassword} error={formErrors.password} />
            <label className="flex items-start gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="mt-1 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-xs text-gray-500">
                Akceptuję <a href="/terms" className="text-indigo-600 hover:underline">Regulamin</a> i{' '}
                <a href="/privacy" className="text-indigo-600 hover:underline">Politykę prywatności</a>
              </span>
            </label>
            {formErrors.terms && <p className="text-xs text-red-500">{formErrors.terms}</p>}
            <div className="flex gap-3">
              <Btn variant="ghost" onClick={() => setStep(2)} type="button" className="flex-1">Wstecz</Btn>
              <Btn type="submit" loading={loading} className="flex-1">Zarejestruj się</Btn>
            </div>
          </form>
        )}

        <div className="mt-6 text-center border-t border-gray-200 pt-4">
          <p className="text-sm text-gray-500">Masz już konto?{' '}<Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">Zaloguj się</Link></p>
        </div>
      </div>
    </div>
  );
}
