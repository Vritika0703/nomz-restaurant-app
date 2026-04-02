import { useState } from 'react';
import { Footer } from './Footer';

export function SignUp({ onBackClick, onSignUp }: { onBackClick: () => void; onSignUp: (accountType: 'diner' | 'restaurant', username: string) => void }) {
  const [accountType, setAccountType] = useState<'diner' | 'restaurant' | ''>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const usernameInput = document.getElementById('username') as HTMLInputElement;
    const username = usernameInput?.value || 'User';
    if (accountType && accountType !== '') {
      onSignUp(accountType, username);
    }
  };

  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
      {/* Back Arrow */}
      <button
        onClick={onBackClick}
        className="absolute top-8 left-8 p-2 rounded-lg transition-all hover:bg-opacity-10"
        style={{
          color: '#E06E7F',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
        aria-label="Go back"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="24" 
          height="24" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>

      {/* Centered Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-8 py-20">
        {/* nomz branding */}
        <h1 className="text-3xl mb-10" style={{ 
          fontFamily: 'Montserrat, sans-serif',
          color: '#E06E7F'
        }}>
          nomz
        </h1>
        
        {/* Sign up form */}
        <div className="w-full max-w-3xl">
          <h2 className="text-xl mb-6 text-center" style={{ 
            fontFamily: 'Montserrat, sans-serif', 
            color: '#333' 
          }}>
            Create Your Account
          </h2>
          
          <form className="flex flex-col gap-5">
            {/* Two column layout for user details */}
            <div className="grid grid-cols-2 gap-5">
              <div className="flex flex-col gap-2">
                <label htmlFor="name" className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif', 
                  color: '#666' 
                }}>
                  Full Name
                </label>
                <input
                  type="text"
                  id="name"
                  className="px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)', 
                    fontFamily: 'Montserrat, sans-serif',
                    backgroundColor: 'transparent'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                  placeholder="Enter your full name"
                />
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="username" className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif', 
                  color: '#666' 
                }}>
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  className="px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)', 
                    fontFamily: 'Montserrat, sans-serif',
                    backgroundColor: 'transparent'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                  placeholder="Choose a username"
                />
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="accountType" className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif', 
                  color: '#666' 
                }}>
                  Account Type
                </label>
                <select
                  id="accountType"
                  value={accountType}
                  onChange={(e) => setAccountType(e.target.value as 'diner' | 'restaurant')}
                  className="px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)', 
                    fontFamily: 'Montserrat, sans-serif',
                    backgroundColor: 'transparent',
                    color: '#333'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                >
                  <option value="" disabled>Select account type</option>
                  <option value="diner">Diner</option>
                  <option value="restaurant">Restaurant</option>
                </select>
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="email" className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif', 
                  color: '#666' 
                }}>
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  className="px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)', 
                    fontFamily: 'Montserrat, sans-serif',
                    backgroundColor: 'transparent'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                  placeholder="Enter your email"
                />
              </div>
            
              <div className="flex flex-col gap-2">
                <label htmlFor="password" className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif', 
                  color: '#666' 
                }}>
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  className="px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)', 
                    fontFamily: 'Montserrat, sans-serif',
                    backgroundColor: 'transparent'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                  placeholder="Create a password"
                />
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="confirmPassword" className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif', 
                  color: '#666' 
                }}>
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  className="px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)', 
                    fontFamily: 'Montserrat, sans-serif',
                    backgroundColor: 'transparent'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                  placeholder="Confirm your password"
                />
              </div>
            </div>
            
            <button
              type="submit"
              onClick={handleSubmit}
              className="py-2.5 rounded-lg text-white transition-all text-sm"
              style={{ 
                backgroundColor: '#E06E7F', 
                fontFamily: 'Montserrat, sans-serif'
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              Sign Up
            </button>
          </form>
          
          <p className="text-center text-xs mt-6" style={{ 
            fontFamily: 'Montserrat, sans-serif', 
            color: '#666' 
          }}>
            Already have an account? <span className="cursor-pointer transition-all" style={{ 
              color: '#E06E7F' 
            }}>Log in</span>
          </p>
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
}