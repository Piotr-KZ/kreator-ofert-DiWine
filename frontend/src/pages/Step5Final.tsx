import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";
import { getPreviewUrl, exportHtml } from "@/api/client";

export default function Step5Final() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { projectName } = useLabStore();
  const [viewport, setViewport] = useState<"desktop" | "tablet" | "mobile">("desktop");

  const previewUrl = projectId ? getPreviewUrl(projectId) : "";

  const viewportWidths = {
    desktop: "100%",
    tablet: "768px",
    mobile: "375px",
  };

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)]">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-gray-700">Gotowa strona</h2>
          <span className="text-xs text-gray-400">{projectName}</span>
        </div>

        <div className="flex items-center gap-3">
          {/* Viewport toggle */}
          <div className="flex border border-gray-200 rounded-lg overflow-hidden">
            {(["desktop", "tablet", "mobile"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setViewport(v)}
                className={`px-3 py-1.5 text-xs ${
                  viewport === v
                    ? "bg-emerald-50 text-emerald-700 font-medium"
                    : "text-gray-500 hover:bg-gray-50"
                }`}
              >
                {v === "desktop" ? "Desktop" : v === "tablet" ? "Tablet" : "Mobile"}
              </button>
            ))}
          </div>

          {/* Actions */}
          <button
            onClick={() => projectId && exportHtml(projectId)}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-semibold hover:bg-emerald-700"
          >
            Pobierz HTML
          </button>
          <button
            onClick={() => navigate("/lab/create")}
            className="px-4 py-2 border border-gray-200 rounded-lg text-xs text-gray-600 hover:bg-gray-50"
          >
            Generuj nowa
          </button>
        </div>
      </div>

      {/* Preview */}
      <div className="flex-1 bg-gray-100 flex justify-center overflow-auto p-4">
        <div
          style={{ width: viewportWidths[viewport], maxWidth: "100%" }}
          className="bg-white shadow-lg rounded-lg overflow-hidden transition-all duration-300"
        >
          <iframe
            src={previewUrl}
            className="w-full h-full border-0"
            style={{ minHeight: "80vh" }}
            title="Podglad finalny"
          />
        </div>
      </div>

      {/* Bottom bar */}
      <div className="bg-white border-t border-gray-200 px-6 py-3 flex justify-between">
        <button
          onClick={() => navigate(`/lab/${projectId}/step/4`)}
          className="text-xs text-gray-500 hover:text-gray-700"
        >
          ← Wstecz do tresci
        </button>
      </div>
    </div>
  );
}
