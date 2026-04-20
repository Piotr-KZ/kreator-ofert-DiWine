import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Btn, Fld } from '@/components/ui';
import { APP_CONFIG } from '@/config/app.config';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, error, clearError } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const errors: Record<string, string> = {};
    if (!email) errors.email = 'Podaj adres email';
    else if (!/\S+@\S+\.\S+/.test(email)) errors.email = 'Podaj poprawny adres email';
    if (!password) errors.password = 'Podaj haslo';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    clearError();
    try {
      await login(email, password, rememberMe);
      navigate('/panel');
    } catch {
      // error handled by store
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
    >
      <div className="bg-white rounded-2xl shadow-md w-full max-w-sm p-8">
        <div className="text-center mb-6">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${APP_CONFIG.logo.gradient} flex items-center justify-center mx-auto mb-3`}>
            <span className="text-white font-extrabold text-lg">{APP_CONFIG.logo.icon}</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900">{APP_CONFIG.name}</h1>
          <p className="text-sm text-gray-500 mt-1">Zaloguj sie do swojego konta</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4 flex items-center justify-between">
            <p className="text-sm text-red-700">{typeof error === 'string' ? error : 'Logowanie nie powiodlo sie.'}</p>
            <button onClick={clearError} className="text-red-400 hover:text-red-600 ml-2 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-4">
          <Fld label="Email" type="email" placeholder="jan@example.com" value={email} onChange={setEmail} error={formErrors.email} />
          <Fld label="Haslo" type="password" placeholder="Haslo" value={password} onChange={setPassword} error={formErrors.password} />

          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-600">Zapamietaj mnie</span>
            </label>
            <Link to="/forgot-password" className="text-sm text-indigo-600 hover:text-indigo-700">
              Nie pamietasz hasla?
            </Link>
          </div>

          <Btn type="submit" loading={loading} className="w-full">
            Zaloguj sie
          </Btn>
        </form>

        <div className="mt-6 text-center border-t border-gray-200 pt-4">
          <p className="text-sm text-gray-500">
            Nie masz konta?{' '}
            <Link to="/register" className="text-indigo-600 hover:text-indigo-700 font-medium">Zarejestruj sie</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
