/**
 * Step 6 — Visual preview: rendered page in iframe, viewport switcher, stock photos.
 * Brief 34: fullscreen immersive layout with real page rendering.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Btn from "@/components/ui/Btn";
import SidePanel from "@/components/creator/SidePanel";
import AddSectionModal from "@/components/creator/AddSectionModal";
import StockPhotoModal from "@/components/creator/StockPhotoModal";
import { useCreatorStore } from "@/store/creatorStore";
import * as api from "@/api/creator";

type Viewport = "desktop" | "tablet" | "phone";

const VIEWPORTS: Record<Viewport, { width: number; label: string }> = {
  desktop: { width: 1280, label: "Desktop" },
  tablet: { width: 768, label: "Tablet" },
  phone: { width: 375, label: "Telefon" },
};

export default function Step6Preview() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const {
    project,
    sections,
    renderedHtml,
    renderedCss,
    loadRenderedPage,
    loadSections,
    addSection,
    regenerateSection,
    updateSection,
    removeSection,
  } = useCreatorStore();

  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [mode, setMode] = useState<"ai" | "manual">("ai");
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [stockPhotoOpen, setStockPhotoOpen] = useState(false);
  const [stockPhotoTarget, setStockPhotoTarget] = useState({ sectionId: "", slotId: "" });
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [reviewResult, setReviewResult] = useState<Record<string, unknown> | null>(null);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [sectionPopup, setSectionPopup] = useState<string | null>(null);

  useEffect(() => {
    loadSections();
    loadRenderedPage();
  }, []);

  // Build full HTML for iframe
  const iframeSrcDoc = useMemo(() => {
    if (!renderedHtml) return "";
    return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@3/dist/tailwind.min.css" />
  <style>${renderedCss}</style>
  <style>
    body { margin: 0; }
    [data-section-id] { cursor: pointer; position: relative; }
    [data-section-id]:hover { outline: 2px solid rgba(79, 70, 229, 0.3); outline-offset: -2px; }
  </style>
</head>
<body>${renderedHtml}</body>
</html>`;
  }, [renderedHtml, renderedCss]);

  // Calculate scale for viewport
  const containerRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (!node) return;
      // No additional setup needed — CSS handles scaling
    },
    [],
  );

  // Visual review
  const handleVisualReview = async () => {
    if (!projectId) return;
    setReviewLoading(true);
    setReviewModalOpen(true);
    try {
      const { data } = await api.visualReview(projectId);
      setReviewResult(data);
    } catch {
      setReviewResult({ error: "Nie udalo sie przeprowadzic przegladu" });
    }
    setReviewLoading(false);
  };

  // Add section
  const handleAddSection = async (blockCode: string) => {
    setAddModalOpen(false);
    const section = await addSection(blockCode);
    if (section) {
      await regenerateSection(section.id);
      loadRenderedPage();
    }
  };

  // Section action popup
  const handleSectionAction = (action: string, sectionId: string) => {
    setSectionPopup(null);
    switch (action) {
      case "regenerate":
        regenerateSection(sectionId).then(() => loadRenderedPage());
        break;
      case "delete":
        removeSection(sectionId).then(() => loadRenderedPage());
        break;
      case "photo": {
        const sec = sections.find((s) => s.id === sectionId);
        const imgSlot = sec
          ? Object.entries(sec.slots_json || {}).find(([, v]) => typeof v === "string" && String(v).startsWith("/"))
          : null;
        if (imgSlot) {
          setStockPhotoTarget({ sectionId, slotId: imgSlot[0] });
          setStockPhotoOpen(true);
        }
        break;
      }
      case "variant": {
        const sec = sections.find((s) => s.id === sectionId);
        if (sec) {
          const next = sec.variant === "A" ? "B" : sec.variant === "B" ? "C" : "A";
          updateSection(sectionId, { variant: next }).then(() => loadRenderedPage());
        }
        break;
      }
    }
  };

  // Photo saved callback
  const handlePhotoSaved = () => {
    loadSections();
    loadRenderedPage();
  };

  const vpConfig = VIEWPORTS[viewport];

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)]">
      {/* Sticky top bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-200 flex-shrink-0">
        <div className="flex items-center gap-2">
          {/* Mode toggle */}
          <div className="flex bg-gray-100 rounded-lg p-0.5">
            <button
              onClick={() => setMode("ai")}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                mode === "ai" ? "bg-white shadow text-indigo-700" : "text-gray-500"
              }`}
            >
              AI buduje
            </button>
            <button
              onClick={() => setMode("manual")}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                mode === "manual" ? "bg-white shadow text-gray-900" : "text-gray-500"
              }`}
            >
              Sam buduje
            </button>
          </div>
        </div>

        {/* Viewport switcher */}
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-0.5">
          {(Object.keys(VIEWPORTS) as Viewport[]).map((vp) => (
            <button
              key={vp}
              onClick={() => setViewport(vp)}
              className={`px-2.5 py-1.5 rounded-md transition-colors ${
                viewport === vp ? "bg-white shadow text-gray-900" : "text-gray-400 hover:text-gray-600"
              }`}
              title={VIEWPORTS[vp].label}
            >
              {vp === "desktop" ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              ) : vp === "tablet" ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              )}
            </button>
          ))}
        </div>

        {/* Next button */}
        <Btn onClick={() => navigate(`/creator/${projectId}/step/7`)} className="text-xs py-1.5">
          Dalej
        </Btn>
      </div>

      {/* Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Preview panel */}
        <div className="flex-1 overflow-auto bg-gray-100 flex justify-center py-6" ref={containerRef}>
          <div
            className="bg-white shadow-xl origin-top transition-all duration-300"
            style={{ width: vpConfig.width, minHeight: 600 }}
          >
            {iframeSrcDoc ? (
              <iframe
                srcDoc={iframeSrcDoc}
                className="w-full border-0"
                style={{ width: vpConfig.width, minHeight: 800 }}
                title="Podglad strony"
              />
            ) : (
              <div className="flex items-center justify-center h-96 text-gray-400 text-sm">
                <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Renderuje strone...
              </div>
            )}
          </div>
        </div>

        {/* Section action popup (shown when section is clicked in AI mode) */}
        {sectionPopup && mode === "ai" && (
          <div className="fixed z-30 bg-white border border-gray-200 rounded-xl shadow-lg p-2 w-48"
            style={{ top: "50%", left: "40%", transform: "translate(-50%, -50%)" }}
          >
            <button onClick={() => handleSectionAction("regenerate", sectionPopup)} className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-gray-50">Napisz inaczej</button>
            <button onClick={() => handleSectionAction("variant", sectionPopup)} className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-gray-50">Zmien wariant</button>
            <button onClick={() => handleSectionAction("photo", sectionPopup)} className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-gray-50">Zmien zdjecie</button>
            <button onClick={() => handleSectionAction("delete", sectionPopup)} className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-red-50 text-red-600">Usun sekcje</button>
            <hr className="my-1" />
            <button onClick={() => setSectionPopup(null)} className="w-full text-left px-3 py-2 text-xs rounded-lg text-gray-400 hover:bg-gray-50">Zamknij</button>
          </div>
        )}

        {/* Side panel */}
        <SidePanel
          step={6}
          onScrollToSection={() => {}}
          onAddSection={() => setAddModalOpen(true)}
          onVisualReview={handleVisualReview}
        />
      </div>

      {/* Modals */}
      <AddSectionModal
        open={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onSelect={handleAddSection}
      />

      {projectId && (
        <StockPhotoModal
          open={stockPhotoOpen}
          onClose={() => setStockPhotoOpen(false)}
          projectId={projectId}
          sectionId={stockPhotoTarget.sectionId}
          slotId={stockPhotoTarget.slotId}
          onPhotoSaved={handlePhotoSaved}
        />
      )}

      {/* Visual review modal */}
      {reviewModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={() => setReviewModalOpen(false)}>
          <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full mx-4 p-6" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">AI ocenia Twoja strone</h2>
            {reviewLoading ? (
              <div className="flex items-center gap-2 text-gray-400 py-8 justify-center text-sm">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                AI analizuje...
              </div>
            ) : reviewResult ? (
              <div className="text-sm text-gray-700">
                <pre className="whitespace-pre-wrap bg-gray-50 rounded-xl p-4 text-xs max-h-60 overflow-y-auto">
                  {JSON.stringify(reviewResult, null, 2)}
                </pre>
              </div>
            ) : null}
            <div className="mt-4 flex justify-end gap-2">
              <Btn variant="ghost" onClick={() => setReviewModalOpen(false)}>Zamknij</Btn>
              <Btn onClick={() => { setReviewModalOpen(false); loadRenderedPage(); }}>Popraw automatycznie</Btn>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
