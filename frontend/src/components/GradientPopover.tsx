import { useLayoutEffect, useEffect, useState, type RefObject } from 'react';
import { createPortal } from 'react-dom';
import type { Gradient } from '@/types/lab';
import { GRADIENT_PRESETS, GRADIENT_ANGLES } from '@/types/lab';

const COLOR_PALETTE = [
  '#6366F1','#8B5CF6','#EC4899','#F59E0B','#EF4444',
  '#10B981','#06B6D4','#0EA5E9','#0F172A','#FFFFFF','#F1F5F9','#FEF3C7',
];

interface Props {
  anchorRef: RefObject<HTMLElement | null>;
  open: boolean;
  onClose: () => void;
  value: Gradient;
  onChange: (g: Gradient) => void;
  title?: string;
}

function ColorSwatch({ value, onChange }: { value: string; onChange: (c: string) => void }) {
  const [hexOpen, setHexOpen] = useState(false);
  return (
    <div className="relative">
      {/* palette swatches + custom */}
      <div className="flex gap-1 flex-wrap items-center">
        {COLOR_PALETTE.map(c => (
          <button
            key={c}
            onClick={() => onChange(c)}
            title={c}
            className="w-6 h-6 rounded-md border-2 cursor-pointer transition-transform hover:scale-110"
            style={{
              background: c,
              borderColor: value.toLowerCase() === c.toLowerCase() ? '#0F172A' : '#E2E8F0',
            }}
          />
        ))}
        <button
          onClick={() => setHexOpen(o => !o)}
          title="Własny kolor"
          className="w-6 h-6 rounded-md border border-gray-200 cursor-pointer grid place-items-center"
          style={{ background: 'conic-gradient(from 0deg, #F59E0B, #EC4899, #6366F1, #06B6D4, #10B981, #F59E0B)' }}
        >
          <span className="text-white text-xs font-bold" style={{ textShadow: '0 1px 1px rgba(0,0,0,.4)' }}>+</span>
        </button>
      </div>
      {hexOpen && (
        <div className="absolute top-full left-0 mt-1 z-20 bg-white rounded-lg shadow-lg border border-gray-200 p-2 flex flex-col gap-1"
          onMouseLeave={() => setTimeout(() => setHexOpen(false), 120)}>
          <input type="color" value={value} onChange={e => onChange(e.target.value)}
            className="w-20 h-8 cursor-pointer border-none bg-transparent" />
          <input type="text" value={value.toUpperCase()}
            onChange={e => { if (/^#[0-9A-Fa-f]{0,6}$/.test(e.target.value)) onChange(e.target.value); }}
            className="w-20 h-6 px-2 border border-gray-200 rounded font-mono text-xs outline-none" />
        </div>
      )}
    </div>
  );
}

export function GradientPopover({ anchorRef, open, onClose, value, onChange, title = 'Gradient' }: Props) {
  const [pos, setPos] = useState<{ left: number; top: number; maxH: number } | null>(null);
  const [stage, setStage] = useState<Gradient>(value);

  useLayoutEffect(() => {
    if (!open || !anchorRef.current) return;
    const compute = () => {
      if (!anchorRef.current) return;
      const rect = anchorRef.current.getBoundingClientRect();
      const W = 292;
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const margin = 12;
      let left = rect.right - W;
      if (left < margin) left = margin;
      if (left + W > vw - margin) left = vw - margin - W;
      let top = rect.bottom + 6;
      const approxH = Math.min(540, vh - 2 * margin);
      if (top + approxH > vh - margin) {
        const above = rect.top - 6 - approxH;
        top = above > margin ? above : margin;
      }
      const maxH = Math.min(560, vh - top - margin);
      setPos({ left, top, maxH });
    };
    compute();
    window.addEventListener('scroll', compute, true);
    window.addEventListener('resize', compute);
    return () => {
      window.removeEventListener('scroll', compute, true);
      window.removeEventListener('resize', compute);
    };
  }, [open, anchorRef]);

  useEffect(() => {
    if (open) setStage(value);
  }, [open, value]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    const onDown = (e: MouseEvent) => {
      if (!anchorRef.current) return;
      if (anchorRef.current.contains(e.target as Node)) return;
      const t = e.target as Element;
      if (t.closest?.('[data-gradient-popover="1"]')) return;
      onClose();
    };
    window.addEventListener('keydown', onKey);
    window.addEventListener('mousedown', onDown);
    return () => {
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('mousedown', onDown);
    };
  }, [open, onClose, anchorRef]);

  if (!open || !pos) return null;

  const previewBg = `linear-gradient(${stage.angle}, ${stage.c1}, ${stage.c2})`;

  return createPortal(
    <div
      data-gradient-popover="1"
      className="fixed z-[2000] bg-white border border-gray-200 rounded-xl shadow-xl flex flex-col"
      style={{ left: pos.left, top: pos.top, width: 292, maxHeight: pos.maxH }}
    >
      {/* Header */}
      <div className="flex items-center px-3 pt-2.5 pb-1">
        <span className="text-sm font-bold text-slate-800">{title}</span>
        <button onClick={onClose} className="ml-auto w-5 h-5 flex items-center justify-center text-gray-400 hover:text-gray-600 text-sm">✕</button>
      </div>

      <div className="px-3 pb-3 overflow-y-auto flex-1 space-y-3">
        {/* Preview */}
        <div className="h-11 rounded-lg border border-gray-200" style={{ background: previewBg }} />

        {/* Presets */}
        <div>
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide mb-1.5">Presety</div>
          <div className="grid grid-cols-8 gap-1">
            {GRADIENT_PRESETS.map((p, i) => {
              const bg = `linear-gradient(135deg, ${p.c1}, ${p.c2})`;
              const active = stage.c1 === p.c1 && stage.c2 === p.c2;
              return (
                <button
                  key={i}
                  onClick={() => setStage(s => ({ ...s, c1: p.c1, c2: p.c2 }))}
                  title={p.label}
                  className="h-5 rounded cursor-pointer p-0"
                  style={{
                    background: bg,
                    border: active ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  }}
                />
              );
            })}
          </div>
        </div>

        {/* Color 1 */}
        <div>
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide mb-1.5">Kolor 1</div>
          <ColorSwatch value={stage.c1} onChange={c => setStage(s => ({ ...s, c1: c }))} />
        </div>

        {/* Color 2 */}
        <div>
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide mb-1.5">Kolor 2</div>
          <ColorSwatch value={stage.c2} onChange={c => setStage(s => ({ ...s, c2: c }))} />
        </div>

        {/* Direction */}
        <div>
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wide mb-1.5">Kierunek</div>
          <div className="grid grid-cols-8 gap-1">
            {GRADIENT_ANGLES.map(a => (
              <button
                key={a.value}
                onClick={() => setStage(s => ({ ...s, angle: a.value }))}
                className="h-6 rounded text-sm font-bold cursor-pointer"
                style={{
                  background: '#fff',
                  border: stage.angle === a.value ? '2px solid #0F172A' : '1px solid #E2E8F0',
                }}
              >
                {a.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="flex gap-2 px-3 py-2.5 border-t border-gray-100">
        <button onClick={onClose} className="flex-1 h-8 border border-gray-200 bg-white rounded-lg text-sm font-semibold text-gray-500 hover:bg-gray-50 cursor-pointer">
          Anuluj
        </button>
        <button
          onClick={() => { onChange(stage); onClose(); }}
          className="flex-1 h-8 border-none rounded-lg text-sm font-semibold text-white cursor-pointer"
          style={{ background: 'linear-gradient(135deg, #6366F1, #EC4899)' }}
        >
          Zapisz
        </button>
      </div>
    </div>,
    document.body,
  );
}
