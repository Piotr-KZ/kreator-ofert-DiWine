/**
 * SectionRenderers — shared section rendering components.
 * Używane przez Step4Content (edycja treści) i Step5Visual (wizualizacja).
 */

import { useState, useRef, useEffect, createElement } from "react";
import type { Section } from "@/store/labStore";
import type { Brand } from "@/types/lab";

// ─── Typography ───────────────────────────────────────────────────────────────

export const DENSITY_SCALE: Record<number, { body: number; scale: number; lh: number; sp: number }> = {
  1: { body: 14, scale: 1.20, lh: 1.40, sp: 0.70 },
  2: { body: 15, scale: 1.22, lh: 1.45, sp: 0.85 },
  3: { body: 16, scale: 1.25, lh: 1.50, sp: 1.00 },
  4: { body: 17, scale: 1.28, lh: 1.55, sp: 1.20 },
  5: { body: 18, scale: 1.30, lh: 1.60, sp: 1.40 },
};

export const DENSITY_LABELS: Record<number, string> = {
  1: 'Kompakt', 2: 'Zwarty', 3: 'Komfort', 4: 'Przestronny', 5: 'Luźny',
};

export type Typo = {
  hf: string; bf: string; body: number; lh: number; sp: number;
  ey: number; h3: number; h2: number; h1: number;
};

