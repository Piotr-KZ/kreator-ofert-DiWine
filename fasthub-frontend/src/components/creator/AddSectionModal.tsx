/**
 * AddSectionModal — block configurator: pick category + media → matching blocks.
 * Brief 34: type + media + layout → POST /blocks/match → pick block → add section.
 */

import { useEffect, useState } from "react";
import * as api from "@/api/creator";
import type { BlockCategory, BlockTemplate } from "@/types/creator";

interface AddSectionModalProps {
  open: boolean;
  onClose: () => void;
  onSelect: (blockCode: string) => void;
}

const MEDIA_OPTIONS = [
  { id: "", label: "Dowolne" },
  { id: "photo", label: "Zdjecie" },
  { id: "video", label: "Video" },
  { id: "icon", label: "Ikony" },
  { id: "opinion", label: "Opinie" },
  { id: "none", label: "Bez mediow" },
];

export default function AddSectionModal({ open, onClose, onSelect }: AddSectionModalProps) {
  const [categories, setCategories] = useState<BlockCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedMedia, setSelectedMedia] = useState("");
  const [blocks, setBlocks] = useState<BlockTemplate[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    api.listCategories().then(({ data }) => setCategories(data)).catch(() => {});
  }, [open]);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    const criteria: Record<string, string> = {};
    if (selectedCategory) criteria.category_code = selectedCategory;
    if (selectedMedia) criteria.media_type = selectedMedia;

    api.matchBlocks(criteria)
      .then(({ data }) => setBlocks(data))
      .catch(() => setBlocks([]))
      .finally(() => setLoading(false));
  }, [open, selectedCategory, selectedMedia]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <div
        className="bg-white rounded-2xl shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Dodaj sekcje</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-100 space-y-3">
          {/* Category */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1.5 block">Rodzaj</label>
            <div className="flex flex-wrap gap-1.5">
              <button
                onClick={() => setSelectedCategory("")}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  !selectedCategory ? "bg-indigo-100 text-indigo-700" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                Wszystkie
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.code}
                  onClick={() => setSelectedCategory(cat.code)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    selectedCategory === cat.code ? "bg-indigo-100 text-indigo-700" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>

          {/* Media */}
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1.5 block">Media</label>
            <div className="flex flex-wrap gap-1.5">
              {MEDIA_OPTIONS.map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => setSelectedMedia(opt.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    selectedMedia === opt.id ? "bg-indigo-100 text-indigo-700" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
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
              Szukam klockow...
            </div>
          ) : blocks.length === 0 ? (
            <div className="text-center py-8 text-gray-400 text-sm">
              Brak pasujacych klockow. Zmien filtry.
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {blocks.map((block) => (
                <button
                  key={block.code}
                  onClick={() => onSelect(block.code)}
                  className="border-2 border-gray-200 rounded-xl p-3 text-left hover:border-indigo-400 hover:bg-indigo-50/50 transition-all group"
                >
                  <div className="text-xs font-mono text-gray-400 mb-1">{block.code}</div>
                  <div className="text-sm font-medium text-gray-800 group-hover:text-indigo-700">{block.name}</div>
                  <div className="text-xs text-gray-500 mt-1 line-clamp-2">{block.description}</div>
                  <div className="flex gap-1 mt-2">
                    <span className="text-[10px] px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">{block.media_type}</span>
                    <span className="text-[10px] px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">{block.size}</span>
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
