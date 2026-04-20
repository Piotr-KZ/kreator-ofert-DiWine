/**
 * MySites — list of user's creator projects.
 * Brief 36.
 */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDashboardStore } from "@/store/dashboardStore";
import * as api from "@/api/creator";
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
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [deletingSite, setDeletingSite] = useState<{ id: string; name: string } | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    loadSites();
  }, [loadSites]);

  const handleDelete = async () => {
    if (!deletingSite) return;
    setDeleteLoading(true);
    setDeleteError(null);
    try {
      await api.deleteProject(deletingSite.id);
      setDeletingSite(null);
      loadSites();
    } catch (err: any) {
      setDeleteError(err.response?.data?.detail || "Nie udalo sie usunac strony. Sprobuj ponownie.");
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleDuplicate = async (projectId: string) => {
    try {
      await api.duplicateProject(projectId);
      loadSites();
    } catch {
      // ignore
    }
  };

  const filteredSites = sites.filter((s) => {
    if (search && !s.name.toLowerCase().includes(search.toLowerCase())) return false;
    if (statusFilter && s.status !== statusFilter) return false;
    return true;
  });

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

      {/* Search & filter */}
      {sites.length > 0 && (
        <div className="flex gap-3 mb-4">
          <input
            type="text"
            placeholder="Szukaj projektu..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white"
          >
            <option value="">Wszystkie</option>
            <option value="draft">Szkice</option>
            <option value="published">Opublikowane</option>
          </select>
        </div>
      )}

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
              {filteredSites.map((site) => (
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
                    <div className="flex items-center justify-end gap-2">
                      <button
                        className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/creator/${site.id}/step/${site.current_step || 1}`);
                        }}
                      >
                        Edytuj
                      </button>
                      <button
                        className="text-sm text-gray-400 hover:text-gray-600"
                        title="Duplikuj"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDuplicate(site.id);
                        }}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                      <button
                        className="text-sm text-gray-400 hover:text-red-500"
                        title="Usun"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeletingSite({ id: site.id, name: site.name });
                        }}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredSites.length === 0 && sites.length > 0 && (
            <div className="text-center py-8 text-gray-400 text-sm">
              Brak wyników dla podanych filtrów
            </div>
          )}
        </div>
      )}

      {/* Delete confirmation modal */}
      {deletingSite && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl shadow-xl max-w-sm w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Usun strone</h3>
            <p className="text-sm text-gray-600 mb-1">
              Czy na pewno chcesz usunac strone <strong>{deletingSite.name}</strong>?
            </p>
            <p className="text-xs text-gray-400 mb-5">Tej operacji nie mozna cofnac.</p>
            {deleteError && (
              <div className="bg-red-50 text-red-700 text-sm px-3 py-2 rounded-lg mb-4">{deleteError}</div>
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => { setDeletingSite(null); setDeleteError(null); }}
                disabled={deleteLoading}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Anuluj
              </button>
              <button
                onClick={handleDelete}
                disabled={deleteLoading}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {deleteLoading && (
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                )}
                Usun
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
