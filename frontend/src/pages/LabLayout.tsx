import { useEffect } from "react";
import { Outlet, useParams, useNavigate, useLocation } from "react-router-dom";
import { useLabStore } from "@/store/labStore";

const STEPS_WEB = [
  { num: 1, label: "Brief + Styl" },
  { num: 2, label: "Walidacja AI" },
  { num: 3, label: "Kreator" },
  { num: 4, label: "Treści" },
  { num: 5, label: "Wizualizacja" },
];

const STEPS_OFFER = [
  { num: 5, label: "Edycja oferty" },
];

export default function LabLayout() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { loadProject, isLoading, projectName, siteType, brief } = useLabStore();

  useEffect(() => {
    if (projectId) loadProject(projectId);
  }, [projectId]);

  const stepMatch = location.pathname.match(/step\/(\d)/);
  const currentStep = stepMatch ? parseInt(stepMatch[1]) : 1;
  const isOffer = siteType === 'offer';
  const steps = isOffer ? STEPS_OFFER : STEPS_WEB;

  // For offers, extract offer info from brief
  const offerNumber = (brief as any)?.offer_number || '';
  const offerId = (brief as any)?.offer_id || '';

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-400">Ładowanie projektu...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top bar */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {isOffer ? (
            <>
              <span className="text-lg font-bold text-indigo-600">LC</span>
              <span className="text-sm font-semibold text-gray-800">
                Oferta {offerNumber}
              </span>
            </>
          ) : (
            <>
              <span className="text-lg font-bold text-emerald-600">LC</span>
              <span className="text-sm text-gray-600">{projectName}</span>
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          {isOffer && offerId && (
            <>
              <button
                onClick={() => navigate(`/offer/${offerId}/cost`)}
                className="text-xs text-gray-400 hover:text-gray-600 px-2 py-1"
              >
                ← Kosztorys
              </button>
              <button
                onClick={() => navigate(`/offer/${offerId}/export`)}
                className="text-xs bg-indigo-600 text-white px-3 py-1.5 rounded-lg font-semibold hover:bg-indigo-700"
              >
                Eksport oferty →
              </button>
            </>
          )}
          {!isOffer && (
            <button
              onClick={() => navigate("/lab/create")}
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              Nowy projekt
            </button>
          )}
        </div>
      </header>

      {/* Step bar — for offers show only "Edycja oferty", for web show all 5 */}
      <nav className="bg-white border-b border-gray-100 px-6">
        <div className="max-w-4xl mx-auto flex">
          {steps.map((step) => (
            <button
              key={step.num}
              onClick={() => navigate(`/lab/${projectId}/step/${step.num}`)}
              className={`flex-1 py-3 text-xs font-medium border-b-2 transition-colors ${
                currentStep === step.num
                  ? "border-emerald-500 text-emerald-700"
                  : "border-transparent text-gray-400 hover:text-gray-600"
              }`}
            >
              {step.num}. {step.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1">
        <Outlet />
      </div>
    </div>
  );
}
