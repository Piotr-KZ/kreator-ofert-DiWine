// TweakPanel v2 — rozbudowany panel globalnych ustawień strony
// 6 sekcji: Kolory, Typografia, Przyciski CTA, Karty, Zdjęcia, Motyw i dekoracje
// Drop-in replacement for TweakPanel in Step5Wizualizacja.tsx

import React from "react";

// ─── Constants ───

const BRAND_COLORS = [
  '#0F766E', '#065F46', '#7C3AED', '#6366F1',
  '#EC4899', '#DC2626', '#F59E0B', '#0F172A',
];

const TEXT_COLORS = [
  { id: 'auto', label: 'Auto', val: null },
  { id: 'dark', label: 'Ciemny', val: '#1F2937' },
  { id: 'gray', label: 'Szary', val: '#475569' },
  { id: 'brown', label: 'Brązowy', val: '#44403C' },
  { id: 'brand', label: 'Kolor marki', val: '__brand__' },
];

const HEADING_FONTS = [
  { label: 'Fraunces', val: "'Fraunces', serif" },
  { label: 'Playfair Display', val: "'Playfair Display', serif" },
  { label: 'Instrument Serif', val: "'Instrument Serif', serif" },
  { label: 'DM Serif Display', val: "'DM Serif Display', serif" },
  { label: 'Cormorant Garamond', val: "'Cormorant Garamond', serif" },
  { label: 'Space Grotesk', val: "'Space Grotesk', sans-serif" },
  { label: 'Inter', val: "'Inter', sans-serif" },
  { label: 'Manrope', val: "'Manrope', sans-serif" },
];

const BODY_FONTS = [
  { label: 'Inter', val: "'Inter', sans-serif" },
  { label: 'Manrope', val: "'Manrope', sans-serif" },
  { label: 'Space Grotesk', val: "'Space Grotesk', sans-serif" },
  { label: 'IBM Plex Sans', val: "'IBM Plex Sans', sans-serif" },
];

const CTA_STYLES = [
  { id: 'filled', label: 'Wypełniony' },
  { id: 'outline', label: 'Kontur' },
  { id: 'ghost', label: 'Ghost' },
];

const CTA_SIZES = [
  { id: 'sm', label: 'Mały' },
  { id: 'md', label: 'Średni' },
  { id: 'lg', label: 'Duży' },
];

const CARD_SHADOWS = [
  { id: 'none', label: 'Brak' },
  { id: 'subtle', label: 'Delikatny' },
  { id: 'strong', label: 'Wyraźny' },
];

const PHOTO_SHAPES = [
  { id: 'rounded_sm', label: 'Zaokrąglony', preview: 'borderRadius:8px' },
  { id: 'rounded_lg', label: 'Mocno zaokr.', preview: 'borderRadius:20px' },
  { id: 'circle', label: 'Koło', preview: 'borderRadius:50%' },
  { id: 'blob_1', label: 'Blob 1', preview: 'borderRadius:30% 70% 70% 30%/30% 30% 70% 70%' },
  { id: 'blob_2', label: 'Blob 2', preview: 'borderRadius:50% 30% 60% 40%/40% 60% 30% 50%' },
  { id: 'hexagon', label: 'Hex', preview: 'clipPath:polygon(25% 0%,75% 0%,100% 50%,75% 100%,25% 100%,0% 50%)' },
  { id: 'arch_top', label: 'Łuk', preview: 'borderRadius:50% 50% 8px 8px' },
  { id: 'rect', label: 'Prostokąt', preview: 'borderRadius:0' },
];

const PHOTO_FILTERS = [
  { id: 'none', label: 'Brak' },
  { id: 'warm', label: 'Ciepły' },
  { id: 'cool', label: 'Zimny' },
  { id: 'grayscale', label: 'B&W' },
  { id: 'sepia', label: 'Sepia' },
];

const BRAND_MOTIFS = [
  { id: 'none', label: 'Brak' },
  { id: 'diamond', label: 'Romb', icon: '◇' },
  { id: 'circle_ring', label: 'Okrąg', icon: '○' },
  { id: 'triangle', label: 'Trójkąt', icon: '△' },
  { id: 'hexagon', label: 'Sześciokąt', icon: '⬡' },
  { id: 'slash', label: 'Ukośnik', icon: '/' },
  { id: 'dot_cluster', label: 'Kropki', icon: '∴' },
];

