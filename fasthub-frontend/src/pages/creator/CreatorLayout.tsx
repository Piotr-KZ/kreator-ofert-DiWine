/**
 * CreatorLayout — wrapper with dark header + step bar + content area.
 * Brief 32: routing /creator/:projectId/step/:n
 */

import { useEffect } from "react";
import { Outlet, useNavigate, useParams } from "react-router-dom";
import { useCreatorStore } from "@/store/creatorStore";

const STEPS = [
  { id: 1, name: "O firmie" },
  { id: 2, name: "Materiały" },
  { id: 3, name: "Styl wizualny" },
  { id: 4, name: "Walidacja AI" },
  { id: 5, name: "Struktura" },
  { id: 6, name: "Podgląd" },
  { id: 7, name: "Konfiguracja" },
  { id: 8, name: "Sprawdzenie" },
  { id: 9, name: "Publikacja" },
];

export default function CreatorLayout() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { project, isLoading, isSaving, lastSavedAt, currentStep, loadProject, saveBrief } =
    useCreatorStore();

  useEffect(() => {
    if (projectId) loadProject(projectId);
  }, [projectId]);

  const handleStepClick = (stepId: number) => {
    if (stepId > currentStep) return; // can't skip ahead
    navigate(`/creator/${projectId}/step/${stepId}`);
  };

  const handleSave = async () => {
    await saveBrief();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex items-center gap-3 text-gray-500">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Ładowanie projektu...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Dark header */}
      <header className="bg-gray-950 text-white px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate("/panel")}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="font-semibold text-sm">WebCreator</span>
          <span className="text-gray-500">/</span>
          <span className="text-gray-300 text-sm">{project?.name || "Nowy projekt"}</span>
        </div>
        <div className="flex items-center gap-3">
          {lastSavedAt && (
            <span className="text-xs text-gray-500">
              Ostatni zapis: {lastSavedAt.toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" })}
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-1.5 text-sm rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors disabled:opacity-50"
          >
            {isSaving ? "Zapisuję..." : "Zapisz szkic"}
          </button>
        </div>
      </header>

      {/* Step bar */}
      <nav className="bg-white border-b border-gray-200 px-6 py-2 flex-shrink-0 overflow-x-auto">
        <div className="flex items-center gap-1 min-w-max">
          {STEPS.map((step) => {
            const isActive = step.id === currentStep;
            const isCompleted = step.id < currentStep;
            const isDisabled = step.id > currentStep;

            return (
              <button
                key={step.id}
                onClick={() => handleStepClick(step.id)}
                disabled={isDisabled}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : isCompleted
                      ? "text-green-700 hover:bg-green-50 cursor-pointer"
                      : "text-gray-400 cursor-not-allowed"
                }`}
              >
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 ${
                    isActive
                      ? "bg-indigo-600 text-white"
                      : isCompleted
                        ? "bg-green-500 text-white"
                        : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {isCompleted ? (
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={3} viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    step.id
                  )}
                </span>
                <span className="hidden sm:inline">{step.name}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Content area */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
