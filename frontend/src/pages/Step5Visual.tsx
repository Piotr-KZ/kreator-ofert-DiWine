/**
 * Step 5 — Kreacja wizualna
 *
 * Components:
 *  1. VisualToolbar     — sticky top bar: project name, actions (regenerate, preview, export)
 *  2. BgTypePicker      — visual bg_type button grid (6 options)
 *  3. MediaTypePicker   — media_type button grid (5 options)
 *  4. SectionDetailPanel — right panel for selected section editing
 *  5. SectionBlock      — single colored section block in the canvas
 *  6. PreviewMode       — full iframe preview with viewport switcher
 */

import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore, type VisualConceptSection } from "@/store/labStore";
import { getPreviewUrl, exportHtml } from "@/api/client";

// ── Constants ─────────────────────────────────────────────────

const CAT_LABELS: Record<string, string> = {
  NA: "Nawigacja", HE: "Hero", FI: "O firmie", OF: "Oferta", CE: "Cennik",
  ZE: "Zespół", OP: "Opinie", FA: "FAQ", CT: "CTA", KO: "Kontakt",
  FO: "Stopka", GA: "Galeria", RE: "Realizacje", PR: "Proces", PB: "Problem",
  RO: "Rozwiązanie", KR: "Korzyści", CF: "Cechy", OB: "Obiekcje",
  LO: "Loga klientów", ST: "Statystyki",
};

const BG_TYPES = [
  { value: "white",             label: "Białe",        bg: "#FFFFFF" },
  { value: "light_gray",        label: "Jasne",        bg: "#F1F5F9" },
  { value: "dark",              label: "Ciemne",       bg: "#1a1a2e" },
  { value: "brand_color",       label: "Brandowe",     bg: null },      // uses primary_color
  { value: "brand_gradient",    label: "Gradient",     bg: null },      // gradient
  { value: "dark_photo_overlay",label: "Foto",         bg: "#111827" },
];

const MEDIA_TYPES = [
  { value: "none",         label: "Brak",     icon: "○" },
  { value: "image",        label: "Zdjęcie",  icon: "🖼" },
  { value: "icon",         label: "Ikona",    icon: "◈" },
  { value: "illustration", label: "Ilustr.",  icon: "✦" },
  { value: "pattern",      label: "Wzór",     icon: "▦" },
];

type Viewport = "desktop" | "tablet" | "mobile";

// ── Helpers ───────────────────────────────────────────────────

function getCatCode(code: string) { return code.replace(/\d+/g, ""); }

function getBgCSS(sec: VisualConceptSection, primary: string, secondary: string): string {
  switch (sec.bg_type) {
    case "white": return "#ffffff";
    case "light_gray": return "#f3f4f6";
    case "dark": return "#1a1a2e";
    case "brand_color": return primary;
    case "brand_gradient": return `linear-gradient(135deg, ${primary}, ${secondary})`;
    case "dark_photo_overlay": return "#111827";
    default: return sec.bg_value || "#ffffff";
  }
}

function isDark(hex: string): boolean {
  const c = hex.replace("#", "");
  if (c.length < 6) return false;
  const r = parseInt(c.substr(0, 2), 16);
  const g = parseInt(c.substr(2, 2), 16);
  const b = parseInt(c.substr(4, 2), 16);
  return (r * 299 + g * 587 + b * 114) / 1000 < 128;
}

function getTextFromSections(
  sections: Array<{ block_code: string; slots_json: Record<string, unknown> | null }>,
  blockCode: string
): { heading: string; sub: string } {
  const sec = sections.find(s => s.block_code === blockCode);
  if (!sec?.slots_json) return { heading: "", sub: "" };
  const slots = sec.slots_json;
  const headingKeys = ["heading", "title", "headline", "cta_text", "logo_text"];
  const subKeys = ["subheading", "subtitle", "description", "text", "paragraph"];
  let heading = "";
  let sub = "";
  for (const [k, v] of Object.entries(slots)) {
    if (typeof v !== "string") continue;
    if (!heading && headingKeys.some(hk => k.toLowerCase().includes(hk))) heading = v;
    if (!sub && subKeys.some(sk => k.toLowerCase().includes(sk))) sub = v;
  }
  if (!heading) {
    const first = Object.values(slots).find(
      v => typeof v === "string" && v.length > 3 && !v.startsWith("/") && v !== "#"
    ) as string | undefined;
    if (first) heading = first;
  }
  return { heading: heading.slice(0, 80), sub: sub.slice(0, 120) };
}

// ══════════════════════════════════════════════════════════════
// 1. VisualToolbar
// ══════════════════════════════════════════════════════════════

