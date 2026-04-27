import React from "react";
// Sekcje strony — per-element edycja + overrides

// Context pozwala Editable zarejestrować focus u parenta (App)
const EditCtx = React.createContext(null);

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
    minWidth: 20,
    display: style.display || 'inline-block',
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
  return <Editable tag="div" value={value} onChange={onChange} sectionId={sectionId} elId={elId}
    style={{ margin: 0, fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: typo.eyebrow, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.12em', color, opacity: 0.8, display: 'block' }}/>;
}
function CTAButton({ value, onChange, typo, brand, variant = 'primary', dark, sectionId, elId }) {
  const bg = variant === 'primary' ? (brand.ctaGradient ? `linear-gradient(135deg, ${brand.cta}, ${brand.cta2})` : brand.cta) : 'transparent';
  const color = variant === 'primary' ? '#fff' : (dark ? '#fff' : '#0F172A');
  const border = variant === 'primary' ? 'none' : `2px solid ${dark ? '#fff' : '#0F172A'}`;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 10,
      padding: `${Math.round(typo.body * 0.75)}px ${Math.round(typo.body * 1.5)}px`,
      background: bg, color, border, borderRadius: 12,
      fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: typo.body, fontWeight: 600, cursor: 'text',
    }}>
      <Editable tag="span" value={value} onChange={onChange} sectionId={sectionId} elId={elId}
        style={{ display: 'inline', color: 'inherit', fontSize: typo.body, fontWeight: 600 }}/>
      <span>→</span>
    </span>
  );
}

/* ===== SECTION RENDERERS ===== */

function NavSection({ s, brand, typo, update }) {
  const f = s.fields;
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const setLink = (i, v) => { const links = [...f.links]; links[i] = v; update({ fields: { ...f, links } }); };
  return (
    <div style={{ padding: '28px 80px', display: 'flex', alignItems: 'center', gap: 40, background: s.bg || brand.bg, borderBottom: '1px solid rgba(0,0,0,.06)' }}>
      <Editable tag="div" value={f.logo} onChange={v => setField('logo', v)} sectionId={s.id} elId="logo"
        style={{ fontFamily: `'${typo.headingFont}', serif`, fontSize: Math.round(typo.h3 * 0.7), fontWeight: 700, color: '#0F172A', letterSpacing: '-0.01em' }}/>
      <div style={{ flex: 1, display: 'flex', gap: 32, justifyContent: 'center' }}>
        {f.links.map((l, i) => (
          <Editable key={i} tag="span" value={l} onChange={v => setLink(i, v)} sectionId={s.id} elId={`link-${i}`}
            style={{ fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: Math.round(typo.body * 0.95), color: '#334155', fontWeight: 500 }}/>
        ))}
      </div>
      <CTAButton value={f.cta} onChange={v => setField('cta', v)} typo={typo} brand={brand} sectionId={s.id} elId="cta"/>
    </div>
  );
}

function HeroSection({ s, brand, typo, update }) {
  const f = s.fields;
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
      <div style={{ aspectRatio: '4/5', background: 'linear-gradient(135deg, #FED7AA 0%, #FDBA74 100%)', borderRadius: 24, display: 'grid', placeItems: 'center', color: '#9A3412', position: 'relative', overflow: 'hidden' }}>
        <div style={{ fontFamily: `'${typo.headingFont}'`, fontSize: 120, opacity: 0.15, letterSpacing: '-0.05em' }}>☕</div>
        <div style={{ position: 'absolute', bottom: 20, right: 20, fontSize: 11, color: '#9A3412', opacity: 0.6, fontFamily: 'ui-monospace, monospace' }}>[zdjęcie kawiarni]</div>
      </div>
    </div>
  );
}

