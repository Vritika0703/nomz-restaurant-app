import { Footer } from "./Footer";
import { useState } from "react";

export function RestaurantProfile({ onLogout, username, onNavigateMessages, onPhotoManagement, onNavigateMap, onNavigateRestaurantMap, onBack, onManageActivation }: { onLogout: () => void; username: string; onNavigateMessages: () => void; onPhotoManagement: () => void; onNavigateMap: () => void; onNavigateRestaurantMap?: () => void; onBack: () => void; onManageActivation?: () => void }) {
  const [showLogoutText, setShowLogoutText] = useState(false);
  const [showMapTooltip, setShowMapTooltip] = useState(false);
  const [showMessagesTooltip, setShowMessagesTooltip] = useState(false);
  const [showProfileTooltip, setShowProfileTooltip] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'details'>('overview');
  const [isEditing, setIsEditing] = useState(false);
  const [showCommunicationSettings, setShowCommunicationSettings] = useState(false);
  const [showAvailabilitySettings, setShowAvailabilitySettings] = useState(false);
  
  // Form state
  const [businessName, setBusinessName] = useState("Greenstick Corp");
  const [email, setEmail] = useState("greenstickcorp@gmail.com");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [cuisineType, setCuisineType] = useState("Other");
  const [priceRange, setPriceRange] = useState("Moderate ($$)");
  const [operatingHours, setOperatingHours] = useState("8:30 AM - 8:30 PM");
  const [messagingHours, setMessagingHours] = useState("Not set (Always available)");
  
  // Communication settings state
  const [messagingEnabled, setMessagingEnabled] = useState(true);
  const [responseHoursStart, setResponseHoursStart] = useState("");
  const [responseHoursEnd, setResponseHoursEnd] = useState("");

  // Availability settings state
  const [isTemporarilyUnavailable, setIsTemporarilyUnavailable] = useState(false);
  const [unavailabilityReason, setUnavailabilityReason] = useState("");
  const [availableAgainDate, setAvailableAgainDate] = useState("");

  const handleSave = () => {
    setIsEditing(false);
    // Here you would typically save to a backend
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Reset form fields to original values if needed
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
        
        <div className="flex items-center gap-6">
          {/* Map Button */}
          <div className="relative">
            <button
              onClick={onNavigateRestaurantMap || onNavigateMap}
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
              onClick={onNavigateMessages}
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
      <main className="w-full py-8 px-8">
        <div className="max-w-7xl mx-auto">
          {/* Account Pending Banner */}
          <div className="mb-8 p-5 rounded-lg flex items-start gap-4" style={{ 
            backgroundColor: 'rgba(224, 110, 127, 0.08)',
            border: '2px solid rgba(224, 110, 127, 0.2)'
          }}>
            <span className="text-2xl">⏳</span>
            <div className="flex-1">
              <h3 className="text-base mb-2" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#E06E7F'
              }}>
                Account Pending Approval
              </h3>
              <p className="text-sm" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                Your restaurant business account is undergoing security review. Most accounts are verified within 24-48 hours.
              </p>
            </div>
          </div>

          {/* Hero Section */}
          <div className="mb-8 p-8 rounded-lg" style={{ 
            backgroundColor: 'white',
            border: '2px solid rgba(224, 110, 127, 0.1)'
          }}>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-3xl mb-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  Greenstick Corp
                </h2>
                <p className="text-sm mb-1" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Other • Moderate ($$) • 8:30 AM - 8:30 PM
                </p>
                <p className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#999'
                }}>
                  greenstickcorp@gmail.com • Member since March 23, 2028
                </p>
              </div>
              <div className="flex gap-3">
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-4 gap-6">
              <div className="p-4 rounded-lg text-center" style={{ 
                backgroundColor: 'rgba(224, 110, 127, 0.05)'
              }}>
                <p className="text-2xl mb-1" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  70.6
                </p>
                <p className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Composite Score
                </p>
              </div>
              <div className="p-4 rounded-lg text-center" style={{ 
                backgroundColor: 'rgba(224, 110, 127, 0.05)'
              }}>
                <p className="text-2xl mb-1" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  --
                </p>
                <p className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Avg Rating
                </p>
              </div>
              <div className="p-4 rounded-lg text-center" style={{ 
                backgroundColor: 'rgba(224, 110, 127, 0.05)'
              }}>
                <p className="text-2xl mb-1" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  #288
                </p>
                <p className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Citywide Rank
                </p>
              </div>
              <div className="p-4 rounded-lg text-center" style={{ 
                backgroundColor: 'rgba(224, 110, 127, 0.05)'
              }}>
                <p className="text-2xl mb-1" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#E06E7F'
                }}>
                  0
                </p>
                <p className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Pending Reservations
                </p>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="mb-6 flex gap-2">
            <button
              onClick={() => setActiveTab('overview')}
              className="py-3 px-6 rounded-lg text-sm transition-all"
              style={{ 
                backgroundColor: activeTab === 'overview' ? '#E06E7F' : 'white',
                color: activeTab === 'overview' ? 'white' : '#666',
                border: activeTab === 'overview' ? 'none' : '2px solid rgba(224, 110, 127, 0.2)',
                fontFamily: 'Montserrat, sans-serif'
              }}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              className="py-3 px-6 rounded-lg text-sm transition-all"
              style={{ 
                backgroundColor: activeTab === 'performance' ? '#E06E7F' : 'white',
                color: activeTab === 'performance' ? 'white' : '#666',
                border: activeTab === 'performance' ? 'none' : '2px solid rgba(224, 110, 127, 0.2)',
                fontFamily: 'Montserrat, sans-serif'
              }}
            >
              Performance Metrics
            </button>
            <button
              onClick={() => setActiveTab('details')}
              className="py-3 px-6 rounded-lg text-sm transition-all"
              style={{ 
                backgroundColor: activeTab === 'details' ? '#E06E7F' : 'white',
                color: activeTab === 'details' ? 'white' : '#666',
                border: activeTab === 'details' ? 'none' : '2px solid rgba(224, 110, 127, 0.2)',
                fontFamily: 'Montserrat, sans-serif'
              }}
            >
              Business Details
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="grid grid-cols-4 gap-4">
                <button
                  onClick={onPhotoManagement}
                  className="p-5 rounded-lg text-center transition-all"
                  style={{ 
                    backgroundColor: 'white',
                    border: '2px solid rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    e.currentTarget.style.borderColor = '#E06E7F';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.2)';
                  }}
                >
                  <span className="text-3xl mb-2 block">📸</span>
                  <p className="text-sm" style={{ color: '#666' }}>Manage Profile</p>
                </button>
                <button
                  onClick={() => setShowAvailabilitySettings(true)}
                  className="p-5 rounded-lg text-center transition-all"
                  style={{ 
                    backgroundColor: 'white',
                    border: '2px solid rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    e.currentTarget.style.borderColor = '#E06E7F';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.2)';
                  }}
                >
                  <span className="text-3xl mb-2 block">{isTemporarilyUnavailable ? '🟡' : '🟢'}</span>
                  <p className="text-sm" style={{ color: '#666' }}>Availability</p>
                </button>
                <button
                  onClick={() => setShowCommunicationSettings(true)}
                  className="p-5 rounded-lg text-center transition-all"
                  style={{ 
                    backgroundColor: 'white',
                    border: '2px solid rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    e.currentTarget.style.borderColor = '#E06E7F';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.2)';
                  }}
                >
                  <span className="text-3xl mb-2 block">⚙️</span>
                  <p className="text-sm" style={{ color: '#666' }}>Settings</p>
                </button>
                <button
                  onClick={onManageActivation}
                  className="p-5 rounded-lg text-center transition-all"
                  style={{ 
                    backgroundColor: 'white',
                    border: '2px solid rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    e.currentTarget.style.borderColor = '#E06E7F';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.2)';
                  }}
                >
                  <span className="text-3xl mb-2 block">⚡</span>
                  <p className="text-sm" style={{ color: '#666' }}>Activation</p>
                </button>
              </div>

              {/* Account Status */}
              <div className="p-6 rounded-lg" style={{ 
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)'
              }}>
                <h3 className="text-lg mb-4" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Account Status
                </h3>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Verification Status
                    </p>
                    <span className="inline-block py-1 px-3 rounded text-xs" style={{ 
                      backgroundColor: '#FFD700',
                      color: '#333',
                      fontFamily: 'Montserrat, sans-serif'
                    }}>
                      Pending approval
                    </span>
                  </div>
                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Profile Completion
                    </p>
                    <p className="text-sm" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#E06E7F'
                    }}>
                      65% Complete
                    </p>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="p-6 rounded-lg" style={{ 
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)'
              }}>
                <h3 className="text-lg mb-4" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Recent Activity
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 rounded" style={{ backgroundColor: 'rgba(224, 110, 127, 0.05)' }}>
                    <span className="text-xl">✨</span>
                    <div className="flex-1">
                      <p className="text-sm mb-1" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        Account created successfully
                      </p>
                      <p className="text-xs" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#999'
                      }}>
                        March 23, 2028
                      </p>
                    </div>
                  </div>
                  <div className="text-center py-8">
                    <p className="text-sm" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      No additional activity yet
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'performance' && (
            <div className="space-y-6">
              {/* Performance Overview */}
              <div className="grid grid-cols-2 gap-6">
                {/* Composite Score */}
                <div className="p-6 rounded-lg" style={{ 
                  backgroundColor: 'white',
                  border: '2px solid rgba(224, 110, 127, 0.1)'
                }}>
                  <h4 className="text-base mb-4" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#333'
                  }}>
                    Composite Score
                  </h4>
                  <p className="text-5xl mb-4" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#E06E7F'
                  }}>
                    70.6<span className="text-2xl text-gray-400">/100</span>
                  </p>
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      <span>Latest grade:</span>
                      <span style={{ color: '#999' }}>N/A</span>
                    </div>
                    <div className="flex justify-between text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      <span>Last inspection:</span>
                      <span style={{ color: '#999' }}>Not available</span>
                    </div>
                    <div className="flex justify-between text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      <span>Reviews used:</span>
                      <span style={{ color: '#999' }}>0 (confidence 0%)</span>
                    </div>
                  </div>
                </div>

                {/* Neighborhood Comparison */}
                <div className="p-6 rounded-lg" style={{ 
                  backgroundColor: 'white',
                  border: '2px solid rgba(224, 110, 127, 0.1)'
                }}>
                  <h4 className="text-base mb-4" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#333'
                  }}>
                    Neighborhood Comparison
                  </h4>
                  <p className="text-xs mb-3" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#666'
                  }}>
                    Scope: <span style={{ color: '#333' }}>citywide</span>
                  </p>
                  <p className="text-4xl mb-4" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#E06E7F'
                  }}>
                    #288 <span className="text-xl text-gray-400">/ 801</span>
                  </p>
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      <span>Percentile:</span>
                      <span style={{ color: '#333' }}>64.2%</span>
                    </div>
                    <div className="flex justify-between text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      <span>Neighborhood average:</span>
                      <span style={{ color: '#333' }}>72.98</span>
                    </div>
                    <div className="flex justify-between text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      <span>Delta vs average:</span>
                      <span style={{ color: '#DC2626' }}>-2.43</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Composite Factor Breakdown */}
              <div className="p-6 rounded-lg" style={{ 
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)'
              }}>
                <h4 className="text-lg mb-6" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Composite Factor Breakdown
                </h4>

                <div className="space-y-6">
                  {/* User Experience Signal */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        User Experience Signal (20%)
                      </p>
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#E06E7F'
                      }}>
                        80.0
                      </p>
                    </div>
                    <div className="w-full h-3 rounded-full mb-2" style={{ backgroundColor: 'rgba(224, 110, 127, 0.1)' }}>
                      <div className="h-full rounded-full" style={{ 
                        width: '80%',
                        backgroundColor: '#E06E7F'
                      }}></div>
                    </div>
                    <p className="text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      0 review(s), confidence 0.0% | Weighted contribution: 12.00
                    </p>
                  </div>

                  {/* Inspection & Hygiene */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        Inspection & Hygiene (20%)
                      </p>
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#E06E7F'
                      }}>
                        48.8
                      </p>
                    </div>
                    <div className="w-full h-3 rounded-full mb-2" style={{ backgroundColor: 'rgba(224, 110, 127, 0.1)' }}>
                      <div className="h-full rounded-full" style={{ 
                        width: '48.8%',
                        backgroundColor: '#E06E7F'
                      }}></div>
                    </div>
                    <p className="text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Grade N/A | Critical 0 | Non-critical 0 | Weighted contribution: 8.75
                    </p>
                  </div>

                  {/* Price-to-Value Fit */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        Price-to-Value Fit (20%)
                      </p>
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#E06E7F'
                      }}>
                        58.0
                      </p>
                    </div>
                    <div className="w-full h-3 rounded-full mb-2" style={{ backgroundColor: 'rgba(224, 110, 127, 0.1)' }}>
                      <div className="h-full rounded-full" style={{ 
                        width: '58%',
                        backgroundColor: '#E06E7F'
                      }}></div>
                    </div>
                    <p className="text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Derived from value ratings against expected value for price tier. | Weighted contribution: 11.60
                    </p>
                  </div>

                  {/* Operational Reliability */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        Operational Reliability (40%)
                      </p>
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#E06E7F'
                      }}>
                        93.0
                      </p>
                    </div>
                    <div className="w-full h-3 rounded-full mb-2" style={{ backgroundColor: 'rgba(224, 110, 127, 0.1)' }}>
                      <div className="h-full rounded-full" style={{ 
                        width: '93%',
                        backgroundColor: '#E06E7F'
                      }}></div>
                    </div>
                    <p className="text-xs" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Based on profile status, temporary availability, and metadata quality. | Weighted contribution: 37.20
                    </p>
                  </div>
                </div>
              </div>

              {/* Review & Historical Sections */}
              <div className="grid grid-cols-2 gap-6">
                <div className="p-6 rounded-lg" style={{ 
                  backgroundColor: 'white',
                  border: '2px solid rgba(224, 110, 127, 0.1)'
                }}>
                  <h4 className="text-base mb-4" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#333'
                  }}>
                    Review Parameter Breakdown
                  </h4>
                  <div className="text-center py-8">
                    <span className="text-4xl mb-3 block">📊</span>
                    <p className="text-sm" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      No published reviews yet
                    </p>
                  </div>
                </div>

                <div className="p-6 rounded-lg" style={{ 
                  backgroundColor: 'white',
                  border: '2px solid rgba(224, 110, 127, 0.1)'
                }}>
                  <h4 className="text-base mb-4" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#333'
                  }}>
                    Historical Trend
                  </h4>
                  <div className="text-center py-8">
                    <span className="text-4xl mb-3 block">📈</span>
                    <p className="text-sm" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      No historical data available
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Business Information */}
              <div className="p-6 rounded-lg" style={{ 
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)'
              }}>
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#333'
                  }}>
                    Business Information
                  </h3>
                  {!isEditing && (
                    <button
                      className="py-2 px-6 rounded-lg text-sm transition-all"
                      style={{ 
                        backgroundColor: '#E06E7F',
                        color: 'white',
                        fontFamily: 'Montserrat, sans-serif',
                        border: 'none'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#C85B6D'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#E06E7F'}
                      onClick={() => setIsEditing(true)}
                    >
                      Edit Information
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-x-12 gap-y-6">
                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Business Name
                    </p>
                    {isEditing ? (
                      <input
                        type="text"
                        value={businessName}
                        onChange={(e) => setBusinessName(e.target.value)}
                        className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)', 
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'transparent',
                          color: '#333'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                    ) : (
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {businessName}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Username
                    </p>
                    <p className="text-sm py-2.5" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      greenstickcorp
                    </p>
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Email
                    </p>
                    {isEditing ? (
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)', 
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'transparent',
                          color: '#333'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                    ) : (
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {email}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Phone
                    </p>
                    {isEditing ? (
                      <input
                        type="text"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="Enter phone number"
                        className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)', 
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'transparent',
                          color: '#333'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                    ) : (
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: phone ? '#333' : '#999'
                      }}>
                        {phone || "Not provided"}
                      </p>
                    )}
                  </div>

                  <div className="col-span-2">
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Address
                    </p>
                    {isEditing ? (
                      <input
                        type="text"
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        placeholder="Enter business address"
                        className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)', 
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'transparent',
                          color: '#333'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                    ) : (
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: address ? '#333' : '#999'
                      }}>
                        {address || "Not provided"}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Member Since
                    </p>
                    <p className="text-sm py-2.5" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      March 23, 2028
                    </p>
                  </div>
                </div>
              </div>

              {/* Restaurant Details */}
              <div className="p-6 rounded-lg" style={{ 
                backgroundColor: 'white',
                border: '2px solid rgba(224, 110, 127, 0.1)'
              }}>
                <h3 className="text-lg mb-6" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Restaurant Details
                </h3>
                <div className="grid grid-cols-2 gap-x-12 gap-y-6">
                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Cuisine Type
                    </p>
                    {isEditing ? (
                      <input
                        type="text"
                        value={cuisineType}
                        onChange={(e) => setCuisineType(e.target.value)}
                        className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)', 
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'transparent',
                          color: '#333'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                    ) : (
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {cuisineType}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Price Range
                    </p>
                    {isEditing ? (
                      <select
                        value={priceRange}
                        onChange={(e) => setPriceRange(e.target.value)}
                        className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)', 
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'transparent',
                          color: '#333'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      >
                        <option value="Budget ($)">Budget ($)</option>
                        <option value="Moderate ($$)">Moderate ($$)</option>
                        <option value="Upscale ($$$)">Upscale ($$$)</option>
                        <option value="Fine Dining ($$$$)">Fine Dining ($$$$)</option>
                      </select>
                    ) : (
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {priceRange}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Operating Hours
                    </p>
                    {isEditing ? (
                      <input
                        type="text"
                        value={operatingHours}
                        onChange={(e) => setOperatingHours(e.target.value)}
                        placeholder="e.g. 8:00 AM - 10:00 PM"
                        className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)', 
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'transparent',
                          color: '#333'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                    ) : (
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {operatingHours}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Messaging Hours
                    </p>
                    {isEditing ? (
                      <input
                        type="text"
                        value={messagingHours}
                        onChange={(e) => setMessagingHours(e.target.value)}
                        placeholder="e.g. 9:00 AM - 6:00 PM"
                        className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                        style={{ 
                          borderColor: 'rgba(224, 110, 127, 0.2)', 
                          fontFamily: 'Montserrat, sans-serif',
                          backgroundColor: 'transparent',
                          color: '#333'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                        onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                      />
                    ) : (
                      <p className="text-sm" style={{ 
                        fontFamily: 'Montserrat, sans-serif',
                        color: '#333'
                      }}>
                        {messagingHours}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Account Status
                    </p>
                    <span className="inline-block py-1 px-3 rounded text-xs" style={{ 
                      backgroundColor: '#FFD700',
                      color: '#333',
                      fontFamily: 'Montserrat, sans-serif'
                    }}>
                      Pending approval
                    </span>
                  </div>

                  <div>
                    <p className="text-xs mb-2" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Account Type
                    </p>
                    <p className="text-sm py-2.5" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      Restaurant
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {isEditing && (
                <div className="flex justify-end gap-3">
                  <button
                    className="py-3 px-8 rounded-lg text-sm transition-all"
                    style={{ 
                      backgroundColor: 'white',
                      color: '#E06E7F',
                      border: '2px solid rgba(224, 110, 127, 0.3)',
                      fontFamily: 'Montserrat, sans-serif'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                      e.currentTarget.style.borderColor = '#E06E7F';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'white';
                      e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.3)';
                    }}
                    onClick={handleCancel}
                  >
                    Cancel
                  </button>
                  <button
                    className="py-3 px-8 rounded-lg text-sm transition-all"
                    style={{ 
                      backgroundColor: '#E06E7F',
                      color: 'white',
                      fontFamily: 'Montserrat, sans-serif',
                      border: 'none'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#C85B6D'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#E06E7F'}
                    onClick={handleSave}
                  >
                    Save Changes
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <Footer />

      {/* Communication Settings Modal */}
      {showCommunicationSettings && (
        <div 
          className="fixed inset-0 flex items-center justify-center p-8"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', zIndex: 1000 }}
          onClick={() => setShowCommunicationSettings(false)}
        >
          <div 
            className="w-full max-w-4xl rounded-lg overflow-hidden"
            style={{ backgroundColor: 'white' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="p-6" style={{ backgroundColor: '#E06E7F' }}>
              <h2 className="text-xl flex items-center gap-2" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: 'white'
              }}>
                <span>📧</span> Communication Settings
              </h2>
            </div>

            {/* Content */}
            <div className="p-8">
              <p className="text-sm mb-6" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                Control when and how diners can reach you through the Nomz messaging system.
              </p>

              {/* Status Banner */}
              <div className="mb-8 p-4 rounded-lg" style={{ 
                backgroundColor: messagingEnabled ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                border: `2px solid ${messagingEnabled ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
              }}>
                <p className="text-sm flex items-center gap-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  <span>{messagingEnabled ? '✅' : '❌'}</span>
                  Messaging is currently <strong>{messagingEnabled ? 'Enabled' : 'Disabled'}</strong> 
                  {messagingEnabled ? ' — diners can send you messages.' : ' — diners cannot send you messages.'}
                </p>
              </div>

              {/* Messaging Toggle */}
              <div className="mb-8 p-6 rounded-lg" style={{ 
                backgroundColor: 'rgba(224, 110, 127, 0.05)',
                border: '2px solid rgba(224, 110, 127, 0.1)'
              }}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-base" style={{ 
                    fontFamily: 'Montserrat, sans-serif',
                    color: '#333'
                  }}>
                    Messaging Toggle
                  </h3>
                  <button
                    onClick={() => setMessagingEnabled(!messagingEnabled)}
                    className="relative inline-block w-14 h-8 rounded-full transition-all"
                    style={{ 
                      backgroundColor: messagingEnabled ? '#E06E7F' : '#D1D5DB'
                    }}
                  >
                    <span
                      className="absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-all"
                      style={{ 
                        transform: messagingEnabled ? 'translateX(24px)' : 'translateX(0)'
                      }}
                    />
                  </button>
                </div>
                <p className="text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  When disabled, diners will not be able to send you new messages.
                </p>
              </div>

              {/* Response Hours */}
              <div className="mb-8">
                <h3 className="text-base mb-2" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Response Hours <span style={{ color: '#999' }}>(optional)</span>
                </h3>
                <p className="text-xs mb-4" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Let diners know what time window you typically respond. This is informational only.
                </p>

                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="text-xs mb-2 block" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      Response Hours Start
                    </label>
                    <input
                      type="text"
                      value={responseHoursStart}
                      onChange={(e) => setResponseHoursStart(e.target.value)}
                      placeholder="e.g. 11:00 AM or 11pm"
                      className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                      style={{ 
                        borderColor: 'rgba(224, 110, 127, 0.2)', 
                        fontFamily: 'Montserrat, sans-serif',
                        backgroundColor: 'transparent',
                        color: '#333'
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                      onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                    />
                    <p className="text-xs mt-1" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Earliest time you typically respond to messages (optional).
                    </p>
                  </div>

                  <div>
                    <label className="text-xs mb-2 block" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#666'
                    }}>
                      Response Hours End
                    </label>
                    <input
                      type="text"
                      value={responseHoursEnd}
                      onChange={(e) => setResponseHoursEnd(e.target.value)}
                      placeholder="e.g. 4:00 PM or 4pm"
                      className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                      style={{ 
                        borderColor: 'rgba(224, 110, 127, 0.2)', 
                        fontFamily: 'Montserrat, sans-serif',
                        backgroundColor: 'transparent',
                        color: '#333'
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                      onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                    />
                    <p className="text-xs mt-1" style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#999'
                    }}>
                      Latest time you typically respond to messages (optional).
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-start gap-3">
                <button
                  className="py-3 px-8 rounded-lg text-sm transition-all"
                  style={{ 
                    backgroundColor: '#E06E7F',
                    color: 'white',
                    fontFamily: 'Montserrat, sans-serif',
                    border: 'none'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#C85B6D'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#E06E7F'}
                  onClick={() => setShowCommunicationSettings(false)}
                >
                  Save Settings
                </button>
                <button
                  className="py-3 px-8 rounded-lg text-sm transition-all"
                  style={{ 
                    backgroundColor: 'white',
                    color: '#666',
                    border: '2px solid rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    e.currentTarget.style.borderColor = '#E06E7F';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.2)';
                  }}
                  onClick={() => setShowCommunicationSettings(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Availability Settings Modal */}
      {showAvailabilitySettings && (
        <div 
          className="fixed inset-0 flex items-center justify-center p-8"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', zIndex: 1000 }}
          onClick={() => setShowAvailabilitySettings(false)}
        >
          <div 
            className="w-full max-w-4xl rounded-lg overflow-hidden max-h-[90vh] flex flex-col"
            style={{ backgroundColor: 'white' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="p-6" style={{ backgroundColor: '#E06E7F' }}>
              <h2 className="text-xl" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: 'white'
              }}>
                Manage Restaurant Availability
              </h2>
            </div>

            {/* Content */}
            <div className="p-8 overflow-y-auto">
              <p className="text-sm mb-6" style={{ 
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                Use this page to temporarily mark your restaurant as unavailable for a period of time. This allows you to inform customers of closures, renovations, or special events.
              </p>

              {/* Unavailable Toggle */}
              <div className="mb-6 p-6 rounded-lg" style={{ 
                backgroundColor: 'rgba(224, 110, 127, 0.05)',
                border: '2px solid rgba(224, 110, 127, 0.1)'
              }}>
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="unavailable-checkbox"
                    checked={isTemporarilyUnavailable}
                    onChange={(e) => setIsTemporarilyUnavailable(e.target.checked)}
                    className="w-5 h-5 rounded"
                    style={{ 
                      accentColor: '#E06E7F',
                      cursor: 'pointer'
                    }}
                  />
                  <label 
                    htmlFor="unavailable-checkbox"
                    className="text-base cursor-pointer"
                    style={{ 
                      fontFamily: 'Montserrat, sans-serif',
                      color: '#333'
                    }}
                  >
                    Mark as Temporarily Unavailable
                  </label>
                </div>
                <p className="text-xs mt-2 ml-8" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Check this box if your restaurant is temporarily closed or unavailable.
                </p>
              </div>

              {/* Reason for Unavailability */}
              <div className="mb-6">
                <label className="text-sm mb-2 block" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Reason for Unavailability
                </label>
                <textarea
                  value={unavailabilityReason}
                  onChange={(e) => setUnavailabilityReason(e.target.value)}
                  placeholder="e.g., Renovations, Special Event, Staffing Issues..."
                  rows={4}
                  className="w-full px-4 py-3 border-2 rounded-lg focus:outline-none transition-all text-sm resize-none"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)', 
                    fontFamily: 'Montserrat, sans-serif',
                    backgroundColor: 'transparent',
                    color: '#333'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                />
                <p className="text-xs mt-1" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  This message will be displayed to customers.
                </p>
              </div>

              {/* Available Again On */}
              <div className="mb-8">
                <label className="text-sm mb-2 block" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Available Again On
                </label>
                <input
                  type="datetime-local"
                  value={availableAgainDate}
                  onChange={(e) => setAvailableAgainDate(e.target.value)}
                  className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none transition-all text-sm"
                  style={{ 
                    borderColor: 'rgba(224, 110, 127, 0.2)', 
                    fontFamily: 'Montserrat, sans-serif',
                    backgroundColor: 'transparent',
                    color: '#333'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#E06E7F'}
                  onBlur={(e) => e.target.style.borderColor = 'rgba(224, 110, 127, 0.2)'}
                />
                <p className="text-xs mt-1" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  Select when your restaurant will be available again.
                </p>
              </div>

              {/* Common Reasons */}
              <div className="mb-8 p-6 rounded-lg" style={{ 
                backgroundColor: 'rgba(224, 110, 127, 0.03)',
                border: '1px solid rgba(224, 110, 127, 0.1)'
              }}>
                <h3 className="text-sm mb-3" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#333'
                }}>
                  Common Reasons for Unavailability:
                </h3>
                <ul className="space-y-1.5 text-xs" style={{ 
                  fontFamily: 'Montserrat, sans-serif',
                  color: '#666'
                }}>
                  <li>• Renovations and maintenance</li>
                  <li>• Equipment repairs or replacement</li>
                  <li>• Staff training or reorganization</li>
                  <li>• Special event or private catering</li>
                  <li>• Temporary staffing shortage</li>
                  <li>• Inventory replenishment</li>
                  <li>• Holiday or seasonal closure</li>
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-start gap-3">
                <button
                  className="py-3 px-8 rounded-lg text-sm transition-all"
                  style={{ 
                    backgroundColor: '#E06E7F',
                    color: 'white',
                    fontFamily: 'Montserrat, sans-serif',
                    border: 'none'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#C85B6D'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#E06E7F'}
                  onClick={() => setShowAvailabilitySettings(false)}
                >
                  Save Changes
                </button>
                <button
                  className="py-3 px-8 rounded-lg text-sm transition-all"
                  style={{ 
                    backgroundColor: 'white',
                    color: '#666',
                    border: '2px solid rgba(224, 110, 127, 0.2)',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.05)';
                    e.currentTarget.style.borderColor = '#E06E7F';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.2)';
                  }}
                  onClick={() => setShowAvailabilitySettings(false)}
                >
                  Back to Profile
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}