/**
 * MySites — list of user's creator projects.
 * Brief 36.
 */

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDashboardStore } from "@/store/dashboardStore";
import StatusBadge from "@/components/ui/StatusBadge";

const STEP_LABELS: Record<number, string> = {
  1: "Brief",
  2: "Materiały",
  3: "Styl",
  4: "Walidacja",
  5: "Wireframe",
  6: "Podgląd",
  7: "Konfiguracja",
  8: "Gotowość",
  9: "Publikacja",
};

function statusVariant(status: string): "success" | "warning" | "neutral" | "info" {
  if (status === "published") return "success";
  if (status === "draft") return "info";
  return "neutral";
}

function statusLabel(status: string): string {
  if (status === "published") return "Opublikowana";
  if (status === "draft") return "Szkic";
  return status;
}

export default function MySites() {
  const navigate = useNavigate();
  const { sites, loading, error, loadSites } = useDashboardStore();

  useEffect(() => {
    loadSites();
  }, [loadSites]);

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Moje strony</h1>
        <button
          onClick={() => navigate("/creator/new")}
          className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-5 py-2 rounded-lg font-medium transition-colors"
        >
          + Utwórz nową stronę
        </button>
      </div>

      {loading && (
        <div className="text-center py-16 text-gray-400">Ładowanie...</div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>
      )}

      {!loading && sites.length === 0 && (
        <div className="text-center py-20">
          <div className="text-5xl mb-4 text-gray-300">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
          </div>
          <p className="text-gray-500 mb-4">Nie masz jeszcze żadnych stron</p>
          <button
            onClick={() => navigate("/creator/new")}
            className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-5 py-2 rounded-lg font-medium"
          >
            Utwórz pierwszą stronę
          </button>
        </div>
      )}

      {!loading && sites.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Nazwa</th>
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Postęp</th>
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Status</th>
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Domena</th>
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Data</th>
                <th className="text-right text-xs font-medium text-gray-500 px-5 py-3">Akcje</th>
              </tr>
            </thead>
            <tbody>
              {sites.map((site) => (
                <tr
                  key={site.id}
                  className="border-b border-gray-50 hover:bg-gray-50/50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/panel/sites/${site.id}`)}
                >
                  <td className="px-5 py-3.5">
                    <div className="font-medium text-gray-900 text-sm">{site.name}</div>
                    {site.site_type && (
                      <div className="text-xs text-gray-400 mt-0.5">{site.site_type}</div>
                    )}
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 rounded-full transition-all"
                          style={{ width: `${((site.current_step || 1) / 9) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {STEP_LABELS[site.current_step] || `Krok ${site.current_step}`}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge variant={statusVariant(site.status)}>
                      {statusLabel(site.status)}
                    </StatusBadge>
                  </td>
                  <td className="px-5 py-3.5">
                    {site.domain ? (
                      <a
                        href={`https://${site.domain}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm text-indigo-600 hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {site.domain}
                      </a>
                    ) : (
                      <span className="text-xs text-gray-400">—</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-sm text-gray-500">
                    {new Date(site.created_at).toLocaleDateString("pl-PL")}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <button
                      className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/creator/${site.id}/step/${site.current_step || 1}`);
                      }}
                    >
                      Edytuj
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
