// Treści dla kawiarni "Miętowa" — z briefu
// Każda sekcja ma swój content object z edytowalnymi polami

const BRIEF = {
  brand: 'Miętowa',
  tagline: 'Kawiarnia z własną paloarnią',
  city: 'Wrocław, ul. Ruska 12',
  tone: 'ciepły, rzemieślniczy, autentyczny',
};

const FONT_OPTIONS = [
  { id: 'Inter', name: 'Inter', cat: 'Sans', sample: 'Aa' },
  { id: 'Manrope', name: 'Manrope', cat: 'Sans', sample: 'Aa' },
  { id: 'Plus Jakarta Sans', name: 'Plus Jakarta', cat: 'Sans', sample: 'Aa' },
  { id: 'Space Grotesk', name: 'Space Grotesk', cat: 'Sans', sample: 'Aa' },
  { id: 'Fraunces', name: 'Fraunces', cat: 'Serif', sample: 'Aa' },
  { id: 'Playfair Display', name: 'Playfair', cat: 'Serif', sample: 'Aa' },
  { id: 'DM Serif Display', name: 'DM Serif', cat: 'Serif', sample: 'Aa' },
  { id: 'Cormorant', name: 'Cormorant', cat: 'Serif', sample: 'Aa' },
  { id: 'JetBrains Mono', name: 'JetBrains Mono', cat: 'Mono', sample: 'Aa' },
  { id: 'Instrument Serif', name: 'Instrument', cat: 'Serif', sample: 'Aa' },
];

// Density scale: 1 = kompakt, 3 = komfort, 5 = luźny
const DENSITY_SCALE = {
  1: { bodySize: 14, scale: 1.2, spacing: 0.85, lineHeight: 1.4 },
  2: { bodySize: 15, scale: 1.25, spacing: 0.95, lineHeight: 1.5 },
  3: { bodySize: 16, scale: 1.33, spacing: 1.0, lineHeight: 1.6 },
  4: { bodySize: 18, scale: 1.414, spacing: 1.15, lineHeight: 1.7 },
  5: { bodySize: 20, scale: 1.5, spacing: 1.3, lineHeight: 1.8 },
};

