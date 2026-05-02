import React from "react";
// Sekcje strony — per-element edycja + overrides

// Context pozwala Editable zarejestrować focus u parenta (App)
const EditCtx = React.createContext(null);

// Stock images for different section types (Unsplash, free license)
const STOCK_IMAGES = {
  hero: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=75',
  about: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=900&q=75',
  solution: 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=900&q=75',
  portfolio: [
    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=70',
    'https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&q=70',
    'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&q=70',
  ],
  team: [
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=70',
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=70',
    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&q=70',
    'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=70',
  ],
  offer_hero: 'https://images.unsplash.com/photo-1516594915697-87eb3b1c14ea?w=1200&q=75',
  offer_wine: 'https://images.unsplash.com/photo-1474722883778-792e7990302f?w=900&q=75',
  offer_gift: 'https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=900&q=75',
  offer_table: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=900&q=75',
};

// Clickable image with hover overlay — opens ImagePicker on click
// Hidden when ctx.hideImages is true (used in Step 4 to hide photos)
function SectionImg({ src, fallback, alt, style, sectionId, field }) {
  const ctx = React.useContext(EditCtx);
  if (ctx?.hideImages) return null;
  const rawSrc = typeof src === 'object' && src !== null ? (src.text || src.url || src.src || '') : (src || '');
  const imgSrc = rawSrc || fallback;
  const [hover, setHover] = React.useState(false);
  return (
    <div
      data-wiz-img="true"
      style={{ ...style, position: 'relative', overflow: 'hidden', cursor: 'pointer' }}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      onMouseDown={(e) => e.stopPropagation()}
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
        if (ctx?.select) ctx.select(null);
        setTimeout(() => ctx?.onImageClick?.({ sectionId, field, current: imgSrc }), 50);
      }}>
      {imgSrc ? <img src={imgSrc} alt={alt || ''} style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}/> : <div style={{ width: '100%', height: '100%', background: '#E2E8F0', display: 'grid', placeItems: 'center', color: '#94A3B8' }}><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 21"/></svg></div>}
      {hover && (
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,.25)', display: 'grid', placeItems: 'center' }}>
          <span style={{ padding: '6px 12px', background: 'rgba(0,0,0,.7)', color: '#fff', borderRadius: 8, fontSize: 12, fontWeight: 600 }}>Zmien zdjecie</span>
        </div>
      )}
    </div>
  );
}

// Wspólny hook — zwraca stan overrides dla danego pola i setter
function useFieldOverrides(sectionId, elId) {
  const ctx = React.useContext(EditCtx);
  const ov = ctx.getOv ? ctx.getOv(sectionId, elId) : ((ctx.overrides[sectionId] && ctx.overrides[sectionId][elId]) || {});
  const setOv = (patch) => ctx.patchOverride(sectionId, elId, patch);
  const removeOv = () => ctx.removeOverride(sectionId, elId);
  const copyEl = () => ctx.copyOverride(sectionId, elId);
  return { ov, setOv, removeOv, copyEl };
}

function Editable({ tag: Tag = 'span', value, onChange, style, placeholder, multiline, sectionId, elId, editable = true, hidden, color, fontFamily, fontSize, fontWeight }) {
  const ref = React.useRef(null);
  const [editing, setEditing] = React.useState(false);
  const ctx = React.useContext(EditCtx);
  const { ov, setOv, removeOv, copyEl } = useFieldOverrides(sectionId, elId);

  // Sync text content
  React.useEffect(() => {
    if (ref.current && !editing && ref.current.innerText !== value) {
      ref.current.innerText = value || '';
    }
  }, [value, editing]);

  if (ov.deleted) return null;
  if (hidden) return null;

  const mergedStyle = {
    ...style,
    fontFamily: ov.fontFamily ? `'${ov.fontFamily}', sans-serif` : (fontFamily || style.fontFamily),
    fontSize: ov.fontSize ? Math.round((fontSize || style.fontSize) * ov.fontSize) : (fontSize || style.fontSize),
    fontWeight: ov.fontWeight || fontWeight || style.fontWeight,
    fontStyle: ov.italic ? 'italic' : (style.fontStyle || 'normal'),
    textDecoration: ov.underline ? 'underline' : (style.textDecoration || 'none'),
    color: ov.color || color || style.color,
    textAlign: ov.align || style.textAlign,
    cursor: editable ? 'text' : 'default',
    resize: 'both' as const,
    overflow: 'auto' as const,
    minWidth: 50,
    minHeight: 20,
    display: 'block',
    outline: ctx.selected && ctx.selected.sectionId === sectionId && ctx.selected.elId === elId ? '2px solid #6366F1' : 'none',
    outlineOffset: 2,
    borderRadius: 3,
    transition: 'outline-color .1s',
  };

  const selectMe = (e) => {
    e.stopPropagation();
    const rect = ref.current.getBoundingClientRect();
    ctx.select({ sectionId, elId, rect, onPatch: setOv, onRemove: removeOv, onCopy: copyEl, currentOv: ov, tag: Tag });
  };

  return (
    <Tag
      ref={ref}
      contentEditable={editable}
      suppressContentEditableWarning
      onFocus={(e) => { setEditing(true); selectMe(e); }}
      onClick={selectMe}
      onBlur={(e) => { setEditing(false); onChange(e.currentTarget.innerText); }}
      onKeyDown={(e) => {
        if (!multiline && e.key === 'Enter') { e.preventDefault(); e.currentTarget.blur(); }
        if (e.key === 'Escape') { e.currentTarget.blur(); }
      }}
      style={mergedStyle}
      data-placeholder={placeholder}
    >{value || ''}</Tag>
  );
}

