/**
 * Step 5 — Wizualizacja (Krok 5 z 6)
 * Odwzorowanie makiety wiz_app.jsx: podgląd strony z TweakPanel,
 * device switcher, Edit/Preview toggle, fullscreen overlay, AI FAB.
 */

import { useState, useRef, useLayoutEffect, useCallback, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";
import * as api from "@/api/client";
import {
  makeTypo,
  getRenderer, PlaceholderSection,
} from "@/components/SectionRenderers";
import ElementToolbar from "@/components/ElementToolbar";

// ─── Constants ─────────────────────────────────────────────────────────────────

const DEVICES = {
  desktop: { w: 1440, label: 'Desktop' },
  tablet:  { w: 820,  label: 'Tablet'  },
  mobile:  { w: 390,  label: 'Mobile'  },
} as const;

type Device = keyof typeof DEVICES;

const BRAND_COLORS = ['#0F766E', '#065F46', '#7C3AED', '#6366F1', '#EC4899', '#DC2626', '#F59E0B', '#0F172A'];

const FONT_PAIRS: Record<string, { h: string; b: string }> = {
  'Fraunces + Inter':           { h: 'Fraunces',          b: 'Inter'   },
  'Instrument Serif + Inter':   { h: 'Instrument Serif',  b: 'Inter'   },
  'Playfair Display + Inter':   { h: 'Playfair Display',  b: 'Inter'   },
  'DM Serif Display + Manrope': { h: 'DM Serif Display',  b: 'Manrope' },
  'Space Grotesk + Inter':      { h: 'Space Grotesk',     b: 'Inter'   },
  'Cormorant + Inter':          { h: 'Cormorant Garamond', b: 'Inter'  },
};

const DENSITY_LEVELS: Record<string, number> = { compact: 2, normal: 3, spacious: 4 };

// ─── Helper ────────────────────────────────────────────────────────────────────

function getFontPairKey(fontHeading: string, fontBody: string): string {
  for (const [key, pair] of Object.entries(FONT_PAIRS)) {
    if (pair.h === fontHeading && pair.b === fontBody) return key;
  }
  for (const [key, pair] of Object.entries(FONT_PAIRS)) {
    if (pair.h === fontHeading) return key;
  }
  return 'Instrument Serif + Inter';
}

// ─── useToast ──────────────────────────────────────────────────────────────────

function useToast() {
  const [msg, setMsg] = useState<string | null>(null);
  const tRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const show = useCallback((text: string) => {
    setMsg(text);
    if (tRef.current) clearTimeout(tRef.current);
    tRef.current = setTimeout(() => setMsg(null), 2200);
  }, []);
  return { toast: msg, show };
}

// ─── TweakRow ─────────────────────────────────────────────────────────────────

function TweakRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: 0.4, marginBottom: 8 }}>{label}</div>
      {children}
    </div>
  );
}

// ─── TweakPanel ───────────────────────────────────────────────────────────────

interface TweakPanelProps {
  brandColor: string;
  accentColor: string;
  fontPairKey: string;
  density: string;
  onBrandColor: (c: string) => void;
  onAccentColor: (c: string) => void;
  onFontPair: (key: string) => void;
  onDensity: (d: string) => void;
}

