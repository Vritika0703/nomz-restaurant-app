import { Footer } from "./Footer";

export function Messages({ 
  onNavigateMap,
  onNavigateHome, 
  onNavigateProfile, 
  onLogout,
  accountType = 'Diner'
}: { 
  onNavigateMap: () => void;
  onNavigateHome: () => void;
  onNavigateProfile: () => void;
  onLogout: () => void;
  accountType?: 'Diner' | 'Restaurant';
}) {
  return (
    <div className="size-full flex flex-col" style={{ backgroundColor: '#FFF9F5' }}>
      {/* Navigation Bar */}
      <nav className="w-full px-8 py-4 flex items-center justify-between">
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
          
          {/* Only show profile button for Diners */}
          {accountType === 'Diner' && (
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
          )}
          
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
      </nav>

      {/* Main Content */}
      <main className="w-full py-12 px-8 flex-1">
        <div className="max-w-5xl mx-auto">
          {/* Messages Container */}
          <div className="rounded-lg overflow-hidden" style={{
            border: '2px solid rgba(224, 110, 127, 0.1)'
          }}>
            {/* Header */}
            <div className="px-6 py-4" style={{
              backgroundColor: '#E06E7F',
              color: 'white'
            }}>
              <h2 className="text-lg" style={{
                fontFamily: 'Montserrat, sans-serif'
              }}>
                Messages
              </h2>
            </div>
            
            {/* Content */}
            <div className="px-6 py-8" style={{
              backgroundColor: 'white'
            }}>
              <p className="text-sm" style={{
                fontFamily: 'Montserrat, sans-serif',
                color: '#666'
              }}>
                {accountType === 'Restaurant' 
                  ? 'No messages yet. Customers will be able to contact you here.'
                  : 'No conversations yet. Open a restaurant profile and click "Message Restaurant" to start.'
                }
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}