function H1({ value, onChange, typo, color, sectionId, elId }) {
  return <Editable tag="h1" value={value} onChange={onChange} sectionId={sectionId} elId={elId}
    style={{ margin: 0, fontFamily: `'${typo.headingFont}', serif`, fontSize: typo.h1, fontWeight: 700, lineHeight: 1.1, letterSpacing: '-0.02em', color, display: 'block' }}/>;
}
function H2({ value, onChange, typo, color, sectionId, elId }) {
  return <Editable tag="h2" value={value} onChange={onChange} sectionId={sectionId} elId={elId}
    style={{ margin: 0, fontFamily: `'${typo.headingFont}', serif`, fontSize: typo.h2, fontWeight: 700, lineHeight: 1.15, letterSpacing: '-0.015em', color, display: 'block' }}/>;
}
function H3({ value, onChange, typo, color, sectionId, elId }) {
  return <Editable tag="h3" value={value} onChange={onChange} sectionId={sectionId} elId={elId}
    style={{ margin: 0, fontFamily: `'${typo.headingFont}', serif`, fontSize: typo.h3, fontWeight: 600, lineHeight: 1.25, color, display: 'block' }}/>;
}
function Body({ value, onChange, typo, color, sectionId, elId }) {
  return <Editable tag="p" value={value} onChange={onChange} multiline sectionId={sectionId} elId={elId}
    style={{ margin: 0, fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: typo.body, lineHeight: typo.lineHeight, color, fontWeight: 400, display: 'block' }}/>;
}
function Eyebrow({ value, onChange, typo, color, sectionId, elId }) {
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '5px 12px', background: (color || '#6366F1') + '20', borderRadius: 999 }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: color || '#6366F1', flexShrink: 0 }}/>
      <Editable tag="span" value={value} onChange={onChange} sectionId={sectionId} elId={elId}
        style={{ margin: 0, fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: typo.eyebrow, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: color || '#6366F1', display: 'inline' }}/>
    </div>
  );
}
function CTAButton({ value, onChange, typo, brand, variant = 'primary', dark, sectionId, elId }) {
  const bg = variant === 'primary' ? (brand.ctaGradient ? `linear-gradient(135deg, ${brand.cta}, ${brand.cta2})` : brand.cta) : 'transparent';
  const color = variant === 'primary' ? '#fff' : (dark ? '#fff' : '#0F172A');
  const border = variant === 'primary' ? 'none' : `1px solid ${dark ? 'rgba(255,255,255,.3)' : '#E2E8F0'}`;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 10,
      padding: `${Math.round(typo.body * 0.75)}px ${Math.round(typo.body * 1.5)}px`,
      background: bg, color, border, borderRadius: 999,
      boxShadow: variant === 'primary' ? '0 1px 2px rgba(31,41,55,.08)' : 'none',
      fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: typo.body, fontWeight: 600, cursor: 'text',
    }}>
      <Editable tag="span" value={value} onChange={onChange} sectionId={sectionId} elId={elId}
        style={{ display: 'inline', color: 'inherit', fontSize: typo.body, fontWeight: 600 }}/>
      <span>→</span>
    </span>
  );
}

/* ===== SECTION RENDERERS ===== */

function txt(v) { return typeof v === 'object' && v !== null ? (v.text || v.name || v.label || '') : (v || ''); }

function NavSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const links = f.links || [];
  const setLink = (i, v) => { const next = [...links]; next[i] = typeof links[i] === 'object' ? { ...links[i], text: v } : v; update({ fields: { ...f, links: next } }); };
  return (
    <div style={{ padding: '28px 80px', display: 'flex', alignItems: 'center', gap: 40, background: s.bg || brand.bg, borderBottom: '1px solid rgba(0,0,0,.06)' }}>
      <Editable tag="div" value={f.logo || ''} onChange={v => setField('logo', v)} sectionId={s.id} elId="logo"
        style={{ fontFamily: `'${typo.headingFont}', serif`, fontSize: Math.round(typo.h3 * 0.7), fontWeight: 700, color: '#0F172A', letterSpacing: '-0.01em' }}/>
      <div style={{ flex: 1, display: 'flex', gap: 32, justifyContent: 'center' }}>
        {links.map((l, i) => (
          <Editable key={i} tag="span" value={txt(l)} onChange={v => setLink(i, v)} sectionId={s.id} elId={`link-${i}`}
            style={{ fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: Math.round(typo.body * 0.95), color: '#334155', fontWeight: 500 }}/>
        ))}
      </div>
      <CTAButton value={f.cta || ''} onChange={v => setField('cta', v)} typo={typo} brand={brand} sectionId={s.id} elId="cta"/>
    </div>
  );
}

function HeroSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ padding: `${120 * typo.spacing}px 80px`, background: s.bg || brand.bg, display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 80, alignItems: 'center' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 * typo.spacing }}>
        <Eyebrow value={f.eyebrow} onChange={v => setField('eyebrow', v)} typo={typo} color="#B45309" sectionId={s.id} elId="eyebrow"/>
        <H1 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
        <Body value={f.body} onChange={v => setField('body', v)} typo={typo} color="#334155" sectionId={s.id} elId="body"/>
        <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
          <CTAButton value={f.cta} onChange={v => setField('cta', v)} typo={typo} brand={brand} sectionId={s.id} elId="cta"/>
          <CTAButton value={f.cta2} onChange={v => setField('cta2', v)} typo={typo} brand={brand} variant="ghost" sectionId={s.id} elId="cta2"/>
        </div>
      </div>
      <SectionImg src={f.image} fallback={STOCK_IMAGES.hero} alt={f.heading || ''} sectionId={s.id} field="image"
        style={{ aspectRatio: '4/5', borderRadius: 24 }}/>
    </div>
  );
}

function LogosSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const logos = f.logos || [];
  const setLogo = (i, v) => { const next = [...logos]; next[i] = v; update({ fields: { ...f, logos: next } }); };
  return (
    <div style={{ padding: `${60 * typo.spacing}px 80px`, background: s.bg || brand.bg, textAlign: 'center' }}>
      <Editable tag="div" value={f.title || ''} onChange={v => setField('title', v)} sectionId={s.id} elId="title"
        style={{ fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: typo.eyebrow, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#64748B', marginBottom: 32, display: 'block' }}/>
      <div style={{ display: 'flex', gap: 48, justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }}>
        {logos.map((l, i) => (
          <Editable key={i} tag="span" value={txt(l)} onChange={v => setLogo(i, v)} sectionId={s.id} elId={`logo-${i}`}
            style={{ fontFamily: `'${typo.headingFont}', serif`, fontSize: Math.round(typo.h3 * 0.85), fontWeight: 500, color: '#94A3B8', fontStyle: 'italic' }}/>
        ))}
      </div>
    </div>
  );
}

function ProblemSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg, textAlign: 'center' }}>
      <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 * typo.spacing, alignItems: 'center' }}>
        <Eyebrow value={f.eyebrow} onChange={v => setField('eyebrow', v)} typo={typo} color="#C2410C" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
        <Body value={f.body} onChange={v => setField('body', v)} typo={typo} color="#475569" sectionId={s.id} elId="body"/>
      </div>
    </div>
  );
}

function SolutionSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const features = f.features || [];
  const setFeat = (i, k, v) => { const next = [...features]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, features: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', marginBottom: 56, display: 'flex', flexDirection: 'column', gap: 12, alignItems: 'center' }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color={brand.cta} sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(features.length, 3)}, 1fr)`, gap: 32 }}>
        {features.map((feat, i) => (
          <div key={i}>
            {feat.image && <SectionImg src={feat.image} fallback={undefined} alt={feat.title || ''} sectionId={s.id} field={`feat-${i}-image`}
              style={{ width: '100%', height: 280, borderRadius: 8, marginBottom: 20 }}/>}
            <H3 value={feat.title || ''} onChange={v => setFeat(i, 'title', v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`feat-${i}-title`}/>
            <div style={{ marginTop: 10 }}>
              <Body value={feat.body || ''} onChange={v => setFeat(i, 'body', v)} typo={typo} color="#475569" sectionId={s.id} elId={`feat-${i}-body`}/>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function WhyUsSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const points = f.points || [];
  const setPoint = (i, v) => { const next = [...points]; next[i] = typeof points[i] === 'object' ? { ...points[i], text: v } : v; update({ fields: { ...f, points: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center' }}>
      <SectionImg src={f.image} fallback={STOCK_IMAGES.about} alt={f.heading || ''} sectionId={s.id} field="image"
        style={{ width: '100%', height: 480, borderRadius: 8 }}/>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 * typo.spacing }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color={brand.cta} sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
        <Body value={f.body || ''} onChange={v => setField('body', v)} typo={typo} color="#475569" sectionId={s.id} elId="body"/>
        <div style={{ display: 'grid', gap: 14 }}>
          {points.map((p, i) => (
            <div key={i} style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
              <div style={{ width: 24, height: 24, borderRadius: '50%', background: brand.cta, display: 'grid', placeItems: 'center', flexShrink: 0, marginTop: 1 }}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
              <Body value={txt(p)} onChange={v => setPoint(i, v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`point-${i}`}/>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function OfferSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const tiers = f.tiers || [];
  const setTier = (i, k, v) => { const next = [...tiers]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, tiers: next } }); };
  const setItem = (ti, ii, v) => { const next = [...tiers]; const items = [...(next[ti].items || [])]; items[ii] = typeof items[ii] === 'object' ? { ...items[ii], text: v } : v; next[ti] = { ...next[ti], items }; update({ fields: { ...f, tiers: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px`, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(tiers.length, 3)}, 1fr)`, gap: 24 }}>
        {tiers.map((t, i) => (
          <div key={i} style={{ border: '1px solid #E2E8F0', borderRadius: 12, overflow: 'hidden', background: '#fff' }}>
            {/* Card image (if available) */}
            {t.image && <SectionImg src={t.image} fallback={undefined} alt={t.name || ''} sectionId={s.id} field={`tier-${i}-image`}
              style={{ width: '100%', height: 180 }}/>}
            <div style={{ padding: 28 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 6 }}>
                <H3 value={t.name || ''} onChange={v => setTier(i, 'name', v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`tier-${i}-name`}/>
                {t.price && <Editable tag="span" value={t.price || ''} onChange={v => setTier(i, 'price', v)} sectionId={s.id} elId={`tier-${i}-price`}
                  style={{ fontFamily: `'${typo.headingFont}'`, fontSize: Math.round(typo.body * 1.1), fontWeight: 500, fontStyle: 'italic', color: brand.cta }}/>}
              </div>
              <Body value={t.desc || ''} onChange={v => setTier(i, 'desc', v)} typo={typo} color="#94A3B8" sectionId={s.id} elId={`tier-${i}-desc`}/>
              <div style={{ borderTop: '1px solid #E2E8F0', paddingTop: 14, marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {(t.items || []).map((it, ii) => (
                  <Editable key={ii} tag="div" value={txt(it)} onChange={v => setItem(i, ii, v)} sectionId={s.id} elId={`tier-${i}-item-${ii}`}
                    style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: '#475569', display: 'block' }}/>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function OpinionsSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const testimonials = f.testimonials || [];
  const setT = (i, k, v) => { const next = [...testimonials]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, testimonials: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px`, display: 'flex', flexDirection: 'column', gap: 12, alignItems: 'center' }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color={brand.cta} sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(testimonials.length, 3)}, 1fr)`, gap: 28 }}>
        {testimonials.map((t, i) => (
          <div key={i} style={{ padding: 32, background: '#fff', borderRadius: 12, border: '1px solid #E2E8F0', display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Star rating */}
            <div style={{ display: 'flex', gap: 2, color: '#E0A84F' }}>
              {[1,2,3,4,5].map(n => <svg key={n} width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>)}
            </div>
            <div style={{ fontFamily: `'${typo.headingFont}'`, fontSize: 46, lineHeight: 0.5, color: brand.cta, marginBottom: 4 }}>"</div>
            <Editable tag="p" value={t.quote || ''} onChange={v => setT(i, 'quote', v)} multiline sectionId={s.id} elId={`test-${i}-quote`}
              style={{ margin: 0, fontFamily: `'${typo.bodyFont}'`, fontSize: Math.round(typo.body * 1.05), lineHeight: 1.6, color: '#0F172A', display: 'block' }}/>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 'auto' }}>
              <SectionImg src={t.image || t.photo} fallback={STOCK_IMAGES.team[i % STOCK_IMAGES.team.length]} alt={t.author || ''} sectionId={s.id} field={`test-${i}-image`}
                style={{ width: 44, height: 44, borderRadius: '50%', flexShrink: 0 }}/>
              <div>
                <Editable tag="div" value={t.author || ''} onChange={v => setT(i, 'author', v)} sectionId={s.id} elId={`test-${i}-author`}
                  style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, fontWeight: 600, color: '#0F172A', display: 'block' }}/>
                <Editable tag="div" value={t.role || ''} onChange={v => setT(i, 'role', v)} sectionId={s.id} elId={`test-${i}-role`}
                  style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: Math.round(typo.body * 0.85), color: '#94A3B8', display: 'block' }}/>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CtaSection({ s, brand, typo, update }) {
  const ctx = React.useContext(EditCtx);
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const bgImg = f.image || f.hero_image;
  return (
    <div style={{ padding: `${120 * typo.spacing}px 80px`, background: '#1F2937', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
      {/* Background image overlay (like mockup SecCTA) */}
      {bgImg && !ctx?.hideImages && <img src={bgImg} alt="" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.25 }}/>}
      {!bgImg && <div style={{ position: 'absolute', inset: 0, opacity: 0.15, background: `radial-gradient(circle at 20% 80%, ${brand.cta}44 0%, transparent 50%), radial-gradient(circle at 80% 20%, ${brand.cta2 || brand.cta}33 0%, transparent 50%)` }}/>}
      <div style={{ position: 'relative', maxWidth: 760, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 * typo.spacing, alignItems: 'center' }}>
        <Eyebrow value={f.eyebrow} onChange={v => setField('eyebrow', v)} typo={typo} color={brand.cta} sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color="#fff" sectionId={s.id} elId="heading"/>
        <Body value={f.body} onChange={v => setField('body', v)} typo={typo} color="rgba(255,255,255,.8)" sectionId={s.id} elId="body"/>
        <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
          <CTAButton value={f.cta || ''} onChange={v => setField('cta', v)} typo={typo} brand={brand} sectionId={s.id} elId="cta"/>
          {f.cta2 && <CTAButton value={f.cta2} onChange={v => setField('cta2', v)} typo={typo} brand={brand} variant="ghost" dark sectionId={s.id} elId="cta2"/>}
        </div>
      </div>
    </div>
  );
}

function FooterSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const cols = f.cols || [];
  const setCol = (i, k, v) => { const next = [...cols]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, cols: next } }); };
  const setLink = (ci, li, v) => { const next = [...cols]; const links = [...(next[ci].links || [])]; links[li] = typeof links[li] === 'object' ? { ...links[li], text: v } : v; next[ci] = { ...next[ci], links }; update({ fields: { ...f, cols: next } }); };
  return (
    <div style={{ padding: '80px 80px 32px', background: s.bg || '#0F172A', color: '#CBD5E1' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr 1fr', gap: 60, marginBottom: 60 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Editable tag="div" value={f.logo || ''} onChange={v => setField('logo', v)} sectionId={s.id} elId="logo"
            style={{ fontFamily: `'${typo.headingFont}', serif`, fontSize: typo.h3, fontWeight: 700, color: '#fff', letterSpacing: '-0.01em', display: 'block' }}/>
          <Body value={f.desc || ''} onChange={v => setField('desc', v)} typo={typo} color="#94A3B8" sectionId={s.id} elId="desc"/>
        </div>
        {cols.map((col, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Editable tag="div" value={col.title || ''} onChange={v => setCol(i, 'title', v)} sectionId={s.id} elId={`col-${i}-title`}
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.eyebrow, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#fff', marginBottom: 8, display: 'block' }}/>
            {(col.links || []).map((l, li) => (
              <Editable key={li} tag="div" value={txt(l)} onChange={v => setLink(i, li, v)} sectionId={s.id} elId={`col-${i}-link-${li}`}
                style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: Math.round(typo.body * 0.95), color: '#CBD5E1', display: 'block' }}/>
            ))}
          </div>
        ))}
      </div>
      <div style={{ paddingTop: 24, borderTop: '1px solid rgba(255,255,255,.1)' }}>
        <Editable tag="div" value={f.copyright || ''} onChange={v => setField('copyright', v)} sectionId={s.id} elId="copyright"
          style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: Math.round(typo.body * 0.85), color: '#64748B', textAlign: 'center', display: 'block' }}/>
      </div>
    </div>
  );
}

// ── HE1: Hero centered + stats — with background image ──
function HeroCenteredSection({ s, brand, typo, update }) {
  const ctx = React.useContext(EditCtx);
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const stats = f.stats || [];
  const setStat = (i, k, v) => { const next = [...stats]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, stats: next } }); };
  const heroImg = f.image || STOCK_IMAGES.hero;
  return (
    <div style={{ padding: `${120 * typo.spacing}px 80px`, textAlign: 'center', position: 'relative', overflow: 'hidden', minHeight: 520 }}>
      {/* Background image */}
      {!ctx?.hideImages && <img src={heroImg} alt="" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }}/>}
      {/* Dark overlay */}
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(15,23,42,.7) 0%, rgba(15,23,42,.55) 100%)' }}/>
      {/* Content */}
      <div style={{ position: 'relative', maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 24 * typo.spacing, alignItems: 'center' }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color={brand.cta} sectionId={s.id} elId="eyebrow"/>
        <H1 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#fff" sectionId={s.id} elId="heading"/>
        <Body value={f.body || ''} onChange={v => setField('body', v)} typo={typo} color="rgba(255,255,255,.85)" sectionId={s.id} elId="body"/>
        <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
          <CTAButton value={f.cta || ''} onChange={v => setField('cta', v)} typo={typo} brand={brand} sectionId={s.id} elId="cta"/>
          {f.cta2 && <CTAButton value={f.cta2} onChange={v => setField('cta2', v)} typo={typo} brand={brand} variant="ghost" dark sectionId={s.id} elId="cta2"/>}
        </div>
      </div>
      {stats.length > 0 && (
        <div style={{ position: 'relative', display: 'flex', justifyContent: 'center', gap: 60, marginTop: 60 * typo.spacing }}>
          {stats.map((st, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <Editable tag="div" value={txt(st.value || st.number || '')} onChange={v => setStat(i, 'value', v)} sectionId={s.id} elId={`stat-${i}-val`}
                style={{ fontFamily: `'${typo.headingFont}'`, fontSize: typo.h2, fontWeight: 700, color: brand.cta, display: 'block' }}/>
              <Editable tag="div" value={txt(st.label || st.desc || '')} onChange={v => setStat(i, 'label', v)} sectionId={s.id} elId={`stat-${i}-lbl`}
                style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: 'rgba(255,255,255,.7)', marginTop: 4, display: 'block' }}/>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── PB2/PB3: Problem + stats/items ──
function ProblemStatsSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const stats = f.stats || f.items || [];
  const setStat = (i, k, v) => { const key = f.stats ? 'stats' : 'items'; const next = [...stats]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, [key]: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg, textAlign: 'center' }}>
      <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 * typo.spacing, alignItems: 'center' }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#C2410C" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
        <Body value={f.body || ''} onChange={v => setField('body', v)} typo={typo} color="#475569" sectionId={s.id} elId="body"/>
      </div>
      {stats.length > 0 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: 48, marginTop: 48 }}>
          {stats.map((st, i) => (
            <div key={i} style={{ textAlign: 'center', padding: 24, background: '#fff', borderRadius: 12, border: '1px solid #E2E8F0', minWidth: 140 }}>
              <Editable tag="div" value={txt(st.value || st.number || '')} onChange={v => setStat(i, 'value', v)} sectionId={s.id} elId={`stat-${i}-val`}
                style={{ fontFamily: `'${typo.headingFont}'`, fontSize: typo.h2, fontWeight: 700, color: '#DC2626', display: 'block' }}/>
              <Editable tag="div" value={txt(st.label || st.desc || '')} onChange={v => setStat(i, 'label', v)} sectionId={s.id} elId={`stat-${i}-lbl`}
                style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body * 0.9, color: '#64748B', marginTop: 6, display: 'block' }}/>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── CF1/CF2: Features grid ──
function FeaturesSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const features = f.features || f.items || [];
  const setFeat = (i, k, v) => { const key = f.features ? 'features' : 'items'; const next = [...features]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, [key]: next } }); };
  const cols = features.length <= 3 ? 3 : features.length === 4 ? 2 : 3;
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px` }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 32 }}>
        {features.map((feat, i) => (
          <div key={i} style={{ padding: 28, background: '#fff', borderRadius: 14, border: '1px solid #E2E8F0', display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: `${brand.cta}15`, display: 'grid', placeItems: 'center', color: brand.cta, fontWeight: 700, fontSize: 18 }}>
              {feat.icon ? <span style={{ fontSize: 20 }}>{feat.icon.slice(0,2)}</span> : (i+1)}
            </div>
            <H3 value={txt(feat.title || feat.name || '')} onChange={v => setFeat(i, 'title', v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`feat-${i}-title`}/>
            <Body value={txt(feat.body || feat.desc || '')} onChange={v => setFeat(i, 'body', v)} typo={typo} color="#475569" sectionId={s.id} elId={`feat-${i}-body`}/>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── OB1/FA1: FAQ accordion ──
function FAQSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const questions = f.questions || f.items || [];
  const setQ = (i, k, v) => { const key = f.questions ? 'questions' : 'items'; const next = [...questions]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, [key]: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${48 * typo.spacing}px` }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ maxWidth: 720, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {questions.map((q, i) => (
          <div key={i} style={{ padding: '20px 24px', background: '#fff', borderRadius: 12, border: '1px solid #E2E8F0' }}>
            <H3 value={txt(q.question || q.title || q.q || '')} onChange={v => setQ(i, 'question', v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`q-${i}-q`}/>
            <div style={{ marginTop: 10 }}>
              <Body value={txt(q.answer || q.body || q.a || '')} onChange={v => setQ(i, 'answer', v)} typo={typo} color="#475569" sectionId={s.id} elId={`q-${i}-a`}/>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── FI1-FI4: About / O firmie — split text + image ──
function AboutSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80, alignItems: 'center' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 * typo.spacing }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
        <Body value={f.body || ''} onChange={v => setField('body', v)} typo={typo} color="#475569" sectionId={s.id} elId="body"/>
        {f.quote && <Editable tag="blockquote" value={f.quote} onChange={v => setField('quote', v)} sectionId={s.id} elId="quote"
          style={{ margin: 0, padding: '16px 24px', borderLeft: `3px solid ${brand.cta}`, fontFamily: `'${typo.headingFont}'`, fontSize: typo.body * 1.1, fontStyle: 'italic', color: '#334155', display: 'block' }}/>}
        {f.cta && <CTAButton value={f.cta} onChange={v => setField('cta', v)} typo={typo} brand={brand} sectionId={s.id} elId="cta"/>}
      </div>
      <SectionImg src={f.image} fallback={STOCK_IMAGES.about} alt={f.heading || ''} sectionId={s.id} field="image"
        style={{ aspectRatio: '4/3', borderRadius: 20 }}/>
    </div>
  );
}

// ── PR1/PR2: Process steps ──
function ProcessSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const steps = f.steps || f.items || f.features || [];
  const setStep = (i, k, v) => { const key = f.steps ? 'steps' : (f.items ? 'items' : 'features'); const next = [...steps]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, [key]: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px` }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(steps.length, 4)}, 1fr)`, gap: 32 }}>
        {steps.map((step, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 14, textAlign: 'center', alignItems: 'center' }}>
            <div style={{ width: 48, height: 48, borderRadius: '50%', background: `linear-gradient(135deg, ${brand.cta}, ${brand.cta2 || brand.cta})`, display: 'grid', placeItems: 'center', color: '#fff', fontWeight: 700, fontSize: 18, fontFamily: `'${typo.headingFont}'` }}>{i+1}</div>
            <H3 value={txt(step.title || step.name || '')} onChange={v => setStep(i, 'title', v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`step-${i}-title`}/>
            <Body value={txt(step.body || step.desc || '')} onChange={v => setStep(i, 'body', v)} typo={typo} color="#475569" sectionId={s.id} elId={`step-${i}-body`}/>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── ZE1/ZE2: Team ──
function TeamSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const members = f.members || f.team || [];
  const setM = (i, k, v) => { const key = f.members ? 'members' : 'team'; const next = [...members]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, [key]: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px` }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(members.length, 4)}, 1fr)`, gap: 32 }}>
        {members.map((m, i) => (
          <div key={i} style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
            <SectionImg src={m.image || m.photo} fallback={STOCK_IMAGES.team[i % STOCK_IMAGES.team.length]} alt={txt(m.name || '')} sectionId={s.id} field={`m-${i}-image`}
              style={{ width: 96, height: 96, borderRadius: '50%' }}/>
            <Editable tag="div" value={txt(m.name || '')} onChange={v => setM(i, 'name', v)} sectionId={s.id} elId={`m-${i}-name`}
              style={{ fontFamily: `'${typo.headingFont}'`, fontSize: typo.h3 * 0.85, fontWeight: 600, color: '#0F172A', display: 'block' }}/>
            <Editable tag="div" value={txt(m.role || m.position || '')} onChange={v => setM(i, 'role', v)} sectionId={s.id} elId={`m-${i}-role`}
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: '#6366F1', fontWeight: 500, display: 'block' }}/>
            {m.bio && <Body value={txt(m.bio)} onChange={v => setM(i, 'bio', v)} typo={typo} color="#64748B" sectionId={s.id} elId={`m-${i}-bio`}/>}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── CE1: Pricing ──
function PricingSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const plans = f.plans || f.tiers || [];
  const key = f.plans ? 'plans' : 'tiers';
  const setPlan = (i, k, v) => { const next = [...plans]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, [key]: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px` }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(plans.length, 3)}, 1fr)`, gap: 24 }}>
        {plans.map((p, i) => {
          const highlighted = p.highlighted || p.popular || i === 1;
          return (
            <div key={i} style={{ padding: 36, background: highlighted ? brand.cta : '#fff', borderRadius: 16, border: highlighted ? 'none' : '1px solid #E2E8F0', display: 'flex', flexDirection: 'column', gap: 14, transform: highlighted ? 'scale(1.03)' : 'none' }}>
              <H3 value={txt(p.name || p.title || '')} onChange={v => setPlan(i, 'name', v)} typo={typo} color={highlighted ? '#fff' : '#0F172A'} sectionId={s.id} elId={`plan-${i}-name`}/>
              <Editable tag="div" value={txt(p.price || '')} onChange={v => setPlan(i, 'price', v)} sectionId={s.id} elId={`plan-${i}-price`}
                style={{ fontFamily: `'${typo.headingFont}'`, fontSize: typo.h2, fontWeight: 700, color: highlighted ? '#fff' : brand.cta, display: 'block' }}/>
              <Body value={txt(p.desc || '')} onChange={v => setPlan(i, 'desc', v)} typo={typo} color={highlighted ? 'rgba(255,255,255,.8)' : '#64748B'} sectionId={s.id} elId={`plan-${i}-desc`}/>
              <div style={{ height: 1, background: highlighted ? 'rgba(255,255,255,.2)' : '#E2E8F0', margin: '8px 0' }}/>
              {(p.items || p.features || []).map((it, ii) => (
                <div key={ii} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={highlighted ? '#fff' : brand.cta} strokeWidth="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                  <Editable tag="span" value={txt(it)} onChange={v => { const next = [...plans]; const items = [...(next[i].items || next[i].features || [])]; items[ii] = typeof it === 'object' ? { ...it, text: v } : v; next[i] = { ...next[i], [next[i].items ? 'items' : 'features']: items }; update({ fields: { ...f, [key]: next } }); }} sectionId={s.id} elId={`plan-${i}-item-${ii}`}
                    style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: highlighted ? '#fff' : '#334155' }}/>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── KO1: Contact ──
function ContactSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const formFields = f.form_fields || [];
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
        <Body value={f.body || ''} onChange={v => setField('body', v)} typo={typo} color="#475569" sectionId={s.id} elId="body"/>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 16 }}>
          {f.address && <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: `${brand.cta}15`, display: 'grid', placeItems: 'center', color: brand.cta, flexShrink: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 6-9 13-9 13S3 16 3 10a9 9 0 1118 0z"/><circle cx="12" cy="10" r="3"/></svg>
            </div>
            <Editable tag="span" value={f.address} onChange={v => setField('address', v)} sectionId={s.id} elId="address"
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: '#334155' }}/>
          </div>}
          {f.phone && <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: `${brand.cta}15`, display: 'grid', placeItems: 'center', color: brand.cta, flexShrink: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 01-2.18 2A19.79 19.79 0 013.09 5.18 2 2 0 015.11 3h3a2 2 0 012 1.72c.13.81.36 1.6.68 2.34a2 2 0 01-.45 2.11L8.09 11.5a16 16 0 006.41 6.41l2.33-2.33a2 2 0 012.11-.45c.74.32 1.53.55 2.34.68a2 2 0 011.72 2z"/></svg>
            </div>
            <Editable tag="span" value={f.phone} onChange={v => setField('phone', v)} sectionId={s.id} elId="phone"
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: '#334155' }}/>
          </div>}
          {f.email && <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: `${brand.cta}15`, display: 'grid', placeItems: 'center', color: brand.cta, flexShrink: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </div>
            <Editable tag="span" value={f.email} onChange={v => setField('email', v)} sectionId={s.id} elId="email"
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: '#334155' }}/>
          </div>}
        </div>
      </div>
      <div style={{ background: '#fff', borderRadius: 16, border: '1px solid #E2E8F0', padding: 32, display: 'flex', flexDirection: 'column', gap: 16 }}>
        {formFields.map((field, i) => (
          <div key={i}>
            <div style={{ fontSize: typo.body * 0.85, fontWeight: 500, color: '#64748B', marginBottom: 6, fontFamily: `'${typo.bodyFont}'` }}>{txt(field)}</div>
            <div style={{ height: 40, borderRadius: 8, border: '1px solid #E2E8F0', background: '#FAFBFC' }}/>
          </div>
        ))}
        {formFields.length === 0 && ['Imię i nazwisko', 'Email', 'Telefon', 'Wiadomość'].map((label, i) => (
          <div key={i}>
            <div style={{ fontSize: typo.body * 0.85, fontWeight: 500, color: '#64748B', marginBottom: 6, fontFamily: `'${typo.bodyFont}'` }}>{label}</div>
            <div style={{ height: i === 3 ? 80 : 40, borderRadius: 8, border: '1px solid #E2E8F0', background: '#FAFBFC' }}/>
          </div>
        ))}
        <div style={{ marginTop: 8, padding: '12px 24px', background: `linear-gradient(135deg, ${brand.cta}, ${brand.cta2 || brand.cta})`, color: '#fff', borderRadius: 10, textAlign: 'center', fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, fontWeight: 600 }}>Wyślij wiadomość</div>
      </div>
    </div>
  );
}

