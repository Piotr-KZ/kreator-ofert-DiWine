/**
 * Step 1 — "Opowiedz o swojej firmie" — 11 cascading questions.
 * Brief 32: biggest step, data saved to project.brief_json.
 */

import { useNavigate, useParams } from "react-router-dom";
import Btn from "@/components/ui/Btn";
import Chk from "@/components/ui/Chk";
import Fld from "@/components/ui/Fld";
import Rad from "@/components/ui/Rad";
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

export default function Step1Brief() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { brief, setBrief, saveBrief } = useCreatorStore();

  // Auto-save brief every 2s
  useAutoSave(brief, saveBrief, 2000);

  const canProceed = brief.forWhom && brief.siteType && brief.companyName && brief.industry;

  const toggleArray = (arr: string[], item: string): string[] =>
    arr.includes(item) ? arr.filter((i) => i !== item) : [...arr, item];

  const showSubpages =
    brief.forWhom === "firma" &&
    !brief.siteType.startsWith("lp-") &&
    brief.siteType !== "wizytowka";

  return (
    <div className="max-w-3xl mx-auto py-8 px-6 space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Opowiedz o swojej firmie</h1>
        <p className="text-sm text-gray-500 mt-1">
          Im więcej nam powiesz, tym lepszą stronę stworzymy.
        </p>
      </div>

      {/* ───── Punkt 1: Rodzaj strony ───── */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">1. Dla kogo tworzymy stronę?</h2>
        <div className="grid grid-cols-3 gap-3">
          <Rad on={brief.forWhom === "firma"} onClick={() => setBrief({ forWhom: "firma", siteType: "" })}>
            <span className="font-medium">Firma</span>
          </Rad>
          <Rad on={brief.forWhom === "osoba"} onClick={() => setBrief({ forWhom: "osoba", siteType: "" })}>
            <span className="font-medium">Osoba</span>
          </Rad>
          <Rad on={brief.forWhom === "sklep"} onClick={() => {}}>
            <span className="font-medium text-gray-400">Sklep (wkrótce)</span>
          </Rad>
        </div>

        {brief.forWhom === "firma" && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {SITE_TYPES_FIRMA.map((t) => (
              <Tile key={t.id} on={brief.siteType === t.id} onClick={() => setBrief({ siteType: t.id })}>
                <div className="font-medium text-sm">{t.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{t.desc}</div>
              </Tile>
            ))}
          </div>
        )}

        {brief.forWhom === "osoba" && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {SITE_TYPES_OSOBA.map((t) => (
              <Tile key={t.id} on={brief.siteType === t.id} onClick={() => setBrief({ siteType: t.id })}>
                <div className="font-medium text-sm">{t.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{t.desc}</div>
              </Tile>
            ))}
          </div>
        )}
      </section>

      {/* ───── Punkt 2: O firmie ───── */}
      {brief.forWhom && brief.siteType && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">
            2. {brief.forWhom === "osoba" ? "Opowiedz o sobie" : "Opowiedz o firmie"}
          </h2>
          <Fld
            label={brief.forWhom === "osoba" ? "Imię i nazwisko" : "Nazwa firmy"}
            placeholder={brief.forWhom === "osoba" ? "Jan Kowalski" : "Acme Sp. z o.o."}
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
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
            >
              <option value="">Wybierz branżę...</option>
              {INDUSTRIES.map((ind) => (
                <option key={ind} value={ind}>{ind}</option>
              ))}
            </select>
          </div>
        </section>
      )}

      {/* ───── Punkt 3: Klienci ───── */}
      {brief.industry && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">3. Kim są Twoi klienci?</h2>
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
        </section>
      )}

      {/* ───── Punkt 4: Profil behawioralny ───── */}
      {brief.clientTypes.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">4. Profil behawioralny klienta</h2>
          <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 text-sm text-indigo-800">
            Zrozumienie motywacji klientów pomoże AI dopasować ton komunikacji i treści strony do ich potrzeb.
          </div>
          <Fld label="Co klienci cenią najbardziej?" value={brief.clientValues} onChange={(v) => setBrief({ clientValues: v })} large={3} placeholder="np. Jakość, terminowość, profesjonalizm..." />
          <Fld label="Co ich przyciąga, co im się podoba?" value={brief.clientLikes} onChange={(v) => setBrief({ clientLikes: v })} large={3} placeholder="np. Nowoczesne podejście, transparentność..." />
          <Fld label="Co ich denerwuje, czego nie lubią?" value={brief.clientDislikes} onChange={(v) => setBrief({ clientDislikes: v })} large={3} placeholder="np. Ukryte koszty, brak kontaktu..." />
          <Fld label="Jakie mają potrzeby i wartości?" value={brief.clientNeeds} onChange={(v) => setBrief({ clientNeeds: v })} large={3} placeholder="np. Szukają partnera na lata, cenią bezpieczeństwo..." />
        </section>
      )}

      {/* ───── Punkt 5: USP ───── */}
      {brief.clientValues && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">5. Co Cię wyróżnia?</h2>
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
        </section>
      )}

      {/* ───── Punkt 6: Pozycjonowanie marki ───── */}
      {brief.usp && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">6. Pozycjonowanie marki</h2>
          <div className="space-y-2">
            {BRAND_POSITIONS.map((bp) => (
              <Rad key={bp.id} on={brief.brandPos === bp.id} onClick={() => setBrief({ brandPos: bp.id })}>
                <div>
                  <div className="font-medium text-sm">{bp.label}</div>
                  <div className="text-xs text-gray-500">{bp.desc}</div>
                </div>
              </Rad>
            ))}
          </div>
        </section>
      )}

      {/* ───── Punkt 7: Styl komunikacji ───── */}
      {brief.brandPos && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">7. Styl komunikacji</h2>
          <div className="space-y-2">
            {WRITING_STYLES.map((ws) => (
              <Rad key={ws.id} on={brief.writingStyle === ws.id} onClick={() => setBrief({ writingStyle: ws.id })}>
                <div>
                  <div className="font-medium text-sm">{ws.label}</div>
                  <div className="text-xs text-gray-500 italic">"{ws.example}"</div>
                </div>
              </Rad>
            ))}
          </div>
        </section>
      )}

      {/* ───── Punkt 8: Cel strony + zawartość ───── */}
      {brief.writingStyle && (
        <section className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-800">8. Cel strony</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {SITE_GOALS.map((g) => (
                <Tile key={g.id} on={brief.mainGoal === g.id} onClick={() => setBrief({ mainGoal: g.id })}>
                  <div className="font-medium text-sm">{g.label}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{g.desc}</div>
                </Tile>
              ))}
            </div>
          </div>
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">Co ma zawierać strona?</label>
            <div className="grid grid-cols-2 gap-2">
              {SITE_CONTENT.map((c) => (
                <Chk key={c} on={brief.siteContent.includes(c)} onClick={() => setBrief({ siteContent: toggleArray(brief.siteContent, c) })}>
                  <span className="text-sm">{c}</span>
                </Chk>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ───── Punkt 9: Wrażenia ───── */}
      {brief.mainGoal && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">9. Co ma pomyśleć i poczuć klient?</h2>
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
        </section>
      )}

      {/* ───── Punkt 10: Podstrony (warunkowy) ───── */}
      {brief.mainGoal && showSubpages && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">10. Podstrony</h2>
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
        </section>
      )}

      {/* ───── Punkt 11: Dodatkowe życzenia ───── */}
      {brief.mainGoal && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800">
            {showSubpages ? "11" : "10"}. Dodatkowe życzenia
          </h2>
          <Fld
            label="Cokolwiek ważnego chcesz dodać?"
            value={brief.extraWishes || ""}
            onChange={(v) => setBrief({ extraWishes: v })}
            large={6}
            placeholder="Funkcjonalności, inspiracje, ograniczenia — wszystko co ważne..."
          />
        </section>
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
          Świetnie! Pokaż nam swoje materiały →
        </Btn>
      </div>
    </div>
  );
}
