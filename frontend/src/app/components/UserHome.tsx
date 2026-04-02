import { useState } from "react";
import { Footer } from "./Footer";

export function UserHome({ onLogout, onViewProfile, onViewMessages, onNavigateMap, username }: { onLogout: () => void; onViewProfile: () => void; onViewMessages: () => void; onNavigateMap: () => void; username: string }) {
  const [showLogoutText, setShowLogoutText] = useState(false);
  const [showMapTooltip, setShowMapTooltip] = useState(false);
  const [showMessagesTooltip, setShowMessagesTooltip] = useState(false);
  const [showProfileTooltip, setShowProfileTooltip] = useState(false);

  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
      {/* Navigation Bar */}
      <nav className="w-full px-8 py-4 flex items-center justify-between">
        <h1 className="text-2xl" style={{ 
          fontFamily: 'Montserrat, sans-serif',
          color: '#E06E7F'
        }}>
          nomz
        </h1>
        
        <div className="flex items-center gap-6">
          {/* Map Button */}
          <div className="relative">
            <button
              onClick={onNavigateMap}
              className="text-xl transition-all p-2 rounded-lg"
              onMouseEnter={(e) => {
                setShowMapTooltip(true);
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
              }}
              onMouseLeave={(e) => {
                setShowMapTooltip(false);
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
              style={{ 
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#E06E7F',
                fontWeight: 'normal'
              }}
            >
              🗺️
            </button>
            {showMapTooltip && (
              <div 
                className="absolute top-full mt-1 left-1/2 transform -translate-x-1/2 px-2 py-1 rounded text-xs whitespace-nowrap"
                style={{ 
                  backgroundColor: '#E06E7F',
                  color: 'white',
                  fontFamily: 'Montserrat, sans-serif'
                }}
              >
                map
              </div>
            )}
          </div>

          {/* Messages Button */}
          <div className="relative">
            <button
              onClick={onViewMessages}
              className="text-xl transition-all p-2 rounded-lg"
              onMouseEnter={(e) => {
                setShowMessagesTooltip(true);
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
              }}
              onMouseLeave={(e) => {
                setShowMessagesTooltip(false);
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
              style={{ 
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#E06E7F',
                fontWeight: 'normal'
              }}
            >
              💬
            </button>
            {showMessagesTooltip && (
              <div 
                className="absolute top-full mt-1 left-1/2 transform -translate-x-1/2 px-2 py-1 rounded text-xs whitespace-nowrap"
                style={{ 
                  backgroundColor: '#E06E7F',
                  color: 'white',
                  fontFamily: 'Montserrat, sans-serif'
                }}
              >
                messages
              </div>
            )}
          </div>

          {/* Profile Button */}
          <div className="relative">
            <button
              onClick={onViewProfile}
              className="text-xl transition-all p-2 rounded-lg"
              onMouseEnter={(e) => {
                setShowProfileTooltip(true);
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
              }}
              onMouseLeave={(e) => {
                setShowProfileTooltip(false);
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
              style={{ 
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#E06E7F',
                fontWeight: 'normal'
              }}
            >
              👤
            </button>
            {showProfileTooltip && (
              <div 
                className="absolute top-full mt-1 left-1/2 transform -translate-x-1/2 px-2 py-1 rounded text-xs whitespace-nowrap"
                style={{ 
                  backgroundColor: '#E06E7F',
                  color: 'white',
                  fontFamily: 'Montserrat, sans-serif'
                }}
              >
                profile
              </div>
            )}
          </div>

          {/* Logout Button */}
          <div className="relative">
            <button
              onClick={onLogout}
              className="text-xl transition-all p-2 rounded-lg"
              onMouseEnter={(e) => {
                setShowLogoutText(true);
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
              }}
              onMouseLeave={(e) => {
                setShowLogoutText(false);
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
              style={{ 
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#E06E7F',
                fontWeight: 'normal'
              }}
            >
              →
            </button>
            {showLogoutText && (
              <div 
                className="absolute top-full mt-1 right-0 px-2 py-1 rounded text-xs whitespace-nowrap"
                style={{ 
                  backgroundColor: '#E06E7F',
                  color: 'white',
                  fontFamily: 'Montserrat, sans-serif'
                }}
              >
                logout
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="w-full py-20 px-8">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl mb-4 text-center" style={{ 
            fontFamily: 'Montserrat, sans-serif',
            color: '#E06E7F'
          }}>
            Welcome, {username}! 🍽️
          </h2>
          
          <p className="text-sm text-center mb-16" style={{ 
            fontFamily: 'Montserrat, sans-serif',
            color: '#666'
          }}>
            Discover amazing restaurants and delicious food near you
          </p>

          {/* Search Section */}
          <div className="mb-16 max-w-2xl mx-auto">
            <div className="relative">
              <input
                type="text"
                placeholder="Search for restaurants, cuisines, or dishes..."
                className="w-full px-6 py-4 border-2 rounded-lg focus:outline-none transition-all text-sm"
                style={{ 
                  borderColor: 'rgba(224, 110, 127, 0.2)', 
                  fontFamily: 'Montserrat, sans-serif',
                  backgroundColor: 'white'
                }}
                onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
              />
            </div>
          </div>

          {/* Featured Restaurants */}
          <div className="mb-12">
            <h3 className="text-xl mb-8" style={{ 
              fontFamily: 'Montserrat, sans-serif',
              color: '#E06E7F'
            }}>
              Recommended Restaurants
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map((item) => (
                <div 
                  key={item}
                  className="rounded-lg overflow-hidden transition-all cursor-pointer"
                  style={{ 
                    backgroundColor: 'white',
                    border: '2px solid rgba(224, 110, 127, 0.1)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.1)';
                  }}
                >
                  <div className="h-48 w-full" style={{ backgroundColor: 'rgba(224, 110, 127, 0.1)' }}></div>
                  <div className="p-5">
                    <h4 className="text-base mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#333'
                    }}>
                      Restaurant Name
                    </h4>
                    <p className="text-xs mb-3" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      Cuisine Type • $$ • 4.5 ⭐
                    </p>
                    <p className="text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      123 Main St, City
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Popular Cuisines */}
          <div>
            <h3 className="text-xl mb-8" style={{ 
              fontFamily: 'Montserrat, sans-serif',
              color: '#E06E7F'
            }}>
              Popular Cuisines
            </h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {['Italian 🍝', 'Japanese 🍣', 'Mexican 🌮', 'Indian 🍛'].map((cuisine) => (
                <div 
                  key={cuisine}
                  className="p-6 rounded-lg text-center cursor-pointer transition-all"
                  style={{ 
                    backgroundColor: 'rgba(224, 110, 127, 0.08)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.15)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.08)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <p className="text-sm" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#E06E7F'
                  }}>
                    {cuisine}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}