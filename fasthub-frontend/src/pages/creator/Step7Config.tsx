/**
 * Step7Config — 6-tab config page (Formularze / Social / SEO / Widoczność AI / Prawo / Hosting).
 * Brief 35: step 7. Brief 41: AI Visibility tab.
 */

import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useCreatorStore } from "@/store/creatorStore";
import * as api from "@/api/creator";
import type { ConfigData, LegalSource, CookieBanner, AIVisibilityData } from "@/types/creator";
import AIVisibilityTab from "@/components/creator/AIVisibilityTab";

const TABS = [
  { id: "forms", label: "Formularze" },
  { id: "social", label: "Social" },
  { id: "seo", label: "SEO" },
  { id: "ai-visibility", label: "Widoczność AI" },
  { id: "legal", label: "Prawo" },
  { id: "hosting", label: "Hosting" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function Step7Config() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { config, saveConfig, loadConfig, isSaving, project } = useCreatorStore();

  const [searchParams] = useSearchParams();
  const tabParam = searchParams.get("tab") as TabId | null;
  const [activeTab, setActiveTab] = useState<TabId>(
    tabParam && TABS.some((t) => t.id === tabParam) ? tabParam : "forms"
  );
  const [local, setLocal] = useState<ConfigData>({});
  const [aiVisibility, setAiVisibility] = useState<AIVisibilityData>({});
  const [isSuggestingSeo, setIsSuggestingSeo] = useState(false);
  const [ftpTestResult, setFtpTestResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [isFtpTesting, setIsFtpTesting] = useState(false);

  useEffect(() => {
    loadConfig();
    if (projectId) {
      api.getAiVisibility(projectId).then(({ data }) => {
        setAiVisibility(data.ai_visibility || {});
      }).catch(() => {});
    }
  }, []);

  useEffect(() => {
    setLocal(config);
  }, [config]);

  const saveAiVis = async () => {
    if (!projectId) return;
    try {
      await api.saveAiVisibility(projectId, aiVisibility);
    } catch (e) {
      console.error("Failed to save AI visibility:", e);
    }
  };

  const handleTabChange = async (tab: TabId) => {
    await saveConfig(local);
    if (activeTab === "ai-visibility") await saveAiVis();
    setActiveTab(tab);
  };

  const handleNext = async () => {
    await saveConfig(local);
    await saveAiVis();
    navigate(`/creator/${projectId}/step/8`);
  };

  const handleSuggestSeo = async () => {
    if (!projectId) return;
    setIsSuggestingSeo(true);
    try {
      const { data } = await api.suggestSeo(projectId);
      setLocal((prev) => ({
        ...prev,
        seo: {
          ...prev.seo,
          meta_title: data.meta_title,
          meta_description: data.meta_description,
          og_title: data.og_title,
          og_description: data.og_description,
        },
      }));
    } catch (e) {
      console.error("SEO suggest failed:", e);
    } finally {
      setIsSuggestingSeo(false);
    }
  };

  const updateForms = (key: string, value: unknown) =>
    setLocal((p) => ({ ...p, forms: { ...p.forms, [key]: value } }));

  const updateSocial = (key: string, value: string) =>
    setLocal((p) => ({ ...p, social: { ...p.social, [key]: value } }));

  const updateSeo = (key: string, value: unknown) =>
    setLocal((p) => ({ ...p, seo: { ...p.seo, [key]: value } }));

  const updateTracking = (key: string, value: string) =>
    setLocal((p) => ({
      ...p,
      seo: { ...p.seo, tracking: { ...p.seo?.tracking, [key]: value } },
    }));

  const updateLegal = (key: string, value: unknown) =>
    setLocal((p) => ({ ...p, legal: { ...p.legal, [key]: value } }));

  const updateHosting = (key: string, value: unknown) =>
    setLocal((p) => ({ ...p, hosting: { ...p.hosting, domain_type: p.hosting?.domain_type ?? "subdomain", deploy_method: p.hosting?.deploy_method ?? "auto", [key]: value } }));

  const updateFtp = (key: string, value: unknown) =>
    setLocal((p) => ({
      ...p,
      hosting: {
        ...p.hosting,
        domain_type: p.hosting?.domain_type ?? "subdomain",
        deploy_method: p.hosting?.deploy_method ?? "auto",
        ftp: { ...p.hosting?.ftp, [key]: value },
      },
    }));

  const handleTestFtp = async () => {
    if (!projectId) return;
    setIsFtpTesting(true);
    setFtpTestResult(null);
    try {
      await saveConfig(local);
      const { data } = await api.testFtp(projectId);
      setFtpTestResult(data);
    } catch (e: any) {
      setFtpTestResult({ ok: false, message: e?.response?.data?.detail || "Błąd testu FTP" });
    } finally {
      setIsFtpTesting(false);
    }
  };

  const inputClass = "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Konfiguracja</h1>
      <p className="text-gray-500 text-sm mb-6">Ustawienia techniczne strony</p>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-lg p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabChange(tab.id)}
            className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content — all tabs always in DOM (CSS-based hiding for E2E/chaos test) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="space-y-4" style={{ display: activeTab === "forms" ? "block" : "none" }}>
            <h2 className="text-lg font-semibold">Formularze kontaktowe</h2>
            <div>
              <label className={labelClass}>E-mail do powiadomień</label>
              <input type="email" name="contact_email" className={inputClass} placeholder="kontakt@firma.pl"
                value={local.forms?.contact_email || ""} onChange={(e) => updateForms("contact_email", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Wiadomość po wysłaniu (thank you)</label>
              <textarea name="thank_you_message" className={inputClass} rows={3} placeholder="Dziękujemy za kontakt! Odpowiemy w ciągu 24h."
                value={local.forms?.thank_you_message || ""} onChange={(e) => updateForms("thank_you_message", e.target.value)} />
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="email_notif" checked={local.forms?.send_email_notification !== false}
                onChange={(e) => updateForms("send_email_notification", e.target.checked)} />
              <label htmlFor="email_notif" className="text-sm text-gray-700">Wysyłaj powiadomienia e-mail o nowych zgłoszeniach</label>
            </div>

            {/* CRM Integration */}
            <div className="pt-4 border-t">
              <h3 className="text-md font-semibold mb-3">Integracja CRM</h3>
              <div className="flex items-center gap-2 mb-2">
                <input type="checkbox" id="crm_enabled" checked={local.forms?.crm_enabled || false}
                  onChange={(e) => updateForms("crm_enabled", e.target.checked)} />
                <label htmlFor="crm_enabled" className="text-sm text-gray-700">Wysyłaj leady do CRM (webhook)</label>
              </div>
              {local.forms?.crm_enabled && (
                <div>
                  <label className={labelClass}>Webhook URL (HTTPS)</label>
                  <input type="url" className={inputClass} placeholder="https://twoj-crm.pl/api/webhook/leads"
                    value={local.forms?.crm_webhook_url || ""}
                    onChange={(e) => updateForms("crm_webhook_url", e.target.value)} />
                  <p className="text-xs text-gray-400 mt-1">Każde nowe zgłoszenie z formularza zostanie wysłane jako JSON POST na ten adres.</p>
                </div>
              )}
            </div>

            {/* Newsletter */}
            <div className="pt-4 border-t">
              <h3 className="text-md font-semibold mb-3">Newsletter</h3>
              <div className="flex items-center gap-2 mb-2">
                <input type="checkbox" id="newsletter_enabled" checked={local.forms?.newsletter_enabled || false}
                  onChange={(e) => updateForms("newsletter_enabled", e.target.checked)} />
                <label htmlFor="newsletter_enabled" className="text-sm text-gray-700">Dodaj formularz zapisu do newslettera na stronie</label>
              </div>
              {local.forms?.newsletter_enabled && (
                <p className="text-xs text-gray-500 ml-6">
                  Formularz zapisu pojawi się na dole strony. Adresy e-mail trafiają do zgłoszeń formularza i mogą być przekazywane do CRM.
                </p>
              )}
            </div>
          </div>

        <div className="space-y-4" style={{ display: activeTab === "social" ? "block" : "none" }}>
            <h2 className="text-lg font-semibold">Social Media</h2>
            {(["facebook", "instagram", "linkedin", "twitter", "youtube", "tiktok"] as const).map((key) => (
              <div key={key}>
                <label className={labelClass}>{key.charAt(0).toUpperCase() + key.slice(1)}</label>
                <input type="url" name={key} className={inputClass} placeholder={`https://${key}.com/...`}
                  value={(local.social as Record<string, string>)?.[key] || ""} onChange={(e) => updateSocial(key, e.target.value)} />
              </div>
            ))}
          </div>

        <div className="space-y-4" style={{ display: activeTab === "seo" ? "block" : "none" }}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">SEO</h2>
              <button onClick={handleSuggestSeo} disabled={isSuggestingSeo}
                className="px-3 py-1.5 text-sm bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 disabled:opacity-50">
                {isSuggestingSeo ? "AI myśli..." : "AI zaproponuj"}
              </button>
            </div>
            <div>
              <label className={labelClass}>Meta title <span className="text-gray-400">({(local.seo?.meta_title || "").length}/60)</span></label>
              <input type="text" name="meta_title" className={inputClass} maxLength={60}
                value={local.seo?.meta_title || ""} onChange={(e) => updateSeo("meta_title", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Meta description <span className="text-gray-400">({(local.seo?.meta_description || "").length}/160)</span></label>
              <textarea name="meta_description" className={inputClass} rows={3} maxLength={160}
                value={local.seo?.meta_description || ""} onChange={(e) => updateSeo("meta_description", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>OG title</label>
              <input type="text" name="og_title" className={inputClass}
                value={local.seo?.og_title || ""} onChange={(e) => updateSeo("og_title", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>OG description</label>
              <textarea name="og_description" className={inputClass} rows={2}
                value={local.seo?.og_description || ""} onChange={(e) => updateSeo("og_description", e.target.value)} />
            </div>

            <div>
              <label className={labelClass}>Język strony</label>
              <select className={inputClass}
                value={local.seo?.language || "pl"}
                onChange={(e) => updateSeo("language", e.target.value)}>
                <option value="pl">Polski (pl)</option>
                <option value="en">English (en)</option>
                <option value="de">Deutsch (de)</option>
                <option value="fr">Français (fr)</option>
                <option value="es">Español (es)</option>
                <option value="uk">Українська (uk)</option>
                <option value="cs">Čeština (cs)</option>
              </select>
            </div>

            {/* SERP Preview */}
            {(local.seo?.meta_title || local.seo?.meta_description) && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-xs text-gray-500 mb-2 font-medium">Podgląd w Google (SERP)</p>
                <div className="font-sans">
                  <p className="text-[#1a0dab] text-lg leading-tight hover:underline cursor-default truncate">
                    {local.seo?.meta_title || project?.name || "Tytuł strony"}
                  </p>
                  <p className="text-[#006621] text-sm mt-0.5 truncate">
                    {local.hosting?.custom_domain
                      || (local.hosting?.subdomain ? `${local.hosting.subdomain}.webcreator.site` : "twoja-strona.webcreator.site")}
                  </p>
                  <p className="text-[#545454] text-sm mt-0.5 line-clamp-2">
                    {local.seo?.meta_description || "Opis strony pojawi się tutaj..."}
                  </p>
                </div>
              </div>
            )}

            <h3 className="text-md font-semibold pt-4 border-t">Tracking</h3>
            {([
              ["ga4_id", "Google Analytics 4 (G-XXXXXX)"],
              ["gtm_id", "Google Tag Manager (GTM-XXXXXX)"],
              ["fb_pixel_id", "Facebook Pixel ID"],
              ["hotjar_id", "Hotjar Site ID"],
              ["linkedin_id", "LinkedIn Insight Tag"],
              ["gsc_verification", "Google Search Console (meta tag value)"],
            ] as const).map(([key, label]) => (
              <div key={key}>
                <label className={labelClass}>{label}</label>
                <input type="text" name={key} className={inputClass}
                  value={local.seo?.tracking?.[key] || ""} onChange={(e) => updateTracking(key, e.target.value)} />
              </div>
            ))}
            <div>
              <label className={labelClass}>Własny kod w &lt;head&gt;</label>
              <textarea name="custom_head" className={`${inputClass} font-mono text-xs`} rows={3}
                value={local.seo?.tracking?.custom_head || ""} onChange={(e) => updateTracking("custom_head", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Własny kod w &lt;body&gt;</label>
              <textarea name="custom_body" className={`${inputClass} font-mono text-xs`} rows={3}
                value={local.seo?.tracking?.custom_body || ""} onChange={(e) => updateTracking("custom_body", e.target.value)} />
            </div>
          </div>

        <div style={{ display: activeTab === "ai-visibility" ? "block" : "none" }}>
            <AIVisibilityTab data={aiVisibility} onChange={setAiVisibility} />
          </div>

        <div className="space-y-6" style={{ display: activeTab === "legal" ? "block" : "none" }}>
            <h2 className="text-lg font-semibold">Prawo</h2>
            {/* Privacy Policy */}
            <div>
              <label className={labelClass}>Polityka prywatności</label>
              <div className="flex gap-3 mt-1">
                {(["ai", "own", "none"] as const).map((src) => (
                  <label key={src} className="flex items-center gap-2 text-sm">
                    <input type="radio" name="pp_source" value={src}
                      checked={(local.legal?.privacy_policy?.source || "none") === src}
                      onChange={() => updateLegal("privacy_policy", { ...local.legal?.privacy_policy, source: src })} />
                    {src === "ai" ? "AI generuje" : src === "own" ? "Własna" : "Brak"}
                  </label>
                ))}
              </div>
              {local.legal?.privacy_policy?.source === "own" && (
                <textarea name="privacy_policy_html" className={`${inputClass} mt-2`} rows={5} placeholder="Wklej treść polityki prywatności (HTML)"
                  value={local.legal?.privacy_policy?.html || ""}
                  onChange={(e) => updateLegal("privacy_policy", { ...local.legal?.privacy_policy, html: e.target.value })} />
              )}
            </div>

            {/* Terms */}
            <div>
              <label className={labelClass}>Regulamin</label>
              <div className="flex gap-3 mt-1">
                {(["ai", "own", "none"] as const).map((src) => (
                  <label key={src} className="flex items-center gap-2 text-sm">
                    <input type="radio" name="terms_source" value={src}
                      checked={(local.legal?.terms?.source || "none") === src}
                      onChange={() => updateLegal("terms", { ...local.legal?.terms, source: src })} />
                    {src === "ai" ? "AI generuje" : src === "own" ? "Własny" : "Brak"}
                  </label>
                ))}
              </div>
              {local.legal?.terms?.source === "own" && (
                <textarea name="terms_html" className={`${inputClass} mt-2`} rows={5} placeholder="Wklej treść regulaminu (HTML)"
                  value={local.legal?.terms?.html || ""}
                  onChange={(e) => updateLegal("terms", { ...local.legal?.terms, html: e.target.value })} />
              )}
            </div>

            {/* Cookie banner */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <input type="checkbox" id="cookie_enabled" checked={local.legal?.cookie_banner?.enabled || false}
                  onChange={(e) => updateLegal("cookie_banner", { ...local.legal?.cookie_banner, enabled: e.target.checked, style: local.legal?.cookie_banner?.style || "bar" })} />
                <label htmlFor="cookie_enabled" className={labelClass + " mb-0"}>Baner cookies</label>
              </div>
              {local.legal?.cookie_banner?.enabled && (
                <div className="ml-6 space-y-2">
                  <div className="flex gap-3">
                    {(["bar", "modal", "corner"] as const).map((s) => (
                      <label key={s} className="flex items-center gap-1 text-sm">
                        <input type="radio" name="cookie_style" value={s}
                          checked={(local.legal?.cookie_banner?.style || "bar") === s}
                          onChange={() => updateLegal("cookie_banner", { ...local.legal?.cookie_banner, style: s })} />
                        {s === "bar" ? "Pasek" : s === "modal" ? "Modal" : "Narożnik"}
                      </label>
                    ))}
                  </div>
                  <textarea name="cookie_banner_text" className={inputClass} rows={2} placeholder="Tekst banera cookies"
                    value={local.legal?.cookie_banner?.text || ""}
                    onChange={(e) => updateLegal("cookie_banner", { ...local.legal?.cookie_banner, text: e.target.value })} />
                </div>
              )}
            </div>

            {/* RODO */}
            <div>
              <div className="flex items-center gap-2 mb-2">
                <input type="checkbox" id="rodo_enabled" checked={local.legal?.rodo?.enabled || false}
                  onChange={(e) => updateLegal("rodo", { ...local.legal?.rodo, enabled: e.target.checked })} />
                <label htmlFor="rodo_enabled" className={labelClass + " mb-0"}>Klauzula RODO przy formularzach</label>
              </div>
              {local.legal?.rodo?.enabled && (
                <textarea name="rodo_text" className={`${inputClass} ml-6`} rows={2} placeholder="Treść klauzuli RODO"
                  value={local.legal?.rodo?.text || ""}
                  onChange={(e) => updateLegal("rodo", { ...local.legal?.rodo, text: e.target.value })} />
              )}
            </div>
          </div>

        <div className="space-y-4" style={{ display: activeTab === "hosting" ? "block" : "none" }}>
            <h2 className="text-lg font-semibold">Hosting</h2>
            <div>
              <label className={labelClass}>Typ domeny</label>
              <div className="flex gap-3">
                <label className="flex items-center gap-2 text-sm">
                  <input type="radio" name="domain_type" value="subdomain"
                    checked={(local.hosting?.domain_type || "subdomain") === "subdomain"}
                    onChange={() => updateHosting("domain_type", "subdomain")} />
                  Subdomena WebCreator
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input type="radio" name="domain_type" value="custom"
                    checked={local.hosting?.domain_type === "custom"}
                    onChange={() => updateHosting("domain_type", "custom")} />
                  Własna domena
                </label>
              </div>
            </div>

            {local.hosting?.domain_type === "custom" ? (
              <div>
                <label className={labelClass}>Własna domena</label>
                <input type="text" name="custom_domain" className={inputClass} placeholder="www.mojafirma.pl"
                  value={local.hosting?.custom_domain || ""} onChange={(e) => updateHosting("custom_domain", e.target.value)} />
              </div>
            ) : (
              <div>
                <label className={labelClass}>Subdomena</label>
                <div className="flex items-center gap-1">
                  <input type="text" name="subdomain" className={inputClass} placeholder="mojafirma"
                    value={local.hosting?.subdomain || ""} onChange={(e) => updateHosting("subdomain", e.target.value)} />
                  <span className="text-sm text-gray-500 whitespace-nowrap">.webcreator.site</span>
                </div>
              </div>
            )}

            <div>
              <label className={labelClass}>Metoda wdrożenia</label>
              <div className="flex gap-3">
                {(["auto", "ftp", "zip"] as const).map((m) => (
                  <label key={m} className="flex items-center gap-2 text-sm">
                    <input type="radio" name="deploy_method" value={m}
                      checked={(local.hosting?.deploy_method || "auto") === m}
                      onChange={() => updateHosting("deploy_method", m)} />
                    {m === "auto" ? "Automatycznie" : m === "ftp" ? "FTP" : "Pobierz ZIP"}
                  </label>
                ))}
              </div>
            </div>

            {/* FTP credentials form */}
            {local.hosting?.deploy_method === "ftp" && (
              <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700">Dane serwera FTP</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className={labelClass}>Host</label>
                    <input type="text" className={inputClass} placeholder="ftp.mojadomena.pl"
                      value={local.hosting?.ftp?.host || ""} onChange={(e) => updateFtp("host", e.target.value)} />
                  </div>
                  <div>
                    <label className={labelClass}>Port</label>
                    <input type="number" className={inputClass} placeholder="21"
                      value={local.hosting?.ftp?.port || 21} onChange={(e) => updateFtp("port", parseInt(e.target.value) || 21)} />
                  </div>
                </div>
                <div>
                  <label className={labelClass}>Nazwa użytkownika</label>
                  <input type="text" className={inputClass} placeholder="user@mojadomena.pl"
                    value={local.hosting?.ftp?.username || ""} onChange={(e) => updateFtp("username", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>Hasło</label>
                  <input type="password" className={inputClass} placeholder="••••••••"
                    value={local.hosting?.ftp?.password || ""} onChange={(e) => updateFtp("password", e.target.value)} />
                </div>
                <div>
                  <label className={labelClass}>Katalog docelowy</label>
                  <input type="text" className={inputClass} placeholder="/public_html"
                    value={local.hosting?.ftp?.path || ""} onChange={(e) => updateFtp("path", e.target.value)} />
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={handleTestFtp} disabled={isFtpTesting || !local.hosting?.ftp?.host}
                    className="px-4 py-2 text-sm bg-gray-800 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50">
                    {isFtpTesting ? "Testuję..." : "Testuj połączenie"}
                  </button>
                  {ftpTestResult && (
                    <span className={`text-sm ${ftpTestResult.ok ? "text-green-600" : "text-red-600"}`}>
                      {ftpTestResult.message}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
      </div>

      {/* Bottom bar */}
      <div className="flex justify-between mt-6">
        <button onClick={() => navigate(`/creator/${projectId}/step/6`)}
          className="px-6 py-2.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">
          Wstecz
        </button>
        <button onClick={handleNext} disabled={isSaving}
          className="px-6 py-2.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {isSaving ? "Zapisuję..." : "Dalej →"}
        </button>
      </div>
    </div>
  );
}
