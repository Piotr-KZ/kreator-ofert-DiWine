import { useState, useRef, useEffect, useLayoutEffect, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore, type Section } from "@/store/labStore";

const CAT_LABELS: Record<string, string> = {
  NA: "Nawigacja", HE: "Hero", FI: "O firmie", OF: "Oferta", CE: "Cennik",
  ZE: "Zespół", OP: "Opinie", FA: "FAQ", CT: "CTA", KO: "Kontakt",
  FO: "Stopka", GA: "Galeria", RE: "Realizacje", PR: "Proces", PB: "Problem",
  RO: "Rozwiązanie", KR: "Korzyści", CF: "Cechy", OB: "Obiekcje",
  LO: "Loga klientów", ST: "Statystyki",
};

type Viewport = "desktop" | "tablet" | "mobile";
const VIEWPORT_WIDTHS: Record<Viewport, number> = { desktop: 1440, tablet: 768, mobile: 390 };

// ── Toast ─────────────────────────────────────────────────────

function Toast({ message }: { message: string }) {
  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-[9000] bg-slate-800 text-white text-xs font-medium px-4 py-2.5 rounded-xl shadow-xl pointer-events-none animate-fade-in">
      {message}
    </div>
  );
}

function useToast() {
  const [msg, setMsg] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const show = useCallback((text: string) => {
    setMsg(text);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setMsg(null), 2200);
  }, []);
  return { toast: msg, show };
}

// ── Slot type detection ────────────────────────────────────────

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
      const keys = Object.keys(value[0] as object);
      if (keys.some(k2 => k2.includes("value") || k2.includes("number") || k2.includes("count"))) return "stats";
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

function getSectionBg(catCode: string): string {
  switch (catCode) {
    case "FO": return "#1E293B";
    case "CT": return "#0F172A";
    case "HE": return "#F8FAFC";
    default: return "#FFFFFF";
  }
}

// ── Editable Text ─────────────────────────────────────────────

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
      className={`${className ?? ""} w-full resize-none border-0 bg-transparent outline-none focus:bg-yellow-50 focus:ring-1 focus:ring-yellow-300 rounded px-1 -mx-1 cursor-text overflow-hidden`}
    />
  );
}

// ── Semantic Section Renderer ──────────────────────────────────

