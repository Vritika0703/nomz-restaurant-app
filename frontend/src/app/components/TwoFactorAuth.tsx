import { useState } from 'react';

export function TwoFactorAuth({ onBack, onVerify, onResend }: { onBack: () => void; onVerify: (code: string) => void; onResend?: () => void }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [resendCount, setResendCount] = useState(0);
  const [showResendOption, setShowResendOption] = useState(false);

  const handleVerify = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!code) {
      setError('Please enter your authentication code');
      return;
    }

    if (code.length < 6) {
      setError('Code must be at least 6 characters');
      return;
    }

    setIsVerifying(true);
    // Simulate API call - in real app, this would verify the code with backend
    setTimeout(() => {
      // For demo, accept any 6+ digit code
      if (/^\d{6,}$/.test(code)) {
        onVerify(code);
      } else {
        setError('Invalid code format. Please try again.');
      }
      setIsVerifying(false);
    }, 500);
  };

  const handleResend = () => {
    onResend?.();
    setResendCount(resendCount + 1);
    setError('');
    setCode('');
    // Show resend option again after 60 seconds
    setTimeout(() => {
      setShowResendOption(true);
    }, 60000);
  };

  return (
    <div className="size-full flex flex-col items-center justify-center" style={{ backgroundColor: '#FFF9F5' }}>
      <div className="w-full max-w-md px-8">
        {/* Card */}
        <div className="rounded-lg p-8" style={{
          backgroundColor: 'white',
          border: '2px solid rgba(224, 110, 127, 0.1)'
        }}>
          {/* Icon */}
          <div className="text-center mb-6">
            <span className="text-5xl">🔐</span>
          </div>

          {/* Header */}
          <div className="mb-6 text-center">
            <h2 className="text-3xl mb-3" style={{
              fontFamily: 'Montserrat, sans-serif',
              color: '#E06E7F',
              fontWeight: '600'
            }}>
              Two-Factor Authentication
            </h2>
            <p style={{
              fontFamily: 'Montserrat, sans-serif',
              color: '#999',
              fontSize: '14px'
            }}>
              Enter the code from your authentication app or SMS.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleVerify}>
            <div className="mb-4">
              <label style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#333',
                fontSize: '14px',
                fontWeight: '500'
              }}>
                Authentication Code
              </label>
              <input
                type="text"
                inputMode="numeric"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 12))}
                placeholder="000000"
                maxLength={12}
                className="w-full mt-2 px-4 py-4 rounded-lg focus:outline-none transition-all text-center text-2xl tracking-widest"
                style={{
                  backgroundColor: '#FFF9F5',
                  border: '2px solid rgba(224, 110, 127, 0.1)',
                  fontFamily: 'Montserrat, sans-serif',
                  letterSpacing: '8px'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.3)';
                  e.currentTarget.style.backgroundColor = 'white';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.1)';
                  e.currentTarget.style.backgroundColor = '#FFF9F5';
                }}
              />
            </div>

            {error && (
              <div className="mb-4 p-3 rounded-lg" style={{
                backgroundColor: 'rgba(212, 24, 61, 0.1)',
                border: '1px solid rgba(212, 24, 61, 0.2)'
              }}>
                <p style={{
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#D4183D',
                  fontSize: '13px',
                  margin: '0'
                }}>
                  {error}
                </p>
              </div>
            )}

            {/* Verify Button */}
            <button
              type="submit"
              disabled={isVerifying}
              className="w-full py-3 rounded-lg font-medium transition-all text-white mb-3"
              style={{
                backgroundColor: isVerifying ? '#ccc' : '#E06E7F',
                cursor: isVerifying ? 'not-allowed' : 'pointer',
                fontFamily: 'Montserrat, sans-serif',
                fontSize: '14px',
                border: 'none'
              }}
              onMouseEnter={(e) => {
                if (!isVerifying) {
                  e.currentTarget.style.backgroundColor = '#d1596d';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isVerifying) {
                  e.currentTarget.style.backgroundColor = '#E06E7F';
                  e.currentTarget.style.transform = 'translateY(0)';
                }
              }}
            >
              {isVerifying ? 'Verifying...' : 'Verify'}
            </button>

            {/* Back Button */}
            <button
              type="button"
              onClick={onBack}
              className="w-full py-3 rounded-lg font-medium transition-all"
              style={{
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.2)',
                color: '#E06E7F',
                cursor: 'pointer',
                fontFamily: 'Montserrat, sans-serif',
                fontSize: '14px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
              }}
            >
              Back
            </button>
          </form>

          {/* Resend Option */}
          {onResend && (
            <div className="mt-4 text-center">
              <p style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#999',
                fontSize: '13px',
                marginBottom: '10px'
              }}>
                Didn't receive your code?
              </p>
              <button
                type="button"
                onClick={handleResend}
                disabled={!showResendOption && resendCount > 0}
                className="text-sm transition-all"
                style={{
                  color: showResendOption || resendCount === 0 ? '#E06E7F' : '#999',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: showResendOption || resendCount === 0 ? 'pointer' : 'not-allowed',
                  fontFamily: 'Montserrat, sans-serif',
                  textDecoration: 'underline'
                }}
                onMouseEnter={(e) => {
                  if (showResendOption || resendCount === 0) {
                    e.currentTarget.style.color = '#d1596d';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = showResendOption || resendCount === 0 ? '#E06E7F' : '#999';
                }}
              >
                {resendCount > 0 ? 'Resend code' : 'Send code again'}
              </button>
            </div>
          )}
        </div>

        {/* Help Text */}
        <p style={{
          fontFamily: 'Montserrat, sans-serif',
          color: '#999',
          fontSize: '12px',
          textAlign: 'center',
          marginTop: '16px'
        }}>
          Use an authentication app or the code sent to your device
        </p>
      </div>
    </div>
  );
}
