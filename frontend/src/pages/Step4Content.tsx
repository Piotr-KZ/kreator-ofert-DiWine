import { useState, useRef, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";

const CAT_LABELS: Record<string, string> = {
  NA: "Nawigacja", HE: "Hero", FI: "O firmie", OF: "Oferta", CE: "Cennik",
  ZE: "Zespół", OP: "Opinie", FA: "FAQ", CT: "CTA", KO: "Kontakt",
  FO: "Stopka", GA: "Galeria", RE: "Realizacje", PR: "Proces", PB: "Problem",
  RO: "Rozwiązanie", KR: "Korzyści", CF: "Cechy", OB: "Obiekcje",
  LO: "Loga klientów", ST: "Statystyki",
};

// ─── Slot type detection ───

type SlotRole = "title" | "subtitle" | "description" | "button" | "link" | "image" | "list" | "stats" | "text" | "other";

function detectSlotRole(key: string, value: unknown): SlotRole {
  const k = key.toLowerCase();
  if (k.includes("title") || k.includes("heading") || k === "name") return "title";
  if (k.includes("subtitle") || k.includes("subheading") || k.includes("tagline")) return "subtitle";
  if (k.includes("description") || k.includes("text") || k.includes("content") || k.includes("paragraph") || k.includes("body")) return "description";
  if (k.includes("cta") || k.includes("button") || k.includes("btn")) return "button";
  if (k.includes("url") || k.includes("link") || k.includes("href")) return "link";
  if (k.includes("image") || k.includes("logo") || k.includes("photo") || k.includes("avatar") || k.includes("icon")) return "image";
  if (Array.isArray(value)) {
    if (value.length > 0 && typeof value[0] === "object" && value[0] !== null) {
      const keys = Object.keys(value[0]);
      if (keys.some(k => k.includes("value") || k.includes("number") || k.includes("count"))) return "stats";
      return "list";
    }
    return "list";
  }
  if (typeof value === "string") {
    if (value === "#" || value.startsWith("http") || value.startsWith("/")) return "link";
  }
  return "other";
}

function getCatCode(blockCode: string): string {
  return blockCode.replace(/\d+/g, "");
}

// ─── Section background by category ───

function getSectionStyle(catCode: string): string {
  switch (catCode) {
    case "NA": return "bg-white py-3";
    case "FO": return "bg-gray-800 text-white py-6";
    case "HE": return "bg-gradient-to-b from-gray-50 to-white py-12";
    case "CT": return "bg-emerald-50 py-10";
    default: return "bg-white py-8";
  }
}

// ─── AI Selection Toolbar ───

function AISelectionToolbar({ selectedText, onSubmit, onClose }: {
  selectedText: string;
  onSubmit: (instruction: string) => void;
  onClose: () => void;
}) {
  const [instruction, setInstruction] = useState("");

  return (
    <div className="fixed z-50 bg-white border border-gray-300 rounded-xl shadow-xl p-3 flex items-center gap-2 max-w-md"
      style={{ bottom: "5rem", left: "50%", transform: "translateX(-50%)" }}
    >
      <div className="text-xs text-gray-400 max-w-[120px] truncate" title={selectedText}>
        "{selectedText.slice(0, 40)}..."
      </div>
      <input
        type="text"
        value={instruction}
        onChange={(e) => setInstruction(e.target.value)}
        placeholder="Polecenie AI..."
        className="flex-1 px-2 py-1.5 border border-gray-200 rounded-lg text-xs min-w-[160px]"
        autoFocus
        onKeyDown={(e) => {
          if (e.key === "Enter" && instruction.trim()) onSubmit(instruction);
          if (e.key === "Escape") onClose();
        }}
      />
      <button
        onClick={() => instruction.trim() && onSubmit(instruction)}
        disabled={!instruction.trim()}
        className="px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 disabled:opacity-50"
      >
        Zmień
      </button>
      <button onClick={onClose} className="text-gray-300 hover:text-gray-500 text-xs">✕</button>
    </div>
  );
}

// ─── Editable Text ───

function EditableText({ value, onChange, className }: {
  value: string;
  onChange: (newVal: string) => void;
  className?: string;
}) {
  const [localVal, setLocalVal] = useState(value);
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { setLocalVal(value); }, [value]);
  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = "auto";
      ref.current.style.height = ref.current.scrollHeight + "px";
    }
  }, [localVal]);

  return (
    <textarea
      ref={ref}
      value={localVal}
      onChange={(e) => setLocalVal(e.target.value)}
      onBlur={() => { if (localVal !== value) onChange(localVal); }}
      rows={1}
      className={`${className || ""} w-full resize-none border-0 bg-transparent outline-none focus:bg-yellow-50 focus:ring-1 focus:ring-yellow-300 rounded px-1 -mx-1 cursor-text overflow-hidden`}
    />
  );
}

