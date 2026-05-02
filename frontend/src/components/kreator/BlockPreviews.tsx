// BlockPreviews — adaptacja z makiety previews.jsx (562 linii)
// Hybrid preview: wireframe (szare paski = tekst) + realne CTA w kolorze + ramka obrazu
// Zachowany inline style 1:1

import React from 'react';

// ─── Helpers ───────────────────────────────────────────
const Bar = ({ w = '70%', h = 3, c = '#94A3B8', mb = 5, style = {} }: { w?: string | number; h?: number; c?: string; mb?: number; style?: React.CSSProperties }) => (
  <div style={{ width: w, height: h, background: c, borderRadius: h / 2, marginBottom: mb, ...style }} />
);
const BigBar = ({ w = '80%', mb = 6, c = '#334155', style = {} }: { w?: string | number; mb?: number; c?: string; style?: React.CSSProperties }) => <Bar w={w} h={10} c={c} mb={mb} style={style} />;
const Chip = ({ children, bg = 'rgba(255,255,255,.7)', fg = '#6366F1', invert }: { children: React.ReactNode; bg?: string; fg?: string; invert?: boolean }) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center', gap: 4,
    background: invert ? 'rgba(255,255,255,.15)' : bg,
    color: invert ? '#fff' : fg,
    fontSize: 10, fontWeight: 600,
    padding: '3px 8px', borderRadius: 10, marginBottom: 8,
    letterSpacing: 0.2,
  }}>{children}</span>
);

const BrandCtx = React.createContext({ cta: '#6366F1', ctaSecondary: '#EC4899' });

const CTA = ({ w, text = 'CTA', style = {}, variant = 'primary' }: { w?: string | number; text?: string; style?: React.CSSProperties; variant?: string }) => {
  const b = React.useContext(BrandCtx);
  const ctaIsGradient = typeof b.cta === 'string' && b.cta.includes('gradient');
  const primaryBg = ctaIsGradient ? b.cta : `linear-gradient(135deg, ${b.cta}, ${b.ctaSecondary})`;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      background: variant === 'primary' ? primaryBg : 'transparent',
      color: variant === 'primary' ? '#fff' : '#334155',
      border: variant === 'primary' ? 'none' : '1.5px solid #334155',
      borderRadius: 6, padding: '7px 14px', fontSize: 10, fontWeight: 600,
      width: w, justifyContent: 'center',
      ...style,
    }}>{text} <span style={{ fontSize: 11 }}>{'\u2192'}</span></span>
  );
};

