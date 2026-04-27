import React from "react";
// Wizualizacja — prawdziwe wyrenderowane sekcje Kawiarni Miętowa
// Nie abstrakcyjne paski — prawdziwe nagłówki, paragrafy, zdjęcia, paleta miętowa

// Paleta Miętowa — z Brand (krok 2)
const MIETOWA = {
  mint: '#A8D5BA',       // primary — miętowa
  mintDark: '#6FAE8C',   // hover
  cream: '#FAF6EF',      // ciepły beż (hero bg)
  sand: '#F2EADB',       // sand card
  ink: '#1F2937',        // tekst
  inkSoft: '#4B5563',    // tekst 2
  muted: '#94A3B8',
  line: '#E5E1D6',
  accent: '#C2410C',     // terakota akcent
};

// Zdjęcia kawiarni — Unsplash (free, cafe/coffee theme)
const PHOTOS = {
  hero: 'https://images.unsplash.com/photo-1453614512568-c4024d13c247?w=1200&q=75',
  interior: 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1200&q=75',
  barista: 'https://images.unsplash.com/photo-1511920170033-f8396924c348?w=900&q=75',
  beans: 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=900&q=75',
  cake: 'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=900&q=75',
  pourover: 'https://images.unsplash.com/photo-1559925393-8be0ec4767c8?w=900&q=75',
  shop: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=900&q=75',
  couple: 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=900&q=75',
  dog: 'https://images.unsplash.com/photo-1542736667-069246bdbc6d?w=900&q=75',
  people1: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&q=75',
  people2: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=75',
  people3: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&q=75',
};

// Galeria Unsplash kawiarni dla popovera wymiany zdjęć
const PHOTO_LIBRARY = {
  'Wnętrze': [
    'https://images.unsplash.com/photo-1453614512568-c4024d13c247?w=600&q=70',
    'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600&q=70',
    'https://images.unsplash.com/photo-1511920170033-f8396924c348?w=600&q=70',
    'https://images.unsplash.com/photo-1445116572660-236099ec97a0?w=600&q=70',
    'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=600&q=70',
    'https://images.unsplash.com/photo-1521017432531-fbd92d768814?w=600&q=70',
    'https://images.unsplash.com/photo-1571991661639-a4a82f5f1bde?w=600&q=70',
    'https://images.unsplash.com/photo-1600093463592-8e36ae95ef56?w=600&q=70',
  ],
  'Kawa': [
    'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=600&q=70',
    'https://images.unsplash.com/photo-1559925393-8be0ec4767c8?w=600&q=70',
    'https://images.unsplash.com/photo-1442975631115-c4f7b05b8a2c?w=600&q=70',
    'https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=600&q=70',
    'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=600&q=70',
    'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&q=70',
    'https://images.unsplash.com/photo-1485808191679-5f86510681a2?w=600&q=70',
    'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=600&q=70',
  ],
  'Ciasta': [
    'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=600&q=70',
    'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&q=70',
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600&q=70',
    'https://images.unsplash.com/photo-1464195244916-405fa0a82545?w=600&q=70',
    'https://images.unsplash.com/photo-1505253304499-671c55fb57fe?w=600&q=70',
    'https://images.unsplash.com/photo-1517686469429-8bdb88b9f907?w=600&q=70',
  ],
  'Ludzie': [
    'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&q=70',
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=70',
    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&q=70',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=70',
    'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=70',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&q=70',
    'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=70',
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=70',
  ],
};

// Edit mode context — przekazany z wiz_app przez window global
let __editMode = false;
const EditCtx = React.createContext({ editMode: false, onPickImage: null });
export { EditCtx };

