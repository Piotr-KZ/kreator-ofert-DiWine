// ToolbarPickers.tsx — 3 komponenty dropdownowe do wbudowania w ElementToolbar
// ShapeSelector — per-sekcja override kształtu zdjęcia (obok istniejącego "Kształt")
// DecorationPicker — nowy przycisk "Dekoracja" w toolbarze sekcji
// LayoutPicker — nowy przycisk "Układ" w toolbarze sekcji (gdy ma zdjęcia)
//
// WDROŻENIE: import w ElementToolbar.tsx, dodać do sekcji `kind === 'section'` i `kind === 'image'`
// Każdy komponent to SubPanel (taki sam pattern jak istniejące panele w ElementToolbar)

import React from "react";

// ─── SHAPES (per-image override, same pool as TweakPanel global) ───

const SHAPE_PRESETS = [
  { id: 'rounded_sm', label: 'Zaokrąglony', css: 'border-radius:8px' },
  { id: 'rounded_lg', label: 'Mocno zaokr.', css: 'border-radius:20px' },
  { id: 'circle', label: 'Koło', css: 'border-radius:50%' },
  { id: 'blob_1', label: 'Blob 1', css: 'border-radius:30% 70% 70% 30%/30% 30% 70% 70%' },
  { id: 'blob_2', label: 'Blob 2', css: 'border-radius:50% 30% 60% 40%/40% 60% 30% 50%' },
  { id: 'blob_3', label: 'Blob 3', css: 'border-radius:60% 40% 30% 70%/60% 30% 70% 40%' },
  { id: 'hexagon', label: 'Hex', css: 'clip-path:polygon(25% 0%,75% 0%,100% 50%,75% 100%,25% 100%,0% 50%)' },
  { id: 'diamond', label: 'Romb', css: 'clip-path:polygon(50% 0%,100% 50%,50% 100%,0% 50%)' },
  { id: 'arch_top', label: 'Łuk', css: 'border-radius:50% 50% 8px 8px' },
  { id: 'slant_right', label: 'Ukośny', css: 'clip-path:polygon(8% 0%,100% 0%,92% 100%,0% 100%)' },
  { id: 'rect', label: 'Prostokąt', css: 'border-radius:0' },
];

// Grid of shape previews — user picks, applies to el
export function ShapeSelector({ el, brandColor = '#6366F1', accentColor = '#F59E0B', onApply }: any) {
  // Determine current shape from el styles
  const currentClip = el?.style?.clipPath || '';
  const currentRadius = el?.style?.borderRadius || '';

  const getCurrent = () => {
    for (const s of SHAPE_PRESETS) {
      if (s.css.includes('clip-path') && currentClip && s.css.includes(currentClip)) return s.id;
      if (s.css.includes('border-radius') && currentRadius && s.css.includes(currentRadius)) return s.id;
    }
    return 'rounded_sm';
  };

  const apply = (shape: typeof SHAPE_PRESETS[0]) => {
    if (!el) return;
    // Reset both
    el.style.clipPath = '';
    el.style.borderRadius = '';
    if (shape.css.startsWith('clip-path:')) {
      el.style.clipPath = shape.css.replace('clip-path:', '');
      el.style.aspectRatio = '1 / 1';
      el.style.height = 'auto';
    } else {
      el.style.borderRadius = shape.css.replace('border-radius:', '');
      el.style.aspectRatio = '';
    }
    el.style.overflow = 'hidden';
    if (onApply) onApply(shape.id);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 5 }}>
      {SHAPE_PRESETS.map(s => {
        const active = getCurrent() === s.id;
        const previewStyle: any = {};
        if (s.css.includes('clip-path:')) {
          previewStyle.clipPath = s.css.replace('clip-path:', '');
        } else {
          previewStyle.borderRadius = s.css.replace('border-radius:', '');
        }
        return (
          <button key={s.id} onClick={() => apply(s)} title={s.label}
            style={{
              aspectRatio: '1', cursor: 'pointer', padding: 0, overflow: 'hidden',
              border: active ? '2.5px solid #0F172A' : '1px solid #E2E8F0',
              borderRadius: 6, background: '#F8FAFC',
            }}>
            <div style={{
              width: '70%', height: '70%', margin: '15%',
              background: `linear-gradient(135deg, ${brandColor}, ${accentColor})`,
              ...previewStyle,
            }}/>
          </button>
        );
      })}
    </div>
  );
}

