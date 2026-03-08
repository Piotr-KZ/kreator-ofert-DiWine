import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authApi } from '../../api/auth';
import { Btn, Fld } from '@/components/ui';
import { APP_CONFIG } from '@/config/app.config';

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [email, setEmail] = useState('');

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !/\S+@\S+\.\S+/.test(email)) return;
    setLoading(true);
    setError(null);
    try {
      await authApi.forgotPassword(email);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send reset email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <div className="bg-white rounded-2xl shadow-md w-full max-w-sm p-8">
        {success ? (
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
            </div>
            <h2 className="text-lg font-bold text-gray-900 mb-2">Check Your Email</h2>
            <p className="text-sm text-gray-500 mb-6">We've sent you a password reset link. Please check your inbox.</p>
            <Link to="/login"><Btn variant="primary">Back to Login</Btn></Link>
          </div>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${APP_CONFIG.logo.gradient} flex items-center justify-center mx-auto mb-3`}>
                <span className="text-white font-extrabold text-lg">{APP_CONFIG.logo.icon}</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">Reset Password</h1>
              <p className="text-sm text-gray-500 mt-1">Enter your email to receive a reset link</p>
            </div>
            {error && <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4"><p className="text-sm text-red-700">{error}</p></div>}
            <form onSubmit={onSubmit} className="space-y-4">
              <Fld label="Email" type="email" placeholder="you@example.com" value={email} onChange={setEmail} />
              <Btn type="submit" loading={loading} className="w-full">Send Reset Link</Btn>
            </form>
            <div className="mt-6 text-center"><Link to="/login" className="text-sm text-gray-500 hover:text-gray-700">Back to Login</Link></div>
          </>
        )}
      </div>
    </div>
  );
}