// EditableImg — <img> zapakowany w wrapper z CSS hover-hint "Kliknij, aby edytować".
// Cały wrapper ma data-editable-img="true" — klik na obraz zaznacza img w globalnym listenerze
// i otwiera UniToolbar. Overlay to tylko WSKAZÓWKA wizualna (CSS :hover, nie React state).
function EditableImg({ src, alt, style, defaultCategory = 'Wnętrze' }) {
  const [currentSrc, setCurrentSrc] = React.useState(src);
  const imgRef = React.useRef(null);
  React.useEffect(() => { setCurrentSrc(src); }, [src]);

  // Zapisz oryginalną deklarację AI (inline styles) + faktyczne wymiary po render-ze (piksele).
  const declared = React.useMemo(() => ({
    w: style?.width != null ? String(style.width) : null,
    h: style?.height != null ? String(style.height) : null,
    maxW: style?.maxWidth != null ? String(style.maxWidth) : null,
    maxH: style?.maxHeight != null ? String(style.maxHeight) : null,
  }), [style?.width, style?.height, style?.maxWidth, style?.maxHeight]);

  // Po zmount, zmierz faktyczne wymiary i zapisz je JAKO piksele — to jest nasza "wartość wyjściowa".
  // Robimy to TYLKO raz (gdy element się pojawi), żeby nie nadpisać po ręcznej edycji usera.
  React.useEffect(() => {
    const img = imgRef.current;
    if (!img) return;
    const snapshot = () => {
      if (img.dataset.origSnapshot) return; // już zapisane
      const r = img.getBoundingClientRect();
      if (r.width < 2 || r.height < 2) return;
      img.dataset.origSnapshot = JSON.stringify({
        w: Math.round(r.width),
        h: Math.round(r.height),
        declared,
      });
    };
    if (img.complete) snapshot();
    else img.addEventListener('load', snapshot, { once: true });
    // Fallback — gdyby load nigdy nie odpalił, spróbuj po chwili
    const t = setTimeout(snapshot, 200);
    return () => clearTimeout(t);
  }, [declared]);

  // Wrapper dostaje wymiary z obrazu, ale jest inline-block/block zgodnie ze style.display
  const display = style?.display === 'block' ? 'block' : 'inline-block';
  return (
    <span className="wiz-img-wrap" data-img-wrap="true"
      style={{
        position: 'relative', display, verticalAlign: 'top',
        width: style?.width, maxWidth: style?.maxWidth,
      }}>
      <img ref={imgRef} src={currentSrc} alt={alt} style={style}
        data-editable-img="true"
        data-photo-category={defaultCategory}/>
      {/* CSS-only hint, pokazuje się tylko na hover wrappera */}
      <span className="wiz-img-hint" aria-hidden="true">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
          <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>
        Kliknij, aby edytować
      </span>
    </span>
  );
}
export { EditableImg };
export { PHOTO_LIBRARY };

// EditableText — legacy (zostawione, ale nie używane w sekcjach — używamy globalnego listenera)
function EditableText({ children, as = 'span', style }) {
  const Tag = as;
  return <Tag style={style}>{children}</Tag>;
}
export { EditableText };

