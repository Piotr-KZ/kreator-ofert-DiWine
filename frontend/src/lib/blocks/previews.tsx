import React, { createContext, useContext } from 'react';

// Brand context for CTA colors in previews
export type BrandCtxType = { cta: string; ctaSecondary: string };
export const BrandCtx = createContext<BrandCtxType>({ cta: '#6366F1', ctaSecondary: '#EC4899' });

// ── Primitive helpers (inline styles kept for dynamic sizing) ──

const Bar = ({ w = '70%', h = 3, c = '#94A3B8', mb = 5, style }: { w?: string | number; h?: number; c?: string; mb?: number; style?: React.CSSProperties }) => (
  <div style={{ width: w, height: h, background: c, borderRadius: h / 2, marginBottom: mb, ...style }} />
);

const BigBar = ({ w = '80%', mb = 6, c = '#334155', style }: { w?: string | number; mb?: number; c?: string; style?: React.CSSProperties }) => (
  <Bar w={w} h={10} c={c} mb={mb} style={style} />
);

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

const CTABtn = ({ w, text = 'CTA', variant = 'primary' }: { w?: string | number; text?: string; variant?: string }) => {
  const b = useContext(BrandCtx);
  const primaryBg = b.ctaSecondary
    ? `linear-gradient(135deg, ${b.cta}, ${b.ctaSecondary})`
    : b.cta;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      background: variant === 'primary' ? primaryBg : 'transparent',
      color: variant === 'primary' ? '#fff' : '#334155',
      border: variant === 'primary' ? 'none' : '1.5px solid #334155',
      borderRadius: 6, padding: '7px 14px', fontSize: 10, fontWeight: 600,
      width: w, justifyContent: 'center',
    }}>{text} <span style={{ fontSize: 11 }}>→</span></span>
  );
};

const ImgFrame = ({ style = {}, ratio = '4/3', dark, icon = 'image', src }: { style?: React.CSSProperties; ratio?: string; dark?: boolean; icon?: string; src?: string }) => (
  <div style={{
    aspectRatio: ratio,
    background: src ? `url(${src}) center/cover no-repeat` : (dark ? 'rgba(255,255,255,.08)' : 'linear-gradient(135deg,#E2E8F0,#F1F5F9)'),
    border: src ? 'none' : `1px solid ${dark ? 'rgba(255,255,255,.15)' : '#E2E8F0'}`,
    borderRadius: 10,
    display: src ? 'block' : 'grid', placeItems: 'center',
    color: dark ? 'rgba(255,255,255,.4)' : '#94A3B8',
    width: '100%',
    ...style,
  }}>
    {!src && icon === 'image' && (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4">
        <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="1.5" fill="currentColor"/><path d="m21 15-5-5L5 21"/>
      </svg>
    )}
    {!src && icon === 'play' && (
      <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
    )}
    {!src && icon === 'user' && (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4">
        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z"/>
      </svg>
    )}
  </div>
);

type IconName = 'check' | 'star' | 'warn' | 'sparkle' | 'arrow' | 'phone';
const iconPaths: Record<IconName, string> = {
  check: 'M20 6L9 17l-5-5',
  star: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z',
  warn: 'M12 9v3m0 3h.01M10.29 3.86l-8.14 14A2 2 0 003.86 21h16.28a2 2 0 001.71-3.14l-8.14-14a2 2 0 00-3.42 0z',
  sparkle: 'M12 3v4M12 17v4M3 12h4M17 12h4',
  arrow: 'M5 12h14M13 5l7 7-7 7',
  phone: 'M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z',
};
const Ico = ({ name, size = 14, c = '#6366F1' }: { name: IconName; size?: number; c?: string }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d={iconPaths[name]} />
  </svg>
);