const MOTIF_PLACEMENTS = [
  { id: 'hero_bg', label: 'Hero' },
  { id: 'card_accent', label: 'Karty' },
  { id: 'separator', label: 'Separatory' },
  { id: 'cta_overlay', label: 'CTA' },
];

const BG_DECORATIONS = [
  { id: 'none', label: 'Brak' },
  { id: 'dot_grid', label: 'Kropki' },
  { id: 'circles', label: 'Kółka' },
  { id: 'blob', label: 'Blob' },
  { id: 'diagonal_lines', label: 'Linie' },
];

// ─── Defaults (extend WIZ_TWEAKS_DEFAULT) ───

export const TWEAKS_DEFAULT = {
  // Kolory (existing)
  brandColor: '#0F766E',
  accentColor: '#F59E0B',
  ctaColor: null,            // null = use brandColor
  headingColor: null,        // null = auto
  textColor: '#1F2937',

  // Typografia (extended)
  headingFont: "'Fraunces', serif",
  bodyFont: "'Inter', sans-serif",
  fontPair: 'Fraunces + Inter',  // backward compat
  h1Size: 40,
  h2Size: 28,
  h3Size: 20,
  bodySize: 16,

  // CTA (new)
  ctaStyle: 'filled',
  ctaRadius: 8,
  ctaSize: 'md',

  // Karty (new)
  cardRadius: 12,
  cardShadow: 'subtle',
  density: 'comfortable',

  // Zdjęcia (new)
  photoShape: 'rounded_sm',
  photoFilter: 'none',

  // Motyw marki (new)
  brandMotif: 'none',
  motifUsage: ['hero_bg', 'separator'],
  motifOpacity: 0.08,
  bgDecoration: 'none',

  // Tło (existing)
  headerBg: '#FFFFFF',
};

// ─── Sub-components ───

function TweakRow({ label, children, collapsed, onToggle }: any) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div
        onClick={onToggle}
        style={{
          fontSize: 11, fontWeight: 600, color: '#475569',
          textTransform: 'uppercase' as const, letterSpacing: 0.4, marginBottom: 8,
          cursor: onToggle ? 'pointer' : 'default',
          display: 'flex', alignItems: 'center', gap: 4,
        }}
      >
        {onToggle && (
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"
            style={{ transform: collapsed ? 'rotate(-90deg)' : 'rotate(0)', transition: 'transform .15s' }}>
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        )}
        {label}
      </div>
      {!collapsed && children}
    </div>
  );
}