// Popover do wymiany zdjęć
function ImagePicker({ picker, onClose }) {
  const [category, setCategory] = React.useState(picker.category || 'Wnętrze');
  const [uploadedSrc, setUploadedSrc] = React.useState(null);
  const fileInputRef = React.useRef(null);

  const handleUpload = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result;
      setUploadedSrc(result);
      picker.onPick(result);
      onClose();
    };
    reader.readAsDataURL(f);
  };

  return (
    <div onClick={onClose} style={{
      position: 'fixed', inset: 0, background: 'rgba(15,23,42,.4)', backdropFilter: 'blur(2px)',
      zIndex: 400, display: 'grid', placeItems: 'center', animation: 'fadeIn .15s',
      fontFamily: 'Inter, sans-serif',
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        width: 680, maxHeight: '80vh', background: '#fff', borderRadius: 16,
        boxShadow: '0 20px 60px rgba(15,23,42,.3)',
        display: 'flex', flexDirection: 'column', overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{ padding: '18px 22px', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: 12 }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0F172A" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 21"/></svg>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 15, fontWeight: 700, color: '#0F172A' }}>Wymień zdjęcie</div>
            <div style={{ fontSize: 12, color: '#64748B' }}>Wybierz z galerii Unsplash albo wrzuć własne</div>
          </div>
          <button onClick={onClose} style={{
            width: 30, height: 30, border: 'none', background: '#F1F5F9',
            borderRadius: 8, cursor: 'pointer', display: 'grid', placeItems: 'center',
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
        {/* Tabs */}
        <div style={{ padding: '12px 22px 0', display: 'flex', gap: 4, borderBottom: '1px solid #E2E8F0' }}>
          {Object.keys(PHOTO_LIBRARY).map(cat => (
            <button key={cat} onClick={() => setCategory(cat)} style={{
              padding: '9px 14px', border: 'none', background: 'transparent',
              fontSize: 13, fontWeight: 500, cursor: 'pointer', fontFamily: 'inherit',
              color: category === cat ? '#0F172A' : '#64748B',
              borderBottom: category === cat ? '2px solid #0F172A' : '2px solid transparent',
              marginBottom: -1,
            }}>{cat}</button>
          ))}
          <div style={{ flex: 1 }}/>
          <button onClick={() => fileInputRef.current?.click()} style={{
            padding: '7px 13px', margin: '3px 0 6px', border: '1px solid #0F172A',
            background: '#0F172A', color: '#fff', borderRadius: 7,
            fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
            display: 'inline-flex', alignItems: 'center', gap: 6,
          }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            Wrzuć własne
          </button>
          <input ref={fileInputRef} type="file" accept="image/*" onChange={handleUpload} style={{ display: 'none' }}/>
        </div>
        {/* Grid */}
        <div style={{ padding: 22, overflow: 'auto', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
          {(PHOTO_LIBRARY[category] || []).map((url, i) => {
            const isCurrent = url === picker.current;
            return (
              <div key={i} onClick={() => { picker.onPick(url); onClose(); }}
                style={{
                  position: 'relative', aspectRatio: '1/1',
                  borderRadius: 8, overflow: 'hidden', cursor: 'pointer',
                  border: isCurrent ? '3px solid #10B981' : '2px solid transparent',
                  transition: 'all .15s',
                }}
                onMouseEnter={e => { if (!isCurrent) e.currentTarget.style.border = '2px solid #CBD5E1'; }}
                onMouseLeave={e => { if (!isCurrent) e.currentTarget.style.border = '2px solid transparent'; }}>
                <img src={url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}/>
                {isCurrent && (
                  <div style={{ position: 'absolute', top: 6, right: 6, background: '#10B981', color: '#fff', borderRadius: '50%', width: 20, height: 20, display: 'grid', placeItems: 'center' }}>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        {/* Footer */}
        <div style={{ padding: '12px 22px', borderTop: '1px solid #E2E8F0', fontSize: 11, color: '#94A3B8', background: '#F8FAFC' }}>
          Zdjęcia z Unsplash (darmowa licencja). Po publikacji zostaną zhostowane w Twoim projekcie.
        </div>
      </div>
    </div>
  );
}
export { ImagePicker };

// Typography helper — używa CSS vars z Wizualizacja (pair)
const H = (extra = {}) => ({
  fontFamily: 'var(--font-heading, Fraunces, serif)',
  fontWeight: 500,
  letterSpacing: '-0.01em',
  lineHeight: 1.1,
  color: MIETOWA.ink,
  margin: 0,
  ...extra,
});
const B = (extra = {}) => ({
  fontFamily: 'var(--font-body, Inter, sans-serif)',
  lineHeight: 1.6,
  color: MIETOWA.inkSoft,
  margin: 0,
  ...extra,
});

// Button
function Btn({ children, primary, onWhite, secondary, style = {} }) {
  const base = {
    display: 'inline-flex', alignItems: 'center', gap: 8,
    padding: '13px 22px', borderRadius: 999,
    fontFamily: 'var(--font-body, Inter, sans-serif)',
    fontSize: 14, fontWeight: 600, textDecoration: 'none',
    cursor: 'pointer', border: '1px solid transparent',
    transition: 'all .2s',
  };
  if (secondary) {
    return <span data-cta="true" role="button" style={{ ...base, background: 'transparent', color: onWhite ? '#fff' : MIETOWA.ink, border: `1px solid ${onWhite ? 'rgba(255,255,255,.3)' : MIETOWA.line}`, ...style }}>{children}</span>;
  }
  return <span data-cta="true" role="button" style={{ ...base, background: MIETOWA.mint, color: MIETOWA.ink, boxShadow: '0 1px 2px rgba(31,41,55,.08)', ...style }}>{children} <span data-no-edit="true">→</span></span>;
}

// Chip/eyebrow
function Eyebrow({ children, onDark }) {
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 8,
      padding: '5px 12px',
      background: onDark ? 'rgba(168,213,186,.15)' : MIETOWA.mint + '30',
      color: onDark ? MIETOWA.mint : '#2F6F50',
      borderRadius: 999,
      fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em',
      fontFamily: 'var(--font-body, Inter, sans-serif)',
    }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'currentColor' }}/>
      {children}
    </div>
  );
}

// Container
const Container = ({ children, style = {} }) => (
  <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 48px', ...style }}>{children}</div>
);

// ============ SECTIONS ============

function SecNav() {
  return (
    <nav style={{ background: '#fff', borderBottom: `1px solid ${MIETOWA.line}`, padding: '18px 0' }}>
      <Container style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: '50%', background: MIETOWA.mint, display: 'grid', placeItems: 'center', color: MIETOWA.ink, fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 18, fontWeight: 500 }}>M</div>
          <span style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 22, color: MIETOWA.ink, fontWeight: 500, letterSpacing: '-0.01em' }}>Miętowa</span>
        </div>
        <div style={{ flex: 1, display: 'flex', gap: 28, fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 14, color: MIETOWA.inkSoft }}>
          {['Menu', 'O nas', 'Wydarzenia', 'Kontakt'].map(l => <a key={l} style={{ color: 'inherit', textDecoration: 'none' }}>{l}</a>)}
        </div>
        <Btn>Rezerwuj stolik</Btn>
      </Container>
    </nav>
  );
}

function SecHero() {
  return (
    <section style={{ background: MIETOWA.cream, padding: '0', position: 'relative' }}>
      <Container style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center', padding: '80px 48px', maxWidth: 1280 }}>
        <div>
          <Eyebrow>Kawa palona we Wrocławiu</Eyebrow>
          <h1 style={H({ fontSize: 64, marginTop: 20, marginBottom: 24 })}>
            <span data-editable-color="true">Miętowa.</span><br/>
            <span data-editable-color="true">Twoja codzienna</span><br/>
            <em data-editable-color="true" style={{ fontStyle: 'italic', color: '#2F6F50' }}>przystań</em>
            <span data-editable-color="true">.</span>
          </h1>
          <p style={B({ fontSize: 17, marginBottom: 32, maxWidth: 480 })}>
            Palimy kawę świeżo w naszej mikropalarni przy ul. Ruskiej. Serwujemy ją z ciastami, książkami i prawdziwymi rozmowami — codziennie od 8:00.
          </p>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <Btn>Sprawdź menu</Btn>
            <Btn secondary>Znajdź nas na mapie</Btn>
          </div>
          <div style={{ display: 'flex', gap: 24, marginTop: 48, paddingTop: 28, borderTop: `1px solid ${MIETOWA.line}` }}>
            {[['8:00–19:00', 'codziennie'], ['Ruska 12', 'Wrocław'], ['4.9 ★', '312 opinii Google']].map(([k, v], i) => (
              <div key={i}>
                <div style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 20, color: MIETOWA.ink }}>{k}</div>
                <div style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 12, color: MIETOWA.muted, marginTop: 2 }}>{v}</div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ position: 'relative' }}>
          <EditableImg src={PHOTOS.hero} alt="Wnętrze kawiarni Miętowa" defaultCategory="Wnętrze"
            style={{ width: '100%', height: 560, objectFit: 'cover', borderRadius: 8, display: 'block' }}/>
          <div style={{
            position: 'absolute', bottom: 24, left: 24,
            background: '#fff', padding: '14px 18px', borderRadius: 8,
            boxShadow: '0 10px 30px rgba(0,0,0,.1)',
            display: 'flex', alignItems: 'center', gap: 12,
          }}>
            <div style={{ width: 40, height: 40, borderRadius: '50%', background: MIETOWA.mint, display: 'grid', placeItems: 'center', fontSize: 18 }}>☕</div>
            <div>
              <div style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 15, color: MIETOWA.ink }}>Dzisiejsza kawa</div>
              <div style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 12, color: MIETOWA.muted }}>Etiopia Guji · owocowa, lekka</div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}

