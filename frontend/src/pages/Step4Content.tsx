/**
 * Step 4 — Treści (Krok 4 z 6)
 * Odwzorowanie makiety tresci_app.jsx: pełny widok sekcji, contentEditable inline,
 * SectionHoverActions, AI FAB, TypoPopover.
 */

import { useState, useRef, useEffect, useLayoutEffect, useCallback, createElement } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore, type Section } from "@/store/labStore";
import type { Brand } from "@/types/lab";
import { FONT_OPTIONS } from "@/types/lab";
import * as api from "@/api/client";
import ElementToolbar from "@/components/ElementToolbar";

// ─── Typography ─────────────────────────────────────────────────────────────

const DENSITY_SCALE: Record<number, { body: number; scale: number; lh: number; sp: number }> = {
  1: { body: 14, scale: 1.20, lh: 1.40, sp: 0.70 },
  2: { body: 15, scale: 1.22, lh: 1.45, sp: 0.85 },
  3: { body: 16, scale: 1.25, lh: 1.50, sp: 1.00 },
  4: { body: 17, scale: 1.28, lh: 1.55, sp: 1.20 },
  5: { body: 18, scale: 1.30, lh: 1.60, sp: 1.40 },
};

const DENSITY_LABELS: Record<number, string> = { 1: 'Kompakt', 2: 'Zwarty', 3: 'Komfort', 4: 'Przestronny', 5: 'Luźny' };

type Typo = { hf: string; bf: string; body: number; lh: number; sp: number; ey: number; h3: number; h2: number; h1: number };

function makeTypo(density: number, hf: string, bf: string): Typo {
  const d = DENSITY_SCALE[density] || DENSITY_SCALE[3];
  const b = d.body, s = d.scale;
  return { hf, bf, body: b, lh: d.lh, sp: d.sp, ey: Math.round(b * 0.8), h3: Math.round(b * s * s), h2: Math.round(b * s * s * s), h1: Math.round(b * s * s * s * s) };
}

type Viewport = "desktop" | "tablet" | "mobile";
const VP_WIDTHS: Record<Viewport, number> = { desktop: 1440, tablet: 768, mobile: 390 };

// ─── Helpers ─────────────────────────────────────────────────────────────────

function isDark(hex: string): boolean {
  const c = (hex || '').replace('#', '');
  if (c.length < 6) return false;
  return (0.299 * parseInt(c.slice(0,2),16) + 0.587 * parseInt(c.slice(2,4),16) + 0.114 * parseInt(c.slice(4,6),16)) < 128;
}

function str(v: unknown): string { return v == null ? '' : String(v); }
function arr<T>(v: unknown): T[] { return Array.isArray(v) ? (v as T[]) : []; }

/** Pobierz pierwszą pasującą wartość ze slots */
function gStr(s: Record<string, unknown>, keys: string[]): [string, string] {
  for (const k of keys) if (s[k] !== undefined && s[k] !== null) return [k, str(s[k])];
  return ['', ''];
}
function gArr<T>(s: Record<string, unknown>, keys: string[]): [string, T[]] {
  for (const k of keys) if (Array.isArray(s[k])) return [k, s[k] as T[]];
  return ['', []];
}

function ctaBg(brand: Brand): string {
  if (brand.ctaIsGradient) return `linear-gradient(135deg, ${brand.ctaColor}, ${brand.ctaColor2})`;
  return brand.ctaColor as string;
}

// ─── Toast ───────────────────────────────────────────────────────────────────

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

// ─── InlineEdit — contentEditable z obsluga HTML ────────────────────────────

interface InlineEditProps {
  value: string;
  onChange: (v: string) => void;
  tag?: string;
  style?: React.CSSProperties;
  multiline?: boolean;
}

function InlineEdit({ value, onChange, tag = 'span', style, multiline = false }: InlineEditProps) {
  const ref = useRef<HTMLElement>(null);
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    if (ref.current && !focused && ref.current.innerHTML !== (value || '')) {
      ref.current.innerHTML = value || '';
    }
  }, [value, focused]);

  return createElement(tag, {
    ref,
    contentEditable: true,
    suppressContentEditableWarning: true,
    style: {
      ...style,
      cursor: 'text',
      minWidth: 16,
      outline: focused ? '2px solid #6366F1' : 'none',
      outlineOffset: 2,
      borderRadius: 3,
      transition: 'outline .1s',
    },
    onFocus: () => setFocused(true),
    onBlur: (e: React.FocusEvent<HTMLElement>) => {
      setFocused(false);
      const html = e.currentTarget.innerHTML;
      if (html !== value) onChange(html);
    },
    onKeyDown: (e: React.KeyboardEvent) => {
      if (!multiline && e.key === 'Enter') { e.preventDefault(); (e.target as HTMLElement).blur(); }
      if (e.key === 'Escape') { (e.target as HTMLElement).blur(); }
    },
  });
}

// ─── Renderer props ───────────────────────────────────────────────────────────

interface RP {
  section: Section;
  brand: Brand;
  typo: Typo;
  onSlotUpdate: (key: string, value: unknown) => void;
}

// ─── NavSection ───────────────────────────────────────────────────────────────

function NavSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#FFFFFF';
  const dark = isDark(bg);
  const tc = dark ? '#FFFFFF' : '#0F172A';
  const sc = dark ? '#CBD5E1' : '#334155';
  const [logoKey, logoVal] = gStr(s, ['logo_text', 'logo', 'brand_name', 'title']);
  const [ctaKey, ctaVal] = gStr(s, ['cta_text', 'cta', 'button_text']);
  const [menuKey, menuItems] = gArr<{ label: string; url: string }>(s, ['menu_items', 'links', 'nav_items']);

  return (
    <div style={{ padding: '0 80px', display: 'flex', alignItems: 'center', height: 72, background: bg, borderBottom: `1px solid ${dark ? 'rgba(255,255,255,.1)' : 'rgba(0,0,0,.06)'}` }}>
      <InlineEdit value={logoVal} onChange={v => onSlotUpdate(logoKey || 'logo_text', v)} tag="div"
        style={{ fontFamily: `'${typo.hf}', serif`, fontSize: Math.round(typo.h3 * 0.72), fontWeight: 700, color: tc, letterSpacing: '-0.01em', whiteSpace: 'nowrap', flexShrink: 0 }} />
      <div style={{ flex: 1, display: 'flex', gap: 32, justifyContent: 'center' }}>
        {menuItems.slice(0, 6).map((item, i) => (
          <InlineEdit key={i} value={str(item.label)} tag="span"
            onChange={v => onSlotUpdate(menuKey || 'menu_items', menuItems.map((m, j) => j === i ? { ...m, label: v } : m))}
            style={{ fontFamily: `'${typo.bf}', sans-serif`, fontSize: Math.round(typo.body * 0.95), color: sc, fontWeight: 500 }} />
        ))}
      </div>
      <span style={{ display: 'inline-flex', alignItems: 'center', padding: `8px 20px`, background: ctaBg(brand), borderRadius: 10, fontFamily: `'${typo.bf}'`, fontSize: typo.body, fontWeight: 600, flexShrink: 0 }}>
        <InlineEdit value={ctaVal} onChange={v => onSlotUpdate(ctaKey || 'cta_text', v)} tag="span"
          style={{ color: brand.ctaTextColor || '#fff', fontSize: 'inherit', fontWeight: 'inherit' }} />
      </span>
    </div>
  );
}

// ─── HeroSection ─────────────────────────────────────────────────────────────

function HeroSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#F8FAFC';
  const dark = isDark(bg);
  const tc = dark ? '#FFFFFF' : '#0F172A';
  const bc = dark ? '#CBD5E1' : '#334155';
  const ec = dark ? (brand.ctaColor2 as string) : '#B45309';

  const [preTitleKey, preTitleVal] = gStr(s, ['pre_title', 'eyebrow', 'tagline', 'label']);
  const [titleKey, titleVal] = gStr(s, ['title', 'heading', 'h1']);
  const [bodyKey, bodyVal] = gStr(s, ['subtitle', 'description', 'body', 'text', 'paragraph']);
  const [cta1Key, cta1Val] = gStr(s, ['cta_primary', 'cta_text', 'cta', 'button_text']);
  const [cta2Key, cta2Val] = gStr(s, ['cta_secondary', 'cta_secondary_text', 'cta2', 'button2_text']);
  const [statsKey, statsVal] = gArr<{ value: string; label: string }>(s, ['stats', 'statistics', 'numbers']);

  const isHE2 = section.block_code === 'HE2';
  const isCentered = !isHE2;

  return (
    <div style={{ padding: `${Math.round(120 * typo.sp)}px 80px`, background: bg, ...(isHE2 ? { display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 80, alignItems: 'center' } : {}) }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: Math.round(20 * typo.sp), ...(isCentered ? { textAlign: 'center', alignItems: 'center' } : {}) }}>
        {preTitleVal && (
          <InlineEdit value={preTitleVal} onChange={v => onSlotUpdate(preTitleKey, v)} tag="div"
            style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.ey, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.12em', color: ec, opacity: 0.9 }} />
        )}
        <InlineEdit value={titleVal} onChange={v => onSlotUpdate(titleKey || 'title', v)} tag="h1"
          style={{ margin: 0, fontFamily: `'${typo.hf}', serif`, fontSize: typo.h1, fontWeight: 700, lineHeight: 1.1, letterSpacing: '-0.02em', color: tc }} />
        {bodyVal && (
          <InlineEdit value={bodyVal} onChange={v => onSlotUpdate(bodyKey, v)} tag="p" multiline
            style={{ margin: 0, fontFamily: `'${typo.bf}'`, fontSize: typo.body, lineHeight: typo.lh, color: bc }} />
        )}
        <div style={{ display: 'flex', gap: 16, marginTop: 8, ...(isCentered ? { justifyContent: 'center' } : {}) }}>
          {cta1Val && (
            <span style={{ display: 'inline-flex', alignItems: 'center', padding: `${Math.round(typo.body * 0.7)}px ${Math.round(typo.body * 1.5)}px`, background: ctaBg(brand), borderRadius: 12, fontFamily: `'${typo.bf}'`, fontWeight: 600 }}>
              <InlineEdit value={cta1Val} onChange={v => onSlotUpdate(cta1Key, v)} tag="span"
                style={{ color: brand.ctaTextColor || '#fff', fontSize: typo.body, fontWeight: 600 }} />
            </span>
          )}
          {cta2Val && (
            <span style={{ display: 'inline-flex', alignItems: 'center', padding: `${Math.round(typo.body * 0.7)}px ${Math.round(typo.body * 1.5)}px`, border: `2px solid ${dark ? '#fff' : '#0F172A'}`, borderRadius: 12, fontFamily: `'${typo.bf}'`, fontWeight: 600 }}>
              <InlineEdit value={cta2Val} onChange={v => onSlotUpdate(cta2Key, v)} tag="span"
                style={{ color: dark ? '#fff' : '#0F172A', fontSize: typo.body, fontWeight: 600 }} />
            </span>
          )}
        </div>
        {statsVal.length > 0 && (
          <div style={{ display: 'flex', gap: 40, marginTop: 8, ...(isCentered ? { justifyContent: 'center' } : {}) }}>
            {statsVal.map((stat, i) => (
              <div key={i} style={{ textAlign: 'center' }}>
                <InlineEdit value={str(stat.value)} tag="div" onChange={v => onSlotUpdate(statsKey, statsVal.map((st, j) => j === i ? { ...st, value: v } : st))}
                  style={{ fontFamily: `'${typo.hf}'`, fontSize: typo.h3, fontWeight: 700, color: tc }} />
                <InlineEdit value={str(stat.label)} tag="div" onChange={v => onSlotUpdate(statsKey, statsVal.map((st, j) => j === i ? { ...st, label: v } : st))}
                  style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.ey, color: dark ? '#94A3B8' : '#64748B' }} />
              </div>
            ))}
          </div>
        )}
      </div>
      {isHE2 && (
        <div style={{ aspectRatio: '4/5', background: `linear-gradient(135deg, ${brand.ctaColor}, ${brand.ctaColor2})`, borderRadius: 24, display: 'grid', placeItems: 'center', position: 'relative', overflow: 'hidden' }}>
          <div style={{ fontSize: 96, opacity: 0.2, color: '#fff' }}>▭</div>
          <div style={{ position: 'absolute', bottom: 16, right: 16, fontSize: 10, color: '#fff', opacity: 0.4, fontFamily: 'ui-monospace, monospace' }}>[zdjęcie]</div>
        </div>
      )}
    </div>
  );
}

// ─── FeaturesSection (RO, KR, CF, PR) ────────────────────────────────────────

function FeaturesSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#FFFFFF';
  const dark = isDark(bg);
  const tc = dark ? '#FFFFFF' : '#0F172A';
  const bc = dark ? '#CBD5E1' : '#475569';
  const ec = dark ? '#A5B4FC' : '#6366F1';

  const [preTKey, preTVal] = gStr(s, ['pre_title', 'eyebrow', 'tagline']);
  const [titleKey, titleVal] = gStr(s, ['title', 'heading']);
  const [bodyKey, bodyVal] = gStr(s, ['subtitle', 'description', 'body']);
  const [itemsKey, items] = gArr<Record<string, unknown>>(s, ['features', 'steps', 'benefits', 'points', 'items', 'cards', 'problems', 'services', 'solutions', 'reasons']);

  // Also look for simple string arrays
  const [, simpleItems] = gArr<string>(s, ['checkmarks', 'list']);

  return (
    <div style={{ padding: `${Math.round(100 * typo.sp)}px 80px`, background: bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${Math.round(56 * typo.sp)}px`, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {preTVal && (
          <InlineEdit value={preTVal} onChange={v => onSlotUpdate(preTKey, v)} tag="div"
            style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.ey, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.12em', color: ec, opacity: 0.9 }} />
        )}
        {titleVal && (
          <InlineEdit value={titleVal} onChange={v => onSlotUpdate(titleKey || 'title', v)} tag="h2"
            style={{ margin: 0, fontFamily: `'${typo.hf}'`, fontSize: typo.h2, fontWeight: 700, lineHeight: 1.15, color: tc }} />
        )}
        {bodyVal && (
          <InlineEdit value={bodyVal} onChange={v => onSlotUpdate(bodyKey, v)} tag="p" multiline
            style={{ margin: 0, fontFamily: `'${typo.bf}'`, fontSize: typo.body, lineHeight: typo.lh, color: bc }} />
        )}
      </div>
      {items.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(items.length, 3)}, 1fr)`, gap: 28 }}>
          {items.map((feat, i) => {
            const titleEntry = Object.entries(feat).find(([k]) => k.includes('title') || k.includes('name') || k === 'heading');
            const descEntry = Object.entries(feat).find(([k]) => k.includes('description') || k.includes('body') || k.includes('text') || k.includes('desc'));
            return (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 14, padding: 28, background: dark ? 'rgba(255,255,255,.07)' : '#F8FAFC', borderRadius: 14, border: `1px solid ${dark ? 'rgba(255,255,255,.08)' : '#E2E8F0'}` }}>
                <div style={{ width: 48, height: 48, borderRadius: 12, background: ctaBg(brand), display: 'grid', placeItems: 'center', color: '#fff', fontWeight: 700, fontSize: 18, fontFamily: `'${typo.hf}'`, flexShrink: 0 }}>{i + 1}</div>
                {titleEntry && (
                  <InlineEdit value={str(titleEntry[1])} tag="div" onChange={v => onSlotUpdate(itemsKey, items.map((f, j) => j === i ? { ...f, [titleEntry[0]]: v } : f))}
                    style={{ fontFamily: `'${typo.hf}'`, fontSize: typo.h3, fontWeight: 600, lineHeight: 1.25, color: tc }} />
                )}
                {descEntry && (
                  <InlineEdit value={str(descEntry[1])} tag="p" multiline onChange={v => onSlotUpdate(itemsKey, items.map((f, j) => j === i ? { ...f, [descEntry[0]]: v } : f))}
                    style={{ margin: 0, fontFamily: `'${typo.bf}'`, fontSize: Math.round(typo.body * 0.95), lineHeight: typo.lh, color: bc }} />
                )}
              </div>
            );
          })}
        </div>
      )}
      {simpleItems.length > 0 && items.length === 0 && (
        <div style={{ maxWidth: 720, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
          {simpleItems.map((p, i) => (
            <div key={i} style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
              <div style={{ width: 28, height: 28, borderRadius: 8, background: ctaBg(brand), display: 'grid', placeItems: 'center', color: '#fff', flexShrink: 0, marginTop: 2 }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>
              </div>
              <InlineEdit value={p} tag="div" onChange={v => onSlotUpdate('checkmarks', simpleItems.map((s, j) => j === i ? v : s))}
                style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.body, lineHeight: typo.lh, color: bc }} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── TestimonialsSection (OP) ─────────────────────────────────────────────────

function TestimonialsSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#FFFFFF';
  const dark = isDark(bg);
  const tc = dark ? '#FFFFFF' : '#0F172A';
  const bc = dark ? '#CBD5E1' : '#475569';

  const [preTKey, preTVal] = gStr(s, ['pre_title', 'eyebrow']);
  const [titleKey, titleVal] = gStr(s, ['title', 'heading']);
  const [tKey, testimonials] = gArr<Record<string, unknown>>(s, ['testimonials', 'opinions', 'reviews', 'quotes']);

  return (
    <div style={{ padding: `${Math.round(100 * typo.sp)}px 80px`, background: bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${Math.round(56 * typo.sp)}px`, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {preTVal && (
          <InlineEdit value={preTVal} onChange={v => onSlotUpdate(preTKey, v)} tag="div"
            style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.ey, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#B45309', opacity: 0.9 }} />
        )}
        {titleVal && (
          <InlineEdit value={titleVal} onChange={v => onSlotUpdate(titleKey || 'title', v)} tag="h2"
            style={{ margin: 0, fontFamily: `'${typo.hf}'`, fontSize: typo.h2, fontWeight: 700, lineHeight: 1.15, color: tc }} />
        )}
      </div>
      {testimonials.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(testimonials.length, 3)}, 1fr)`, gap: 24 }}>
          {testimonials.map((t, i) => {
            const quoteEntry = Object.entries(t).find(([k]) => k.includes('quote') || k.includes('text') || k.includes('content'));
            const authorEntry = Object.entries(t).find(([k]) => k.includes('author') || k.includes('name'));
            const roleEntry = Object.entries(t).find(([k]) => k.includes('role') || k.includes('position') || k.includes('company'));
            return (
              <div key={i} style={{ padding: 32, background: dark ? 'rgba(255,255,255,.08)' : '#fff', borderRadius: 16, display: 'flex', flexDirection: 'column', gap: 20, border: `1px solid ${dark ? 'rgba(255,255,255,.08)' : '#E2E8F0'}` }}>
                <div style={{ fontFamily: `'${typo.hf}'`, fontSize: 48, lineHeight: 0.5, color: brand.ctaColor as string, opacity: 0.4 }}>"</div>
                {quoteEntry && (
                  <InlineEdit value={str(quoteEntry[1])} tag="p" multiline onChange={v => onSlotUpdate(tKey, testimonials.map((tt, j) => j === i ? { ...tt, [quoteEntry[0]]: v } : tt))}
                    style={{ margin: 0, fontFamily: `'${typo.bf}'`, fontSize: Math.round(typo.body * 1.05), lineHeight: 1.55, color: bc, fontStyle: 'italic' }} />
                )}
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: ctaBg(brand), flexShrink: 0 }} />
                  <div>
                    {authorEntry && (
                      <InlineEdit value={str(authorEntry[1])} tag="div" onChange={v => onSlotUpdate(tKey, testimonials.map((tt, j) => j === i ? { ...tt, [authorEntry[0]]: v } : tt))}
                        style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.body, fontWeight: 600, color: tc }} />
                    )}
                    {roleEntry && (
                      <InlineEdit value={str(roleEntry[1])} tag="div" onChange={v => onSlotUpdate(tKey, testimonials.map((tt, j) => j === i ? { ...tt, [roleEntry[0]]: v } : tt))}
                        style={{ fontFamily: `'${typo.bf}'`, fontSize: Math.round(typo.body * 0.85), color: dark ? '#94A3B8' : '#64748B' }} />
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── CtaSection ───────────────────────────────────────────────────────────────

function CtaSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#0F172A';
  const dark = isDark(bg);
  const tc = dark ? '#FFFFFF' : '#0F172A';
  const bc = dark ? '#CBD5E1' : '#475569';

  const [preTKey, preTVal] = gStr(s, ['pre_title', 'eyebrow', 'tagline']);
  const [titleKey, titleVal] = gStr(s, ['title', 'heading']);
  const [bodyKey, bodyVal] = gStr(s, ['subtitle', 'description', 'body']);
  const [cta1Key, cta1Val] = gStr(s, ['cta_primary', 'cta_text', 'cta', 'button_text']);
  const [cta2Key, cta2Val] = gStr(s, ['cta_secondary', 'cta_secondary_text', 'cta2']);

  return (
    <div style={{ padding: `${Math.round(120 * typo.sp)}px 80px`, background: bg, textAlign: 'center' }}>
      <div style={{ maxWidth: 720, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: Math.round(20 * typo.sp), alignItems: 'center' }}>
        {preTVal && (
          <InlineEdit value={preTVal} onChange={v => onSlotUpdate(preTKey, v)} tag="div"
            style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.ey, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.12em', color: brand.ctaColor2 as string, opacity: 0.9 }} />
        )}
        {titleVal && (
          <InlineEdit value={titleVal} onChange={v => onSlotUpdate(titleKey || 'title', v)} tag="h2"
            style={{ margin: 0, fontFamily: `'${typo.hf}'`, fontSize: typo.h2, fontWeight: 700, lineHeight: 1.15, color: tc }} />
        )}
        {bodyVal && (
          <InlineEdit value={bodyVal} onChange={v => onSlotUpdate(bodyKey, v)} tag="p" multiline
            style={{ margin: 0, fontFamily: `'${typo.bf}'`, fontSize: typo.body, lineHeight: typo.lh, color: bc }} />
        )}
        <div style={{ display: 'flex', gap: 16, marginTop: 12, justifyContent: 'center' }}>
          {cta1Val && (
            <span style={{ display: 'inline-flex', alignItems: 'center', padding: `${Math.round(typo.body * 0.75)}px ${Math.round(typo.body * 1.75)}px`, background: ctaBg(brand), borderRadius: 12, fontFamily: `'${typo.bf}'`, fontWeight: 600 }}>
              <InlineEdit value={cta1Val} onChange={v => onSlotUpdate(cta1Key, v)} tag="span"
                style={{ color: brand.ctaTextColor || '#fff', fontSize: typo.body, fontWeight: 600 }} />
            </span>
          )}
          {cta2Val && (
            <span style={{ display: 'inline-flex', alignItems: 'center', padding: `${Math.round(typo.body * 0.75)}px ${Math.round(typo.body * 1.75)}px`, border: `2px solid ${dark ? '#fff' : '#0F172A'}`, borderRadius: 12, fontFamily: `'${typo.bf}'`, fontWeight: 600 }}>
              <InlineEdit value={cta2Val} onChange={v => onSlotUpdate(cta2Key, v)} tag="span"
                style={{ color: dark ? '#fff' : '#0F172A', fontSize: typo.body, fontWeight: 600 }} />
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── FooterSection ────────────────────────────────────────────────────────────

function FooterSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#0F172A';
  const [logoKey, logoVal] = gStr(s, ['logo_text', 'brand_name', 'company_name', 'logo']);
  const [descKey, descVal] = gStr(s, ['description', 'tagline', 'desc', 'subtitle']);
  const [copyKey, copyVal] = gStr(s, ['copyright', 'copy', 'footer_note']);
  const [colsKey, cols] = gArr<{ title: string; links: string[] }>(s, ['columns', 'cols', 'sections']);

  return (
    <div style={{ padding: '80px 80px 32px', background: bg, color: '#CBD5E1' }}>
      <div style={{ display: 'grid', gridTemplateColumns: cols.length > 0 ? `1.2fr ${cols.slice(0,3).map(() => '1fr').join(' ')}` : '1fr', gap: 60, marginBottom: 60 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <InlineEdit value={logoVal} onChange={v => onSlotUpdate(logoKey || 'logo_text', v)} tag="div"
            style={{ fontFamily: `'${typo.hf}', serif`, fontSize: typo.h3, fontWeight: 700, color: '#fff', letterSpacing: '-0.01em' }} />
          {descVal && (
            <InlineEdit value={descVal} onChange={v => onSlotUpdate(descKey, v)} tag="p" multiline
              style={{ margin: 0, fontFamily: `'${typo.bf}'`, fontSize: Math.round(typo.body * 0.95), lineHeight: typo.lh, color: '#94A3B8' }} />
          )}
        </div>
        {cols.slice(0, 3).map((col, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <InlineEdit value={str(col.title)} tag="div" onChange={v => onSlotUpdate(colsKey, cols.map((c, j) => j === i ? { ...c, title: v } : c))}
              style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.ey, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#fff', marginBottom: 8 }} />
            {arr<string>(col.links).map((lnk, li) => (
              <InlineEdit key={li} value={str(lnk)} tag="div" onChange={v => onSlotUpdate(colsKey, cols.map((c, j) => j === i ? { ...c, links: (c.links || []).map((l: string, k: number) => k === li ? v : l) } : c))}
                style={{ fontFamily: `'${typo.bf}'`, fontSize: Math.round(typo.body * 0.95), color: '#CBD5E1' }} />
            ))}
          </div>
        ))}
      </div>
      <div style={{ paddingTop: 24, borderTop: '1px solid rgba(255,255,255,.1)' }}>
        <InlineEdit value={copyVal || `© ${new Date().getFullYear()} Wszelkie prawa zastrzeżone`} onChange={v => onSlotUpdate(copyKey || 'copyright', v)} tag="div"
          style={{ fontFamily: `'${typo.bf}'`, fontSize: Math.round(typo.body * 0.85), color: '#64748B', textAlign: 'center' }} />
      </div>
    </div>
  );
}

// ─── GenericSection — ogólny renderer dla reszty sekcji ──────────────────────

function GenericSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#FFFFFF';
  const dark = isDark(bg);
  const tc = dark ? '#FFFFFF' : '#0F172A';
  const bc = dark ? '#CBD5E1' : '#475569';

  const [preTKey, preTVal] = gStr(s, ['pre_title', 'eyebrow', 'tagline', 'label']);
  const [titleKey, titleVal] = gStr(s, ['title', 'heading', 'h1', 'h2']);
  const [bodyKey, bodyVal] = gStr(s, ['subtitle', 'description', 'body', 'text', 'paragraph', 'content']);
  const [cta1Key, cta1Val] = gStr(s, ['cta_primary', 'cta_text', 'cta', 'button_text']);

  // All array fields
  const arrayEntries = Object.entries(s).filter(([, v]) => Array.isArray(v));

  return (
    <div style={{ padding: `${Math.round(100 * typo.sp)}px 80px`, background: bg }}>
      <div style={{ maxWidth: 820, margin: '0 auto', textAlign: 'center' }}>
        {preTVal && (
          <InlineEdit value={preTVal} onChange={v => onSlotUpdate(preTKey, v)} tag="div"
            style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.ey, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.12em', color: dark ? '#A5B4FC' : '#6366F1', marginBottom: 16 }} />
        )}
        {titleVal && (
          <InlineEdit value={titleVal} onChange={v => onSlotUpdate(titleKey || 'title', v)} tag="h2"
            style={{ margin: '0 0 20px', fontFamily: `'${typo.hf}'`, fontSize: typo.h2, fontWeight: 700, lineHeight: 1.15, color: tc }} />
        )}
        {bodyVal && (
          <InlineEdit value={bodyVal} onChange={v => onSlotUpdate(bodyKey, v)} tag="p" multiline
            style={{ margin: '0 0 28px', fontFamily: `'${typo.bf}'`, fontSize: typo.body, lineHeight: typo.lh, color: bc, maxWidth: 640, display: 'block', marginInline: 'auto' }} />
        )}
        {cta1Val && (
          <span style={{ display: 'inline-flex', alignItems: 'center', padding: `${Math.round(typo.body * 0.7)}px ${Math.round(typo.body * 1.5)}px`, background: ctaBg(brand), borderRadius: 12, fontFamily: `'${typo.bf}'`, fontWeight: 600, marginBottom: 32 }}>
            <InlineEdit value={cta1Val} onChange={v => onSlotUpdate(cta1Key, v)} tag="span"
              style={{ color: brand.ctaTextColor || '#fff', fontSize: typo.body, fontWeight: 600 }} />
          </span>
        )}
      </div>
      {arrayEntries.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(3, (arrayEntries[0]?.[1] as unknown[]).length)}, 1fr)`, gap: 24, maxWidth: 900, margin: '0 auto' }}>
          {((arrayEntries[0]?.[1] as unknown[]) || []).slice(0, 6).map((item, i) => {
            const [key, items] = arrayEntries[0];
            if (typeof item === 'string') return (
              <div key={i} style={{ padding: 20, background: dark ? 'rgba(255,255,255,.07)' : '#F8FAFC', borderRadius: 12, border: `1px solid ${dark ? 'rgba(255,255,255,.08)' : '#E2E8F0'}` }}>
                <InlineEdit value={item} tag="div" onChange={v => onSlotUpdate(key, (items as unknown[]).map((it, j) => j === i ? v : it))}
                  style={{ fontFamily: `'${typo.bf}'`, fontSize: typo.body, color: bc }} />
              </div>
            );
            if (typeof item === 'object' && item !== null) {
              const obj = item as Record<string, unknown>;
              const titleEnt = Object.entries(obj).find(([k]) => k.includes('title') || k.includes('name') || k === 'heading');
              const descEnt = Object.entries(obj).find(([k]) => k.includes('description') || k.includes('body') || k.includes('text'));
              return (
                <div key={i} style={{ padding: 24, background: dark ? 'rgba(255,255,255,.07)' : '#fff', borderRadius: 14, border: `1px solid ${dark ? 'rgba(255,255,255,.08)' : '#E2E8F0'}`, display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {titleEnt && (
                    <InlineEdit value={str(titleEnt[1])} tag="div" onChange={v => onSlotUpdate(key, (items as unknown[]).map((it, j) => j === i ? { ...obj, [titleEnt[0]]: v } : it))}
                      style={{ fontFamily: `'${typo.hf}'`, fontSize: typo.h3, fontWeight: 600, color: tc }} />
                  )}
                  {descEnt && (
                    <InlineEdit value={str(descEnt[1])} tag="p" multiline onChange={v => onSlotUpdate(key, (items as unknown[]).map((it, j) => j === i ? { ...obj, [descEnt[0]]: v } : it))}
                      style={{ margin: 0, fontFamily: `'${typo.bf}'`, fontSize: Math.round(typo.body * 0.9), lineHeight: typo.lh, color: bc }} />
                  )}
                </div>
              );
            }
            return null;
          })}
        </div>
      )}
    </div>
  );
}

// ─── PlaceholderSection ───────────────────────────────────────────────────────

function PlaceholderSection({ section }: { section: Section }) {
  return (
    <div style={{ padding: '60px 80px', background: '#FAFBFC', textAlign: 'center' }}>
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 12px', background: '#fff', border: '1px dashed #CBD5E1', borderRadius: 8, marginBottom: 12 }}>
        <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 11, fontWeight: 700, color: '#6366F1' }}>{section.block_code}</span>
        <span style={{ fontSize: 11, color: '#94A3B8' }}>· szablon w przygotowaniu</span>
      </div>
      <div style={{ fontSize: 22, fontWeight: 600, color: '#0F172A', marginBottom: 8 }}>{section.name || section.block_code}</div>
      <div style={{ fontSize: 13, color: '#64748B', maxWidth: 440, margin: '0 auto' }}>Tę sekcję wypełnij w etapie Wizualizacji lub kliknij "AI" aby wygenerować treść.</div>
    </div>
  );
}

// ─── SECTION_RENDERERS map ────────────────────────────────────────────────────

type RendererFn = (props: RP) => React.ReactNode;

const NAV_CODES = new Set(['NA1','NA2','NA3']);
const HERO_CODES = new Set(['HE1','HE2','HE3','HE4','HE5']);
const FEAT_CODES = new Set(['RO1','RO2','KR1','KR2','CF1','CF2','PB1','PB2','PB3','PR1','PR2','FI1','FI2','FI3','FA1','OB1','LO1','ST1','ZE1','ZE2','CE1','RE1','KO1','OF1','OF2']);
const TESTI_CODES = new Set(['OP1','OP2']);
const CTA_CODES = new Set(['CT1','CT2','CT3']);
const FOOTER_CODES = new Set(['FO1']);

function getRenderer(blockCode: string): RendererFn {
  if (NAV_CODES.has(blockCode)) return NavSection;
  if (HERO_CODES.has(blockCode)) return HeroSection;
  if (TESTI_CODES.has(blockCode)) return TestimonialsSection;
  if (CTA_CODES.has(blockCode)) return CtaSection;
  if (FOOTER_CODES.has(blockCode)) return FooterSection;
  if (FEAT_CODES.has(blockCode)) return FeaturesSection;
  return GenericSection;
}

// ─── SectionHoverActions — z makiety tresci_app.jsx ──────────────────────────

interface SHAProps {
  scale: number;
  label: string;
  canUp: boolean;
  canDown: boolean;
  onUp: () => void;
  onDown: () => void;
  onDel: () => void;
  onRegen: () => void;
}

function SectionHoverActions({ scale, label, canUp, canDown, onUp, onDown, onDel, onRegen }: SHAProps) {
  const inv = scale ? 1 / scale : 1;
  return (
    <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 20, pointerEvents: 'none', transform: `scale(${inv})`, transformOrigin: 'top right' }}>
      <div style={{ pointerEvents: 'auto', display: 'inline-flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6 }}>
        <div style={{ padding: '3px 9px', background: '#0F172A', color: '#fff', borderRadius: 6, fontSize: 10.5, fontWeight: 600, fontFamily: 'Inter, sans-serif', letterSpacing: 0.2 }}>
          {label}
        </div>
        <div style={{ display: 'inline-flex', gap: 1, padding: 3, background: '#fff', border: '1px solid rgba(15,23,42,.1)', borderRadius: 8, boxShadow: '0 4px 14px rgba(15,23,42,.12)', fontFamily: 'Inter, sans-serif' }}>
          <SecAct title="Przesuń w górę" disabled={!canUp} onClick={onUp}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 15l-6-6-6 6"/></svg>
          </SecAct>
          <SecAct title="Przesuń w dół" disabled={!canDown} onClick={onDown}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M6 9l6 6 6-6"/></svg>
          </SecAct>
          <div style={{ width: 1, background: '#E2E8F0', margin: '2px 2px' }} />
          <SecAct title="Regeneruj AI" onClick={onRegen}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
          </SecAct>
          <SecAct title="Usuń sekcję" danger onClick={onDel}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </SecAct>
        </div>
      </div>
    </div>
  );
}

function SecAct({ children, onClick, title, disabled, danger }: { children: React.ReactNode; onClick?: () => void; title: string; disabled?: boolean; danger?: boolean }) {
  return (
    <button disabled={disabled} onClick={onClick} title={title}
      style={{ width: 30, height: 28, border: 'none', borderRadius: 6, background: 'transparent', color: disabled ? '#CBD5E1' : (danger ? '#DC2626' : '#334155'), cursor: disabled ? 'not-allowed' : 'pointer', display: 'grid', placeItems: 'center', fontFamily: 'inherit' }}
      onMouseEnter={e => { if (!disabled) (e.currentTarget as HTMLButtonElement).style.background = danger ? '#FEF2F2' : '#F1F5F9'; }}
      onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.background = 'transparent'; }}>
      {children}
    </button>
  );
}

// ─── TypoPopover ──────────────────────────────────────────────────────────────

interface TypoPopoverProps {
  open: boolean;
  setOpen: (v: boolean) => void;
  density: number;
  setDensity: (v: number) => void;
  headingFont: string;
  setHeadingFont: (v: string) => void;
  bodyFont: string;
  setBodyFont: (v: string) => void;
}

function TypoPopover({ open, setOpen, density, setDensity, headingFont, setHeadingFont, bodyFont, setBodyFont }: TypoPopoverProps) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false); };
    setTimeout(() => document.addEventListener('mousedown', h), 0);
    return () => document.removeEventListener('mousedown', h);
  }, [open, setOpen]);

  const HEADING_FONTS = FONT_OPTIONS.filter((_, i) => i % 2 === 1 || i < 3);
  const BODY_FONTS = FONT_OPTIONS.filter((_, i) => i % 2 === 0 || i < 3);

  return (
    <div style={{ position: 'relative' }}>
      <button onClick={() => setOpen(!open)}
        style={{ padding: '6px 12px 6px 10px', background: open ? '#F1F5F9' : '#fff', border: '1px solid #E2E8F0', borderRadius: 8, display: 'inline-flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 13, fontWeight: 500, color: '#334155' }}>
        <span style={{ fontFamily: `'${headingFont}', serif`, fontSize: 16, fontWeight: 700, lineHeight: 1 }}>Aa</span>
        <span style={{ fontSize: 11, color: '#94A3B8' }}>/</span>
        <span style={{ fontFamily: `'${bodyFont}', sans-serif`, fontSize: 13, fontWeight: 500, lineHeight: 1 }}>Aa</span>
        <span>Typografia</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      {open && (
        <div ref={ref} style={{ position: 'absolute', top: 'calc(100% + 8px)', left: 0, width: 340, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 14, boxShadow: '0 16px 40px rgba(15,23,42,.15)', zIndex: 50, padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: 14 }}>
            <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>Typografia</h3>
            <span style={{ marginLeft: 'auto', fontSize: 11, color: '#94A3B8' }}>dla podglądu treści</span>
          </div>
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Font nagłówków</div>
            <select value={headingFont} onChange={e => setHeadingFont(e.target.value)}
              style={{ width: '100%', padding: '8px 10px', border: '1px solid #E2E8F0', borderRadius: 8, fontSize: 13, fontFamily: 'inherit', cursor: 'pointer', background: '#F8FAFC' }}>
              {HEADING_FONTS.map(f => <option key={f} value={f} style={{ fontFamily: `'${f}'` }}>{f}</option>)}
            </select>
          </div>
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Font treści</div>
            <select value={bodyFont} onChange={e => setBodyFont(e.target.value)}
              style={{ width: '100%', padding: '8px 10px', border: '1px solid #E2E8F0', borderRadius: 8, fontSize: 13, fontFamily: 'inherit', cursor: 'pointer', background: '#F8FAFC' }}>
              {BODY_FONTS.map(f => <option key={f} value={f} style={{ fontFamily: `'${f}'` }}>{f}</option>)}
            </select>
          </div>
          <div>
            <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Gęstość tekstu</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <input type="range" min={1} max={5} step={1} value={density} onChange={e => setDensity(+e.target.value)}
                style={{ flex: 1, accentColor: '#6366F1' }} />
              <span style={{ width: 96, fontSize: 12, color: '#0F172A', fontWeight: 600, textAlign: 'right' }}>{DENSITY_LABELS[density]}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: '#94A3B8', marginTop: 4 }}>
              <span>kompakt</span><span>komfort</span><span>luźny</span>
            </div>
          </div>
          <div style={{ marginTop: 16, padding: '10px 12px', background: '#F8FAFC', borderRadius: 8, border: '1px solid #E2E8F0' }}>
            <div style={{ fontFamily: `'${headingFont}', serif`, fontSize: Math.round(DENSITY_SCALE[density].body * DENSITY_SCALE[density].scale * DENSITY_SCALE[density].scale), fontWeight: 700, lineHeight: 1.1, color: '#0F172A', letterSpacing: '-0.01em' }}>Nagłówek sekcji</div>
            <div style={{ fontFamily: `'${bodyFont}', sans-serif`, fontSize: DENSITY_SCALE[density].body, lineHeight: DENSITY_SCALE[density].lh, color: '#475569', marginTop: 6 }}>Przykładowy paragraf z treścią strony firmy.</div>
          </div>
          <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid #E2E8F0', display: 'flex', gap: 8 }}>
            <button onClick={() => { setDensity(3); }} style={{ padding: '6px 10px', background: 'transparent', border: '1px solid #E2E8F0', borderRadius: 7, fontSize: 12, color: '#64748B', cursor: 'pointer' }}>↺ Reset</button>
            <div style={{ flex: 1 }} />
            <button onClick={() => setOpen(false)} style={{ padding: '6px 14px', background: 'linear-gradient(135deg, #6366F1, #EC4899)', color: '#fff', border: 'none', borderRadius: 7, fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>Gotowe</button>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── AI Chat panel ────────────────────────────────────────────────────────────

interface AIChatMsg { role: 'ai' | 'user'; text: string }

function AiChatPanel({ projectId, onClose }: { projectId: string; onClose: () => void }) {
  const [messages, setMessages] = useState<AIChatMsg[]>([
    { role: 'ai', text: 'Cześć! Widzę treści Twojej strony. Co chcesz poprawić, przepisać lub wygenerować? Możesz też poprosić mnie o sugestie.' },
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
      await api.chatStream(projectId, text, 4, (chunk) => {
        aiText += chunk;
        setMessages(prev => { const n = [...prev]; n[n.length - 1] = { role: 'ai', text: aiText }; return n; });
      });
    } catch {
      setMessages(prev => { const n = [...prev]; n[n.length - 1] = { role: 'ai', text: 'Błąd połączenia z AI.' }; return n; });
    } finally {
      setSending(false);
    }
  };

  const suggestions = ['Popraw nagłówek hero', 'Napisz mocniejsze CTA', 'Skróć opisy sekcji', 'Dodaj statistyki'];

  return (
    <div style={{ position: 'fixed', right: 24, bottom: 90, width: 380, height: 480, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 16, boxShadow: '0 20px 48px rgba(15,23,42,.18)', display: 'flex', flexDirection: 'column', zIndex: 70, fontFamily: 'Inter, sans-serif' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #F1F5F9', display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: 'linear-gradient(135deg, #6366F1, #EC4899)', display: 'grid', placeItems: 'center' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
        </div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#0F172A' }}>AI asystent</div>
          <div style={{ fontSize: 10.5, color: '#94A3B8' }}>Edytor treści · Krok 4</div>
        </div>
        <button onClick={onClose} style={{ marginLeft: 'auto', width: 28, height: 28, border: 'none', background: 'transparent', cursor: 'pointer', borderRadius: 6, display: 'grid', placeItems: 'center', color: '#94A3B8', fontSize: 16 }}
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
            placeholder="Co chcesz poprawić?"
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

// ─── Undo/Redo types ──────────────────────────────────────────────────────────

type SlotsSnapshot = { id: string; slots_json: Record<string, unknown> | null }[];

// ─── Regenerate panel (per section, from hover action) ────────────────────────

function RegenPanel({ sectionId, onSubmit, onClose }: { sectionId: string; onSubmit: (instruction: string) => void; onClose: () => void }) {
  const [inst, setInst] = useState('');
  return (
    <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 80, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 16, boxShadow: '0 20px 48px rgba(15,23,42,.18)', padding: '20px 24px', width: 400, fontFamily: 'Inter, sans-serif' }}>
      <div style={{ fontSize: 14, fontWeight: 600, color: '#0F172A', marginBottom: 12 }}>Regeneruj sekcję ({sectionId.slice(0, 8)}…)</div>
      <input type="text" value={inst} onChange={e => setInst(e.target.value)} placeholder="Dodatkowa instrukcja (opcjonalnie)"
        style={{ width: '100%', padding: '8px 12px', border: '1px solid #E2E8F0', borderRadius: 8, fontSize: 13, fontFamily: 'inherit', outline: 'none', boxSizing: 'border-box', marginBottom: 12 }}
        onKeyDown={e => { if (e.key === 'Enter') { onSubmit(inst.trim()); onClose(); } if (e.key === 'Escape') onClose(); }}
        autoFocus />
      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button onClick={onClose} style={{ padding: '7px 14px', border: '1px solid #E2E8F0', background: 'transparent', borderRadius: 8, fontSize: 13, cursor: 'pointer', color: '#64748B' }}>Anuluj</button>
        <button onClick={() => { onSubmit(inst.trim()); onClose(); }} style={{ padding: '7px 16px', background: '#6366F1', color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>Regeneruj AI</button>
      </div>
    </div>
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function Step4Content() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { sections, brand, updateSection, regenerateSection, generateContent, removeSection, reorderSections, isGenerating, error, setError } = useLabStore();

  const [viewport, setViewport] = useState<Viewport>('desktop');
  const [hoveredSection, setHoveredSection] = useState<string | null>(null);
  const [regenPanel, setRegenPanel] = useState<string | null>(null); // sectionId
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const [typoOpen, setTypoOpen] = useState(false);

  // Typo local state (init from brand)
  const [density, setDensity] = useState(brand.density === 'compact' ? 2 : brand.density === 'spacious' ? 4 : 3);
  const [headingFont, setHeadingFont] = useState(brand.fontHeading || 'Instrument Serif');
  const [bodyFont, setBodyFont] = useState(brand.fontBody || 'Inter');

  const { toast, show: showToast } = useToast();
  const historyRef = useRef<{ past: SlotsSnapshot[]; future: SlotsSnapshot[] }>({ past: [], future: [] });

  const snapshots = (): SlotsSnapshot => sections.map(s => ({ id: s.id, slots_json: s.slots_json ?? null }));

  const pushHistory = useCallback(() => {
    historyRef.current.past.push(snapshots());
    if (historyRef.current.past.length > 30) historyRef.current.past.shift();
    historyRef.current.future = [];
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sections]);

  const applySnapshot = useCallback((snap: SlotsSnapshot) => {
    for (const entry of snap) {
      const s = sections.find(x => x.id === entry.id);
      if (s && JSON.stringify(s.slots_json) !== JSON.stringify(entry.slots_json)) {
        updateSection(entry.id, { slots_json: entry.slots_json });
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sections, updateSection]);

  const undo = useCallback(() => {
    const h = historyRef.current;
    if (!h.past.length) return;
    const prev = h.past.pop()!;
    h.future.push(snapshots());
    applySnapshot(prev);
    showToast('↶ Cofnięto');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [applySnapshot, showToast]);

  const redo = useCallback(() => {
    const h = historyRef.current;
    if (!h.future.length) return;
    const next = h.future.pop()!;
    h.past.push(snapshots());
    applySnapshot(next);
    showToast('↷ Przywrócono');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [applySnapshot, showToast]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const meta = e.metaKey || e.ctrlKey;
      if (meta && e.key === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
      if (meta && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) { e.preventDefault(); redo(); }
      if (e.key === 'Escape') { setRegenPanel(null); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [undo, redo]);

  // Scaled canvas
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerW, setContainerW] = useState(1200);
  useLayoutEffect(() => {
    const update = () => { if (containerRef.current) setContainerW(containerRef.current.clientWidth); };
    update();
    const ro = new ResizeObserver(update);
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);
  const stageWidth = VP_WIDTHS[viewport];
  const fitScale = Math.min(1, (containerW - 40) / stageWidth);

  const handleSlotUpdate = useCallback((sectionId: string, key: string, newValue: unknown) => {
    const section = sections.find(s => s.id === sectionId);
    if (!section || !section.slots_json) return;
    pushHistory();
    const updatedSlots = { ...(section.slots_json as Record<string, unknown>), [key]: newValue };
    updateSection(sectionId, { slots_json: updatedSlots });
  }, [sections, updateSection, pushHistory]);

  const handleRegenerate = useCallback(async (sectionId: string, instruction: string) => {
    pushHistory();
    await regenerateSection(sectionId, instruction || undefined);
    showToast('Sekcja zregenerowana');
  }, [regenerateSection, pushHistory, showToast]);

  const handleGenerateAll = useCallback(async () => {
    pushHistory();
    await generateContent();
    showToast('Treści wygenerowane');
  }, [generateContent, pushHistory, showToast]);

  const handleMoveSection = useCallback(async (sectionId: string, dir: 'up' | 'down') => {
    const idx = sections.findIndex(s => s.id === sectionId);
    if (idx < 0) return;
    const target = dir === 'up' ? idx - 1 : idx + 1;
    if (target < 0 || target >= sections.length) return;
    const newOrder = [...sections];
    [newOrder[idx], newOrder[target]] = [newOrder[target], newOrder[idx]];
    await reorderSections(newOrder.map(s => s.id));
    showToast(dir === 'up' ? '↑ Sekcja przesunięta' : '↓ Sekcja przesunięta');
  }, [sections, reorderSections, showToast]);

  const handleDeleteSection = useCallback(async (sectionId: string) => {
    if (!confirm('Usunąć tę sekcję?')) return;
    await removeSection(sectionId);
    showToast('Sekcja usunięta');
  }, [removeSection, showToast]);

  const typo = makeTypo(density, headingFont, bodyFont);
  const hasContent = sections.some(s => s.slots_json && Object.keys(s.slots_json).length > 0);

  return (
    <div className="flex flex-col h-full overflow-hidden" style={{ minHeight: 'calc(100vh - 96px)' }}>
      {/* Topbar */}
      <div style={{ height: 64, borderBottom: '1px solid #F1F5F9', background: '#fff', display: 'flex', alignItems: 'center', padding: '0 24px', gap: 12, position: 'sticky', top: 0, zIndex: 40, flexShrink: 0 }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: '#6366F1', textTransform: 'uppercase', letterSpacing: 0.8 }}>● Krok 4 · Treści</div>

        <TypoPopover open={typoOpen} setOpen={setTypoOpen} density={density} setDensity={setDensity} headingFont={headingFont} setHeadingFont={setHeadingFont} bodyFont={bodyFont} setBodyFont={setBodyFont} />

        {/* Undo/Redo */}
        <div style={{ display: 'inline-flex', gap: 2, padding: 3, background: '#F1F5F9', borderRadius: 8 }}>
          <button onClick={undo} disabled={historyRef.current.past.length === 0} title="Cofnij (Ctrl+Z)"
            style={{ width: 30, height: 28, border: 'none', background: 'transparent', cursor: 'pointer', borderRadius: 6, color: '#64748B', display: 'grid', placeItems: 'center', opacity: historyRef.current.past.length ? 1 : 0.35 }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M9 14l-4-4 4-4"/><path d="M5 10h9a6 6 0 010 12h-2"/></svg>
          </button>
          <button onClick={redo} disabled={historyRef.current.future.length === 0} title="Przywróć (Ctrl+Shift+Z)"
            style={{ width: 30, height: 28, border: 'none', background: 'transparent', cursor: 'pointer', borderRadius: 6, color: '#64748B', display: 'grid', placeItems: 'center', opacity: historyRef.current.future.length ? 1 : 0.35 }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M15 14l4-4-4-4"/><path d="M19 10h-9a6 6 0 000 12h2"/></svg>
          </button>
        </div>

        {/* Viewport switcher */}
        <div style={{ display: 'inline-flex', gap: 2, padding: 3, background: '#F1F5F9', borderRadius: 9 }}>
          {(['desktop', 'tablet', 'mobile'] as const).map(v => (
            <button key={v} onClick={() => setViewport(v)} title={`${v} — ${VP_WIDTHS[v]}px`}
              style={{ padding: '5px 10px', border: 'none', borderRadius: 7, background: viewport === v ? '#fff' : 'transparent', color: viewport === v ? '#0F172A' : '#64748B', fontSize: 12, fontWeight: 500, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6, boxShadow: viewport === v ? '0 1px 2px rgba(15,23,42,.08)' : 'none' }}>
              {v === 'desktop' ? (<><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>Desktop</>) : v === 'tablet' ? (<><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="5" y="2" width="14" height="20" rx="2"/></svg>Tablet</>) : (<><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="6" y="2" width="12" height="20" rx="2"/></svg>Mobile</>)}
            </button>
          ))}
        </div>

        <div style={{ flex: 1 }} />

        <button onClick={handleGenerateAll} disabled={isGenerating}
          style={{ padding: '7px 14px', background: '#F1F5F9', border: '1px solid #E2E8F0', borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: 'pointer', color: '#475569', opacity: isGenerating ? 0.6 : 1 }}>
          {isGenerating ? 'Generowanie…' : 'Regeneruj wszystko'}
        </button>
      </div>

      {/* Instruction strip */}
      <div style={{ background: '#fff', borderBottom: '1px solid #F1F5F9', padding: '8px 24px', display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
        <div style={{ fontSize: 13, color: '#64748B' }}>
          Kliknij dowolny tekst aby go edytować. Najedź na sekcję by zobaczyć akcje.
          {viewport !== 'desktop' && (
            <span style={{ marginLeft: 10, padding: '3px 9px', background: '#FEF3C7', color: '#92400E', borderRadius: 999, fontSize: 11, fontWeight: 600 }}>
              ✎ Tryb {viewport === 'mobile' ? 'Mobile' : 'Tablet'}
            </span>
          )}
        </div>
      </div>

      {/* Canvas */}
      <div style={{ flex: 1, overflow: 'auto', padding: '24px 24px 120px', background: '#F5F6FA' }}>
        {/* Loading states */}
        {isGenerating && sections.length === 0 && (
          <div className="text-center py-20">
            <div className="inline-flex items-center gap-3 bg-white border border-gray-200 px-6 py-4 rounded-2xl shadow-sm">
              <svg className="animate-spin w-5 h-5 text-indigo-500" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
              <span className="text-sm font-medium text-gray-600">AI generuje treści…</span>
            </div>
          </div>
        )}
        {!isGenerating && error && sections.length === 0 && (
          <div className="text-center py-12 space-y-4">
            <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-5 py-3 rounded-xl border border-red-200">
              <span>✗</span><span className="text-sm">{error}</span>
            </div>
            <div>
              <button onClick={() => { setError(null); handleGenerateAll(); }} className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700">
                Spróbuj ponownie
              </button>
            </div>
          </div>
        )}
        {sections.length === 0 && !isGenerating && !error && (
          <div className="text-center py-20 text-gray-400 text-sm">
            <p>Brak sekcji. Wróć do kroku 3 aby wygenerować strukturę.</p>
          </div>
        )}
        {sections.length > 0 && !hasContent && !isGenerating && (
          <div className="text-center py-12 text-gray-400 text-sm space-y-4">
            <p>Sekcje gotowe — wygeneruj treści AI.</p>
            <button onClick={handleGenerateAll} className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700">
              Generuj treści AI
            </button>
          </div>
        )}
        {isGenerating && sections.length > 0 && (
          <div className="text-center py-4 mb-4">
            <div className="inline-flex items-center gap-3 bg-white border border-gray-200 px-5 py-3 rounded-xl shadow-sm">
              <svg className="animate-spin w-4 h-4 text-indigo-500" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
              <span className="text-sm font-medium text-gray-600">AI regeneruje…</span>
            </div>
          </div>
        )}

        {/* Scaled canvas */}
        {sections.length > 0 && (
          <div ref={containerRef} style={{ width: '100%', position: 'relative' }}>
            <div style={{ width: stageWidth, transformOrigin: 'top left', transform: `scale(${fitScale})`, margin: '0 auto', height: 'auto' }}>
              <div style={{ width: stageWidth, background: '#fff', borderRadius: 16, overflow: 'hidden', boxShadow: '0 4px 20px rgba(15,23,42,.08), 0 0 0 1px rgba(15,23,42,.06)' }}>
                {sections.map((section, idx) => {
                  const Renderer = section.slots_json ? getRenderer(section.block_code) : null;
                  return (
                    <div key={section.id} style={{ position: 'relative' }}
                      onMouseEnter={() => setHoveredSection(section.id)}
                      onMouseLeave={() => setHoveredSection(prev => prev === section.id ? null : prev)}>
                      {Renderer ? (
                        <Renderer
                          section={section}
                          brand={brand}
                          typo={typo}
                          onSlotUpdate={(key, val) => handleSlotUpdate(section.id, key, val)}
                        />
                      ) : (
                        <PlaceholderSection section={section} />
                      )}
                      {hoveredSection === section.id && (
                        <SectionHoverActions
                          scale={fitScale}
                          label={section.name || section.block_code}
                          canUp={idx > 0}
                          canDown={idx < sections.length - 1}
                          onUp={() => handleMoveSection(section.id, 'up')}
                          onDown={() => handleMoveSection(section.id, 'down')}
                          onDel={() => handleDeleteSection(section.id)}
                          onRegen={() => setRegenPanel(section.id)}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Chat panel */}
      {aiChatOpen && projectId && (
        <AiChatPanel projectId={projectId} onClose={() => setAiChatOpen(false)} />
      )}

      {/* AI FAB */}
      {!aiChatOpen && (
        <button onClick={() => setAiChatOpen(true)}
          style={{ position: 'fixed', right: 24, bottom: 80, zIndex: 60, padding: '12px 18px', background: 'linear-gradient(135deg, #6366F1, #EC4899)', color: '#fff', border: 'none', borderRadius: 999, fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8, boxShadow: '0 12px 30px rgba(99,102,241,.35), 0 4px 10px rgba(15,23,42,.15)', fontFamily: 'Inter, sans-serif' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
          AI asystent
        </button>
      )}

      {/* Regenerate panel */}
      {regenPanel && (
        <>
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,.4)', zIndex: 75 }} onClick={() => setRegenPanel(null)} />
          <RegenPanel sectionId={regenPanel} onSubmit={inst => handleRegenerate(regenPanel, inst)} onClose={() => setRegenPanel(null)} />
        </>
      )}

      {/* ElementToolbar — floating formatting toolbar */}
      <ElementToolbar />

      {/* Toast */}
      {toast && (
        <div style={{ position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)', padding: '10px 18px', background: '#0F172A', color: '#fff', borderRadius: 10, fontSize: 13, fontWeight: 500, zIndex: 100, boxShadow: '0 8px 24px rgba(15,23,42,.3)', fontFamily: 'Inter, sans-serif' }}>{toast}</div>
      )}

      {/* Bottom nav */}
      <div className="bg-white border-t border-gray-100 px-6 py-3 flex justify-between flex-shrink-0">
        <button onClick={() => navigate(`/lab/${projectId}/step/3`)} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">
          ← Wstecz
        </button>
        <button onClick={() => navigate(`/lab/${projectId}/step/5`)} disabled={sections.length === 0}
          className="px-6 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors">
          Dalej → Kreacja wizualna
        </button>
      </div>
    </div>
  );
}