// ── RE1: Portfolio / Realizacje ──
function PortfolioSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const projects = f.projects || f.items || [];
  const setProj = (i, k, v) => { const key = f.projects ? 'projects' : 'items'; const next = [...projects]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, [key]: next } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px` }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading || ''} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(projects.length, 3)}, 1fr)`, gap: 24 }}>
        {projects.map((p, i) => (
          <div key={i} style={{ borderRadius: 16, overflow: 'hidden', border: '1px solid #E2E8F0' }}>
            <SectionImg src={p.image} fallback={STOCK_IMAGES.portfolio[i % STOCK_IMAGES.portfolio.length]} alt={txt(p.title || '')} sectionId={s.id} field={`proj-${i}-image`}
              style={{ aspectRatio: '16/10' }}/>
            <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <H3 value={txt(p.title || p.name || '')} onChange={v => setProj(i, 'title', v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`proj-${i}-title`}/>
              <Body value={txt(p.desc || p.body || '')} onChange={v => setProj(i, 'desc', v)} typo={typo} color="#64748B" sectionId={s.id} elId={`proj-${i}-desc`}/>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── ST1: Stats / Statystyki ──
function StatsSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const stats = f.stats || f.items || [];
  const setStat = (i, k, v) => { const key = f.stats ? 'stats' : 'items'; const next = [...stats]; next[i] = { ...next[i], [k]: v }; update({ fields: { ...f, [key]: next } }); };
  return (
    <div style={{ padding: `${80 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      {f.heading && <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <H2 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 64 }}>
        {stats.map((st, i) => (
          <div key={i} style={{ textAlign: 'center' }}>
            <Editable tag="div" value={txt(st.value || st.number || '')} onChange={v => setStat(i, 'value', v)} sectionId={s.id} elId={`stat-${i}-val`}
              style={{ fontFamily: `'${typo.headingFont}'`, fontSize: typo.h1, fontWeight: 700, color: brand.cta, display: 'block' }}/>
            <Editable tag="div" value={txt(st.label || st.desc || '')} onChange={v => setStat(i, 'label', v)} sectionId={s.id} elId={`stat-${i}-lbl`}
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: '#64748B', marginTop: 8, display: 'block' }}/>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── OP2: Single big quote ──
function BigQuoteSection({ s, brand, typo, update }) {
  const f = s.fields || {};
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const testimonials = f.testimonials || [];
  const t = testimonials[0] || {};
  const setT = (k, v) => { const next = [{ ...t, [k]: v }, ...testimonials.slice(1)]; update({ fields: { ...f, testimonials: next } }); };
  return (
    <div style={{ padding: `${120 * typo.spacing}px 80px`, background: s.bg || brand.bg, textAlign: 'center' }}>
      <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
        <Eyebrow value={f.eyebrow || ''} onChange={v => setField('eyebrow', v)} typo={typo} color="#B45309" sectionId={s.id} elId="eyebrow"/>
        <div style={{ fontFamily: `'${typo.headingFont}'`, fontSize: 72, lineHeight: 0.5, color: brand.cta, opacity: 0.3 }}>"</div>
        <Editable tag="p" value={txt(t.quote || '')} onChange={v => setT('quote', v)} multiline sectionId={s.id} elId="quote"
          style={{ margin: 0, fontFamily: `'${typo.headingFont}'`, fontSize: typo.h2, lineHeight: 1.4, color: '#0F172A', fontStyle: 'italic', display: 'block' }}/>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginTop: 16 }}>
          <div style={{ width: 56, height: 56, borderRadius: '50%', background: `linear-gradient(135deg, ${brand.cta}, ${brand.cta2 || brand.cta})`, flexShrink: 0 }}/>
          <div style={{ textAlign: 'left' }}>
            <Editable tag="div" value={txt(t.author || '')} onChange={v => setT('author', v)} sectionId={s.id} elId="author"
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, fontWeight: 600, color: '#0F172A', display: 'block' }}/>
            <Editable tag="div" value={txt(t.role || '')} onChange={v => setT('role', v)} sectionId={s.id} elId="role"
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body * 0.9, color: '#64748B', display: 'block' }}/>
          </div>
        </div>
      </div>
    </div>
  );
}

// Placeholder — fallback
function PlaceholderSection({ s }) {
  return (
    <div style={{ padding: '60px 80px', background: '#FAFBFC', textAlign: 'center', borderRadius: 0 }}>
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 12px', background: '#fff', border: '1px dashed #CBD5E1', borderRadius: 8, marginBottom: 12 }}>
        <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 11, fontWeight: 700, color: '#6366F1' }}>{s?.code || '—'}</span>
        <span style={{ fontSize: 11, color: '#94A3B8' }}>· szablon w przygotowaniu</span>
      </div>
      <div style={{ fontSize: 22, fontWeight: 600, color: '#0F172A', marginBottom: 6 }}>{s?.title || s?.code}</div>
    </div>
  );
}

// ═══════════════════════════════════════════════
// SECTION_RENDERERS — all 40 block codes mapped
// ═══════════════════════════════════════════════
// ═══════════════════════════════════════
// OFFER BLOCKS — NO, DW, CTA
// Landscape A4, każdy klocek = 1 strona
// ═══════════════════════════════════════

function OfferHeaderSection({ s, brand, typo, update }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'flex', alignItems: 'center',
      background: `linear-gradient(rgba(0,0,0,0.5),rgba(0,0,0,0.5)),url('${txt(f.bg_photo_url) || STOCK_IMAGES.offer_hero}') center/cover no-repeat` }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '80px 64px', width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <Eyebrow value={f.eyebrow || 'OFERTA PREZENTOWA'} onChange={(v: any) => setField('eyebrow', v)} typo={typo} color="#a78bfa" sectionId={s.id} elId="eyebrow" />
            <H1 value={f.occasion_name || 'Oferta prezentowa'} onChange={(v: any) => setField('occasion_name', v)} typo={typo} color="#fff" sectionId={s.id} elId="occasion_name" />
            <Body value={f.client_name ? `dla ${txt(f.client_name)}` : 'dla Klienta'} onChange={(v: any) => setField('client_name', v)} typo={typo} color="#cbd5e1" sectionId={s.id} elId="client_name" />
            <Editable tag="div" value={`Nr: ${txt(f.offer_number)} • ${txt(f.date)}`} onChange={(v: any) => setField('offer_number', v)} sectionId={s.id} elId="offer_number" style={{ fontSize: 14, color: '#94a3b8', marginTop: 8 }} />
          </div>
          <SectionImg src={f.client_logo_url} fallback="" alt="Logo" sectionId={s.id} field="client_logo_url" style={{ height: 64, width: 'auto', background: '#fff', borderRadius: 14, padding: 12 }} />
        </div>
      </div>
      <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 10 }}>
        <SectionImg src={f.bg_photo_url} fallback={STOCK_IMAGES.offer_hero} alt="Tło" sectionId={s.id} field="bg_photo_url" style={{ width: 48, height: 48, borderRadius: 8, border: '2px solid rgba(255,255,255,0.3)' }} />
      </div>
    </div>
  );
}

function OfferHeaderFullSection({ s, brand, typo, update }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'flex', alignItems: 'flex-end',
      background: `linear-gradient(to top,rgba(0,0,0,0.75) 0%,rgba(0,0,0,0.05) 50%),url('${txt(f.bg_photo_url) || STOCK_IMAGES.offer_hero}') center/cover no-repeat` }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 64px 64px', width: '100%' }}>
        <SectionImg src={f.client_logo_url} fallback="" alt="Logo" sectionId={s.id} field="client_logo_url" style={{ height: 48, width: 'auto', background: 'rgba(255,255,255,0.9)', borderRadius: 10, padding: 8, marginBottom: 20 }} />
        <H1 value={f.occasion_name || 'Oferta prezentowa'} onChange={(v: any) => setField('occasion_name', v)} typo={typo} color="#fff" sectionId={s.id} elId="occasion_name" />
        <Body value={`${txt(f.occasion_name)} — ${txt(f.client_name)}`} onChange={(v: any) => setField('client_name', v)} typo={typo} color="#e2e8f0" sectionId={s.id} elId="client_name" />
      </div>
      <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 10 }}>
        <SectionImg src={f.bg_photo_url} fallback={STOCK_IMAGES.offer_hero} alt="Tło" sectionId={s.id} field="bg_photo_url" style={{ width: 48, height: 48, borderRadius: 8, border: '2px solid rgba(255,255,255,0.3)' }} />
      </div>
    </div>
  );
}

function OfferImgLeftTextRight({ s, brand, typo, update }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
      <SectionImg src={f.image} fallback={STOCK_IMAGES.offer_wine} alt="" sectionId={s.id} field="image" style={{ width: '100%', height: '100%', minHeight: 400 }} />
      <div style={{ padding: '80px 64px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 20, background: s.bg || brand.bg }}>
        <Eyebrow value={f.eyebrow} onChange={(v: any) => setField('eyebrow', v)} typo={typo} color="#8b7355" sectionId={s.id} elId="eyebrow" />
        <H2 value={f.heading} onChange={(v: any) => setField('heading', v)} typo={typo} color="#1e293b" sectionId={s.id} elId="heading" />
        <Body value={f.body} onChange={(v: any) => setField('body', v)} typo={typo} color="#64748b" sectionId={s.id} elId="body" />
      </div>
    </div>
  );
}

function OfferTextLeftImgRight({ s, brand, typo, update }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
      <div style={{ padding: '80px 64px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 20, background: s.bg || brand.bg }}>
        <Eyebrow value={f.eyebrow} onChange={(v: any) => setField('eyebrow', v)} typo={typo} color="#8b7355" sectionId={s.id} elId="eyebrow" />
        <H2 value={f.heading} onChange={(v: any) => setField('heading', v)} typo={typo} color="#1e293b" sectionId={s.id} elId="heading" />
        <Body value={f.body} onChange={(v: any) => setField('body', v)} typo={typo} color="#64748b" sectionId={s.id} elId="body" />
      </div>
      <SectionImg src={f.image} fallback={STOCK_IMAGES.offer_gift} alt="" sectionId={s.id} field="image" style={{ width: '100%', height: '100%', minHeight: 400 }} />
    </div>
  );
}

function OfferImgTopTextBottom({ s, brand, typo, update }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <SectionImg src={f.image} fallback={STOCK_IMAGES.offer_table} alt="" sectionId={s.id} field="image" style={{ flex: '0 0 55%', width: '100%' }} />
      <div style={{ flex: 1, padding: '48px 64px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 16, maxWidth: 900, margin: '0 auto', width: '100%' }}>
        <Eyebrow value={f.eyebrow} onChange={(v: any) => setField('eyebrow', v)} typo={typo} color="#8b7355" sectionId={s.id} elId="eyebrow" />
        <H2 value={f.heading} onChange={(v: any) => setField('heading', v)} typo={typo} color="#1e293b" sectionId={s.id} elId="heading" />
        <Body value={f.body} onChange={(v: any) => setField('body', v)} typo={typo} color="#64748b" sectionId={s.id} elId="body" />
      </div>
    </div>
  );
}

function OfferGridSection({ s, brand, typo, update, cols = 2 }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  const fontSize = cols > 3 ? { h: 18, b: 13 } : cols > 2 ? { h: 22, b: 14 } : { h: 26, b: 15 };
  const radius = cols > 3 ? 12 : cols > 2 ? 14 : 16;
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'flex', flexDirection: 'column', padding: '48px 64px', background: s.bg || brand.bg }}>
      <Eyebrow value={f.eyebrow} onChange={(v: any) => setField('eyebrow', v)} typo={typo} color="#8b7355" sectionId={s.id} elId="eyebrow" />
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: cols > 3 ? 20 : 24, flex: 1, marginTop: 24 }}>
        {Array.from({ length: cols }, (_, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <SectionImg src={f[`image_${i+1}`]} fallback={STOCK_IMAGES.offer_wine} alt="" sectionId={s.id} field={`image_${i+1}`} style={{ flex: '0 0 55%', borderRadius: radius }} />
            <H3 value={f[`heading_${i+1}`]} onChange={(v: any) => setField(`heading_${i+1}`, v)} typo={typo} color="#1e293b" sectionId={s.id} elId={`heading_${i+1}`} />
            <Body value={f[`body_${i+1}`]} onChange={(v: any) => setField(`body_${i+1}`, v)} typo={typo} color="#64748b" sectionId={s.id} elId={`body_${i+1}`} />
          </div>
        ))}
      </div>
    </div>
  );
}

function OfferGrid2Section(props: any) { return <OfferGridSection {...props} cols={2} />; }
function OfferGrid3Section(props: any) { return <OfferGridSection {...props} cols={3} />; }
function OfferGrid4Section(props: any) { return <OfferGridSection {...props} cols={4} />; }

function OfferColumnsSection({ s, brand, typo, update }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: 32 }}>
        {[1,2,3].map(i => <SectionImg key={i} src={f[`image_${i}`]} fallback={STOCK_IMAGES.offer_wine} alt="" sectionId={s.id} field={`image_${i}`} style={{ flex: 1, borderRadius: 14 }} />)}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 40, padding: 64, background: s.bg || brand.bg }}>
        <Eyebrow value={f.eyebrow} onChange={(v: any) => setField('eyebrow', v)} typo={typo} color="#8b7355" sectionId={s.id} elId="eyebrow" />
        {[1,2,3].map(i => (
          <div key={i}>
            <H3 value={f[`heading_${i}`]} onChange={(v: any) => setField(`heading_${i}`, v)} typo={typo} color="#1e293b" sectionId={s.id} elId={`heading_${i}`} />
            <Body value={f[`body_${i}`]} onChange={(v: any) => setField(`body_${i}`, v)} typo={typo} color="#64748b" sectionId={s.id} elId={`body_${i}`} />
          </div>
        ))}
      </div>
    </div>
  );
}

function OfferQuoteSection({ s, brand, typo, update }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: `linear-gradient(rgba(0,0,0,0.6),rgba(0,0,0,0.6)),url('${txt(f.image) || STOCK_IMAGES.offer_table}') center/cover no-repeat` }}>
      <div style={{ maxWidth: 800, textAlign: 'center' as const, padding: '80px 64px' }}>
        <div style={{ width: 56, height: 2, background: '#c4a87a', margin: '0 auto 32px' }} />
        <H2 value={f.heading} onChange={(v: any) => setField('heading', v)} typo={typo} color="#fff" sectionId={s.id} elId="heading" />
        <Body value={f.body} onChange={(v: any) => setField('body', v)} typo={typo} color="#c4a87a" sectionId={s.id} elId="body" />
        <div style={{ width: 56, height: 2, background: '#c4a87a', margin: '32px auto 0' }} />
      </div>
      <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 10 }}>
        <SectionImg src={f.image} fallback={STOCK_IMAGES.offer_table} alt="Tło" sectionId={s.id} field="image" style={{ width: 48, height: 48, borderRadius: 8, border: '2px solid rgba(255,255,255,0.3)' }} />
      </div>
    </div>
  );
}

function OfferCtaSection({ s, brand, typo, update }: any) {
  const f = s.fields || {};
  const setField = (k: any, v: any) => update({ fields: { ...f, [k]: v } });
  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#111827', padding: '80px 64px' }}>
      <div style={{ textAlign: 'center' as const, maxWidth: 700 }}>
        <H2 value={f.heading || 'Zainteresowany?'} onChange={(v: any) => setField('heading', v)} typo={typo} color="#fff" sectionId={s.id} elId="heading" />
        <Body value={f.body} onChange={(v: any) => setField('body', v)} typo={typo} color="#9ca3af" sectionId={s.id} elId="body" />
        <div style={{ marginTop: 32 }}>
          <CTAButton value={f.cta_text || 'Akceptuję ofertę'} onChange={(v: any) => setField('cta_text', v)} typo={typo} brand={brand} sectionId={s.id} elId="cta_text" />
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 32, marginTop: 32 }}>
          <Editable tag="span" value={f.contact_name} onChange={(v: any) => setField('contact_name', v)} sectionId={s.id} elId="contact_name" style={{ fontSize: 15, color: '#6b7280' }} />
          <Editable tag="span" value={f.contact_email} onChange={(v: any) => setField('contact_email', v)} sectionId={s.id} elId="contact_email" style={{ fontSize: 15, color: '#818cf8' }} />
          <Editable tag="span" value={f.contact_phone} onChange={(v: any) => setField('contact_phone', v)} sectionId={s.id} elId="contact_phone" style={{ fontSize: 15, color: '#6b7280' }} />
        </div>
      </div>
    </div>
  );
}

const SECTION_RENDERERS = {
  // Navigation (NA)
  NA1: NavSection, NA2: NavSection, NA3: NavSection,
  // Hero (HE)
  HE1: HeroCenteredSection, HE2: HeroSection, HE3: HeroCenteredSection, HE4: HeroCenteredSection, HE5: HeroCenteredSection,
  // Problem (PB)
  PB1: ProblemSection, PB2: ProblemStatsSection, PB3: ProblemStatsSection,
  // Solution (RO)
  RO1: SolutionSection, RO2: SolutionSection,
  // Benefits (KR)
  KR1: WhyUsSection, KR2: WhyUsSection,
  // Features (CF)
  CF1: FeaturesSection, CF2: FeaturesSection,
  // Objections (OB)
  OB1: FAQSection,
  // About (FI)
  FI1: AboutSection, FI2: AboutSection, FI3: AboutSection, FI4: AboutSection,
  // Offer (OF)
  OF1: OfferSection, OF2: OfferSection,
  // Process (PR)
  PR1: ProcessSection, PR2: ProcessSection,
  // Opinions (OP)
  OP1: OpinionsSection, OP2: BigQuoteSection,
  // Team (ZE)
  ZE1: TeamSection, ZE2: TeamSection,
  // Pricing (CE)
  CE1: PricingSection,
  // CTA (CT)
  CT1: CtaSection, CT2: CtaSection, CT3: CtaSection,
  // Contact (KO)
  KO1: ContactSection,
  // FAQ (FA)
  FA1: FAQSection,
  // Portfolio (RE)
  RE1: PortfolioSection,
  // Logos (LO)
  LO1: LogosSection,
  // Stats (ST)
  ST1: StatsSection,
  // Footer (FO)
  FO1: FooterSection,
  // Offer blocks (NO, DW, CTA)
  NO1: OfferHeaderSection,
  NO2: OfferHeaderFullSection,
  DW1: OfferImgLeftTextRight,
  DW2: OfferTextLeftImgRight,
  DW3: OfferImgTopTextBottom,
  DW4: OfferGrid2Section,
  DW5: OfferGrid3Section,
  DW6: OfferGrid4Section,
  DW7: OfferColumnsSection,
  DW8: OfferQuoteSection,
  CTA1: OfferCtaSection,
  // Fallback
  PLACEHOLDER: PlaceholderSection,
};

export { SECTION_RENDERERS };
export { Editable };
export { EditCtx };
