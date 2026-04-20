/**
 * TypeScript types for WebCreator (Brief 32).
 */

// ─── Brief (Step 1) ───

export interface BriefData {
  // Punkt 1
  forWhom: "firma" | "osoba" | "sklep" | "";
  siteType: string;

  // Punkt 2
  companyName: string;
  whatYouDo: string;
  hasWebsite: boolean;
  currentUrl?: string;
  industry: string;

  // Punkt 3
  clientTypes: string[];
  clientB2B?: string;
  clientB2C?: string;
  clientB2G?: string;
  clientNGO?: string;
  decisionMaker: string;

  // Punkt 4
  clientValues: string;
  clientLikes: string;
  clientDislikes: string;
  clientNeeds: string;

  // Punkt 5
  slogan?: string;
  mission?: string;
  usp: string;
  whyChooseUs: string;
  strengths: string[];

  // Punkt 6
  brandPos: string[];

  // Punkt 7
  writingStyle: string[];

  // Punkt 8
  mainGoal: string[];
  siteContent: string[];

  // Punkt 9
  impressionCustom: string;
  impThink: string[];
  impFeel: string[];

  // Punkt 10
  menuProposal?: string;
  openToAI?: boolean;

  // Punkt 11
  extraWishes?: string;

  // Step 2 extra (stored in brief)
  contentVision?: string;
}

// ─── Style (Step 3) ───

export interface StyleData {
  palette_preset: string;
  color_primary?: string;
  color_secondary?: string;
  color_accent?: string;
  heading_font: string;
  body_font: string;
  section_theme: string;
  border_radius: string;
}

// ─── Materials ───

export interface ProjectMaterial {
  id: string;
  project_id: string;
  type: string;
  file_url?: string;
  original_filename?: string;
  file_size?: number;
  mime_type?: string;
  external_url?: string;
  description?: string;
  created_at: string;
}

// ─── Validation (Step 4) ───

export interface ValidationItem {
  key: string;
  status: "ok" | "warning" | "error";
  message: string;
  suggestion?: string;
}

// ─── Chat ───

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// ─── Section (Step 5-6) ───

export interface ProjectSection {
  id: string;
  project_id: string;
  block_code: string;
  position: number;
  variant: string;
  is_visible: boolean;
  slots_json: Record<string, unknown>;
  created_at: string;
}

export interface BlockTemplate {
  code: string;
  category_code: string;
  name: string;
  description: string;
  html_template: string;
  slots_definition: SlotDefinition[];
  media_type: string;
  layout_type: string;
  size: string;
  is_active: boolean;
}

export interface SlotDefinition {
  id: string;
  type: string;
  label: string;
  max_length?: number;
  default?: string;
}

export interface BlockCategory {
  code: string;
  name: string;
  icon: string;
  order: number;
}

export interface StockPhoto {
  url: string;
  thumb: string;
  author: string;
  source: "unsplash" | "pexels";
  download_url: string;
}

export interface GenerateProgress {
  status: "generating" | "completed" | "error";
  message: string;
  progress: number;
  result?: { sections: number };
}

// ─── Project ───

