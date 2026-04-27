// ColorPicker + CtaPicker — adaptacja z makiety card.jsx
// Zachowany inline style 1:1

import React from 'react';
import { BRAND_PALETTE } from '@/config/blocks';
import { GradientPopover, GradTrigger } from './GradientPopover';
import type { GradStage } from './GradientPopover';

export function getContrastColor(hex: string): string {
  if (!hex || typeof hex !== 'string' || !hex.startsWith('#')) return '#fff';
  const h = hex.replace('#', '');
  if (h.length < 6) return '#fff';
  const r = parseInt(h.substr(0, 2), 16);
  const g = parseInt(h.substr(2, 2), 16);
  const b = parseInt(h.substr(4, 2), 16);
  return (0.299 * r + 0.587 * g + 0.114 * b) < 128 ? '#fff' : '#0F172A';
}

const GRADIENT_PRESETS: GradStage[] = [
  { angle: '135deg', c1: '#6366F1', c2: '#EC4899' },
  { angle: '135deg', c1: '#8B5CF6', c2: '#EC4899' },
  { angle: '135deg', c1: '#F59E0B', c2: '#EF4444' },
  { angle: '135deg', c1: '#10B981', c2: '#06B6D4' },
  { angle: '135deg', c1: '#0EA5E9', c2: '#6366F1' },
  { angle: '180deg', c1: '#FAFBFC', c2: '#E2E8F0' },
  { angle: '135deg', c1: '#FEF3C7', c2: '#FCE7F3' },
  { angle: '135deg', c1: '#0F172A', c2: '#1E293B' },
];

const ANGLES = [
  { deg: '0deg', icon: '\u2191' }, { deg: '45deg', icon: '\u2197' },
  { deg: '90deg', icon: '\u2192' }, { deg: '135deg', icon: '\u2198' },
  { deg: '180deg', icon: '\u2193' }, { deg: '225deg', icon: '\u2199' },
  { deg: '270deg', icon: '\u2190' }, { deg: '315deg', icon: '\u2196' },
];

const COLOR_PALETTE = ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#EF4444', '#10B981', '#06B6D4', '#0EA5E9', '#0F172A', '#FFFFFF', '#F1F5F9', '#FEF3C7'];

function parseGrad(g: string): GradStage {
  const m = typeof g === 'string' && g.match(/linear-gradient\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\)/i);
  if (!m) return { angle: '135deg', c1: '#6366F1', c2: '#EC4899' };
  return { angle: m[1].trim(), c1: m[2].trim(), c2: m[3].trim() };
}

