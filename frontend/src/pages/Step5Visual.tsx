import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore, type VisualConceptSection } from "@/store/labStore";
import { getPreviewUrl, exportHtml } from "@/api/client";

const CAT_LABELS: Record<string, string> = {
  NA: "Nawigacja", HE: "Hero", FI: "O firmie", OF: "Oferta", CE: "Cennik",
  ZE: "Zespół", OP: "Opinie", FA: "FAQ", CT: "CTA", KO: "Kontakt",
  FO: "Stopka", GA: "Galeria", RE: "Realizacje", PR: "Proces", PB: "Problem",
  RO: "Rozwiązanie", KR: "Korzyści", CF: "Cechy", OB: "Obiekcje",
  LO: "Loga klientów", ST: "Statystyki",
};

const BG_TYPES = ["white", "light_gray", "dark", "brand_color", "brand_gradient", "dark_photo_overlay"];

/** Get display bg color */
function getBgColor(sec: VisualConceptSection, primary: string, secondary: string): string {
  switch (sec.bg_type) {
    case "white": return "#ffffff";
    case "light_gray": return "#f3f4f6";
    case "dark": return "#1a1a2e";
    case "brand_color": return primary;
    case "brand_gradient": return primary;
    case "dark_photo_overlay": return "#1a1a2e";
    default: return sec.bg_value || "#ffffff";
  }
}

function isDark(hex: string): boolean {
  const c = hex.replace("#", "");
  const r = parseInt(c.substr(0, 2), 16);
  const g = parseInt(c.substr(2, 2), 16);
  const b = parseInt(c.substr(4, 2), 16);
  return (r * 299 + g * 587 + b * 114) / 1000 < 128;
}

/** Get a text snippet from section's slots_json */
function getSectionText(sections: Array<{ block_code: string; slots_json: Record<string, unknown> | null }>, blockCode: string): { heading: string; sub: string } {
  const sec = sections.find((s) => s.block_code === blockCode);
  if (!sec?.slots_json) return { heading: "", sub: "" };
  const slots = sec.slots_json;
  // Find heading-like fields
  const headingKeys = ["heading", "title", "headline", "cta_text", "logo_text"];
  const subKeys = ["subheading", "subtitle", "description", "text", "paragraph"];
  let heading = "";
  let sub = "";
  for (const [k, v] of Object.entries(slots)) {
    if (typeof v !== "string") continue;
    if (!heading && headingKeys.some((hk) => k.toLowerCase().includes(hk))) heading = v;
    if (!sub && subKeys.some((sk) => k.toLowerCase().includes(sk))) sub = v;
  }
  // Fallback: first string field
  if (!heading) {
    const first = Object.values(slots).find((v) => typeof v === "string" && v.length > 3 && !v.startsWith("/") && v !== "#") as string | undefined;
    if (first) heading = first;
  }
  return { heading: heading.slice(0, 80), sub: sub.slice(0, 120) };
}

