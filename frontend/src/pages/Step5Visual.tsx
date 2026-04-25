/**
 * Step 5 — Kreacja wizualna (Krok 5 z 6)
 * Gotowa strona 1:1 z pełną edycją: tekst (inline), tło sekcji (picker),
 * globalne style (TweakPanel), AI asystent.
 */

import { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore, type Section } from "@/store/labStore";
import * as api from "@/api/client";
import {
  makeTypo, isDark,
  getRenderer, PlaceholderSection,
} from "@/components/SectionRenderers";
import ElementToolbar from "@/components/ElementToolbar";

// ─── Stałe ─────────────────────────────────────────────────────────────────────

const BRAND_COLORS = ['#0F766E','#065F46','#7C3AED','#6366F1','#EC4899','#DC2626','#F59E0B','#0F172A'];

const SECTION_BG_PALETTE = [
  '#FFFFFF','#F8FAFC','#F1F5F9','#FEF7ED',
  '#EEF2FF','#EEF6F4','#FEF3C7','#FDF2F8',
  '#0F172A','#1E293B',
];

const FONT_PAIRS: Record<string, { h: string; b: string }> = {
  'Fraunces + Inter':           { h: 'Fraunces',           b: 'Inter'   },
  'Instrument Serif + Inter':   { h: 'Instrument Serif',   b: 'Inter'   },
  'Playfair Display + Inter':   { h: 'Playfair Display',   b: 'Inter'   },
  'DM Serif Display + Manrope': { h: 'DM Serif Display',   b: 'Manrope' },
  'Space Grotesk + Inter':      { h: 'Space Grotesk',      b: 'Inter'   },
  'Cormorant + Inter':          { h: 'Cormorant Garamond', b: 'Inter'   },
};

const DENSITY_LEVELS: Record<string, number> = { compact: 2, normal: 3, spacious: 4 };

// ─── Helpery ───────────────────────────────────────────────────────────────────

function getFontPairKey(h: string, b: string): string {
  for (const [k, p] of Object.entries(FONT_PAIRS)) {
    if (p.h === h && p.b === b) return k;
  }
  for (const [k, p] of Object.entries(FONT_PAIRS)) {
    if (p.h === h) return k;
  }
  return 'Instrument Serif + Inter';
}

/** Zwraca kolor tła sekcji: najpierw VC, potem section.bgColor, potem biały */
function resolveBg(
  section: Section,
  idx: number,
  vcSections: Array<{ block_code: string; bg_value: string }> | undefined,
): string {
  if (section.bgColor && typeof section.bgColor === 'string') return section.bgColor;
  const vc = vcSections?.[idx];
  if (vc?.bg_value && typeof vc.bg_value === 'string') return vc.bg_value;
  return '#FFFFFF';
}

// ─── useToast ──────────────────────────────────────────────────────────────────

function useToast() {
  const [msg, setMsg] = useState<string | null>(null);
  const t = useRef<ReturnType<typeof setTimeout> | null>(null);
  const show = useCallback((text: string) => {
    setMsg(text);
    if (t.current) clearTimeout(t.current);
    t.current = setTimeout(() => setMsg(null), 2200);
  }, []);
  return { toast: msg, show };
}

// ─── TweakPanel ────────────────────────────────────────────────────────────────

function TweakRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: 0.4, marginBottom: 8 }}>{label}</div>
      {children}
    </div>
  );
}

interface TweakPanelProps {
  brandColor: string; accentColor: string; fontPairKey: string; density: string;
  onBrandColor: (c: string) => void; onAccentColor: (c: string) => void;
  onFontPair: (k: string) => void; onDensity: (d: string) => void;
}