function TweakPanel({ brandColor, accentColor, fontPairKey, density, onBrandColor, onAccentColor, onFontPair, onDensity }: TweakPanelProps) {
  return (
    <div style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      <h3 style={{ margin: '0 0 3px', fontSize: 15, fontWeight: 600, color: '#0F172A' }}>Tweaki</h3>
      <p style={{ margin: '0 0 20px', fontSize: 12, color: '#64748B' }}>Dostrój globalne style całej strony</p>

      <TweakRow label="Kolor brandu">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 4 }}>
          {BRAND_COLORS.map(c => (
            <button key={c} onClick={() => onBrandColor(c)} style={{
              aspectRatio: '1', border: brandColor === c ? '2.5px solid #0F172A' : '1.5px solid #E2E8F0',
              borderRadius: 6, background: c, cursor: 'pointer', padding: 0,
            }} />
          ))}
        </div>
      </TweakRow>

      <TweakRow label="Kolor akcentu">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 4 }}>
          {BRAND_COLORS.map(c => (
            <button key={c} onClick={() => onAccentColor(c)} style={{
              aspectRatio: '1', border: accentColor === c ? '2.5px solid #0F172A' : '1.5px solid #E2E8F0',
              borderRadius: 6, background: c, cursor: 'pointer', padding: 0,
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
                padding: '9px 11px',
                border: active ? '1.5px solid #6366F1' : '1px solid #E2E8F0',
                background: active ? '#EEF2FF' : '#fff',
                borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit',
                textAlign: 'left', display: 'flex', alignItems: 'center', gap: 10,
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
        <div style={{ display: 'inline-flex', background: '#F1F5F9', padding: 2, borderRadius: 7, gap: 1, width: '100%' }}>
          {[
            { k: 'compact',  l: 'Kompakt' },
            { k: 'normal',   l: 'Komfort' },
            { k: 'spacious', l: 'Luźna'   },
          ].map(o => (
            <button key={o.k} onClick={() => onDensity(o.k)} style={{
              flex: 1, padding: '7px 6px', border: 'none',
              background: density === o.k ? '#fff' : 'transparent',
              borderRadius: 5, cursor: 'pointer',
              fontFamily: 'inherit', fontSize: 11.5, fontWeight: density === o.k ? 600 : 500,
              color: density === o.k ? '#0F172A' : '#64748B',
              boxShadow: density === o.k ? '0 1px 2px rgba(0,0,0,.06)' : 'none',
            }}>{o.l}</button>
          ))}
        </div>
      </TweakRow>
    </div>
  );
}

// ─── AiChatPanel ──────────────────────────────────────────────────────────────

interface AIChatMsg { role: 'ai' | 'user'; text: string }

function AiChatPanel({ projectId, onClose }: { projectId: string; onClose: () => void }) {
  const [messages, setMessages] = useState<AIChatMsg[]>([
    { role: 'ai', text: 'Cześć! Widzę podgląd Twojej strony. Co chcesz zmienić w wyglądzie lub treści?' },
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
    setMessages(prev => [...prev, { role: 'user', text }]);
    setInput('');
    setSending(true);
    let aiText = '';
    setMessages(prev => [...prev, { role: 'ai', text: '…' }]);
    try {
      await api.chatStream(projectId, text, 5, (chunk) => {
        aiText += chunk;
        setMessages(prev => { const n = [...prev]; n[n.length - 1] = { role: 'ai', text: aiText }; return n; });
      });
    } catch {
      setMessages(prev => { const n = [...prev]; n[n.length - 1] = { role: 'ai', text: 'Błąd połączenia z AI.' }; return n; });
    } finally {
      setSending(false);
    }
  };

  const suggestions = ['Zmień styl na ciemny', 'Bardziej minimalistycznie', 'Dobierz kolory do branży', 'Co poprawić?'];

  return (
    <div style={{ position: 'fixed', right: 24, bottom: 90, width: 380, height: 480, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 16, boxShadow: '0 20px 48px rgba(15,23,42,.18)', display: 'flex', flexDirection: 'column', zIndex: 70, fontFamily: 'Inter, sans-serif' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #F1F5F9', display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: 'linear-gradient(135deg, #6366F1, #EC4899)', display: 'grid', placeItems: 'center' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
        </div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#0F172A' }}>AI asystent</div>
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
            placeholder="Co chcesz zmienić?"
            rows={1}
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
  const { sections, brand, setBrand, saveBrief, projectName } = useLabStore();

  const [device, setDevice] = useState<Device>('desktop');
  const [tweaksOpen, setTweaksOpen] = useState(true);
  const [liveEdit, setLiveEdit] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const { toast, show: showToast } = useToast();

  const colRef = useRef<HTMLDivElement>(null);
  const [previewScale, setPreviewScale] = useState(1);
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Derived values
  const fontPairKey = getFontPairKey(brand.fontHeading || 'Instrument Serif', brand.fontBody || 'Inter');
  const densityLevel = DENSITY_LEVELS[brand.density || 'normal'] ?? 3;
  const typo = makeTypo(densityLevel, brand.fontHeading || 'Instrument Serif', brand.fontBody || 'Inter');

  // Canvas scaling via ResizeObserver
  useLayoutEffect(() => {
    const fit = () => {
      const col = colRef.current;
      if (!col) return;
      if (!liveEdit) { setPreviewScale(1); return; }
      const available = col.clientWidth - 48;
      setPreviewScale(Math.min(1, available / DEVICES[device].w));
    };
    fit();
    const ro = new ResizeObserver(fit);
    if (colRef.current) ro.observe(colRef.current);
    return () => ro.disconnect();
  }, [device, tweaksOpen, liveEdit]);

  // Escape closes fullscreen
  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') setFullscreen(false); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, []);

  // Debounced brand save after TweakPanel change
  const patchBrand = useCallback((patch: Parameters<typeof setBrand>[0]) => {
    setBrand(patch);
    setSaved(false);
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      saveBrief().catch(() => {});
    }, 800);
  }, [setBrand, saveBrief]);

  const handleFontPair = useCallback((key: string) => {
    const pair = FONT_PAIRS[key];
    if (pair) patchBrand({ fontHeading: pair.h, fontBody: pair.b });
  }, [patchBrand]);

  const handleSave = async () => {
    await saveBrief();
    setSaved(true);
    showToast('Styl strony zapisany!');
  };

  // Sections renderer (read-only in Step5 — tweaks only)
  const noop = useCallback(() => {}, []);

  const renderSections = () =>
    sections.map(section => {
      const Renderer = section.slots_json ? getRenderer(section.block_code) : null;
      return (
        <div key={section.id}>
          {Renderer
            ? <Renderer section={section} brand={brand} typo={typo} onSlotUpdate={noop} />
            : <PlaceholderSection section={section} />
          }
        </div>
      );
    });

  const stageW = DEVICES[device].w;
  const chromeW = Math.min(stageW * previewScale, stageW);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden', fontFamily: 'Inter, system-ui, sans-serif' }}>

      {/* ── Topbar ─────────────────────────────────────────────────────────── */}
      <div style={{ background: '#fff', borderBottom: '1px solid #E2E8F0', height: 56, display: 'flex', alignItems: 'center', padding: '0 20px', gap: 12, flexShrink: 0, zIndex: 40 }}>

        <div style={{ fontSize: 10, fontWeight: 600, color: '#6366F1', textTransform: 'uppercase', letterSpacing: 0.8, whiteSpace: 'nowrap' }}>
          ● Krok 5 · Wizualizacja
        </div>

        <div style={{ flex: 1 }} />

        {/* Device switcher */}
        <div style={{ display: 'inline-flex', background: '#F1F5F9', padding: 3, borderRadius: 9, gap: 2 }}>
          {(['desktop', 'tablet', 'mobile'] as const).map(d => (
            <button key={d} onClick={() => setDevice(d)} title={`${DEVICES[d].label} — ${DEVICES[d].w}px`}
              style={{ padding: '5px 10px', border: 'none', borderRadius: 7, background: device === d ? '#fff' : 'transparent', color: device === d ? '#0F172A' : '#64748B', fontSize: 12, fontWeight: device === d ? 600 : 500, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6, boxShadow: device === d ? '0 1px 2px rgba(15,23,42,.08)' : 'none', fontFamily: 'inherit' }}>
              {d === 'desktop'
                ? <><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>Desktop</>
                : d === 'tablet'
                  ? <><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="5" y="2" width="14" height="20" rx="2"/></svg>Tablet</>
                  : <><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="6" y="2" width="12" height="20" rx="2"/></svg>Mobile</>
              }
            </button>
          ))}
        </div>

        {/* Edit / Preview toggle */}
        <div style={{ display: 'inline-flex', background: '#F1F5F9', padding: 3, borderRadius: 9, gap: 2 }}>
          {[
            { v: true,  label: 'Edytuj',  icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg> },
            { v: false, label: 'Podgląd', icon: <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg> },
          ].map(({ v, label, icon }) => (
            <button key={label} onClick={() => setLiveEdit(v)}
              style={{ padding: '5px 11px', border: 'none', background: liveEdit === v ? '#fff' : 'transparent', borderRadius: 6, cursor: 'pointer', color: liveEdit === v ? '#0F172A' : '#64748B', boxShadow: liveEdit === v ? '0 1px 2px rgba(15,23,42,.08)' : 'none', display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: liveEdit === v ? 600 : 500, fontFamily: 'inherit' }}>
              {icon}{label}
            </button>
          ))}
        </div>

        {/* Fullscreen */}
        <button onClick={() => { setLiveEdit(false); setFullscreen(true); }}
          style={{ padding: '6px 12px', border: '1px solid #E2E8F0', background: '#fff', borderRadius: 9, cursor: 'pointer', color: '#334155', fontSize: 12, fontWeight: 500, display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: 'inherit' }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M3 3h6M3 3v6M21 3h-6M21 3v6M21 21h-6M21 21v-6M3 21h6M3 21v-6"/></svg>
          Pełny ekran
        </button>

        {/* Tweaks toggle */}
        <button onClick={() => setTweaksOpen(v => !v)}
          style={{ padding: '6px 12px', border: `1px solid ${tweaksOpen ? '#6366F1' : '#E2E8F0'}`, background: tweaksOpen ? '#EEF2FF' : '#fff', borderRadius: 9, cursor: 'pointer', color: tweaksOpen ? '#6366F1' : '#334155', fontSize: 12, fontWeight: tweaksOpen ? 600 : 500, display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: 'inherit' }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93l-1.41 1.41M4.93 4.93l1.41 1.41M19.07 19.07l-1.41-1.41M4.93 19.07l1.41-1.41M21 12h-3M6 12H3M12 21v-3M12 6V3"/></svg>
          Tweaki
        </button>

        {/* Save */}
        <button onClick={handleSave}
          style={{ padding: '8px 16px', background: saved ? '#DCFCE7' : 'linear-gradient(135deg, #10B981 0%, #14B8A6 100%)', color: saved ? '#065F46' : '#fff', border: 'none', borderRadius: 9, fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 7, boxShadow: saved ? 'none' : '0 2px 8px rgba(16,185,129,.35)', transition: 'background .2s' }}>
          {saved
            ? <><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>Zapisano</>
            : <><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 00-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 012-3.95A12.88 12.88 0 0122 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 01-4 2z"/></svg>Zapisz styl</>
          }
        </button>
      </div>

      {/* ── Main area ──────────────────────────────────────────────────────── */}
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: tweaksOpen ? 'minmax(0,1fr) 320px' : '1fr', overflow: 'hidden' }}>

        {/* ── Preview column ── */}
        <div ref={colRef} style={{ background: '#E5E7EB', padding: '20px 24px 40px', overflow: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

          {/* Browser chrome */}
          <div style={{ width: chromeW, maxWidth: '100%', background: '#F8FAFC', borderRadius: '12px 12px 0 0', border: '1px solid #D1D5DB', borderBottom: 'none', padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 10, boxShadow: '0 2px 4px rgba(0,0,0,.04)', fontFamily: 'Inter, sans-serif', flexShrink: 0 }}>
            <div style={{ display: 'flex', gap: 5 }}>
              <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#FF5F57', display: 'block' }} />
              <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#FEBC2E', display: 'block' }} />
              <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#28C840', display: 'block' }} />
            </div>
            <div style={{ flex: 1, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 6, padding: '4px 10px', fontSize: 11, color: '#94A3B8', fontFamily: 'ui-monospace, monospace', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {(projectName || 'moja-strona').toLowerCase().replace(/\s+/g, '-')}.pl/
            </div>
            <div style={{ fontSize: 10, color: '#94A3B8', flexShrink: 0 }}>{stageW}px</div>
          </div>

          {/* Scaled canvas */}
          <div style={{ width: chromeW, maxWidth: '100%', background: '#fff', border: '1px solid #D1D5DB', borderTop: 'none', overflow: 'hidden', boxShadow: '0 8px 24px rgba(0,0,0,.08)', flexShrink: 0, position: 'relative' }}>
            {/* Overlay in preview mode to prevent accidental edits */}
            {!liveEdit && <div style={{ position: 'absolute', inset: 0, zIndex: 10 }} />}
            <div style={{ width: stageW, transformOrigin: 'top left', transform: `scale(${previewScale})` }}>
              {sections.length === 0 ? (
                <div style={{ padding: '80px 40px', textAlign: 'center', color: '#94A3B8', fontFamily: 'Inter, sans-serif' }}>
                  <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>Brak sekcji</div>
                  <div style={{ fontSize: 13 }}>Wróć do kroku 3 aby wygenerować strukturę strony.</div>
                </div>
              ) : renderSections()}
            </div>
          </div>
        </div>

        {/* ── TweakPanel column ── */}
        {tweaksOpen && (
          <div style={{ background: '#fff', borderLeft: '1px solid #E2E8F0', overflow: 'auto', padding: '20px 20px 40px' }}>
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
        )}
      </div>

      {/* ── Fullscreen overlay ─────────────────────────────────────────────── */}
      {fullscreen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 500, background: '#0F172A', display: 'flex', flexDirection: 'column' }}>
          {/* Top bar */}
          <div style={{ height: 44, background: '#0F172A', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', borderBottom: '1px solid rgba(255,255,255,.08)', fontSize: 12, fontFamily: 'Inter, sans-serif' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 8, height: 8, borderRadius: 4, background: '#10B981', boxShadow: '0 0 0 3px rgba(16,185,129,.2)' }} />
              <span style={{ fontWeight: 600 }}>Podgląd 1:1</span>
              <span style={{ color: 'rgba(255,255,255,.5)' }}>·</span>
              <span style={{ color: 'rgba(255,255,255,.7)' }}>{projectName || 'Projekt'}</span>
              <span style={{ color: 'rgba(255,255,255,.5)' }}>·</span>
              <span style={{ color: 'rgba(255,255,255,.7)' }}>{DEVICES[device].w}px</span>
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              {(['desktop', 'tablet', 'mobile'] as const).map(d => (
                <button key={d} onClick={() => setDevice(d)} style={{ padding: '4px 10px', border: '1px solid rgba(255,255,255,.15)', background: device === d ? 'rgba(255,255,255,.12)' : 'transparent', color: '#fff', borderRadius: 6, cursor: 'pointer', fontSize: 11, fontWeight: 500, fontFamily: 'inherit' }}>
                  {DEVICES[d].label}
                </button>
              ))}
              <div style={{ width: 1, height: 18, background: 'rgba(255,255,255,.15)', margin: '0 4px' }} />
              <button onClick={() => setFullscreen(false)} style={{ padding: '6px 12px', border: '1px solid rgba(255,255,255,.2)', background: 'rgba(255,255,255,.1)', color: '#fff', borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 600, fontFamily: 'inherit', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                Zamknij (Esc)
              </button>
            </div>
          </div>
          {/* Canvas 1:1 */}
          <div style={{ flex: 1, overflow: 'auto', display: 'flex', justifyContent: 'center', alignItems: 'flex-start', padding: device === 'desktop' ? 0 : 24 }}>
            <div style={{ width: DEVICES[device].w, minHeight: '100%', background: '#fff', boxShadow: device === 'desktop' ? 'none' : '0 30px 60px rgba(0,0,0,.4)', borderRadius: device === 'desktop' ? 0 : 14, overflow: 'hidden' }}>
              {renderSections()}
            </div>
          </div>
        </div>
      )}

      {/* ── AI FAB ──────────────────────────────────────────────────────────── */}
      {!aiChatOpen && (
        <button onClick={() => setAiChatOpen(true)}
          style={{ position: 'fixed', right: 24, bottom: 80, zIndex: 60, padding: '12px 18px', background: 'linear-gradient(135deg, #6366F1, #EC4899)', color: '#fff', border: 'none', borderRadius: 999, fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8, boxShadow: '0 12px 30px rgba(99,102,241,.35)', fontFamily: 'Inter, sans-serif' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
          AI asystent
        </button>
      )}

      {/* ── AI Chat ─────────────────────────────────────────────────────────── */}
      {aiChatOpen && projectId && (
        <AiChatPanel projectId={projectId} onClose={() => setAiChatOpen(false)} />
      )}

      {/* ── ElementToolbar ──────────────────────────────────────────────────── */}
      <ElementToolbar />

      {/* ── Toast ───────────────────────────────────────────────────────────── */}
      {toast && (
        <div style={{ position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)', padding: '10px 18px', background: '#0F172A', color: '#fff', borderRadius: 10, fontSize: 13, fontWeight: 500, zIndex: 100, boxShadow: '0 8px 24px rgba(15,23,42,.3)', fontFamily: 'Inter, sans-serif', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
          {toast}
        </div>
      )}

      {/* ── Bottom nav ──────────────────────────────────────────────────────── */}
      <div style={{ background: '#fff', borderTop: '1px solid #F1F5F9', padding: '12px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0, zIndex: 30 }}>
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
