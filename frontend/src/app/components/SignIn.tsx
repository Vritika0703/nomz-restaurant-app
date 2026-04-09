import { useState } from 'react';
import { Footer } from './Footer';
import { apiFetch } from '../api';

export function SignIn({
  onBackClick,
  onSignIn,
  onForgotPassword,
  onTwoFactorRequired,
}: {
  onBackClick: () => void;
  onSignIn: (accountType: 'diner' | 'restaurant' | 'admin', username: string) => void;
  onForgotPassword?: () => void;
  onTwoFactorRequired?: () => void;
}) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const username = (document.getElementById('username') as HTMLInputElement)?.value?.trim() ?? '';
    const password = (document.getElementById('password') as HTMLInputElement)?.value ?? '';
    if (!username || !password) {
      setError('Enter username and password.');
      return;
    }
    setLoading(true);
    try {
      const r = await apiFetch('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) {
        setError(typeof data.error === 'string' ? data.error : 'Login failed.');
        return;
      }
      // Check if 2FA is required
      if (data.requires_2fa) {
        onTwoFactorRequired?.();
        return;
      }
      let role: 'diner' | 'restaurant' | 'admin' = 'diner';
      if (data.is_staff) role = 'admin';
      else if (data.role === 'restaurant') role = 'restaurant';
      onSignIn(role, data.username);
    } catch {
      setError('Network error. Is Django running (and VITE_API_BASE_URL / proxy set)?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
      <button
        onClick={onBackClick}
        className="absolute top-8 left-8 p-2 rounded-lg transition-all hover:bg-opacity-10"
        style={{ color: '#E06E7F' }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
        aria-label="Go back"
        type="button"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
      </button>

      <div className="flex-1 flex flex-col items-center justify-center px-8 py-20">
        <h1 className="text-3xl mb-10" style={{ fontFamily: 'Montserrat, sans-serif', color: '#E06E7F' }}>
          nomz
        </h1>

        <div className="w-full max-w-md">
          <h2 className="text-xl mb-6 text-center" style={{ fontFamily: 'Montserrat, sans-serif', color: '#333' }}>
            Log In to Your Account
          </h2>

          {error && (
            <p className="text-sm mb-4 text-center" style={{ fontFamily: 'Montserrat, sans-serif', color: '#b91c1c' }}>
              {error}
            </p>
          )}

          <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-2">
              <label htmlFor="username" className="text-xs" style={{ fontFamily: 'Montserrat, sans-serif', color: '#666' }}>
                Username
              </label>
              <input
                type="text"
                id="username"
                autoComplete="username"
                className="px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                style={{
                  borderColor: 'rgba(224, 110, 127, 0.2)',
                  fontFamily: 'Montserrat, sans-serif',
                  backgroundColor: 'transparent',
                }}
                onFocus={(e) => (e.target.style.borderColor = '#E06E7F')}
                onBlur={(e) => (e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)')}
                placeholder="Enter your username"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="password" className="text-xs" style={{ fontFamily: 'Montserrat, sans-serif', color: '#666' }}>
                Password
              </label>
              <input
                type="password"
                id="password"
                autoComplete="current-password"
                className="px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                style={{
                  borderColor: 'rgba(224, 110, 127, 0.2)',
                  fontFamily: 'Montserrat, sans-serif',
                  backgroundColor: 'transparent',
                }}
                onFocus={(e) => (e.target.style.borderColor = '#E06E7F')}
                onBlur={(e) => (e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)')}
                placeholder="Enter your password"
              />
            </div>

            <div className="flex justify-end">
              {onForgotPassword && (
                <button
                  type="button"
                  onClick={onForgotPassword}
                  className="text-xs transition-all"
                  style={{
                    color: '#999',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    fontFamily: 'Montserrat, sans-serif',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = '#E06E7F';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = '#999';
                  }}
                >
                  Forgot password?
                </button>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="py-2.5 rounded-lg text-white transition-all text-sm"
              style={{
                backgroundColor: loading ? '#ccc' : '#E06E7F',
                fontFamily: 'Montserrat, sans-serif',
                border: 'none',
                cursor: loading ? 'wait' : 'pointer',
              }}
              onMouseEnter={(e) => !loading && (e.currentTarget.style.transform = 'translateY(-2px)')}
              onMouseLeave={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
            >
              {loading ? 'Signing in…' : 'Log In'}
            </button>
          </form>

          <p className="text-center text-xs mt-6" style={{ fontFamily: 'Montserrat, sans-serif', color: '#666' }}>
            Don&apos;t have an account?{' '}
            <span className="cursor-pointer transition-all" style={{ color: '#E06E7F' }}>
              Sign up
            </span>
          </p>
        </div>
      </div>

      <Footer />
    </div>
  );
}
