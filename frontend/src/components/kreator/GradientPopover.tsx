// GradientPopover — adaptacja z makiety card.jsx
// Floating popover do edycji gradientu (portal + fixed + clamp do viewportu)

import React from 'react';
import ReactDOM from 'react-dom';

export interface GradStage {
  angle: string;
  c1: string;
  c2: string;
}

interface GradientPopoverProps {
  anchorRef: React.RefObject<HTMLElement>;
  open: boolean;
  onClose: () => void;
  title: string;
  stage: GradStage;
  setStage: React.Dispatch<React.SetStateAction<GradStage>>;
  onSave: () => void;
  presets: GradStage[];
  angles: { deg: string; icon: string }[];
  palette: string[];
}

export function GradientPopover({ anchorRef, open, onClose, title, stage, setStage, onSave, presets, angles, palette }: GradientPopoverProps) {
  const [pos, setPos] = React.useState<{left: number; top: number; maxH: number} | null>(null);
  React.useLayoutEffect(() => {
    if (!open || !anchorRef.current) return;
    const compute = () => {
      const rect = anchorRef.current!.getBoundingClientRect();
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
    const onScroll = () => compute();
    window.addEventListener('scroll', onScroll, true);
    window.addEventListener('resize', compute);
    return () => {
      window.removeEventListener('scroll', onScroll, true);
      window.removeEventListener('resize', compute);
    };
  }, [open, anchorRef]);

  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    const onDown = (e: MouseEvent) => {
      if (!anchorRef.current) return;
      if (anchorRef.current.contains(e.target as Node)) return;
      if ((e.target as HTMLElement).closest && (e.target as HTMLElement).closest('[data-gradient-popover="1"]')) return;
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

  return ReactDOM.createPortal(
    <div data-gradient-popover="1" style={{
      position: 'fixed', left: pos.left, top: pos.top, width: 292, maxHeight: pos.maxH,
      background: '#fff', border: '1px solid #E2E8F0', borderRadius: 12,
      boxShadow: '0 8px 24px rgba(15,23,42,.12)', zIndex: 2000,
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', padding: '10px 12px 4px' }}>
        <div style={{ fontSize: 12, color: '#0F172A', fontWeight: 700 }}>{title}</div>
        <button onClick={onClose} style={{ marginLeft: 'auto', width: 22, height: 22, border: 'none', background: 'transparent', cursor: 'pointer', color: '#94A3B8' }}>x</button>
      </div>
      <div style={{ padding: '6px 12px 12px', overflowY: 'auto', flex: 1 }}>
        {/* Preview */}
        <div style={{ height: 44, borderRadius: 8, background: `linear-gradient(${stage.angle}, ${stage.c1}, ${stage.c2})`, border: '1px solid #E2E8F0', marginBottom: 10 }}/>
        {/* Presety */}
        <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 5 }}>Presety</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 4, marginBottom: 10 }}>
          {presets.map((p, i) => (
            <button key={i} onClick={() => setStage(p)} title={`${p.c1} → ${p.c2}`}
              style={{
                height: 22, borderRadius: 5,
                background: `linear-gradient(${p.angle}, ${p.c1}, ${p.c2})`,
                border: (stage.c1 === p.c1 && stage.c2 === p.c2 && stage.angle === p.angle) ? '2px solid #0F172A' : '1px solid #E2E8F0',
                cursor: 'pointer', padding: 0,
              }}/>
          ))}
        </div>
        <GradColorRow label="Kolor 1" value={stage.c1} palette={palette} onChange={(c: string) => setStage(s => ({ ...s, c1: c }))}/>
        <GradColorRow label="Kolor 2" value={stage.c2} palette={palette} onChange={(c: string) => setStage(s => ({ ...s, c2: c }))}/>
        <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 5, marginTop: 10 }}>Kierunek</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 3 }}>
          {angles.map(a => (
            <button key={a.deg} onClick={() => setStage(s => ({ ...s, angle: a.deg }))}
              style={{
                height: 24, borderRadius: 5, cursor: 'pointer',
                border: stage.angle === a.deg ? '2px solid #0F172A' : '1px solid #E2E8F0',
                background: '#fff', fontSize: 12, fontWeight: 700, fontFamily: 'inherit',
              }}>{a.icon}</button>
          ))}
        </div>
      </div>
      <div style={{ display: 'flex', gap: 6, padding: '10px 12px', borderTop: '1px solid #E2E8F0' }}>
        <button onClick={onClose} style={{ flex: 1, height: 32, border: '1px solid #E2E8F0', background: '#fff', borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit', fontSize: 12.5, fontWeight: 600, color: '#64748B' }}>Anuluj</button>
        <button onClick={onSave} style={{ flex: 1, height: 32, border: 'none', background: '#6366F1', color: '#fff', borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit', fontSize: 12.5, fontWeight: 600 }}>Zapisz</button>
      </div>
    </div>,
    document.body,
  );
}

function GradColorRow({ label, value, palette, onChange }: { label: string; value: string; palette: string[]; onChange: (c: string) => void }) {
  const [customOpen, setCustomOpen] = React.useState(false);
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 5 }}>{label}</div>
      <div style={{ display: 'flex', gap: 4, alignItems: 'center', flexWrap: 'wrap' }}>
        {palette.map(c => {
          const active = c.toLowerCase() === (value || '').toLowerCase();
          return (
            <button key={c} onClick={() => onChange(c)} title={c}
              style={{
                width: 22, height: 22, borderRadius: 6,
                background: c, border: active ? '2px solid #0F172A' : '1px solid #E2E8F0',
                cursor: 'pointer', padding: 0,
              }}/>
          );
        })}
        <div style={{ position: 'relative' }}>
          <button onClick={() => setCustomOpen(o => !o)} title="Wlasny kolor"
            style={{
              width: 22, height: 22, borderRadius: 6,
              background: 'conic-gradient(from 0deg, #F59E0B, #EC4899, #6366F1, #06B6D4, #10B981, #F59E0B)',
              border: '1px solid #E2E8F0', cursor: 'pointer', padding: 0,
              display: 'grid', placeItems: 'center',
            }}>
            <span style={{ color: '#fff', fontSize: 11, fontWeight: 700, textShadow: '0 1px 1px rgba(0,0,0,.3)' }}>+</span>
          </button>
          {customOpen && (
            <div style={{ position: 'absolute', top: 'calc(100% + 4px)', left: 0, zIndex: 20, background: '#fff', padding: 8, borderRadius: 8, boxShadow: '0 8px 24px rgba(15,23,42,.12)', border: '1px solid #E2E8F0' }}
              onMouseLeave={() => setTimeout(() => setCustomOpen(false), 150)}>
              <input type="color" value={value} onChange={e => onChange(e.target.value)} style={{ width: 80, height: 32, border: 'none', cursor: 'pointer', background: 'none' }}/>
              <input type="text" value={value.toUpperCase()} onChange={e => { if (/^#[0-9A-Fa-f]{0,6}$/.test(e.target.value)) onChange(e.target.value); }}
                style={{ width: 80, marginTop: 6, height: 26, padding: '0 8px', border: '1px solid #E2E8F0', borderRadius: 5, fontFamily: 'ui-monospace, monospace', fontSize: 11, outline: 'none' }}/>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Trigger dla popupu Gradientu
export function GradTrigger({ active, current, onClick, title, onPopover }: {
  active: boolean;
  current: string;
  onClick: () => void;
  title: string;
  onPopover: (ref: React.RefObject<HTMLButtonElement>) => React.ReactNode;
}) {
  const ref = React.useRef<HTMLButtonElement>(null);
  return (
    <div style={{ position: 'relative' }}>
      <button
        ref={ref}
        onClick={onClick}
        title={title}
        style={{
          height: 30, padding: '0 8px 0 4px', borderRadius: 9,
          display: 'inline-flex', alignItems: 'center', gap: 6,
          background: '#fff',
          border: active ? '2px solid #6366F1' : '1px solid #E2E8F0',
          cursor: 'pointer',
          fontFamily: 'inherit', fontSize: 11, fontWeight: 600,
          color: active ? '#6366F1' : '#475569',
        }}
      >
        <span style={{
          width: 22, height: 22, borderRadius: 6,
          background: active ? current : 'linear-gradient(135deg, #6366F1, #EC4899, #F59E0B)',
          border: '1px solid rgba(0,0,0,.08)',
        }}/>
        Gradient
        {active && <span style={{ fontSize: 12, lineHeight: 1 }}>+</span>}
      </button>
      {onPopover(ref)}
    </div>
  );
}
