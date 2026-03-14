/**
 * SiteDashboard — per-site management with 5 tabs.
 * Brief 36: Statystyki, Integracje, Automatyzacje, Formularze, SEO.
 */

import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useDashboardStore } from "@/store/dashboardStore";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import StatusBadge from "@/components/ui/StatusBadge";
import Modal from "@/components/shared/Modal";
import Btn from "@/components/ui/Btn";
import type {
  IntegrationCatalogItem,
  IntegrationCategory,
  FormSubmission,
} from "@/types/creator";

type Tab = "stats" | "integrations" | "automations" | "forms" | "seo";

const TABS: { id: Tab; label: string }[] = [
  { id: "stats", label: "Statystyki" },
  { id: "integrations", label: "Integracje" },
  { id: "automations", label: "Automatyzacje" },
  { id: "forms", label: "Formularze" },
  { id: "seo", label: "SEO" },
];

export default function SiteDashboard() {
  const { siteId } = useParams<{ siteId: string }>();
  const navigate = useNavigate();
  const {
    sites, stats, integrations, catalog, automations, submissions,
    activeTab, setActiveTab,
    loadSites, loadStats, loadIntegrations, loadCatalog, loadAutomations, loadSubmissions,
    doConnect, doDisconnect, markRead,
  } = useDashboardStore();

  const site = sites.find((s) => s.id === siteId);

  useEffect(() => {
    if (sites.length === 0) loadSites();
  }, [sites.length, loadSites]);

  useEffect(() => {
    if (!siteId) return;
    loadStats(siteId);
    loadIntegrations(siteId);
    loadCatalog();
    loadAutomations();
    loadSubmissions(siteId);
  }, [siteId, loadStats, loadIntegrations, loadCatalog, loadAutomations, loadSubmissions]);

  if (!siteId) return null;

  return (
    <div className="flex h-full" data-testid="site-dashboard">
      {/* Sidebar — site list */}
      <aside className="w-56 bg-white border-r border-gray-200 p-4 overflow-auto flex-shrink-0 hidden lg:block">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Strony</h3>
        <div className="space-y-1">
          {sites.map((s) => (
            <button
              key={s.id}
              onClick={() => navigate(`/panel/sites/${s.id}`)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                s.id === siteId
                  ? "bg-indigo-50 text-indigo-700 font-medium"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              {s.name}
            </button>
          ))}
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">{site?.name || "Strona"}</h1>
              {site?.domain && (
                <a
                  href={`https://${site.domain}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm text-indigo-600 hover:underline"
                >
                  {site.domain}
                </a>
              )}
            </div>
            <div className="flex gap-2">
              <Link
                to={`/creator/${siteId}/step/${site?.current_step || 1}`}
                className="text-sm px-4 py-2 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 font-medium"
              >
                Edytuj stronę
              </Link>
              {site?.domain && (
                <a
                  href={`https://${site.domain}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 font-medium"
                >
                  Otwórz stronę
                </a>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 mt-4">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab content */}
        <div className="p-6">
          {activeTab === "stats" && <TabStats />}
          {activeTab === "integrations" && (
            <TabIntegrations
              siteId={siteId}
              catalog={catalog}
              connected={integrations}
              onConnect={doConnect}
              onDisconnect={doDisconnect}
            />
          )}
          {activeTab === "automations" && <TabAutomations />}
          {activeTab === "forms" && (
            <TabForms
              siteId={siteId}
              submissions={submissions}
              onMarkRead={markRead}
            />
          )}
          {activeTab === "seo" && <TabSeo site={site} />}
        </div>
      </div>
    </div>
  );
}

// ─── Tab: Statystyki ───

function TabStats() {
  const { stats } = useDashboardStore();
  const [period, setPeriod] = useState("30d");
  const { siteId } = useParams<{ siteId: string }>();
  const { loadStats } = useDashboardStore();

  const handlePeriod = (p: string) => {
    setPeriod(p);
    if (siteId) loadStats(siteId, p);
  };

  const kpis = [
    { label: "Odwiedzający", value: stats?.visitors ?? 0, icon: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" },
    { label: "Leady", value: stats?.leads ?? 0, icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
    { label: "Bounce rate", value: stats?.bounce_rate != null ? `${stats.bounce_rate}%` : "—", icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" },
    { label: "Online od", value: stats?.published_at ? new Date(stats.published_at).toLocaleDateString("pl-PL") : "—", icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" },
  ];

  return (
    <div>
      {/* Period selector */}
      <div className="flex gap-2 mb-6">
        {["7d", "30d", "90d"].map((p) => (
          <button
            key={p}
            onClick={() => handlePeriod(p)}
            className={`text-xs px-3 py-1 rounded-full font-medium transition-colors ${
              period === p ? "bg-indigo-100 text-indigo-700" : "bg-gray-100 text-gray-500 hover:bg-gray-200"
            }`}
          >
            {p === "7d" ? "7 dni" : p === "30d" ? "30 dni" : "90 dni"}
          </button>
        ))}
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-9 h-9 bg-indigo-50 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={kpi.icon} />
                </svg>
              </div>
              <span className="text-xs text-gray-500 font-medium">{kpi.label}</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Chart */}
      {stats?.daily_visitors && stats.daily_visitors.length > 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Odwiedzający dziennie</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stats.daily_visitors}>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#4F46E5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
          <p className="text-gray-400 text-sm">Dane o odwiedzających będą dostępne po wdrożeniu trackingu (Brief 38)</p>
        </div>
      )}
    </div>
  );
}

// ─── Tab: Integracje ───

function TabIntegrations({
  siteId,
  catalog,
  connected,
  onConnect,
  onDisconnect,
}: {
  siteId: string;
  catalog: IntegrationCategory[];
  connected: { id: string; provider: string; status: string }[];
  onConnect: (pid: string, provider: string, cfg: Record<string, string>) => Promise<void>;
  onDisconnect: (pid: string, id: string) => Promise<void>;
}) {
  const [modalItem, setModalItem] = useState<IntegrationCatalogItem | null>(null);
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);

  const connectedProviders = new Set(connected.map((c) => c.provider));

  const handleConnect = async () => {
    if (!modalItem) return;
    setSaving(true);
    try {
      await onConnect(siteId, modalItem.provider, formValues);
      setModalItem(null);
      setFormValues({});
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      {/* AI recommendation */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-xl p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-indigo-800">Rekomendacja AI</h3>
            <p className="text-sm text-indigo-700 mt-1">
              Na podstawie Twojej branży rekomendujemy: Google Analytics + Tidio Chat + Calendly.
              Te integracje pomogą śledzić ruch, obsługiwać klientów i przyjmować rezerwacje.
            </p>
          </div>
        </div>
      </div>

      {/* Categories + items */}
      {catalog.map((cat) => (
        <div key={cat.category} className="mb-8">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">{cat.category_name}</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {cat.items.map((item) => {
              const isConnected = connectedProviders.has(item.provider);
              const connItem = connected.find((c) => c.provider === item.provider);
              return (
                <div
                  key={item.provider}
                  className={`bg-white rounded-xl border p-4 transition-colors ${
                    isConnected ? "border-green-200 bg-green-50/30" : "border-gray-200"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-semibold text-gray-900">{item.name}</h4>
                        {item.v2 && (
                          <span className="text-[10px] px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded font-medium">
                            V2
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{item.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-[10px] px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">
                          {item.difficulty}
                        </span>
                        <span className="text-[10px] text-gray-400">{item.price}</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    {isConnected ? (
                      <div className="flex items-center justify-between">
                        <StatusBadge variant="success">Połączono</StatusBadge>
                        <button
                          onClick={() => connItem && onDisconnect(siteId, connItem.id)}
                          className="text-xs text-red-500 hover:text-red-700"
                        >
                          Odłącz
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => {
                          setModalItem(item);
                          setFormValues({});
                        }}
                        className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                        disabled={!!item.v2}
                      >
                        {item.v2 ? "Wkrótce" : "Połącz"}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}

      {/* Connect modal */}
      <Modal
        open={!!modalItem}
        onClose={() => setModalItem(null)}
        title={`Połącz ${modalItem?.name}`}
        footer={
          <div className="flex gap-2 justify-end">
            <Btn variant="secondary" onClick={() => setModalItem(null)}>Anuluj</Btn>
            <Btn variant="primary" onClick={handleConnect} loading={saving}>Połącz</Btn>
          </div>
        }
      >
        {modalItem && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">{modalItem.description}</p>
            {modalItem.fields.map((field) => (
              <div key={field.id}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{field.label}</label>
                <input
                  type="text"
                  placeholder={field.placeholder}
                  value={formValues[field.id] || ""}
                  onChange={(e) => setFormValues({ ...formValues, [field.id]: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
}

// ─── Tab: Automatyzacje ───

function TabAutomations() {
  const { automations } = useDashboardStore();
  const [enabled, setEnabled] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    const next = new Set(enabled);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setEnabled(next);
  };

  return (
    <div>
      {/* AutoFlow banner */}
      <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-100 rounded-xl p-5 mb-6">
        <h3 className="text-sm font-semibold text-emerald-800">AutoFlow — Automatyzacja w pakiecie</h3>
        <p className="text-sm text-emerald-700 mt-1">
          130+ systemów w automatyczne procesy biznesowe. Natywne automatyzacje działają od razu, zewnętrzne wymagają połączenia z Zapier/Make.
        </p>
      </div>

      {automations.map((group) => (
        <div key={group.group} className="mb-8">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">{group.group_name}</h3>
          <div className="space-y-2">
            {group.templates.map((tmpl) => (
              <div
                key={tmpl.id}
                className="bg-white rounded-xl border border-gray-200 px-5 py-3 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900">{tmpl.name}</p>
                      {tmpl.native && (
                        <span className="text-[10px] px-1.5 py-0.5 bg-emerald-100 text-emerald-700 rounded font-medium">
                          natywna
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">{tmpl.description}</p>
                  </div>
                </div>
                <button
                  onClick={() => toggle(tmpl.id)}
                  className={`w-10 h-5 rounded-full transition-colors flex-shrink-0 relative ${
                    enabled.has(tmpl.id) ? "bg-emerald-500" : "bg-gray-300"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                      enabled.has(tmpl.id) ? "translate-x-5" : "translate-x-0.5"
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Tab: Formularze ───

function TabForms({
  siteId,
  submissions,
  onMarkRead,
}: {
  siteId: string;
  submissions: FormSubmission[];
  onMarkRead: (pid: string, sid: string, read: boolean) => Promise<void>;
}) {
  const [selected, setSelected] = useState<FormSubmission | null>(null);

  return (
    <div>
      {submissions.length === 0 ? (
        <div className="text-center py-16">
          <svg className="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-400 text-sm">Brak zgłoszeń z formularzy</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/50">
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Status</th>
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Dane</th>
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">IP</th>
                <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Data</th>
                <th className="text-right text-xs font-medium text-gray-500 px-5 py-3">Akcje</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub) => (
                <tr
                  key={sub.id}
                  className={`border-b border-gray-50 hover:bg-gray-50/50 cursor-pointer transition-colors ${
                    !sub.read ? "bg-indigo-50/30" : ""
                  }`}
                  onClick={() => setSelected(sub)}
                >
                  <td className="px-5 py-3">
                    <StatusBadge variant={sub.read ? "neutral" : "info"}>
                      {sub.read ? "Przeczytane" : "Nowe"}
                    </StatusBadge>
                  </td>
                  <td className="px-5 py-3">
                    <p className="text-sm text-gray-700 truncate max-w-xs">
                      {Object.entries(sub.data_json || {}).map(([k, v]) => `${k}: ${v}`).join(", ")}
                    </p>
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-500">{sub.ip || "—"}</td>
                  <td className="px-5 py-3 text-sm text-gray-500">
                    {new Date(sub.created_at).toLocaleDateString("pl-PL")}
                  </td>
                  <td className="px-5 py-3 text-right">
                    {!sub.read && (
                      <button
                        className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                        onClick={(e) => {
                          e.stopPropagation();
                          onMarkRead(siteId, sub.id, true);
                        }}
                      >
                        Oznacz jako przeczytane
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail modal */}
      <Modal
        open={!!selected}
        onClose={() => setSelected(null)}
        title="Szczegóły zgłoszenia"
      >
        {selected && (
          <div className="space-y-3">
            {Object.entries(selected.data_json || {}).map(([key, value]) => (
              <div key={key}>
                <label className="text-xs font-medium text-gray-500 uppercase">{key}</label>
                <p className="text-sm text-gray-900 mt-0.5">{String(value)}</p>
              </div>
            ))}
            <hr className="border-gray-200" />
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>IP: {selected.ip || "—"}</span>
              <span>{new Date(selected.created_at).toLocaleString("pl-PL")}</span>
            </div>
            {!selected.read && (
              <Btn
                variant="primary"
                onClick={() => {
                  onMarkRead(siteId!, selected.id, true);
                  setSelected({ ...selected, read: true });
                }}
              >
                Oznacz jako przeczytane
              </Btn>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}

// ─── Tab: SEO ───

function TabSeo({ site }: { site?: { config_json?: Record<string, unknown> } | null }) {
  const seoConfig = (site?.config_json as { seo?: Record<string, unknown> })?.seo;

  const checks = [
    { label: "Meta title", value: (seoConfig as Record<string, unknown>)?.meta_title },
    { label: "Meta description", value: (seoConfig as Record<string, unknown>)?.meta_description },
    { label: "OG title", value: (seoConfig as Record<string, unknown>)?.og_title },
    { label: "OG description", value: (seoConfig as Record<string, unknown>)?.og_description },
    { label: "OG image", value: (seoConfig as Record<string, unknown>)?.og_image },
    { label: "Canonical URL", value: (seoConfig as Record<string, unknown>)?.canonical_url },
  ];

  return (
    <div>
      {/* SEO KPI placeholders */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {[
          { label: "SEO Score", value: "—", sub: "Brief 38" },
          { label: "Pozycja Google", value: "—", sub: "Brief 38" },
          { label: "Indeksacja", value: "—", sub: "Brief 38" },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-white rounded-xl border border-gray-200 p-5 text-center">
            <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
            <p className="text-xs text-gray-500 mt-1">{kpi.label}</p>
            <p className="text-[10px] text-gray-400 mt-0.5">{kpi.sub}</p>
          </div>
        ))}
      </div>

      {/* SEO meta table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50/50">
              <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Pole</th>
              <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Wartość</th>
              <th className="text-left text-xs font-medium text-gray-500 px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {checks.map((ch) => (
              <tr key={ch.label} className="border-b border-gray-50">
                <td className="px-5 py-3 text-sm text-gray-700 font-medium">{ch.label}</td>
                <td className="px-5 py-3 text-sm text-gray-600 max-w-md truncate">
                  {ch.value ? String(ch.value) : "—"}
                </td>
                <td className="px-5 py-3">
                  <StatusBadge variant={ch.value ? "success" : "warning"}>
                    {ch.value ? "OK" : "Brak"}
                  </StatusBadge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