export default function Step5Visual() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { visualConcept, sections, style, projectName, generateVisualConcept, saveVisualConcept, isGenerating, error, setError } = useLabStore();

  const [showPreview, setShowPreview] = useState(false);
  const [viewport, setViewport] = useState<"desktop" | "tablet" | "mobile">("desktop");
  const [iframeKey, setIframeKey] = useState(0);
  const startedRef = useRef(false);

  const previewUrl = projectId ? getPreviewUrl(projectId) : "";
  const viewportWidths = { desktop: "100%", tablet: "768px", mobile: "375px" };

  useEffect(() => {
    if (!visualConcept && !isGenerating && !startedRef.current) {
      startedRef.current = true;
      setError(null);
      generateVisualConcept();
    }
  }, [visualConcept, isGenerating]);

  const handleSectionChange = (idx: number, field: string, value: string) => {
    if (!visualConcept) return;
    const updated = { ...visualConcept };
    updated.sections = [...updated.sections];
    updated.sections[idx] = { ...updated.sections[idx], [field]: value };
    saveVisualConcept(updated);
  };

  // Loading / error / empty states
  if (!visualConcept) {
    return (
      <div className="max-w-2xl mx-auto p-6 text-center py-16 space-y-4">
        {isGenerating && (
          <>
            <div className="inline-flex items-center gap-3 bg-emerald-50 text-emerald-700 px-6 py-4 rounded-xl">
              <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
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
            <div>
              <button onClick={() => { setError(null); generateVisualConcept(); }} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">
                Spróbuj ponownie
              </button>
            </div>
          </>
        )}
        {!isGenerating && !error && (
          <>
            <p className="text-gray-400 text-sm">Brak kreacji wizualnej.</p>
            <button onClick={() => generateVisualConcept()} className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700">
              Generuj kreację wizualną
            </button>
          </>
        )}
        <div className="pt-4">
          <button onClick={() => navigate(`/lab/${projectId}/step/4`)} className="text-xs text-gray-500 hover:text-gray-700">← Wstecz</button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)]">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-semibold text-gray-700">Kreacja wizualna</h2>
          <span className="text-xs text-gray-400">{projectName}</span>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => { setError(null); generateVisualConcept(); }} disabled={isGenerating} className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 disabled:opacity-50">
            {isGenerating ? "Generowanie..." : "Regeneruj"}
          </button>
          <button onClick={() => { setShowPreview(true); setIframeKey((k) => k + 1); }} className="text-xs px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 font-medium">
            Podgląd
          </button>
          <button onClick={() => projectId && exportHtml(projectId)} className="text-xs px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-semibold">
            Pobierz HTML
          </button>
        </div>
      </div>

      {showPreview ? (
        <>
          <div className="bg-white border-b border-gray-100 px-6 py-2 flex items-center gap-3">
            <div className="flex border border-gray-200 rounded-lg overflow-hidden">
              {(["desktop", "tablet", "mobile"] as const).map((v) => (
                <button key={v} onClick={() => setViewport(v)} className={`px-3 py-1.5 text-xs ${viewport === v ? "bg-emerald-50 text-emerald-700 font-medium" : "text-gray-500 hover:bg-gray-50"}`}>
                  {v === "desktop" ? "Desktop" : v === "tablet" ? "Tablet" : "Mobile"}
                </button>
              ))}
            </div>
            <button onClick={() => setShowPreview(false)} className="text-xs text-gray-500 hover:text-gray-700 ml-auto">Zamknij podgląd</button>
          </div>
          <div className="flex-1 bg-gray-100 flex justify-center overflow-auto p-4">
            <div style={{ width: viewportWidths[viewport], maxWidth: "100%" }} className="bg-white shadow-lg rounded-lg overflow-hidden transition-all duration-300">
              <iframe key={iframeKey} src={previewUrl} className="w-full h-full border-0" style={{ minHeight: "80vh" }} title="Podglad strony" />
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Page layout view — kolorowe klocki 1:1 */}
          <div className="flex-1 overflow-y-auto bg-gray-100">
            <div className="max-w-2xl mx-auto py-6">
              {/* Global info */}
              <div className="bg-white rounded-xl border border-gray-200 p-3 mb-4 flex items-center gap-4 mx-4">
                <span className="text-xs text-gray-500">Styl: <strong>{visualConcept.style}</strong></span>
                <span className="text-xs text-gray-500">Tło: <strong>{visualConcept.bg_approach}</strong></span>
                <div className="flex items-center gap-1 ml-auto">
                  <div className="w-5 h-5 rounded border border-gray-200" style={{ backgroundColor: style.primary_color }} />
                  <div className="w-5 h-5 rounded border border-gray-200" style={{ backgroundColor: style.secondary_color }} />
                </div>
              </div>

              {/* Stacked blocks */}
              <div className="mx-4 rounded-xl overflow-hidden shadow-lg border border-gray-200">
                {visualConcept.sections.map((sec, idx) => {
                  const bg = getBgColor(sec, style.primary_color, style.secondary_color);
                  const dark = isDark(bg);
                  const catCode = sec.block_code.replace(/\d+/g, "");
                  const catLabel = CAT_LABELS[catCode] || catCode;
                  const { heading, sub } = getSectionText(sections, sec.block_code);

                  // Height based on section type
                  const isNav = catCode === "NA";
                  const isFooter = catCode === "FO";
                  const isHero = catCode === "HE";
                  const isCta = catCode === "CT";
                  const minH = isNav ? "h-12" : isFooter ? "h-16" : isHero ? "h-44" : isCta ? "h-28" : "h-32";

                  const gradientStyle = sec.bg_type === "brand_gradient"
                    ? { background: `linear-gradient(135deg, ${style.primary_color}, ${style.secondary_color})` }
                    : { backgroundColor: bg };

                  return (
                    <div
                      key={idx}
                      className={`${minH} relative flex flex-col justify-center px-8 transition-all group cursor-pointer`}
                      style={gradientStyle}
                      onClick={() => {
                        // Cycle bg type on click
                        const currentIdx = BG_TYPES.indexOf(sec.bg_type);
                        const nextBg = BG_TYPES[(currentIdx + 1) % BG_TYPES.length];
                        handleSectionChange(idx, "bg_type", nextBg);
                      }}
                    >
                      {/* Section label */}
                      <div className={`absolute top-2 left-3 flex items-center gap-2 ${dark ? "text-white/60" : "text-black/30"}`}>
                        <span className="text-[10px] font-mono font-bold">{sec.block_code}</span>
                        <span className="text-[10px]">{catLabel}</span>
                        <span className="text-[9px] opacity-0 group-hover:opacity-100 transition-opacity">
                          tło: {sec.bg_type} (kliknij aby zmienić)
                        </span>
                      </div>

                      {/* Content text */}
                      <div className={`${isNav ? "flex items-center justify-between" : ""}`}>
                        {heading && (
                          <h3 className={`${isHero ? "text-xl" : isNav ? "text-sm" : "text-base"} font-bold leading-tight ${dark ? "text-white" : "text-gray-800"}`}>
                            {heading}
                          </h3>
                        )}
                        {sub && !isNav && (
                          <p className={`text-sm mt-1 ${dark ? "text-white/70" : "text-gray-500"} line-clamp-2`}>
                            {sub}
                          </p>
                        )}
                        {!heading && !sub && (
                          <span className={`text-sm italic ${dark ? "text-white/40" : "text-gray-300"}`}>
                            {catLabel}
                          </span>
                        )}
                      </div>

                      {/* Media indicator */}
                      {sec.media_type && sec.media_type !== "none" && (
                        <div className={`absolute top-2 right-3 text-[9px] px-1.5 py-0.5 rounded ${dark ? "bg-white/10 text-white/50" : "bg-black/5 text-black/30"}`}>
                          {sec.media_type.replace(/_/g, " ")}
                        </div>
                      )}

                      {/* Separator */}
                      {sec.separator_after && (
                        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-gray-300 to-transparent" />
                      )}
                    </div>
                  );
                })}
              </div>

              <p className="text-center text-[10px] text-gray-400 mt-3">
                Kliknij na sekcję aby zmienić kolor tła
              </p>
            </div>
          </div>
        </>
      )}

      {/* Bottom nav */}
      <div className="bg-white border-t border-gray-200 px-6 py-3 flex justify-between">
        <button onClick={() => navigate(`/lab/${projectId}/step/4`)} className="text-xs text-gray-500 hover:text-gray-700">← Wstecz</button>
      </div>
    </div>
  );
}
