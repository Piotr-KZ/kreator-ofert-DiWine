/**
 * EditableImg — zdjęcie pobierane z Unsplash (backend proxy).
 * Pokazuje skeleton podczas ładowania, placeholder gdy brak API key.
 */

import { useState, useEffect } from "react";

interface EditableImgProps {
  query: string;
  alt?: string;
  style?: React.CSSProperties;
  orientation?: "landscape" | "portrait" | "squarish";
  width?: number;
}

export default function EditableImg({
  query,
  alt = "",
  style,
  orientation = "landscape",
  width = 1200,
}: EditableImgProps) {
  const [url, setUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!query) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    fetch(
      `/api/v1/media/unsplash/search?query=${encodeURIComponent(query)}&orientation=${orientation}&width=${width}`
    )
      .then((r) => r.json())
      .then((data) => {
        if (!cancelled && data.url) setUrl(data.url);
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [query, orientation, width]);

  const base: React.CSSProperties = {
    display: "block",
    objectFit: "cover",
    ...style,
  };

  if (loading) {
    return (
      <div
        style={{
          ...base,
          background: "linear-gradient(135deg, #F1F5F9 0%, #E2E8F0 100%)",
          animation: "pulse 1.5s ease-in-out infinite",
        }}
      />
    );
  }

  if (!url) {
    // Brak klucza Unsplash lub brak wyników — gradient placeholder
    return (
      <div
        style={{
          ...base,
          background:
            "linear-gradient(135deg, var(--brand-color, #6366F1) 0%, var(--brand-color2, #EC4899) 100%)",
          opacity: 0.35,
        }}
      />
    );
  }

  return (
    <img
      src={url}
      alt={alt}
      loading="lazy"
      style={base}
    />
  );
}