function TweakPanel({ brandColor, accentColor, fontPairKey, density, onBrandColor, onAccentColor, onFontPair, onDensity }: TweakPanelProps) {
  return (
    <div style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div style={{ fontSize: 15, fontWeight: 700, color: '#0F172A', marginBottom: 3 }}>Tweaki</div>
      <div style={{ fontSize: 12, color: '#64748B', marginBottom: 20 }}>Globalne style strony</div>

      <TweakRow label="Kolor brandu">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 4 }}>
          {BRAND_COLORS.map(c => (
            <button key={c} onClick={() => onBrandColor(c)} style={{
              aspectRatio: '1', borderRadius: 6, background: c, cursor: 'pointer', padding: 0,
              border: brandColor === c ? '2.5px solid #0F172A' : '1.5px solid #E2E8F0',
            }} />
          ))}
        </div>
      </TweakRow>

      <TweakRow label="Kolor akcentu">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 4 }}>
          {BRAND_COLORS.map(c => (
            <button key={c} onClick={() => onAccentColor(c)} style={{
              aspectRatio: '1', borderRadius: 6, background: c, cursor: 'pointer', padding: 0,
              border: accentColor === c ? '2.5px solid #0F172A' : '1.5px solid #E2E8F0',
            }} />
          ))}
        </div>
      </TweakRow>

      <TweakRow label="Typografia">
        <div style={{ display: 'grid', gap: 5 }}>
          {Object.entries(FONT_PAIRS).map(([key, pair]) => {
            const active = fontPairKey === key;
            return (
              <button key={key} onClick={() => onFontPair(key)} style={{
                padding: '9px 11px', border: active ? '1.5px solid #6366F1' : '1px solid #E2E8F0',
                background: active ? '#EEF2FF' : '#fff', borderRadius: 8, cursor: 'pointer',
                textAlign: 'left', display: 'flex', alignItems: 'center', gap: 10, fontFamily: 'inherit',
              }}>
                <span style={{ fontFamily: `'${pair.h}', serif`, fontSize: 18, fontWeight: 600, color: '#0F172A', lineHeight: 1 }}>Aa</span>
                <span style={{ fontFamily: `'${pair.b}', sans-serif`, fontSize: 11, color: '#64748B', flex: 1 }}>{key}</span>
                {active && <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>}
              </button>
            );
          })}
        </div>
      </TweakRow>

      <TweakRow label="Gęstość">
        <div style={{ display: 'inline-flex', background: '#F1F5F9', padding: 2, borderRadius: 7, width: '100%', gap: 1 }}>
          {[{ k: 'compact', l: 'Kompakt' }, { k: 'normal', l: 'Komfort' }, { k: 'spacious', l: 'Luźna' }].map(o => (
            <button key={o.k} onClick={() => onDensity(o.k)} style={{
              flex: 1, padding: '7px 4px', border: 'none', fontFamily: 'inherit', fontSize: 11.5, cursor: 'pointer',
              borderRadius: 5, fontWeight: density === o.k ? 600 : 500,
              background: density === o.k ? '#fff' : 'transparent',
              color: density === o.k ? '#0F172A' : '#64748B',
              boxShadow: density === o.k ? '0 1px 2px rgba(0,0,0,.06)' : 'none',
            }}>{o.l}</button>
          ))}
        </div>
      </TweakRow>
    </div>
  );
}

// ─── BgPickerPopup ─────────────────────────────────────────────────────────────

function BgPickerPopup({ current, brandColor, onPick, onClose }: {
  current: string; brandColor: string;
  onPick: (c: string) => void; onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) onClose(); };
    const t = setTimeout(() => document.addEventListener('mousedown', h), 0);
    return () => { clearTimeout(t); document.removeEventListener('mousedown', h); };
  }, [onClose]);

  const palette = [...new Set([brandColor, ...SECTION_BG_PALETTE])];

  return (
    <div ref={ref} style={{
      position: 'absolute', top: 'calc(100% + 6px)', right: 0, zIndex: 60,
      background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10,
      padding: 10, boxShadow: '0 8px 24px rgba(15,23,42,.15)',
      display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 5, width: 174,
    }}>
      {palette.map(c => (
        <button key={c} onMouseDown={e => { e.preventDefault(); onPick(c); onClose(); }} style={{
          aspectRatio: '1', borderRadius: 6, background: c, cursor: 'pointer', padding: 0,
          border: current === c ? '2.5px solid #6366F1' : isDark(c) ? '1.5px solid rgba(255,255,255,.2)' : '1.5px solid #E2E8F0',
          position: 'relative',
        }}>
          {current === c && (
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke={isDark(c) ? '#fff' : '#0F172A'} strokeWidth="3" strokeLinecap="round"
              style={{ position: 'absolute', inset: 0, margin: 'auto' }}>
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          )}
        </button>
      ))}
    </div>
  );
}

