import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Btn, Fld } from '@/components/ui';
import { APP_CONFIG } from '@/config/app.config';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);

  const validate = () => {
    const errors: Record<string, string> = {};
    if (!fullName.trim()) errors.fullName = 'Podaj imię';
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

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    clearError();
    try {
      await register({
        email,
        password,
        full_name: fullName.trim(),
        organization_name: fullName.trim(),
      });
      navigate('/onboarding');
    } catch {
      // error handled by store
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <div className="bg-white rounded-2xl shadow-md w-full max-w-md p-8">
        <div className="text-center mb-6">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${APP_CONFIG.logo.gradient} flex items-center justify-center mx-auto mb-3`}>
            <span className="text-white font-extrabold text-lg">{APP_CONFIG.logo.icon}</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900">Utwórz konto</h1>
          <p className="text-sm text-gray-500 mt-1">Zarejestruj się i stwórz swoją stronę</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4 flex items-center justify-between">
            <p className="text-sm text-red-700">{typeof error === 'string' ? error : 'Rejestracja nie powiodła się.'}</p>
            <button onClick={clearError} className="text-red-400 hover:text-red-600 ml-2 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-4">
          <Fld label="Imię" placeholder="Jan" value={fullName} onChange={setFullName} error={formErrors.fullName} />
          <Fld label="Email" type="email" placeholder="jan@example.com" value={email} onChange={setEmail} error={formErrors.email} />
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

          <Btn type="submit" loading={loading} className="w-full">
            Zarejestruj się
          </Btn>
        </form>

        <div className="mt-6 text-center border-t border-gray-200 pt-4">
          <p className="text-sm text-gray-500">Masz już konto?{' '}<Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">Zaloguj się</Link></p>
        </div>
      </div>
    </div>
  );
}
