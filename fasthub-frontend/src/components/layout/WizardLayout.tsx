import React from "react";
import { APP_CONFIG } from "@/config/app.config";

interface Step {
  id: string;
  name: string;
}

interface WizardLayoutProps {
  steps: Step[];
  currentStep: number;
  projectName?: string;
  onBack?: () => void;
  onSave?: () => void;
  children: React.ReactNode;
}

export default function WizardLayout({
  steps,
  currentStep,
  projectName,
  onBack,
  onSave,
  children,
}: WizardLayoutProps) {
  return (
    <div className="h-screen flex flex-col bg-gray-50" style={{ fontFamily: APP_CONFIG.theme.fontFamily }}>
      {/* Header */}
      <nav className="bg-gray-950 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          {onBack && (
            <button onClick={onBack} className="text-gray-400 hover:text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
          )}
          <div className="flex items-center gap-2.5">
            <div className={`w-7 h-7 rounded-lg bg-gradient-to-br ${APP_CONFIG.logo.gradient} flex items-center justify-center`}>
              <span className="text-white font-extrabold text-xs">{APP_CONFIG.logo.icon}</span>
            </div>
            <span className="text-white font-bold">{APP_CONFIG.name}</span>
          </div>
          {projectName && (
            <>
              <span className="text-gray-600">/</span>
              <span className="text-gray-300 text-sm">{projectName}</span>
            </>
          )}
        </div>
        {onSave && (
          <button
            onClick={onSave}
            className="px-4 py-1.5 text-sm bg-white/10 text-white rounded-lg hover:bg-white/20 font-medium"
          >
            Save draft
          </button>
        )}
      </nav>

      {/* Steps bar */}
      <div className="bg-white border-b px-4 py-2.5 flex items-center gap-0.5 overflow-x-auto flex-shrink-0">
        {steps.map((s, i) => (
          <div key={s.id} className="flex items-center">
            {i > 0 && <div className="w-4 h-px bg-gray-200 mx-0.5" />}
            <div
              className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs whitespace-nowrap ${
                i + 1 === currentStep
                  ? "bg-indigo-50 text-indigo-700 font-semibold"
                  : i + 1 < currentStep
                  ? "text-green-600"
                  : "text-gray-400"
              }`}
            >
              <div
                className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                  i + 1 === currentStep
                    ? "bg-indigo-600 text-white"
                    : i + 1 < currentStep
                    ? "bg-green-500 text-white"
                    : "bg-gray-200"
                }`}
              >
                {i + 1 < currentStep ? "\u2713" : i + 1}
              </div>
              {s.name}
            </div>
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8">{children}</div>
    </div>
  );
}