function SecLogos() {
  return (
    <section style={{ background: '#fff', padding: '32px 0', borderBottom: `1px solid ${MIETOWA.line}` }}>
      <Container>
        <div style={{ textAlign: 'center', fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 11, color: MIETOWA.muted, textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: 20 }}>Piszą o nas</div>
        <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', gap: 48, opacity: 0.55 }}>
          {['Gazeta Wyborcza', 'Kukbuk', 'Coffee Lovers', 'Wroclove', 'Slow Food'].map(n => (
            <div key={n} style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 17, color: MIETOWA.ink, fontStyle: 'italic', fontWeight: 400 }}>{n}</div>
          ))}
        </div>
      </Container>
    </section>
  );
}

function SecProblem() {
  return (
    <section style={{ background: MIETOWA.sand, padding: '100px 0' }}>
      <Container style={{ maxWidth: 820, textAlign: 'center' }}>
        <Eyebrow>Po co kolejna kawiarnia?</Eyebrow>
        <h2 style={H({ fontSize: 48, marginTop: 20, marginBottom: 20 })}>
          Bo szybka kawa z sieciówki<br/>to nie to samo.
        </h2>
        <p style={B({ fontSize: 17, maxWidth: 620, margin: '0 auto' })}>
          Każdego ranka mijasz dziesięć miejsc, gdzie kawa jest… po prostu kawą. Tymczasem dobra filiżanka to pretekst do zatrzymania się, rozmowy i doceniania chwili.
        </p>
      </Container>
    </section>
  );
}

