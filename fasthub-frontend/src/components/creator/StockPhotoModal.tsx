/**
 * StockPhotoModal — search Unsplash/Pexels, pick photo, save to section slot.
 * Brief 34: stock photo search + download + crop.
 */

import { useState } from "react";
import * as api from "@/api/creator";
import type { StockPhoto } from "@/types/creator";

interface StockPhotoModalProps {
  open: boolean;
  onClose: () => void;
  projectId: string;
  sectionId: string;
  slotId: string;
  aspectRatio?: string;
  onPhotoSaved: (fileUrl: string) => void;
}

export default function StockPhotoModal({
  open,
  onClose,
  projectId,
  sectionId,
  slotId,
  aspectRatio = "auto",
  onPhotoSaved,
}: StockPhotoModalProps) {
  const [query, setQuery] = useState("");
  const [photos, setPhotos] = useState<StockPhoto[]>([]);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const { data } = await api.searchStockPhotos(query.trim());
      setPhotos(data);
    } catch {
      setPhotos([]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  };

  const handleSelect = async (photo: StockPhoto) => {
    setDownloading(photo.url);
    try {
      const { data } = await api.downloadStockPhoto(projectId, {
        url: photo.download_url || photo.url,
        slot_id: slotId,
        section_id: sectionId,
        aspect_ratio: aspectRatio,
      });
      onPhotoSaved(data.file_url);
      onClose();
    } catch {
      // ignore
    }
    setDownloading(null);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <div
        className="bg-white rounded-2xl shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Zmien zdjecie</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Search */}
        <div className="px-6 py-3 border-b border-gray-100">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Szukaj zdjec..."
              className="flex-1 px-4 py-2 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400"
              autoFocus
            />
            <button
              onClick={handleSearch}
              disabled={!query.trim() || loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
            >
              Szukaj
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-8 text-gray-400 text-sm">
              <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Szukam...
            </div>
          ) : photos.length === 0 ? (
            <div className="text-center py-8 text-gray-400 text-sm">
              {query ? "Brak wynikow. Sprobuj inne slowa kluczowe." : "Wpisz slowa kluczowe i kliknij Szukaj."}
            </div>
          ) : (
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              {photos.map((photo, i) => (
                <button
                  key={i}
                  onClick={() => handleSelect(photo)}
                  disabled={downloading === photo.url}
                  className="relative group rounded-lg overflow-hidden aspect-[4/3] bg-gray-100 hover:ring-2 ring-indigo-400 transition-all"
                >
                  <img
                    src={photo.thumb}
                    alt={photo.author}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                  {downloading === photo.url && (
                    <div className="absolute inset-0 bg-white/70 flex items-center justify-center">
                      <svg className="animate-spin h-5 w-5 text-indigo-600" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                    </div>
                  )}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <p className="text-[10px] text-white truncate">{photo.author} / {photo.source}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