function ColorSwatches({ colors, value, onChange, showCustom = true }: any) {
  const [customOpen, setCustomOpen] = React.useState(false);
  const hex = (value || '').toUpperCase();
  const isCustom = value && !colors.some((c: string) => c.toUpperCase() === hex);
  return (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${colors.length + (showCustom ? 1 : 0)}, 1fr)`, gap: 4 }}>
        {colors.map((c: string) => (
          <button key={c} onClick={() => onChange(c)} style={{
            aspectRatio: '1', borderRadius: 6, cursor: 'pointer', padding: 0,
            background: c,
            border: hex === c.toUpperCase() ? '2.5px solid #0F172A' : '1.5px solid #E2E8F0',
          }}/>
        ))}
        {showCustom && (
          <div style={{ position: 'relative' }}>
            <button onClick={() => setCustomOpen(o => !o)} style={{
              width: '100%', aspectRatio: '1', borderRadius: 6, cursor: 'pointer', padding: 0,
              background: isCustom ? value : 'conic-gradient(from 180deg, #EF4444, #F59E0B, #10B981, #3B82F6, #8B5CF6, #EF4444)',
              border: isCustom ? '2.5px solid #0F172A' : '1.5px solid #E2E8F0',
              display: 'grid', placeItems: 'center',
            }}>
              {!isCustom && <span style={{ color: '#fff', fontSize: 13, fontWeight: 700, textShadow: '0 1px 1px rgba(0,0,0,.3)' }}>+</span>}
            </button>
            {customOpen && (
              <div style={{
                position: 'absolute', top: 'calc(100% + 4px)', left: 0, zIndex: 20,
                background: '#fff', padding: 8, borderRadius: 8,
                boxShadow: '0 8px 24px rgba(15,23,42,.12)', border: '1px solid #E2E8F0',
              }}>
                <input type="color" value={value || '#6366F1'} onChange={e => { onChange(e.target.value); setCustomOpen(false); }}
                  style={{ width: 80, height: 32, border: 'none', cursor: 'pointer', background: 'none' }}/>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}

function Slider({ value, min, max, step = 1, unit = 'px', onChange }: any) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        style={{ flex: 1, accentColor: '#6366F1' }}/>
      <span style={{ fontSize: 11, fontWeight: 600, color: '#334155', minWidth: 36, textAlign: 'right' as const }}>
        {value}{unit}
      </span>
    </div>
  );
}

function ToggleGroup({ options, value, onChange }: any) {
  return (
    <div style={{ display: 'inline-flex', background: '#F1F5F9', padding: 2, borderRadius: 7, gap: 1, width: '100%' }}>
      {options.map((o: any) => (
        <button key={o.id} onClick={() => onChange(o.id)} style={{
          flex: 1, padding: '7px 6px', border: 'none',
          background: value === o.id ? '#fff' : 'transparent',
          borderRadius: 5, cursor: 'pointer',
          fontFamily: 'inherit', fontSize: 11.5,
          fontWeight: value === o.id ? 600 : 500,
          color: value === o.id ? '#0F172A' : '#64748B',
          boxShadow: value === o.id ? '0 1px 2px rgba(0,0,0,.06)' : 'none',
        }}>{o.label}</button>
      ))}
    </div>
  );
}

function FontSelect({ fonts, value, onChange, label }: any) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ fontSize: 10, fontWeight: 600, color: '#94A3B8', marginBottom: 4 }}>{label}</div>
      <select value={value} onChange={e => onChange(e.target.value)}
        style={{
          width: '100%', padding: '8px 10px', border: '1px solid #E2E8F0',
          borderRadius: 7, fontSize: 12.5, fontFamily: 'inherit',
          background: '#fff', cursor: 'pointer', color: '#0F172A',
        }}>
        {fonts.map((f: any) => (
          <option key={f.val} value={f.val} style={{ fontFamily: f.val }}>{f.label}</option>
        ))}
      </select>
    </div>
  );
}

// ─── Collapsed sections logic ───

function Section({ title, defaultOpen = true, children }: any) {
  const [open, setOpen] = React.useState(defaultOpen);
  return (
    <div style={{
      marginBottom: 6,
      border: '1px solid #E2E8F0',
      borderRadius: 10,
      overflow: 'hidden',
    }}>
      <button onClick={() => setOpen(o => !o)} style={{
        width: '100%', padding: '10px 12px',
        background: open ? '#F8FAFC' : '#fff',
        border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 8,
        fontFamily: 'inherit', fontSize: 12, fontWeight: 600, color: '#0F172A',
        textAlign: 'left' as const,
      }}>
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"
          style={{ transform: open ? 'rotate(0)' : 'rotate(-90deg)', transition: 'transform .15s' }}>
          <polyline points="6 9 12 15 18 9"/>
        </svg>
        {title}
      </button>
      {open && (
        <div style={{ padding: '12px 12px 4px' }}>
          {children}
        </div>
      )}
    </div>
  );
}

// ─── Main TweakPanel ───

export function TweakPanel({ tweaks, onPatch }: { tweaks: any; onPatch: (key: string, val: any) => void }) {
  const t = { ...TWEAKS_DEFAULT, ...tweaks };

  return (
    <div>
      <h3 style={{ margin: '0 0 3px', fontSize: 15, fontWeight: 600 }}>Globalne style</h3>
      <p style={{ margin: '0 0 14px', fontSize: 12, color: '#64748B' }}>Dostrój wygląd całej strony</p>

      {/* 1. KOLORY */}
      <Section title="Kolory" defaultOpen={true}>
        <TweakRow label="Kolor główny">
          <ColorSwatches colors={BRAND_COLORS} value={t.brandColor} onChange={(v: string) => onPatch('brandColor', v)}/>
        </TweakRow>

        <TweakRow label="Kolor akcentu">
          <ColorSwatches colors={BRAND_COLORS} value={t.accentColor} onChange={(v: string) => onPatch('accentColor', v)}/>
        </TweakRow>

        <TweakRow label="Kolor CTA">
          <ColorSwatches
            colors={[t.brandColor, t.accentColor, '#0F172A', '#DC2626', '#059669', '#7C3AED', '#EC4899', '#F59E0B']}
            value={t.ctaColor || t.brandColor}
            onChange={(v: string) => onPatch('ctaColor', v)}
          />
          <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 4 }}>
            Gradient CTA: ustaw w toolbarze przycisku (2 kolory + kierunek)
          </div>
        </TweakRow>

        <TweakRow label="Kolor nagłówków">
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' as const }}>
            {TEXT_COLORS.map(tc => (
              <button key={tc.id} onClick={() => onPatch('headingColor', tc.val)} style={{
                padding: '5px 10px', borderRadius: 6, cursor: 'pointer',
                border: t.headingColor === tc.val ? '2px solid #0F172A' : '1px solid #E2E8F0',
                background: '#fff', fontFamily: 'inherit', fontSize: 11, fontWeight: 500,
                color: tc.val === '__brand__' ? t.brandColor : (tc.val || '#1F2937'),
              }}>{tc.label}</button>
            ))}
          </div>
        </TweakRow>
      </Section>

      {/* 2. TYPOGRAFIA */}
      <Section title="Typografia" defaultOpen={false}>
        <FontSelect fonts={HEADING_FONTS} value={t.headingFont} onChange={(v: string) => onPatch('headingFont', v)} label="Czcionka nagłówków"/>
        <FontSelect fonts={BODY_FONTS} value={t.bodyFont} onChange={(v: string) => onPatch('bodyFont', v)} label="Czcionka treści"/>

        <TweakRow label="Rozmiar H1">
          <Slider value={t.h1Size} min={28} max={56} onChange={(v: number) => onPatch('h1Size', v)}/>
        </TweakRow>
        <TweakRow label="Rozmiar H2">
          <Slider value={t.h2Size} min={22} max={40} onChange={(v: number) => onPatch('h2Size', v)}/>
        </TweakRow>
        <TweakRow label="Rozmiar H3">
          <Slider value={t.h3Size} min={16} max={28} onChange={(v: number) => onPatch('h3Size', v)}/>
        </TweakRow>
        <TweakRow label="Rozmiar treści">
          <Slider value={t.bodySize} min={14} max={20} onChange={(v: number) => onPatch('bodySize', v)}/>
        </TweakRow>
      </Section>

      {/* 3. PRZYCISKI CTA */}
      <Section title="Przyciski CTA" defaultOpen={false}>
        <TweakRow label="Styl">
          <ToggleGroup options={CTA_STYLES} value={t.ctaStyle} onChange={(v: string) => onPatch('ctaStyle', v)}/>
        </TweakRow>
        <TweakRow label="Zaokrąglenie">
          <Slider value={t.ctaRadius} min={0} max={50} onChange={(v: number) => onPatch('ctaRadius', v)}/>
        </TweakRow>
        <TweakRow label="Rozmiar">
          <ToggleGroup options={CTA_SIZES} value={t.ctaSize} onChange={(v: string) => onPatch('ctaSize', v)}/>
        </TweakRow>
        <div style={{
          marginTop: 8, padding: 10, borderRadius: 8, background: '#F8FAFC',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12,
        }}>
          <button style={{
            padding: t.ctaSize === 'sm' ? '8px 16px' : t.ctaSize === 'lg' ? '14px 28px' : '10px 22px',
            borderRadius: t.ctaRadius,
            background: t.ctaStyle === 'filled' ? (t.ctaColor || t.brandColor) : 'transparent',
            color: t.ctaStyle === 'filled' ? '#fff' : (t.ctaColor || t.brandColor),
            border: t.ctaStyle === 'ghost' ? 'none' : `2px solid ${t.ctaColor || t.brandColor}`,
            fontFamily: 'inherit', fontSize: t.ctaSize === 'sm' ? 12 : t.ctaSize === 'lg' ? 15 : 13,
            fontWeight: 600, cursor: 'default',
            textDecoration: t.ctaStyle === 'ghost' ? 'underline' : 'none',
          }}>Podgląd CTA</button>
        </div>
      </Section>

      {/* 4. KARTY I ELEMENTY */}
      <Section title="Karty i elementy" defaultOpen={false}>
        <TweakRow label="Zaokrąglenie kart">
          <Slider value={t.cardRadius} min={0} max={24} onChange={(v: number) => onPatch('cardRadius', v)}/>
        </TweakRow>
        <TweakRow label="Cień kart">
          <ToggleGroup options={CARD_SHADOWS} value={t.cardShadow} onChange={(v: string) => onPatch('cardShadow', v)}/>
        </TweakRow>
        <TweakRow label="Gęstość">
          <ToggleGroup
            options={[
              { id: 'compact', label: 'Kompakt' },
              { id: 'comfortable', label: 'Komfort' },
              { id: 'spacious', label: 'Luźna' },
            ]}
            value={t.density}
            onChange={(v: string) => onPatch('density', v)}
          />
        </TweakRow>
      </Section>

      {/* 5. ZDJĘCIA */}
      <Section title="Zdjęcia" defaultOpen={false}>
        <TweakRow label="Domyślny kształt">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6 }}>
            {PHOTO_SHAPES.map(s => {
              const style: any = {};
              const parts = s.preview.split(';').filter(Boolean);
              parts.forEach(p => {
                const [k, v] = p.split(':');
                if (k && v) {
                  const camel = k.trim().replace(/-([a-z])/g, (_: string, c: string) => c.toUpperCase());
                  style[camel] = v.trim();
                }
              });
              return (
                <button key={s.id} onClick={() => onPatch('photoShape', s.id)}
                  title={s.label}
                  style={{
                    aspectRatio: '1', cursor: 'pointer', padding: 0, overflow: 'hidden',
                    border: t.photoShape === s.id ? '2.5px solid #0F172A' : '1.5px solid #E2E8F0',
                    borderRadius: 8, position: 'relative' as const,
                  }}>
                  <div style={{
                    width: '80%', height: '80%', margin: '10%',
                    background: `linear-gradient(135deg, ${t.brandColor}, ${t.accentColor})`,
                    ...style,
                  }}/>
                </button>
              );
            })}
          </div>
        </TweakRow>
        <TweakRow label="Domyślny filtr">
          <ToggleGroup options={PHOTO_FILTERS} value={t.photoFilter} onChange={(v: string) => onPatch('photoFilter', v)}/>
        </TweakRow>
      </Section>

      {/* 6. MOTYW I DEKORACJE */}
      <Section title="Motyw marki" defaultOpen={false}>
        <TweakRow label="Kształt motywu">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 4 }}>
            {BRAND_MOTIFS.map(m => (
              <button key={m.id} onClick={() => onPatch('brandMotif', m.id)}
                style={{
                  padding: '8px 4px', cursor: 'pointer',
                  border: t.brandMotif === m.id ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  borderRadius: 7, background: t.brandMotif === m.id ? '#EEF2FF' : '#fff',
                  fontFamily: 'inherit', fontSize: m.icon ? 16 : 11, fontWeight: 500,
                  color: t.brandMotif === m.id ? '#4338CA' : '#64748B',
                  textAlign: 'center' as const,
                }}>
                {m.icon || m.label}
              </button>
            ))}
          </div>
        </TweakRow>

        {t.brandMotif !== 'none' && (
          <>
            <TweakRow label="Gdzie użyć">
              <div style={{ display: 'flex', flexWrap: 'wrap' as const, gap: 6 }}>
                {MOTIF_PLACEMENTS.map(p => {
                  const active = (t.motifUsage || []).includes(p.id);
                  return (
                    <button key={p.id}
                      onClick={() => {
                        const usage = t.motifUsage || [];
                        const next = active ? usage.filter((u: string) => u !== p.id) : [...usage, p.id];
                        onPatch('motifUsage', next);
                      }}
                      style={{
                        padding: '5px 10px', borderRadius: 6, cursor: 'pointer',
                        border: active ? `2px solid ${t.brandColor}` : '1px solid #E2E8F0',
                        background: active ? `${t.brandColor}18` : '#fff',
                        fontFamily: 'inherit', fontSize: 11, fontWeight: 500,
                        color: active ? t.brandColor : '#64748B',
                      }}>
                      {p.label}
                    </button>
                  );
                })}
              </div>
            </TweakRow>
            <TweakRow label="Intensywność">
              <Slider value={Math.round(t.motifOpacity * 100)} min={3} max={15} unit="%" onChange={(v: number) => onPatch('motifOpacity', v / 100)}/>
            </TweakRow>
          </>
        )}

        <TweakRow label="Dekoracja tła (domyślna)">
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' as const }}>
            {BG_DECORATIONS.map(d => (
              <button key={d.id} onClick={() => onPatch('bgDecoration', d.id)}
                style={{
                  padding: '5px 10px', borderRadius: 6, cursor: 'pointer',
                  border: t.bgDecoration === d.id ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  background: t.bgDecoration === d.id ? '#F1F5F9' : '#fff',
                  fontFamily: 'inherit', fontSize: 11, fontWeight: 500,
                  color: t.bgDecoration === d.id ? '#0F172A' : '#64748B',
                }}>
                {d.label}
              </button>
            ))}
          </div>
        </TweakRow>
      </Section>
    </div>
  );
}

export default TweakPanel;
