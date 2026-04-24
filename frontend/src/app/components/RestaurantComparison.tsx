import { useEffect, useState } from 'react';
import { apiFetch } from '../api';
import { Footer } from './Footer';
import { useAppContext } from '../AppContext';

interface RestaurantData {
  id: number;
  name: string;
  cuisine: string;
  cuisine_tags: string[];
  neighborhood: string;
  address: string;
  description: string;
  phone: string;
  price_range: string;
  hours_open: string;
  hours_close: string;
  is_flagged: boolean;
  is_owner_flagged: boolean;
  owner_id: number | null;
  messaging_enabled: boolean;
  composite_score: number | null;
  grade: string;
  reviews: any[];
}

export function RestaurantComparison({
  onBack,
  onSelectRestaurant,
}: {
  onBack: () => void;
  onSelectRestaurant: (id: number) => void;
}) {
  const { selectedRestaurants, clearSelectedRestaurants } = useAppContext();
  const [restaurants, setRestaurants] = useState<RestaurantData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const promises = selectedRestaurants.map(id =>
          apiFetch(`/api/restaurants/${id}/`).then(r => r.json())
        );
        const results = await Promise.all(promises);
        if (!cancelled) {
          setRestaurants(results);
        }
      } catch {
        if (!cancelled) {
          setError('Failed to load restaurant data.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => { cancelled = true; };
  }, [selectedRestaurants]);

  if (loading) {
    return (
      <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
        <div className="flex-1 flex items-center justify-center">
          <p style={{ color: '#666', fontFamily: 'Montserrat, sans-serif' }}>Loading comparison...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
        <div className="flex-1 flex items-center justify-center">
          <p style={{ color: '#b91c1c', fontFamily: 'Montserrat, sans-serif' }}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
      <nav className="w-full px-8 py-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={onBack}
            className="text-xl p-2 rounded-lg transition-all"
            title="Back"
            style={{ border: 'none', background: 'transparent', color: '#E06E7F', cursor: 'pointer' }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(224,110,127,0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            ←
          </button>
          <h1 className="text-2xl" style={{ fontFamily: 'Montserrat, sans-serif', color: '#E06E7F' }}>
            Compare Restaurants
          </h1>
        </div>
        <button
          type="button"
          onClick={() => {
            clearSelectedRestaurants();
            onBack();
          }}
          className="px-4 py-2 rounded-lg text-sm"
          style={{ backgroundColor: '#E06E7F', color: 'white', fontFamily: 'Montserrat, sans-serif', border: 'none', cursor: 'pointer' }}
        >
          Clear Selection
        </button>
      </nav>

      <main className="flex-1 px-8 py-8 overflow-x-auto">
        <div className="min-w-max">
          {/* Header Row */}
          <div className="grid gap-4 mb-6" style={{ gridTemplateColumns: `200px repeat(${restaurants.length}, 1fr)` }}>
            <div className="font-semibold" style={{ color: '#333', fontFamily: 'Montserrat, sans-serif' }}>
              Attribute
            </div>
            {restaurants.map(restaurant => (
              <div key={restaurant.id} className="text-center">
                <button
                  type="button"
                  onClick={() => onSelectRestaurant(restaurant.id)}
                  className="block w-full p-3 rounded-lg transition-all text-left"
                  style={{
                    backgroundColor: 'white',
                    border: '2px solid rgba(224, 110, 127, 0.15)',
                    fontFamily: 'Montserrat, sans-serif',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)'; e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.3)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'white'; e.currentTarget.style.borderColor = 'rgba(224, 110, 127, 0.15)'; }}
                >
                  <h3 className="font-semibold text-sm mb-1" style={{ color: '#333' }}>
                    {restaurant.name}
                  </h3>
                  <p className="text-xs" style={{ color: '#666' }}>
                    {restaurant.cuisine}
                  </p>
                </button>
              </div>
            ))}
          </div>

          {/* Comparison Rows */}
          <div className="space-y-2">
            {/* Cuisine */}
            <div className="grid gap-4 py-3" style={{ gridTemplateColumns: `200px repeat(${restaurants.length}, 1fr)` }}>
              <div className="font-medium text-sm" style={{ color: '#666', fontFamily: 'Montserrat, sans-serif' }}>
                Cuisine
              </div>
              {restaurants.map(restaurant => (
                <div key={restaurant.id} className="text-center text-sm" style={{ color: '#333', fontFamily: 'Montserrat, sans-serif' }}>
                  {restaurant.cuisine || 'N/A'}
                </div>
              ))}
            </div>

            {/* Price Range */}
            <div className="grid gap-4 py-3 bg-white rounded-lg" style={{ gridTemplateColumns: `200px repeat(${restaurants.length}, 1fr)` }}>
              <div className="font-medium text-sm pl-3" style={{ color: '#666', fontFamily: 'Montserrat, sans-serif' }}>
                Price Range
              </div>
              {restaurants.map(restaurant => (
                <div key={restaurant.id} className="text-center text-sm" style={{ color: '#333', fontFamily: 'Montserrat, sans-serif' }}>
                  {restaurant.price_range || 'N/A'}
                </div>
              ))}
            </div>

            {/* Hours */}
            <div className="grid gap-4 py-3" style={{ gridTemplateColumns: `200px repeat(${restaurants.length}, 1fr)` }}>
              <div className="font-medium text-sm" style={{ color: '#666', fontFamily: 'Montserrat, sans-serif' }}>
                Hours
              </div>
              {restaurants.map(restaurant => (
                <div key={restaurant.id} className="text-center text-sm" style={{ color: '#333', fontFamily: 'Montserrat, sans-serif' }}>
                  {restaurant.hours_open && restaurant.hours_close
                    ? `${restaurant.hours_open} - ${restaurant.hours_close}`
                    : 'N/A'
                  }
                </div>
              ))}
            </div>

            {/* Rating/Score */}
            <div className="grid gap-4 py-3 bg-white rounded-lg" style={{ gridTemplateColumns: `200px repeat(${restaurants.length}, 1fr)` }}>
              <div className="font-medium text-sm pl-3" style={{ color: '#666', fontFamily: 'Montserrat, sans-serif' }}>
                Composite Score
              </div>
              {restaurants.map(restaurant => (
                <div key={restaurant.id} className="text-center text-sm font-semibold" style={{ color: '#E06E7F', fontFamily: 'Montserrat, sans-serif' }}>
                  {restaurant.composite_score != null ? restaurant.composite_score.toFixed(1) : 'N/A'}
                </div>
              ))}
            </div>

            {/* Grade */}
            <div className="grid gap-4 py-3" style={{ gridTemplateColumns: `200px repeat(${restaurants.length}, 1fr)` }}>
              <div className="font-medium text-sm" style={{ color: '#666', fontFamily: 'Montserrat, sans-serif' }}>
                Health Grade
              </div>
              {restaurants.map(restaurant => (
                <div key={restaurant.id} className="text-center text-sm" style={{ color: '#333', fontFamily: 'Montserrat, sans-serif' }}>
                  {restaurant.grade || 'N/A'}
                </div>
              ))}
            </div>

            {/* Neighborhood */}
            <div className="grid gap-4 py-3 bg-white rounded-lg" style={{ gridTemplateColumns: `200px repeat(${restaurants.length}, 1fr)` }}>
              <div className="font-medium text-sm pl-3" style={{ color: '#666', fontFamily: 'Montserrat, sans-serif' }}>
                Neighborhood
              </div>
              {restaurants.map(restaurant => (
                <div key={restaurant.id} className="text-center text-sm" style={{ color: '#333', fontFamily: 'Montserrat, sans-serif' }}>
                  {restaurant.neighborhood || 'N/A'}
                </div>
              ))}
            </div>

            {/* Address */}
            <div className="grid gap-4 py-3" style={{ gridTemplateColumns: `200px repeat(${restaurants.length}, 1fr)` }}>
              <div className="font-medium text-sm" style={{ color: '#666', fontFamily: 'Montserrat, sans-serif' }}>
                Address
              </div>
              {restaurants.map(restaurant => (
                <div key={restaurant.id} className="text-center text-sm" style={{ color: '#333', fontFamily: 'Montserrat, sans-serif' }}>
                  {restaurant.address || 'N/A'}
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}