// ─── DECORATIONS (per-section background decoration) ───

const DECORATION_PRESETS: { id: string; label: string; desc: string; svg: string }[] = [
  { id: 'none', label: 'Brak', desc: 'Bez dekoracji', svg: '' },
  { id: 'dot_grid', label: 'Kropki', desc: 'Siatka kropek w tle', svg: '<circle cx="6" cy="6" r="1.2" fill="CL"/><circle cx="16" cy="6" r="1.2" fill="CL"/><circle cx="26" cy="6" r="1.2" fill="CL"/><circle cx="6" cy="14" r="1.2" fill="CL"/><circle cx="16" cy="14" r="1.2" fill="CL"/><circle cx="26" cy="14" r="1.2" fill="CL"/><circle cx="6" cy="22" r="1.2" fill="CL"/><circle cx="16" cy="22" r="1.2" fill="CL"/><circle cx="26" cy="22" r="1.2" fill="CL"/>' },
  { id: 'circles', label: 'Kółka', desc: 'Dekoracyjne kółka', svg: '<circle cx="8" cy="10" r="6" fill="none" stroke="CL" stroke-width=".8"/><circle cx="22" cy="16" r="8" fill="none" stroke="CL" stroke-width=".8"/><circle cx="14" cy="6" r="4" fill="none" stroke="CL" stroke-width=".8"/>' },
  { id: 'blob', label: 'Blob', desc: 'Organiczny kształt', svg: '<ellipse cx="16" cy="13" rx="12" ry="9" fill="CL" opacity=".25" style="transform:rotate(-10deg);transform-origin:16px 13px"/><ellipse cx="20" cy="11" rx="8" ry="6" fill="CL" opacity=".15" style="transform:rotate(15deg);transform-origin:20px 11px"/>' },
  { id: 'diagonal_lines', label: 'Linie', desc: 'Ukośne linie w tle', svg: '<line x1="0" y1="0" x2="8" y2="26" stroke="CL" stroke-width=".7"/><line x1="8" y1="0" x2="16" y2="26" stroke="CL" stroke-width=".7"/><line x1="16" y1="0" x2="24" y2="26" stroke="CL" stroke-width=".7"/><line x1="24" y1="0" x2="32" y2="26" stroke="CL" stroke-width=".7"/>' },
  { id: 'brand_shape', label: 'Motyw', desc: 'Geometria marki', svg: '<polygon points="16,2 20,10 28,10 22,16 24,24 16,20 8,24 10,16 4,10 12,10" fill="none" stroke="CL" stroke-width=".8"/>' },
];

export function DecorationPicker({ el, brandColor = '#6366F1', onApply }: any) {
  // Read current from data attribute
  const current = el?.dataset?.bgDecoration || 'none';

  const apply = (id: string) => {
    if (!el) return;
    el.dataset.bgDecoration = id;
    // Remove existing decoration overlay
    const existing = el.querySelector('[data-decoration-overlay]');
    if (existing) existing.remove();
    // Signal change
    if (onApply) onApply(id);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6 }}>
      {DECORATION_PRESETS.map(d => {
        const active = current === d.id;
        const cl = active ? brandColor : '#94A3B8';
        return (
          <button key={d.id} onClick={() => apply(d.id)}
            style={{
              padding: '6px 4px 8px', cursor: 'pointer',
              border: active ? '2px solid #0F172A' : '1px solid #E2E8F0',
              borderRadius: 7,
              background: active ? '#F1F5F9' : '#fff',
              fontFamily: 'inherit', fontSize: 10, fontWeight: 500,
              color: active ? '#0F172A' : '#64748B',
              textAlign: 'center' as const,
            }}>
            {d.svg ? (
              <div style={{ height: 28, display: 'grid', placeItems: 'center', marginBottom: 3 }}>
                <svg width="32" height="26" viewBox="0 0 32 26" dangerouslySetInnerHTML={{ __html: d.svg.replace(/CL/g, cl) }}/>
              </div>
            ) : (
              <div style={{ height: 28, display: 'grid', placeItems: 'center', marginBottom: 3, fontSize: 18, color: cl }}>—</div>
            )}
            <div style={{ fontWeight: 600, marginBottom: 1 }}>{d.label}</div>
            <div style={{ fontSize: 9, color: '#94A3B8', lineHeight: 1.2 }}>{d.desc}</div>
          </button>
        );
      })}
    </div>
  );
}

