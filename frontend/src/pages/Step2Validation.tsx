import { useEffect, useState, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";

interface ValidationItem {
  type: "ok" | "warning" | "error";
  message: string;
  field?: string;
  suggestion?: string;
}

const FIELD_LABELS: Record<string, string> = {
  description: "Opis firmy",
  target_audience: "Grupa docelowa",
  usp: "Wyróżnik",
  tone: "Ton komunikacji",
};

export default function Step2Validation() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { validateBrief, analyzeWebsite, setBrief, saveBrief, isGenerating, error, projectId: storeProjectId } = useLabStore();

  const [items, setItems] = useState<ValidationItem[]>([]);
  const [dismissed, setDismissed] = useState<Set<number>>(new Set());
  const [editedSuggestions, setEditedSuggestions] = useState<Record<number, string>>({});
  const [accepted, setAccepted] = useState<Set<number>>(new Set());
  const [localError, setLocalError] = useState<string | null>(null);
  const [websiteAnalysis, setWebsiteAnalysis] = useState<Record<string, unknown> | null>(null);
  const [phase, setPhase] = useState<"idle" | "analyzing_website" | "validating">("idle");
  const startedRef = useRef(false);

  const runFullFlow = async () => {
    setLocalError(null);
    setItems([]);
    setDismissed(new Set());
    setAccepted(new Set());
    setEditedSuggestions({});
    setWebsiteAnalysis(null);

    // Phase 1: If website is set, analyze it first
    const { brief: currentBrief } = useLabStore.getState();
    if (currentBrief.website && currentBrief.website.startsWith("http")) {
      setPhase("analyzing_website");
      const analysis = await analyzeWebsite();
      if (analysis && !analysis.error) {
        setWebsiteAnalysis(analysis);
        const updates: Record<string, string> = {};
        if (!currentBrief.description && analysis.description) updates.description = analysis.description as string;
        if (!currentBrief.target_audience && analysis.target_audience) updates.target_audience = analysis.target_audience as string;
        if (!currentBrief.usp && analysis.usp) updates.usp = analysis.usp as string;
        if (analysis.tone) updates.tone = analysis.tone as string;

        for (const [field, value] of Object.entries(updates)) {
          setBrief(field, value);
        }
        if (Object.keys(updates).length > 0) {
          await saveBrief();
        }
      }
    }

    // Phase 2: Validate
    setPhase("validating");
    const result = await validateBrief();
    setPhase("idle");

    if (result.length === 0) {
      const storeError = useLabStore.getState().error;
      if (storeError) {
        setLocalError(storeError);
      } else {
        setItems([{ type: "ok", message: "Brief wygląda dobrze — możesz przejść dalej." }]);
      }
    } else {
      setItems(result as ValidationItem[]);
    }
  };

  // Auto-run on mount
  useEffect(() => {
    if (storeProjectId && !startedRef.current) {
      startedRef.current = true;
      runFullFlow();
    }
    return () => { startedRef.current = false; };
  }, [storeProjectId]);

  const handleAccept = async (idx: number) => {
    const item = items[idx];
    if (!item.field) return;
    const text = editedSuggestions[idx] ?? item.suggestion ?? "";
    if (!text) return;
    setBrief(item.field, text);
    setAccepted((prev) => new Set(prev).add(idx));
    // Save to backend
    await saveBrief();
  };

  const handleDismiss = (idx: number) => {
    setDismissed((prev) => new Set(prev).add(idx));
  };

  const handleEditSuggestion = (idx: number, value: string) => {
    setEditedSuggestions((prev) => ({ ...prev, [idx]: value }));
  };

  const hasUnaddressedErrors = items.some(
    (item, idx) => item.type === "error" && !dismissed.has(idx) && !accepted.has(idx)
  );

  const iconMap = { ok: "✓", warning: "⚠", error: "✗" };

  const colorMap = {
    ok: "bg-green-50 border-green-200",
    warning: "bg-yellow-50 border-yellow-200",
    error: "bg-red-50 border-red-200",
  };

  const iconColorMap = {
    ok: "text-green-500",
    warning: "text-yellow-500",
    error: "text-red-500",
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-xl font-bold text-gray-800">Walidacja AI</h1>

      {/* Website analysis result */}
      {websiteAnalysis && !websiteAnalysis.error && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-indigo-500">🌐</span>
            <span className="text-sm font-medium text-indigo-700">Dane ze strony www</span>
          </div>
          {!!websiteAnalysis.summary && (
            <p className="text-sm text-indigo-600">{String(websiteAnalysis.summary)}</p>
          )}
          {!!websiteAnalysis.services && Array.isArray(websiteAnalysis.services) && (
            <div className="flex flex-wrap gap-1 mt-1">
              {(websiteAnalysis.services as string[]).slice(0, 6).map((s, i) => (
                <span key={i} className="text-xs bg-indigo-100 text-indigo-600 px-2 py-0.5 rounded">{s}</span>
              ))}
            </div>
          )}
          <p className="text-[10px] text-indigo-400">Puste pola briefu zostały automatycznie uzupełnione</p>
        </div>
      )}

      {/* Loading state */}
      {isGenerating && (
        <div className="text-center py-16">
          <div className="inline-flex items-center gap-3 bg-emerald-50 text-emerald-700 px-6 py-4 rounded-xl">
            <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span className="text-sm font-medium">
              {phase === "analyzing_website" ? "AI czyta stronę www..." : "AI analizuje Twój brief..."}
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-3">To może potrwać kilka sekund</p>
        </div>
      )}

      {/* Error state */}
      {!isGenerating && (localError || error) && items.length === 0 && (
        <div className="text-center py-12 space-y-4">
          <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-5 py-3 rounded-xl border border-red-200">
            <span>✗</span>
            <span className="text-sm">{localError || error}</span>
          </div>
          <div className="flex justify-center gap-3">
            <button
              onClick={runFullFlow}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700"
            >
              Spróbuj ponownie
            </button>
            <button
              onClick={() => navigate(`/lab/${projectId}/step/3`)}
              className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50"
            >
              Pomiń walidację →
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      {!isGenerating && items.length > 0 && (
        <>
          <p className="text-sm text-gray-500">
            AI przeanalizowało Twój brief:
          </p>

          <div className="space-y-4">
            {items.map((item, idx) => {
              const isAccepted = accepted.has(idx);
              const isDismissed = dismissed.has(idx);
              const isResolved = isAccepted || isDismissed;

              return (
                <div
                  key={idx}
                  className={`rounded-xl border transition-opacity ${colorMap[item.type]} ${
                    isResolved ? "opacity-40" : ""
                  }`}
                >
                  {/* Header row */}
                  <div className="flex items-start gap-3 p-4">
                    <span className={`text-lg mt-0.5 ${iconColorMap[item.type]}`}>
                      {iconMap[item.type]}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm text-gray-800">{item.message}</p>
                      {item.field && (
                        <span className="text-xs text-gray-500 mt-0.5 block">
                          {FIELD_LABELS[item.field] || item.field}
                        </span>
                      )}
                    </div>
                    {isAccepted && (
                      <span className="text-xs text-green-600 font-medium px-2 py-1 bg-green-100 rounded">
                        Zaakceptowano
                      </span>
                    )}
                    {isDismissed && (
                      <span className="text-xs text-gray-500 font-medium px-2 py-1 bg-gray-100 rounded">
                        Odrzucono
                      </span>
                    )}
                  </div>

                  {/* Suggestion area — only for warning/error with suggestion, not resolved */}
                  {!isResolved && item.type !== "ok" && item.suggestion && item.field && (
                    <div className="px-4 pb-4 space-y-3">
                      <div className="border-t border-gray-200/50 pt-3">
                        <label className="text-xs font-medium text-gray-600 block mb-1.5">
                          Propozycja AI:
                        </label>
                        <textarea
                          value={editedSuggestions[idx] ?? item.suggestion}
                          onChange={(e) => handleEditSuggestion(idx, e.target.value)}
                          rows={3}
                          className="w-full text-sm border border-gray-300 rounded-lg p-2.5 bg-white text-gray-800 resize-y focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                        />
                      </div>
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => handleDismiss(idx)}
                          className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-white text-gray-600"
                        >
                          Odrzuć
                        </button>
                        <button
                          onClick={() => handleAccept(idx)}
                          className="text-xs px-4 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                        >
                          Akceptuj
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Warning/error without suggestion — simple dismiss/go-back */}
                  {!isResolved && item.type !== "ok" && (!item.suggestion || !item.field) && (
                    <div className="px-4 pb-4 flex gap-2 justify-end">
                      <button
                        onClick={() => handleDismiss(idx)}
                        className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-white text-gray-600"
                      >
                        Zostaw
                      </button>
                      <button
                        onClick={() => navigate(`/lab/${projectId}/step/1`)}
                        className="text-xs px-3 py-1.5 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700 font-medium"
                      >
                        Popraw ręcznie
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* Navigation */}
      {!isGenerating && (
        <div className="flex justify-between pt-6">
          <button
            onClick={() => navigate(`/lab/${projectId}/step/1`)}
            className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700"
          >
            ← Wstecz
          </button>
          {items.length > 0 && (
            <button
              onClick={() => navigate(`/lab/${projectId}/step/3`)}
              disabled={hasUnaddressedErrors}
              className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            >
              Dalej → Struktura
            </button>
          )}
        </div>
      )}
    </div>
  );
}