function LogosSection({ s, brand, typo, update }) {
  const f = s.fields;
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const setLogo = (i, v) => { const logos = [...f.logos]; logos[i] = v; update({ fields: { ...f, logos } }); };
  return (
    <div style={{ padding: `${60 * typo.spacing}px 80px`, background: s.bg || brand.bg, textAlign: 'center' }}>
      <Editable tag="div" value={f.title} onChange={v => setField('title', v)} sectionId={s.id} elId="title"
        style={{ fontFamily: `'${typo.bodyFont}', sans-serif`, fontSize: typo.eyebrow, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#64748B', marginBottom: 32, display: 'block' }}/>
      <div style={{ display: 'flex', gap: 48, justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }}>
        {f.logos.map((l, i) => (
          <Editable key={i} tag="span" value={l} onChange={v => setLogo(i, v)} sectionId={s.id} elId={`logo-${i}`}
            style={{ fontFamily: `'${typo.headingFont}', serif`, fontSize: Math.round(typo.h3 * 0.85), fontWeight: 500, color: '#94A3B8', fontStyle: 'italic' }}/>
        ))}
      </div>
    </div>
  );
}

function ProblemSection({ s, brand, typo, update }) {
  const f = s.fields;
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
  const f = s.fields;
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const setFeat = (i, k, v) => { const features = [...f.features]; features[i] = { ...features[i], [k]: v }; update({ fields: { ...f, features } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px` }}>
        <Eyebrow value={f.eyebrow} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 40 }}>
        {f.features.map((feat, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ width: 56, height: 56, borderRadius: 14, background: `linear-gradient(135deg, ${brand.cta}, ${brand.cta2})`, display: 'grid', placeItems: 'center', color: '#fff', fontWeight: 700, fontSize: 20, fontFamily: `'${typo.headingFont}'` }}>{i+1}</div>
            <H3 value={feat.title} onChange={v => setFeat(i, 'title', v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`feat-${i}-title`}/>
            <Body value={feat.body} onChange={v => setFeat(i, 'body', v)} typo={typo} color="#475569" sectionId={s.id} elId={`feat-${i}-body`}/>
          </div>
        ))}
      </div>
    </div>
  );
}

function WhyUsSection({ s, brand, typo, update }) {
  const f = s.fields;
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const setPoint = (i, v) => { const points = [...f.points]; points[i] = v; update({ fields: { ...f, points } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80, alignItems: 'center' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 * typo.spacing }}>
        <Eyebrow value={f.eyebrow} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
        <Body value={f.body} onChange={v => setField('body', v)} typo={typo} color="#475569" sectionId={s.id} elId="body"/>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {f.points.map((p, i) => (
          <div key={i} style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
            <div style={{ width: 28, height: 28, borderRadius: 8, background: brand.cta, display: 'grid', placeItems: 'center', color: '#fff', flexShrink: 0, marginTop: 2 }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>
            </div>
            <Body value={p} onChange={v => setPoint(i, v)} typo={typo} color="#334155" sectionId={s.id} elId={`point-${i}`}/>
          </div>
        ))}
      </div>
    </div>
  );
}

function OfferSection({ s, brand, typo, update }) {
  const f = s.fields;
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const setTier = (i, k, v) => { const tiers = [...f.tiers]; tiers[i] = { ...tiers[i], [k]: v }; update({ fields: { ...f, tiers } }); };
  const setItem = (ti, ii, v) => { const tiers = [...f.tiers]; const items = [...tiers[ti].items]; items[ii] = v; tiers[ti] = { ...tiers[ti], items }; update({ fields: { ...f, tiers } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px`, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <Eyebrow value={f.eyebrow} onChange={v => setField('eyebrow', v)} typo={typo} color="#6366F1" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
        {f.tiers.map((t, i) => (
          <div key={i} style={{ padding: 36, background: '#fff', borderRadius: 16, border: '1px solid #E2E8F0', display: 'flex', flexDirection: 'column', gap: 14 }}>
            <H3 value={t.name} onChange={v => setTier(i, 'name', v)} typo={typo} color="#0F172A" sectionId={s.id} elId={`tier-${i}-name`}/>
            <Editable tag="div" value={t.price} onChange={v => setTier(i, 'price', v)} sectionId={s.id} elId={`tier-${i}-price`}
              style={{ fontFamily: `'${typo.headingFont}'`, fontSize: typo.h3, fontWeight: 700, color: brand.cta, display: 'block' }}/>
            <Body value={t.desc} onChange={v => setTier(i, 'desc', v)} typo={typo} color="#64748B" sectionId={s.id} elId={`tier-${i}-desc`}/>
            <div style={{ height: 1, background: '#E2E8F0', margin: '8px 0' }}/>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {t.items.map((it, ii) => (
                <div key={ii} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={brand.cta} strokeWidth="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                  <Editable tag="span" value={it} onChange={v => setItem(i, ii, v)} sectionId={s.id} elId={`tier-${i}-item-${ii}`}
                    style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, color: '#334155' }}/>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function OpinionsSection({ s, brand, typo, update }) {
  const f = s.fields;
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const setT = (i, k, v) => { const testimonials = [...f.testimonials]; testimonials[i] = { ...testimonials[i], [k]: v }; update({ fields: { ...f, testimonials } }); };
  return (
    <div style={{ padding: `${100 * typo.spacing}px 80px`, background: s.bg || brand.bg }}>
      <div style={{ textAlign: 'center', maxWidth: 720, margin: `0 auto ${60 * typo.spacing}px`, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <Eyebrow value={f.eyebrow} onChange={v => setField('eyebrow', v)} typo={typo} color="#B45309" sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color="#0F172A" sectionId={s.id} elId="heading"/>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
        {f.testimonials.map((t, i) => (
          <div key={i} style={{ padding: 32, background: '#fff', borderRadius: 16, display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ fontFamily: `'${typo.headingFont}'`, fontSize: 48, lineHeight: 0.5, color: brand.cta, opacity: 0.4 }}>"</div>
            <Editable tag="p" value={t.quote} onChange={v => setT(i, 'quote', v)} multiline sectionId={s.id} elId={`test-${i}-quote`}
              style={{ margin: 0, fontFamily: `'${typo.bodyFont}'`, fontSize: Math.round(typo.body * 1.1), lineHeight: 1.5, color: '#334155', fontStyle: 'italic', display: 'block' }}/>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 40, height: 40, borderRadius: '50%', background: `linear-gradient(135deg, ${brand.cta}, ${brand.cta2})`, flexShrink: 0 }}/>
              <div>
                <Editable tag="div" value={t.author} onChange={v => setT(i, 'author', v)} sectionId={s.id} elId={`test-${i}-author`}
                  style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.body, fontWeight: 600, color: '#0F172A', display: 'block' }}/>
                <Editable tag="div" value={t.role} onChange={v => setT(i, 'role', v)} sectionId={s.id} elId={`test-${i}-role`}
                  style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: Math.round(typo.body * 0.85), color: '#64748B', display: 'block' }}/>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CtaSection({ s, brand, typo, update }) {
  const f = s.fields;
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const isDark = (s.bg || '').toLowerCase().startsWith('#0') || (s.bg || '').toLowerCase().startsWith('#1');
  const color = isDark ? '#fff' : '#0F172A';
  return (
    <div style={{ padding: `${120 * typo.spacing}px 80px`, background: s.bg || brand.bg, textAlign: 'center' }}>
      <div style={{ maxWidth: 720, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20 * typo.spacing, alignItems: 'center' }}>
        <Eyebrow value={f.eyebrow} onChange={v => setField('eyebrow', v)} typo={typo} color={brand.cta2} sectionId={s.id} elId="eyebrow"/>
        <H2 value={f.heading} onChange={v => setField('heading', v)} typo={typo} color={color} sectionId={s.id} elId="heading"/>
        <Body value={f.body} onChange={v => setField('body', v)} typo={typo} color={isDark ? '#CBD5E1' : '#475569'} sectionId={s.id} elId="body"/>
        <div style={{ display: 'flex', gap: 16, marginTop: 12 }}>
          <CTAButton value={f.cta} onChange={v => setField('cta', v)} typo={typo} brand={brand} sectionId={s.id} elId="cta"/>
          <CTAButton value={f.cta2} onChange={v => setField('cta2', v)} typo={typo} brand={brand} variant="ghost" dark={isDark} sectionId={s.id} elId="cta2"/>
        </div>
      </div>
    </div>
  );
}

function FooterSection({ s, brand, typo, update }) {
  const f = s.fields;
  const setField = (k, v) => update({ fields: { ...f, [k]: v } });
  const setCol = (i, k, v) => { const cols = [...f.cols]; cols[i] = { ...cols[i], [k]: v }; update({ fields: { ...f, cols } }); };
  const setLink = (ci, li, v) => { const cols = [...f.cols]; const links = [...cols[ci].links]; links[li] = v; cols[ci] = { ...cols[ci], links }; update({ fields: { ...f, cols } }); };
  return (
    <div style={{ padding: '80px 80px 32px', background: s.bg || brand.bg, color: '#CBD5E1' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr 1fr', gap: 60, marginBottom: 60 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Editable tag="div" value={f.logo} onChange={v => setField('logo', v)} sectionId={s.id} elId="logo"
            style={{ fontFamily: `'${typo.headingFont}', serif`, fontSize: typo.h3, fontWeight: 700, color: '#fff', letterSpacing: '-0.01em', display: 'block' }}/>
          <Body value={f.desc} onChange={v => setField('desc', v)} typo={typo} color="#94A3B8" sectionId={s.id} elId="desc"/>
        </div>
        {f.cols.map((col, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Editable tag="div" value={col.title} onChange={v => setCol(i, 'title', v)} sectionId={s.id} elId={`col-${i}-title`}
              style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: typo.eyebrow, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#fff', marginBottom: 8, display: 'block' }}/>
            {col.links.map((l, li) => (
              <Editable key={li} tag="div" value={l} onChange={v => setLink(i, li, v)} sectionId={s.id} elId={`col-${i}-link-${li}`}
                style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: Math.round(typo.body * 0.95), color: '#CBD5E1', display: 'block' }}/>
            ))}
          </div>
        ))}
      </div>
      <div style={{ paddingTop: 24, borderTop: '1px solid rgba(255,255,255,.1)' }}>
        <Editable tag="div" value={f.copyright} onChange={v => setField('copyright', v)} sectionId={s.id} elId="copyright"
          style={{ fontFamily: `'${typo.bodyFont}'`, fontSize: Math.round(typo.body * 0.85), color: '#64748B', textAlign: 'center', display: 'block' }}/>
      </div>
    </div>
  );
}

// Placeholder dla kodów których jeszcze nie zaimplementowaliśmy w Treściach
function PlaceholderSection({ s }) {
  return (
    <div style={{ padding: '60px 80px', background: '#FAFBFC', textAlign: 'center', borderRadius: 0 }}>
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 12px', background: '#fff', border: '1px dashed #CBD5E1', borderRadius: 8, marginBottom: 12 }}>
        <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 11, fontWeight: 700, color: '#6366F1' }}>{s?.code || '—'}</span>
        <span style={{ fontSize: 11, color: '#94A3B8' }}>· szablon w przygotowaniu</span>
      </div>
      <div style={{ fontSize: 22, fontWeight: 600, color: '#0F172A', marginBottom: 6 }}>{s?.title || s?.code}</div>
      <div style={{ fontSize: 13, color: '#64748B', maxWidth: 440, margin: '0 auto' }}>
        Tę sekcję wypełnisz w etapie Wizualizacji. W tym widoku skupiamy się na treściach głównych klocków.
      </div>
    </div>
  );
}

const SECTION_RENDERERS = {
  NA1: NavSection,
  HE2: HeroSection,
  LO1: LogosSection,
  PB1: ProblemSection,
  RO1: SolutionSection,
  KR1: WhyUsSection,
  OF1: OfferSection,
  OP1: OpinionsSection,
  CT1: CtaSection,
  FO1: FooterSection,
  // Aliasy / fallbacky: kody używane na podstronach Menu/Rezerwacja/Kontakt — renderowane jako placeholder
  HE1: PlaceholderSection,
  ME1: PlaceholderSection,
  ME2: PlaceholderSection,
  MP1: PlaceholderSection,
  IN1: PlaceholderSection,
  CTA1: PlaceholderSection,
  PLACEHOLDER: PlaceholderSection,
};

export { SECTION_RENDERERS };
export { Editable };
export { EditCtx };
