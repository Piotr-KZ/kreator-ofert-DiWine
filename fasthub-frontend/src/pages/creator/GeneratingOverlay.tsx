/**
 * GeneratingOverlay — fullscreen progress screen during AI site generation.
 * Brief 34: SSE progress → checklist → redirect to Step 5.
 */

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useCreatorStore } from "@/store/creatorStore";
import Btn from "@/components/ui/Btn";

interface ProgressStep {
  label: string;
  status: "pending" | "active" | "done";
}

const INITIAL_STEPS: ProgressStep[] = [
  { label: "Projektowanie struktury strony", status: "pending" },
  { label: "Tworzenie treści", status: "pending" },
  { label: "Dopieszczanie szczegółów", status: "pending" },
];

function getStepsFromProgress(progress: number): ProgressStep[] {
  if (progress >= 100) {
    return INITIAL_STEPS.map((s) => ({ ...s, status: "done" }));
  }
  if (progress >= 40) {
    return [
      { ...INITIAL_STEPS[0], status: "done" },
      { ...INITIAL_STEPS[1], status: "active" },
      { ...INITIAL_STEPS[2], status: "pending" },
    ];
  }
  if (progress >= 10) {
    return [
      { ...INITIAL_STEPS[0], status: "active" },
      { ...INITIAL_STEPS[1], status: "pending" },
      { ...INITIAL_STEPS[2], status: "pending" },
    ];
  }
  return INITIAL_STEPS;
}

export default function GeneratingOverlay() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { generateSite, generateProgress, isGenerating } = useCreatorStore();
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (started) return;
    setStarted(true);

    generateSite().then((success) => {
      if (success) {
        navigate(`/creator/${projectId}/step/5`, { replace: true });
      } else {
        setError("Wystąpił błąd podczas generowania strony.");
      }
    });
  }, []);

  const progress = generateProgress?.progress ?? 0;
  const message = generateProgress?.message ?? "Przygotowuję...";
  const steps = getStepsFromProgress(progress);

  const handleRetry = () => {
    setError(null);
    setStarted(false);
  };

  return (
    <div className="fixed inset-0 z-50 bg-gray-950 flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        {/* Icon */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-indigo-600 flex items-center justify-center">
            <svg className="w-8 h-8 text-white animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">AI buduje Twoja strone</h1>
          <p className="text-gray-400 text-sm">{message}</p>
        </div>

        {error ? (
          <div className="text-center">
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
            <Btn onClick={handleRetry}>Sprobuj ponownie</Btn>
          </div>
        ) : (
          <>
            {/* Progress bar */}
            <div className="mb-8">
              <div className="flex justify-between text-sm text-gray-400 mb-2">
                <span>Postep</span>
                <span>{progress}%</span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-500 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Steps checklist */}
            <div className="space-y-3">
              {steps.map((step, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="flex-shrink-0">
                    {step.status === "done" ? (
                      <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
                        <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" strokeWidth={3} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    ) : step.status === "active" ? (
                      <div className="w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center">
                        <svg className="w-3.5 h-3.5 text-white animate-spin" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                      </div>
                    ) : (
                      <div className="w-6 h-6 rounded-full border-2 border-gray-700" />
                    )}
                  </div>
                  <span className={`text-sm ${step.status === "done" ? "text-green-400" : step.status === "active" ? "text-white" : "text-gray-600"}`}>
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