type TC = { big: string; small: string; chipBg: string; chipFg: string; dark: boolean };
function getTC(bg?: string | null): TC {
  if (!bg || bg === 'null') return { big: '#334155', small: '#94A3B8', chipBg: 'rgba(99,102,241,.1)', chipFg: '#6366F1', dark: false };
  const hex = bg.replace('#', '');
  if (hex.length < 6) return { big: '#334155', small: '#94A3B8', chipBg: 'rgba(99,102,241,.1)', chipFg: '#6366F1', dark: false };
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const dark = (0.299 * r + 0.587 * g + 0.114 * b) < 128;
  return dark
    ? { big: '#fff', small: 'rgba(255,255,255,.55)', chipBg: 'rgba(255,255,255,.12)', chipFg: '#fff', dark: true }
    : { big: '#334155', small: '#94A3B8', chipBg: 'rgba(99,102,241,.1)', chipFg: '#6366F1', dark: false };
}

// ── Block preview components ──

export const PV: Record<string, (bg?: string | null) => React.ReactElement> = {

  NA1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: '16px 22px', height: '100%', display: 'flex', alignItems: 'center', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <div style={{ width: 18, height: 18, borderRadius: 5, background: c.dark ? '#fff' : '#0F172A' }} />
        <BigBar w={50} mb={0} c={c.big} />
      </div>
      <div style={{ flex: 1 }} />
      <Bar w={28} h={4} c={c.small} mb={0} /><Bar w={28} h={4} c={c.small} mb={0} /><Bar w={28} h={4} c={c.small} mb={0} />
      <div style={{ marginLeft: 10 }}><CTABtn text="CTA" /></div>
    </div>
  ); },

  NA2: (bg) => PV.NA1(bg || '#0F172A'),

  NA3: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: '16px 22px', height: '100%', display: 'flex', alignItems: 'center', gap: 20 }}>
      <div style={{ width: 18, height: 18, borderRadius: 5, background: c.dark ? '#fff' : '#0F172A' }} />
      <div style={{ flex: 1 }} />
      <Bar w={36} h={4} c={c.small} mb={0} />
      <div><Bar w={36} h={4} c={c.big} mb={2} /><Bar w={36} h={2} c={c.big} mb={0} /></div>
      <Bar w={36} h={4} c={c.small} mb={0} />
      <div style={{ flex: 1 }} />
      <CTABtn text="Kontakt" />
    </div>
  ); },

  HE1: (bg) => { const c = getTC(bg || '#0F172A'); return (
    <div style={{ padding: 32, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <BigBar w="65%" mb={8} c={c.big} />
      <BigBar w="45%" mb={14} c={c.big} />
      <Bar w="55%" c={c.small} mb={4} /><Bar w="40%" c={c.small} mb={16} />
      <div style={{ display: 'flex', gap: 8, marginBottom: 22 }}>
        <CTABtn text="Umów rozmowę" />
        <CTABtn text="Zobacz ofertę" variant="ghost" />
      </div>
      <div style={{ display: 'flex', gap: 24, paddingTop: 14, borderTop: `1px solid ${c.small}33`, width: '80%', justifyContent: 'space-around' }}>
        {['120+','15 lat','98%','4.9'].map((s, i) => (
          <div key={i} style={{ textAlign: 'center' }}>
            <div style={{ fontFamily: 'Instrument Serif, serif', fontSize: 20, color: c.big, fontWeight: 400 }}>{s}</div>
            <Bar w={32} h={2} c={c.small} mb={0} />
          </div>
        ))}
      </div>
    </div>
  ); },

  HE2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: 24, alignItems: 'center' }}>
      <div>
        <Chip bg={c.chipBg} fg={c.chipFg}>✦ NOWOŚĆ</Chip>
        <BigBar w="95%" mb={6} c={c.big} />
        <BigBar w="70%" mb={14} c={c.big} />
        <Bar w="100%" c={c.small} /><Bar w="90%" c={c.small} /><Bar w="75%" c={c.small} mb={16} />
        <CTABtn text="Umów konsultację" />
      </div>
      <ImgFrame ratio="4/5" dark={c.dark} src="https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=400&q=60" />
    </div>
  ); },

  HE3: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'center' }}>
      <div>
        <BigBar w="90%" mb={6} c={c.big} />
        <BigBar w="65%" mb={14} c={c.big} />
        <Bar w="95%" c={c.small} /><Bar w="80%" c={c.small} mb={14} />
        {[1,2].map(i => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}><Ico name="check" size={13} c={c.chipFg}/><Bar w={110} c={c.small} mb={0}/></div>)}
      </div>
      <div style={{ background: c.dark ? 'rgba(255,255,255,.08)' : '#fff', border: `1px solid ${c.dark ? 'rgba(255,255,255,.15)' : '#E2E8F0'}`, borderRadius: 10, padding: 16 }}>
        <Bar w="35%" h={3} c={c.chipFg} mb={10} />
        {[1,2,3].map(i => <div key={i} style={{ marginBottom: 8 }}><Bar w={40} h={2} c={c.small}/><div style={{ height: 22, background: c.dark ? 'rgba(255,255,255,.08)' : '#F1F5F9', borderRadius: 4, marginTop: 3 }}/></div>)}
        <CTABtn text="Wyślij" />
      </div>
    </div>
  ); },

  HE4: (_bg) => (
    <div style={{ padding: 0, height: '100%', position: 'relative', background: 'linear-gradient(135deg, #1E293B, #0F172A)', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(99,102,241,.12)', display: 'grid', placeItems: 'center' }}>
        <svg width="26" height="26" viewBox="0 0 24 24" fill="rgba(255,255,255,.4)"><path d="M8 5v14l11-7z"/></svg>
      </div>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 28, background: 'rgba(15,23,42,.55)' }}>
        <Chip invert>VIDEO</Chip>
        <BigBar w="70%" mb={6} c="#fff" />
        <BigBar w="50%" mb={14} c="#fff" />
        <Bar w="45%" c="rgba(255,255,255,.5)" mb={16}/>
        <CTABtn text="Zobacz video" />
      </div>
    </div>
  ),

  HE5: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 40, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <BigBar w="55%" mb={6} c={c.big} />
      <BigBar w="35%" mb={14} c={c.big} />
      <Bar w="40%" c={c.small} mb={16}/>
      <CTABtn text="Zacznij" />
    </div>
  ); },

  PB1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 18 }}><BigBar w="40%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {[1,2,3,4].map(i => <div key={i} style={{ padding: 12, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 8, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}` }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}><Ico name="warn" size={14} c="#F59E0B"/><Bar w={60} h={4} c={c.big} mb={0}/></div>
          <Bar w="95%" c={c.small}/><Bar w="70%" c={c.small} mb={0}/>
        </div>)}
      </div>
    </div>
  ); },

  PB2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 14 }}>
      {[85, 78, 70].map((w, i) => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ fontFamily: 'Instrument Serif, serif', fontSize: 28, color: c.chipFg, fontStyle: 'italic', lineHeight: 1 }}>"</div>
        <div style={{ flex: 1 }}><Bar w={`${w}%`} h={4} c={c.big}/><Bar w={`${w-20}%`} h={4} c={c.big} mb={0}/></div>
      </div>)}
    </div>
  ); },

  PB3: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center', marginBottom: 20 }}><BigBar w="35%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, textAlign: 'center' }}>
        {['67%','3x','45min'].map((s, i) => <div key={i}>
          <div style={{ fontFamily: 'Instrument Serif, serif', fontSize: 36, color: '#EF4444', fontWeight: 400, lineHeight: 1 }}>{s}</div>
          <Bar w="80%" c={c.small} style={{ margin: '8px auto 2px' }}/><Bar w="60%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
        </div>)}
      </div>
    </div>
  ); },

  RO1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 18 }}><BigBar w="35%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {[1,2,3].map(i => <div key={i} style={{ padding: 16, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 10, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}`, textAlign: 'center' }}>
          <div style={{ width: 34, height: 34, borderRadius: 8, background: 'linear-gradient(135deg,#6366F1,#EC4899)', margin: '0 auto 8px', display: 'grid', placeItems: 'center' }}><Ico name="star" c="#fff" size={16}/></div>
          <Bar w="70%" h={4} c={c.big} style={{ margin: '0 auto 6px' }}/><Bar w="90%" c={c.small} style={{ margin: '0 auto' }}/><Bar w="70%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
        </div>)}
      </div>
    </div>
  ); },

  RO2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'center' }}>
      <div>
        <BigBar w="80%" mb={14} c={c.big}/>
        {[1,2,3,4].map(i => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}><Ico name="check" c={c.chipFg}/><Bar w={130} c={c.small} mb={0}/></div>)}
        <div style={{ marginTop: 14 }}><CTABtn text="Dowiedz się więcej" /></div>
      </div>
      <ImgFrame dark={c.dark} src="https://images.unsplash.com/photo-1453614512568-c4024d13c247?w=400&q=60"/>
    </div>
  ); },

  KR1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {[1,2,3,4,5,6].map(i => <div key={i}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}><Ico name="star" c={c.chipFg} size={12}/><Bar w={50} h={3} c={c.big} mb={0}/></div>
          <Bar w="90%" c={c.small}/><Bar w="70%" c={c.small} mb={0}/>
        </div>)}
      </div>
    </div>
  ); },

  KR2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, alignItems: 'center', textAlign: 'center' }}>
      {['120+','15','98%','3x'].map((s, i) => <div key={i}>
        <div style={{ fontFamily: 'Instrument Serif, serif', fontSize: 44, color: c.big, fontWeight: 400, lineHeight: 1 }}>{s}</div>
        <Bar w="70%" c={c.small} style={{ margin: '10px auto 3px' }}/><Bar w="50%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
      </div>)}
    </div>
  ); },

  CF1: (bg) => PV.RO1(bg),

  CF2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, alignContent: 'center' }}>
      {[1,2,3,4,5,6,7,8].map(i => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 18, height: 18, borderRadius: '50%', background: 'rgba(16,185,129,.15)', display: 'grid', placeItems: 'center' }}><Ico name="check" size={11} c="#10B981"/></div>
        <Bar w={120} c={c.big} mb={0}/>
      </div>)}
    </div>
  ); },

  OB1: (bg) => PV.FA1(bg),

  FI1: (bg) => PV.HE2(bg),

  FI2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1.1fr', gap: 24, alignItems: 'center' }}>
      <ImgFrame ratio="4/5" dark={c.dark} src="https://images.unsplash.com/photo-1559925393-8be0ec4767c8?w=400&q=60"/>
      <div>
        <Chip bg={c.chipBg} fg={c.chipFg}>O NAS</Chip>
        <BigBar w="90%" mb={10} c={c.big}/>
        <Bar w="100%" c={c.small}/><Bar w="95%" c={c.small}/><Bar w="85%" c={c.small}/><Bar w="70%" c={c.small} mb={14}/>
        <CTABtn text="Poznaj nas" />
      </div>
    </div>
  ); },

  FI3: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 30, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <BigBar w="40%" mb={12} c={c.big}/>
      <Bar w="70%" c={c.small}/><Bar w="65%" c={c.small}/><Bar w="55%" c={c.small} mb={18}/>
      <div style={{ fontFamily: 'Instrument Serif, serif', fontSize: 22, color: c.chipFg, fontStyle: 'italic', marginBottom: 6 }}>"</div>
      <Bar w="60%" c={c.big}/><Bar w="50%" c={c.big} mb={10}/>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 24, height: 24, borderRadius: '50%', background: 'linear-gradient(135deg,#EC4899,#F59E0B)' }}/>
        <Bar w={90} c={c.small} mb={0}/>
      </div>
    </div>
  ); },

  FI4: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      {['2010','2015','2020','2024'].map((y, i) => <div key={i} style={{ display: 'flex', gap: 14, marginBottom: 10, alignItems: 'flex-start' }}>
        <div style={{ fontFamily: 'Instrument Serif, serif', fontSize: 16, color: c.chipFg, minWidth: 40, fontStyle: 'italic' }}>{y}</div>
        <div style={{ width: 10, height: 10, borderRadius: '50%', background: c.chipFg, marginTop: 4, flexShrink: 0 }}/>
        <div style={{ flex: 1 }}><Bar w={70} h={4} c={c.big}/><Bar w="90%" c={c.small} mb={0}/></div>
      </div>)}
    </div>
  ); },

  OF1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {[1,2,3].map(i => <div key={i} style={{ padding: 14, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 10, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}` }}>
          <Ico name="star" c={c.chipFg} size={16}/>
          <Bar w="75%" h={4} c={c.big} style={{ marginTop: 8 }}/><Bar w="95%" c={c.small}/><Bar w="80%" c={c.small} mb={8}/>
          <div style={{ fontFamily: 'Instrument Serif, serif', fontSize: 18, color: c.big }}>od 2000 zł</div>
          <div style={{ marginTop: 8 }}><CTABtn text="Więcej" /></div>
        </div>)}
      </div>
    </div>
  ); },

  OF2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 26, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      {[1,2,3,4].map(i => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0', borderBottom: i<4 ? `1px solid ${c.small}22` : 'none' }}>
        <div style={{ width: 26, height: 26, borderRadius: 7, background: c.chipBg, display: 'grid', placeItems: 'center' }}><Ico name="star" c={c.chipFg} size={13}/></div>
        <Bar w={80} h={4} c={c.big} mb={0}/>
        <span style={{ color: c.small, fontSize: 10 }}>—</span>
        <Bar w={140} c={c.small} mb={0}/>
      </div>)}
    </div>
  ); },

  PR1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 16 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {[1,2,3,4].map((n, i) => (
          <React.Fragment key={i}>
            <div style={{ flex: 1, textAlign: 'center' }}>
              <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg,#6366F1,#EC4899)', color: '#fff', display: 'grid', placeItems: 'center', margin: '0 auto 8px', fontFamily: 'Instrument Serif, serif', fontSize: 16 }}>{n}</div>
              <Bar w="80%" h={4} c={c.big} style={{ margin: '0 auto 4px' }}/><Bar w="60%" c={c.small} mb={0} style={{ margin: '0 auto' }}/>
            </div>
            {i < 3 && <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={c.small} strokeWidth="2"><path d="M5 12h14M13 5l7 7-7 7"/></svg>}
          </React.Fragment>
        ))}
      </div>
    </div>
  ); },

  PR2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 26, height: '100%' }}>
      {[1,2,3,4].map((n, i) => <div key={i} style={{ display: 'flex', gap: 14, paddingBottom: 12, position: 'relative' }}>
        <div style={{ position: 'relative' }}>
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg,#6366F1,#EC4899)', color: '#fff', display: 'grid', placeItems: 'center', fontFamily: 'Instrument Serif, serif', fontSize: 14 }}>{n}</div>
          {i < 3 && <div style={{ position: 'absolute', left: 13, top: 28, width: 2, height: 32, background: `${c.small}44` }}/>}
        </div>
        <div style={{ flex: 1 }}><Bar w={120} h={4} c={c.big}/><Bar w="90%" c={c.small} mb={0}/></div>
      </div>)}
    </div>
  ); },

  OP1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="35%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {[1,2,3].map(i => <div key={i} style={{ padding: 14, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 10, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}` }}>
          <div style={{ display: 'flex', gap: 2, marginBottom: 8 }}>{[1,2,3,4,5].map(s => <Ico key={s} name="star" c="#F59E0B" size={10}/>)}</div>
          <Bar w="100%" c={c.big}/><Bar w="95%" c={c.big}/><Bar w="80%" c={c.big} mb={10}/>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 22, height: 22, borderRadius: '50%', background: ['linear-gradient(135deg,#EC4899,#F59E0B)','linear-gradient(135deg,#6366F1,#06B6D4)','linear-gradient(135deg,#10B981,#14B8A6)'][i-1] }}/>
            <div><Bar w={50} h={3} c={c.big}/><Bar w={60} h={2} c={c.small} mb={0}/></div>
          </div>
        </div>)}
      </div>
    </div>
  ); },

  OP2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 30, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <div style={{ display: 'flex', gap: 3, marginBottom: 14 }}>{[1,2,3,4,5].map(s => <Ico key={s} name="star" c="#F59E0B" size={14}/>)}</div>
      <Bar w="75%" c={c.big}/><Bar w="85%" c={c.big}/><Bar w="65%" c={c.big} mb={20}/>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg,#EC4899,#F59E0B)' }}/>
        <div style={{ textAlign: 'left' }}><Bar w={80} h={4} c={c.big}/><Bar w={60} h={2} c={c.small} mb={0}/></div>
      </div>
    </div>
  ); },

  ZE1: (bg) => { const c = getTC(bg); return (
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

  ZE2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, alignContent: 'center' }}>
      {[1,2].map(i => <div key={i} style={{ display: 'flex', gap: 10 }}>
        <ImgFrame ratio="3/4" dark={c.dark} icon="user" style={{ width: 60 }}/>
        <div style={{ flex: 1 }}><Bar w={90} h={4} c={c.big}/><Bar w={60} h={2} c={c.chipFg} mb={6}/><Bar w="95%" c={c.small}/><Bar w="80%" c={c.small} mb={0}/></div>
      </div>)}
    </div>
  ); },

  CE1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="25%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {['Basic','Premium','Ent'].map((p, i) => <div key={i} style={{ padding: 14, background: i===1 ? 'linear-gradient(135deg,#6366F1,#EC4899)' : (c.dark ? 'rgba(255,255,255,.06)' : '#fff'), color: i===1 ? '#fff' : c.big, borderRadius: 10, border: `1px solid ${i===1 ? 'transparent' : (c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0')}`, textAlign: 'center', position: 'relative' }}>
          {i===1 && <div style={{ position: 'absolute', top: -8, left: '50%', transform: 'translateX(-50%)', background: '#F59E0B', color: '#fff', fontSize: 8, fontWeight: 700, padding: '2px 7px', borderRadius: 6 }}>TOP</div>}
          <div style={{ fontSize: 10, fontWeight: 600, opacity: .7 }}>{p.toUpperCase()}</div>
          <div style={{ fontFamily: 'Instrument Serif, serif', fontSize: 24, marginTop: 4 }}>{['99','199','499'][i]} zł</div>
          {[1,2,3].map(j => <div key={j} style={{ fontSize: 9, display: 'flex', alignItems: 'center', gap: 4, marginBottom: 3 }}><Ico name="check" size={10} c={i===1 ? '#fff' : c.chipFg}/>Cecha {j}</div>)}
          <div style={{ marginTop: 8 }}><CTABtn text="Wybierz" /></div>
        </div>)}
      </div>
    </div>
  ); },

  CT1: (bg) => { const c = getTC(bg || '#0F172A'); return (
    <div style={{ padding: 32, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <BigBar w="55%" mb={8} c={c.big}/>
      <Bar w="40%" c={c.small} mb={16}/>
      <CTABtn text="Umów konsultację" />
    </div>
  ); },

  CT2: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 28, height: '100%', display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 24, alignItems: 'center' }}>
      <div>
        <BigBar w="85%" mb={6} c={c.big}/>
        <Bar w="70%" c={c.small} mb={14}/>
        <CTABtn text="Umów rozmowę" />
      </div>
      <ImgFrame ratio="4/3" dark={c.dark} src="https://images.unsplash.com/photo-1511920170033-f8396924c348?w=400&q=60"/>
    </div>
  ); },

  CT3: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: '16px 24px', height: '100%', display: 'flex', alignItems: 'center', gap: 14 }}>
      <Bar w={180} h={5} c={c.big} mb={0}/>
      <div style={{ flex: 1 }}/>
      <CTABtn text="Kontakt" />
    </div>
  ); },

  KO1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%', display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 20 }}>
      <div style={{ padding: 14, background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 10, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}` }}>
        <Bar w={80} h={4} c={c.big} mb={10}/>
        {['Imię','Email','Temat'].map((_l, i) => <div key={i} style={{ marginBottom: 7 }}><Bar w={40} h={2} c={c.small}/><div style={{ height: 20, background: c.dark ? 'rgba(255,255,255,.08)' : '#F1F5F9', borderRadius: 4, marginTop: 3 }}/></div>)}
        <div style={{ height: 40, background: c.dark ? 'rgba(255,255,255,.08)' : '#F1F5F9', borderRadius: 4, margin: '3px 0 8px' }}/>
        <CTABtn text="Wyślij" />
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, justifyContent: 'center' }}>
        {[{i:'phone' as IconName, t:'+48 123 456'}, {i:'star' as IconName, t:'kontakt@firma.pl'}, {i:'star' as IconName, t:'Warszawa'}].map((r, i) => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 26, height: 26, borderRadius: 7, background: c.chipBg, display: 'grid', placeItems: 'center' }}><Ico name={r.i} c={c.chipFg} size={13}/></div>
          <Bar w={110} c={c.big} mb={0}/>
        </div>)}
      </div>
    </div>
  ); },

  FA1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 24, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="35%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      {[{open:true},{open:false},{open:false},{open:false}].map((q, i) => <div key={i} style={{ padding: '10px 12px', background: c.dark ? 'rgba(255,255,255,.06)' : '#fff', borderRadius: 8, border: `1px solid ${c.dark ? 'rgba(255,255,255,.1)' : '#E2E8F0'}`, marginBottom: 6 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Bar w={180} h={4} c={c.big} mb={0}/>
          <div style={{ flex: 1 }}/><span style={{ color: c.small, fontSize: 12 }}>{q.open ? '▼' : '▸'}</span>
        </div>
        {q.open && <div style={{ marginTop: 7 }}><Bar w="95%" c={c.small}/><Bar w="80%" c={c.small} mb={0}/></div>}
      </div>)}
    </div>
  ); },

  RE1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><BigBar w="30%" mb={0} c={c.big} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {['https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=300&q=60','https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300&q=60','https://images.unsplash.com/photo-1442975631115-c4f7b05b8a2c?w=300&q=60'].map((u, i) => <div key={i}>
          <ImgFrame ratio="4/3" dark={c.dark} src={u} style={{ marginBottom: 8 }}/>
          <Bar w="70%" h={4} c={c.big}/><Bar w="50%" c={c.small} mb={0}/>
        </div>)}
      </div>
    </div>
  ); },

  LO1: (bg) => { const c = getTC(bg); return (
    <div style={{ padding: 26, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center', marginBottom: 14 }}><Bar w="25%" h={4} c={c.small} mb={0} style={{ margin: '0 auto' }}/></div>
      <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', gap: 16, opacity: .65 }}>
        {[1,2,3,4,5].map(i => <div key={i} style={{ width: 60, height: 24, borderRadius: 4, background: `linear-gradient(135deg,${c.small}66,${c.small}33)`, display: 'grid', placeItems: 'center', fontSize: 9, color: c.big, fontWeight: 600 }}>LOGO {i}</div>)}
      </div>
    </div>
  ); },

  ST1: (bg) => PV.KR2(bg),

  FO1: (bg) => { const c = getTC(bg || '#0F172A'); return (
    <div style={{ padding: 22, height: '100%' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr 1fr 1fr', gap: 16, marginBottom: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <div style={{ width: 18, height: 18, borderRadius: 4, background: c.big }}/><Bar w={60} h={4} c={c.big} mb={0}/>
          </div>
          <Bar w="90%" c={c.small}/><Bar w="70%" c={c.small} mb={10}/>
          <div style={{ display: 'flex', gap: 6 }}>{[1,2,3,4].map(s => <div key={s} style={{ width: 20, height: 20, borderRadius: '50%', background: `${c.big}22` }}/>)}</div>
        </div>
        {['Usługi','O nas','Kontakt'].map((_h, i) => <div key={i}>
          <Bar w={50} h={4} c={c.big}/>
          {[1,2,3,4].map(l => <Bar key={l} w={70} c={c.small}/>)}
        </div>)}
      </div>
      <div style={{ paddingTop: 10, borderTop: `1px solid ${c.small}33`, display: 'flex' }}>
        <Bar w={160} c={c.small} mb={0}/><div style={{ flex: 1 }}/><Bar w={80} c={c.small} mb={0}/>
      </div>
    </div>
  ); },
};

// ── BlockPreview wrapper ──

export function BlockPreview({ code, bg, brand }: {
  code: string;
  bg?: string | null;
  brand?: BrandCtxType;
}) {
  const fn = PV[code] ?? (() => (
    <div style={{ padding: 20, textAlign: 'center', color: '#94A3B8', fontSize: 12 }}>
      Podgląd {code}
    </div>
  ));
  const b = brand ?? { cta: '#6366F1', ctaSecondary: '#EC4899' };
  return (
    <BrandCtx.Provider value={b}>
      <div
        style={{
          background: bg ?? undefined,
          width: '100%',
          height: '100%',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        {fn(bg ?? undefined)}
      </div>
    </BrandCtx.Provider>
  );
}
