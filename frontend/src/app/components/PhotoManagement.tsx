import { useCallback, useEffect, useRef, useState } from "react";
import { apiFetch } from "../api";

interface Photo {
  id: number;
  url: string;
  caption: string;
  is_primary: boolean;
}

const MAX_UPLOAD_MB = 10;
const MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

function firstErrorMessage(errors: unknown): string | null {
  if (!errors || typeof errors !== "object") return null;
  for (const value of Object.values(errors as Record<string, unknown>)) {
    if (Array.isArray(value) && value.length > 0) {
      const msg = value[0];
      if (typeof msg === "string" && msg.trim()) return msg;
    }
    if (typeof value === "string" && value.trim()) return value;
  }
  return null;
}

export function PhotoManagement({ onBack }: { onBack: () => void }) {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const loadPhotos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await apiFetch("/api/restaurant/photos/data/");
      if (!r.ok) {
        setError(`Could not load photos (${r.status}).`);
        setPhotos([]);
        return;
      }
      const data = await r.json();
      setPhotos((data.photos ?? []) as Photo[]);
    } catch {
      setError("Network error loading photos.");
      setPhotos([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadPhotos();
  }, [loadPhotos]);

  const handleSetMainPhoto = async (photoId: number) => {
    setError(null);
    try {
      const r = await apiFetch(`/api/restaurant/photos/${photoId}/set-primary/`, { method: "POST" });
      if (!r.ok) {
        setError("Could not update main photo.");
        return;
      }
      await loadPhotos();
    } catch {
      setError("Network error.");
    }
  };

  const handleDeletePhoto = async (photoId: number) => {
    setError(null);
    try {
      const r = await apiFetch(`/api/restaurant/photos/${photoId}/delete/`, { method: "POST" });
      if (!r.ok) {
        setError("Could not delete photo.");
        return;
      }
      await loadPhotos();
    } catch {
      setError("Network error.");
    }
  };

  const handleUploadClick = () => fileRef.current?.click();

  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setError(null);
    if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
      setError("Please upload a JPG, PNG, or WEBP image.");
      return;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      setError(`Image is too large. Maximum size is ${MAX_UPLOAD_MB}MB.`);
      return;
    }
    const fd = new FormData();
    fd.append("photo", file);
    fd.append("caption", "");
    fd.append("is_primary", photos.length === 0 ? "on" : "");
    try {
      const r = await apiFetch("/api/restaurant/photos/upload/", {
        method: "POST",
        body: fd,
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        const backendMessage = firstErrorMessage(d?.errors);
        setError(backendMessage ?? `Upload failed (${r.status}).`);
        return;
      }
      await loadPhotos();
    } catch {
      setError("Network error during upload.");
    }
  };

  return (
    <div className="size-full flex flex-col overflow-y-auto" style={{ backgroundColor: "#FFF9F5" }}>
      <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={(e) => void onFileChange(e)} />

      <nav className="w-full px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="text-xl transition-all p-2 rounded-lg"
            title="Back"
            style={{
              backgroundColor: "transparent",
              border: "none",
              cursor: "pointer",
              color: "#E06E7F",
            }}
            type="button"
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "rgba(224, 110, 127, 0.1)")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
          >
            ←
          </button>
          <h1 className="text-2xl" style={{ fontFamily: "Montserrat, sans-serif", color: "#E06E7F" }}>
            nomz
          </h1>
        </div>
      </nav>

      <div className="flex-1 px-8 py-6">
        <div className="mb-8">
          <h2 className="text-3xl mb-2" style={{ fontFamily: "Montserrat, sans-serif", color: "#333" }}>
            Manage Photos
          </h2>
          <p className="text-sm" style={{ fontFamily: "Montserrat, sans-serif", color: "#666" }}>
            Upload, delete, and manage photos for your restaurant.
          </p>
          {error && (
            <p className="text-sm mt-2" style={{ color: "#b91c1c" }}>
              {error}
            </p>
          )}
          {loading && <p className="text-xs mt-2" style={{ color: "#999" }}>Loading…</p>}
        </div>

        <div className="mb-8">
          <button
            onClick={handleUploadClick}
            title="Upload a new restaurant photo"
            className="py-3 px-8 rounded-lg text-sm transition-all"
            style={{
              backgroundColor: "#E06E7F",
              color: "white",
              fontFamily: "Montserrat, sans-serif",
              border: "none",
              cursor: "pointer",
            }}
            type="button"
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#C85B6D")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#E06E7F")}
          >
            📸 Upload New Photo
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {photos.map((photo) => (
            <div
              key={photo.id}
              className="rounded-lg overflow-hidden relative group"
              style={{
                backgroundColor: "white",
                border: photo.is_primary ? "3px solid #E06E7F" : "2px solid rgba(224, 110, 127, 0.2)",
              }}
            >
              <div className="aspect-[4/3] overflow-hidden bg-neutral-100">
                {photo.url ? (
                  <img src={photo.url} alt="" className="w-full h-full object-cover" />
                ) : null}
              </div>

              {photo.is_primary && (
                <div
                  className="absolute top-3 left-3 px-3 py-1 rounded text-xs"
                  style={{
                    backgroundColor: "#E06E7F",
                    color: "white",
                    fontFamily: "Montserrat, sans-serif",
                  }}
                >
                  ⭐ Main Photo
                </div>
              )}

              <div className="p-4 flex gap-2">
                {!photo.is_primary && (
                  <button
                    onClick={() => void handleSetMainPhoto(photo.id)}
                    title="Set this photo as main restaurant image"
                    className="flex-1 py-2 px-4 rounded-lg text-xs transition-all"
                    style={{
                      backgroundColor: "white",
                      color: "#E06E7F",
                      border: "2px solid rgba(224, 110, 127, 0.3)",
                      fontFamily: "Montserrat, sans-serif",
                      cursor: "pointer",
                    }}
                    type="button"
                  >
                    Set as Main
                  </button>
                )}
                <button
                  onClick={() => void handleDeletePhoto(photo.id)}
                  title="Delete this photo"
                  className="py-2 px-4 rounded-lg text-xs transition-all"
                  style={{
                    backgroundColor: "white",
                    color: "#E06E7F",
                    border: "2px solid rgba(224, 110, 127, 0.3)",
                    fontFamily: "Montserrat, sans-serif",
                    cursor: "pointer",
                  }}
                  type="button"
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        {!loading && photos.length === 0 && (
          <div className="text-center py-16">
            <p className="text-xl mb-2" style={{ fontFamily: "Montserrat, sans-serif", color: "#666" }}>
              No photos yet
            </p>
            <p className="text-sm" style={{ fontFamily: "Montserrat, sans-serif", color: "#999" }}>
              Upload your first photo to get started
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