export function makeTypo(density: number, hf: string, bf: string): Typo {
  const d = DENSITY_SCALE[density] || DENSITY_SCALE[3];
  const b = d.body, s = d.scale;
  return {
    hf, bf, body: b, lh: d.lh, sp: d.sp,
    ey: Math.round(b * 0.8),
    h3: Math.round(b * s * s),
    h2: Math.round(b * s * s * s),
    h1: Math.round(b * s * s * s * s),
  };
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

export function isDark(hex: string): boolean {
  const c = (hex || '').replace('#', '');
  if (c.length < 6) return false;
  return (0.299 * parseInt(c.slice(0, 2), 16) + 0.587 * parseInt(c.slice(2, 4), 16) + 0.114 * parseInt(c.slice(4, 6), 16)) < 128;
}

export function str(v: unknown): string { return v == null ? '' : String(v); }
export function arr<T>(v: unknown): T[] { return Array.isArray(v) ? (v as T[]) : []; }

export function gStr(s: Record<string, unknown>, keys: string[]): [string, string] {
  for (const k of keys) if (s[k] !== undefined && s[k] !== null) return [k, str(s[k])];
  return ['', ''];
}
export function gArr<T>(s: Record<string, unknown>, keys: string[]): [string, T[]] {
  for (const k of keys) if (Array.isArray(s[k])) return [k, s[k] as T[]];
  return ['', []];
}

export function ctaBg(brand: Brand): string {
  if (brand.ctaIsGradient) return `linear-gradient(135deg, ${brand.ctaColor}, ${brand.ctaColor2})`;
  return brand.ctaColor as string;
}

// ─── InlineEdit — contentEditable z obsługą HTML ──────────────────────────────

interface InlineEditProps {
  value: string;
  onChange: (v: string) => void;
  tag?: string;
  style?: React.CSSProperties;
  multiline?: boolean;
}

export function InlineEdit({ value, onChange, tag = 'span', style, multiline = false }: InlineEditProps) {
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

export interface RP {
  section: Section;
  brand: Brand;
  typo: Typo;
  onSlotUpdate: (key: string, value: unknown) => void;
}

export type RendererFn = (props: RP) => React.ReactNode;

// ─── NavSection ───────────────────────────────────────────────────────────────

export function NavSection({ section, brand, typo, onSlotUpdate }: RP) {
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

export function HeroSection({ section, brand, typo, onSlotUpdate }: RP) {
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

// ─── FeaturesSection (RO, KR, CF, PB, PR, FI, OF, ...) ───────────────────────

export function FeaturesSection({ section, brand, typo, onSlotUpdate }: RP) {
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
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5" /></svg>
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

export function TestimonialsSection({ section, brand, typo, onSlotUpdate }: RP) {
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

// ─── CtaSection (CT) ──────────────────────────────────────────────────────────

export function CtaSection({ section, brand, typo, onSlotUpdate }: RP) {
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

// ─── FooterSection (FO) ───────────────────────────────────────────────────────

export function FooterSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#0F172A';
  const [logoKey, logoVal] = gStr(s, ['logo_text', 'brand_name', 'company_name', 'logo']);
  const [descKey, descVal] = gStr(s, ['description', 'tagline', 'desc', 'subtitle']);
  const [copyKey, copyVal] = gStr(s, ['copyright', 'copy', 'footer_note']);
  const [colsKey, cols] = gArr<{ title: string; links: string[] }>(s, ['columns', 'cols', 'sections']);

  return (
    <div style={{ padding: '80px 80px 32px', background: bg, color: '#CBD5E1' }}>
      <div style={{ display: 'grid', gridTemplateColumns: cols.length > 0 ? `1.2fr ${cols.slice(0, 3).map(() => '1fr').join(' ')}` : '1fr', gap: 60, marginBottom: 60 }}>
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

// ─── GenericSection ───────────────────────────────────────────────────────────

export function GenericSection({ section, brand, typo, onSlotUpdate }: RP) {
  const s = section.slots_json || {};
  const bg = (section.bgColor as string) || '#FFFFFF';
  const dark = isDark(bg);
  const tc = dark ? '#FFFFFF' : '#0F172A';
  const bc = dark ? '#CBD5E1' : '#475569';

  const [preTKey, preTVal] = gStr(s, ['pre_title', 'eyebrow', 'tagline', 'label']);
  const [titleKey, titleVal] = gStr(s, ['title', 'heading', 'h1', 'h2']);
  const [bodyKey, bodyVal] = gStr(s, ['subtitle', 'description', 'body', 'text', 'paragraph', 'content']);
  const [cta1Key, cta1Val] = gStr(s, ['cta_primary', 'cta_text', 'cta', 'button_text']);

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

export function PlaceholderSection({ section }: { section: Section }) {
  return (
    <div style={{ padding: '60px 80px', background: '#FAFBFC', textAlign: 'center' }}>
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 12px', background: '#fff', border: '1px dashed #CBD5E1', borderRadius: 8, marginBottom: 12 }}>
        <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 11, fontWeight: 700, color: '#6366F1' }}>{section.block_code}</span>
        <span style={{ fontSize: 11, color: '#94A3B8' }}>· szablon w przygotowaniu</span>
      </div>
      <div style={{ fontSize: 22, fontWeight: 600, color: '#0F172A', marginBottom: 8 }}>{section.name || section.block_code}</div>
      <div style={{ fontSize: 13, color: '#64748B', maxWidth: 440, margin: '0 auto' }}>Tę sekcję wypełnij w etapie Treści lub kliknij "AI" aby wygenerować treść.</div>
    </div>
  );
}

// ─── SECTION_RENDERERS map ────────────────────────────────────────────────────

export const NAV_CODES = new Set(['NA1', 'NA2', 'NA3']);
export const HERO_CODES = new Set(['HE1', 'HE2', 'HE3', 'HE4', 'HE5']);
export const FEAT_CODES = new Set(['RO1', 'RO2', 'KR1', 'KR2', 'CF1', 'CF2', 'PB1', 'PB2', 'PB3', 'PR1', 'PR2', 'FI1', 'FI2', 'FI3', 'FA1', 'OB1', 'LO1', 'ST1', 'ZE1', 'ZE2', 'CE1', 'RE1', 'KO1', 'OF1', 'OF2']);
export const TESTI_CODES = new Set(['OP1', 'OP2']);
export const CTA_CODES = new Set(['CT1', 'CT2', 'CT3']);
export const FOOTER_CODES = new Set(['FO1']);

export function getRenderer(blockCode: string): RendererFn {
  if (NAV_CODES.has(blockCode)) return NavSection;
  if (HERO_CODES.has(blockCode)) return HeroSection;
  if (TESTI_CODES.has(blockCode)) return TestimonialsSection;
  if (CTA_CODES.has(blockCode)) return CtaSection;
  if (FOOTER_CODES.has(blockCode)) return FooterSection;
  if (FEAT_CODES.has(blockCode)) return FeaturesSection;
  return GenericSection;
}
