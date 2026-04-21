import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";
import { getPreviewUrl } from "@/api/client";

export default function Step4Content() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { sections, regenerateSection, generateContent, isGenerating } = useLabStore();
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [instruction, setInstruction] = useState("");
  const [iframeKey, setIframeKey] = useState(0);

  const previewUrl = projectId ? getPreviewUrl(projectId) : "";

  const handleRegenerate = async (sectionId: string) => {
    await regenerateSection(sectionId, instruction || undefined);
    setInstruction("");
    setActiveSection(null);
    setIframeKey((k) => k + 1); // refresh iframe
  };

  const refreshPreview = () => setIframeKey((k) => k + 1);

  return (
    <div className="flex h-[calc(100vh-7rem)]">
      {/* Preview iframe */}
      <div className="flex-1 bg-gray-100">
        {projectId && sections.some((s) => s.slots_json) ? (
          <iframe
            key={iframeKey}
            src={previewUrl}
            className="w-full h-full border-0"
            title="Podglad strony"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
            <div className="text-center">
              <p className="mb-4">Brak tresci. Wygeneruj je.</p>
              <button
                onClick={() => generateContent()}
                disabled={isGenerating}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 disabled:opacity-50"
              >
                {isGenerating ? "Generowanie..." : "Generuj tresci"}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Side panel */}
      <div className="w-72 bg-white border-l border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-100">
          <h2 className="text-sm font-semibold text-gray-700">Sekcje</h2>
          <div className="flex gap-2 mt-2">
            <button
              onClick={refreshPreview}
              className="text-xs px-2 py-1 border border-gray-200 rounded hover:bg-gray-50"
            >
              Odswiez
            </button>
            <button
              onClick={() => generateContent()}
              disabled={isGenerating}
              className="text-xs px-2 py-1 bg-emerald-50 text-emerald-700 rounded hover:bg-emerald-100 disabled:opacity-50"
            >
              {isGenerating ? "..." : "Regeneruj wszystko"}
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {sections.map((section, idx) => (
            <div key={section.id}>
              <button
                onClick={() => setActiveSection(activeSection === section.id ? null : section.id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors ${
                  activeSection === section.id
                    ? "bg-emerald-50 text-emerald-700"
                    : "hover:bg-gray-50 text-gray-600"
                }`}
              >
                <span className="font-mono text-gray-400 mr-1">{idx + 1}.</span>
                {section.block_code}
                {section.slots_json ? (
                  <span className="text-green-500 ml-1">✓</span>
                ) : (
                  <span className="text-gray-300 ml-1">○</span>
                )}
              </button>

              {/* Quick actions per section */}
              {activeSection === section.id && (
                <div className="ml-4 mt-1 space-y-1 pb-2">
                  <div className="flex gap-1">
                    <input
                      type="text"
                      value={instruction}
                      onChange={(e) => setInstruction(e.target.value)}
                      placeholder="Instrukcja AI..."
                      className="flex-1 px-2 py-1 border border-gray-200 rounded text-xs"
                      onKeyDown={(e) => e.key === "Enter" && handleRegenerate(section.id)}
                    />
                    <button
                      onClick={() => handleRegenerate(section.id)}
                      disabled={isGenerating}
                      className="px-2 py-1 bg-emerald-600 text-white rounded text-xs hover:bg-emerald-700 disabled:opacity-50"
                    >
                      OK
                    </button>
                  </div>
                  {["Skroc teksty", "Bardziej formalnie", "Dodaj liczby"].map((q) => (
                    <button
                      key={q}
                      onClick={() => {
                        regenerateSection(section.id, q);
                        setActiveSection(null);
                        setTimeout(refreshPreview, 2000);
                      }}
                      className="block w-full text-left px-2 py-1 text-xs text-gray-500 hover:text-emerald-700 hover:bg-emerald-50 rounded"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Bottom nav */}
        <div className="p-4 border-t border-gray-100 flex justify-between">
          <button
            onClick={() => navigate(`/lab/${projectId}/step/3`)}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            ← Wstecz
          </button>
          <button
            onClick={() => navigate(`/lab/${projectId}/step/5`)}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-semibold hover:bg-emerald-700"
          >
            Dalej →
          </button>
        </div>
      </div>
    </div>
  );
}
