import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";
import * as api from "@/api/client";

/** Dane bloku z API /blocks */
interface BlockInfo {
  code: string;
  category_code: string;
  name: string;
  description: string;
  media_type: string;
  layout_type: string;
  size: string;
}

/** Mapa category_code → polska nazwa */
const CAT_LABELS: Record<string, string> = {
  NA: "Nawigacja",
  HE: "Hero",
  FI: "O firmie",
  OF: "Oferta",
  CE: "Cennik",
  ZE: "Zespół",
  OP: "Opinie",
  FA: "FAQ",
  CT: "CTA",
  KO: "Kontakt",
  FO: "Stopka",
  GA: "Galeria",
  RE: "Realizacje",
  PR: "Proces",
  PB: "Problem",
  RO: "Rozwiązanie",
  KR: "Korzyści",
  CF: "Cechy",
  OB: "Obiekcje",
  LO: "Loga klientów",
  ST: "Statystyki",
};

/** Wireframe SVG per layout pattern */
function LayoutWireframe({ block }: { block: BlockInfo | undefined }) {
  if (!block) {
    return <UnknownLayout />;
  }

  const lt = block.layout_type || "";
  const mt = block.media_type || "none";
  const cat = block.category_code;

  // Navigation — sticky bar
  if (cat === "NA") return <NavLayout />;
  // Footer
  if (cat === "FO") return <FooterLayout />;

  // Split layouts: text + photo
  if (lt.includes("photo-full-2") || lt.includes("photo-left") || lt.includes("photo-right")) {
    return <SplitLayout mediaRight={!lt.includes("-left") && !lt.includes("FI2")} />;
  }

  // 3-column card grids
  if (lt.includes("-3") || lt.includes("info-title-text-3")) return <GridLayout cols={3} hasIcons={mt === "icons" || mt === "infographic"} />;

  // 4-column grids (team, stats)
  if (lt.includes("-4") || cat === "ST") return <GridLayout cols={4} hasIcons={false} />;

  // 2-column grids
  if (lt.includes("-2") && !lt.includes("photo-full-2")) return <GridLayout cols={2} hasIcons={false} />;

  // Testimonials
  if (cat === "OP" && lt.includes("opin-top-3")) return <GridLayout cols={3} hasIcons={false} isTestimonial />;
  if (cat === "OP") return <QuoteLayout />;

  // Video full
  if (lt.includes("vid-full") || mt === "video") return <VideoLayout />;

  // FAQ
  if (cat === "FA" || cat === "OB") return <FaqLayout />;

  // CTA
  if (cat === "CT") return <CtaLayout />;

  // Centered hero (text-only, large)
  if (cat === "HE") return <HeroCenteredLayout />;

  // Pricing
  if (cat === "CE") return <GridLayout cols={3} hasIcons={false} isPricing />;

  // Process / timeline
  if (cat === "PR") return <StepsLayout />;

  // Default: centered text block
  return <CenteredTextLayout />;
}

// ─── Layout SVG Components ───

function NavLayout() {
  return (
    <div className="w-full h-full flex items-center px-4 bg-gray-50 rounded">
      <div className="w-6 h-3 bg-gray-400 rounded-sm" />
      <div className="flex-1" />
      <div className="flex gap-2">
        <div className="w-8 h-2 bg-gray-300 rounded-sm" />
        <div className="w-8 h-2 bg-gray-300 rounded-sm" />
        <div className="w-8 h-2 bg-gray-300 rounded-sm" />
      </div>
      <div className="ml-3 w-12 h-4 bg-indigo-400 rounded-sm" />
    </div>
  );
}

function FooterLayout() {
  return (
    <div className="w-full h-full flex items-center justify-between px-4 bg-gray-800 rounded">
      <div className="flex gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="flex flex-col gap-1">
            <div className="w-8 h-1.5 bg-gray-500 rounded-sm" />
            <div className="w-6 h-1 bg-gray-600 rounded-sm" />
            <div className="w-7 h-1 bg-gray-600 rounded-sm" />
          </div>
        ))}
      </div>
    </div>
  );
}

