// Core TypeScript types for Lab Creator — aligned with SPECYFIKACJA.md

export type Gradient = {
  type: 'gradient';
  angle: string;   // "135deg"
  c1: string;      // hex
  c2: string;      // hex
};

export type Brand = {
  bgColor: string;
  textColor: string;
  ctaColor: string;
  ctaColor2: string;        // second gradient color for CTA
  ctaTextColor: string;
  ctaIsGradient: boolean;
  fontHeading: string;      // "Instrument Serif", "Inter", "Playfair Display"
  fontBody: string;
  density: 'compact' | 'normal' | 'spacious';
  borderRadius: number;
  palette: string[];        // 6 hex colors
  logo?: { src: string; alt: string };
};

export const DEFAULT_BRAND: Brand = {
  bgColor: '#FFFFFF',
  textColor: '#0F172A',
  ctaColor: '#6366F1',
  ctaColor2: '#EC4899',
  ctaTextColor: '#FFFFFF',
  ctaIsGradient: true,
  fontHeading: 'Instrument Serif',
  fontBody: 'Inter',
  density: 'normal',
  borderRadius: 8,
  palette: ['#FFFFFF', '#FEF7ED', '#FEF3C7', '#EEF2FF', '#6366F1', '#0F172A'],
};

export type SectionContent = Record<string, unknown>;

export type Section = {
  id: string;
  code: string;             // "HE1", "PB2", "CT3"
  variant?: string;
  name: string;
  size: 'S' | 'M' | 'L';
  bgColor?: string | Gradient | null;   // null = z brandu
  ctaColor?: string | Gradient | null;
  content: SectionContent;
  hidden?: boolean;
  brandWarning?: string;
  padding?: { top: number; right: number; bottom: number; left: number };
  // Backend fields
  block_code?: string;      // alias for code (backend compat)
  slots_json?: Record<string, unknown> | null;
  is_visible?: boolean;
  position?: number;
};

export type Page = {
  id: string;
  name: string;
  slug: string;
  sections: Section[];
  isHome: boolean;
};

export type Project = {
  id: string;
  name: string;
  brief: string;
  brand: Brand;
  pages: Page[];
  createdAt?: string;
  updatedAt?: string;
  publishedUrl?: string;
};

export type Block = {
  code: string;
  cat: string;
  name: string;
  desc: string;
  size: 'S' | 'M' | 'L';
};

export type Category = {
  name: string;
  color: string;
  icon: string;
};

export const CATEGORIES: Record<string, Category> = {
  NA: { name: 'Nawigacja', color: '#8B5CF6', icon: 'menu' },
  HE: { name: 'Hero', color: '#EC4899', icon: 'zap' },
  PB: { name: 'Problem', color: '#F59E0B', icon: 'alert-triangle' },
  RO: { name: 'Rozwiązanie', color: '#10B981', icon: 'check-circle' },
  KR: { name: 'Korzyści', color: '#06B6D4', icon: 'trending-up' },
  CF: { name: 'Cechy', color: '#0EA5E9', icon: 'star' },
  OB: { name: 'Obiekcje', color: '#F97316', icon: 'message-square' },
  FI: { name: 'O firmie', color: '#6366F1', icon: 'users' },
  OF: { name: 'Oferta', color: '#EAB308', icon: 'package' },
  PR: { name: 'Proces', color: '#14B8A6', icon: 'git-branch' },
  OP: { name: 'Opinie', color: '#EC4899', icon: 'star' },
  ZE: { name: 'Zespół', color: '#8B5CF6', icon: 'users' },
  CE: { name: 'Cennik', color: '#10B981', icon: 'dollar-sign' },
  CT: { name: 'CTA', color: '#EF4444', icon: 'zap' },
  KO: { name: 'Kontakt', color: '#0EA5E9', icon: 'phone' },
  FA: { name: 'FAQ', color: '#A855F7', icon: 'help-circle' },
  RE: { name: 'Realizacje', color: '#F97316', icon: 'image' },
  LO: { name: 'Loga', color: '#64748B', icon: 'layout' },
  ST: { name: 'Statystyki', color: '#14B8A6', icon: 'bar-chart' },
  FO: { name: 'Stopka', color: '#475569', icon: 'layout' },
};

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

export const BRAND_PALETTE = [
  { name: 'Biały', value: '#FFFFFF', textOn: '#0F172A' },
  { name: 'Kremowy', value: '#FEF7ED', textOn: '#78350F' },
  { name: 'Piaskowy', value: '#FEF3C7', textOn: '#78350F' },
  { name: 'Niebieski', value: '#EEF2FF', textOn: '#3730A3' },
  { name: 'Brand', value: '#6366F1', textOn: '#FFFFFF' },
  { name: 'Ciemny', value: '#0F172A', textOn: '#FFFFFF' },
];

export const FONT_OPTIONS = [
  'Inter',
  'Instrument Serif',
  'Playfair Display',
  'Lato',
  'Montserrat',
  'Open Sans',
  'Raleway',
  'Merriweather',
  'DM Serif Display',
  'Sora',
];

// Gradient presets for GradientPopover
export const GRADIENT_PRESETS = [
  { c1: '#6366F1', c2: '#EC4899', label: 'Fiolet → Róż' },
  { c1: '#06B6D4', c2: '#6366F1', label: 'Cyan → Fiolet' },
  { c1: '#10B981', c2: '#06B6D4', label: 'Zieleń → Cyan' },
  { c1: '#F59E0B', c2: '#EF4444', label: 'Złoto → Czerwień' },
  { c1: '#8B5CF6', c2: '#EC4899', label: 'Purpura → Róż' },
  { c1: '#0F172A', c2: '#334155', label: 'Czarny → Grafit' },
  { c1: '#1E293B', c2: '#6366F1', label: 'Granat → Fiolet' },
  { c1: '#FEF3C7', c2: '#FEF7ED', label: 'Piasek → Krem' },
];

export const GRADIENT_ANGLES = [
  { label: '→', value: '90deg' },
  { label: '↗', value: '45deg' },
  { label: '↓', value: '180deg' },
  { label: '↘', value: '135deg' },
  { label: '←', value: '270deg' },
  { label: '↙', value: '225deg' },
  { label: '↑', value: '0deg' },
  { label: '↖', value: '315deg' },
];

// Helper to get CSS string from bgColor (string | Gradient | null)
export function bgColorToCSS(bgColor: string | Gradient | null | undefined, fallback = '#FFFFFF'): string {
  if (!bgColor) return fallback;
  if (typeof bgColor === 'string') return bgColor;
  if (bgColor.type === 'gradient') {
    return `linear-gradient(${bgColor.angle}, ${bgColor.c1}, ${bgColor.c2})`;
  }
  return fallback;
}

// Luminance check for text color
export function isDark(hex: string): boolean {
  const c = hex.replace('#', '');
  if (c.length < 6) return false;
  const r = parseInt(c.substr(0, 2), 16);
  const g = parseInt(c.substr(2, 2), 16);
  const b = parseInt(c.substr(4, 2), 16);
  return (0.299 * r + 0.587 * g + 0.114 * b) < 128;
}