// ─── Semantic Section Renderer ───

function SectionContent({ section, onSlotUpdate }: {
  section: { block_code: string; slots_json: Record<string, unknown> | null };
  onSlotUpdate: (key: string, newValue: unknown) => void;
}) {
  const slots = section.slots_json as Record<string, unknown> | null;
  if (!slots) return <p className="text-sm text-gray-300 italic py-2">Brak treści — wygeneruj</p>;

  const catCode = getCatCode(section.block_code);
  const entries = Object.entries(slots);

  // Classify all slots
  const classified = entries.map(([key, value]) => ({
    key,
    value,
    role: detectSlotRole(key, value),
  }));

  const titles = classified.filter(s => s.role === "title");
  const subtitles = classified.filter(s => s.role === "subtitle");
  const descriptions = classified.filter(s => s.role === "description");
  const buttons = classified.filter(s => s.role === "button");
  const lists = classified.filter(s => s.role === "list" || s.role === "stats");
  const others = classified.filter(s => s.role === "other");
  // Skip links and images silently (they are placeholders)

  const isCentered = ["HE", "CT", "ST"].includes(catCode);

  return (
    <div className={`space-y-4 ${isCentered ? "text-center" : ""}`}>
      {/* Titles */}
      {titles.map(({ key, value }) => (
        <EditableText
          key={key}
          value={String(value)}
          onChange={(v) => onSlotUpdate(key, v)}
          className={`text-2xl font-bold ${catCode === "FO" ? "text-white" : "text-gray-900"}`}
        />
      ))}

      {/* Subtitles */}
      {subtitles.map(({ key, value }) => (
        <EditableText
          key={key}
          value={String(value)}
          onChange={(v) => onSlotUpdate(key, v)}
          className={`text-lg ${catCode === "FO" ? "text-gray-300" : "text-gray-500"}`}
        />
      ))}

      {/* Descriptions */}
      {descriptions.map(({ key, value }) => (
        <EditableText
          key={key}
          value={String(value)}
          onChange={(v) => onSlotUpdate(key, v)}
          className={`text-base leading-relaxed ${catCode === "FO" ? "text-gray-400" : "text-gray-600"}`}
        />
      ))}

      {/* Buttons — render as button-style elements */}
      {buttons.length > 0 && (
        <div className={`flex gap-3 ${isCentered ? "justify-center" : ""} pt-2`}>
          {buttons.map(({ key, value }, i) => (
            <div key={key} className={`inline-block px-5 py-2.5 rounded-lg text-sm font-semibold ${
              i === 0 ? "bg-emerald-600 text-white" : "border border-gray-300 text-gray-700"
            }`}>
              <EditableText
                value={String(value)}
                onChange={(v) => onSlotUpdate(key, v)}
                className={`text-sm font-semibold ${i === 0 ? "text-white" : "text-gray-700"} text-center`}
              />
            </div>
          ))}
        </div>
      )}

      {/* Lists / Stats */}
      {lists.map(({ key, value, role }) => {
        if (!Array.isArray(value) || value.length === 0) return null;

        // Stats grid — numbers prominent
        if (role === "stats") {
          return (
            <div key={key} className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
              {value.map((item, i) => {
                if (typeof item !== "object" || item === null) return null;
                const obj = item as Record<string, unknown>;
                const numKey = Object.keys(obj).find(k => k.includes("value") || k.includes("number") || k.includes("count")) || Object.keys(obj)[0];
                const labelKey = Object.keys(obj).find(k => k.includes("label") || k.includes("title") || k.includes("name")) || Object.keys(obj)[1];
                return (
                  <div key={i} className="text-center p-3 bg-gray-50 rounded-lg">
                    <EditableText
                      value={String(obj[numKey] ?? "")}
                      onChange={(v) => {
                        const newArr = [...value]; newArr[i] = { ...newArr[i], [numKey]: v }; onSlotUpdate(key, newArr);
                      }}
                      className="text-2xl font-bold text-emerald-600 text-center"
                    />
                    {labelKey && (
                      <EditableText
                        value={String(obj[labelKey] ?? "")}
                        onChange={(v) => {
                          const newArr = [...value]; newArr[i] = { ...newArr[i], [labelKey]: v }; onSlotUpdate(key, newArr);
                        }}
                        className="text-xs text-gray-500 text-center mt-1"
                      />
                    )}
                  </div>
                );
              })}
            </div>
          );
        }

        // Object list — cards
        if (typeof value[0] === "object" && value[0] !== null) {
          return (
            <div key={key} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
              {value.map((item, i) => {
                if (typeof item !== "object" || item === null) return null;
                const obj = item as Record<string, unknown>;
                const itemEntries = Object.entries(obj);
                // Find title-like and description-like fields
                const titleEntry = itemEntries.find(([k]) => k.includes("title") || k.includes("name") || k.includes("heading"));
                const descEntry = itemEntries.find(([k]) => k.includes("description") || k.includes("text") || k.includes("content"));
                const otherEntries = itemEntries.filter(([k, v]) => {
                  if (titleEntry && k === titleEntry[0]) return false;
                  if (descEntry && k === descEntry[0]) return false;
                  if (typeof v === "string" && (v === "#" || v.startsWith("http") || v.startsWith("/"))) return false;
                  if (k.includes("icon") || k.includes("image") || k.includes("url") || k.includes("link")) return false;
                  return true;
                });

                return (
                  <div key={i} className="bg-gray-50 rounded-lg p-4 space-y-2">
                    {titleEntry && (
                      <EditableText
                        value={String(titleEntry[1])}
                        onChange={(v) => {
                          const newArr = [...value]; newArr[i] = { ...newArr[i], [titleEntry[0]]: v }; onSlotUpdate(key, newArr);
                        }}
                        className="text-sm font-semibold text-gray-800"
                      />
                    )}
                    {descEntry && (
                      <EditableText
                        value={String(descEntry[1])}
                        onChange={(v) => {
                          const newArr = [...value]; newArr[i] = { ...newArr[i], [descEntry[0]]: v }; onSlotUpdate(key, newArr);
                        }}
                        className="text-sm text-gray-500 leading-relaxed"
                      />
                    )}
                    {otherEntries.map(([k, v]) => (
                      <EditableText
                        key={k}
                        value={String(v)}
                        onChange={(newV) => {
                          const newArr = [...value]; newArr[i] = { ...newArr[i], [k]: newV }; onSlotUpdate(key, newArr);
                        }}
                        className="text-xs text-gray-400"
                      />
                    ))}
                  </div>
                );
              })}
            </div>
          );
        }

        // String list
        return (
          <ul key={key} className="list-disc list-inside text-sm text-gray-600 space-y-1 pt-1">
            {value.map((item, i) => (
              <li key={i}>
                {typeof item === "string" ? (
                  <EditableText
                    value={item}
                    onChange={(v) => { const a = [...value]; a[i] = v; onSlotUpdate(key, a); }}
                    className="text-sm text-gray-600 inline"
                  />
                ) : String(item)}
              </li>
            ))}
          </ul>
        );
      })}

      {/* Other string values — render as body text */}
      {others.map(({ key, value }) => (
        typeof value === "string" ? (
          <EditableText
            key={key}
            value={value}
            onChange={(v) => onSlotUpdate(key, v)}
            className={`text-sm ${catCode === "FO" ? "text-gray-400" : "text-gray-600"}`}
          />
        ) : typeof value === "number" || typeof value === "boolean" ? (
          <span key={key} className="text-sm font-medium text-gray-700 block">{String(value)}</span>
        ) : null
      ))}
    </div>
  );
}

