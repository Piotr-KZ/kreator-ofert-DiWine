/**
 * IntegrationsGlobal — full integrations marketplace page.
 * Brief 36.
 */

import { useEffect, useState } from "react";
import { useDashboardStore } from "@/store/dashboardStore";

const CATEGORY_ICONS: Record<string, string> = {
  analytics: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  email_marketing: "M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
  crm: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
  chat: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
  social_ads: "M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z",
  reservations: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
  automation: "M13 10V3L4 14h7v7l9-11h-7z",
  payments: "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z",
  other: "M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4",
};

export default function IntegrationsGlobal() {
  const { catalog, loadCatalog } = useDashboardStore();
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  const filtered = activeCategory
    ? catalog.filter((c) => c.category === activeCategory)
    : catalog;

  return (
    <div className="flex h-full">
      {/* Sidebar — categories */}
      <aside className="w-56 bg-white border-r border-gray-200 p-4 overflow-auto flex-shrink-0 hidden lg:block">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Kategorie</h3>
        <div className="space-y-0.5">
          <button
            onClick={() => setActiveCategory(null)}
            className={`w-full text-left flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
              !activeCategory ? "bg-indigo-50 text-indigo-700 font-medium" : "text-gray-600 hover:bg-gray-50"
            }`}
          >
            Wszystkie
          </button>
          {catalog.map((cat) => (
            <button
              key={cat.category}
              onClick={() => setActiveCategory(cat.category)}
              className={`w-full text-left flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                activeCategory === cat.category
                  ? "bg-indigo-50 text-indigo-700 font-medium"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={CATEGORY_ICONS[cat.category] || CATEGORY_ICONS.other} />
              </svg>
              {cat.category_name}
            </button>
          ))}
        </div>
      </aside>

      {/* Main grid */}
      <div className="flex-1 overflow-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Marketplace integracji</h1>
          <p className="text-sm text-gray-500 mt-1">
            Połącz swoją stronę z narzędziami, które pomogą Ci rozwijać biznes
          </p>
        </div>

        {/* AI banner */}
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-xl p-5 mb-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-indigo-800">Pakiet AI — dopasowany do Twojej branży</h3>
              <p className="text-sm text-indigo-700 mt-1">
                Nasz AI dobierze zestaw integracji idealnie dopasowany do Twojego biznesu. Skonfiguruj wszystko jednym kliknięciem.
              </p>
            </div>
          </div>
        </div>

        {/* Integration cards */}
        {filtered.map((cat) => (
          <div key={cat.category} className="mb-8">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">{cat.category_name}</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {cat.items.map((item) => (
                <div
                  key={item.provider}
                  className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-200 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="text-sm font-semibold text-gray-900">{item.name}</h4>
                    {item.v2 && (
                      <span className="text-[10px] px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded font-medium">
                        V2
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mb-3">{item.description}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">
                      {item.difficulty}
                    </span>
                    <span className="text-[10px] text-gray-400">{item.price}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