// Starting content — sekcje z prawdziwymi tekstami dla kawiarni Miętowa
const INITIAL_CONTENT = [
  {
    id: 's1', code: 'NA1', label: 'Nawigacja',
    bg: '#FFFFFF', // navigation zawsze białe
    fields: {
      logo: 'Miętowa',
      links: ['Menu', 'O nas', 'Wydarzenia', 'Kontakt'],
      cta: 'Rezerwuj stolik',
    },
  },
  {
    id: 's2', code: 'HE2', label: 'Hero',
    bg: '#FEF3C7',
    fields: {
      eyebrow: 'Kawa palona w sercu Wrocławia',
      heading: 'Miętowa. Twoja codzienna przystań.',
      body: 'Palimy kawę świeżo w naszej mikropalarni przy ul. Ruskiej. Serwujemy ją z ciastami, książkami i prawdziwymi rozmowami — codziennie od 8:00.',
      cta: 'Sprawdź menu',
      cta2: 'Znajdź nas na mapie',
    },
  },
  {
    id: 's3', code: 'LO1', label: 'Zaufali nam',
    bg: null,
    fields: {
      title: 'Piszą o nas',
      logos: ['Gazeta Wyborcza', 'Kukbuk', 'Coffee Lovers PL', 'Wroclove', 'Slow Food'],
    },
  },
  {
    id: 's4', code: 'PB1', label: 'Problem',
    bg: '#FEF7ED',
    fields: {
      eyebrow: 'Po co kolejna kawiarnia?',
      heading: 'Bo szybka kawa z sieciówki to nie to samo.',
      body: 'Każdego ranka mijasz dziesięć miejsc, gdzie kawa jest… po prostu kawą. Tymczasem dobra filiżanka to pretekst do zatrzymania się, rozmowy i doceniania chwili.',
    },
  },
  {
    id: 's5', code: 'RO1', label: 'Rozwiązanie',
    bg: null,
    fields: {
      eyebrow: 'Co robimy inaczej',
      heading: 'Palimy, parzymy, dzielimy się.',
      features: [
        { title: 'Własna palarnia', body: 'Surowe ziarna z małych farm w Etiopii, Kolumbii i Gwatemali. Palimy co dwa tygodnie, sprzedajemy tylko świeże.' },
        { title: 'Ręczna parzenie', body: 'Chemex, V60, aeropress — każda metoda dobrana do profilu ziarna. Baristki znają swoje rzemiosło.' },
        { title: 'Lokalne ciasta', body: 'Codziennie nowe wypieki od pań z piekarni Szelągowska. Marchewkowe, makowiec, sernik krakowski.' },
      ],
    },
  },
  {
    id: 's6', code: 'KR1', label: 'Dlaczego my',
    bg: '#EEF2FF',
    fields: {
      eyebrow: 'Nasze zasady',
      heading: 'Nie śpieszymy się. I tego uczymy.',
      body: 'Kawa to rytuał. Stół, przy którym siedzisz, książka, którą pożyczasz z półki, pies, którego głaszczesz — tu wszystko ma czas.',
      points: [
        'Kawa z plantacji pod kontrolą fair-trade',
        'Zero plastiku — kubki kompostowalne lub własny termos -2 zł',
        'Pies mile widziany, dostaje miskę wody i gratis uszko',
        'Wi-Fi, książki, ciche godziny 8–11 dla pracujących',
      ],
    },
  },
  {
    id: 's7', code: 'OF1', label: 'Oferta',
    bg: null,
    fields: {
      eyebrow: 'Nasze menu',
      heading: 'Proste, dobre, bez ściemy.',
      tiers: [
        { name: 'Kawa', price: 'od 9 zł', desc: 'Espresso, cappuccino, flat white, filtr', items: ['Espresso', 'Cappuccino', 'Flat white', 'Chemex/V60', 'Mrożona'] },
        { name: 'Śniadania', price: 'od 18 zł', desc: 'Do 13:00, codziennie', items: ['Jajecznica z feta', 'Owsianka z orzechami', 'Kanapka z serem kozim', 'Naleśniki z twarogiem'] },
        { name: 'Ciasta', price: 'od 12 zł', desc: 'Codzienne wypieki', items: ['Sernik krakowski', 'Makowiec', 'Marchewkowe', 'Brownie wegańskie', 'Szarlotka'] },
      ],
    },
  },
  {
    id: 's8', code: 'OP1', label: 'Opinie',
    bg: '#FEF3C7',
    fields: {
      eyebrow: 'Co mówią goście',
      heading: 'Nasze najlepsze recenzje.',
      testimonials: [
        { quote: 'Najlepszy flat white jaki piłam we Wrocławiu. A cisza rano — bezcenna.', author: 'Kasia W.', role: 'Dziennikarka' },
        { quote: 'Zabrałem tu rodziców z Warszawy. Mama zamówiła makowiec trzy razy.', author: 'Marcin K.', role: 'Klient od 2022' },
        { quote: 'Właściciele wiedzą jak mi na imię, jak mój pies ma na imię i jaka kawa mi smakuje. Tego nie ma nigdzie indziej.', author: 'Ania P.', role: 'Stała bywalczyni' },
      ],
    },
  },
  {
    id: 's9', code: 'CT1', label: 'CTA',
    bg: '#0F172A',
    fields: {
      eyebrow: 'Zapraszamy',
      heading: 'Wpadnij dziś na filiżankę.',
      body: 'Codziennie 8:00–19:00. Rezerwacja nie jest potrzebna, ale miło wiedzieć, że będziesz.',
      cta: 'Zarezerwuj stolik',
      cta2: 'Zadzwoń: 71 123 45 67',
    },
  },
  {
    id: 's10', code: 'FO1', label: 'Stopka',
    bg: '#0F172A',
    fields: {
      logo: 'Miętowa',
      desc: 'Kawiarnia z własną palarnią. Wrocław, Ruska 12. Codziennie 8:00–19:00.',
      cols: [
        { title: 'Menu', links: ['Kawa', 'Śniadania', 'Ciasta', 'Lunch'] },
        { title: 'O nas', links: ['Historia', 'Palarnia', 'Zespół', 'Kariera'] },
        { title: 'Kontakt', links: ['Ruska 12, Wrocław', '71 123 45 67', 'hej@mietowa.pl', 'Mapa'] },
      ],
      copyright: '© 2024 Miętowa. Palimy kawę i spędzamy czas. Zrobione z miłości.',
    },
  },
];

export { BRIEF };
export { FONT_OPTIONS };
export { DENSITY_SCALE };
export { INITIAL_CONTENT };