interface VisualToolbarProps {
  projectName: string;
  isGenerating: boolean;
  showPreview: boolean;
  onRegenerate: () => void;
  onTogglePreview: () => void;
  onExport: () => void;
}

function VisualToolbar({ projectName, isGenerating, showPreview, onRegenerate, onTogglePreview, onExport }: VisualToolbarProps) {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between flex-shrink-0">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-bold text-slate-800">Kreacja wizualna</h2>
        {projectName && <span className="text-xs text-gray-400">{projectName}</span>}
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={onRegenerate}
          disabled={isGenerating}
          className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 disabled:opacity-50 transition-colors"
        >
          {isGenerating ? "Generowanie..." : "Regeneruj"}
        </button>
        <button
          onClick={onTogglePreview}
          className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors ${
            showPreview
              ? "bg-slate-800 text-white"
              : "bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
          }`}
        >
          {showPreview ? "← Edytuj" : "Podgląd"}
        </button>
        <button
          onClick={onExport}
          className="text-xs px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-semibold transition-colors"
        >
          Pobierz HTML
        </button>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 2. BgTypePicker
// ══════════════════════════════════════════════════════════════

interface BgTypePickerProps {
  value: string;
  primary: string;
  secondary: string;
  onChange: (bgType: string) => void;
}

function BgTypePicker({ value, primary, secondary, onChange }: BgTypePickerProps) {
  return (
    <div className="grid grid-cols-3 gap-1.5">
      {BG_TYPES.map(bt => {
        const bg = bt.bg ?? (bt.value === "brand_gradient"
          ? `linear-gradient(135deg, ${primary}, ${secondary})`
          : primary);
        const active = value === bt.value;
        return (
          <button
            key={bt.value}
            onClick={() => onChange(bt.value)}
            title={bt.label}
            className={`h-10 rounded-lg text-[10px] font-semibold border-2 transition-all ${
              active ? "border-indigo-600 shadow-sm" : "border-transparent hover:border-gray-300"
            }`}
            style={{ background: bg }}
          >
            <span
              className="block text-center"
              style={{
                color: isDark(typeof bg === "string" && bg.startsWith("#") ? bg : "#1a1a2e") ? "#fff" : "#1a1a2e",
                textShadow: "0 1px 2px rgba(0,0,0,.2)",
              }}
            >
              {bt.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 3. MediaTypePicker
// ══════════════════════════════════════════════════════════════

interface MediaTypePickerProps {
  value: string;
  onChange: (mediaType: string) => void;
}

function MediaTypePicker({ value, onChange }: MediaTypePickerProps) {
  return (
    <div className="flex gap-1.5 flex-wrap">
      {MEDIA_TYPES.map(mt => (
        <button
          key={mt.value}
          onClick={() => onChange(mt.value)}
          className={`h-8 px-3 rounded-lg text-xs font-medium border transition-all flex items-center gap-1.5 ${
            value === mt.value
              ? "border-indigo-600 bg-indigo-50 text-indigo-700"
              : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
          }`}
        >
          <span>{mt.icon}</span>
          <span>{mt.label}</span>
        </button>
      ))}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 4. SectionDetailPanel
// ══════════════════════════════════════════════════════════════

interface SectionDetailPanelProps {
  sec: VisualConceptSection;
  primary: string;
  secondary: string;
  onClose: () => void;
  onChange: (field: string, value: string | boolean) => void;
}

function SectionDetailPanel({ sec, primary, secondary, onClose, onChange }: SectionDetailPanelProps) {
  const catCode = getCatCode(sec.block_code);
  const catLabel = CAT_LABELS[catCode] ?? catCode;

  return (
    <aside className="w-72 flex-shrink-0 bg-white border-l border-gray-200 flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div>
          <div className="text-xs font-bold text-slate-800">{sec.block_code}</div>
          <div className="text-[10px] text-gray-400">{catLabel}</div>
        </div>
        <button onClick={onClose} className="text-gray-300 hover:text-gray-600 text-sm w-7 h-7 grid place-items-center rounded-lg hover:bg-gray-50">
          ✕
        </button>
      </div>

      <div className="p-4 space-y-5">
        {/* Bg type */}
        <div>
          <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-2">
            Kolor tła
          </label>
          <BgTypePicker value={sec.bg_type} primary={primary} secondary={secondary} onChange={v => onChange("bg_type", v)} />
        </div>

        {/* Custom bg color — show only when bg_type is "white" or "light_gray" so user can override */}
        {(sec.bg_type === "white" || sec.bg_type === "light_gray") && (
          <div>
            <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-1.5">
              Własny kolor tła
            </label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={sec.bg_value || (sec.bg_type === "white" ? "#ffffff" : "#f3f4f6")}
                onChange={e => { onChange("bg_type", "custom"); onChange("bg_value", e.target.value); }}
                className="w-9 h-9 cursor-pointer border border-gray-200 rounded-lg p-0.5 bg-white"
              />
              <span className="text-xs font-mono text-gray-500">{sec.bg_value || "domyślny"}</span>
            </div>
          </div>
        )}

        {/* Media type */}
        <div>
          <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-2">
            Media / ozdoba
          </label>
          <MediaTypePicker value={sec.media_type || "none"} onChange={v => onChange("media_type", v)} />
        </div>

        {/* Photo query */}
        {(sec.media_type === "image" || sec.media_type === "illustration") && (
          <div>
            <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-1.5">
              Hasło do wyszukiwania zdjęcia
            </label>
            <input
              type="text"
              value={sec.photo_query ?? ""}
              onChange={e => onChange("photo_query", e.target.value)}
              placeholder="np. modern office team"
              className="w-full h-8 px-2.5 text-xs border border-gray-200 rounded-lg outline-none focus:border-indigo-400 transition-colors"
            />
            <p className="text-[10px] text-gray-400 mt-1">Używane przy generowaniu HTML</p>
          </div>
        )}

        {/* Separator */}
        <div>
          <label className="flex items-center gap-2.5 cursor-pointer">
            <div
              onClick={() => onChange("separator_after", !sec.separator_after)}
              className={`w-9 h-5 rounded-full transition-colors flex-shrink-0 ${sec.separator_after ? "bg-indigo-600" : "bg-gray-200"}`}
            >
              <div className={`w-4 h-4 bg-white rounded-full shadow-sm transition-transform mt-0.5 ${sec.separator_after ? "translate-x-4" : "translate-x-0.5"}`} />
            </div>
            <span className="text-xs text-gray-700">Separator po sekcji</span>
          </label>
        </div>

        {/* Preview swatch */}
        <div>
          <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-2">Podgląd tła</label>
          <div
            className="h-12 rounded-xl border border-gray-200"
            style={{ background: getBgCSS(sec, primary, secondary) }}
          />
        </div>
      </div>
    </aside>
  );
}

// ══════════════════════════════════════════════════════════════
// 5. SectionBlock
// ══════════════════════════════════════════════════════════════

interface SectionBlockProps {
  sec: VisualConceptSection;
  idx: number;
  total: number;
  primary: string;
  secondary: string;
  isSelected: boolean;
  textContent: { heading: string; sub: string };
  onClick: () => void;
}

function SectionBlock({ sec, idx, primary, secondary, isSelected, textContent, onClick }: SectionBlockProps) {
  const catCode = getCatCode(sec.block_code);
  const catLabel = CAT_LABELS[catCode] ?? catCode;
  const isNav = catCode === "NA";
  const isFooter = catCode === "FO";
  const isHero = catCode === "HE";
  const isCta = catCode === "CT";
  const minH = isNav ? "h-12" : isFooter ? "h-16" : isHero ? "h-48" : isCta ? "h-28" : "h-32";

  const bgStyle = sec.bg_type === "brand_gradient"
    ? { background: `linear-gradient(135deg, ${primary}, ${secondary})` }
    : { background: getBgCSS(sec, primary, secondary) };

  const dark = isDark(bgStyle.background.startsWith("linear-gradient") ? primary : bgStyle.background);

  return (
    <div
      onClick={onClick}
      className={`${minH} relative flex flex-col justify-center px-8 transition-all cursor-pointer group ${
        isSelected ? "ring-2 ring-indigo-500 ring-inset" : "hover:brightness-95"
      }`}
      style={bgStyle}
      title="Kliknij aby edytować"
    >
      {/* Section label */}
      <div className={`absolute top-2 left-3 flex items-center gap-2 ${dark ? "text-white/50" : "text-black/25"}`}>
        <span className="text-[10px] font-mono font-bold">{sec.block_code}</span>
        <span className="text-[10px]">{catLabel}</span>
        {idx === 0 && <span className="text-[9px] opacity-0 group-hover:opacity-100 transition-opacity">(kliknij aby edytować)</span>}
      </div>

      {/* Selected indicator */}
      {isSelected && (
        <div className="absolute top-2 right-3 bg-indigo-600 text-white text-[9px] font-bold px-2 py-0.5 rounded">
          EDYTUJESZ
        </div>
      )}

      {/* Content preview */}
      <div className={isNav ? "flex items-center justify-between" : ""}>
        {textContent.heading && (
          <h3 className={`${isHero ? "text-xl" : isNav ? "text-sm" : "text-base"} font-bold leading-tight ${dark ? "text-white" : "text-gray-800"}`}>
            {textContent.heading}
          </h3>
        )}
        {textContent.sub && !isNav && (
          <p className={`text-sm mt-1 line-clamp-2 ${dark ? "text-white/70" : "text-gray-500"}`}>
            {textContent.sub}
          </p>
        )}
        {!textContent.heading && !textContent.sub && (
          <span className={`text-sm italic ${dark ? "text-white/30" : "text-gray-300"}`}>{catLabel}</span>
        )}
      </div>

      {/* Media badge */}
      {sec.media_type && sec.media_type !== "none" && (
        <div className={`absolute top-2 right-${isSelected ? "20" : "3"} text-[9px] px-1.5 py-0.5 rounded ${dark ? "bg-white/10 text-white/50" : "bg-black/5 text-black/30"}`}>
          {sec.media_type.replace(/_/g, " ")}
        </div>
      )}

      {/* Separator indicator */}
      {sec.separator_after && (
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-gray-300/60 to-transparent" />
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 6. PreviewMode
// ══════════════════════════════════════════════════════════════

interface PreviewModeProps {
  previewUrl: string;
  onClose: () => void;
}

function PreviewMode({ previewUrl, onClose }: PreviewModeProps) {
  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [iframeKey, setIframeKey] = useState(0);
  const viewportWidths: Record<Viewport, string> = { desktop: "100%", tablet: "768px", mobile: "375px" };

  useEffect(() => { setIframeKey(k => k + 1); }, [viewport]);

  return (
    <>
      {/* Preview toolbar */}
      <div className="bg-white border-b border-gray-100 px-6 py-2 flex items-center gap-3 flex-shrink-0">
        <div className="flex border border-gray-200 rounded-lg overflow-hidden">
          {(["desktop", "tablet", "mobile"] as const).map(v => (
            <button
              key={v}
              onClick={() => setViewport(v)}
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                viewport === v ? "bg-slate-800 text-white" : "text-gray-500 hover:bg-gray-50"
              }`}
            >
              {v === "desktop" ? "🖥 Desktop" : v === "tablet" ? "⬜ Tablet" : "📱 Mobile"}
            </button>
          ))}
        </div>
        <button
          onClick={() => setIframeKey(k => k + 1)}
          className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-500"
          title="Odśwież podgląd"
        >
          ↻ Odśwież
        </button>
        <button onClick={onClose} className="text-xs text-gray-500 hover:text-gray-700 ml-auto">
          ✕ Zamknij podgląd
        </button>
      </div>
      <div className="flex-1 bg-gray-200 flex justify-center overflow-auto p-6">
        <div
          style={{ width: viewportWidths[viewport], maxWidth: "100%" }}
          className="bg-white shadow-2xl rounded-xl overflow-hidden transition-all duration-300"
        >
          <iframe
            key={iframeKey}
            src={previewUrl}
            className="w-full border-0"
            style={{ minHeight: "80vh", height: "100%" }}
            title="Podgląd strony"
          />
        </div>
      </div>
    </>
  );
}