const ImgFrame = ({ style = {}, ratio = '4/3', dark, icon = 'image', src }: { style?: React.CSSProperties; ratio?: string; dark?: boolean; icon?: string; src?: string }) => (
  <div style={{
    aspectRatio: ratio,
    background: src ? `url(${src}) center/cover no-repeat` : (dark ? 'rgba(255,255,255,.08)' : '#E2E8F0'),
    border: src ? 'none' : `1.5px dashed ${dark ? 'rgba(255,255,255,.35)' : '#94A3B8'}`,
    borderRadius: 8, display: src ? 'block' : 'grid', placeItems: 'center',
    color: dark ? 'rgba(255,255,255,.5)' : '#64748B',
    width: '100%',
    ...style,
  }}>
    {!src && icon === 'image' && <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>}
    {!src && icon === 'play' && <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>}
    {!src && icon === 'user' && <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z"/></svg>}
  </div>
);

const iconPaths: Record<string, string> = {
  check: 'M20 6L9 17l-5-5',
  star: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z',
  warn: 'M12 9v3m0 3h.01M10.29 3.86l-8.14 14A2 2 0 003.86 21h16.28a2 2 0 001.71-3.14l-8.14-14a2 2 0 00-3.42 0z',
  sparkle: 'M12 3v4M12 17v4M3 12h4M17 12h4',
  arrow: 'M5 12h14M13 5l7 7-7 7',
  phone: 'M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z',
};
const Icon = ({ name, size = 14, c = '#6366F1' }: { name: string; size?: number; c?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d={iconPaths[name] || ''} /></svg>
);

function getTextColors(bg: string | null) {
  if (!bg) return { big: '#334155', small: '#94A3B8', chipBg: 'rgba(99,102,241,.1)', chipFg: '#6366F1', dark: false };
  const hex = bg.replace('#', '');
  if (hex.length < 6) return { big: '#334155', small: '#94A3B8', chipBg: 'rgba(99,102,241,.1)', chipFg: '#6366F1', dark: false };
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const lum = (0.299 * r + 0.587 * g + 0.114 * b);
  const dark = lum < 128;
  return dark
    ? { big: '#fff', small: 'rgba(255,255,255,.55)', chipBg: 'rgba(255,255,255,.12)', chipFg: '#fff', dark: true }
    : { big: '#334155', small: '#94A3B8', chipBg: 'rgba(99,102,241,.1)', chipFg: '#6366F1', dark: false };
}

// ─── Previews per block type ───────────────────────────
type PreviewFn = (bg: string | null) => React.ReactNode;

const Previews: Record<string, PreviewFn> = {
  NA1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: '16px 22px', height: '100%', display: 'flex', alignItems: 'center', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ width: 18, height: 18, borderRadius: 5, background: c.dark ? '#fff' : '#0F172A' }} />
        <BigBar w={50} mb={0} c={c.big} />
      </div>
      <div style={{ flex: 1 }} />
      <Bar w={28} h={4} c={c.small} mb={0} /><Bar w={28} h={4} c={c.small} mb={0} /><Bar w={28} h={4} c={c.small} mb={0} />
      <div style={{ marginLeft: 10 }}><CTA text="CTA" /></div>
    </div>
  ); },
  NA2: (bg) => Previews.NA1(bg || '#0F172A'),
  NA3: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: '16px 22px', height: '100%', display: 'flex', alignItems: 'center', gap: 20 }}>
      <div style={{ width: 18, height: 18, borderRadius: 5, background: c.dark ? '#fff' : '#0F172A' }} />
      <div style={{ flex: 1 }} />
      <Bar w={36} h={4} c={c.small} mb={0} />
      <div><Bar w={36} h={4} c={c.big} mb={2} /><Bar w={36} h={2} c={c.big} mb={0} /></div>
      <Bar w={36} h={4} c={c.small} mb={0} />
      <div style={{ flex: 1 }} />
      <CTA text="Kontakt" />
    </div>
  ); },

  HE1: (bg) => { const c = getTextColors(bg || '#0F172A'); return (
    <div style={{ padding: 32, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <BigBar w="65%" mb={8} c={c.big} /><BigBar w="45%" mb={14} c={c.big} />
      <Bar w="55%" c={c.small} mb={4} /><Bar w="40%" c={c.small} mb={16} />
      <div style={{ display: 'flex', gap: 8, marginBottom: 22 }}><CTA text="Umow rozmowe" /><CTA text="Zobacz oferte" variant="ghost" style={{ color: c.big, borderColor: c.big }} /></div>
      <div style={{ display: 'flex', gap: 24, paddingTop: 14, borderTop: `1px solid ${c.small}33`, width: '80%', justifyContent: 'space-around' }}>
        {['120+','15 lat','98%','4.9'].map((s,i) => <div key={i} style={{ textAlign: 'center' }}>
          <div style={{ fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 20, color: c.big, fontWeight: 400 }}>{s}</div>
          <Bar w={32} h={2} c={c.small} mb={0} style={{ margin: '4px auto 0' }} />
        </div>)}
      </div>
    </div>
  ); },

  HE2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 24, alignItems: 'center' }}>
      <div>
        <Chip bg={c.chipBg} fg={c.chipFg}>NOWOSC</Chip>
        <BigBar w="95%" mb={6} c={c.big} /><BigBar w="70%" mb={14} c={c.big} />
        <Bar w="100%" c={c.small} /><Bar w="90%" c={c.small} /><Bar w="75%" c={c.small} mb={16} />
        <CTA text="Umow konsultacje" />
      </div>
      <ImgFrame ratio="4/5" dark={c.dark} />
    </div>
  ); },

  HE3: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'center' }}>
      <div>
        <BigBar w="90%" mb={6} c={c.big} /><BigBar w="65%" mb={14} c={c.big} />
        <Bar w="95%" c={c.small} /><Bar w="80%" c={c.small} mb={14} />
        {[1,2].map(i => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}><Icon name="check" size={13} c={c.chipFg}/><Bar w={110} c={c.small} mb={0}/></div>)}
      </div>
      <div style={{ background: c.dark ? 'rgba(255,255,255,.08)' : '#fff', border: `1px solid ${c.dark ? 'rgba(255,255,255,.15)' : '#E2E8F0'}`, borderRadius: 10, padding: 16 }}>
        <Bar w="35%" h={3} c={c.chipFg} mb={10} />
        {[1,2,3].map(i => <div key={i} style={{ marginBottom: 8 }}><Bar w={40} h={2} c={c.small}/><div style={{ height: 22, background: c.dark ? 'rgba(255,255,255,.08)' : '#F1F5F9', borderRadius: 4, marginTop: 3 }}/></div>)}
        <CTA text="Wyslij" style={{ width: '100%', marginTop: 4 }} />
      </div>
    </div>
  ); },

  HE4: (bg) => { return (
    <div style={{ padding: 0, height: '100%', position: 'relative', background: 'linear-gradient(135deg, #1E293B, #0F172A)', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 28, background: 'rgba(15,23,42,.55)' }}>
        <Chip invert>VIDEO</Chip>
        <BigBar w="70%" mb={6} c="#fff" /><BigBar w="50%" mb={14} c="#fff" />
        <Bar w="45%" c="rgba(255,255,255,.5)" mb={16}/>
        <CTA text="Zobacz video" />
      </div>
    </div>
  ); },

  HE5: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 40, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <BigBar w="55%" mb={6} c={c.big} /><BigBar w="35%" mb={14} c={c.big} />
      <Bar w="40%" c={c.small} mb={16}/><CTA text="Zacznij" />
    </div>
  ); },

  PB1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 18 }}><BigBar w="40%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {[1,2,3,4].map(i => <div key={i} style={{ padding: 12, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 8, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}` }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}><Icon name="warn" size={14} c="#F59E0B"/><Bar w={60} h={4} c={c.big} mb={0}/></div>
          <Bar w="95%" c={c.small}/><Bar w="70%" c={c.small} mb={0}/>
        </div>)}
      </div>
    </div>
  ); },

  PB2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 14 }}>
      {[85, 78, 70].map((w,i) => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 28, color: c.chipFg, fontStyle: 'italic', lineHeight: 1 }}>"</div>
        <div style={{ flex: 1 }}><Bar w={`${w}%`} h={4} c={c.big}/><Bar w={`${w-20}%`} h={4} c={c.big} mb={0}/></div>
      </div>)}
    </div>
  ); },

  PB3: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center', marginBottom: 20 }}><BigBar w="35%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, textAlign: 'center' }}>
        {['67%','3x','45min'].map((s,i) => <div key={i}>
          <div style={{ fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 36, color: '#EF4444', fontWeight: 400, lineHeight: 1 }}>{s}</div>
          <Bar w="80%" c={c.small} style={{ margin: '8px auto 2px' }}/><Bar w="60%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
        </div>)}
      </div>
    </div>
  ); },

  RO1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 18 }}><BigBar w="35%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {[1,2,3].map(i => <div key={i} style={{ padding: 16, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 10, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}`, textAlign: 'center' }}>
          <div style={{ width: 34, height: 34, borderRadius: 8, background: 'linear-gradient(135deg, #6366F1, #EC4899)', margin: '0 auto 8px', display: 'grid', placeItems: 'center' }}><Icon name="star" c="#fff" size={16}/></div>
          <Bar w="70%" h={4} c={c.big} style={{ margin: '0 auto 6px' }}/><Bar w="90%" c={c.small} style={{ margin: '0 auto' }}/><Bar w="70%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
        </div>)}
      </div>
    </div>
  ); },

  RO2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'center' }}>
      <div>
        <BigBar w="80%" mb={14} c={c.big}/>
        {[1,2,3,4].map(i => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}><Icon name="check" c={c.chipFg}/><Bar w={130} c={c.small} mb={0}/></div>)}
        <div style={{ marginTop: 14 }}><CTA text="Dowiedz sie wiecej" /></div>
      </div>
      <ImgFrame dark={c.dark} />
    </div>
  ); },

  KR1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {[1,2,3,4,5,6].map(i => <div key={i}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}><Icon name="star" c={c.chipFg} size={12}/><Bar w={50} h={3} c={c.big} mb={0}/></div>
          <Bar w="90%" c={c.small}/><Bar w="70%" c={c.small} mb={0}/>
        </div>)}
      </div>
    </div>
  ); },

  KR2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, alignItems: 'center', textAlign: 'center' }}>
      {['120+','15','98%','3x'].map((s,i) => <div key={i}>
        <div style={{ fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 44, color: c.big, fontWeight: 400, lineHeight: 1 }}>{s}</div>
        <Bar w="70%" c={c.small} style={{ margin: '10px auto 3px' }}/><Bar w="50%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
      </div>)}
    </div>
  ); },

  CF1: (bg) => Previews.RO1(bg),
  CF2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, alignContent: 'center' }}>
      {[1,2,3,4,5,6,7,8].map(i => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 18, height: 18, borderRadius: '50%', background: 'rgba(16,185,129,.15)', display: 'grid', placeItems: 'center' }}><Icon name="check" size={11} c="#10B981"/></div>
        <Bar w={120} c={c.big} mb={0}/>
      </div>)}
    </div>
  ); },

  OB1: (bg) => Previews.FA1(bg),

  FI1: (bg) => Previews.HE2(bg),
  FI2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1.1fr', gap: 24, alignItems: 'center' }}>
      <ImgFrame ratio="4/5" dark={c.dark} />
      <div>
        <Chip bg={c.chipBg} fg={c.chipFg}>O NAS</Chip>
        <BigBar w="90%" mb={10} c={c.big}/><Bar w="100%" c={c.small}/><Bar w="95%" c={c.small}/><Bar w="85%" c={c.small}/><Bar w="70%" c={c.small} mb={14}/>
        <CTA text="Poznaj nas" />
      </div>
    </div>
  ); },
  FI3: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 30, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <BigBar w="40%" mb={12} c={c.big}/><Bar w="70%" c={c.small}/><Bar w="65%" c={c.small}/><Bar w="55%" c={c.small} mb={18}/>
      <div style={{ fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 22, color: c.chipFg, fontStyle: 'italic', marginBottom: 6 }}>"</div>
      <Bar w="60%" c={c.big}/><Bar w="50%" c={c.big} mb={10}/>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 24, height: 24, borderRadius: '50%', background: 'linear-gradient(135deg, #EC4899, #F59E0B)' }}/>
        <Bar w={90} c={c.small} mb={0}/>
      </div>
    </div>
  ); },
  FI4: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      {['2010','2015','2020','2024'].map((y,i) => <div key={i} style={{ display: 'flex', gap: 14, marginBottom: 10, alignItems: 'flex-start' }}>
        <div style={{ fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 16, color: c.chipFg, minWidth: 40, fontStyle: 'italic' }}>{y}</div>
        <div style={{ width: 10, height: 10, borderRadius: '50%', background: c.chipFg, marginTop: 4, flexShrink: 0, border: `2px solid ${bg || '#fff'}`, boxShadow: `0 0 0 1px ${c.chipFg}` }}/>
        <div style={{ flex: 1 }}><Bar w={70} h={4} c={c.big}/><Bar w="90%" c={c.small} mb={0}/></div>
      </div>)}
    </div>
  ); },

  OF1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {[1,2,3].map(i => <div key={i} style={{ padding: 14, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 10, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}` }}>
          <Icon name="star" c={c.chipFg} size={16}/>
          <Bar w="75%" h={4} c={c.big} style={{ marginTop: 8 }}/><Bar w="95%" c={c.small}/><Bar w="80%" c={c.small} mb={8}/>
          <div style={{ fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 18, color: c.big }}>od 2000 zl</div>
          <div style={{ marginTop: 8 }}><CTA text="Wiecej" style={{ width: '100%' }}/></div>
        </div>)}
      </div>
    </div>
  ); },

  OF2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 26, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      {[1,2,3,4].map(i => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0', borderBottom: i<4 ? `1px solid ${c.small}22` : 'none' }}>
        <div style={{ width: 26, height: 26, borderRadius: 7, background: c.chipBg, display: 'grid', placeItems: 'center' }}><Icon name="star" c={c.chipFg} size={13}/></div>
        <Bar w={80} h={4} c={c.big} mb={0}/><span style={{ color: c.small, fontSize: 10 }}>—</span><Bar w={140} c={c.small} mb={0}/>
      </div>)}
    </div>
  ); },

  PR1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 16 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {[1,2,3,4].map((n,i) => <React.Fragment key={i}>
          <div style={{ flex: 1, textAlign: 'center' }}>
            <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg, #6366F1, #EC4899)', color: '#fff', display: 'grid', placeItems: 'center', margin: '0 auto 8px', fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 16 }}>{n}</div>
            <Bar w="80%" h={4} c={c.big} style={{ margin: '0 auto 4px' }}/><Bar w="60%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
          </div>
          {i<3 && <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={c.small} strokeWidth="2"><path d="M5 12h14M13 5l7 7-7 7"/></svg>}
        </React.Fragment>)}
      </div>
    </div>
  ); },

  PR2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 26, height: '100%' }}>
      {[1,2,3,4].map((n,i) => <div key={i} style={{ display: 'flex', gap: 14, paddingBottom: 12, position: 'relative' }}>
        <div style={{ position: 'relative' }}>
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg, #6366F1, #EC4899)', color: '#fff', display: 'grid', placeItems: 'center', fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 14 }}>{n}</div>
          {i<3 && <div style={{ position: 'absolute', left: 13, top: 28, width: 2, height: 32, background: `${c.small}44` }}/>}
        </div>
        <div style={{ flex: 1 }}><Bar w={120} h={4} c={c.big}/><Bar w="90%" c={c.small} mb={0}/></div>
      </div>)}
    </div>
  ); },

  OP1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="35%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {[1,2,3].map(i => <div key={i} style={{ padding: 14, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 10, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}` }}>
          <div style={{ display: 'flex', gap: 2, marginBottom: 8 }}>{[1,2,3,4,5].map(s => <Icon key={s} name="star" c="#F59E0B" size={10}/>)}</div>
          <Bar w="100%" c={c.big}/><Bar w="95%" c={c.big}/><Bar w="80%" c={c.big} mb={10}/>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 22, height: 22, borderRadius: '50%', background: ['linear-gradient(135deg,#EC4899,#F59E0B)','linear-gradient(135deg,#6366F1,#06B6D4)','linear-gradient(135deg,#10B981,#14B8A6)'][i-1] }}/>
            <div><Bar w={50} h={3} c={c.big}/><Bar w={60} h={2} c={c.small} mb={0}/></div>
          </div>
        </div>)}
      </div>
    </div>
  ); },

  OP2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 30, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <div style={{ display: 'flex', gap: 3, marginBottom: 14 }}>{[1,2,3,4,5].map(s => <Icon key={s} name="star" c="#F59E0B" size={14}/>)}</div>
      <Bar w="75%" c={c.big}/><Bar w="85%" c={c.big}/><Bar w="65%" c={c.big} mb={20}/>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg,#EC4899,#F59E0B)' }}/>
        <div style={{ textAlign: 'left' }}><Bar w={80} h={4} c={c.big}/><Bar w={60} h={2} c={c.small} mb={0}/></div>
      </div>
    </div>
  ); },

  ZE1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
        {[1,2,3,4].map(i => <div key={i} style={{ textAlign: 'center' }}>
          <ImgFrame ratio="1/1" dark={c.dark} icon="user" style={{ marginBottom: 8 }}/>
          <Bar w="70%" h={4} c={c.big} style={{ margin: '0 auto 3px' }}/><Bar w="50%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
        </div>)}
      </div>
    </div>
  ); },

  ZE2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, alignContent: 'center' }}>
      {[1,2].map(i => <div key={i} style={{ display: 'flex', gap: 10 }}>
        <ImgFrame ratio="3/4" dark={c.dark} icon="user" style={{ width: 60 }}/>
        <div style={{ flex: 1 }}><Bar w={90} h={4} c={c.big}/><Bar w={60} h={2} c={c.chipFg} mb={6}/><Bar w="95%" c={c.small}/><Bar w="80%" c={c.small} mb={0}/></div>
      </div>)}
    </div>
  ); },

  CE1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="25%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {['Basic','Premium','Enterprise'].map((p,i) => <div key={i} style={{ padding: 14, background: i===1 ? 'linear-gradient(135deg, #6366F1, #EC4899)' : (c.dark ? 'rgba(255,255,255,.06)' : '#fff'), color: i===1 ? '#fff' : c.big, borderRadius: 10, border: `1px solid ${i===1 ? 'transparent' : (c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0')}`, textAlign: 'center', position: 'relative' }}>
          {i===1 && <div style={{ position: 'absolute', top: -8, left: '50%', transform: 'translateX(-50%)', background: '#F59E0B', color: '#fff', fontSize: 8, fontWeight: 700, padding: '2px 7px', borderRadius: 6 }}>POLECANY</div>}
          <div style={{ fontSize: 10, fontWeight: 600, opacity: .7 }}>{p.toUpperCase()}</div>
          <div style={{ fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 28, marginTop: 4 }}>{['99','199','499'][i]} zl</div>
          <div style={{ fontSize: 9, opacity: .6 }}>/mies</div>
          <div style={{ height: 1, background: i===1 ? 'rgba(255,255,255,.2)' : `${c.small}33`, margin: '8px 0' }}/>
          {[1,2,3].map(j => <div key={j} style={{ fontSize: 9, display: 'flex', alignItems: 'center', gap: 4, marginBottom: 3, opacity: .9 }}><Icon name="check" size={10} c={i===1 ? '#fff' : c.chipFg}/>Cecha {j}</div>)}
          <div style={{ marginTop: 8 }}><CTA text="Wybierz" style={{ width: '100%', background: i===1 ? '#fff' : 'linear-gradient(135deg, #6366F1, #EC4899)', color: i===1 ? '#6366F1' : '#fff' }}/></div>
        </div>)}
      </div>
    </div>
  ); },

  CT1: (bg) => { const c = getTextColors(bg || '#0F172A'); return (
    <div style={{ padding: 32, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <BigBar w="55%" mb={8} c={c.big}/><Bar w="40%" c={c.small} mb={16}/><CTA text="Umow konsultacje" />
    </div>
  ); },

  CT2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 24, alignItems: 'center' }}>
      <div><BigBar w="85%" mb={6} c={c.big}/><Bar w="70%" c={c.small} mb={14}/><CTA text="Umow rozmowe" /></div>
      <ImgFrame ratio="4/3" dark={c.dark} />
    </div>
  ); },

  CT3: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: '16px 24px', height: '100%', display: 'flex', alignItems: 'center', gap: 14 }}>
      <Bar w={180} h={5} c={c.big} mb={0}/><div style={{ flex: 1 }}/><CTA text="Kontakt" />
    </div>
  ); },

  KO1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%', display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 20 }}>
      <div style={{ padding: 14, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 10, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}` }}>
        <Bar w={80} h={4} c={c.big} mb={10}/>
        {['Imie','Email','Temat'].map((l,i) => <div key={i} style={{ marginBottom: 7 }}><Bar w={40} h={2} c={c.small}/><div style={{ height: 20, background: c.dark ? 'rgba(255,255,255,.08)' : '#F1F5F9', borderRadius: 4, marginTop: 3 }}/></div>)}
        <div style={{ height: 40, background: c.dark ? 'rgba(255,255,255,.08)' : '#F1F5F9', borderRadius: 4, marginTop: 3, marginBottom: 8 }}/>
        <CTA text="Wyslij" style={{ width: '100%' }}/>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, justifyContent: 'center' }}>
        {[{i:'phone'}, {i:'star'}, {i:'star'}].map((r,idx) => <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 26, height: 26, borderRadius: 7, background: c.chipBg, display: 'grid', placeItems: 'center' }}><Icon name={r.i} c={c.chipFg} size={13}/></div>
          <Bar w={110} c={c.big} mb={0}/>
        </div>)}
      </div>
    </div>
  ); },

  FA1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="35%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      {[{open:true},{open:false},{open:false},{open:false}].map((q,i) => <div key={i} style={{ padding: '10px 12px', background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 8, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}`, marginBottom: 6 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Bar w={180} h={4} c={c.big} mb={0}/><div style={{ flex: 1 }}/><span style={{ color: c.small, fontSize: 12 }}>{q.open ? '\u25BC' : '\u25B8'}</span></div>
        {q.open && <div style={{ marginTop: 7 }}><Bar w="95%" c={c.small}/><Bar w="80%" c={c.small} mb={0}/></div>}
      </div>)}
    </div>
  ); },

  RE1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {[1,2,3].map((_,i) => <div key={i}>
          <ImgFrame ratio="4/3" dark={c.dark} style={{ marginBottom: 8 }}/>
          <Bar w="70%" h={4} c={c.big}/><Bar w="50%" c={c.small} mb={0}/>
        </div>)}
      </div>
    </div>
  ); },

  LO1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: 26, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><Bar w="25%" h={4} c={c.small} mb={0} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', gap: 16, opacity: .65 }}>
        {[1,2,3,4,5].map(i => <div key={i} style={{ width: 60, height: 24, borderRadius: 4, background: `linear-gradient(135deg, ${c.small}66, ${c.small}33)`, display: 'grid', placeItems: 'center', fontSize: 9, color: c.big, fontWeight: 600 }}>LOGO {i}</div>)}
      </div>
    </div>
  ); },

  ST1: (bg) => Previews.KR2(bg),

  FO1: (bg) => { const c = getTextColors(bg || '#0F172A'); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr 1fr 1fr', gap: 16, marginBottom: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <div style={{ width: 18, height: 18, borderRadius: 4, background: c.big }}/>
            <Bar w={60} h={4} c={c.big} mb={0}/>
          </div>
          <Bar w="90%" c={c.small}/><Bar w="70%" c={c.small} mb={10}/>
          <div style={{ display: 'flex', gap: 6 }}>
            {[1,2,3,4].map(s => <div key={s} style={{ width: 20, height: 20, borderRadius: '50%', background: `${c.big}22` }}/>)}
          </div>
        </div>
        {['Uslugi','O nas','Kontakt'].map((h,i) => <div key={i}>
          <Bar w={50} h={4} c={c.big}/>
          {[1,2,3,4].map(l => <Bar key={l} w={70} c={c.small}/>)}
        </div>)}
      </div>
      <div style={{ paddingTop: 10, borderTop: `1px solid ${c.small}33`, display: 'flex' }}>
        <Bar w={160} c={c.small} mb={0}/><div style={{ flex: 1 }}/><Bar w={80} c={c.small} mb={0}/>
      </div>
    </div>
  ); },

  // ═══ OFFER BLOCKS — NO, DW, CTA ═══

  // NO1 — Nagłówek standard (zdjęcie w tle + tytuł + logo)
  NO1: (bg) => { return (
    <div style={{ padding: 0, height: '100%', background: '#1E293B', display: 'flex', flexDirection: 'column' }}>
      <ImgFrame ratio="16/7" dark style={{ borderRadius: 0, flex: '0 0 60%' }} />
      <div style={{ padding: '16px 20px', flex: 1 }}>
        <Chip bg="rgba(167,139,250,0.2)" fg="#A78BFA">OFERTA</Chip>
        <BigBar w="75%" c="#E2E8F0" mb={8} />
        <Bar w="55%" c="#94A3B8" mb={4} />
        <Bar w="40%" c="#64748B" mb={0} />
      </div>
      <div style={{ position: 'absolute', top: 12, right: 12, width: 28, height: 20, background: '#fff', borderRadius: 4 }} />
    </div>
  );},

  // NO2 — Nagłówek pełnoekranowy (wielkie zdjęcie + tekst na dole)
  NO2: (bg) => { return (
    <div style={{ padding: 0, height: '100%', background: '#0F172A', display: 'flex', flexDirection: 'column' }}>
      <ImgFrame ratio="16/9" dark style={{ borderRadius: 0, flex: 1 }} />
      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '20px', background: 'linear-gradient(transparent, rgba(0,0,0,0.8))' }}>
        <BigBar w="65%" c="#E2E8F0" mb={6} />
        <Bar w="45%" c="#94A3B8" />
      </div>
    </div>
  );},

  // DW1 — Obraz lewo + Tekst prawo
  DW1: (bg) => { const c = getTextColors(bg); return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', height: '100%' }}>
      <ImgFrame ratio="auto" style={{ borderRadius: 0, height: '100%' }} />
      <div style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 6 }}>
        <Chip fg="#8B7355" bg="rgba(139,115,85,0.1)">SEKCJA</Chip>
        <BigBar w="80%" c={c.big} />
        <Bar w="95%" c={c.small} />
        <Bar w="85%" c={c.small} />
        <Bar w="70%" c={c.small} />
      </div>
    </div>
  );},

  // DW2 — Tekst lewo + Obraz prawo
  DW2: (bg) => { const c = getTextColors(bg); return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', height: '100%' }}>
      <div style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 6 }}>
        <Chip fg="#8B7355" bg="rgba(139,115,85,0.1)">SEKCJA</Chip>
        <BigBar w="80%" c={c.big} />
        <Bar w="95%" c={c.small} />
        <Bar w="85%" c={c.small} />
        <Bar w="70%" c={c.small} />
      </div>
      <ImgFrame ratio="auto" style={{ borderRadius: 0, height: '100%' }} />
    </div>
  );},

  // DW3 — Obraz góra + Tekst dół
  DW3: (bg) => { const c = getTextColors(bg); return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <ImgFrame ratio="16/7" style={{ borderRadius: 0, flex: '0 0 55%' }} />
      <div style={{ padding: '16px 20px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 5 }}>
        <Chip fg="#8B7355" bg="rgba(139,115,85,0.1)">SEKCJA</Chip>
        <BigBar w="70%" c={c.big} />
        <Bar w="90%" c={c.small} />
        <Bar w="75%" c={c.small} />
      </div>
    </div>
  );},

  // DW4 — 2 kolumny (obrazy + teksty)
  DW4: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: '16px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Chip fg="#8B7355" bg="rgba(139,115,85,0.1)">2 KOLUMNY</Chip>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, flex: 1, marginTop: 8 }}>
        <div><ImgFrame ratio="4/3" style={{ marginBottom: 6, borderRadius: 6 }} /><BigBar w="75%" c={c.big} mb={4} /><Bar w="90%" c={c.small} /></div>
        <div><ImgFrame ratio="4/3" style={{ marginBottom: 6, borderRadius: 6 }} /><BigBar w="75%" c={c.big} mb={4} /><Bar w="90%" c={c.small} /></div>
      </div>
    </div>
  );},

  // DW5 — 3 kolumny
  DW5: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: '16px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Chip fg="#8B7355" bg="rgba(139,115,85,0.1)">3 KOLUMNY</Chip>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, flex: 1, marginTop: 8 }}>
        {[1,2,3].map(i => <div key={i}><ImgFrame ratio="4/3" style={{ marginBottom: 5, borderRadius: 5 }} /><Bar w="80%" h={5} c={c.big} mb={3} /><Bar w="95%" c={c.small} h={2} /></div>)}
      </div>
    </div>
  );},

  // DW6 — 4 kolumny
  DW6: (bg) => { const c = getTextColors(bg); return (
    <div style={{ padding: '16px 14px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Chip fg="#8B7355" bg="rgba(139,115,85,0.1)">4 KOLUMNY</Chip>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 6, flex: 1, marginTop: 8 }}>
        {[1,2,3,4].map(i => <div key={i}><ImgFrame ratio="1/1" style={{ marginBottom: 4, borderRadius: 4 }} /><Bar w="80%" h={4} c={c.big} mb={2} /><Bar w="95%" c={c.small} h={2} /></div>)}
      </div>
    </div>
  );},

  // DW7 — Obrazy lewo + Teksty prawo (kolumny)
  DW7: (bg) => { const c = getTextColors(bg); return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', height: '100%' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: 10 }}>
        <ImgFrame ratio="3/2" style={{ flex: 1, borderRadius: 6 }} />
        <ImgFrame ratio="3/2" style={{ flex: 1, borderRadius: 6 }} />
        <ImgFrame ratio="3/2" style={{ flex: 1, borderRadius: 6 }} />
      </div>
      <div style={{ padding: '20px 16px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 16 }}>
        <div><Bar w="70%" h={5} c={c.big} mb={3} /><Bar w="90%" c={c.small} h={2} /></div>
        <div><Bar w="65%" h={5} c={c.big} mb={3} /><Bar w="85%" c={c.small} h={2} /></div>
        <div><Bar w="75%" h={5} c={c.big} mb={3} /><Bar w="80%" c={c.small} h={2} /></div>
      </div>
    </div>
  );},

  // DW8 — Cytat z obrazem w tle
  DW8: (bg) => { return (
    <div style={{ height: '100%', background: '#1E293B', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
      <ImgFrame ratio="auto" dark style={{ position: 'absolute', inset: 0, borderRadius: 0, opacity: 0.3 }} />
      <div style={{ textAlign: 'center', padding: 20, position: 'relative', zIndex: 1 }}>
        <div style={{ width: 30, height: 2, background: '#C4A87A', margin: '0 auto 12px' }} />
        <BigBar w="85%" c="#E2E8F0" mb={6} style={{ margin: '0 auto 6px' }} />
        <Bar w="60%" c="#C4A87A" style={{ margin: '0 auto' }} />
        <div style={{ width: 30, height: 2, background: '#C4A87A', margin: '12px auto 0' }} />
      </div>
    </div>
  );},

  // CTA1 — Zaproszenie do kontaktu
  CTA1: (bg) => { return (
    <div style={{ height: '100%', background: '#111827', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center', padding: 20 }}>
        <BigBar w="70%" c="#E2E8F0" mb={8} style={{ margin: '0 auto 8px' }} />
        <Bar w="55%" c="#6B7280" mb={12} style={{ margin: '0 auto 12px' }} />
        <CTA text="Akceptuję ofertę" />
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 12 }}>
          <Bar w={40} c="#4B5563" h={2} mb={0} />
          <Bar w={50} c="#818CF8" h={2} mb={0} />
          <Bar w={40} c="#4B5563" h={2} mb={0} />
        </div>
      </div>
    </div>
  );},
};

// ─── BlockPreview — glowny eksport ────────────────────
export default function BlockPreview({ code, bg, brand }: {
  code: string;
  bg?: string;
  brand?: { cta: string; ctaSecondary: string };
}) {
  const fn = Previews[code] || (() => <div style={{ padding: 20, textAlign: 'center', color: '#94A3B8' }}>Podglad {code} (TBD)</div>);
  const b = brand || { cta: '#6366F1', ctaSecondary: '#EC4899' };
  return (
    <BrandCtx.Provider value={b}>
      <div style={{
        background: bg,
        borderRadius: 12,
        width: '100%',
        height: '100%',
        minHeight: 280,
        overflow: 'hidden',
        position: 'relative',
      }}>
        {fn(bg || null)}
      </div>
    </BrandCtx.Provider>
  );
}
