import { useEffect } from "react";
import { Outlet, useParams, useNavigate, useLocation } from "react-router-dom";
import { useLabStore } from "@/store/labStore";

const STEPS = [
  { num: 1, label: "Brief + Styl" },
  { num: 2, label: "Struktura" },
  { num: 3, label: "Visual Concept" },
  { num: 4, label: "Tresci + Podglad" },
  { num: 5, label: "Gotowa strona" },
];

export default function LabLayout() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { loadProject, isLoading, projectName } = useLabStore();

  useEffect(() => {
    if (projectId) loadProject(projectId);
  }, [projectId]);

  // Current step from URL
  const stepMatch = location.pathname.match(/step\/(\d)/);
  const currentStep = stepMatch ? parseInt(stepMatch[1]) : 1;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-400">Ladowanie projektu...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top bar */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-emerald-600">LC</span>
          <span className="text-sm text-gray-600">{projectName}</span>
        </div>
        <button
          onClick={() => navigate("/lab/create")}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          Nowy projekt
        </button>
      </header>

      {/* Step bar */}
      <nav className="bg-white border-b border-gray-100 px-6">
        <div className="max-w-4xl mx-auto flex">
          {STEPS.map((step) => (
            <button
              key={step.num}
              onClick={() => navigate(`/lab/${projectId}/step/${step.num}`)}
              className={`flex-1 py-3 text-xs font-medium border-b-2 transition-colors ${
                currentStep === step.num
                  ? "border-emerald-500 text-emerald-700"
                  : "border-transparent text-gray-400 hover:text-gray-600"
              }`}
            >
              <span className="mr-1.5">{step.num}.</span>
              {step.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
