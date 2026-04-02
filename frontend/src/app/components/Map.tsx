import { useState } from "react";
import { Footer } from "./Footer";

export function Map({ 
  onNavigateHome, 
  onNavigateMessages, 
  onNavigateProfile, 
  onLogout,
  isAdmin = false
}: { 
  onNavigateHome: () => void;
  onNavigateMessages: () => void;
  onNavigateProfile: () => void;
  onLogout: () => void;
  isAdmin?: boolean;
}) {
  const [search, setSearch] = useState('');
  const [borough, setBorough] = useState('all');
  const [cuisine, setCuisine] = useState('all');
  const [minScore, setMinScore] = useState('');
  const [maxScore, setMaxScore] = useState('');
  const [sortBy, setSortBy] = useState('composite-high-low');
  const [onlyVisibleArea, setOnlyVisibleArea] = useState(false);

  const mockRestaurants = [
    { name: "SOHO TOSCANO", address: "508 WEST 26 STREET, Manhattan, 10001", cuisine: "Manhattan · ITALIAN", score: "91 / 100" },
    { name: "STARBUCKS COFFEE #82647", address: "304 WEST 37 STREET, Manhattan, 10001", cuisine: "Manhattan · COFFEE/TEA", score: "91 / 100" },
    { name: "HUDSON MARKET AT SHERATON NEW YORK TIMES SQUARE", address: "811 7 AVENUE, Manhattan, 10019", cuisine: "Manhattan · COFFEE/TEA, AMERICAN", score: "91 / 100" },
    { name: "POPUP BAGELS INC", address: "171 171 THOMPSON STREET, Manhattan, 10012", cuisine: "Manhattan · BAGELS/PRETZELS", score: "90 / 100" },
    { name: "B AND D RESTAURANT", address: "908 WEST 36 STREET, Manhattan, 10001", cuisine: "Manhattan · KOREAN, AFRICAN", score: "90 / 100" },
    { name: "AMY'S CHINESE RESTAURANT", address: "47-48 BELL BOULEVARD, Queens, 11361", cuisine: "Queens · KOREAN, CHINESE", score: "89 / 100" },
  ];

  return (
    <div className="size-full flex flex-col" style={{ backgroundColor: '#FFF9F5' }}>
      {/* Navigation Bar */}
      <nav className="w-full px-8 py-4 flex items-center justify-between">
        {isAdmin ? (
          <>
            <div className="flex items-center gap-6">
              <button
                onClick={onNavigateProfile}
                className="text-xl transition-all p-2 rounded-lg"
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
                }}
                onMouseLeave={(e) => {
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
                ←
              </button>
              
              <h1 className="text-2xl" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                nomz Admin
              </h1>
            </div>
            
            <button
              onClick={onLogout}
              className="text-xl transition-all p-2 rounded-lg"
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
              }}
              onMouseLeave={(e) => {
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
          </>
        ) : (
          <>
            <div className="flex items-center gap-6">
              <button
                onClick={onNavigateHome}
                className="text-xl transition-all p-2 rounded-lg"
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
                }}
                onMouseLeave={(e) => {
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
                ←
              </button>
              
              <h1 className="text-2xl" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                nomz
              </h1>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={onNavigateMessages}
                className="text-xl transition-all p-2 rounded-lg"
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
                }}
                onMouseLeave={(e) => {
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
              
              <button
                onClick={onNavigateProfile}
                className="text-xl transition-all p-2 rounded-lg"
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
                }}
                onMouseLeave={(e) => {
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
              
              <button
                onClick={onLogout}
                className="text-xl transition-all p-2 rounded-lg"
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
                }}
                onMouseLeave={(e) => {
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
            </div>
          </>
        )}
      </nav>

      {/* Main Content */}
      <main className="w-full flex-1 px-8 pb-8 overflow-hidden">
        <div className="size-full flex flex-col gap-4">
          {/* Filters Section */}
          <div className="w-full p-6 rounded-lg" style={{ 
            backgroundColor: 'white',
            border: '2px solid rgba(224, 110, 127, 0.1)'
          }}>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              {/* Search */}
              <div>
                <label className="block text-xs mb-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Search
                </label>
                <input
                  type="text"
                  placeholder="Name, street, or ZIP"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full px-3 py-2 border rounded text-xs focus:outline-none transition-all"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                />
              </div>

              {/* Borough */}
              <div>
                <label className="block text-xs mb-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Borough
                </label>
                <select
                  value={borough}
                  onChange={(e) => setBorough(e.target.value)}
                  className="w-full px-3 py-2 border rounded text-xs focus:outline-none transition-all"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                >
                  <option value="all">All Boroughs</option>
                  <option value="manhattan">Manhattan</option>
                  <option value="brooklyn">Brooklyn</option>
                  <option value="queens">Queens</option>
                  <option value="bronx">The Bronx</option>
                  <option value="staten">Staten Island</option>
                </select>
              </div>

              {/* Cuisine */}
              <div>
                <label className="block text-xs mb-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Cuisine
                </label>
                <select
                  value={cuisine}
                  onChange={(e) => setCuisine(e.target.value)}
                  className="w-full px-3 py-2 border rounded text-xs focus:outline-none transition-all"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                >
                  <option value="all">All cuisines</option>
                  <option value="italian">Italian</option>
                  <option value="chinese">Chinese</option>
                  <option value="mexican">Mexican</option>
                  <option value="japanese">Japanese</option>
                  <option value="american">American</option>
                </select>
              </div>

              {/* Min Score */}
              <div>
                <label className="block text-xs mb-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Min Score
                </label>
                <input
                  type="number"
                  placeholder="0"
                  value={minScore}
                  onChange={(e) => setMinScore(e.target.value)}
                  className="w-full px-3 py-2 border rounded text-xs focus:outline-none transition-all"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
              {/* Max Score */}
              <div>
                <label className="block text-xs mb-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Max Score
                </label>
                <input
                  type="number"
                  placeholder="100"
                  value={maxScore}
                  onChange={(e) => setMaxScore(e.target.value)}
                  className="w-full px-3 py-2 border rounded text-xs focus:outline-none transition-all"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                />
              </div>

              {/* Sort By */}
              <div>
                <label className="block text-xs mb-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Sort by
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 border rounded text-xs focus:outline-none transition-all"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                >
                  <option value="composite-high-low">Composite: High → Low</option>
                  <option value="composite-low-high">Composite: Low → High</option>
                  <option value="name-a-z">Name: A → Z</option>
                  <option value="name-z-a">Name: Z → A</option>
                </select>
              </div>

              {/* Map Scope Checkbox */}
              <div>
                <label className="flex items-center gap-2 text-xs cursor-pointer" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  <input
                    type="checkbox"
                    checked={onlyVisibleArea}
                    onChange={(e) => setOnlyVisibleArea(e.target.checked)}
                    className="cursor-pointer"
                    style={{ accentColor: '#E06E7F' }}
                  />
                  Only visible map area
                </label>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex gap-4 mt-4">
              <button
                className="flex-1 px-4 py-2 rounded text-xs transition-all"
                style={{ 
                  backgroundColor: 'rgba(224, 110, 127, 0.7)',
                  color: 'white',
                  border: 'none',
                  fontFamily: 'Montserrat, sans-serif',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.9)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.7)';
                }}
              >
                Reset
              </button>
              <button
                className="flex-1 px-4 py-2 rounded text-xs transition-all"
                style={{ 
                  backgroundColor: '#5a6c7d',
                  color: 'white',
                  border: 'none',
                  fontFamily: 'Montserrat, sans-serif',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#4a5c6d';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#5a6c7d';
                }}
              >
                Apply Filters
              </button>
            </div>
          </div>

          {/* Map and Restaurant List */}
          <div className="flex-1 flex gap-4 overflow-hidden">
            {/* Map Area */}
            <div className="flex-1 rounded-lg overflow-hidden" style={{ 
              backgroundColor: 'rgba(224, 110, 127, 0.05)',
              border: '2px solid rgba(224, 110, 127, 0.1)',
              minHeight: '400px'
            }}>
              <div className="size-full flex items-center justify-center" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                <p className="text-sm">Map View (Integration Required)</p>
              </div>
            </div>

            {/* Restaurant List */}
            <div className="w-96 rounded-lg overflow-hidden flex flex-col" style={{ 
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              {/* Header */}
              <div className="px-4 py-3 flex items-center justify-between" style={{ 
                borderBottom: '2px solid rgba(224, 110, 127, 0.1)'
              }}>
                <h3 className="text-sm" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Nearby restaurants
                </h3>
                <span className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#999'
                }}>
                  {mockRestaurants.length} results
                </span>
              </div>

              {/* Restaurant List */}
              <div className="flex-1 overflow-y-auto">
                <p className="px-4 py-2 text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#999'
                }}>
                  Click a row or marker to view details.
                </p>

                {/* Legend */}
                <div className="px-4 py-2 flex gap-3 text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif'
                }}>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#90EE90' }}></span>
                    <span style={{ color: '#666' }}>90+</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#FFD700' }}></span>
                    <span style={{ color: '#666' }}>80-79</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#FFA07A' }}></span>
                    <span style={{ color: '#666' }}>&lt;80</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: '#D3D3D3' }}></span>
                    <span style={{ color: '#666' }}>no score</span>
                  </span>
                </div>

                {mockRestaurants.map((restaurant, index) => (
                  <div
                    key={index}
                    className="px-4 py-3 cursor-pointer transition-all"
                    style={{ 
                      borderBottom: '1px solid rgba(224, 110, 127, 0.1)'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <h4 className="text-xs" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {restaurant.name}
                      </h4>
                      <span className="text-xs ml-2" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#E06E7F',
                        whiteSpace: 'nowrap'
                      }}>
                        {restaurant.score}
                      </span>
                    </div>
                    <p className="text-xs mb-1" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      {restaurant.address}
                    </p>
                    <p className="text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      {restaurant.cuisine}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}