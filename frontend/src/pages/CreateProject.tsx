import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLabStore } from "@/store/labStore";
import * as api from "@/api/client";

interface SiteType {
  value: string;
  label: string;
}

const FALLBACK_SITE_TYPES: SiteType[] = [
  { value: 'company_card', label: 'Strona firmowa' },
  { value: 'portfolio', label: 'Portfolio' },
  { value: 'landing', label: 'Landing page' },
];

export default function CreateProject() {
  const navigate = useNavigate();
  const createProject = useLabStore((s) => s.createProject);
  const [name, setName] = useState("");
  const [siteType, setSiteType] = useState("company_card");
  const [siteTypes, setSiteTypes] = useState<SiteType[]>(FALLBACK_SITE_TYPES);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listSiteTypes().then(({ data }) => {
      if (data?.length) setSiteTypes(data);
    }).catch(() => {/* zostają fallbacki */});
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const id = await createProject(name.trim(), siteType);
      navigate(`/lab/${id}/step/1`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Błąd połączenia z backendem — sprawdź czy serwer działa");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md space-y-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-emerald-600 mb-1">Lab Creator</div>
          <p className="text-sm text-gray-500">Narzedzie testowe do generowania stron</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nazwa projektu
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="np. Firma XYZ"
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-emerald-400"
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Typ strony
            </label>
            <select
              value={siteType}
              onChange={(e) => setSiteType(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-emerald-400 bg-white"
            >
              {siteTypes.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 rounded-xl px-4 py-2">{error}</p>
        )}

        <button
          onClick={handleCreate}
          disabled={!name.trim() || loading}
          className="w-full py-3 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Tworzenie..." : "Stworz projekt"}
        </button>
      </div>
    </div>
  );
}
