import { useState, useRef } from 'react';
import type { Gradient } from '@/types/lab';
import { bgColorToCSS, isDark } from '@/types/lab';
import { GradientPopover } from './GradientPopover';

const SECTION_PALETTE = [
  '#FFFFFF','#F8FAFC','#FEF7ED','#FEF3C7','#ECFDF5','#EEF2FF','#FCE7F3','#0F172A',
];

interface Props {
  value: string | Gradient | null | undefined;
  brandValue?: string;          // CSS string of brand bg — shown as "★ z brandu"
  onChange: (v: string | Gradient | null) => void;
  palette?: string[];
}

export function ColorPicker({ value, brandValue, onChange, palette = SECTION_PALETTE }: Props) {
  const [customOpen, setCustomOpen] = useState(false);
  const [gradOpen, setGradOpen] = useState(false);
  const gradAnchorRef = useRef<HTMLButtonElement>(null);

  const useBrand = value == null;
  const isGradient = typeof value === 'object' && value?.type === 'gradient';
  const isGradientStr = typeof value === 'string' && value.includes('gradient');
  const currentCSS = bgColorToCSS(value, brandValue ?? '#FFFFFF');
  const isPreset = !useBrand && !isGradient && !isGradientStr && palette.some(p => p.toLowerCase() === (value as string)?.toLowerCase());

  const currentGradient: Gradient = isGradient
    ? (value as Gradient)
    : { type: 'gradient', angle: '135deg', c1: '#6366F1', c2: '#EC4899' };

  const hexValue = (!useBrand && !isGradient && !isGradientStr)
    ? ((value as string) || '#FFFFFF')
    : '#6366F1';

  return (
    <div className="flex gap-1.5 flex-wrap items-center">
      {/* Brand swatch */}
      {brandValue != null && (
        <button
          title="Z brandu (domyślny)"
          onClick={() => onChange(null)}
          className="w-8 h-8 rounded-lg border-2 cursor-pointer relative flex-shrink-0"
          style={{
            background: brandValue,
            borderColor: '#fff',
            boxShadow: useBrand ? '0 0 0 2px #6366F1' : '0 0 0 1px #E2E8F0',
          }}
        >
          <span
            className="absolute inset-0 grid place-items-center text-sm font-bold"
            style={{ color: isDark(brandValue) ? '#fff' : '#0F172A' }}
          >★</span>
        </button>
      )}

      {/* Palette swatches */}
      {palette.filter(p => !(brandValue && p.toLowerCase() === brandValue.toLowerCase())).map(p => {
        const active = !useBrand && !isGradient && !isGradientStr && (value as string)?.toLowerCase() === p.toLowerCase();
        return (
          <button
            key={p}
            title={p}
            onClick={() => onChange(p)}
            className="w-8 h-8 rounded-lg border-2 cursor-pointer relative flex-shrink-0 transition-transform hover:scale-105"
            style={{
              background: p,
              borderColor: '#fff',
              boxShadow: active ? '0 0 0 2px #6366F1' : '0 0 0 1px #E2E8F0',
            }}
          >
            {active && (
              <span className="absolute inset-0 grid place-items-center text-sm font-bold"
                style={{ color: isDark(p) ? '#fff' : '#0F172A' }}>✓</span>
            )}
          </button>
        );
      })}

      {/* Gradient button */}
      <button
        ref={gradAnchorRef}
        onClick={() => { setGradOpen(o => !o); setCustomOpen(false); }}
        title="Gradient"
        className="h-8 px-2 rounded-lg border-2 flex items-center gap-1.5 cursor-pointer text-xs font-semibold flex-shrink-0"
        style={{
          background: '#fff',
          borderColor: (isGradient || isGradientStr) && !useBrand ? '#6366F1' : '#E2E8F0',
          color: (isGradient || isGradientStr) && !useBrand ? '#6366F1' : '#475569',
        }}
      >
        <span
          className="w-5 h-5 rounded-md border border-black/10"
          style={{
            background: (isGradient || isGradientStr) && !useBrand
              ? currentCSS
              : 'linear-gradient(135deg, #6366F1, #EC4899, #F59E0B)',
          }}
        />
        Gradient
        {(isGradient || isGradientStr) && !useBrand && <span className="text-sm">✓</span>}
      </button>

      <GradientPopover
        anchorRef={gradAnchorRef}
        open={gradOpen}
        onClose={() => setGradOpen(false)}
        value={currentGradient}
        onChange={g => onChange(g)}
        title="Gradient tła"
      />

      {/* Custom hex */}
      <div className="relative flex-shrink-0">
        <button
          onClick={() => { setCustomOpen(o => !o); setGradOpen(false); }}
          title="Własny kolor"
          className="w-8 h-8 rounded-lg border-2 cursor-pointer relative"
          style={{
            background: !isPreset && !useBrand && !isGradient && !isGradientStr ? currentCSS : 'conic-gradient(from 0deg, #F59E0B, #EC4899, #6366F1, #06B6D4, #10B981, #F59E0B)',
            borderColor: '#fff',
            boxShadow: !isPreset && !useBrand && !isGradient && !isGradientStr ? '0 0 0 2px #6366F1' : '0 0 0 1px #E2E8F0',
          }}
        >
          {(!isPreset && !useBrand && !isGradient && !isGradientStr) ? (
            <span className="absolute inset-0 grid place-items-center text-sm font-bold"
              style={{ color: isDark(hexValue) ? '#fff' : '#0F172A' }}>✓</span>
          ) : (
            <span className="absolute inset-0 grid place-items-center text-sm font-bold text-white"
              style={{ textShadow: '0 1px 2px rgba(0,0,0,.4)' }}>+</span>
          )}
        </button>
        {customOpen && (
          <div
            className="absolute top-full right-0 mt-1.5 z-10 bg-white rounded-xl shadow-xl border border-gray-200 p-3 space-y-2 min-w-[180px]"
            onMouseLeave={() => setTimeout(() => setCustomOpen(false), 150)}
          >
            <div className="text-xs font-semibold text-gray-500">Własny kolor</div>
            <input
              type="color"
              value={hexValue}
              onChange={e => onChange(e.target.value)}
              className="w-full h-10 border border-gray-200 rounded-lg cursor-pointer bg-transparent"
            />
            <input
              type="text"
              value={hexValue.toUpperCase()}
              onChange={e => { const v = e.target.value; if (/^#[0-9A-Fa-f]{0,6}$/.test(v)) onChange(v); }}
              className="w-full h-7 px-2.5 border border-gray-200 rounded-md font-mono text-xs outline-none focus:border-indigo-400"
            />
          </div>
        )}
      </div>
    </div>
  );
}