// ─── SectionActions ────────────────────────────────────────────────────────────

function Btn5({ children, onClick, title, disabled, danger }: {
  children: React.ReactNode; onClick?: () => void; title: string; disabled?: boolean; danger?: boolean;
}) {
  return (
    <button disabled={disabled} onClick={onClick} title={title}
      style={{ width: 30, height: 28, border: 'none', borderRadius: 6, background: 'transparent', cursor: disabled ? 'not-allowed' : 'pointer', display: 'grid', placeItems: 'center', color: disabled ? '#CBD5E1' : danger ? '#DC2626' : '#334155', fontFamily: 'inherit' }}
      onMouseEnter={e => { if (!disabled) (e.currentTarget as HTMLButtonElement).style.background = danger ? '#FEF2F2' : '#F1F5F9'; }}
      onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.background = 'transparent'; }}>
      {children}
    </button>
  );
}

interface SAProps {
  label: string; bgColor: string; brandColor: string;
  canUp: boolean; canDown: boolean;
  onUp: () => void; onDown: () => void; onDel: () => void; onRegen: () => void;
  onBgChange: (c: string) => void;
}

function SectionActions({ label, bgColor, brandColor, canUp, canDown, onUp, onDown, onDel, onRegen, onBgChange }: SAProps) {
  const [bgOpen, setBgOpen] = useState(false);
  return (
    <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 20 }}>
      <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6 }}>
        <div style={{ padding: '3px 9px', background: '#0F172A', color: '#fff', borderRadius: 6, fontSize: 10.5, fontWeight: 600, fontFamily: 'Inter, sans-serif', letterSpacing: 0.2 }}>
          {label}
        </div>
        <div style={{ display: 'inline-flex', gap: 1, padding: 3, background: '#fff', border: '1px solid rgba(15,23,42,.1)', borderRadius: 8, boxShadow: '0 4px 14px rgba(15,23,42,.12)', position: 'relative' }}>
          <Btn5 title="Przesuń w górę" disabled={!canUp} onClick={onUp}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 15l-6-6-6 6"/></svg>
          </Btn5>
          <Btn5 title="Przesuń w dół" disabled={!canDown} onClick={onDown}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M6 9l6 6 6-6"/></svg>
          </Btn5>
          <div style={{ width: 1, background: '#E2E8F0', margin: '2px 2px' }} />
          {/* Tło sekcji */}
          <div style={{ position: 'relative' }}>
            <Btn5 title="Kolor tła sekcji" onClick={() => setBgOpen(v => !v)}>
              <div style={{ width: 14, height: 14, borderRadius: 4, background: bgColor, border: '1.5px solid rgba(0,0,0,.15)' }} />
            </Btn5>
            {bgOpen && (
              <BgPickerPopup
                current={bgColor} brandColor={brandColor}
                onPick={onBgChange} onClose={() => setBgOpen(false)}
              />
            )}
          </div>
          <div style={{ width: 1, background: '#E2E8F0', margin: '2px 2px' }} />
          <Btn5 title="Regeneruj AI" onClick={onRegen}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
          </Btn5>
          <Btn5 title="Usuń sekcję" danger onClick={onDel}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/></svg>
          </Btn5>
        </div>
      </div>
    </div>
  );
}

// ─── RegenPanel ────────────────────────────────────────────────────────────────