// ─── LAYOUTS (per-section photo arrangement) ───

const LAYOUT_PRESETS = [
  { id: 'single', label: 'Jedno', images: 1 },
  { id: 'duo_overlap', label: '2 nachodzące', images: 2 },
  { id: 'trio_mosaic', label: 'Mozaika 3', images: 3 },
  { id: 'scattered', label: 'Rozrzucone', images: 4 },
  { id: 'grid_2x2', label: 'Siatka 2×2', images: 4 },
];

export function LayoutPicker({ el, brandColor = '#6366F1', onApply }: any) {
  const current = el?.dataset?.photoLayout || 'single';

  const apply = (id: string) => {
    if (!el) return;
    el.dataset.photoLayout = id;
    if (onApply) onApply(id);
  };

  // Mini preview SVGs per layout
  const previews: Record<string, React.ReactNode> = {
    single: (
      <svg width="36" height="24" viewBox="0 0 36 24">
        <rect x="2" y="2" width="32" height="20" rx="2" fill={brandColor} opacity=".2" stroke={brandColor} strokeWidth=".5"/>
      </svg>
    ),
    duo_overlap: (
      <svg width="36" height="24" viewBox="0 0 36 24">
        <rect x="1" y="4" width="20" height="16" rx="2" fill={brandColor} opacity=".25" stroke={brandColor} strokeWidth=".5" transform="rotate(-3 11 12)"/>
        <rect x="14" y="2" width="20" height="16" rx="2" fill={brandColor} opacity=".15" stroke={brandColor} strokeWidth=".5" transform="rotate(2 24 10)"/>
      </svg>
    ),
    trio_mosaic: (
      <svg width="36" height="24" viewBox="0 0 36 24">
        <rect x="1" y="1" width="20" height="22" rx="2" fill={brandColor} opacity=".2" stroke={brandColor} strokeWidth=".5"/>
        <rect x="23" y="1" width="12" height="10" rx="2" fill={brandColor} opacity=".15" stroke={brandColor} strokeWidth=".5"/>
        <rect x="23" y="13" width="12" height="10" rx="2" fill={brandColor} opacity=".15" stroke={brandColor} strokeWidth=".5"/>
      </svg>
    ),
    scattered: (
      <svg width="36" height="24" viewBox="0 0 36 24">
        <rect x="2" y="3" width="14" height="10" rx="1" fill={brandColor} opacity=".2" transform="rotate(-4 9 8)"/>
        <rect x="18" y="1" width="12" height="10" rx="1" fill={brandColor} opacity=".15" transform="rotate(3 24 6)"/>
        <rect x="8" y="13" width="14" height="9" rx="1" fill={brandColor} opacity=".2" transform="rotate(-2 15 17)"/>
      </svg>
    ),
    grid_2x2: (
      <svg width="36" height="24" viewBox="0 0 36 24">
        <rect x="1" y="1" width="16" height="10" rx="1" fill={brandColor} opacity=".2" stroke={brandColor} strokeWidth=".5"/>
        <rect x="19" y="1" width="16" height="10" rx="1" fill={brandColor} opacity=".15" stroke={brandColor} strokeWidth=".5"/>
        <rect x="1" y="13" width="16" height="10" rx="1" fill={brandColor} opacity=".15" stroke={brandColor} strokeWidth=".5"/>
        <rect x="19" y="13" width="16" height="10" rx="1" fill={brandColor} opacity=".2" stroke={brandColor} strokeWidth=".5"/>
      </svg>
    ),
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 5 }}>
      {LAYOUT_PRESETS.map(l => {
        const active = current === l.id;
        return (
          <button key={l.id} onClick={() => apply(l.id)} title={l.label}
            style={{
              padding: '6px 4px', cursor: 'pointer',
              border: active ? '2px solid #0F172A' : '1px solid #E2E8F0',
              borderRadius: 7,
              background: active ? '#F1F5F9' : '#fff',
              fontFamily: 'inherit',
              textAlign: 'center' as const,
            }}>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 3 }}>
              {previews[l.id]}
            </div>
            <div style={{ fontSize: 10, fontWeight: 500, color: active ? '#0F172A' : '#64748B' }}>
              {l.label}
            </div>
          </button>
        );
      })}
    </div>
  );
}
