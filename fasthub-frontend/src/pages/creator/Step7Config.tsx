/**
 * Step7Config — 5-tab config page (Formularze / Social / SEO / Prawo / Hosting).
 * Brief 35: step 7.
 */

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useCreatorStore } from "@/store/creatorStore";
import * as api from "@/api/creator";
import type { ConfigData, LegalSource, CookieBanner } from "@/types/creator";

const TABS = [
  { id: "forms", label: "Formularze" },
  { id: "social", label: "Social" },
  { id: "seo", label: "SEO" },
  { id: "legal", label: "Prawo" },
  { id: "hosting", label: "Hosting" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function Step7Config() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { config, saveConfig, loadConfig, isSaving, project } = useCreatorStore();

  const [activeTab, setActiveTab] = useState<TabId>("forms");
  const [local, setLocal] = useState<ConfigData>({});
  const [isSuggestingSeo, setIsSuggestingSeo] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    setLocal(config);
  }, [config]);

  const handleTabChange = async (tab: TabId) => {
    await saveConfig(local);
    setActiveTab(tab);
  };

  const handleNext = async () => {
    await saveConfig(local);
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

      {/* Tab content */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        {activeTab === "forms" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Formularze kontaktowe</h2>
            <div>
              <label className={labelClass}>E-mail do powiadomień</label>
              <input type="email" className={inputClass} placeholder="kontakt@firma.pl"
                value={local.forms?.contact_email || ""} onChange={(e) => updateForms("contact_email", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Wiadomość po wysłaniu (thank you)</label>
              <textarea className={inputClass} rows={3} placeholder="Dziękujemy za kontakt! Odpowiemy w ciągu 24h."
                value={local.forms?.thank_you_message || ""} onChange={(e) => updateForms("thank_you_message", e.target.value)} />
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="email_notif" checked={local.forms?.send_email_notification !== false}
                onChange={(e) => updateForms("send_email_notification", e.target.checked)} />
              <label htmlFor="email_notif" className="text-sm text-gray-700">Wysyłaj powiadomienia e-mail o nowych zgłoszeniach</label>
            </div>
          </div>
        )}

        {activeTab === "social" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Social Media</h2>
            {(["facebook", "instagram", "linkedin", "twitter", "youtube", "tiktok"] as const).map((key) => (
              <div key={key}>
                <label className={labelClass}>{key.charAt(0).toUpperCase() + key.slice(1)}</label>
                <input type="url" className={inputClass} placeholder={`https://${key}.com/...`}
                  value={(local.social as Record<string, string>)?.[key] || ""} onChange={(e) => updateSocial(key, e.target.value)} />
              </div>
            ))}
          </div>
        )}

        {activeTab === "seo" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">SEO</h2>
              <button onClick={handleSuggestSeo} disabled={isSuggestingSeo}
                className="px-3 py-1.5 text-sm bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 disabled:opacity-50">
                {isSuggestingSeo ? "AI myśli..." : "AI zaproponuj"}
              </button>
            </div>
            <div>
              <label className={labelClass}>Meta title <span className="text-gray-400">({(local.seo?.meta_title || "").length}/60)</span></label>
              <input type="text" className={inputClass} maxLength={60}
                value={local.seo?.meta_title || ""} onChange={(e) => updateSeo("meta_title", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Meta description <span className="text-gray-400">({(local.seo?.meta_description || "").length}/160)</span></label>
              <textarea className={inputClass} rows={3} maxLength={160}
                value={local.seo?.meta_description || ""} onChange={(e) => updateSeo("meta_description", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>OG title</label>
              <input type="text" className={inputClass}
                value={local.seo?.og_title || ""} onChange={(e) => updateSeo("og_title", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>OG description</label>
              <textarea className={inputClass} rows={2}
                value={local.seo?.og_description || ""} onChange={(e) => updateSeo("og_description", e.target.value)} />
            </div>

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
                <input type="text" className={inputClass}
                  value={local.seo?.tracking?.[key] || ""} onChange={(e) => updateTracking(key, e.target.value)} />
              </div>
            ))}
            <div>
              <label className={labelClass}>Własny kod w &lt;head&gt;</label>
              <textarea className={`${inputClass} font-mono text-xs`} rows={3}
                value={local.seo?.tracking?.custom_head || ""} onChange={(e) => updateTracking("custom_head", e.target.value)} />
            </div>
            <div>
              <label className={labelClass}>Własny kod w &lt;body&gt;</label>
              <textarea className={`${inputClass} font-mono text-xs`} rows={3}
                value={local.seo?.tracking?.custom_body || ""} onChange={(e) => updateTracking("custom_body", e.target.value)} />
            </div>
          </div>
        )}

        {activeTab === "legal" && (
          <div className="space-y-6">
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
                <textarea className={`${inputClass} mt-2`} rows={5} placeholder="Wklej treść polityki prywatności (HTML)"
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
                <textarea className={`${inputClass} mt-2`} rows={5} placeholder="Wklej treść regulaminu (HTML)"
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
                  <textarea className={inputClass} rows={2} placeholder="Tekst banera cookies"
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
                <textarea className={`${inputClass} ml-6`} rows={2} placeholder="Treść klauzuli RODO"
                  value={local.legal?.rodo?.text || ""}
                  onChange={(e) => updateLegal("rodo", { ...local.legal?.rodo, text: e.target.value })} />
              )}
            </div>
          </div>
        )}

        {activeTab === "hosting" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Hosting</h2>
            <div>
              <label className={labelClass}>Typ domeny</label>
              <div className="flex gap-3">
                <label className="flex items-center gap-2 text-sm">
                  <input type="radio" name="domain_type" value="subdomain"
                    checked={(local.hosting?.domain_type || "subdomain") === "subdomain"}
                    onChange={() => updateHosting("domain_type", "subdomain")} />
                  Subdomena FastHub
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
                <input type="text" className={inputClass} placeholder="www.mojafirma.pl"
                  value={local.hosting?.custom_domain || ""} onChange={(e) => updateHosting("custom_domain", e.target.value)} />
              </div>
            ) : (
              <div>
                <label className={labelClass}>Subdomena</label>
                <div className="flex items-center gap-1">
                  <input type="text" className={inputClass} placeholder="mojafirma"
                    value={local.hosting?.subdomain || ""} onChange={(e) => updateHosting("subdomain", e.target.value)} />
                  <span className="text-sm text-gray-500 whitespace-nowrap">.fasthub.site</span>
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
          </div>
        )}
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