function RegenPanel({ sectionId, onSubmit, onClose }: { sectionId: string; onSubmit: (i: string) => void; onClose: () => void }) {
  const [inst, setInst] = useState('');
  return (
    <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 80, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 16, boxShadow: '0 20px 48px rgba(15,23,42,.18)', padding: '20px 24px', width: 400, fontFamily: 'Inter, sans-serif' }}>
      <div style={{ fontSize: 14, fontWeight: 600, color: '#0F172A', marginBottom: 12 }}>Regeneruj sekcję</div>
      <input type="text" value={inst} onChange={e => setInst(e.target.value)} placeholder="Dodatkowa instrukcja (opcjonalnie)"
        style={{ width: '100%', padding: '8px 12px', border: '1px solid #E2E8F0', borderRadius: 8, fontSize: 13, fontFamily: 'inherit', outline: 'none', boxSizing: 'border-box', marginBottom: 12 }}
        onKeyDown={e => { if (e.key === 'Enter') { onSubmit(inst.trim()); onClose(); } if (e.key === 'Escape') onClose(); }}
        autoFocus />
      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button onClick={onClose} style={{ padding: '7px 14px', border: '1px solid #E2E8F0', background: 'transparent', borderRadius: 8, fontSize: 13, cursor: 'pointer', color: '#64748B', fontFamily: 'inherit' }}>Anuluj</button>
        <button onClick={() => { onSubmit(inst.trim()); onClose(); }} style={{ padding: '7px 16px', background: '#6366F1', color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>Regeneruj AI</button>
      </div>
    </div>
  );
}

// ─── AiChatPanel ──────────────────────────────────────────────────────────────

interface AIChatMsg { role: 'ai' | 'user'; text: string }