// ══════════════════════════════════════════════════════════════
// Main Page
// ══════════════════════════════════════════════════════════════

export default function Step5Visual() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const {
    visualConcept, sections, style, projectName,
    generateVisualConcept, saveVisualConcept,
    isGenerating, error, setError,
  } = useLabStore();

  const [showPreview, setShowPreview] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const startedRef = useRef(false);

  const previewUrl = projectId ? getPreviewUrl(projectId) : "";

  useEffect(() => {
    if (!visualConcept && !isGenerating && !startedRef.current) {
      startedRef.current = true;
      setError(null);
      generateVisualConcept();
    }
  }, [visualConcept, isGenerating, setError, generateVisualConcept]);

  const handleSectionChange = (idx: number, field: string, value: string | boolean) => {
    if (!visualConcept) return;
    const updated = { ...visualConcept, sections: [...visualConcept.sections] };
    updated.sections[idx] = { ...updated.sections[idx], [field]: value } as VisualConceptSection;
    saveVisualConcept(updated);
  };

  const handleRegenerate = () => {
    setError(null);
    setSelectedIdx(null);
    generateVisualConcept();
  };

  // ── Loading / error / empty states ────────────────────────
  if (!visualConcept) {
    return (
      <div className="max-w-2xl mx-auto p-6 text-center py-16 space-y-4">
        {isGenerating && (
          <>
            <div className="inline-flex items-center gap-3 bg-emerald-50 text-emerald-700 px-6 py-4 rounded-xl">
              <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              <span className="text-sm font-medium">AI generuje kreację wizualną...</span>
            </div>
            <p className="text-xs text-gray-400">To może potrwać kilka sekund</p>
          </>
        )}
        {!isGenerating && error && (
          <>
            <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-5 py-3 rounded-xl border border-red-200">
              <span>✗</span><span className="text-sm">{error}</span>
            </div>
            <button
              onClick={handleRegenerate}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700"
            >
              Spróbuj ponownie
            </button>
          </>
        )}
        {!isGenerating && !error && (
          <>
            <p className="text-gray-400 text-sm">Brak kreacji wizualnej.</p>
            <button onClick={handleRegenerate} className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700">
              Generuj kreację wizualną
            </button>
          </>
        )}
        <div className="pt-4">
          <button onClick={() => navigate(`/lab/${projectId}/step/4`)} className="text-xs text-gray-500 hover:text-gray-700">
            ← Wstecz
          </button>
        </div>
      </div>
    );
  }

  const selectedSec = selectedIdx !== null ? visualConcept.sections[selectedIdx] : null;

  return (
    <div className="flex flex-col h-full overflow-hidden" style={{ minHeight: "calc(100vh - 96px)" }}>

      {/* 1. VisualToolbar */}
      <VisualToolbar
        projectName={projectName}
        isGenerating={isGenerating}
        showPreview={showPreview}
        onRegenerate={handleRegenerate}
        onTogglePreview={() => { setShowPreview(p => !p); setSelectedIdx(null); }}
        onExport={() => projectId && exportHtml(projectId)}
      />

      {showPreview ? (
        /* 6. PreviewMode */
        <PreviewMode previewUrl={previewUrl} onClose={() => setShowPreview(false)} />
      ) : (
        <div className="flex flex-1 overflow-hidden">
          {/* Canvas */}
          <div className="flex-1 overflow-y-auto bg-gray-100 p-4">
            {/* Global info strip */}
            <div className="bg-white rounded-xl border border-gray-200 p-3 mb-4 flex items-center gap-4">
              <span className="text-xs text-gray-500">Styl: <strong>{visualConcept.style}</strong></span>
              <span className="text-xs text-gray-500">Tło: <strong>{visualConcept.bg_approach}</strong></span>
              <div className="flex items-center gap-1 ml-auto">
                <div className="w-5 h-5 rounded border border-gray-200" style={{ backgroundColor: style.primary_color }} title="Kolor główny" />
                <div className="w-5 h-5 rounded border border-gray-200" style={{ backgroundColor: style.secondary_color }} title="Kolor dodatkowy" />
                <span className="text-[10px] text-gray-400 ml-1 font-mono">{style.primary_color}</span>
              </div>
            </div>

            {/* Stacked section blocks */}
            <div className="rounded-2xl overflow-hidden shadow-xl border border-gray-200 max-w-3xl mx-auto">
              {visualConcept.sections.map((sec, idx) => (
                /* 5. SectionBlock */
                <SectionBlock
                  key={idx}
                  sec={sec}
                  idx={idx}
                  total={visualConcept.sections.length}
                  primary={style.primary_color}
                  secondary={style.secondary_color}
                  isSelected={selectedIdx === idx}
                  textContent={getTextFromSections(sections, sec.block_code)}
                  onClick={() => setSelectedIdx(selectedIdx === idx ? null : idx)}
                />
              ))}
            </div>

            <p className="text-center text-[10px] text-gray-400 mt-3">
              Kliknij sekcję aby edytować jej właściwości wizualne
            </p>
          </div>

          {/* 4. SectionDetailPanel */}
          {selectedSec && selectedIdx !== null && (
            <SectionDetailPanel
              sec={selectedSec}
              primary={style.primary_color}
              secondary={style.secondary_color}
              onClose={() => setSelectedIdx(null)}
              onChange={(field, value) => handleSectionChange(selectedIdx, field, value)}
            />
          )}
        </div>
      )}

      {/* Bottom nav */}
      <div className="bg-white border-t border-gray-200 px-6 py-3 flex justify-between flex-shrink-0">
        <button
          onClick={() => navigate(`/lab/${projectId}/step/4`)}
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          ← Wstecz
        </button>
        <div className="text-xs text-gray-400 flex items-center gap-2">
          <span className="w-2 h-2 bg-emerald-400 rounded-full" />
          Gotowe — pobierz HTML lub otwórz podgląd
        </div>
      </div>
    </div>
  );
}
