import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";

const BG_TYPES = ["white", "light_gray", "dark", "brand_color", "brand_gradient", "dark_photo_overlay"];
const MEDIA_TYPES = ["photo_wide", "photo_split", "icons", "infographic_steps", "infographic_numbers", "avatars", "none", "logo"];

export default function Step3VisualConcept() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { visualConcept, style, generateVisualConcept, generateContent, saveVisualConcept, isGenerating } = useLabStore();

  const handleSectionChange = (idx: number, field: string, value: string) => {
    if (!visualConcept) return;
    const updated = { ...visualConcept };
    updated.sections = [...updated.sections];
    updated.sections[idx] = { ...updated.sections[idx], [field]: value };
    saveVisualConcept(updated);
  };

  const handleNext = async () => {
    await generateContent();
    navigate(`/lab/${projectId}/step/4`);
  };

  if (!visualConcept) {
    return (
      <div className="max-w-2xl mx-auto p-6 text-center py-12">
        <p className="text-gray-400 mb-4">Brak visual concept. Wygeneruj go.</p>
        <button
          onClick={() => generateVisualConcept()}
          disabled={isGenerating}
          className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50"
        >
          {isGenerating ? "Generowanie..." : "Generuj Visual Concept"}
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-800">Koncepcja wizualna</h1>
        <button
          onClick={() => generateVisualConcept()}
          disabled={isGenerating}
          className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600"
        >
          Regeneruj
        </button>
      </div>

      {/* Global settings */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
        <div className="flex items-center gap-6 text-sm">
          <div>
            <span className="text-gray-500">Styl:</span>{" "}
            <span className="font-medium">{visualConcept.style}</span>
          </div>
          <div>
            <span className="text-gray-500">Podejscie tla:</span>{" "}
            <span className="font-medium">{visualConcept.bg_approach}</span>
          </div>
          <div>
            <span className="text-gray-500">Separator:</span>{" "}
            <span className="font-medium">{visualConcept.separator_type}</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">Kolory:</span>
          <div className="w-6 h-6 rounded" style={{ backgroundColor: style.primary_color }} />
          <div className="w-6 h-6 rounded" style={{ backgroundColor: style.secondary_color }} />
        </div>
      </div>

      {/* Sections table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-2 text-gray-500 font-medium">Sekcja</th>
              <th className="text-left px-4 py-2 text-gray-500 font-medium">Tlo</th>
              <th className="text-left px-4 py-2 text-gray-500 font-medium">Media</th>
              <th className="text-left px-4 py-2 text-gray-500 font-medium">Photo query</th>
            </tr>
          </thead>
          <tbody>
            {visualConcept.sections.map((sec, idx) => (
              <tr key={idx} className="border-b border-gray-100 last:border-0">
                <td className="px-4 py-2">
                  <span className="font-mono text-xs bg-gray-100 px-1.5 py-0.5 rounded">
                    {sec.block_code}
                  </span>
                </td>
                <td className="px-4 py-2">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-4 h-4 rounded border border-gray-300"
                      style={{ backgroundColor: sec.bg_value || "#fff" }}
                    />
                    <select
                      value={sec.bg_type}
                      onChange={(e) => handleSectionChange(idx, "bg_type", e.target.value)}
                      className="text-xs border border-gray-200 rounded px-1.5 py-0.5 bg-white"
                    >
                      {BG_TYPES.map((t) => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </div>
                </td>
                <td className="px-4 py-2">
                  <select
                    value={sec.media_type}
                    onChange={(e) => handleSectionChange(idx, "media_type", e.target.value)}
                    className="text-xs border border-gray-200 rounded px-1.5 py-0.5 bg-white"
                  >
                    {MEDIA_TYPES.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-2">
                  <input
                    type="text"
                    value={sec.photo_query || ""}
                    onChange={(e) => handleSectionChange(idx, "photo_query", e.target.value)}
                    className="text-xs border border-gray-200 rounded px-2 py-0.5 w-full"
                    placeholder="—"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between pt-4">
        <button
          onClick={() => navigate(`/lab/${projectId}/step/2`)}
          className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700"
        >
          ← Wstecz
        </button>
        <button
          onClick={handleNext}
          disabled={isGenerating}
          className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {isGenerating ? "AI generuje tresci..." : "Generuj tresci →"}
        </button>
      </div>
    </div>
  );
}
