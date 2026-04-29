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
  thumb?: string;
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
  // ─── Nawigacja ───
  { code: 'NA1', cat: 'NA', name: 'Nawigacja jasna', desc: 'Jasne tło, logo lewo, menu prawo, CTA', size: 'S',
    thumb: '<rect x="2" y="6" width="12" height="4" rx="1" fill="#8B5CF6"/><rect x="38" y="7" width="8" height="2" rx="1" fill="#CBD5E1"/><rect x="50" y="7" width="8" height="2" rx="1" fill="#CBD5E1"/><rect x="62" y="6" width="14" height="4" rx="2" fill="#8B5CF6"/>' },
  { code: 'NA2', cat: 'NA', name: 'Nawigacja ciemna', desc: 'Ciemne tło, białe teksty', size: 'S',
    thumb: '<rect x="0" y="0" width="80" height="16" fill="#1E293B"/><rect x="2" y="6" width="12" height="4" rx="1" fill="#fff"/><rect x="38" y="7" width="8" height="2" rx="1" fill="#94A3B8"/><rect x="50" y="7" width="8" height="2" rx="1" fill="#94A3B8"/><rect x="62" y="6" width="14" height="4" rx="2" fill="#8B5CF6"/>' },
  { code: 'NA3', cat: 'NA', name: 'Nawigacja z podkreśleniem', desc: 'Menu wycentrowane, aktywne podkreślone', size: 'S',
    thumb: '<rect x="2" y="6" width="12" height="4" rx="1" fill="#8B5CF6"/><rect x="28" y="7" width="8" height="2" rx="1" fill="#CBD5E1"/><rect x="40" y="7" width="8" height="2" rx="1" fill="#0F172A"/><line x1="40" y1="11" x2="48" y2="11" stroke="#8B5CF6" stroke-width="1.5"/><rect x="52" y="7" width="8" height="2" rx="1" fill="#CBD5E1"/>' },

  // ─── Hero ───
  { code: 'HE1', cat: 'HE', name: 'Hero centered + statystyki', desc: 'Ciemne tło, nagłówek, pod spodem 3-4 stat', size: 'L',
    thumb: '<rect x="0" y="0" width="80" height="56" fill="#1E293B"/><rect x="15" y="10" width="50" height="5" rx="1" fill="#fff"/><rect x="22" y="20" width="36" height="3" rx="1" fill="#94A3B8"/><rect x="30" y="28" width="20" height="5" rx="2" fill="#EC4899"/><g fill="#64748B"><rect x="8" y="42" width="14" height="3" rx="1"/><rect x="33" y="42" width="14" height="3" rx="1"/><rect x="58" y="42" width="14" height="3" rx="1"/></g>' },
  { code: 'HE2', cat: 'HE', name: 'Hero split — tekst + zdjęcie', desc: 'Podział 50/50, tekst L, zdjęcie R', size: 'L',
    thumb: '<rect x="4" y="12" width="30" height="4" rx="1" fill="#0F172A"/><rect x="4" y="20" width="26" height="3" rx="1" fill="#94A3B8"/><rect x="4" y="28" width="16" height="5" rx="2" fill="#EC4899"/><rect x="44" y="6" width="32" height="44" rx="3" fill="#E2E8F0"/>' },
  { code: 'HE3', cat: 'HE', name: 'Hero split — tekst + formularz', desc: 'Split z formularzem kontaktowym', size: 'L',
    thumb: '<rect x="4" y="12" width="30" height="4" rx="1" fill="#0F172A"/><rect x="4" y="20" width="26" height="3" rx="1" fill="#94A3B8"/><rect x="44" y="8" width="32" height="40" rx="3" fill="#F1F5F9" stroke="#E2E8F0" stroke-width=".5"/><rect x="48" y="14" width="24" height="4" rx="1" fill="#fff" stroke="#E2E8F0" stroke-width=".5"/><rect x="48" y="22" width="24" height="4" rx="1" fill="#fff" stroke="#E2E8F0" stroke-width=".5"/><rect x="48" y="30" width="24" height="4" rx="1" fill="#fff" stroke="#E2E8F0" stroke-width=".5"/><rect x="48" y="38" width="24" height="6" rx="2" fill="#6366F1"/>' },
  { code: 'HE4', cat: 'HE', name: 'Hero video background', desc: 'Video w tle, overlay, centered text', size: 'L',
    thumb: '<rect x="0" y="0" width="80" height="56" fill="#334155"/><rect x="0" y="0" width="80" height="56" fill="#000" opacity=".3"/><rect x="20" y="14" width="40" height="5" rx="1" fill="#fff"/><rect x="25" y="24" width="30" height="3" rx="1" fill="#CBD5E1"/><polygon points="38,34 44,38 38,42" fill="#fff"/>' },
  { code: 'HE5', cat: 'HE', name: 'Hero minimal centered', desc: 'Minimalistyczny, dużo przestrzeni', size: 'M',
    thumb: '<rect x="20" y="18" width="40" height="5" rx="1" fill="#0F172A"/><rect x="25" y="28" width="30" height="3" rx="1" fill="#94A3B8"/><rect x="30" y="36" width="20" height="5" rx="2" fill="#6366F1"/>' },

  // ─── Problem ───
  { code: 'PB1', cat: 'PB', name: 'Problem — lista z opisem', desc: '3-4 karty problemów z ikonami', size: 'M',
    thumb: '<rect x="25" y="4" width="30" height="4" rx="1" fill="#F59E0B"/><g fill="#FEF3C7" stroke="#F59E0B" stroke-width=".5"><rect x="4" y="16" width="22" height="30" rx="2"/><rect x="29" y="16" width="22" height="30" rx="2"/><rect x="54" y="16" width="22" height="30" rx="2"/></g>' },
  { code: 'PB2', cat: 'PB', name: 'Problem — pytania retoryczne', desc: 'Seria pytań rezonujących z bolączkami', size: 'M',
    thumb: '<rect x="20" y="6" width="40" height="4" rx="1" fill="#F59E0B"/><rect x="10" y="18" width="60" height="3" rx="1" fill="#FDE68A"/><rect x="14" y="26" width="52" height="3" rx="1" fill="#FDE68A"/><rect x="12" y="34" width="56" height="3" rx="1" fill="#FDE68A"/><rect x="16" y="42" width="48" height="3" rx="1" fill="#FDE68A"/>' },
  { code: 'PB3', cat: 'PB', name: 'Problem — statystyki', desc: 'Problemy poparte liczbami', size: 'M',
    thumb: '<rect x="25" y="4" width="30" height="4" rx="1" fill="#F59E0B"/><g fill="#0F172A"><rect x="10" y="18" width="12" height="6" rx="1"/><rect x="34" y="18" width="12" height="6" rx="1"/><rect x="58" y="18" width="12" height="6" rx="1"/></g><g fill="#94A3B8"><rect x="8" y="28" width="16" height="2" rx="1"/><rect x="32" y="28" width="16" height="2" rx="1"/><rect x="56" y="28" width="16" height="2" rx="1"/></g>' },

  // ─── Rozwiązanie ───
  { code: 'RO1', cat: 'RO', name: 'Rozwiązanie — 3 karty', desc: '3 karty z ikonami', size: 'M',
    thumb: '<rect x="25" y="4" width="30" height="4" rx="1" fill="#10B981"/><g fill="#ECFDF5" stroke="#10B981" stroke-width=".5"><rect x="4" y="16" width="22" height="28" rx="2"/><rect x="29" y="16" width="22" height="28" rx="2"/><rect x="54" y="16" width="22" height="28" rx="2"/></g><g fill="#10B981"><circle cx="15" cy="24" r="3"/><circle cx="40" cy="24" r="3"/><circle cx="65" cy="24" r="3"/></g>' },
  { code: 'RO2', cat: 'RO', name: 'Rozwiązanie — split z obrazem', desc: 'Lista cech + zdjęcie', size: 'M',
    thumb: '<rect x="4" y="8" width="28" height="4" rx="1" fill="#10B981"/><g fill="#10B981"><circle cx="8" cy="20" r="2"/><circle cx="8" cy="28" r="2"/><circle cx="8" cy="36" r="2"/></g><g fill="#94A3B8"><rect x="14" y="19" width="18" height="2" rx="1"/><rect x="14" y="27" width="18" height="2" rx="1"/><rect x="14" y="35" width="18" height="2" rx="1"/></g><rect x="42" y="6" width="34" height="40" rx="3" fill="#E2E8F0"/>' },

  // ─── Korzyści ───
  { code: 'KR1', cat: 'KR', name: 'Korzyści — grid 2x3', desc: '6 korzyści z ikonami', size: 'M',
    thumb: '<rect x="22" y="2" width="36" height="4" rx="1" fill="#06B6D4"/><g fill="#ECFEFF" stroke="#06B6D4" stroke-width=".4"><rect x="4" y="12" width="22" height="16" rx="2"/><rect x="29" y="12" width="22" height="16" rx="2"/><rect x="54" y="12" width="22" height="16" rx="2"/><rect x="4" y="32" width="22" height="16" rx="2"/><rect x="29" y="32" width="22" height="16" rx="2"/><rect x="54" y="32" width="22" height="16" rx="2"/></g>' },
  { code: 'KR2', cat: 'KR', name: 'Korzyści — duże liczby', desc: '4 liczby z opisami', size: 'M',
    thumb: '<rect x="22" y="4" width="36" height="4" rx="1" fill="#06B6D4"/><g fill="#06B6D4"><rect x="6" y="18" width="12" height="8" rx="1"/><rect x="24" y="18" width="12" height="8" rx="1"/><rect x="44" y="18" width="12" height="8" rx="1"/><rect x="62" y="18" width="12" height="8" rx="1"/></g><g fill="#94A3B8"><rect x="4" y="30" width="16" height="2" rx="1"/><rect x="22" y="30" width="16" height="2" rx="1"/><rect x="42" y="30" width="16" height="2" rx="1"/><rect x="60" y="30" width="16" height="2" rx="1"/></g>' },

  // ─── Cechy ───
  { code: 'CF1', cat: 'CF', name: 'Cechy — karty 3 kolumny', desc: '3 karty z ikonami', size: 'M',
    thumb: '<rect x="22" y="4" width="36" height="4" rx="1" fill="#0EA5E9"/><g fill="#F0F9FF" stroke="#0EA5E9" stroke-width=".4"><rect x="4" y="14" width="22" height="30" rx="2"/><rect x="29" y="14" width="22" height="30" rx="2"/><rect x="54" y="14" width="22" height="30" rx="2"/></g>' },
  { code: 'CF2', cat: 'CF', name: 'Cechy — checklist 2 kolumny', desc: 'Prosta lista z checkami', size: 'M',
    thumb: '<rect x="22" y="4" width="36" height="4" rx="1" fill="#0EA5E9"/><g fill="#0EA5E9"><rect x="6" y="16" width="4" height="4" rx="1"/><rect x="6" y="24" width="4" height="4" rx="1"/><rect x="6" y="32" width="4" height="4" rx="1"/><rect x="44" y="16" width="4" height="4" rx="1"/><rect x="44" y="24" width="4" height="4" rx="1"/><rect x="44" y="32" width="4" height="4" rx="1"/></g><g fill="#94A3B8"><rect x="14" y="17" width="22" height="2" rx="1"/><rect x="14" y="25" width="22" height="2" rx="1"/><rect x="14" y="33" width="22" height="2" rx="1"/><rect x="52" y="17" width="22" height="2" rx="1"/><rect x="52" y="25" width="22" height="2" rx="1"/><rect x="52" y="33" width="22" height="2" rx="1"/></g>' },

  // ─── Obiekcje ───
  { code: 'OB1', cat: 'OB', name: 'Obiekcje — FAQ style', desc: 'Rozwijane pytania', size: 'M',
    thumb: '<rect x="22" y="4" width="36" height="4" rx="1" fill="#F97316"/><g fill="#FFF7ED" stroke="#F97316" stroke-width=".4"><rect x="8" y="14" width="64" height="8" rx="2"/><rect x="8" y="26" width="64" height="8" rx="2"/><rect x="8" y="38" width="64" height="8" rx="2"/></g>' },

  // ─── O firmie ───
  { code: 'FI1', cat: 'FI', name: 'O firmie — tekst + zdjęcie', desc: 'Opis L, zdjęcie R', size: 'M',
    thumb: '<rect x="4" y="8" width="28" height="4" rx="1" fill="#6366F1"/><rect x="4" y="16" width="32" height="2" rx="1" fill="#94A3B8"/><rect x="4" y="22" width="30" height="2" rx="1" fill="#94A3B8"/><rect x="4" y="28" width="26" height="2" rx="1" fill="#94A3B8"/><rect x="44" y="6" width="32" height="36" rx="3" fill="#E2E8F0"/>' },
  { code: 'FI2', cat: 'FI', name: 'O firmie — zdjęcie + tekst', desc: 'Odwrócony FI1', size: 'M',
    thumb: '<rect x="4" y="6" width="32" height="36" rx="3" fill="#E2E8F0"/><rect x="44" y="8" width="28" height="4" rx="1" fill="#6366F1"/><rect x="44" y="16" width="32" height="2" rx="1" fill="#94A3B8"/><rect x="44" y="22" width="30" height="2" rx="1" fill="#94A3B8"/><rect x="44" y="28" width="26" height="2" rx="1" fill="#94A3B8"/>' },
  { code: 'FI3', cat: 'FI', name: 'O firmie — centered + cytat', desc: 'Osobisty, cytat założyciela', size: 'M',
    thumb: '<circle cx="40" cy="14" r="8" fill="#E2E8F0"/><rect x="20" y="26" width="40" height="3" rx="1" fill="#6366F1"/><rect x="24" y="34" width="32" height="2" rx="1" fill="#94A3B8"/><rect x="26" y="40" width="28" height="2" rx="1" fill="#94A3B8"/>' },
  { code: 'FI4', cat: 'FI', name: 'O firmie — timeline historia', desc: 'Oś czasu firmy', size: 'L',
    thumb: '<rect x="20" y="2" width="40" height="4" rx="1" fill="#6366F1"/><line x1="40" y1="12" x2="40" y2="52" stroke="#E2E8F0" stroke-width="1"/><g fill="#6366F1"><circle cx="40" cy="16" r="3"/><circle cx="40" cy="30" r="3"/><circle cx="40" cy="44" r="3"/></g><g fill="#94A3B8"><rect x="48" y="14" width="20" height="2" rx="1"/><rect x="12" y="28" width="20" height="2" rx="1"/><rect x="48" y="42" width="20" height="2" rx="1"/></g>' },

  // ─── Oferta ───
  { code: 'OF1', cat: 'OF', name: 'Oferta — karty usług', desc: '3 karty z cennikiem', size: 'M',
    thumb: '<rect x="22" y="2" width="36" height="4" rx="1" fill="#EAB308"/><g fill="#FEFCE8" stroke="#EAB308" stroke-width=".4"><rect x="4" y="12" width="22" height="36" rx="2"/><rect x="29" y="8" width="22" height="40" rx="2"/><rect x="54" y="12" width="22" height="36" rx="2"/></g><rect x="29" y="8" width="22" height="40" rx="2" fill="none" stroke="#EAB308" stroke-width="1"/>' },
  { code: 'OF2', cat: 'OF', name: 'Oferta — lista z ikonami', desc: 'Kompaktowa lista', size: 'M',
    thumb: '<rect x="22" y="4" width="36" height="4" rx="1" fill="#EAB308"/><g fill="#EAB308"><circle cx="12" cy="20" r="3"/><circle cx="12" cy="32" r="3"/><circle cx="12" cy="44" r="3"/></g><g fill="#94A3B8"><rect x="20" y="18" width="50" height="3" rx="1"/><rect x="20" y="30" width="50" height="3" rx="1"/><rect x="20" y="42" width="50" height="3" rx="1"/></g>' },

  // ─── Proces ───
  { code: 'PR1', cat: 'PR', name: 'Proces — kroki poziomo', desc: '4 ponumerowane kroki', size: 'M',
    thumb: '<rect x="22" y="2" width="36" height="4" rx="1" fill="#14B8A6"/><g fill="#14B8A6"><circle cx="12" cy="24" r="6"/><circle cx="32" cy="24" r="6"/><circle cx="52" cy="24" r="6"/><circle cx="72" cy="24" r="4"/></g><g fill="#fff" font-size="7" text-anchor="middle"><text x="12" y="27">1</text><text x="32" y="27">2</text><text x="52" y="27">3</text></g><g stroke="#14B8A6" stroke-width=".5"><line x1="18" y1="24" x2="26" y2="24"/><line x1="38" y1="24" x2="46" y2="24"/><line x1="58" y1="24" x2="68" y2="24"/></g>' },
  { code: 'PR2', cat: 'PR', name: 'Proces — timeline pionowo', desc: 'Pionowy timeline', size: 'M',
    thumb: '<line x1="16" y1="8" x2="16" y2="50" stroke="#E2E8F0" stroke-width="1"/><g fill="#14B8A6"><circle cx="16" cy="12" r="4"/><circle cx="16" cy="28" r="4"/><circle cx="16" cy="44" r="4"/></g><g fill="#94A3B8"><rect x="26" y="10" width="46" height="3" rx="1"/><rect x="26" y="26" width="46" height="3" rx="1"/><rect x="26" y="42" width="46" height="3" rx="1"/></g>' },

  // ─── Opinie ───
  { code: 'OP1', cat: 'OP', name: 'Opinie — 3 karty', desc: 'Z avatarami i gwiazdkami', size: 'M',
    thumb: '<rect x="22" y="2" width="36" height="4" rx="1" fill="#EC4899"/><g fill="#FDF2F8" stroke="#EC4899" stroke-width=".4"><rect x="4" y="12" width="22" height="32" rx="2"/><rect x="29" y="12" width="22" height="32" rx="2"/><rect x="54" y="12" width="22" height="32" rx="2"/></g><g fill="#EC4899"><circle cx="15" cy="22" r="4"/><circle cx="40" cy="22" r="4"/><circle cx="65" cy="22" r="4"/></g>' },
  { code: 'OP2', cat: 'OP', name: 'Opinie — duży cytat', desc: 'Jedna dominująca opinia', size: 'M',
    thumb: '<rect x="10" y="4" width="60" height="44" rx="4" fill="#FDF2F8" stroke="#EC4899" stroke-width=".4"/><text x="16" y="20" fill="#EC4899" font-size="18">"</text><rect x="16" y="24" width="48" height="2" rx="1" fill="#94A3B8"/><rect x="20" y="30" width="40" height="2" rx="1" fill="#94A3B8"/><circle cx="40" cy="42" r="4" fill="#EC4899"/>' },

  // ─── Zespół ───
  { code: 'ZE1', cat: 'ZE', name: 'Zespół — grid 4 osoby', desc: 'Avatary + role', size: 'M',
    thumb: '<rect x="22" y="2" width="36" height="4" rx="1" fill="#8B5CF6"/><g fill="#E2E8F0"><rect x="6" y="14" width="14" height="16" rx="2"/><rect x="24" y="14" width="14" height="16" rx="2"/><rect x="42" y="14" width="14" height="16" rx="2"/><rect x="60" y="14" width="14" height="16" rx="2"/></g><g fill="#94A3B8"><rect x="8" y="34" width="10" height="2" rx="1"/><rect x="26" y="34" width="10" height="2" rx="1"/><rect x="44" y="34" width="10" height="2" rx="1"/><rect x="62" y="34" width="10" height="2" rx="1"/></g>' },
  { code: 'ZE2', cat: 'ZE', name: 'Zespół — lista z bio', desc: 'Foto + biografia', size: 'L',
    thumb: '<rect x="4" y="6" width="20" height="20" rx="3" fill="#E2E8F0"/><rect x="30" y="8" width="40" height="3" rx="1" fill="#8B5CF6"/><rect x="30" y="16" width="44" height="2" rx="1" fill="#94A3B8"/><rect x="30" y="22" width="38" height="2" rx="1" fill="#94A3B8"/><rect x="4" y="34" width="20" height="20" rx="3" fill="#E2E8F0"/><rect x="30" y="36" width="40" height="3" rx="1" fill="#8B5CF6"/><rect x="30" y="44" width="44" height="2" rx="1" fill="#94A3B8"/><rect x="30" y="50" width="38" height="2" rx="1" fill="#94A3B8"/>' },

  // ─── Cennik ───
  { code: 'CE1', cat: 'CE', name: 'Cennik — 3 pakiety', desc: 'Środkowy wyróżniony', size: 'L',
    thumb: '<rect x="22" y="2" width="36" height="4" rx="1" fill="#10B981"/><g fill="#F0FDF4" stroke="#10B981" stroke-width=".4"><rect x="4" y="14" width="22" height="36" rx="2"/><rect x="54" y="14" width="22" height="36" rx="2"/></g><rect x="29" y="10" width="22" height="42" rx="2" fill="#10B981" opacity=".15" stroke="#10B981" stroke-width="1"/>' },

  // ─── CTA ───
  { code: 'CT1', cat: 'CT', name: 'CTA — ciemne tło', desc: 'Pełna szerokość, bold', size: 'M',
    thumb: '<rect x="0" y="8" width="80" height="40" rx="0" fill="#1E293B"/><rect x="18" y="16" width="44" height="5" rx="1" fill="#fff"/><rect x="24" y="26" width="32" height="3" rx="1" fill="#94A3B8"/><rect x="28" y="34" width="24" height="6" rx="3" fill="#EF4444"/>' },
  { code: 'CT2', cat: 'CT', name: 'CTA — kolor + grafika', desc: 'Split z grafiką', size: 'M',
    thumb: '<rect x="0" y="8" width="80" height="40" rx="0" fill="#EF4444" opacity=".1"/><rect x="4" y="16" width="32" height="4" rx="1" fill="#EF4444"/><rect x="4" y="24" width="28" height="3" rx="1" fill="#94A3B8"/><rect x="4" y="32" width="18" height="6" rx="3" fill="#EF4444"/><rect x="50" y="14" width="24" height="24" rx="3" fill="#E2E8F0"/>' },
  { code: 'CT3', cat: 'CT', name: 'CTA — minimalistyczny', desc: 'Jedna linia', size: 'S',
    thumb: '<rect x="14" y="8" width="30" height="4" rx="1" fill="#0F172A"/><rect x="50" y="7" width="18" height="6" rx="3" fill="#EF4444"/>' },

  // ─── Kontakt ───
  { code: 'KO1', cat: 'KO', name: 'Kontakt — formularz + dane', desc: 'Split: formularz L, dane R', size: 'L',
    thumb: '<rect x="4" y="4" width="38" height="48" rx="3" fill="#F0F9FF" stroke="#0EA5E9" stroke-width=".4"/><g fill="#fff" stroke="#E2E8F0" stroke-width=".5"><rect x="8" y="12" width="30" height="5" rx="1"/><rect x="8" y="22" width="30" height="5" rx="1"/><rect x="8" y="32" width="30" height="10" rx="1"/></g><rect x="8" y="46" width="30" height="5" rx="2" fill="#0EA5E9"/><rect x="50" y="12" width="24" height="3" rx="1" fill="#0EA5E9"/><rect x="50" y="20" width="20" height="2" rx="1" fill="#94A3B8"/><rect x="50" y="28" width="22" height="2" rx="1" fill="#94A3B8"/><rect x="50" y="36" width="18" height="2" rx="1" fill="#94A3B8"/>' },

  // ─── FAQ ───
  { code: 'FA1', cat: 'FA', name: 'FAQ — accordion', desc: 'Rozwijane pytania', size: 'M',
    thumb: '<rect x="22" y="2" width="36" height="4" rx="1" fill="#A855F7"/><g fill="#FAF5FF" stroke="#A855F7" stroke-width=".4"><rect x="8" y="12" width="64" height="8" rx="2"/><rect x="8" y="24" width="64" height="14" rx="2"/><rect x="8" y="42" width="64" height="8" rx="2"/></g><rect x="12" y="28" width="56" height="2" rx="1" fill="#94A3B8"/><rect x="12" y="33" width="44" height="2" rx="1" fill="#94A3B8"/>' },

  // ─── Realizacje ───
  { code: 'RE1', cat: 'RE', name: 'Realizacje — grid kart', desc: 'Zdjęcia projektów', size: 'L',
    thumb: '<rect x="22" y="2" width="36" height="4" rx="1" fill="#F97316"/><g fill="#E2E8F0"><rect x="4" y="12" width="22" height="18" rx="2"/><rect x="29" y="12" width="22" height="18" rx="2"/><rect x="54" y="12" width="22" height="18" rx="2"/><rect x="4" y="34" width="22" height="18" rx="2"/><rect x="29" y="34" width="22" height="18" rx="2"/><rect x="54" y="34" width="22" height="18" rx="2"/></g>' },

  // ─── Loga ───
  { code: 'LO1', cat: 'LO', name: 'Loga klientów — rząd', desc: 'Loga w jednym rzędzie', size: 'S',
    thumb: '<rect x="22" y="2" width="36" height="3" rx="1" fill="#64748B"/><g fill="#E2E8F0"><rect x="6" y="10" width="14" height="8" rx="2"/><rect x="24" y="10" width="14" height="8" rx="2"/><rect x="42" y="10" width="14" height="8" rx="2"/><rect x="60" y="10" width="14" height="8" rx="2"/></g>' },

  // ─── Statystyki ───
  { code: 'ST1', cat: 'ST', name: 'Statystyki — 4 liczby', desc: 'Duże liczby z opisami', size: 'S',
    thumb: '<g fill="#14B8A6"><rect x="6" y="4" width="12" height="6" rx="1"/><rect x="24" y="4" width="12" height="6" rx="1"/><rect x="44" y="4" width="12" height="6" rx="1"/><rect x="62" y="4" width="12" height="6" rx="1"/></g><g fill="#94A3B8"><rect x="4" y="14" width="16" height="2" rx="1"/><rect x="22" y="14" width="16" height="2" rx="1"/><rect x="42" y="14" width="16" height="2" rx="1"/><rect x="60" y="14" width="16" height="2" rx="1"/></g>' },

  // ─── Stopka ───
  { code: 'FO1', cat: 'FO', name: 'Stopka — 4 kolumny', desc: 'Logo + linki + copyright', size: 'M',
    thumb: '<rect x="0" y="0" width="80" height="56" fill="#1E293B"/><rect x="4" y="6" width="14" height="4" rx="1" fill="#fff"/><g fill="#94A3B8"><rect x="4" y="16" width="10" height="2" rx="1"/><rect x="4" y="22" width="10" height="2" rx="1"/><rect x="24" y="16" width="10" height="2" rx="1"/><rect x="24" y="22" width="10" height="2" rx="1"/><rect x="44" y="16" width="10" height="2" rx="1"/><rect x="44" y="22" width="10" height="2" rx="1"/><rect x="64" y="16" width="10" height="2" rx="1"/><rect x="64" y="22" width="10" height="2" rx="1"/></g><line x1="4" y1="42" x2="76" y2="42" stroke="#334155" stroke-width=".5"/><rect x="4" y="46" width="40" height="2" rx="1" fill="#475569"/>' },
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