// ─── ColorPicker ──────────────────────────────────────
export function ColorPicker({ value, palette, onChange, brandValue }: {
  value: string | null;
  palette?: string[];
  onChange: (v: string | null) => void;
  brandValue?: string;
}) {
  const [customOpen, setCustomOpen] = React.useState(false);
  const [gradientOpen, setGradientOpen] = React.useState(false);
  const pal = palette || BRAND_PALETTE.map(p => p.value);
  const useBrand = value == null;
  const current = value || brandValue || '#FFFFFF';
  const isGradient = typeof current === 'string' && current.includes('gradient');
  const isPreset = !useBrand && !isGradient && pal.some(v => v.toLowerCase() === current.toLowerCase());

  const [stage, setStage] = React.useState<GradStage>(() => isGradient ? parseGrad(current) : { angle: '135deg', c1: '#6366F1', c2: '#EC4899' });
  React.useEffect(() => { if (gradientOpen) setStage(isGradient ? parseGrad(current) : { angle: '135deg', c1: '#6366F1', c2: '#EC4899' }); }, [gradientOpen]);

  return (
    <div>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {brandValue != null && (
          <button title="Uzyj koloru z brandu" onClick={() => onChange(null)}
            style={{
              width: 30, height: 30, borderRadius: 9,
              background: brandValue,
              border: '2px solid #fff',
              boxShadow: useBrand ? '0 0 0 2px #6366F1' : '0 0 0 1px #E2E8F0',
              cursor: 'pointer', position: 'relative', padding: 0,
            }}>
            <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: getContrastColor(brandValue), fontSize: 13, fontWeight: 700 }}>*</span>
          </button>
        )}
        {pal.filter(v => !(brandValue != null && v.toLowerCase() === brandValue.toLowerCase())).map((val, idx) => {
          const active = !useBrand && val.toLowerCase() === current.toLowerCase();
          return (
            <button key={idx} title={val} onClick={() => onChange(val)}
              style={{
                width: 30, height: 30, borderRadius: 9,
                background: val, border: '2px solid #fff',
                boxShadow: active ? '0 0 0 2px #6366F1' : '0 0 0 1px #E2E8F0',
                cursor: 'pointer', transition: 'transform .1s', position: 'relative', padding: 0,
              }}
              onMouseEnter={e => (e.currentTarget.style.transform = 'scale(1.08)')}
              onMouseLeave={e => (e.currentTarget.style.transform = 'scale(1)')}>
              {active && <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: getContrastColor(val), fontSize: 13, fontWeight: 700 }}>+</span>}
            </button>
          );
        })}
        <GradTrigger
          active={isGradient && !useBrand}
          current={current}
          onClick={() => { setGradientOpen(o => !o); setCustomOpen(false); }}
          title="Gradient"
          onPopover={(anchorRef) => (
            <GradientPopover
              anchorRef={anchorRef}
              open={gradientOpen}
              onClose={() => setGradientOpen(false)}
              title="Gradient"
              stage={stage}
              setStage={setStage}
              presets={GRADIENT_PRESETS}
              angles={ANGLES}
              palette={COLOR_PALETTE}
              onSave={() => { onChange(`linear-gradient(${stage.angle}, ${stage.c1}, ${stage.c2})`); setGradientOpen(false); }}
            />
          )}
        />
        {/* Custom color */}
        <div style={{ position: 'relative' }}>
          <button onClick={() => setCustomOpen(o => !o)} title="Wlasny kolor"
            style={{
              width: 30, height: 30, borderRadius: 9,
              background: !isPreset && !useBrand ? current : 'conic-gradient(from 0deg, #F59E0B, #EC4899, #6366F1, #06B6D4, #10B981, #F59E0B)',
              border: '2px solid #fff',
              boxShadow: !isPreset && !useBrand ? '0 0 0 2px #6366F1' : '0 0 0 1px #E2E8F0',
              cursor: 'pointer', position: 'relative', padding: 0,
            }}>
            {!isPreset && !useBrand ? (
              <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: getContrastColor(current), fontSize: 13, fontWeight: 700 }}>+</span>
            ) : (
              <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: '#fff', fontSize: 14, fontWeight: 700, textShadow: '0 1px 2px rgba(0,0,0,.3)' }}>+</span>
            )}
          </button>
          {customOpen && (
            <div style={{
              position: 'absolute', top: 'calc(100% + 6px)', right: 0,
              background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10,
              padding: 12, zIndex: 10, boxShadow: '0 8px 24px rgba(15,23,42,.12)', minWidth: 200,
            }}
              onMouseLeave={() => setTimeout(() => setCustomOpen(false), 150)}>
              <div style={{ fontSize: 11, color: '#64748B', marginBottom: 8, fontWeight: 600 }}>Wlasny kolor</div>
              <input type="color" value={current} onChange={e => onChange(e.target.value)}
                style={{ width: '100%', height: 40, border: '1px solid #E2E8F0', borderRadius: 8, cursor: 'pointer', background: 'none' }}/>
              <input type="text" value={current.toUpperCase()} onChange={e => { const v = e.target.value; if (/^#[0-9A-Fa-f]{0,6}$/.test(v)) onChange(v); }}
                style={{ width: '100%', marginTop: 8, height: 30, padding: '0 10px', border: '1px solid #E2E8F0', borderRadius: 6, fontFamily: 'ui-monospace, monospace', fontSize: 12, outline: 'none' }}/>
              <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 6 }}>Tip: trzymaj kontrast z tekstem</div>
            </div>
          )}
        </div>
      </div>
      <div style={{ marginTop: 8, fontSize: 11, color: '#64748B', display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ width: 12, height: 12, borderRadius: 3, background: current, border: '1px solid #E2E8F0' }}/>
        <span style={{ fontFamily: 'ui-monospace, monospace' }}>{typeof current === 'string' && current.startsWith('#') ? current.toUpperCase() : 'gradient'}</span>
        {useBrand && <span style={{ color: '#6366F1', fontWeight: 600 }}>z brandu</span>}
        {isPreset && !useBrand && <span>z palety brandu</span>}
        {!isPreset && !useBrand && <span style={{ color: '#F59E0B', fontWeight: 600 }}>wlasny</span>}
      </div>
    </div>
  );
}