function SecSolution() {
  const features = [
    { title: 'Własna palarnia', body: 'Surowe ziarna z małych farm w Etiopii, Kolumbii i Gwatemali. Palimy co dwa tygodnie, sprzedajemy tylko świeże.', img: PHOTOS.beans },
    { title: 'Ręczne parzenie', body: 'Chemex, V60, aeropress — każda metoda dobrana do profilu ziarna. Baristki znają swoje rzemiosło.', img: PHOTOS.pourover },
    { title: 'Lokalne ciasta', body: 'Codziennie nowe wypieki od pań z piekarni Szelągowska. Marchewkowe, makowiec, sernik krakowski.', img: PHOTOS.cake },
  ];
  return (
    <section style={{ background: '#fff', padding: '100px 0' }}>
      <Container>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <Eyebrow>Co robimy inaczej</Eyebrow>
          <h2 style={H({ fontSize: 48, marginTop: 20 })}>Palimy, parzymy, dzielimy się.</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 32 }}>
          {features.map((f, i) => (
            <div key={i}>
              <EditableImg src={f.img} alt={f.title} defaultCategory={f.title === 'Lokalne ciasta' ? 'Ciasta' : f.title === 'Ręczne parzenie' ? 'Kawa' : 'Kawa'} style={{ width: '100%', height: 280, objectFit: 'cover', borderRadius: 8, display: 'block', marginBottom: 20 }}/>
              <h3 style={H({ fontSize: 24, marginBottom: 10 })}>{f.title}</h3>
              <p style={B({ fontSize: 15 })}>{f.body}</p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}

function SecWhy() {
  const points = [
    'Kawa z plantacji pod kontrolą fair-trade',
    'Zero plastiku — kubki kompostowalne lub własny termos -2 zł',
    'Pies mile widziany, dostaje miskę wody i gratis uszko',
    'Wi-Fi, książki, ciche godziny 8–11 dla pracujących',
  ];
  return (
    <section style={{ background: '#EEF6F4', padding: '100px 0' }}>
      <Container style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center' }}>
        <div>
          <EditableImg src={PHOTOS.interior} alt="Wnętrze" defaultCategory="Wnętrze" style={{ width: '100%', height: 480, objectFit: 'cover', borderRadius: 8, display: 'block' }}/>
        </div>
        <div>
          <Eyebrow>Nasze zasady</Eyebrow>
          <h2 style={H({ fontSize: 44, marginTop: 20, marginBottom: 20 })}>
            Nie śpieszymy się.<br/>I tego uczymy.
          </h2>
          <p style={B({ fontSize: 16, marginBottom: 28 })}>
            Kawa to rytuał. Stół, przy którym siedzisz, książka, którą pożyczasz z półki, pies, którego głaszczesz — tu wszystko ma czas.
          </p>
          <div style={{ display: 'grid', gap: 14 }}>
            {points.map((p, i) => (
              <div key={i} style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                <div style={{ width: 24, height: 24, borderRadius: '50%', background: MIETOWA.mint, display: 'grid', placeItems: 'center', flexShrink: 0, marginTop: 1 }}>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={MIETOWA.ink} strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
                <p style={B({ fontSize: 15, color: MIETOWA.ink })}>{p}</p>
              </div>
            ))}
          </div>
        </div>
      </Container>
    </section>
  );
}

function SecOffer() {
  const tiers = [
    { name: 'Kawa', price: 'od 9 zł', desc: 'Espresso, cappuccino, flat white, filtr', items: ['Espresso — 9 zł', 'Cappuccino — 14 zł', 'Flat white — 16 zł', 'Chemex / V60 — 18 zł', 'Mrożona — 17 zł'], img: PHOTOS.pourover },
    { name: 'Śniadania', price: 'od 18 zł', desc: 'Do 13:00, codziennie', items: ['Jajecznica z feta — 22 zł', 'Owsianka z orzechami — 18 zł', 'Kanapka z serem kozim — 24 zł', 'Naleśniki z twarogiem — 21 zł'], img: PHOTOS.barista },
    { name: 'Ciasta', price: 'od 12 zł', desc: 'Codzienne wypieki', items: ['Sernik krakowski — 14 zł', 'Makowiec — 12 zł', 'Marchewkowe — 13 zł', 'Brownie wegańskie — 15 zł', 'Szarlotka — 12 zł'], img: PHOTOS.cake },
  ];
  return (
    <section style={{ background: '#fff', padding: '100px 0' }}>
      <Container>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <Eyebrow>Nasze menu</Eyebrow>
          <h2 style={H({ fontSize: 48, marginTop: 20 })}>Proste, dobre, bez ściemy.</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
          {tiers.map((t, i) => (
            <div key={i} style={{ border: `1px solid ${MIETOWA.line}`, borderRadius: 12, overflow: 'hidden', background: '#fff' }}>
              <EditableImg src={t.img} alt={t.name} defaultCategory={t.name === 'Ciasta' ? 'Ciasta' : t.name === 'Śniadania' ? 'Wnętrze' : 'Kawa'} style={{ width: '100%', height: 180, objectFit: 'cover', display: 'block' }}/>
              <div style={{ padding: 28 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 6 }}>
                  <h3 style={H({ fontSize: 28 })}>{t.name}</h3>
                  <span style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 16, color: '#2F6F50', fontStyle: 'italic' }}>{t.price}</span>
                </div>
                <p style={B({ fontSize: 13, marginBottom: 16, color: MIETOWA.muted })}>{t.desc}</p>
                <div style={{ borderTop: `1px solid ${MIETOWA.line}`, paddingTop: 14, display: 'grid', gap: 8 }}>
                  {t.items.map((it, j) => <div key={j} style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 14, color: MIETOWA.inkSoft }}>{it}</div>)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}

function SecTestimonials() {
  const ts = [
    { quote: 'Najlepszy flat white jaki piłam we Wrocławiu. A cisza rano — bezcenna.', author: 'Kasia W.', role: 'Dziennikarka', img: PHOTOS.people2 },
    { quote: 'Zabrałem tu rodziców z Warszawy. Mama zamówiła makowiec trzy razy.', author: 'Marcin K.', role: 'Klient od 2022', img: PHOTOS.people1 },
    { quote: 'Właściciele wiedzą jak mi na imię, jak mój pies ma na imię i jaka kawa mi smakuje. Tego nie ma nigdzie indziej.', author: 'Ania P.', role: 'Stała bywalczyni', img: PHOTOS.people3 },
  ];
  return (
    <section style={{ background: MIETOWA.cream, padding: '100px 0' }}>
      <Container>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <Eyebrow>Co mówią goście</Eyebrow>
          <h2 style={H({ fontSize: 48, marginTop: 20 })}>Nasze najlepsze recenzje.</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 28 }}>
          {ts.map((t, i) => (
            <div key={i} data-component="testimonial" style={{ background: '#fff', padding: 32, borderRadius: 12, border: `1px solid ${MIETOWA.line}` }}>
              <div style={{ display: 'flex', gap: 2, marginBottom: 16, color: '#E0A84F' }}>
                {[1,2,3,4,5].map(s => <svg key={s} width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>)}
              </div>
              <div style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 46, color: MIETOWA.mint, lineHeight: 0.5, marginBottom: 4 }}>“</div>
              <p style={{ ...B({ fontSize: 16, color: MIETOWA.ink, marginBottom: 24 }), fontStyle: 'normal' }}>{t.quote}</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <EditableImg src={t.img} alt={t.author} defaultCategory="Ludzie" style={{ width: 44, height: 44, borderRadius: '50%', objectFit: 'cover' }}/>
                <div>
                  <div style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 14, fontWeight: 600, color: MIETOWA.ink }}>{t.author}</div>
                  <div style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 12, color: MIETOWA.muted }}>{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}

