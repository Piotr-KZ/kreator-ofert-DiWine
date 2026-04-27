// Definicje wszystkich klocków z katalogu (40 klocków, 17 kategorii)

export interface Category {
  name: string;
  color: string;
  icon: string;
}

export interface Block {
  code: string;
  cat: string;
  name: string;
  desc: string;
  size: 'S' | 'M' | 'L';
}

export interface BrandPaletteColor {
  name: string;
  value: string;
  textOn: string;
}

export interface Section {
  id: string;
  code: string;
  label: string;
  bg: string | null;
  cta: string | null;
}

export interface Brand {
  bg: string;
  bg2: string;
  bgGradient: boolean;
  cta: string;
  cta2: string;
  ctaGradient: boolean;
}

export const CATEGORIES: Record<string, Category> = {
  NA: { name: 'Nawigacja', color: '#8B5CF6', icon: 'M4 6h16M4 12h16M4 18h16' },
  HE: { name: 'Hero', color: '#EC4899', icon: 'M12 2l4 6h-3v6h-2v-6H8l4-6z' },
  PB: { name: 'Problem', color: '#F59E0B', icon: 'M12 9v3m0 3h.01M10.29 3.86l-8.14 14A2 2 0 003.86 21h16.28a2 2 0 001.71-3.14l-8.14-14a2 2 0 00-3.42 0z' },
  RO: { name: 'Rozwiązanie', color: '#10B981', icon: 'M9 12l2 2 4-4' },
  KR: { name: 'Korzyści', color: '#06B6D4', icon: 'M5 3l14 9-14 9V3z' },
  CF: { name: 'Cechy', color: '#0EA5E9', icon: 'M12 2l2.09 6.26L20 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l5.91-1.01L12 2z' },
  OB: { name: 'Obiekcje', color: '#F97316', icon: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z' },
  FI: { name: 'O firmie', color: '#6366F1', icon: 'M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75' },
  OF: { name: 'Oferta', color: '#EAB308', icon: 'M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z' },
  PR: { name: 'Proces', color: '#14B8A6', icon: 'M3 12h3l3-9 6 18 3-9h3' },
  OP: { name: 'Opinie', color: '#EC4899', icon: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z' },
  ZE: { name: 'Zespół', color: '#8B5CF6', icon: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8z' },
  CE: { name: 'Cennik', color: '#10B981', icon: 'M12 2v20M17 5H9.5a3.5 3.5 0 100 7h5a3.5 3.5 0 110 7H6' },
  CT: { name: 'CTA', color: '#EF4444', icon: 'M13 2L3 14h9l-1 8 10-12h-9l1-8z' },
  KO: { name: 'Kontakt', color: '#0EA5E9', icon: 'M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z' },
  FA: { name: 'FAQ', color: '#A855F7', icon: 'M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3M12 17h.01' },
  RE: { name: 'Realizacje', color: '#F97316', icon: 'M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3' },
  LO: { name: 'Loga', color: '#64748B', icon: 'M3 3h18v18H3z' },
  ST: { name: 'Statystyki', color: '#14B8A6', icon: 'M18 20V10M12 20V4M6 20v-6' },
  FO: { name: 'Stopka', color: '#475569', icon: 'M3 21h18M6 18V10M10 18V6M14 18v-8M18 18v-4' },
};

// Biblioteka klocków z katalogu
export const BLOCK_LIBRARY: Block[] = [
  { code: 'NA1', cat: 'NA', name: 'Nawigacja jasna', desc: 'Jasne tło, logo lewo, menu prawo, CTA', size: 'S' },
  { code: 'NA2', cat: 'NA', name: 'Nawigacja ciemna', desc: 'Ciemne tło, białe teksty', size: 'S' },
  { code: 'NA3', cat: 'NA', name: 'Nawigacja z podkreśleniem', desc: 'Menu wycentrowane, aktywne podkreślone', size: 'S' },

  { code: 'HE1', cat: 'HE', name: 'Hero centered + statystyki', desc: 'Ciemne tło, nagłówek, pod spodem 3-4 stat', size: 'L' },
  { code: 'HE2', cat: 'HE', name: 'Hero split — tekst + zdjęcie', desc: 'Podział 50/50, tekst L, zdjęcie R', size: 'L' },
  { code: 'HE3', cat: 'HE', name: 'Hero split — tekst + formularz', desc: 'Split z formularzem kontaktowym', size: 'L' },
  { code: 'HE4', cat: 'HE', name: 'Hero video background', desc: 'Video w tle, overlay, centered text', size: 'L' },
  { code: 'HE5', cat: 'HE', name: 'Hero minimal centered', desc: 'Minimalistyczny, dużo przestrzeni', size: 'M' },

  { code: 'PB1', cat: 'PB', name: 'Problem — lista z opisem', desc: '3-4 karty problemów z ikonami', size: 'M' },
  { code: 'PB2', cat: 'PB', name: 'Problem — pytania retoryczne', desc: 'Seria pytań rezonujących z bolączkami', size: 'M' },
  { code: 'PB3', cat: 'PB', name: 'Problem — statystyki', desc: 'Problemy poparte liczbami', size: 'M' },

  { code: 'RO1', cat: 'RO', name: 'Rozwiązanie — 3 karty', desc: '3 karty z ikonami', size: 'M' },
  { code: 'RO2', cat: 'RO', name: 'Rozwiązanie — split z obrazem', desc: 'Lista cech + zdjęcie', size: 'M' },

  { code: 'KR1', cat: 'KR', name: 'Korzyści — grid 2x3', desc: '6 korzyści z ikonami', size: 'M' },
  { code: 'KR2', cat: 'KR', name: 'Korzyści — duże liczby', desc: '4 liczby z opisami', size: 'M' },

  { code: 'CF1', cat: 'CF', name: 'Cechy — karty 3 kolumny', desc: '3 karty z ikonami', size: 'M' },
  { code: 'CF2', cat: 'CF', name: 'Cechy — checklist 2 kolumny', desc: 'Prosta lista z checkami', size: 'M' },

  { code: 'OB1', cat: 'OB', name: 'Obiekcje — FAQ style', desc: 'Rozwijane pytania', size: 'M' },

  { code: 'FI1', cat: 'FI', name: 'O firmie — tekst + zdjęcie', desc: 'Opis L, zdjęcie R', size: 'M' },
  { code: 'FI2', cat: 'FI', name: 'O firmie — zdjęcie + tekst', desc: 'Odwrócony FI1', size: 'M' },
  { code: 'FI3', cat: 'FI', name: 'O firmie — centered + cytat', desc: 'Osobisty, cytat założyciela', size: 'M' },
  { code: 'FI4', cat: 'FI', name: 'O firmie — timeline historia', desc: 'Oś czasu firmy', size: 'L' },

  { code: 'OF1', cat: 'OF', name: 'Oferta — karty usług', desc: '3 karty z cennikiem', size: 'M' },
  { code: 'OF2', cat: 'OF', name: 'Oferta — lista z ikonami', desc: 'Kompaktowa lista', size: 'M' },

  { code: 'PR1', cat: 'PR', name: 'Proces — kroki poziomo', desc: '4 ponumerowane kroki', size: 'M' },
  { code: 'PR2', cat: 'PR', name: 'Proces — timeline pionowo', desc: 'Pionowy timeline', size: 'M' },

  { code: 'OP1', cat: 'OP', name: 'Opinie — 3 karty', desc: 'Z avatarami i gwiazdkami', size: 'M' },
  { code: 'OP2', cat: 'OP', name: 'Opinie — duży cytat', desc: 'Jedna dominująca opinia', size: 'M' },

  { code: 'ZE1', cat: 'ZE', name: 'Zespół — grid 4 osoby', desc: 'Avatary + role', size: 'M' },
  { code: 'ZE2', cat: 'ZE', name: 'Zespół — lista z bio', desc: 'Foto + biografia', size: 'L' },

  { code: 'CE1', cat: 'CE', name: 'Cennik — 3 pakiety', desc: 'Środkowy wyróżniony', size: 'L' },

  { code: 'CT1', cat: 'CT', name: 'CTA — ciemne tło', desc: 'Pełna szerokość, bold', size: 'M' },
  { code: 'CT2', cat: 'CT', name: 'CTA — kolor + grafika', desc: 'Split z grafiką', size: 'M' },
  { code: 'CT3', cat: 'CT', name: 'CTA — minimalistyczny', desc: 'Jedna linia', size: 'S' },

  { code: 'KO1', cat: 'KO', name: 'Kontakt — formularz + dane', desc: 'Split: formularz L, dane R', size: 'L' },

  { code: 'FA1', cat: 'FA', name: 'FAQ — accordion', desc: 'Rozwijane pytania', size: 'M' },

  { code: 'RE1', cat: 'RE', name: 'Realizacje — grid kart', desc: 'Zdjęcia projektów', size: 'L' },

  { code: 'LO1', cat: 'LO', name: 'Loga klientów — rząd', desc: 'Loga w jednym rzędzie', size: 'S' },

  { code: 'ST1', cat: 'ST', name: 'Statystyki — 4 liczby', desc: 'Duże liczby z opisami', size: 'S' },

  { code: 'FO1', cat: 'FO', name: 'Stopka — 4 kolumny', desc: 'Logo + linki + copyright', size: 'M' },
];

// Gotowa paleta kolorów brandu — 6 kolorów + custom
export const BRAND_PALETTE: BrandPaletteColor[] = [
  { name: 'Biały', value: '#FFFFFF', textOn: '#0F172A' },
  { name: 'Kremowy', value: '#FEF7ED', textOn: '#78350F' },
  { name: 'Piaskowy', value: '#FEF3C7', textOn: '#78350F' },
  { name: 'Niebieski', value: '#EEF2FF', textOn: '#3730A3' },
  { name: 'Brand', value: '#6366F1', textOn: '#FFFFFF' },
  { name: 'Ciemny', value: '#0F172A', textOn: '#FFFFFF' },
];

// Przykładowa struktura strony (domyślna dla demo)
// cta = null → użyj globalnego koloru CTA; string → override dla tej sekcji
// bg = null → użyj globalnego tła brandu; string → override dla tej sekcji
export const INITIAL_STRUCTURE: Section[] = [
  { id: 's1', code: 'NA1', label: 'Nawigacja główna', bg: null, cta: null },
  { id: 's2', code: 'HE2', label: 'Hero główny', bg: '#FEF3C7', cta: null },
  { id: 's3', code: 'LO1', label: 'Zaufali nam', bg: null, cta: null },
  { id: 's4', code: 'PB1', label: 'Problem klienta', bg: '#FEF7ED', cta: null },
  { id: 's5', code: 'RO1', label: 'Nasze rozwiązanie', bg: null, cta: null },
  { id: 's6', code: 'KR1', label: 'Dlaczego my', bg: '#EEF2FF', cta: null },
  { id: 's7', code: 'OF1', label: 'Oferta usług', bg: null, cta: null },
  { id: 's8', code: 'OP1', label: 'Opinie klientów', bg: '#FEF3C7', cta: null },
  { id: 's9', code: 'CT1', label: 'Wezwanie do działania', bg: '#0F172A', cta: null },
  { id: 's10', code: 'FO1', label: 'Stopka', bg: '#0F172A', cta: null },
];

// Kolory brandu — ustawione globalnie dla całej strony
export const INITIAL_BRAND: Brand = {
  bg: '#FFFFFF',
  bg2: '#F1F5F9',
  bgGradient: false,
  cta: '#6366F1',
  cta2: '#EC4899',
  ctaGradient: true,
};
