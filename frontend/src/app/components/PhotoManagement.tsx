import { useState } from "react";

interface Photo {
  id: string;
  url: string;
  isMain: boolean;
}

export function PhotoManagement({ onBack }: { onBack: () => void }) {
  const [photos, setPhotos] = useState<Photo[]>([
    { id: '1', url: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500', isMain: true },
    { id: '2', url: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=500', isMain: false },
    { id: '3', url: 'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=500', isMain: false },
    { id: '4', url: 'https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=500', isMain: false },
  ]);

  const handleSetMainPhoto = (photoId: string) => {
    setPhotos(photos.map(photo => ({
      ...photo,
      isMain: photo.id === photoId
    })));
  };

  const handleDeletePhoto = (photoId: string) => {
    setPhotos(photos.filter(photo => photo.id !== photoId));
  };

  const handleUploadPhoto = () => {
    // In a real app, this would open a file picker
    const newPhoto: Photo = {
      id: Date.now().toString(),
      url: 'https://images.unsplash.com/photo-1552566626-52f8b828add9?w=500',
      isMain: false
    };
    setPhotos([...photos, newPhoto]);
  };

  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: '#FFF9F5' }}>
      {/* Navigation Bar */}
      <nav className="w-full px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="text-xl transition-all p-2 rounded-lg"
            style={{ 
              backgroundColor: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: '#E06E7F'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(224, 110, 127, 0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
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
      </nav>

      {/* Main Content */}
      <div className="flex-1 px-8 py-6">
        {/* Header Section */}
        <div className="mb-8">
          <h2 className="text-3xl mb-2" style={{ 
            fontFamily: 'Montserrat, sans-serif',
            color: '#333'
          }}>
            Manage Photos
          </h2>
          <p className="text-sm" style={{ 
            fontFamily: 'Montserrat, sans-serif',
            color: '#666'
          }}>
            Upload, delete, and manage your restaurant photos. Set a main profile photo to showcase your business.
          </p>
        </div>

        {/* Upload Button */}
        <div className="mb-8">
          <button
            onClick={handleUploadPhoto}
            className="py-3 px-8 rounded-lg text-sm transition-all"
            style={{ 
              backgroundColor: '#E06E7F',
              color: 'white',
              fontFamily: 'Montserrat, sans-serif',
              border: 'none'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#C85B6D'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#E06E7F'}
          >
            📸 Upload New Photo
          </button>
        </div>

        {/* Photos Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {photos.map((photo) => (
            <div
              key={photo.id}
              className="rounded-lg overflow-hidden relative group"
              style={{ 
                backgroundColor: 'white',
                border: photo.isMain ? '3px solid #E06E7F' : '2px solid rgba(224, 110, 127, 0.2)'
              }}
            >
              {/* Photo */}
              <div className="aspect-[4/3] overflow-hidden">
                <img
                  src={photo.url}
                  alt="Restaurant"
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Main Badge */}
              {photo.isMain && (
                <div
                  className="absolute top-3 left-3 px-3 py-1 rounded text-xs"
                  style={{ 
                    backgroundColor: '#E06E7F',
                    color: 'white',
                    fontFamily: 'Montserrat, sans-serif'
                  }}
                >
                  ⭐ Main Photo
                </div>
              )}

              {/* Action Buttons */}
              <div className="p-4 flex gap-2">
                {!photo.isMain && (
                  <button
                    onClick={() => handleSetMainPhoto(photo.id)}
                    className="flex-1 py-2 px-4 rounded-lg text-xs transition-all"
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
                  >
                    Set as Main
                  </button>
                )}
                <button
                  onClick={() => handleDeletePhoto(photo.id)}
                  className="py-2 px-4 rounded-lg text-xs transition-all"
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
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {photos.length === 0 && (
          <div className="text-center py-16">
            <p className="text-xl mb-2" style={{ 
              fontFamily: 'Montserrat, sans-serif',
              color: '#666'
            }}>
              No photos yet
            </p>
            <p className="text-sm" style={{ 
              fontFamily: 'Montserrat, sans-serif',
              color: '#999'
            }}>
              Upload your first photo to get started
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