function SectionContentView({ section, onSlotUpdate }: {
  section: Pick<Section, "block_code" | "slots_json">;
  onSlotUpdate: (key: string, newValue: unknown) => void;
}) {
  const slots = section.slots_json as Record<string, unknown> | null;
  if (!slots) return <p className="text-sm text-gray-300 italic py-4 text-center">Brak treści — wygeneruj</p>;

  const catCode = getCatCode(section.block_code);
  const entries = Object.entries(slots);
  const classified = entries.map(([key, value]) => ({ key, value, role: detectSlotRole(key, value) }));

  const titles = classified.filter(s => s.role === "title");
  const subtitles = classified.filter(s => s.role === "subtitle");
  const descriptions = classified.filter(s => s.role === "description");
  const buttons = classified.filter(s => s.role === "button");
  const lists = classified.filter(s => s.role === "list" || s.role === "stats");
  const others = classified.filter(s => s.role === "other");

  const isDark = ["FO", "CT"].includes(catCode);
  const isCentered = ["HE", "CT", "ST"].includes(catCode);

  return (
    <div className={`space-y-3 ${isCentered ? "text-center" : ""}`}>
      {titles.map(({ key, value }) => (
        <EditableText key={key} value={String(value)} onChange={v => onSlotUpdate(key, v)}
          className={`text-xl font-bold leading-tight ${isDark ? "text-white" : "text-gray-900"}`} />
      ))}
      {subtitles.map(({ key, value }) => (
        <EditableText key={key} value={String(value)} onChange={v => onSlotUpdate(key, v)}
          className={`text-base ${isDark ? "text-gray-300" : "text-gray-500"}`} />
      ))}
      {descriptions.map(({ key, value }) => (
        <EditableText key={key} value={String(value)} onChange={v => onSlotUpdate(key, v)}
          className={`text-sm leading-relaxed ${isDark ? "text-gray-400" : "text-gray-600"}`} />
      ))}
      {buttons.length > 0 && (
        <div className={`flex flex-wrap gap-2 pt-1 ${isCentered ? "justify-center" : ""}`}>
          {buttons.map(({ key, value }, i) => (
            <div key={key} className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold ${
              i === 0 ? "bg-indigo-600 text-white" : "border border-gray-300 text-gray-700"
            }`}>
              <EditableText value={String(value)} onChange={v => onSlotUpdate(key, v)}
                className={`text-sm font-semibold text-center ${i === 0 ? "text-white" : "text-gray-700"}`} />
            </div>
          ))}
        </div>
      )}
      {lists.map(({ key, value, role }) => {
        if (!Array.isArray(value) || value.length === 0) return null;
        if (role === "stats") {
          return (
            <div key={key} className="grid grid-cols-2 gap-3 pt-2">
              {value.map((item, i) => {
                if (typeof item !== "object" || item === null) return null;
                const obj = item as Record<string, unknown>;
                const numKey = Object.keys(obj).find(k2 => k2.includes("value") || k2.includes("number") || k2.includes("count")) ?? Object.keys(obj)[0];
                const labelKey = Object.keys(obj).find(k2 => k2.includes("label") || k2.includes("title") || k2.includes("name")) ?? Object.keys(obj)[1];
                return (
                  <div key={i} className={`p-3 rounded-lg ${isDark ? "bg-white/10" : "bg-gray-50"}`}>
                    <EditableText value={String(obj[numKey] ?? "")} onChange={v => {
                      const a = [...value]; a[i] = { ...a[i], [numKey]: v }; onSlotUpdate(key, a);
                    }} className={`text-xl font-bold text-center ${isDark ? "text-white" : "text-indigo-600"}`} />
                    {labelKey && (
                      <EditableText value={String(obj[labelKey] ?? "")} onChange={v => {
                        const a = [...value]; a[i] = { ...a[i], [labelKey]: v }; onSlotUpdate(key, a);
                      }} className={`text-xs text-center mt-0.5 ${isDark ? "text-gray-400" : "text-gray-500"}`} />
                    )}
                  </div>
                );
              })}
            </div>
          );
        }
        if (typeof value[0] === "object" && value[0] !== null) {
          return (
            <div key={key} className="grid grid-cols-1 gap-3 pt-2">
              {value.map((item, i) => {
                if (typeof item !== "object" || item === null) return null;
                const obj = item as Record<string, unknown>;
                const itemEntries = Object.entries(obj);
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
                  <div key={i} className={`rounded-lg p-3 space-y-1.5 ${isDark ? "bg-white/10" : "bg-gray-50"}`}>
                    {titleEntry && (
                      <EditableText value={String(titleEntry[1])} onChange={v => {
                        const a = [...value]; a[i] = { ...a[i], [titleEntry[0]]: v }; onSlotUpdate(key, a);
                      }} className={`text-sm font-semibold ${isDark ? "text-white" : "text-gray-800"}`} />
                    )}
                    {descEntry && (
                      <EditableText value={String(descEntry[1])} onChange={v => {
                        const a = [...value]; a[i] = { ...a[i], [descEntry[0]]: v }; onSlotUpdate(key, a);
                      }} className={`text-xs leading-relaxed ${isDark ? "text-gray-400" : "text-gray-500"}`} />
                    )}
                    {otherEntries.map(([k, v]) => (
                      <EditableText key={k} value={String(v)} onChange={newV => {
                        const a = [...value]; a[i] = { ...a[i], [k]: newV }; onSlotUpdate(key, a);
                      }} className={`text-xs ${isDark ? "text-gray-500" : "text-gray-400"}`} />
                    ))}
                  </div>
                );
              })}
            </div>
          );
        }
        return (
          <ul key={key} className="space-y-1 pt-1">
            {value.map((item, i) => (
              <li key={i} className={`flex items-start gap-2 text-sm ${isDark ? "text-gray-300" : "text-gray-600"}`}>
                <span className="mt-1 text-indigo-400">•</span>
                {typeof item === "string" ? (
                  <EditableText value={item} onChange={v => { const a = [...value]; a[i] = v; onSlotUpdate(key, a); }}
                    className={`text-sm ${isDark ? "text-gray-300" : "text-gray-600"}`} />
                ) : String(item)}
              </li>
            ))}
          </ul>
        );
      })}
      {others.map(({ key, value }) =>
        typeof value === "string" ? (
          <EditableText key={key} value={value} onChange={v => onSlotUpdate(key, v)}
            className={`text-sm ${isDark ? "text-gray-400" : "text-gray-600"}`} />
        ) : typeof value === "number" || typeof value === "boolean" ? (
          <span key={key} className="text-sm font-medium text-gray-700 block">{String(value)}</span>
        ) : null
      )}
    </div>
  );
}

// ── Per-Section Card ───────────────────────────────────────────

function SectionCard({ section, isGenerating, onSlotUpdate, onRegenerate }: {
  section: Section;
  isGenerating: boolean;
  onSlotUpdate: (key: string, value: unknown) => void;
  onRegenerate: (instruction: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [instruction, setInstruction] = useState("");
  const catCode = getCatCode(section.block_code);
  const catLabel = CAT_LABELS[catCode] ?? catCode;
  const sectionBg = getSectionBg(catCode);
  const isDark = ["FO", "CT"].includes(catCode);

  const handleRegenerate = () => {
    onRegenerate(instruction.trim());
    setInstruction("");
    setOpen(false);
  };

  return (
    <div
      data-section-id={section.id}
      className="relative border-b border-gray-100 last:border-b-0 group"
      style={{ backgroundColor: sectionBg }}
    >
      {/* Section label strip — top right on hover */}
      <div className="absolute top-2 right-3 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2 z-10">
        <span className={`text-[10px] font-mono ${isDark ? "text-white/40" : "text-gray-300"}`}>
          {section.block_code} · {catLabel}
        </span>
        {/* Regenerate toggle */}
        <button
          onClick={() => setOpen(o => !o)}
          title="Regeneruj sekcję"
          className="h-6 px-2 text-[10px] font-semibold rounded-md border transition-all bg-white/90 border-gray-200 text-indigo-600 hover:bg-indigo-50"
        >
          ⟳ AI
        </button>
      </div>

      {/* Regenerate panel */}
      {open && (
        <div className="absolute top-8 right-3 z-20 bg-white border border-gray-200 rounded-xl shadow-xl p-3 flex gap-2 w-72">
          <input
            type="text"
            value={instruction}
            onChange={e => setInstruction(e.target.value)}
            placeholder="Dodatkowa instrukcja (opcjonalnie)"
            className="flex-1 text-xs border border-gray-200 rounded-lg px-2 py-1.5 outline-none focus:border-indigo-400"
            onKeyDown={e => { if (e.key === "Enter") handleRegenerate(); if (e.key === "Escape") setOpen(false); }}
            autoFocus
          />
          <button
            onClick={handleRegenerate}
            disabled={isGenerating}
            className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-700 disabled:opacity-50 whitespace-nowrap"
          >
            {isGenerating ? "..." : "Regeneruj"}
          </button>
          <button onClick={() => setOpen(false)} className="text-gray-300 hover:text-gray-500 text-xs px-1">✕</button>
        </div>
      )}

      {/* Section content */}
      <div className="px-8 py-8">
        <SectionContentView section={section} onSlotUpdate={onSlotUpdate} />
      </div>
    </div>
  );
}

// ── AI Text Selection Toolbar ─────────────────────────────────

function AISelectionToolbar({ selectedText, onSubmit, onClose }: {
  selectedText: string;
  onSubmit: (instruction: string) => void;
  onClose: () => void;
}) {
  const [instruction, setInstruction] = useState("");
  return (
    <div
      className="fixed z-50 bg-white border border-gray-300 rounded-xl shadow-xl p-3 flex items-center gap-2 max-w-md"
      style={{ bottom: "5rem", left: "50%", transform: "translateX(-50%)" }}
    >
      <div className="text-xs text-gray-400 max-w-[100px] truncate" title={selectedText}>
        „{selectedText.slice(0, 30)}…"
      </div>
      <input
        type="text"
        value={instruction}
        onChange={e => setInstruction(e.target.value)}
        placeholder="Polecenie AI..."
        className="flex-1 px-2 py-1.5 border border-gray-200 rounded-lg text-xs min-w-[140px] outline-none focus:border-indigo-400"
        autoFocus
        onKeyDown={e => {
          if (e.key === "Enter" && instruction.trim()) onSubmit(instruction);
          if (e.key === "Escape") onClose();
        }}
      />
      <button
        onClick={() => instruction.trim() && onSubmit(instruction)}
        disabled={!instruction.trim()}
        className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-700 disabled:opacity-50 whitespace-nowrap"
      >
        Zmień
      </button>
      <button onClick={onClose} className="text-gray-300 hover:text-gray-500 text-xs px-1">✕</button>
    </div>
  );
}

// ── Main ──────────────────────────────────────────────────────

type SectionsSnapshot = { id: string; slots_json: Record<string, unknown> | null }[];

export default function Step4Content() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { sections, updateSection, regenerateSection, generateContent, isGenerating, error, setError } = useLabStore();

  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const [activeSectionId, setActiveSectionId] = useState<string | null>(null);
  const { toast, show: showToast } = useToast();

  // Undo/Redo — local snapshot stack of slots_json
  const historyRef = useRef<{ past: SectionsSnapshot[]; future: SectionsSnapshot[] }>({ past: [], future: [] });

  const snapshots = (): SectionsSnapshot => sections.map(s => ({ id: s.id, slots_json: s.slots_json ?? null }));

  const pushHistory = useCallback(() => {
    historyRef.current.past.push(snapshots());
    if (historyRef.current.past.length > 30) historyRef.current.past.shift();
    historyRef.current.future = [];
  }, [sections]); // eslint-disable-line react-hooks/exhaustive-deps

  const applySnapshot = useCallback((snap: SectionsSnapshot) => {
    for (const entry of snap) {
      const s = sections.find(x => x.id === entry.id);
      if (s && JSON.stringify(s.slots_json) !== JSON.stringify(entry.slots_json)) {
        updateSection(entry.id, { slots_json: entry.slots_json });
      }
    }
  }, [sections, updateSection]);

  const undo = useCallback(() => {
    const h = historyRef.current;
    if (!h.past.length) return;
    const prev = h.past.pop()!;
    h.future.push(snapshots());
    applySnapshot(prev);
    showToast("↶ Cofnięto");
  }, [applySnapshot, showToast]); // eslint-disable-line react-hooks/exhaustive-deps

  const redo = useCallback(() => {
    const h = historyRef.current;
    if (!h.future.length) return;
    const next = h.future.pop()!;
    h.past.push(snapshots());
    applySnapshot(next);
    showToast("↷ Przywrócono");
  }, [applySnapshot, showToast]); // eslint-disable-line react-hooks/exhaustive-deps

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const meta = e.metaKey || e.ctrlKey;
      if (meta && e.key === "z" && !e.shiftKey) { e.preventDefault(); undo(); }
      if (meta && (e.key === "y" || (e.key === "z" && e.shiftKey))) { e.preventDefault(); redo(); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [undo, redo]);

  // Scaled canvas
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerW, setContainerW] = useState(900);
  useLayoutEffect(() => {
    const update = () => { if (containerRef.current) setContainerW(containerRef.current.clientWidth); };
    update();
    const ro = new ResizeObserver(update);
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);
  const stageWidth = VIEWPORT_WIDTHS[viewport];
  const fitScale = Math.min(1, (containerW - 32) / stageWidth);

  // Text selection → AI toolbar
  useEffect(() => {
    const handler = () => {
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
    document.addEventListener("mouseup", handler);
    return () => document.removeEventListener("mouseup", handler);
  }, []);

  const handleAIChange = async (instruction: string) => {
    if (!activeSectionId || !selectedText) return;
    pushHistory();
    const fullInstruction = `Zmień fragment: "${selectedText}" — ${instruction}`;
    await regenerateSection(activeSectionId, fullInstruction);
    setSelectedText(null);
    setActiveSectionId(null);
    showToast("AI zaktualizowało tekst");
  };

  const handleSlotUpdate = useCallback((sectionId: string, key: string, newValue: unknown) => {
    pushHistory();
    const section = sections.find(s => s.id === sectionId);
    if (!section || !section.slots_json) return;
    const updatedSlots = { ...(section.slots_json as Record<string, unknown>), [key]: newValue };
    updateSection(sectionId, { slots_json: updatedSlots });
  }, [sections, updateSection, pushHistory]);

  const handleRegenerate = useCallback(async (sectionId: string, instruction: string) => {
    pushHistory();
    await regenerateSection(sectionId, instruction || undefined);
    showToast("Sekcja zregenerowana");
  }, [regenerateSection, pushHistory, showToast]);

  const handleGenerateAll = useCallback(async () => {
    pushHistory();
    await generateContent();
    showToast("Treści wygenerowane");
  }, [generateContent, pushHistory, showToast]);

  const hasContent = sections.some(s => s.slots_json);

  return (
    <div className="flex flex-col h-full overflow-hidden" style={{ minHeight: "calc(100vh - 96px)" }}>
      {/* Toolbar */}
      <div className="sticky top-0 z-20 bg-white border-b border-gray-100 px-6 py-2.5 flex items-center gap-3 flex-shrink-0">
        <h1 className="text-sm font-bold text-slate-800">Treści</h1>

        {/* Viewport switcher */}
        <div className="flex border border-gray-200 rounded-lg overflow-hidden">
          {(["desktop", "tablet", "mobile"] as const).map(v => (
            <button
              key={v}
              onClick={() => setViewport(v)}
              title={`${v} — ${VIEWPORT_WIDTHS[v]}px`}
              className={`px-2.5 py-1.5 text-[11px] font-medium transition-colors ${viewport === v ? "bg-slate-800 text-white" : "text-gray-500 hover:bg-gray-50"}`}
            >
              {v === "desktop" ? "🖥 D" : v === "tablet" ? "⬜ T" : "📱 M"}
            </button>
          ))}
        </div>

        {/* Undo / Redo */}
        <div className="flex bg-gray-100 rounded-lg p-0.5 gap-0.5">
          <button
            onClick={undo}
            disabled={historyRef.current.past.length === 0}
            title="Cofnij (Ctrl+Z)"
            className="w-7 h-7 grid place-items-center rounded-md text-gray-500 hover:bg-white hover:text-gray-800 disabled:opacity-30 transition-all"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M9 14l-4-4 4-4"/><path d="M5 10h9a6 6 0 010 12h-2"/></svg>
          </button>
          <button
            onClick={redo}
            disabled={historyRef.current.future.length === 0}
            title="Przywróć (Ctrl+Shift+Z)"
            className="w-7 h-7 grid place-items-center rounded-md text-gray-500 hover:bg-white hover:text-gray-800 disabled:opacity-30 transition-all"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M15 14l4-4-4-4"/><path d="M19 10h-9a6 6 0 000 12h2"/></svg>
          </button>
        </div>

        <div className="flex-1" />

        <button
          onClick={handleGenerateAll}
          disabled={isGenerating}
          className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 disabled:opacity-50 transition-colors"
        >
          {isGenerating ? "Generowanie..." : "Regeneruj wszystko"}
        </button>
      </div>

      {/* Scaled Canvas */}
      <div className="flex-1 overflow-y-auto bg-slate-100 p-6" ref={containerRef}>
        {/* States */}
        {isGenerating && sections.length === 0 && (
          <div className="text-center py-20">
            <div className="inline-flex items-center gap-3 bg-white border border-gray-200 px-6 py-4 rounded-2xl shadow-sm">
              <svg className="animate-spin w-5 h-5 text-indigo-500" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              <span className="text-sm font-medium text-gray-600">AI generuje treści...</span>
            </div>
          </div>
        )}

        {!isGenerating && error && sections.length === 0 && (
          <div className="text-center py-12 space-y-4">
            <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-5 py-3 rounded-xl border border-red-200">
              <span>✗</span><span className="text-sm">{error}</span>
            </div>
            <div>
              <button onClick={() => { setError(null); handleGenerateAll(); }} className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700">
                Spróbuj ponownie
              </button>
            </div>
          </div>
        )}

        {sections.length === 0 && !isGenerating && !error && (
          <div className="text-center py-20 text-gray-400 text-sm space-y-4">
            <p>Brak sekcji. Wróć do kroku 3 aby wygenerować strukturę.</p>
          </div>
        )}

        {sections.length > 0 && !hasContent && !isGenerating && (
          <div className="text-center py-12 text-gray-400 text-sm space-y-4">
            <p>Sekcje gotowe — wygeneruj treści.</p>
            <button onClick={handleGenerateAll} className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700">
              Generuj treści AI
            </button>
          </div>
        )}

        {isGenerating && sections.length > 0 && (
          <div className="text-center py-4 mb-4">
            <div className="inline-flex items-center gap-3 bg-white border border-gray-200 px-5 py-3 rounded-xl shadow-sm">
              <svg className="animate-spin w-4 h-4 text-indigo-500" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              <span className="text-sm font-medium text-gray-600">AI regeneruje...</span>
            </div>
          </div>
        )}

        {/* Page canvas — scaled */}
        {sections.length > 0 && hasContent && (
          <div style={{ width: stageWidth, transformOrigin: "top center", transform: `scale(${fitScale})`, margin: "0 auto" }}>
            <div
              className="rounded-2xl overflow-hidden shadow-2xl"
              style={{
                width: stageWidth,
                boxShadow: "0 4px 32px rgba(15,23,42,.12), 0 0 0 1px rgba(15,23,42,.06)",
              }}
            >
              {sections.map(section => (
                <SectionCard
                  key={section.id}
                  section={section}
                  isGenerating={isGenerating}
                  onSlotUpdate={(key, val) => handleSlotUpdate(section.id, key, val)}
                  onRegenerate={instruction => handleRegenerate(section.id, instruction)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* AI Selection Toolbar */}
      {selectedText && (
        <AISelectionToolbar
          selectedText={selectedText}
          onSubmit={handleAIChange}
          onClose={() => { setSelectedText(null); setActiveSectionId(null); }}
        />
      )}

      {/* Toast */}
      {toast && <Toast message={toast} />}

      {/* Bottom nav */}
      <div className="bg-white border-t border-gray-100 px-6 py-3 flex justify-between flex-shrink-0">
        <button onClick={() => navigate(`/lab/${projectId}/step/3`)} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">
          ← Wstecz
        </button>
        <button
          onClick={() => navigate(`/lab/${projectId}/step/5`)}
          disabled={sections.length === 0}
          className="px-6 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          Dalej → Kreacja wizualna
        </button>
      </div>
    </div>
  );
}
