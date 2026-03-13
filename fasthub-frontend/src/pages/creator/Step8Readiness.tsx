/**
 * Step8Readiness — readiness check page with checklist.
 * Brief 35: step 8.
 */

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useCreatorStore } from "@/store/creatorStore";
import type { ReadinessResult } from "@/types/creator";

const STATUS_ICON: Record<string, { icon: string; color: string }> = {
  pass: { icon: "✓", color: "text-green-600 bg-green-50" },
  warn: { icon: "!", color: "text-amber-600 bg-amber-50" },
  error: { icon: "✗", color: "text-red-600 bg-red-50" },
};

export default function Step8Readiness() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { readinessChecks, isValidating, runReadinessCheck } = useCreatorStore();

  const [result, setResult] = useState<ReadinessResult | null>(null);

  useEffect(() => {
    handleCheck();
  }, []);

  const handleCheck = async () => {
    const res = await runReadinessCheck();
    if (res) setResult(res);
  };

  const passed = readinessChecks.filter((c) => c.status === "pass").length;
  const total = readinessChecks.length;
  const hasErrors = readinessChecks.some((c) => c.status === "error");

  const handleFix = (fixTab?: string) => {
    if (fixTab) {
      navigate(`/creator/${projectId}/step/7`);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Sprawdzenie gotowości</h1>
      <p className="text-gray-500 text-sm mb-6">Przed publikacją sprawdzamy wszystko</p>

      {/* Score summary */}
      {total > 0 && (
        <div className={`rounded-xl p-6 mb-6 text-center ${hasErrors ? "bg-red-50" : "bg-green-50"}`}>
          <div className={`text-4xl font-bold ${hasErrors ? "text-red-600" : "text-green-600"}`}>
            {passed}/{total}
          </div>
          <p className={`text-sm mt-1 ${hasErrors ? "text-red-600" : "text-green-600"}`}>
            {hasErrors
              ? "Wymagane poprawki przed publikacją"
              : "Strona gotowa do publikacji!"}
          </p>
        </div>
      )}

      {/* Checklist */}
      <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        {isValidating && readinessChecks.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <svg className="animate-spin h-5 w-5 mx-auto mb-2" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Sprawdzam...
          </div>
        ) : (
          readinessChecks.map((check) => {
            const status = STATUS_ICON[check.status] || STATUS_ICON.warn;
            return (
              <div key={check.key} className="flex items-start gap-3 p-4">
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${status.color}`}>
                  {status.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{check.message}</p>
                  {check.suggestion && (
                    <p className="text-xs text-gray-500 mt-0.5">{check.suggestion}</p>
                  )}
                </div>
                {check.fix_tab && check.status !== "pass" && (
                  <button
                    onClick={() => handleFix(check.fix_tab)}
                    className="text-xs text-indigo-600 hover:text-indigo-700 whitespace-nowrap"
                  >
                    Popraw →
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-between mt-6">
        <button onClick={() => navigate(`/creator/${projectId}/step/7`)}
          className="px-6 py-2.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">
          Wstecz
        </button>
        <div className="flex gap-3">
          <button onClick={handleCheck} disabled={isValidating}
            className="px-4 py-2.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50">
            {isValidating ? "Sprawdzam..." : "Sprawdź ponownie"}
          </button>
          <button
            onClick={() => navigate(`/creator/${projectId}/step/9`)}
            disabled={hasErrors}
            className="px-6 py-2.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Publikuję!
          </button>
        </div>
      </div>
    </div>
  );
}