function SecCTA() {
  return (
    <section style={{ background: MIETOWA.ink, padding: '100px 0', position: 'relative', overflow: 'hidden' }}>
      <EditableImg src={PHOTOS.couple} alt="" defaultCategory="Wnętrze" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.25 }}/>
      <Container style={{ position: 'relative', textAlign: 'center', maxWidth: 760 }}>
        <Eyebrow onDark>Zapraszamy</Eyebrow>
        <h2 style={H({ fontSize: 56, marginTop: 20, marginBottom: 20, color: '#fff' })}>
          Wpadnij dziś<br/>na filiżankę.
        </h2>
        <p style={B({ fontSize: 17, color: 'rgba(255,255,255,.8)', marginBottom: 32, maxWidth: 520, margin: '0 auto 32px' })}>
          Codziennie 8:00–19:00. Rezerwacja nie jest potrzebna, ale miło wiedzieć, że będziesz.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          <Btn>Zarezerwuj stolik</Btn>
          <Btn secondary onWhite>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" style={{ marginRight: 6, verticalAlign: '-2px' }}><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.12.96.37 1.9.72 2.78a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.3-1.29a2 2 0 012.11-.45c.88.35 1.82.6 2.78.72A2 2 0 0122 16.92z"/></svg>
            71 123 45 67
          </Btn>
        </div>
      </Container>
    </section>
  );
}

