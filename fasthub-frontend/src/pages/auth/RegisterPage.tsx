import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Btn, Fld } from '@/components/ui';
import { APP_CONFIG } from '@/config/app.config';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const errors: Record<string, string> = {};
    if (!fullName) errors.fullName = 'Please enter your full name';
    if (!email) errors.email = 'Please enter your email';
    else if (!/\S+@\S+\.\S+/.test(email)) errors.email = 'Please enter a valid email';
    if (!password) errors.password = 'Please enter a password';
    else if (password.length < 8) errors.password = 'Password must be at least 8 characters';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    clearError();
    try {
      await register({ email, password, full_name: fullName });
      navigate('/onboarding');
    } catch {
      // error handled by store
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <div className="bg-white rounded-2xl shadow-md w-full max-w-sm p-8">
        <div className="text-center mb-6">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${APP_CONFIG.logo.gradient} flex items-center justify-center mx-auto mb-3`}>
            <span className="text-white font-extrabold text-lg">{APP_CONFIG.logo.icon}</span>
          </div>
          <h1 className="text-xl font-bold text-gray-900">Create Account</h1>
          <p className="text-sm text-gray-500 mt-1">Sign up for {APP_CONFIG.name} in seconds</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4 flex items-center justify-between">
            <p className="text-sm text-red-700">{typeof error === 'string' ? error : 'Registration failed.'}</p>
            <button onClick={clearError} className="text-red-400 hover:text-red-600 ml-2 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-4">
          <Fld label="Full Name" placeholder="John Doe" value={fullName} onChange={setFullName} error={formErrors.fullName} />
          <Fld label="Email" type="email" placeholder="you@example.com" value={email} onChange={setEmail} error={formErrors.email} />
          <Fld label="Password" type="password" placeholder="Min. 8 characters" value={password} onChange={setPassword} error={formErrors.password} />
          <Btn type="submit" loading={loading} className="w-full">Create Account</Btn>
          <p className="text-xs text-gray-400 text-center">By signing up, you agree to our Terms of Service and Privacy Policy</p>
        </form>

        <div className="mt-6 text-center border-t border-gray-200 pt-4">
          <p className="text-sm text-gray-500">Already have an account?{' '}<Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">Sign in</Link></p>
        </div>
      </div>
    </div>
  );
}