function SplitLayout({ mediaRight }: { mediaRight: boolean }) {
  const textBlock = (
    <div className="flex flex-col justify-center gap-2 flex-1 px-3">
      <div className="w-16 h-2 bg-gray-300 rounded-sm" />
      <div className="w-24 h-3 bg-gray-400 rounded-sm" />
      <div className="w-20 h-1.5 bg-gray-200 rounded-sm" />
      <div className="w-14 h-1.5 bg-gray-200 rounded-sm" />
      <div className="w-12 h-4 bg-indigo-400 rounded-sm mt-1" />
    </div>
  );
  const photoBlock = (
    <div className="flex-1 bg-indigo-100 rounded flex items-center justify-center m-1">
      <svg className="w-8 h-8 text-indigo-300" fill="currentColor" viewBox="0 0 24 24">
        <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z" />
      </svg>
    </div>
  );

  return (
    <div className="w-full h-full flex rounded overflow-hidden bg-gray-50">
      {mediaRight ? (
        <>{textBlock}{photoBlock}</>
      ) : (
        <>{photoBlock}{textBlock}</>
      )}
    </div>
  );
}

function GridLayout({ cols, hasIcons, isTestimonial, isPricing }: { cols: number; hasIcons?: boolean; isTestimonial?: boolean; isPricing?: boolean }) {
  return (
    <div className="w-full h-full flex flex-col bg-gray-50 rounded p-3">
      <div className="w-20 h-2 bg-gray-400 rounded-sm mx-auto mb-2" />
      <div className={`flex-1 grid gap-2`} style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="bg-white rounded border border-gray-200 flex flex-col items-center justify-center p-1.5 gap-1">
            {hasIcons && <div className="w-5 h-5 rounded-full bg-indigo-200" />}
            {isTestimonial && <div className="w-4 h-4 rounded-full bg-gray-300" />}
            {isPricing && <div className="w-6 h-2 bg-indigo-300 rounded-sm" />}
            <div className="w-10 h-1.5 bg-gray-300 rounded-sm" />
            <div className="w-8 h-1 bg-gray-200 rounded-sm" />
          </div>
        ))}
      </div>
    </div>
  );
}

function HeroCenteredLayout() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-800 rounded gap-2 p-3">
      <div className="w-10 h-1.5 bg-gray-500 rounded-sm" />
      <div className="w-28 h-3 bg-gray-300 rounded-sm" />
      <div className="w-20 h-1.5 bg-gray-500 rounded-sm" />
      <div className="w-14 h-4 bg-indigo-500 rounded-sm mt-1" />
    </div>
  );
}

function CtaLayout() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-indigo-500 rounded gap-2 p-3">
      <div className="w-24 h-3 bg-indigo-300 rounded-sm" />
      <div className="w-16 h-1.5 bg-indigo-200 rounded-sm" />
      <div className="w-16 h-5 bg-white rounded-sm mt-1" />
    </div>
  );
}

function VideoLayout() {
  return (
    <div className="w-full h-full flex items-center justify-center bg-gray-900 rounded">
      <div className="w-10 h-10 rounded-full border-2 border-white flex items-center justify-center">
        <div className="w-0 h-0 border-l-[8px] border-l-white border-y-[5px] border-y-transparent ml-1" />
      </div>
    </div>
  );
}

function FaqLayout() {
  return (
    <div className="w-full h-full flex flex-col bg-gray-50 rounded p-3 gap-1.5">
      <div className="w-16 h-2 bg-gray-400 rounded-sm mx-auto mb-1" />
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center gap-2 bg-white rounded border border-gray-200 px-2 py-1">
          <div className="flex-1 w-20 h-1.5 bg-gray-300 rounded-sm" />
          <div className="w-3 h-3 text-gray-400 text-[8px] font-bold">+</div>
        </div>
      ))}
    </div>
  );
}

function StepsLayout() {
  return (
    <div className="w-full h-full flex flex-col bg-gray-50 rounded p-3">
      <div className="w-16 h-2 bg-gray-400 rounded-sm mx-auto mb-2" />
      <div className="flex-1 flex items-center justify-center gap-2">
        {[1, 2, 3, 4].map((n) => (
          <div key={n} className="flex flex-col items-center gap-1">
            <div className="w-5 h-5 rounded-full bg-indigo-400 text-white text-[8px] flex items-center justify-center font-bold">{n}</div>
            <div className="w-8 h-1 bg-gray-300 rounded-sm" />
          </div>
        ))}
      </div>
    </div>
  );
}

function QuoteLayout() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-50 rounded p-3 gap-1">
      <div className="text-2xl text-gray-300 leading-none">"</div>
      <div className="w-24 h-1.5 bg-gray-300 rounded-sm" />
      <div className="w-20 h-1.5 bg-gray-200 rounded-sm" />
      <div className="w-5 h-5 rounded-full bg-gray-300 mt-1" />
      <div className="w-10 h-1 bg-gray-400 rounded-sm" />
    </div>
  );
}