function SecFooter() {
  return (
    <footer style={{ background: '#0B1120', color: 'rgba(255,255,255,.7)', padding: '64px 0 32px' }}>
      <Container>
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr 1fr', gap: 48, marginBottom: 48 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              <div style={{ width: 34, height: 34, borderRadius: '50%', background: MIETOWA.mint, display: 'grid', placeItems: 'center', color: MIETOWA.ink, fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 18, fontWeight: 500 }}>M</div>
              <span style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 22, color: '#fff', fontWeight: 500 }}>Miętowa</span>
            </div>
            <p style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 14, lineHeight: 1.6, maxWidth: 320 }}>
              Kawiarnia z własną palarnią. Wrocław, Ruska 12. Codziennie 8:00–19:00.
            </p>
            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              {['FB', 'IG', 'TT'].map(s => <div key={s} style={{ width: 32, height: 32, borderRadius: '50%', border: '1px solid rgba(255,255,255,.2)', display: 'grid', placeItems: 'center', fontSize: 10, fontFamily: 'var(--font-body, Inter, sans-serif)', fontWeight: 600 }}>{s}</div>)}
            </div>
          </div>
          {[
            { title: 'Menu', links: ['Kawa', 'Śniadania', 'Ciasta', 'Lunch'] },
            { title: 'O nas', links: ['Historia', 'Palarnia', 'Zespół', 'Kariera'] },
            { title: 'Kontakt', links: ['Ruska 12, Wrocław', '71 123 45 67', 'hej@mietowa.pl', 'Mapa'] },
          ].map(col => (
            <div key={col.title}>
              <div style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 15, color: '#fff', marginBottom: 14 }}>{col.title}</div>
              <div style={{ display: 'grid', gap: 8, fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 13 }}>
                {col.links.map(l => <a key={l} style={{ color: 'inherit', textDecoration: 'none' }}>{l}</a>)}
              </div>
            </div>
          ))}
        </div>
        <div style={{ paddingTop: 24, borderTop: '1px solid rgba(255,255,255,.1)', fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 12, color: 'rgba(255,255,255,.5)', textAlign: 'center' }}>
          © 2024 Miętowa. Palimy kawę i spędzamy czas. Zrobione z miłości.
        </div>
      </Container>
    </footer>
  );
}

// ============ PAGE: HOME ============
function PageHome() {
  return (
    <div>
      <SecNav/>
      <SecHero/>
      <SecLogos/>
      <SecProblem/>
      <SecSolution/>
      <SecWhy/>
      <SecOffer/>
      <SecTestimonials/>
      <SecCTA/>
      <SecFooter/>
    </div>
  );
}

// ============ PAGE: MENU ============
function PageMenu() {
  return (
    <div>
      <SecNav/>
      <section style={{ background: MIETOWA.cream, padding: '80px 0 40px' }}>
        <Container style={{ textAlign: 'center', maxWidth: 720 }}>
          <Eyebrow>Menu</Eyebrow>
          <h1 style={H({ fontSize: 64, marginTop: 20, marginBottom: 16 })}>Co dziś podajemy.</h1>
          <p style={B({ fontSize: 17 })}>Codziennie świeże. Śniadania do 13:00, kawa i ciasta do 19:00.</p>
        </Container>
      </section>
      <SecOffer/>
      <SecOffer/>
      <SecCTA/>
      <SecFooter/>
    </div>
  );
}

// ============ PAGE: REZERWACJA ============
function PageRezerwacja() {
  return (
    <div>
      <SecNav/>
      <section style={{ background: '#fff', padding: '80px 0' }}>
        <Container style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 64, alignItems: 'center' }}>
          <div>
            <Eyebrow>Rezerwacja</Eyebrow>
            <h1 style={H({ fontSize: 52, marginTop: 20, marginBottom: 20 })}>Zarezerwuj stolik.</h1>
            <p style={B({ fontSize: 16, marginBottom: 24 })}>Nie jest potrzebna, ale miło wiedzieć, że będziesz. Odpowiadamy w 15 min.</p>
            <div style={{ display: 'grid', gap: 10, marginBottom: 20 }}>
              {[
                ['Ciche godziny', '8:00–11:00 — dla pracujących'],
                ['Psy', 'Mile widziane, miska wody gratis'],
                ['Grupy', 'Do 8 osób — zarezerwuj z wyprzedzeniem'],
              ].map(([k, v], i) => (
                <div key={i} style={{ display: 'flex', gap: 12, paddingBottom: 10, borderBottom: `1px solid ${MIETOWA.line}` }}>
                  <div style={{ width: 32, height: 32, borderRadius: '50%', background: MIETOWA.mint, display: 'grid', placeItems: 'center', flexShrink: 0 }}>✓</div>
                  <div>
                    <div style={{ fontFamily: 'var(--font-heading, Fraunces, serif)', fontSize: 16, color: MIETOWA.ink }}>{k}</div>
                    <div style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 13, color: MIETOWA.muted }}>{v}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div data-component="form" style={{ background: MIETOWA.cream, padding: 36, borderRadius: 12, border: `1px solid ${MIETOWA.line}` }}>
            <h2 style={H({ fontSize: 26, marginBottom: 20 })}>Formularz</h2>
            {[
              { l: 'Imię', v: 'Anna Kowalska' },
              { l: 'Telefon', v: '+48 601 234 567' },
              { l: 'Data', v: 'Sobota, 15 czerwca' },
              { l: 'Godzina', v: '10:30' },
              { l: 'Liczba osób', v: '2 osoby' },
            ].map((f, i) => (
              <div key={i} style={{ marginBottom: 14 }}>
                <div style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 12, color: MIETOWA.muted, marginBottom: 5 }}>{f.l}</div>
                <div data-form-field="true" style={{ padding: '11px 14px', background: '#fff', border: `1px solid ${MIETOWA.line}`, borderRadius: 8, fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 14, color: MIETOWA.ink }}>{f.v}</div>
              </div>
            ))}
            <Btn style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}>Zarezerwuj</Btn>
          </div>
        </Container>
      </section>
      <SecFooter/>
    </div>
  );
}

