/**
 * Step 1 — "Opowiedz nam o swojej wymarzonej stronie"
 * Accordion with sections adapted per site type.
 * Brief 32: data saved to project.brief_json.
 */

import { useState, useCallback, useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Btn from "@/components/ui/Btn";
import Chk from "@/components/ui/Chk";
import Fld from "@/components/ui/Fld";
import Tile from "@/components/ui/Tile";
import { useAutoSave } from "@/hooks/useAutoSave";
import { useCreatorStore } from "@/store/creatorStore";
import {
  BRAND_POSITIONS,
  CLIENT_TYPES,
  IMPRESSIONS_FEEL,
  IMPRESSIONS_THINK,
  INDUSTRIES,
  SITE_CONTENT,
  SITE_GOALS,
  SITE_TYPES_FIRMA,
  SITE_TYPES_OSOBA,
  STRENGTHS,
  WRITING_STYLES,
} from "@/types/creator";

// ─── Which sections are visible per site type ───
// Brief 42: primary source is siteTypeConfig.brief_sections from backend.
// Fallback below for loading/offline states.

const OSOBA_IDS = new Set(SITE_TYPES_OSOBA.map((t) => t.id));

type SectionKey = "s1" | "s2" | "s3" | "s4" | "s5" | "s6" | "s7" | "s8" | "s9" | "s10" | "s11";

const ALL_SECTIONS: SectionKey[] = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11"];

function getSectionsForType(siteType: string): Set<SectionKey> {
  if (!siteType) return new Set(["s1"]);
  if (["firmowa", "korporacyjna", "firmowa-blog", "korporacyjna-blog"].includes(siteType))
    return new Set(ALL_SECTIONS);
  if (siteType.startsWith("lp-")) return new Set(["s1", "s2", "s3", "s5", "s7", "s8", "s9", "s11"]);
  if (siteType === "blog") return new Set(["s1", "s2", "s5", "s7", "s8", "s11"]);
  if (siteType === "wizytowka" || siteType === "wizytowka-osoba") return new Set(["s1", "s2", "s8", "s11"]);
  if (siteType === "ekspert") return new Set(["s1", "s2", "s3", "s5", "s6", "s7", "s8", "s9", "s11"]);
  if (siteType === "portfolio") return new Set(["s1", "s2", "s5", "s7", "s8", "s9", "s11"]);
  if (siteType === "cv") return new Set(["s1", "s2", "s5", "s8", "s11"]);
  return new Set(ALL_SECTIONS);
}

// ─── Accordion Row ───

function AccordionRow({
  num,
  title,
  isOpen,
  onToggle,
  filled,
  total,
  children,
}: {
  num: number;
  title: string;
  isOpen: boolean;
  onToggle: () => void;
  filled: number;
  total: number;
  children: React.ReactNode;
}) {
  const allDone = filled >= total && total > 0;

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-5 py-4 bg-white hover:bg-gray-50 transition-colors text-left"
      >
        <span className="font-semibold text-sm text-gray-900">
          {num}. {title}
        </span>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              allDone
                ? "bg-green-100 text-green-700"
                : filled > 0
                  ? "bg-amber-100 text-amber-700"
                  : "bg-gray-100 text-gray-400"
            }`}
          >
            {filled}/{total}
          </span>
          <svg
            className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      {isOpen && <div className="px-5 pb-5 pt-2 border-t border-gray-100 space-y-4">{children}</div>}
    </div>
  );
}

// ─── Section metadata (filled/total) ───

interface SectionMeta {
  key: SectionKey;
  title: string;
  filled: number;
  total: number;
}

export default function Step1Brief() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { brief, setBrief, saveBrief } = useCreatorStore();

  useAutoSave(brief, saveBrief, 2000);

  const [openSections, setOpenSections] = useState<Set<string>>(new Set(["s1"]));

  const toggle = useCallback((key: string) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }, []);

  const pickType = (id: string) => {
    const forWhom = OSOBA_IDS.has(id) ? "osoba" : "firma";
    setBrief({ siteType: id, forWhom });
  };

  const canProceed = brief.siteType && brief.companyName && brief.industry;

  const toggleArray = (arr: string[], item: string): string[] =>
    arr.includes(item) ? arr.filter((i) => i !== item) : [...arr, item];

  const isOsoba = OSOBA_IDS.has(brief.siteType);

  // Brief 42: use backend config as primary source, fallback to local logic
  const { siteTypeConfig, loadSiteTypeConfig } = useCreatorStore();

  // Load config when siteType changes
  const siteType = brief.siteType;
  const prevSiteTypeRef = useState(siteType)[0];
  useMemo(() => {
    if (siteType && siteType !== prevSiteTypeRef) {
      loadSiteTypeConfig(siteType);
    }
  }, [siteType]);

  const visibleSet = useMemo(() => {
    if (siteTypeConfig && siteTypeConfig.site_type === brief.siteType) {
      return new Set(siteTypeConfig.brief_sections as SectionKey[]);
    }
    return getSectionsForType(brief.siteType);
  }, [brief.siteType, siteTypeConfig]);
  const show = (k: SectionKey) => visibleSet.has(k);

  // Brief content filter — normalize to strip diacritics for safe comparison
  const stripDiacritics = (s: string) =>
    s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

  const filteredSiteContent = useMemo(() => {
    const allowed = siteTypeConfig?.brief_content;
    if (!allowed || allowed.length === 0) return SITE_CONTENT;
    const allowedSet = new Set(allowed.map(stripDiacritics));
    return SITE_CONTENT.filter((c) => allowedSet.has(stripDiacritics(c)));
  }, [siteTypeConfig]);

  // ─── Progress per section ───

  const sectionMetas: SectionMeta[] = useMemo(() => {
    const all: SectionMeta[] = [
      { key: "s1", title: "Jaką stronę chcesz stworzyć?", filled: brief.siteType ? 1 : 0, total: 1 },
      {
        key: "s2",
        title: isOsoba ? "Opowiedz o sobie" : "Opowiedz o firmie",
        filled: (brief.companyName ? 1 : 0) + (brief.whatYouDo ? 1 : 0) + (brief.industry ? 1 : 0),
        total: 3,
      },
      {
        key: "s3",
        title: isOsoba ? "Kim są Twoi odbiorcy?" : "Kim są Twoi klienci?",
        filled: (brief.clientTypes.length > 0 ? 1 : 0) + (brief.decisionMaker ? 1 : 0),
        total: 2,
      },
      {
        key: "s4",
        title: "Profil behawioralny klienta",
        filled:
          (brief.clientValues ? 1 : 0) +
          (brief.clientLikes ? 1 : 0) +
          (brief.clientDislikes ? 1 : 0) +
          (brief.clientNeeds ? 1 : 0),
        total: 4,
      },
      {
        key: "s5",
        title: "Co Cię wyróżnia?",
        filled: (brief.usp ? 1 : 0) + (brief.whyChooseUs ? 1 : 0) + (brief.strengths.length > 0 ? 1 : 0),
        total: 3,
      },
      { key: "s6", title: "Pozycjonowanie marki", filled: brief.brandPos.length > 0 ? 1 : 0, total: 1 },
      { key: "s7", title: "Styl komunikacji", filled: brief.writingStyle.length > 0 ? 1 : 0, total: 1 },
      {
        key: "s8",
        title: "Cel strony i zawartość",
        filled: (brief.mainGoal.length > 0 ? 1 : 0) + (brief.siteContent.length > 0 ? 1 : 0),
        total: 2,
      },
      {
        key: "s9",
        title: "Co ma pomyśleć i poczuć odwiedzający?",
        filled:
          (brief.impressionCustom ? 1 : 0) +
          (brief.impThink.length > 0 ? 1 : 0) +
          (brief.impFeel.length > 0 ? 1 : 0),
        total: 3,
      },
      { key: "s10", title: "Podstrony", filled: brief.menuProposal ? 1 : 0, total: 1 },
      { key: "s11", title: "Dodatkowe życzenia", filled: brief.extraWishes ? 1 : 0, total: 1 },
    ];
    return all.filter((s) => visibleSet.has(s.key));
  }, [brief, visibleSet, isOsoba]);

  const totalFilled = sectionMetas.reduce((sum, s) => sum + s.filled, 0);
  const totalFields = sectionMetas.reduce((sum, s) => sum + s.total, 0);

  // Dynamic numbering helper
  const num = (key: SectionKey) => {
    const idx = sectionMetas.findIndex((s) => s.key === key);
    return idx >= 0 ? idx + 1 : 0;
  };
  const meta = (key: SectionKey) => sectionMetas.find((s) => s.key === key);

  return (
    <div className="max-w-3xl mx-auto py-8 px-6 space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Opowiedz nam o swojej wymarzonej stronie</h1>
        <p className="text-sm text-gray-500 mt-1">
          Im więcej nam powiesz, tym lepszą stronę stworzymy.
        </p>
      </div>

      {/* ─── Progress bar ─── */}
      <div className="bg-white border border-gray-200 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Postęp briefu</span>
          <span className="text-sm text-gray-500">
            {totalFilled} z {totalFields} pól
          </span>
        </div>
        <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all duration-300"
            style={{ width: `${totalFields > 0 ? (totalFilled / totalFields) * 100 : 0}%` }}
          />
        </div>
      </div>

      {/* ───── S1: Typ strony ───── */}
      <AccordionRow
        num={num("s1")}
        title="Jaką stronę chcesz stworzyć?"
        isOpen={openSections.has("s1")}
        onToggle={() => toggle("s1")}
        filled={meta("s1")?.filled ?? 0}
        total={meta("s1")?.total ?? 1}
      >
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {SITE_TYPES_FIRMA.map((t) => (
            <Tile key={t.id} on={brief.siteType === t.id} onClick={() => pickType(t.id)}>
              <div className="font-medium text-sm">{t.label}</div>
              <div className="text-xs text-gray-500 mt-0.5">{t.desc}</div>
            </Tile>
          ))}
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {SITE_TYPES_OSOBA.map((t) => (
            <Tile key={t.id} on={brief.siteType === t.id} onClick={() => pickType(t.id)}>
              <div className="font-medium text-sm">{t.label}</div>
              <div className="text-xs text-gray-500 mt-0.5">{t.desc}</div>
            </Tile>
          ))}
          <Tile on={false} onClick={() => {}}>
            <div className="font-medium text-sm text-gray-400">Sklep</div>
            <div className="text-xs text-gray-400 mt-0.5">Wkrótce</div>
          </Tile>
        </div>
      </AccordionRow>

      {/* ───── S2: O firmie / O sobie ───── */}
      {show("s2") && (
        <AccordionRow
          num={num("s2")}
          title={isOsoba ? "Opowiedz o sobie" : "Opowiedz o firmie"}
          isOpen={openSections.has("s2")}
          onToggle={() => toggle("s2")}
          filled={meta("s2")?.filled ?? 0}
          total={meta("s2")?.total ?? 3}
        >
          <Fld
            label={isOsoba ? "Imię i nazwisko" : "Nazwa firmy"}
            placeholder={isOsoba ? "Jan Kowalski" : "Acme Sp. z o.o."}
            value={brief.companyName}
            onChange={(v) => setBrief({ companyName: v })}
          />
          <Fld
            label="Czym się zajmujesz?"
            placeholder="Opisz swoją działalność w 2-3 zdaniach..."
            value={brief.whatYouDo}
            onChange={(v) => setBrief({ whatYouDo: v })}
            large={3}
          />
          <Chk on={brief.hasWebsite} onClick={() => setBrief({ hasWebsite: !brief.hasWebsite })}>
            <span className="text-sm">Mam obecną stronę www</span>
          </Chk>
          {brief.hasWebsite && (
            <Fld
              label="Adres obecnej strony"
              placeholder="https://..."
              value={brief.currentUrl || ""}
              onChange={(v) => setBrief({ currentUrl: v })}
              type="url"
            />
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Branża</label>
            <select
              value={brief.industry}
              onChange={(e) => setBrief({ industry: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 bg-white"
            >
              <option value="">Wybierz branżę...</option>
              {INDUSTRIES.map((ind) => (
                <option key={ind} value={ind}>{ind}</option>
              ))}
            </select>
          </div>
        </AccordionRow>
      )}

      {/* ───── S3: Klienci ───── */}
      {show("s3") && (
        <AccordionRow
          num={num("s3")}
          title={isOsoba ? "Kim są Twoi odbiorcy?" : "Kim są Twoi klienci?"}
          isOpen={openSections.has("s3")}
          onToggle={() => toggle("s3")}
          filled={meta("s3")?.filled ?? 0}
          total={meta("s3")?.total ?? 2}
        >
          <div className="grid grid-cols-2 gap-3">
            {CLIENT_TYPES.map((ct) => (
              <Tile
                key={ct.id}
                on={brief.clientTypes.includes(ct.id)}
                onClick={() => setBrief({ clientTypes: toggleArray(brief.clientTypes, ct.id) })}
              >
                <div className="font-medium text-sm">{ct.label}</div>
                <div className="text-xs text-gray-500">{ct.desc}</div>
              </Tile>
            ))}
          </div>
          {brief.clientTypes.includes("B2B") && (
            <Fld label="Jakie firmy są Twoimi klientami?" value={brief.clientB2B || ""} onChange={(v) => setBrief({ clientB2B: v })} large={2} placeholder="np. Małe i średnie firmy z branży IT..." />
          )}
          {brief.clientTypes.includes("B2C") && (
            <Fld label="Kto jest Twoim klientem? Jakie osoby?" value={brief.clientB2C || ""} onChange={(v) => setBrief({ clientB2C: v })} large={2} placeholder="np. Kobiety 25-45, mieszkanki dużych miast..." />
          )}
          {brief.clientTypes.includes("B2G") && (
            <Fld label="Jakie instytucje?" value={brief.clientB2G || ""} onChange={(v) => setBrief({ clientB2G: v })} large={2} placeholder="np. Urzędy miast, szkoły publiczne..." />
          )}
          {brief.clientTypes.includes("NGO") && (
            <Fld label="Jakie organizacje?" value={brief.clientNGO || ""} onChange={(v) => setBrief({ clientNGO: v })} large={2} placeholder="np. Fundacje ekologiczne, stowarzyszenia..." />
          )}
          <Fld
            label="Kto personalnie podejmuje decyzję o zakupie?"
            value={brief.decisionMaker}
            onChange={(v) => setBrief({ decisionMaker: v })}
            placeholder="np. CEO, dyrektor marketingu, właściciel..."
          />
        </AccordionRow>
      )}

      {/* ───── S4: Profil behawioralny ───── */}
      {show("s4") && (
        <AccordionRow
          num={num("s4")}
          title="Profil behawioralny klienta"
          isOpen={openSections.has("s4")}
          onToggle={() => toggle("s4")}
          filled={meta("s4")?.filled ?? 0}
          total={meta("s4")?.total ?? 4}
        >
          <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 text-sm text-indigo-800">
            Zrozumienie motywacji klientów pomoże AI dopasować ton komunikacji i treści strony do ich potrzeb.
          </div>
          <Fld label="Co klienci cenią najbardziej?" value={brief.clientValues} onChange={(v) => setBrief({ clientValues: v })} large={3} placeholder="np. Jakość, terminowość, profesjonalizm..." />
          <Fld label="Co ich przyciąga, co im się podoba?" value={brief.clientLikes} onChange={(v) => setBrief({ clientLikes: v })} large={3} placeholder="np. Nowoczesne podejście, transparentność..." />
          <Fld label="Co ich denerwuje, czego nie lubią?" value={brief.clientDislikes} onChange={(v) => setBrief({ clientDislikes: v })} large={3} placeholder="np. Ukryte koszty, brak kontaktu..." />
          <Fld label="Jakie mają potrzeby i wartości?" value={brief.clientNeeds} onChange={(v) => setBrief({ clientNeeds: v })} large={3} placeholder="np. Szukają partnera na lata, cenią bezpieczeństwo..." />
        </AccordionRow>
      )}

      {/* ───── S5: USP ───── */}
      {show("s5") && (
        <AccordionRow
          num={num("s5")}
          title="Co Cię wyróżnia?"
          isOpen={openSections.has("s5")}
          onToggle={() => toggle("s5")}
          filled={meta("s5")?.filled ?? 0}
          total={meta("s5")?.total ?? 3}
        >
          <Fld label="Hasło / motto / slogan (opcjonalne)" value={brief.slogan || ""} onChange={(v) => setBrief({ slogan: v })} placeholder="np. Innowacje, które działają" />
          <Fld label="Misja firmy (opcjonalne)" value={brief.mission || ""} onChange={(v) => setBrief({ mission: v })} placeholder="np. Pomagamy firmom rosnąć dzięki technologii" />
          <Fld label="Czym się wyróżniasz? (USP)" value={brief.usp} onChange={(v) => setBrief({ usp: v })} large={3} placeholder="Co oferujesz, czego nie ma konkurencja?" />
          <Fld label="Dlaczego klienci wybierają Ciebie?" value={brief.whyChooseUs} onChange={(v) => setBrief({ whyChooseUs: v })} large={3} placeholder="Co mówią Twoi klienci o współpracy?" />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Twoje atuty (wybierz pasujące)</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {STRENGTHS.map((s) => (
                <Chk key={s} on={brief.strengths.includes(s)} onClick={() => setBrief({ strengths: toggleArray(brief.strengths, s) })}>
                  <span className="text-sm">{s}</span>
                </Chk>
              ))}
            </div>
          </div>
        </AccordionRow>
      )}

      {/* ───── S6: Pozycjonowanie marki ───── */}
      {show("s6") && (
        <AccordionRow
          num={num("s6")}
          title="Pozycjonowanie marki"
          isOpen={openSections.has("s6")}
          onToggle={() => toggle("s6")}
          filled={meta("s6")?.filled ?? 0}
          total={meta("s6")?.total ?? 1}
        >
          <div className="space-y-2">
            {BRAND_POSITIONS.map((bp) => (
              <Chk key={bp.id} on={brief.brandPos.includes(bp.id)} onClick={() => setBrief({ brandPos: toggleArray(brief.brandPos, bp.id) })}>
                <div>
                  <div className="font-medium text-sm">{bp.label}</div>
                  <div className="text-xs text-gray-500">{bp.desc}</div>
                </div>
              </Chk>
            ))}
          </div>
        </AccordionRow>
      )}

      {/* ───── S7: Styl komunikacji ───── */}
      {show("s7") && (
        <AccordionRow
          num={num("s7")}
          title="Styl komunikacji"
          isOpen={openSections.has("s7")}
          onToggle={() => toggle("s7")}
          filled={meta("s7")?.filled ?? 0}
          total={meta("s7")?.total ?? 1}
        >
          <div className="space-y-2">
            {WRITING_STYLES.map((ws) => (
              <Chk key={ws.id} on={brief.writingStyle.includes(ws.id)} onClick={() => setBrief({ writingStyle: toggleArray(brief.writingStyle, ws.id) })}>
                <div>
                  <div className="font-medium text-sm">{ws.label}</div>
                  <div className="text-xs text-gray-500 italic">"{ws.example}"</div>
                </div>
              </Chk>
            ))}
          </div>
        </AccordionRow>
      )}

      {/* ───── S8: Cel strony ───── */}
      {show("s8") && (
        <AccordionRow
          num={num("s8")}
          title="Cel strony i zawartość"
          isOpen={openSections.has("s8")}
          onToggle={() => toggle("s8")}
          filled={meta("s8")?.filled ?? 0}
          total={meta("s8")?.total ?? 2}
        >
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {SITE_GOALS.map((g) => (
              <Tile key={g.id} on={brief.mainGoal.includes(g.id)} onClick={() => setBrief({ mainGoal: toggleArray(brief.mainGoal, g.id) })}>
                <div className="font-medium text-sm">{g.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{g.desc}</div>
              </Tile>
            ))}
          </div>
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">Co ma zawierać strona?</label>
            <div className="grid grid-cols-2 gap-2">
              {filteredSiteContent.map((c) => (
                <Chk key={c} on={brief.siteContent.includes(c)} onClick={() => setBrief({ siteContent: toggleArray(brief.siteContent, c) })}>
                  <span className="text-sm">{c}</span>
                </Chk>
              ))}
            </div>
          </div>
        </AccordionRow>
      )}

      {/* ───── S9: Wrażenia ───── */}
      {show("s9") && (
        <AccordionRow
          num={num("s9")}
          title="Co ma pomyśleć i poczuć odwiedzający?"
          isOpen={openSections.has("s9")}
          onToggle={() => toggle("s9")}
          filled={meta("s9")?.filled ?? 0}
          total={meta("s9")?.total ?? 3}
        >
          <Fld
            label="Opisz własnymi słowami"
            value={brief.impressionCustom}
            onChange={(v) => setBrief({ impressionCustom: v })}
            large={3}
            placeholder="Jakie wrażenie ma zrobić Twoja strona?"
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Co ma pomyśleć?</label>
            <div className="space-y-2">
              {IMPRESSIONS_THINK.map((imp) => (
                <Chk key={imp} on={brief.impThink.includes(imp)} onClick={() => setBrief({ impThink: toggleArray(brief.impThink, imp) })}>
                  <span className="text-sm">{imp}</span>
                </Chk>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Jak ma się poczuć?</label>
            <div className="space-y-2">
              {IMPRESSIONS_FEEL.map((imp) => (
                <Chk key={imp} on={brief.impFeel.includes(imp)} onClick={() => setBrief({ impFeel: toggleArray(brief.impFeel, imp) })}>
                  <span className="text-sm">{imp}</span>
                </Chk>
              ))}
            </div>
          </div>
        </AccordionRow>
      )}

      {/* ───── S10: Podstrony ───── */}
      {show("s10") && (
        <AccordionRow
          num={num("s10")}
          title="Podstrony"
          isOpen={openSections.has("s10")}
          onToggle={() => toggle("s10")}
          filled={meta("s10")?.filled ?? 0}
          total={meta("s10")?.total ?? 1}
        >
          <Fld
            label="Propozycja podstron (opcjonalne)"
            value={brief.menuProposal || ""}
            onChange={(v) => setBrief({ menuProposal: v })}
            large={3}
            placeholder="np. Strona główna, O nas, Oferta, Kontakt..."
          />
          <Chk on={brief.openToAI || false} onClick={() => setBrief({ openToAI: !brief.openToAI })}>
            <span className="text-sm">Jestem otwarty na propozycje AI</span>
          </Chk>
        </AccordionRow>
      )}

      {/* ───── S11: Dodatkowe życzenia ───── */}
      {show("s11") && (
        <AccordionRow
          num={num("s11")}
          title="Dodatkowe życzenia"
          isOpen={openSections.has("s11")}
          onToggle={() => toggle("s11")}
          filled={meta("s11")?.filled ?? 0}
          total={meta("s11")?.total ?? 1}
        >
          <Fld
            label="Cokolwiek ważnego chcesz dodać?"
            value={brief.extraWishes || ""}
            onChange={(v) => setBrief({ extraWishes: v })}
            large={6}
            placeholder="Funkcjonalności, inspiracje, ograniczenia — wszystko co ważne..."
          />
        </AccordionRow>
      )}

      {/* ───── Przycisk DALEJ ───── */}
      <div className="pt-4 pb-8">
        <Btn
          disabled={!canProceed}
          onClick={() => {
            saveBrief();
            navigate(`/creator/${projectId}/step/2`);
          }}
          className="w-full py-3"
        >
          Dalej →
        </Btn>
      </div>
    </div>
  );
}
