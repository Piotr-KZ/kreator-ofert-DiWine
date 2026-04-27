// SectionCard — adaptacja z makiety card.jsx
// Karta sekcji: lewo duzy podglad klocka, prawo panel konfiguracji
// Adaptacja: section.code → section.block_code, var(--*) → literaly

import React from 'react';
import { BLOCK_LIBRARY, CATEGORIES } from '@/config/blocks';
import { ColorPicker, CtaPicker } from './ColorPicker';
import BlockPreview from './BlockPreviews';
import type { Section } from '@/store/labStore';
import type { Brand } from '@/config/blocks';

interface SectionCardProps {
  section: Section;
  index: number;
  total: number;
  brand: Brand;
  onUpdate: (patch: Record<string, unknown>) => void;
  onMove: (dir: number) => void;
  onDelete: () => void;
  onDuplicate: () => void;
  onAI: () => void;
  onOpenVariants: () => void;
}

export default function SectionCard({ section, index, total, brand, onUpdate, onMove, onDelete, onDuplicate, onAI, onOpenVariants }: SectionCardProps) {
  const block = BLOCK_LIBRARY.find(b => b.code === section.block_code);
  const cat = block ? CATEGORIES[block.cat] : null;
  const [hover, setHover] = React.useState(false);

  const sectionBg = (section.slots_json?.bg as string) || null;
  const sectionCta = (section.slots_json?.cta as string) || null;
  const sectionLabel = (section.slots_json?.label as string) || block?.name || section.block_code;

  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        background: '#fff',
        borderRadius: 16,
        boxShadow: hover ? '0 8px 24px rgba(15,23,42,.12)' : '0 1px 3px rgba(15,23,42,.06)',
        border: '1px solid #E2E8F0',
        transition: 'box-shadow .2s, transform .15s',
        transform: hover ? 'translateY(-1px)' : 'none',
        overflow: 'hidden',
      }}
    >
      {/* Header strip */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '10px 14px',
        borderBottom: '1px solid #E2E8F0',
        background: 'linear-gradient(180deg, #FAFBFC, #F5F6FA)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'grab', padding: 2, color: '#94A3B8' }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="6" r="1.5"/><circle cx="15" cy="6" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="18" r="1.5"/><circle cx="15" cy="18" r="1.5"/></svg>
        </div>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 5,
          padding: '3px 8px', borderRadius: 7,
          background: cat ? `${cat.color}15` : '#F1F5F9', color: cat?.color || '#64748B',
          fontSize: 11, fontWeight: 700, fontFamily: 'ui-monospace, monospace', letterSpacing: 0.3,
        }}>
          {cat && <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d={cat.icon}/></svg>}
          {section.block_code}
        </div>
        <div style={{ fontSize: 11, color: '#94A3B8', fontWeight: 500, letterSpacing: 0.3, textTransform: 'uppercase' }}>
          Sekcja {String(index + 1).padStart(2, '0')} / {total}
        </div>
        <div style={{ flex: 1 }} />
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: 4,
          height: 22, padding: '0 8px', borderRadius: 11,
          background: '#DCFCE7', color: '#047857',
          fontSize: 10.5, fontWeight: 600,
        }}>
          <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#10B981' }}></span>
          Skonfigurowany
        </span>
      </div>

      {/* Body: preview + config */}
      <div style={{ display: 'grid', gridTemplateColumns: '2.2fr 1fr', gap: 0, minHeight: 300 }}>
        {/* PREVIEW (left) — graficzny podgląd klocka z BlockPreviews */}
        <div style={{ padding: 14, borderRight: '1px solid #E2E8F0', background: '#F8FAFC', position: 'relative', display: 'flex' }}>
          <div style={{ flex: 1, boxShadow: '0 2px 8px rgba(15,23,42,.06)', borderRadius: 12, overflow: 'hidden' }}>
            <BlockPreview
              code={section.block_code}
              bg={sectionBg || (brand.bgGradient ? `linear-gradient(135deg, ${brand.bg}, ${brand.bg2})` : brand.bg)}
              brand={{ cta: brand.cta, ctaSecondary: brand.cta2 || '#EC4899' }}
            />
          </div>
          <div style={{ position: 'absolute', bottom: 24, left: 28, display: 'flex', gap: 5, fontSize: 10, color: '#64748B', fontFamily: 'ui-monospace, monospace', background: 'rgba(255,255,255,.9)', padding: '3px 7px', borderRadius: 5, border: '1px solid #E2E8F0' }}>
            rozmiar: {block?.size || '?'}
          </div>
        </div>

        {/* CONFIG (right) */}
        <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <ConfigField label="Nazwa sekcji">
            <input
              value={sectionLabel}
              onChange={e => onUpdate({ slots_json: { ...(section.slots_json || {}), label: e.target.value } })}
              style={{
                width: '100%', height: 34, padding: '0 10px',
                border: '1px solid #E2E8F0', borderRadius: 8,
                background: '#fff', fontFamily: 'inherit', fontSize: 13,
                outline: 'none', transition: 'border-color .15s',
              }}
              onFocus={e => (e.target.style.borderColor = '#6366F1')}
              onBlur={e => (e.target.style.borderColor = '#E2E8F0')}
            />
          </ConfigField>

          <ConfigField label="Rodzaj klocka">
            <button onClick={onOpenVariants} style={{
              width: '100%', height: 34, padding: '0 10px',
              border: '1px solid #E2E8F0', borderRadius: 8, background: '#fff',
              display: 'flex', alignItems: 'center', gap: 8,
              cursor: 'pointer', fontFamily: 'inherit', fontSize: 13,
              transition: 'all .15s',
            }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366F1'; e.currentTarget.style.background = '#FAFBFC'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.background = '#fff'; }}>
              <span style={{
                fontFamily: 'ui-monospace, monospace', fontSize: 10, fontWeight: 700,
                background: cat ? `${cat.color}15` : '#F1F5F9', color: cat?.color || '#64748B',
                padding: '2px 6px', borderRadius: 4,
              }}>{section.block_code}</span>
              <span style={{ flex: 1, textAlign: 'left', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{block?.name || section.block_code}</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
            </button>
          </ConfigField>

          <ConfigField label="Kolor tla sekcji">
            <ColorPicker
              value={sectionBg}
              brandValue={brand.bgGradient ? `linear-gradient(135deg, ${brand.bg}, ${brand.bg2})` : brand.bg}
              palette={['#FFFFFF', '#F8FAFC', '#FEF7ED', '#FEF3C7', '#ECFDF5', '#EEF2FF', '#FCE7F3', '#0F172A']}
              onChange={bg => onUpdate({ slots_json: { ...(section.slots_json || {}), bg } })}
            />
          </ConfigField>

          <ConfigField label={<span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>Kolor CTA <span style={{ fontSize: 9, fontWeight: 500, color: '#94A3B8', textTransform: 'none', letterSpacing: 0 }}>(opcjonalnie)</span></span>}>
            <CtaPicker value={sectionCta} brandCta={brand.cta} onChange={cta => onUpdate({ slots_json: { ...(section.slots_json || {}), cta } })} />
          </ConfigField>

          <div style={{ flex: 1 }} />

          {/* Action row */}
          <div style={{ display: 'flex', gap: 6, paddingTop: 10, borderTop: '1px solid #E2E8F0' }}>
            <IconBtn onClick={() => onMove(-1)} disabled={index === 0} title="Przenies wyzej">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 15l-6-6-6 6"/></svg>
            </IconBtn>
            <IconBtn onClick={() => onMove(1)} disabled={index === total - 1} title="Przenies nizej">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M6 9l6 6 6-6"/></svg>
            </IconBtn>
            <IconBtn onClick={onDuplicate} title="Duplikuj">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
            </IconBtn>
            <IconBtn onClick={onDelete} title="Usun" danger>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
            </IconBtn>
            <div style={{ flex: 1 }} />
            <button onClick={onAI} title="Zapytaj AI o te sekcje" style={{
              display: 'inline-flex', alignItems: 'center', gap: 5,
              padding: '0 12px', height: 30, border: 'none', borderRadius: 8,
              background: 'linear-gradient(135deg, #6366F1, #EC4899)',
              color: '#fff', fontFamily: 'inherit', fontSize: 12, fontWeight: 600,
              cursor: 'pointer', boxShadow: '0 2px 6px rgba(99,102,241,.25)',
            }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
              AI
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ConfigField({ label, children }: { label: React.ReactNode; children: React.ReactNode }) {
  return (
    <label style={{ display: 'block' }}>
      <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 5 }}>{label}</div>
      {children}
    </label>
  );
}

function IconBtn({ onClick, disabled, title, danger, children }: {
  onClick: () => void; disabled?: boolean; title: string; danger?: boolean; children: React.ReactNode;
}) {
  return (
    <button onClick={onClick} disabled={disabled} title={title} style={{
      width: 30, height: 30, border: '1px solid #E2E8F0',
      background: '#fff', borderRadius: 8,
      display: 'grid', placeItems: 'center',
      color: danger ? '#EF4444' : '#64748B',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.4 : 1,
      transition: 'all .12s',
    }}
      onMouseEnter={e => { if (!disabled) { e.currentTarget.style.background = danger ? '#FEE2E2' : '#F1F5F9'; e.currentTarget.style.borderColor = danger ? '#FCA5A5' : '#CBD5E1'; } }}
      onMouseLeave={e => { if (!disabled) { e.currentTarget.style.background = '#fff'; e.currentTarget.style.borderColor = '#E2E8F0'; } }}
    >
      {children}
    </button>
  );
}