export interface Project {
  id: string;
  organization_id: string;
  created_by: string;
  name: string;
  site_type?: string;
  status: string;
  current_step: number;
  brief_json?: Partial<BriefData>;
  materials_meta?: Record<string, unknown>;
  style_json?: Partial<StyleData>;
  validation_json?: { items: ValidationItem[]; validated_at?: string };
  config_json?: Record<string, unknown>;
  check_json?: Record<string, unknown>;
  domain?: string;
  custom_domain?: string;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

// ─── Config (Step 7) ───

export interface FormsConfig {
  contact_email?: string;
  thank_you_message?: string;
  thank_you_url?: string;
  send_email_notification?: boolean;
  fields?: Array<{ name: string; type: string; required?: boolean }>;
}

export interface SocialConfig {
  facebook?: string;
  instagram?: string;
  linkedin?: string;
  twitter?: string;
  youtube?: string;
  tiktok?: string;
}

export interface TrackingConfig {
  ga4_id?: string;
  gtm_id?: string;
  fb_pixel_id?: string;
  hotjar_id?: string;
  linkedin_id?: string;
  gsc_verification?: string;
  custom_head?: string;
  custom_body?: string;
}

export interface SeoConfig {
  meta_title?: string;
  meta_description?: string;
  og_title?: string;
  og_description?: string;
  og_image?: string;
  canonical_url?: string;
  language?: string;
  tracking?: TrackingConfig;
}

export interface CookieBanner {
  enabled: boolean;
  style: "bar" | "modal" | "corner";
  text?: string;
}

export interface LegalSource {
  source: "ai" | "own" | "none";
  html?: string;
}

export interface LegalConfig {
  privacy_policy?: LegalSource;
  terms?: LegalSource;
  cookie_banner?: CookieBanner;
  rodo?: { enabled: boolean; text?: string };
}

export interface HostingConfig {
  domain_type: "subdomain" | "custom";
  subdomain?: string;
  custom_domain?: string;
  deploy_method: "auto" | "ftp" | "zip";
  ftp?: { host?: string; port?: number; username?: string; password?: string; path?: string };
}

export interface ConfigData {
  forms?: FormsConfig;
  social?: SocialConfig;
  seo?: SeoConfig;
  legal?: LegalConfig;
  hosting?: HostingConfig;
}

// ─── AI Visibility (Brief 41) ───

export interface AIVisibilityLink {
  name: string;
  url: string;
}

export interface AIVisibilityCategoryItem {
  name: string;
  description?: string;
  period?: string;   // doświadczenie zawodowe
  school?: string;   // wykształcenie
  title?: string;    // wykształcenie — tytuł/kierunek
}

export interface AIVisibilityPerson {
  name: string;
  title?: string;
  categories?: Record<string, AIVisibilityCategoryItem[]>;
}

export interface AIVisibilityData {
  description?: string;
  social_profiles?: AIVisibilityLink[];
  websites?: AIVisibilityLink[];
  categories?: Record<string, AIVisibilityCategoryItem[]>;
  people?: AIVisibilityPerson[];
}

// ─── Readiness (Step 8) ───

export interface CheckItem {
  key: string;
  status: "pass" | "warn" | "error";
  message: string;
  suggestion?: string;
  fix_tab?: string;
}

export interface SkippedCheck {
  key: string;
  status: "skip";
  message: string;
}

export interface ReadinessResult {
  checks: CheckItem[];
  skipped: SkippedCheck[];
  can_publish: boolean;
  score: number;
}

// ─── Site Type Config (Brief 42) ───

export interface StylePreset {
  id: string;
  label: string;
  colors: string[];
}

export interface SiteTypeConfig {
  site_type: string;
  label: string;
  category: string;
  recommended_blocks: string[];
  min_sections: number;
  max_sections: number;
  allowed_block_categories: string[];
  prompt_hints: Record<string, string>;
  readiness_skip_checks: string[];
  readiness_modify_checks: Record<string, Record<string, unknown>>;
  config_defaults: Record<string, unknown>;
  style_presets: StylePreset[];
  brief_sections: string[];
  brief_content: string[];
}

// ─── Publishing (Step 9) ───

export interface PublishResult {
  subdomain: string;
  url: string;
  status: string;
  published_at?: string;
}

export interface FormSubmission {
  id: string;
  site_id: string;
  data_json: Record<string, unknown>;
  ip?: string;
  read: boolean;
  created_at: string;
}

// ─── Dashboard (Brief 36) ───

export interface SiteIntegration {
  id: string;
  provider: string;
  status: string;
  config_json: Record<string, string> | null;
  connected_at: string;
}

export interface IntegrationField {
  id: string;
  label: string;
  placeholder?: string;
}

export interface IntegrationCatalogItem {
  provider: string;
  name: string;
  description: string;
  difficulty: string;
  price: string;
  fields: IntegrationField[];
  v2?: boolean;
}

export interface IntegrationCategory {
  category: string;
  category_name: string;
  items: IntegrationCatalogItem[];
}

export interface AutomationTemplate {
  id: string;
  name: string;
  description: string;
  native: boolean;
}

export interface AutomationGroup {
  group: string;
  group_name: string;
  templates: AutomationTemplate[];
}

export interface DailyVisitors {
  date: string;
  count: number;
}

export interface TrafficSource {
  source: string;
  percentage: number;
}

export interface ProjectStats {
  period: string;
  visitors: number;
  leads: number;
  bounce_rate: number | null;
  avg_time_on_site: number | null;
  published_at: string | null;
  daily_visitors: DailyVisitors[];
  traffic_sources: TrafficSource[];
}

// ─── Constants ───

export const INDUSTRIES = [
  "IT / Technologia", "Marketing / Reklama", "E-commerce / Handel", "Edukacja / Szkolenia",
  "Finanse / Księgowość", "Budownictwo / Architektura", "Zdrowie / Medycyna", "Prawo / Kancelaria",
  "Gastronomia / HoReCa", "Turystyka / Hotelarstwo", "Produkcja / Przemysł",
  "Transport / Logistyka", "Nieruchomości", "Motoryzacja", "Uroda / Kosmetyka", "Fitness / Sport",
  "Fotografia / Wideo", "Sztuka / Kultura", "NGO / Fundacja", "Rolnictwo / Ekologia",
  "Consulting / Doradztwo", "HR / Rekrutacja", "Ubezpieczenia", "Telekomunikacja",
  "Media / Wydawnictwa", "Moda / Odzież", "Usługi dla domu", "Eventowe / Eventy", "Inne",
];

export const SITE_TYPES_FIRMA = [
  { id: "firmowa", label: "Strona firmowa", desc: "Pełna prezentacja firmy" },
  { id: "korporacyjna", label: "Korporacyjna", desc: "Duża firma, wiele działów" },
  { id: "blog", label: "Blog firmowy", desc: "Artykuły, aktualności, wiedza" },
  { id: "firmowa-blog", label: "Firmowa + Blog", desc: "Prezentacja firmy z sekcją blogową" },
  { id: "korporacyjna-blog", label: "Korporacyjna + Blog", desc: "Korporacja z blogiem i bazą wiedzy" },
  { id: "lp-produkt", label: "LP produktowa", desc: "Jeden produkt, pełna prezentacja" },
  { id: "lp-usluga", label: "LP usługowa", desc: "Jedna usługa, konwersja" },
  { id: "lp-wydarzenie", label: "LP wydarzenie", desc: "Konferencja, targi, event" },
  { id: "lp-webinar", label: "LP webinar", desc: "Webinar, kurs online" },
  { id: "lp-wizerunkowa", label: "LP wizerunkowa", desc: "Budowanie marki" },
  { id: "lp-lead", label: "LP lead magnet", desc: "Zbieranie kontaktów" },
  { id: "wizytowka", label: "Wizytówka", desc: "Prosta strona kontaktowa" },
];

export const SITE_TYPES_OSOBA = [
  { id: "ekspert", label: "Ekspert / Freelancer", desc: "Osobista marka ekspercka" },
  { id: "portfolio", label: "Portfolio", desc: "Prezentacja prac" },
  { id: "cv", label: "CV online", desc: "Interaktywne CV" },
  { id: "blog", label: "Blog", desc: "Blog osobisty" },
  { id: "wizytowka-osoba", label: "Wizytówka", desc: "Prosta strona kontaktowa" },
];

export const CLIENT_TYPES = [
  { id: "B2B", label: "B2B", desc: "Firmy, organizacje" },
  { id: "B2C", label: "B2C", desc: "Klienci indywidualni" },
  { id: "B2G", label: "B2G", desc: "Instytucje publiczne" },
  { id: "NGO", label: "NGO", desc: "Organizacje pozarządowe" },
];

export const STRENGTHS = [
  "Doświadczenie i historia", "Certyfikaty i nagrody", "Zespół ekspertów",
  "Innowacyjność", "Indywidualne podejście", "Szybkość realizacji",
  "Konkurencyjna cena", "Szeroka oferta", "Lokalna obecność",
  "Gwarancja jakości", "Wsparcie posprzedażowe", "Ekologia / odpowiedzialność",
];

export const BRAND_POSITIONS = [
  { id: "ekspercka", label: "Marka ekspercka", desc: "Wiedza, kompetencje, autorytet" },
  { id: "premium", label: "Marka premium", desc: "Luksus, wyjątkowość, jakość" },
  { id: "innowacyjna", label: "Marka innowacyjna", desc: "Nowoczesność, technologia, przyszłość" },
  { id: "przyjazna", label: "Marka przyjazna / bliska", desc: "Ciepło, zaufanie, partnerstwo" },
  { id: "lokalna", label: "Marka lokalna / rodzinna", desc: "Tradycja, lokalność, bliskość" },
  { id: "korporacyjna", label: "Marka korporacyjna", desc: "Skala, stabilność, profesjonalizm" },
];

export const WRITING_STYLES = [
  { id: "profesjonalny", label: "Profesjonalny / ekspercki", example: "Oferujemy kompleksowe rozwiązania..." },
  { id: "przyjazny", label: "Przyjazny / bezpośredni", example: "Pomożemy Ci rozwiązać..." },
  { id: "dynamiczny", label: "Dynamiczny / energiczny", example: "Zmieniamy zasady gry!" },
  { id: "elegancki", label: "Elegancki / premium", example: "Wyjątkowe doświadczenia..." },
  { id: "prosty", label: "Prosty / konkretny", example: "Robimy X. Efekt: Y." },
];

export const SITE_GOALS = [
  { id: "leady", label: "Zbieranie leadów", desc: "Formularze kontaktowe, zapytania" },
  { id: "spotkania", label: "Umawianie spotkań", desc: "Rezerwacja terminów" },
  { id: "sprzedaz", label: "Sprzedaż online", desc: "Sklep, koszyk, płatności" },
  { id: "marka", label: "Budowanie marki", desc: "Wizerunkowa prezentacja" },
  { id: "portfolio", label: "Prezentacja portfolio", desc: "Pokaz prac i realizacji" },
  { id: "rekrutacja", label: "Rekrutacja", desc: "Przyciąganie talentów" },
];

export const SITE_CONTENT = [
  "Oferta usług", "Produkty / katalog", "Cennik", "O firmie / o mnie",
  "Zespół / ludzie", "Opinie klientów", "Portfolio / realizacje", "Blog / aktualności",
  "FAQ / pytania", "Kontakt / formularz", "Mapa dojazdu", "Partnerzy / klienci",
  "Proces / jak działamy", "Korzyści / dlaczego my", "Certyfikaty / nagrody", "Kariera / oferty pracy",
];

export const IMPRESSIONS_THINK = [
  "To profesjonaliści, wiedzą co robią",
  "Ta firma jest godna zaufania",
  "To są innowatorzy w swojej branży",
  "Oferują najlepszy stosunek jakości do ceny",
  "Mają indywidualne podejście do klienta",
  "To eksperci w swojej dziedzinie",
  "Firma z ludzką twarzą, którą lubię",
];

export const IMPRESSIONS_FEEL = [
  "Spokój — jestem w dobrych rękach",
  "Ekscytacja — chcę z nimi współpracować",
  "Zaufanie — mogę im powierzyć mój problem",
  "Inspiracja — mają świeże podejście",
  "Prestiż — to marka premium",
  "Komfort — łatwo się z nimi dogadać",
];

export const PALETTE_PRESETS = [
  { id: "indigo-slate", label: "Indigo + Slate", colors: ["#4F46E5", "#64748B", "#E0E7FF"] },
  { id: "emerald-zinc", label: "Emerald + Zinc", colors: ["#059669", "#71717A", "#D1FAE5"] },
  { id: "amber-stone", label: "Amber + Stone", colors: ["#D97706", "#78716C", "#FEF3C7"] },
  { id: "rose-gray", label: "Rose + Gray", colors: ["#E11D48", "#6B7280", "#FFE4E6"] },
  { id: "violet-neutral", label: "Violet + Neutral", colors: ["#7C3AED", "#737373", "#EDE9FE"] },
  { id: "cyan-slate", label: "Cyan + Slate", colors: ["#0891B2", "#475569", "#CFFAFE"] },
];

export const FONT_PAIRS = [
  { id: "outfit-inter", heading: "Outfit", body: "Inter" },
  { id: "poppins-opensans", heading: "Poppins", body: "Open Sans" },
  { id: "playfair-lato", heading: "Playfair Display", body: "Lato" },
  { id: "montserrat-roboto", heading: "Montserrat", body: "Roboto" },
  { id: "raleway-sourcesans", heading: "Raleway", body: "Source Sans 3" },
  { id: "dmsans-dmserif", heading: "DM Sans", body: "DM Serif Display" },
];

export const SECTION_THEMES = [
  { id: "dark-hero", label: "Hero ciemny, reszta jasna", bars: ["#1F2937", "#FFFFFF", "#F9FAFB", "#FFFFFF", "#F9FAFB"] },
  { id: "colorful-hero", label: "Hero kolorowy, reszta biała", bars: ["#4F46E5", "#FFFFFF", "#FFFFFF", "#F9FAFB", "#FFFFFF"] },
  { id: "alternating", label: "Naprzemiennie ciemne i jasne", bars: ["#1F2937", "#FFFFFF", "#1F2937", "#FFFFFF", "#1F2937"] },
  { id: "mixed", label: "Mix kolorowych i białych", bars: ["#4F46E5", "#FFFFFF", "#059669", "#FFFFFF", "#1F2937"] },
];