function AiChatPanel({ projectId, onClose }: { projectId: string; onClose: () => void }) {
  const [messages, setMessages] = useState<AIChatMsg[]>([
    { role: 'ai', text: 'Cześć! Widzę Twoją stronę. Mogę zmienić tekst, styl sekcji, kolory lub zaproponować ulepszenia. Co chcesz zrobić?' },
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || sending) return;
    setMessages(p => [...p, { role: 'user', text }]);
    setInput('');
    setSending(true);
    let aiText = '';
    setMessages(p => [...p, { role: 'ai', text: '…' }]);
    try {
      await api.chatStream(projectId, text, 5, chunk => {
        aiText += chunk;
        setMessages(p => { const n = [...p]; n[n.length - 1] = { role: 'ai', text: aiText }; return n; });
      });
    } catch {
      setMessages(p => { const n = [...p]; n[n.length - 1] = { role: 'ai', text: 'Błąd połączenia z AI.' }; return n; });
    } finally { setSending(false); }
  };

  const suggestions = ['Popraw nagłówek hero', 'Zmień styl na ciemny', 'Skróć opisy', 'Co poprawić?'];

  return (
    <div style={{ position: 'fixed', right: 24, bottom: 90, width: 380, height: 480, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 16, boxShadow: '0 20px 48px rgba(15,23,42,.18)', display: 'flex', flexDirection: 'column', zIndex: 70, fontFamily: 'Inter, sans-serif' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #F1F5F9', display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: 'linear-gradient(135deg, #6366F1, #EC4899)', display: 'grid', placeItems: 'center' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
        </div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600 }}>AI asystent</div>
          <div style={{ fontSize: 10.5, color: '#94A3B8' }}>Kreacja wizualna · Krok 5</div>
        </div>
        <button onClick={onClose} style={{ marginLeft: 'auto', width: 28, height: 28, border: 'none', background: 'transparent', cursor: 'pointer', borderRadius: 6, display: 'grid', placeItems: 'center', color: '#94A3B8', fontSize: 16, fontFamily: 'inherit' }}
          onMouseEnter={e => (e.currentTarget.style.background = '#F1F5F9')}
          onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>×</button>
      </div>
      <div ref={scrollRef} style={{ flex: 1, overflow: 'auto', padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ maxWidth: '85%', alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', padding: '9px 12px', background: m.role === 'user' ? 'linear-gradient(135deg, #6366F1, #EC4899)' : '#F1F5F9', color: m.role === 'user' ? '#fff' : '#0F172A', borderRadius: m.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px', fontSize: 13, lineHeight: 1.45 }}>{m.text}</div>
        ))}
      </div>
      <div style={{ padding: '8px 12px 0', display: 'flex', gap: 6, flexWrap: 'wrap', flexShrink: 0 }}>
        {suggestions.map(s => (
          <button key={s} onClick={() => { setInput(s); inputRef.current?.focus(); }}
            style={{ padding: '5px 10px', background: '#fff', border: '1px solid #E2E8F0', borderRadius: 999, fontSize: 11.5, color: '#475569', cursor: 'pointer', fontFamily: 'inherit', whiteSpace: 'nowrap' }}
            onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = '#6366F1'; (e.currentTarget as HTMLButtonElement).style.color = '#6366F1'; }}
            onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = '#E2E8F0'; (e.currentTarget as HTMLButtonElement).style.color = '#475569'; }}>{s}</button>
        ))}
      </div>
      <div style={{ padding: 12, borderTop: '1px solid #F1F5F9', marginTop: 8, flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, padding: '8px 10px', background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 12 }}>
          <textarea ref={inputRef} value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Co chcesz zmienić?" rows={1}
            style={{ flex: 1, border: 'none', background: 'transparent', outline: 'none', resize: 'none', fontSize: 13, fontFamily: 'inherit', color: '#0F172A', minHeight: 20, maxHeight: 80, lineHeight: 1.5 }} />
          <button onClick={send} disabled={!input.trim() || sending}
            style={{ width: 32, height: 32, background: input.trim() ? 'linear-gradient(135deg, #6366F1, #EC4899)' : '#E2E8F0', color: input.trim() ? '#fff' : '#94A3B8', border: 'none', borderRadius: 8, cursor: input.trim() ? 'pointer' : 'not-allowed', display: 'grid', placeItems: 'center', flexShrink: 0 }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function Step5Visual() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const {
    sections, brand, visualConcept,
    setBrand, saveBrief,
    updateSection, updateSectionMeta,
    regenerateSection, removeSection, reorderSections,
    isGenerating,
  } = useLabStore();

  const [hoveredSection, setHoveredSection] = useState<string | null>(null);
  const [regenPanel, setRegenPanel] = useState<string | null>(null);
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const { toast, show: showToast } = useToast();
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Derived values ──────────────────────────────────────────────────────────
  const fontPairKey = getFontPairKey(brand.fontHeading || 'Instrument Serif', brand.fontBody || 'Inter');
  const densityLevel = DENSITY_LEVELS[brand.density || 'normal'] ?? 3;
  const typo = makeTypo(densityLevel, brand.fontHeading || 'Instrument Serif', brand.fontBody || 'Inter');
  const vcSections = visualConcept?.sections;

  // ── Section slot update (saves to backend) ──────────────────────────────────
  const handleSlotUpdate = useCallback((sectionId: string, key: string, val: unknown) => {
    const sec = sections.find(s => s.id === sectionId);
    if (!sec?.slots_json) return;
    const updated = { ...(sec.slots_json as Record<string, unknown>), [key]: val };
    updateSection(sectionId, { slots_json: updated });
  }, [sections, updateSection]);

  // ── Section background change ───────────────────────────────────────────────
  const handleBgChange = useCallback(async (sectionId: string, color: string) => {
    await updateSectionMeta(sectionId, { bgColor: color });
    showToast('Tło zmienione');
  }, [updateSectionMeta, showToast]);

  // ── Section move ────────────────────────────────────────────────────────────
  const handleMove = useCallback(async (sectionId: string, dir: 'up' | 'down') => {
    const idx = sections.findIndex(s => s.id === sectionId);
    if (idx < 0) return;
    const target = dir === 'up' ? idx - 1 : idx + 1;
    if (target < 0 || target >= sections.length) return;
    const newOrder = [...sections];
    [newOrder[idx], newOrder[target]] = [newOrder[target], newOrder[idx]];
    await reorderSections(newOrder.map(s => s.id));
  }, [sections, reorderSections]);

  const handleDelete = useCallback(async (sectionId: string) => {
    if (!confirm('Usunąć tę sekcję?')) return;
    await removeSection(sectionId);
    showToast('Sekcja usunięta');
  }, [removeSection, showToast]);

  const handleRegen = useCallback(async (sectionId: string, instruction: string) => {
    await regenerateSection(sectionId, instruction || undefined);
    showToast('Sekcja zregenerowana');
  }, [regenerateSection, showToast]);

  // ── Debounced brand save ────────────────────────────────────────────────────
  const patchBrand = useCallback((patch: Parameters<typeof setBrand>[0]) => {
    setBrand(patch);
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => saveBrief().catch(() => {}), 800);
  }, [setBrand, saveBrief]);

  const handleFontPair = useCallback((key: string) => {
    const pair = FONT_PAIRS[key];
    if (pair) patchBrand({ fontHeading: pair.h, fontBody: pair.b });
  }, [patchBrand]);

  // ── Sorted sections ─────────────────────────────────────────────────────────
  const sorted = [...sections].sort((a, b) => (a.position ?? 0) - (b.position ?? 0));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 48px)', overflow: 'hidden', fontFamily: 'Inter, system-ui, sans-serif' }}>

      {/* ── Topbar ─────────────────────────────────────────────────────────── */}
      <div style={{ height: 52, borderBottom: '1px solid #F1F5F9', background: '#fff', display: 'flex', alignItems: 'center', padding: '0 20px', gap: 12, flexShrink: 0, zIndex: 40 }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: '#6366F1', textTransform: 'uppercase', letterSpacing: 0.8 }}>
          ● Krok 5 · Kreacja wizualna
        </div>
        <div style={{ fontSize: 12, color: '#94A3B8' }}>
          Kliknij tekst aby edytować · Najedź na sekcję aby zmienić tło lub kolejność
        </div>
        <div style={{ flex: 1 }} />
        {isGenerating && (
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#6366F1' }}>
            <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" strokeOpacity=".25"/><path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="4" strokeLinecap="round"/></svg>
            AI generuje…
          </div>
        )}
        <button onClick={() => saveBrief().then(() => showToast('Zapisano!'))}
          style={{ padding: '7px 16px', background: '#6366F1', color: '#fff', border: 'none', borderRadius: 8, fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
          Zapisz styl
        </button>
      </div>

      {/* ── Main area ──────────────────────────────────────────────────────── */}
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 300px', overflow: 'hidden' }}>

        {/* ── Canvas (1:1) ── */}
        <div style={{ overflow: 'auto', background: '#F5F6FA' }}>
          {sorted.length === 0 ? (
            <div style={{ padding: '80px 40px', textAlign: 'center', color: '#94A3B8', fontFamily: 'Inter, sans-serif' }}>
              <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>Brak sekcji</div>
              <div style={{ fontSize: 13 }}>Wróć do kroku 3 aby wygenerować strukturę strony.</div>
            </div>
          ) : (
            <div style={{ background: '#fff' }}>
              {sorted.map((section, idx) => {
                const effectiveBg = resolveBg(section, idx, vcSections);
                const augmented: Section = { ...section, bgColor: effectiveBg };
                const Renderer = section.slots_json ? getRenderer(section.block_code) : null;
                return (
                  <div key={section.id} style={{ position: 'relative' }}
                    onMouseEnter={() => setHoveredSection(section.id)}
                    onMouseLeave={() => setHoveredSection(p => p === section.id ? null : p)}>
                    {Renderer ? (
                      <Renderer
                        section={augmented}
                        brand={brand}
                        typo={typo}
                        onSlotUpdate={(key, val) => handleSlotUpdate(section.id, key, val)}
                      />
                    ) : (
                      <PlaceholderSection section={augmented} />
                    )}
                    {hoveredSection === section.id && (
                      <SectionActions
                        label={section.name || section.block_code}
                        bgColor={effectiveBg}
                        brandColor={brand.ctaColor as string}
                        canUp={idx > 0}
                        canDown={idx < sorted.length - 1}
                        onUp={() => handleMove(section.id, 'up')}
                        onDown={() => handleMove(section.id, 'down')}
                        onDel={() => handleDelete(section.id)}
                        onRegen={() => setRegenPanel(section.id)}
                        onBgChange={c => handleBgChange(section.id, c)}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* ── TweakPanel ── */}
        <div style={{ background: '#fff', borderLeft: '1px solid #E2E8F0', overflow: 'auto', padding: '20px 16px 40px' }}>
          <TweakPanel
            brandColor={brand.ctaColor as string}
            accentColor={brand.ctaColor2 as string}
            fontPairKey={fontPairKey}
            density={brand.density || 'normal'}
            onBrandColor={c => patchBrand({ ctaColor: c })}
            onAccentColor={c => patchBrand({ ctaColor2: c })}
            onFontPair={handleFontPair}
            onDensity={d => patchBrand({ density: d as 'compact' | 'normal' | 'spacious' })}
          />
        </div>
      </div>

      {/* ── Regen modal ─────────────────────────────────────────────────────── */}
      {regenPanel && (
        <>
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,.4)', zIndex: 75 }} onClick={() => setRegenPanel(null)} />
          <RegenPanel sectionId={regenPanel} onSubmit={inst => handleRegen(regenPanel, inst)} onClose={() => setRegenPanel(null)} />
        </>
      )}

      {/* ── AI FAB ──────────────────────────────────────────────────────────── */}
      {!aiChatOpen && (
        <button onClick={() => setAiChatOpen(true)}
          style={{ position: 'fixed', right: 24, bottom: 80, zIndex: 60, padding: '12px 18px', background: 'linear-gradient(135deg, #6366F1, #EC4899)', color: '#fff', border: 'none', borderRadius: 999, fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8, boxShadow: '0 12px 30px rgba(99,102,241,.35)', fontFamily: 'Inter, sans-serif' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
          AI asystent
        </button>
      )}

      {aiChatOpen && projectId && (
        <AiChatPanel projectId={projectId} onClose={() => setAiChatOpen(false)} />
      )}

      {/* ── ElementToolbar ──────────────────────────────────────────────────── */}
      <ElementToolbar />

      {/* ── Toast ───────────────────────────────────────────────────────────── */}
      {toast && (
        <div style={{ position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)', padding: '10px 18px', background: '#0F172A', color: '#fff', borderRadius: 10, fontSize: 13, fontWeight: 500, zIndex: 100, boxShadow: '0 8px 24px rgba(15,23,42,.3)', fontFamily: 'Inter, sans-serif' }}>{toast}</div>
      )}

      {/* ── Bottom nav ──────────────────────────────────────────────────────── */}
      <div style={{ background: '#fff', borderTop: '1px solid #F1F5F9', padding: '10px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0, zIndex: 30 }}>
        <button onClick={() => navigate(`/lab/${projectId}/step/4`)}
          style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #E2E8F0', borderRadius: 10, fontSize: 13, color: '#64748B', cursor: 'pointer', fontFamily: 'inherit' }}>
          ← Wstecz
        </button>
        <button onClick={() => { saveBrief(); navigate(`/lab/${projectId}/step/6`); }}
          style={{ padding: '9px 22px', background: '#6366F1', color: '#fff', border: 'none', borderRadius: 10, fontSize: 13, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
          Dalej → Eksport
        </button>
      </div>
    </div>
  );
}
