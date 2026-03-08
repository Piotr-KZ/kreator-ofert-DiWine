import { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { authApi } from '../../api/auth';
import { Btn, Fld } from '@/components/ui';
import { APP_CONFIG } from '@/config/app.config';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <div className="bg-white rounded-2xl shadow-md w-full max-w-sm p-8 text-center">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </div>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Invalid Reset Link</h2>
          <p className="text-sm text-gray-500 mb-6">This password reset link is invalid or has expired.</p>
          <Link to="/forgot-password"><Btn variant="primary">Request New Link</Btn></Link>
        </div>
      </div>
    );
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) { setError('Passwords do not match'); return; }
    if (password.length < 8) { setError('Password must be at least 8 characters'); return; }
    setLoading(true);
    setError(null);
    try {
      await authApi.resetPassword(token, password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password');
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
            <h2 className="text-lg font-bold text-gray-900 mb-2">Password Reset Successful</h2>
            <p className="text-sm text-gray-500">Redirecting to login...</p>
          </div>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${APP_CONFIG.logo.gradient} flex items-center justify-center mx-auto mb-3`}>
                <span className="text-white font-extrabold text-lg">{APP_CONFIG.logo.icon}</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">Set New Password</h1>
              <p className="text-sm text-gray-500 mt-1">Enter your new password</p>
            </div>
            {error && <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4"><p className="text-sm text-red-700">{error}</p></div>}
            <form onSubmit={onSubmit} className="space-y-4">
              <Fld label="New Password" type="password" placeholder="Min. 8 characters" value={password} onChange={setPassword} />
              <Fld label="Confirm Password" type="password" placeholder="Confirm password" value={confirmPassword} onChange={setConfirmPassword} />
              <Btn type="submit" loading={loading} className="w-full">Reset Password</Btn>
            </form>
            <div className="mt-6 text-center"><Link to="/login" className="text-sm text-gray-500 hover:text-gray-700">Back to Login</Link></div>
          </>
        )}
      </div>
    </div>
  );
}
