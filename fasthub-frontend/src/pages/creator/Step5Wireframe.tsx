/**
 * Step 5 — Wireframe editor: inline text editing, reorder, AI per section.
 * Brief 34: fullscreen 2-panel layout, contentEditable, drag handles.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Btn from "@/components/ui/Btn";
import SidePanel from "@/components/creator/SidePanel";
import AddSectionModal from "@/components/creator/AddSectionModal";
import { useCreatorStore } from "@/store/creatorStore";
import type { ProjectSection } from "@/types/creator";

// Quick AI actions for per-section popup
const QUICK_ACTIONS = [
  { label: "Zmien naglowek na krotszy", instruction: "Skróć nagłówek do maksymalnie 6 słów" },
  { label: "Dodaj liczby", instruction: "Dodaj statystyki i liczby do treści" },
  { label: "Napisz bardziej formalnie", instruction: "Przepisz treść w bardziej formalnym tonie" },
  { label: "Napisz krotsze teksty", instruction: "Skróć wszystkie teksty o 30%" },
];

export default function Step5Wireframe() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const {
    sections,
    activeSection,
    setActiveSection,
    loadSections,
    updateSection,
    removeSection,
    reorderSections,
    addSection,
    regenerateSection,
    isSaving,
  } = useCreatorStore();

  const [addModalOpen, setAddModalOpen] = useState(false);
  const [aiPopup, setAiPopup] = useState<string | null>(null);
  const [customInstruction, setCustomInstruction] = useState("");
  const sectionRefs = useRef<Map<string, HTMLDivElement>>(new Map());

  useEffect(() => {
    loadSections();
  }, []);

  // Scroll to section
  const scrollToSection = useCallback((sectionId: string) => {
    const el = sectionRefs.current.get(sectionId);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
    setActiveSection(sectionId);
  }, []);

  // Inline edit: save on blur
  const handleSlotBlur = useCallback(
    (section: ProjectSection, slotId: string, newValue: string) => {
      const currentVal = (section.slots_json?.[slotId] as string) || "";
      if (newValue !== currentVal) {
        updateSection(section.id, {
          slots_json: { ...section.slots_json, [slotId]: newValue },
        });
      }
    },
    [updateSection],
  );

  // Move section up/down
  const moveSection = useCallback(
    (sectionId: string, direction: -1 | 1) => {
      const idx = sections.findIndex((s) => s.id === sectionId);
      if (idx < 0) return;
      const newIdx = idx + direction;
      if (newIdx < 0 || newIdx >= sections.length) return;
      const newOrder = sections.map((s) => s.id);
      [newOrder[idx], newOrder[newIdx]] = [newOrder[newIdx], newOrder[idx]];
      reorderSections(newOrder);
    },
    [sections, reorderSections],
  );

  // Add section
  const handleAddSection = useCallback(
    async (blockCode: string) => {
      setAddModalOpen(false);
      const section = await addSection(blockCode);
      if (section) {
        regenerateSection(section.id);
      }
    },
    [addSection, regenerateSection],
  );

  // AI per section
  const handleAiAction = useCallback(
    (sectionId: string, instruction: string) => {
      setAiPopup(null);
      setCustomInstruction("");
      regenerateSection(sectionId, instruction);
    },
    [regenerateSection],
  );

  // Extract text slots from section
  const getTextSlots = (section: ProjectSection) => {
    const slots = section.slots_json || {};
    return Object.entries(slots).filter(
      ([, val]) => typeof val === "string" && !String(val).startsWith("/"),
    );
  };

  return (
    <div className="flex h-[calc(100vh-7rem)]">
      {/* Main panel */}
      <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
        <div className="max-w-3xl mx-auto space-y-4">
          {sections.length === 0 && (
            <div className="text-center py-16 text-gray-400">
              <p className="text-lg mb-2">Brak sekcji</p>
              <p className="text-sm">Kliknij "Dodaj sekcje" w panelu bocznym.</p>
            </div>
          )}

          {sections.map((section, idx) => (
            <div
              key={section.id}
              ref={(el) => {
                if (el) sectionRefs.current.set(section.id, el);
              }}
              data-section-id={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`relative border-2 rounded-xl p-6 bg-white transition-all cursor-pointer ${
                activeSection === section.id
                  ? "border-indigo-400 shadow-sm"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              {/* Section header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-gray-100 rounded text-gray-500">
                    {section.block_code}
                  </span>
                  <span className="text-xs text-gray-400">
                    Sekcja {idx + 1}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  {/* Move up */}
                  <button
                    onClick={(e) => { e.stopPropagation(); moveSection(section.id, -1); }}
                    disabled={idx === 0}
                    className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                    title="W gore"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                  </button>
                  {/* Move down */}
                  <button
                    onClick={(e) => { e.stopPropagation(); moveSection(section.id, 1); }}
                    disabled={idx === sections.length - 1}
                    className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                    title="W dol"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {/* AI */}
                  <button
                    onClick={(e) => { e.stopPropagation(); setAiPopup(aiPopup === section.id ? null : section.id); }}
                    className="p-1 rounded hover:bg-indigo-50 text-indigo-500 hover:text-indigo-700"
                    title="AI"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                    </svg>
                  </button>
                  {/* Delete */}
                  <button
                    onClick={(e) => { e.stopPropagation(); removeSection(section.id); }}
                    className="p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-500"
                    title="Usun"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* AI popup */}
              {aiPopup === section.id && (
                <div className="absolute right-0 top-12 z-20 bg-white border border-gray-200 rounded-xl shadow-lg p-3 w-64">
                  <div className="space-y-1 mb-2">
                    {QUICK_ACTIONS.map((action) => (
                      <button
                        key={action.label}
                        onClick={() => handleAiAction(section.id, action.instruction)}
                        className="w-full text-left px-3 py-1.5 text-xs rounded-lg hover:bg-indigo-50 text-gray-700 hover:text-indigo-700"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                  <div className="border-t border-gray-100 pt-2">
                    <div className="flex gap-1">
                      <input
                        type="text"
                        value={customInstruction}
                        onChange={(e) => setCustomInstruction(e.target.value)}
                        placeholder="Wlasne polecenie..."
                        className="flex-1 px-2 py-1 border border-gray-200 rounded text-xs outline-none focus:border-indigo-400"
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && customInstruction.trim()) {
                            handleAiAction(section.id, customInstruction.trim());
                          }
                        }}
                      />
                      <button
                        onClick={() => {
                          if (customInstruction.trim()) handleAiAction(section.id, customInstruction.trim());
                        }}
                        className="px-2 py-1 bg-indigo-600 text-white rounded text-xs hover:bg-indigo-700"
                      >
                        OK
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Editable text slots */}
              <div className="space-y-3">
                {getTextSlots(section).map(([slotId, value]) => (
                  <div key={slotId} className="group">
                    <label className="text-[10px] text-gray-400 uppercase tracking-wider">{slotId}</label>
                    <div
                      contentEditable
                      suppressContentEditableWarning
                      onBlur={(e) => handleSlotBlur(section, slotId, e.currentTarget.innerText)}
                      className={`outline-none rounded px-2 py-1 -mx-2 border border-transparent focus:border-indigo-200 focus:bg-indigo-50/30 transition-colors ${
                        slotId.includes("title") ? "text-lg font-semibold text-gray-800" : "text-sm text-gray-600"
                      }`}
                    >
                      {String(value)}
                    </div>
                  </div>
                ))}

                {/* Image placeholders */}
                {Object.entries(section.slots_json || {})
                  .filter(([, val]) => typeof val === "string" && String(val).startsWith("/"))
                  .map(([slotId, val]) => (
                    <div key={slotId} className="rounded-lg bg-gray-100 h-32 flex items-center justify-center">
                      <img src={String(val)} alt={slotId} className="max-h-full max-w-full object-contain rounded" />
                    </div>
                  ))}

                {/* Empty image placeholders for items that are arrays */}
                {Object.entries(section.slots_json || {})
                  .filter(([, val]) => Array.isArray(val))
                  .map(([slotId, val]) => (
                    <div key={slotId}>
                      <label className="text-[10px] text-gray-400 uppercase tracking-wider">{slotId}</label>
                      <div className="text-xs text-gray-500 bg-gray-50 rounded-lg p-2">
                        {(val as unknown[]).length} elementow
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}

          {/* Add section inline button */}
          {sections.length > 0 && (
            <button
              onClick={() => setAddModalOpen(true)}
              className="w-full py-4 border-2 border-dashed border-gray-200 rounded-xl text-gray-400 text-sm hover:border-indigo-300 hover:text-indigo-500 transition-colors"
            >
              + Dodaj sekcje
            </button>
          )}
        </div>

        {/* Bottom action bar */}
        <div className="max-w-3xl mx-auto mt-8 pb-6 flex justify-between">
          <Btn variant="ghost" onClick={() => navigate(`/creator/${projectId}/step/4`)}>
            Wstecz
          </Btn>
          <Btn onClick={() => navigate(`/creator/${projectId}/step/6`)}>
            Dalej — podglad w kolorze
          </Btn>
        </div>
      </div>

      {/* Side panel */}
      <SidePanel
        step={5}
        onScrollToSection={scrollToSection}
        onAddSection={() => setAddModalOpen(true)}
      />

      {/* Add section modal */}
      <AddSectionModal
        open={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onSelect={handleAddSection}
      />
    </div>
  );
}