// ─── Main Component ───

export default function Step4Content() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { sections, updateSection, regenerateSection, generateContent, isGenerating, error, setError } = useLabStore();

  const [selectedText, setSelectedText] = useState<string | null>(null);
  const [activeSectionId, setActiveSectionId] = useState<string | null>(null);

  // Listen for text selection
  useEffect(() => {
    const handleMouseUp = () => {
      const sel = window.getSelection();
      const text = sel?.toString().trim();
      if (text && text.length > 3) {
        const node = sel?.anchorNode?.parentElement;
        const sectionEl = node?.closest("[data-section-id]");
        if (sectionEl) {
          setSelectedText(text);
          setActiveSectionId(sectionEl.getAttribute("data-section-id"));
        }
      }
    };
    document.addEventListener("mouseup", handleMouseUp);
    return () => document.removeEventListener("mouseup", handleMouseUp);
  }, []);

  const handleAIChange = async (instruction: string) => {
    if (!activeSectionId || !selectedText) return;
    const fullInstruction = `Zmień fragment: "${selectedText}" — ${instruction}`;
    await regenerateSection(activeSectionId, fullInstruction);
    setSelectedText(null);
    setActiveSectionId(null);
  };

  const handleSlotUpdate = (sectionId: string, key: string, newValue: unknown) => {
    const section = sections.find(s => s.id === sectionId);
    if (!section || !section.slots_json) return;
    const updatedSlots = { ...(section.slots_json as Record<string, unknown>), [key]: newValue };
    updateSection(sectionId, { slots_json: updatedSlots });
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-xl font-bold text-gray-800">Treści</h1>
        <button
          onClick={() => generateContent()}
          disabled={isGenerating}
          className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 disabled:opacity-50"
        >
          {isGenerating ? "Generowanie..." : "Regeneruj wszystko"}
        </button>
      </div>

      {sections.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p>Brak sekcji. Wróć do kroku 3 aby wygenerować strukturę.</p>
        </div>
      )}

      {isGenerating && (
        <div className="text-center py-4">
          <div className="inline-flex items-center gap-3 bg-emerald-50 text-emerald-700 px-5 py-3 rounded-xl">
            <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span className="text-sm font-medium">AI generuje treści...</span>
          </div>
        </div>
      )}

      {!isGenerating && error && (
        <div className="text-center py-4 space-y-3">
          <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-5 py-3 rounded-xl border border-red-200">
            <span>✗</span><span className="text-sm">{error}</span>
          </div>
          <div>
            <button onClick={() => { setError(null); generateContent(); }} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">
              Spróbuj ponownie
            </button>
          </div>
        </div>
      )}

      {!sections.some((s) => s.slots_json) && sections.length > 0 && !isGenerating && (
        <div className="text-center py-8">
          <p className="text-gray-400 text-sm mb-4">Brak treści. Wygeneruj je.</p>
          <button onClick={() => generateContent()} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700">
            Generuj treści
          </button>
        </div>
      )}

      {/* Full page view — sections with natural sizes */}
      <div className="rounded-xl overflow-hidden border border-gray-200">
        {sections.map((section) => {
          const catCode = getCatCode(section.block_code);
          const catLabel = CAT_LABELS[catCode] || catCode;
          const sectionStyle = getSectionStyle(catCode);

          return (
            <div
              key={section.id}
              data-section-id={section.id}
              className={`${sectionStyle} px-8 border-b border-gray-100 last:border-b-0 relative group`}
            >
              {/* Subtle section label — top-right */}
              <div className="absolute top-2 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-[10px] font-mono text-gray-300">
                  {section.block_code} · {catLabel}
                </span>
              </div>

              <SectionContent
                section={section}
                onSlotUpdate={(key, newValue) => handleSlotUpdate(section.id, key, newValue)}
              />
            </div>
          );
        })}
      </div>

      {/* AI Selection Toolbar */}
      {selectedText && (
        <AISelectionToolbar
          selectedText={selectedText}
          onSubmit={handleAIChange}
          onClose={() => { setSelectedText(null); setActiveSectionId(null); }}
        />
      )}

      <div className="flex justify-between pt-6">
        <button onClick={() => navigate(`/lab/${projectId}/step/3`)} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">← Wstecz</button>
        <button onClick={() => navigate(`/lab/${projectId}/step/5`)} disabled={sections.length === 0} className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors">
          Dalej → Kreacja wizualna
        </button>
      </div>
    </div>
  );
}