function CenteredTextLayout() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-50 rounded gap-1.5 p-3">
      <div className="w-24 h-2.5 bg-gray-400 rounded-sm" />
      <div className="w-28 h-1.5 bg-gray-200 rounded-sm" />
      <div className="w-20 h-1.5 bg-gray-200 rounded-sm" />
    </div>
  );
}

function UnknownLayout() {
  return (
    <div className="w-full h-full flex items-center justify-center bg-gray-100 rounded">
      <div className="w-6 h-6 text-gray-300">?</div>
    </div>
  );
}

// ─── Main Component ───

export default function Step2Structure() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const {
    sections,
    removeSection,
    reorderSections,
    generateStructure,
    generateVisualConcept,
    isGenerating,
  } = useLabStore();

  const [blocksMap, setBlocksMap] = useState<Record<string, BlockInfo>>({});

  useEffect(() => {
    api.listBlocks().then(({ data }) => {
      const map: Record<string, BlockInfo> = {};
      for (const b of data) map[b.code] = b;
      setBlocksMap(map);
    });
  }, []);

  const moveSection = (idx: number, direction: -1 | 1) => {
    const newIdx = idx + direction;
    if (newIdx < 0 || newIdx >= sections.length) return;
    const ids = sections.map((s) => s.id);
    [ids[idx], ids[newIdx]] = [ids[newIdx], ids[idx]];
    reorderSections(ids);
  };

  const handleNext = async () => {
    await generateVisualConcept();
    navigate(`/lab/${projectId}/step/3`);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-3">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-xl font-bold text-gray-800">Struktura strony</h1>
        <button
          onClick={() => generateStructure()}
          disabled={isGenerating}
          className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600"
        >
          Regeneruj
        </button>
      </div>

      {sections.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p>Brak sekcji. Wygeneruj strukturę w kroku 1.</p>
        </div>
      )}

      {sections.map((section, idx) => {
        const block = blocksMap[section.block_code];
        const catCode = block?.category_code || section.block_code.replace(/\d+/g, "");
        const catLabel = CAT_LABELS[catCode] || catCode;

        return (
          <div
            key={section.id}
            className="flex items-stretch gap-3 bg-white border border-gray-200 rounded-xl overflow-hidden hover:border-gray-300 transition-colors"
          >
            {/* Arrows */}
            <div className="flex flex-col justify-center gap-0.5 pl-3">
              <button
                onClick={() => moveSection(idx, -1)}
                disabled={idx === 0}
                className="text-gray-400 hover:text-gray-600 disabled:opacity-20 text-xs"
              >
                ▲
              </button>
              <button
                onClick={() => moveSection(idx, 1)}
                disabled={idx === sections.length - 1}
                className="text-gray-400 hover:text-gray-600 disabled:opacity-20 text-xs"
              >
                ▼
              </button>
            </div>

            {/* Layout wireframe preview */}
            <div className="w-48 h-24 my-2 flex-shrink-0">
              <LayoutWireframe block={block} />
            </div>

            {/* Info */}
            <div className="flex-1 flex flex-col justify-center py-3 pr-2">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded font-semibold">
                  {section.block_code}
                </span>
                <span className="text-sm font-semibold text-gray-700">
                  {catLabel}
                </span>
              </div>
              <p className="text-xs text-gray-400 leading-snug">
                {block?.name || "Nieznany blok"}
              </p>
              {block?.description && (
                <p className="text-[11px] text-gray-300 mt-0.5 line-clamp-1">
                  {block.description}
                </p>
              )}
            </div>

            {/* Delete */}
            <div className="flex items-center pr-3">
              <button
                onClick={() => {
                  if (confirm("Usunąć tę sekcję?")) removeSection(section.id);
                }}
                className="text-gray-300 hover:text-red-500 text-sm transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
        );
      })}

      <div className="flex justify-between pt-6">
        <button
          onClick={() => navigate(`/lab/${projectId}/step/1`)}
          className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700"
        >
          ← Wstecz
        </button>
        <button
          onClick={handleNext}
          disabled={sections.length === 0 || isGenerating}
          className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {isGenerating ? "AI projektuje wygląd..." : "Dalej → Visual Concept"}
        </button>
      </div>
    </div>
  );
}