// ============ PAGE: KONTAKT ============
function PageKontakt() {
  return (
    <div>
      <SecNav/>
      <section style={{ background: MIETOWA.cream, padding: '80px 0 40px' }}>
        <Container style={{ textAlign: 'center', maxWidth: 720 }}>
          <Eyebrow>Kontakt</Eyebrow>
          <h1 style={H({ fontSize: 56, marginTop: 20, marginBottom: 16 })}>Wpadnij albo napisz.</h1>
          <p style={B({ fontSize: 17 })}>Ruska 12, Wrocław · 71 123 45 67 · hej@mietowa.pl</p>
        </Container>
      </section>
      <section style={{ background: '#fff', padding: '40px 0 80px' }}>
        <Container style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48 }}>
          <div style={{ background: '#EEF6F4', borderRadius: 12, overflow: 'hidden', minHeight: 420, position: 'relative', border: `1px solid ${MIETOWA.line}` }}>
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, #D4E9DC 0%, #A8D5BA 60%, #8FC5A7 100%)', opacity: 0.8 }}/>
            {/* Mapa placeholder - pattern */}
            <svg width="100%" height="100%" viewBox="0 0 400 420" style={{ position: 'absolute', inset: 0, opacity: 0.35 }}>
              {[...Array(8)].map((_, i) => <line key={'h'+i} x1="0" y1={i*60} x2="400" y2={i*60} stroke="#fff" strokeWidth="1"/>)}
              {[...Array(7)].map((_, i) => <line key={'v'+i} x1={i*60} y1="0" x2={i*60} y2="420" stroke="#fff" strokeWidth="1"/>)}
              <path d="M 40 120 Q 120 180 180 140 T 360 200" stroke="#fff" strokeWidth="3" fill="none"/>
            </svg>
            <div style={{ position: 'absolute', top: '45%', left: '50%', transform: 'translate(-50%, -50%)', background: MIETOWA.accent, color: '#fff', padding: '10px 16px', borderRadius: 8, fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 13, fontWeight: 600, boxShadow: '0 6px 20px rgba(0,0,0,.25)' }}>📍 Miętowa, Ruska 12</div>
          </div>
          <div>
            <h2 style={H({ fontSize: 30, marginBottom: 20 })}>Godziny otwarcia</h2>
            <div style={{ display: 'grid', gap: 8, marginBottom: 28 }}>
              {[['Poniedziałek–Piątek', '8:00 – 19:00'], ['Sobota', '9:00 – 20:00'], ['Niedziela', '9:00 – 18:00']].map(([d, h], i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: `1px solid ${MIETOWA.line}`, fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 15 }}>
                  <span style={{ color: MIETOWA.inkSoft }}>{d}</span>
                  <span style={{ color: MIETOWA.ink, fontWeight: 600 }}>{h}</span>
                </div>
              ))}
            </div>
            <h2 style={H({ fontSize: 24, marginBottom: 16 })}>Najszybciej:</h2>
            <div style={{ display: 'grid', gap: 10 }}>
              {[
                [<svg key="p" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.12.96.37 1.9.72 2.78a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.3-1.29a2 2 0 012.11-.45c.88.35 1.82.6 2.78.72A2 2 0 0122 16.92z"/></svg>, '71 123 45 67', 'Pon–Pt 8–17'],
                [<svg key="e" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>, 'hej@mietowa.pl', 'Odpisujemy w 24h'],
                [<svg key="i" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1112.63 8 4 4 0 0116 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>, '@mietowa.wroclaw', 'Instagram']
              ].map(([i, t, s], k) => (
                <div key={k} style={{ display: 'flex', gap: 14, alignItems: 'center', padding: 14, background: MIETOWA.cream, borderRadius: 10 }}>
                  <div style={{ display: 'grid', placeItems: 'center', width: 36, height: 36, background: '#fff', borderRadius: 8, color: MIETOWA.ink }}>{i}</div>
                  <div>
                    <div style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 15, fontWeight: 600, color: MIETOWA.ink }}>{t}</div>
                    <div style={{ fontFamily: 'var(--font-body, Inter, sans-serif)', fontSize: 12, color: MIETOWA.muted }}>{s}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Container>
      </section>
      <SecFooter/>
    </div>
  );
}

// Export
export const MietowaPages = {
  home: PageHome,
  menu: PageMenu,
  rezerwacja: PageRezerwacja,
  kontakt: PageKontakt,
};