// ─── CtaPicker ──────────────────────────────────────
export function CtaPicker({ value, brandCta, onChange }: {
  value: string | null;
  brandCta: string;
  onChange: (v: string | null) => void;
}) {
  const [customOpen, setCustomOpen] = React.useState(false);
  const [gradientOpen, setGradientOpen] = React.useState(false);
  const usesGlobal = value === null || value === undefined;
  const effective = usesGlobal ? brandCta : value;
  const isGradient = typeof effective === 'string' && effective.includes('gradient');

  const CTA_GRADIENT_PRESETS: GradStage[] = [
    { angle: '135deg', c1: '#6366F1', c2: '#EC4899' },
    { angle: '135deg', c1: '#8B5CF6', c2: '#EC4899' },
    { angle: '135deg', c1: '#F59E0B', c2: '#EF4444' },
    { angle: '135deg', c1: '#10B981', c2: '#06B6D4' },
    { angle: '135deg', c1: '#0EA5E9', c2: '#6366F1' },
    { angle: '135deg', c1: '#EC4899', c2: '#F59E0B' },
  ];

  const [stage, setStage] = React.useState<GradStage>(() => isGradient ? parseGrad(effective) : { angle: '135deg', c1: '#6366F1', c2: '#EC4899' });
  React.useEffect(() => { if (gradientOpen) setStage(isGradient ? parseGrad(effective) : { angle: '135deg', c1: '#6366F1', c2: '#EC4899' }); }, [gradientOpen]);

  const ctaPalette = [
    { val: brandCta, name: 'Brand (globalny)' },
    { val: '#EC4899', name: 'Rozowy' },
    { val: '#F59E0B', name: 'Zolty' },
    { val: '#10B981', name: 'Zielony' },
    { val: '#EF4444', name: 'Czerwony' },
    { val: '#0F172A', name: 'Czarny' },
  ];

  return (
    <div>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        <button title="Uzyj globalnego koloru brandu" onClick={() => onChange(null)}
          style={{
            width: 30, height: 30, borderRadius: 9,
            background: brandCta, border: '2px solid #fff',
            boxShadow: usesGlobal ? '0 0 0 2px #6366F1' : '0 0 0 1px #E2E8F0',
            cursor: 'pointer', position: 'relative', padding: 0,
            transition: 'transform .1s',
          }}
          onMouseEnter={e => (e.currentTarget.style.transform = 'scale(1.08)')}
          onMouseLeave={e => (e.currentTarget.style.transform = 'scale(1)')}>
          <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: getContrastColor(brandCta), fontSize: 11, fontWeight: 700 }}>*</span>
          {usesGlobal && <span style={{ position: 'absolute', bottom: -4, left: '50%', transform: 'translateX(-50%)', width: 14, height: 2, background: '#6366F1', borderRadius: 2 }}/>}
        </button>
        {ctaPalette.slice(1).map(p => {
          const active = !usesGlobal && p.val.toLowerCase() === (value || '').toLowerCase();
          return (
            <button key={p.val} title={p.name} onClick={() => onChange(p.val)}
              style={{
                width: 30, height: 30, borderRadius: 9,
                background: p.val, border: '2px solid #fff',
                boxShadow: active ? '0 0 0 2px #6366F1' : '0 0 0 1px #E2E8F0',
                cursor: 'pointer', transition: 'transform .1s', position: 'relative', padding: 0,
              }}
              onMouseEnter={e => (e.currentTarget.style.transform = 'scale(1.08)')}
              onMouseLeave={e => (e.currentTarget.style.transform = 'scale(1)')}>
              {active && <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: getContrastColor(p.val), fontSize: 12, fontWeight: 700 }}>+</span>}
            </button>
          );
        })}
        <GradTrigger
          active={isGradient}
          current={effective}
          onClick={() => { setGradientOpen(o => !o); setCustomOpen(false); }}
          title="Gradient CTA"
          onPopover={(anchorRef) => (
            <GradientPopover
              anchorRef={anchorRef}
              open={gradientOpen}
              onClose={() => setGradientOpen(false)}
              title="Gradient CTA"
              stage={stage}
              setStage={setStage}
              presets={CTA_GRADIENT_PRESETS}
              angles={ANGLES}
              palette={COLOR_PALETTE}
              onSave={() => { onChange(`linear-gradient(${stage.angle}, ${stage.c1}, ${stage.c2})`); setGradientOpen(false); }}
            />
          )}
        />
        <div style={{ position: 'relative' }}>
          <button onClick={() => setCustomOpen(o => !o)} title="Wlasny kolor CTA"
            style={{
              width: 30, height: 30, borderRadius: 9,
              background: 'conic-gradient(from 0deg, #F59E0B, #EC4899, #6366F1, #06B6D4, #10B981, #F59E0B)',
              border: '2px solid #fff', boxShadow: '0 0 0 1px #E2E8F0',
              cursor: 'pointer', position: 'relative', padding: 0,
            }}>
            <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: '#fff', fontSize: 14, fontWeight: 700, textShadow: '0 1px 2px rgba(0,0,0,.3)' }}>+</span>
          </button>
          {customOpen && (
            <div style={{
              position: 'absolute', top: 'calc(100% + 6px)', right: 0,
              background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10,
              padding: 12, zIndex: 10, boxShadow: '0 8px 24px rgba(15,23,42,.12)', minWidth: 200,
            }}
              onMouseLeave={() => setTimeout(() => setCustomOpen(false), 150)}>
              <div style={{ fontSize: 11, color: '#64748B', marginBottom: 8, fontWeight: 600 }}>Wlasny kolor CTA</div>
              <input type="color" value={effective} onChange={e => onChange(e.target.value)} style={{ width: '100%', height: 40, border: '1px solid #E2E8F0', borderRadius: 8, cursor: 'pointer', background: 'none' }}/>
            </div>
          )}
        </div>
      </div>
      <div style={{ marginTop: 8, fontSize: 11, color: '#64748B', display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ width: 12, height: 12, borderRadius: 3, background: effective, border: '1px solid #E2E8F0' }}/>
        <span style={{ fontFamily: 'ui-monospace, monospace' }}>{isGradient ? 'gradient' : effective.toUpperCase()}</span>
        {usesGlobal && <span style={{ color: '#6366F1', fontWeight: 600 }}>z brandu</span>}
        {!usesGlobal && <button onClick={() => onChange(null)} style={{ marginLeft: 'auto', padding: '2px 6px', background: 'transparent', border: 'none', color: '#6366F1', fontSize: 11, cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600 }}>Reset</button>}
      </div>
    </div>
  );
}
