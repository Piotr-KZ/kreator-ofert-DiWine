import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { organizationsApi } from '../api/organizations';
import { Btn, Fld } from '@/components/ui';
import { APP_CONFIG } from '@/config/app.config';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [orgName, setOrgName] = useState('');
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orgName.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await organizationsApi.create({ name: orgName });
      navigate('/panel');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create organization');
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
          <h1 className="text-xl font-bold text-gray-900">Witaj w {APP_CONFIG.name}!</h1>
          <p className="text-sm text-gray-500 mt-1">Utworz organizacje, zeby zaczac</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-4">
          <Fld label="Nazwa organizacji" placeholder="Moja firma" value={orgName} onChange={setOrgName} />
          <Btn type="submit" loading={loading} className="w-full">Utworz</Btn>
        </form>

        <div className="text-center mt-4">
          <button onClick={() => navigate('/panel')} className="text-sm text-gray-400 hover:text-gray-600">
            Pomin na razie
          </button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-4">Mozesz to zmienic pozniej w ustawieniach</p>
      </div>
    </div>
  );
}
