import { Footer } from "./Footer";
import { useState } from "react";

export function UserProfile({ onBack, onViewMessages, onNavigateMap, onNavigateHome, username }: { onBack: () => void; onViewMessages: () => void; onNavigateMap: () => void; onNavigateHome: () => void; username: string }) {
  const [showLogoutText, setShowLogoutText] = useState(false);
  
  // Edit states
  const [editingDetails, setEditingDetails] = useState(false);
  const [editingTaste, setEditingTaste] = useState(false);
  const [editingDietaryRestrictions, setEditingDietaryRestrictions] = useState(false);
  const [editingPreferences, setEditingPreferences] = useState(false);
  
  // User details
  const [fullName, setFullName] = useState(username);
  const [email, setEmail] = useState(`${username.toLowerCase()}@email.com`);
  
  // Taste profile
  const [cuisines, setCuisines] = useState(['Asian', 'Mexican', 'Indian', 'French', 'Japanese', 'Thai', 'Vegan']);
  const [availableCuisines] = useState(['American', 'Asian', 'Italian', 'Mexican', 'Indian', 'French', 'Japanese', 'Chinese', 'Thai', 'Mediterranean', 'Fusion', 'Vegetarian', 'Vegan', 'Other']);
  
  // Dietary restrictions
  const [dietaryRestrictions, setDietaryRestrictions] = useState(['Vegan']);
  const [availableDietaryRestrictions] = useState(['Vegan', 'Vegetarian', 'Non-vegetarian', 'Gluten-Free', 'Halal', 'Kosher']);
  
  // Preferences
  const [priceRange, setPriceRange] = useState('$$');
  const [location, setLocation] = useState('Manhattan');
  const [boroughs] = useState(['Manhattan', 'Brooklyn', 'Queens', 'The Bronx', 'Staten Island']);
  
  const toggleCuisine = (cuisine: string) => {
    if (cuisines.includes(cuisine)) {
      setCuisines(cuisines.filter(c => c !== cuisine));
    } else {
      setCuisines([...cuisines, cuisine]);
    }
  };

  const toggleDietaryRestriction = (restriction: string) => {
    if (dietaryRestrictions.includes(restriction)) {
      setDietaryRestrictions(dietaryRestrictions.filter(r => r !== restriction));
    } else {
      setDietaryRestrictions([...dietaryRestrictions, restriction]);
    }
  };
  
  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
      {/* Navigation Bar */}
      <nav className="w-full px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <button
            onClick={onBack}
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
            onClick={onNavigateMap}
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
            🗺️
          </button>
          
          <button
            onClick={onViewMessages}
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
            →
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="w-full py-12 px-8 flex-1">
        <div className="max-w-7xl mx-auto">
          {/* Profile Header - Compact */}
          <div className="mb-12 p-8 rounded-lg" style={{ 
            backgroundColor: 'white',
            border: '2px solid rgba(224, 110, 127, 0.1)'
          }}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 rounded-full flex items-center justify-center text-3xl" style={{ 
                  backgroundColor: 'rgba(224, 110, 127, 0.15)' 
                }}>
                  👤
                </div>
                {!editingDetails ? (
                  <div>
                    <h2 className="text-2xl mb-1" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#E06E7F'
                    }}>
                      {fullName}
                    </h2>
                    <p className="text-sm" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      {email}
                    </p>
                  </div>
                ) : (
                  <div className="flex gap-4">
                    <div>
                      <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="Full Name"
                        className="px-4 py-2 border-2 rounded-lg focus:outline-none transition-all text-sm mb-2"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)',
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'white',
                          width: '250px'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Email"
                        className="px-4 py-2 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)',
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'white',
                          width: '250px'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                    </div>
                  </div>
                )}
              </div>
              
              <button
                className="px-5 py-2 rounded-lg transition-all text-sm"
                style={{ 
                  backgroundColor: editingDetails ? '#E06E7F' : 'transparent',
                  color: editingDetails ? 'white' : '#E06E7F',
                  border: '2px solid #E06E7F',
                  fontFamily: 'Montserrat, sans-serif'
                }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                onClick={() => setEditingDetails(!editingDetails)}
              >
                {editingDetails ? 'Save' : 'Edit Profile'}
              </button>
            </div>
          </div>

          {/* Dashboard Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Favorite Cuisines Card */}
            <div className="p-6 rounded-lg" style={{ 
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Favorite Cuisines
                </h3>
                <span style={{ fontSize: '24px' }}>🍽️</span>
              </div>
              
              {!editingTaste ? (
                <div>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-2 mb-4 min-h-[120px]">
                    {cuisines.map((cuisine) => (
                      <span 
                        key={cuisine}
                        className="text-sm"
                        style={{ 
                          color: '#333',
                          fontFamily: 'Montserrat, sans-serif'
                        }}
                      >
                        {cuisine}
                      </span>
                    ))}
                  </div>
                  <button
                    className="text-xs transition-all w-full py-2 rounded-lg"
                    style={{ 
                      color: '#E06E7F',
                      fontFamily: 'Montserrat, sans-serif',
                      border: '1px solid rgba(224, 110, 127, 0.3)',
                      backgroundColor: 'transparent',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                    onClick={() => setEditingTaste(true)}
                  >
                    Edit
                  </button>
                </div>
              ) : (
                <div>
                  <div className="space-y-2 mb-4 max-h-[180px] overflow-y-auto">
                    {availableCuisines.map((cuisine) => (
                      <label 
                        key={cuisine}
                        className="flex items-center gap-2 cursor-pointer"
                        style={{ 
                          fontFamily: 'Montserrat, sans-serif',
                          color: '#333'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={cuisines.includes(cuisine)}
                          onChange={() => toggleCuisine(cuisine)}
                          className="w-4 h-4 cursor-pointer"
                          style={{ 
                            accentColor: '#E06E7F'
                          }}
                        />
                        <span className="text-xs">{cuisine}</span>
                      </label>
                    ))}
                  </div>
                  <button
                    className="text-xs w-full py-2 rounded-lg transition-all"
                    style={{ 
                      backgroundColor: '#E06E7F',
                      color: 'white',
                      fontFamily: 'Montserrat, sans-serif',
                      border: 'none',
                      cursor: 'pointer'
                    }}
                    onClick={() => setEditingTaste(false)}
                  >
                    Save
                  </button>
                </div>
              )}
            </div>

            {/* Dietary Restrictions Card */}
            <div className="p-6 rounded-lg" style={{ 
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Dietary Restrictions
                </h3>
                <span style={{ fontSize: '24px' }}>🥗</span>
              </div>
              
              {!editingDietaryRestrictions ? (
                <div>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-2 mb-4 min-h-[120px]">
                    {dietaryRestrictions.length > 0 ? (
                      dietaryRestrictions.map((restriction) => (
                        <span 
                          key={restriction}
                          className="text-sm"
                          style={{ 
                            color: '#333',
                            fontFamily: 'Montserrat, sans-serif'
                          }}
                        >
                          {restriction}
                        </span>
                      ))
                    ) : (
                      <p className="text-xs col-span-2" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#999'
                      }}>
                        No dietary restrictions
                      </p>
                    )}
                  </div>
                  <button
                    className="text-xs transition-all w-full py-2 rounded-lg"
                    style={{ 
                      color: '#E06E7F',
                      fontFamily: 'Montserrat, sans-serif',
                      border: '1px solid rgba(224, 110, 127, 0.3)',
                      backgroundColor: 'transparent',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                    onClick={() => setEditingDietaryRestrictions(true)}
                  >
                    Edit
                  </button>
                </div>
              ) : (
                <div>
                  <div className="space-y-2 mb-4 max-h-[180px] overflow-y-auto">
                    {availableDietaryRestrictions.map((restriction) => (
                      <label 
                        key={restriction}
                        className="flex items-center gap-2 cursor-pointer"
                        style={{ 
                          fontFamily: 'Montserrat, sans-serif',
                          color: '#333'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={dietaryRestrictions.includes(restriction)}
                          onChange={() => toggleDietaryRestriction(restriction)}
                          className="w-4 h-4 cursor-pointer"
                          style={{ 
                            accentColor: '#E06E7F'
                          }}
                        />
                        <span className="text-xs">{restriction}</span>
                      </label>
                    ))}
                  </div>
                  <button
                    className="text-xs w-full py-2 rounded-lg transition-all"
                    style={{ 
                      backgroundColor: '#E06E7F',
                      color: 'white',
                      fontFamily: 'Montserrat, sans-serif',
                      border: 'none',
                      cursor: 'pointer'
                    }}
                    onClick={() => setEditingDietaryRestrictions(false)}
                  >
                    Save
                  </button>
                </div>
              )}
            </div>

            {/* Price Range Card */}
            <div className="p-6 rounded-lg" style={{ 
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Price Range
                </h3>
                <span style={{ fontSize: '24px' }}>💰</span>
              </div>
              
              <div className="flex flex-col gap-3">
                <div className="grid grid-cols-4 gap-2">
                  {['$', '$$', '$$$', '$$$$'].map((price) => (
                    <div 
                      key={price}
                      className="py-3 rounded-lg cursor-pointer transition-all text-center text-sm"
                      style={{ 
                        backgroundColor: price === priceRange ? '#E06E7F' : 'rgba(224, 110, 127, 0.1)',
                        color: price === priceRange ? 'white' : '#E06E7F',
                        fontFamily: 'Montserrat, sans-serif'
                      }}
                      onClick={() => setPriceRange(price)}
                      onMouseEnter={(e) => {
                        if (price !== priceRange) {
                          e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.2)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (price !== priceRange) {
                          e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)';
                        }
                      }}
                    >
                      {price}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Preferred Location Card */}
            <div className="p-6 rounded-lg" style={{ 
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Preferred Location
                </h3>
                <span style={{ fontSize: '24px' }}>📍</span>
              </div>
              
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full px-4 py-3 border-2 rounded-lg focus:outline-none transition-all text-sm cursor-pointer"
                style={{ 
                  borderColor: 'rgba(224, 110, 127, 0.2)',
                  fontFamily: 'Montserrat, sans-serif',
                  backgroundColor: 'white',
                  color: '#333'
                }}
                onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
              >
                {boroughs.map((borough) => (
                  <option key={borough} value={borough}>
                    {borough}
                  </option>
                ))}
              </select>
            </div>

            {/* Saved Favorites Card */}
            <div className="p-6 rounded-lg" style={{ 
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Saved Favorites
                </h3>
                <span style={{ fontSize: '24px' }}>❤️</span>
              </div>
              <p className="text-5xl" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#333'
              }}>
                0
              </p>
            </div>

            {/* Reviews Written Card */}
            <div className="p-6 rounded-lg" style={{ 
              backgroundColor: 'white',
              border: '2px solid rgba(224, 110, 127, 0.1)'
            }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Reviews Written
                </h3>
                <span style={{ fontSize: '24px' }}>⭐</span>
              </div>
              <p className="text-5xl" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#333'
              }}>
                0
              </p>
            </div>

          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}