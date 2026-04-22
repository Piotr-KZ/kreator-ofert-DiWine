import { useEffect, useState, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";
import * as api from "@/api/client";

interface BlockInfo {
  code: string;
  category_code: string;
  name: string;
  description: string;
  media_type: string;
  layout_type: string;
  size: string;
}

const CAT_LABELS: Record<string, string> = {
  NA: "Nawigacja", HE: "Hero", FI: "O firmie", OF: "Oferta", CE: "Cennik",
  ZE: "Zespół", OP: "Opinie", FA: "FAQ", CT: "CTA", KO: "Kontakt",
  FO: "Stopka", GA: "Galeria", RE: "Realizacje", PR: "Proces", PB: "Problem",
  RO: "Rozwiązanie", KR: "Korzyści", CF: "Cechy", OB: "Obiekcje",
  LO: "Loga klientów", ST: "Statystyki",
};

/** Wireframe per layout */
function LayoutWireframe({ block }: { block: BlockInfo | undefined }) {
  if (!block) return <div className="w-full h-full flex items-center justify-center rounded text-gray-300 text-xs">?</div>;
  const lt = block.layout_type || "";
  const mt = block.media_type || "none";
  const cat = block.category_code;

  if (cat === "NA") return (
    <div className="w-full h-full flex items-center px-4 rounded">
      <div className="w-6 h-3 bg-gray-400 rounded-sm" /><div className="flex-1" />
      <div className="flex gap-2">{[1,2,3].map(i=><div key={i} className="w-8 h-2 bg-gray-300 rounded-sm"/>)}</div>
      <div className="ml-3 w-12 h-4 bg-indigo-400 rounded-sm" />
    </div>
  );
  if (cat === "FO") return (
    <div className="w-full h-full flex items-center px-4 rounded">
      <div className="flex gap-6">{[1,2,3,4].map(i=><div key={i} className="flex flex-col gap-1"><div className="w-8 h-1.5 bg-gray-500 rounded-sm"/><div className="w-6 h-1 bg-gray-600 rounded-sm"/></div>)}</div>
    </div>
  );
  if (lt.includes("photo-full-2") || lt.includes("photo-left") || lt.includes("photo-right")) {
    const right = !lt.includes("-left") && !lt.includes("FI2");
    const text = <div className="flex flex-col justify-center gap-2 flex-1 px-3"><div className="w-16 h-2 bg-gray-300 rounded-sm"/><div className="w-24 h-3 bg-gray-400 rounded-sm"/><div className="w-20 h-1.5 bg-gray-200 rounded-sm"/><div className="w-12 h-4 bg-indigo-400 rounded-sm mt-1"/></div>;
    const photo = <div className="flex-1 bg-indigo-100 rounded flex items-center justify-center m-1"><svg className="w-8 h-8 text-indigo-300" fill="currentColor" viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg></div>;
    return <div className="w-full h-full flex rounded overflow-hidden">{right ? <>{text}{photo}</> : <>{photo}{text}</>}</div>;
  }
  if (lt.includes("-3") || lt.includes("info-title-text-3")) return <GridWire cols={3} hasIcons={mt==="icons"||mt==="infographic"}/>;
  if (lt.includes("-4") || cat === "ST") return <GridWire cols={4}/>;
  if (lt.includes("-2") && !lt.includes("photo-full-2")) return <GridWire cols={2}/>;
  if (cat === "OP") return <div className="w-full h-full flex flex-col items-center justify-center rounded p-3 gap-1"><div className="text-2xl text-gray-300 leading-none">"</div><div className="w-24 h-1.5 bg-gray-300 rounded-sm"/><div className="w-5 h-5 rounded-full bg-gray-300 mt-1"/></div>;
  if (cat === "FA" || cat === "OB") return <div className="w-full h-full flex flex-col rounded p-3 gap-1.5"><div className="w-16 h-2 bg-gray-400 rounded-sm mx-auto mb-1"/>{[1,2,3].map(i=><div key={i} className="flex items-center gap-2 bg-white/50 rounded border border-gray-200 px-2 py-1"><div className="flex-1 h-1.5 bg-gray-300 rounded-sm"/><div className="text-gray-400 text-[8px] font-bold">+</div></div>)}</div>;
  if (cat === "CT") return <div className="w-full h-full flex flex-col items-center justify-center rounded gap-2 p-3"><div className="w-24 h-3 bg-gray-300 rounded-sm"/><div className="w-16 h-5 bg-indigo-400 rounded-sm mt-1"/></div>;
  if (cat === "HE") return <div className="w-full h-full flex flex-col items-center justify-center rounded gap-2 p-3"><div className="w-28 h-3 bg-gray-300 rounded-sm"/><div className="w-20 h-1.5 bg-gray-400 rounded-sm"/><div className="w-14 h-4 bg-indigo-500 rounded-sm mt-1"/></div>;
  if (cat === "CE") return <GridWire cols={3} isPricing/>;
  if (cat === "PR") return <div className="w-full h-full flex flex-col rounded p-3"><div className="w-16 h-2 bg-gray-400 rounded-sm mx-auto mb-2"/><div className="flex-1 flex items-center justify-center gap-2">{[1,2,3,4].map(n=><div key={n} className="flex flex-col items-center gap-1"><div className="w-5 h-5 rounded-full bg-indigo-400 text-white text-[8px] flex items-center justify-center font-bold">{n}</div><div className="w-8 h-1 bg-gray-300 rounded-sm"/></div>)}</div></div>;
  return <div className="w-full h-full flex flex-col items-center justify-center rounded gap-1.5 p-3"><div className="w-24 h-2.5 bg-gray-400 rounded-sm"/><div className="w-28 h-1.5 bg-gray-200 rounded-sm"/></div>;
}

function GridWire({ cols, hasIcons, isPricing }: { cols: number; hasIcons?: boolean; isPricing?: boolean }) {
  return (
    <div className="w-full h-full flex flex-col rounded p-3">
      <div className="w-20 h-2 bg-gray-400 rounded-sm mx-auto mb-2" />
      <div className="flex-1 grid gap-2" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="bg-white/50 rounded border border-gray-200 flex flex-col items-center justify-center p-1.5 gap-1">
            {hasIcons && <div className="w-5 h-5 rounded-full bg-indigo-200" />}
            {isPricing && <div className="w-6 h-2 bg-indigo-300 rounded-sm" />}
            <div className="w-10 h-1.5 bg-gray-300 rounded-sm" />
            <div className="w-8 h-1 bg-gray-200 rounded-sm" />
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Add Section Picker ───

function AddSectionPicker({ blocksList, onAdd, onCancel }: {
  blocksList: BlockInfo[];
  onAdd: (code: string) => void;
  onCancel: () => void;
}) {
  const [selectedCat, setSelectedCat] = useState<string | null>(null);
  const categories = [...new Set(blocksList.map((b) => b.category_code))];
  const blocksInCat = selectedCat ? blocksList.filter((b) => b.category_code === selectedCat) : [];

  return (
    <div className="bg-white border border-dashed border-emerald-300 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">
          {selectedCat ? `Wybierz klocek: ${CAT_LABELS[selectedCat] || selectedCat}` : "Wybierz kategorię sekcji"}
        </span>
        <button onClick={() => selectedCat ? setSelectedCat(null) : onCancel()} className="text-xs text-gray-400 hover:text-gray-600">
          {selectedCat ? "← Wróć" : "Anuluj"}
        </button>
      </div>
      {!selectedCat ? (
        <div className="grid grid-cols-4 gap-2">
          {categories.map((cat) => (
            <button key={cat} onClick={() => setSelectedCat(cat)} className="px-3 py-2 text-xs border border-gray-200 rounded-lg hover:bg-emerald-50 hover:border-emerald-300 hover:text-emerald-700 text-gray-600 text-center transition-colors">
              {CAT_LABELS[cat] || cat}
            </button>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-2">
          {blocksInCat.map((b) => (
            <button key={b.code} onClick={() => onAdd(b.code)} className="px-3 py-2 text-left border border-gray-200 rounded-lg hover:bg-emerald-50 hover:border-emerald-300 transition-colors">
              <span className="text-xs font-mono font-semibold text-indigo-600">{b.code}</span>
              <span className="text-xs text-gray-500 ml-2">{b.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Hex to tint ───

function tintBg(hex: string, opacity: number = 0.12): string {
  const c = hex.replace("#", "");
  const r = parseInt(c.substr(0, 2), 16);
  const g = parseInt(c.substr(2, 2), 16);
  const b = parseInt(c.substr(4, 2), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// ─── Main Component ───

export default function Step3Structure() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const {
    sections, removeSection, reorderSections, generateStructure,
    addSection, updateSection, style, setStyle, saveBrief,
    isGenerating, error, setError,
  } = useLabStore();

  const [blocksMap, setBlocksMap] = useState<Record<string, BlockInfo>>({});
  const [blocksList, setBlocksList] = useState<BlockInfo[]>([]);
  const [addingAt, setAddingAt] = useState<number | null>(null);
  const startedRef = useRef(false);

  const bgColor = style.primary_color;

  useEffect(() => {
    api.listBlocks().then(({ data }) => {
      const map: Record<string, BlockInfo> = {};
      for (const b of data) map[b.code] = b;
      setBlocksMap(map);
      setBlocksList(data);
    });
  }, []);

  useEffect(() => {
    if (sections.length === 0 && !isGenerating && !startedRef.current) {
      startedRef.current = true;
      setError(null);
      generateStructure();
    }
  }, [sections.length, isGenerating]);

  const moveSection = (idx: number, dir: -1 | 1) => {
    const n = idx + dir;
    if (n < 0 || n >= sections.length) return;
    const ids = sections.map((s) => s.id);
    [ids[idx], ids[n]] = [ids[n], ids[idx]];
    reorderSections(ids);
  };

  const changeBlock = (sectionId: string, newCode: string) => {
    updateSection(sectionId, { block_code: newCode });
  };

  const handleColorChange = (val: string) => {
    setStyle("primary_color", val);
    saveBrief();
  };

  const handleAddSection = async (code: string, afterIdx: number) => {
    await addSection(code, afterIdx + 1);
    setAddingAt(null);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h1 className="text-xl font-bold text-gray-800">Struktura strony</h1>
        <button
          onClick={() => { setError(null); startedRef.current = true; generateStructure(); }}
          disabled={isGenerating}
          className="text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 disabled:opacity-50"
        >
          {isGenerating ? "Generowanie..." : "Regeneruj strukturę"}
        </button>
      </div>

      {/* Single color picker — one field */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-4">
        <span className="text-sm font-medium text-gray-700">Kolor sekcji:</span>
        <input
          type="color"
          value={bgColor}
          onChange={(e) => handleColorChange(e.target.value)}
          className="w-10 h-10 rounded-lg border border-gray-200 cursor-pointer"
        />
        <span className="text-xs font-mono text-gray-400">{bgColor}</span>
      </div>

      {/* Loading */}
      {isGenerating && sections.length === 0 && (
        <div className="text-center py-16">
          <div className="inline-flex items-center gap-3 bg-emerald-50 text-emerald-700 px-6 py-4 rounded-xl">
            <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span className="text-sm font-medium">AI generuje strukturę strony...</span>
          </div>
        </div>
      )}

      {/* Error */}
      {!isGenerating && error && sections.length === 0 && (
        <div className="text-center py-12 space-y-4">
          <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-5 py-3 rounded-xl border border-red-200">
            <span>✗</span><span className="text-sm">{error}</span>
          </div>
          <div>
            <button onClick={() => { setError(null); generateStructure(); }} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">
              Spróbuj ponownie
            </button>
          </div>
        </div>
      )}

      {/* Empty */}
      {!isGenerating && !error && sections.length === 0 && (
        <div className="text-center py-12 space-y-4">
          <p className="text-gray-400 text-sm">Brak sekcji.</p>
          <button onClick={() => generateStructure()} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">Generuj strukturę</button>
        </div>
      )}

      {/* Sections */}
      {sections.map((section, idx) => {
        const block = blocksMap[section.block_code];
        const catCode = block?.category_code || section.block_code.replace(/\d+/g, "");
        const catLabel = CAT_LABELS[catCode] || catCode;
        const sameCatBlocks = blocksList.filter((b) => b.category_code === catCode);

        return (
          <div key={section.id}>
            {/* Section card — wireframe colored, description white, vertical line separator */}
            <div className="border border-gray-200 rounded-xl overflow-hidden hover:border-gray-300 transition-all flex">
              {/* Left: arrows */}
              <div className="flex flex-col justify-center gap-1 px-3 bg-white">
                <button onClick={() => moveSection(idx, -1)} disabled={idx === 0} className="text-gray-400 hover:text-gray-600 disabled:opacity-20 text-sm">▲</button>
                <button onClick={() => moveSection(idx, 1)} disabled={idx === sections.length - 1} className="text-gray-400 hover:text-gray-600 disabled:opacity-20 text-sm">▼</button>
              </div>

              {/* Wireframe area — colored background */}
              <div
                className="w-64 h-36 flex-shrink-0 my-0"
                style={{ backgroundColor: tintBg(bgColor, 0.12) }}
              >
                <LayoutWireframe block={block} />
              </div>

              {/* Vertical separator */}
              <div className="w-px bg-gray-200 self-stretch" />

              {/* Description area — white background */}
              <div className="flex-1 flex items-center bg-white">
                <div className="flex-1 flex flex-col justify-center py-4 px-5 gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded font-semibold">
                      {section.block_code}
                    </span>
                    <span className="text-base font-semibold text-gray-700">{catLabel}</span>
                  </div>
                  <p className="text-sm text-gray-400">{block?.name || "Nieznany blok"}</p>

                  {/* Block type selector — same category only */}
                  {sameCatBlocks.length > 1 && (
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-gray-500">Wariant:</label>
                      <select
                        value={section.block_code}
                        onChange={(e) => changeBlock(section.id, e.target.value)}
                        className="text-xs border border-gray-200 rounded-lg px-2 py-1 bg-white max-w-xs"
                      >
                        {sameCatBlocks.map((b) => (
                          <option key={b.code} value={b.code}>{b.code} — {b.name}</option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>

                {/* Delete */}
                <div className="flex items-center pr-4">
                  <button
                    onClick={() => { if (confirm("Usunąć tę sekcję?")) removeSection(section.id); }}
                    className="text-gray-300 hover:text-red-500 text-base transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>

            {/* Add section button */}
            {addingAt === idx ? (
              <div className="my-2">
                <AddSectionPicker
                  blocksList={blocksList}
                  onAdd={(code) => handleAddSection(code, idx)}
                  onCancel={() => setAddingAt(null)}
                />
              </div>
            ) : (
              <div className="flex justify-center my-1">
                <button
                  onClick={() => setAddingAt(idx)}
                  className="flex items-center gap-1 text-xs text-gray-300 hover:text-emerald-600 transition-colors py-1 px-3 rounded-lg hover:bg-emerald-50"
                >
                  <span className="text-base leading-none">+</span>
                  <span>Dodaj sekcję</span>
                </button>
              </div>
            )}
          </div>
        );
      })}

      {/* Add section at the end */}
      {sections.length > 0 && addingAt === null && (
        <div className="flex justify-center">
          <button
            onClick={() => setAddingAt(sections.length - 1)}
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-emerald-600 transition-colors py-2 px-4 rounded-lg hover:bg-emerald-50 border border-dashed border-gray-200 hover:border-emerald-300"
          >
            <span className="text-base leading-none">+</span>
            <span>Dodaj nową sekcję</span>
          </button>
        </div>
      )}

      <div className="flex justify-between pt-6">
        <button onClick={() => navigate(`/lab/${projectId}/step/2`)} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">← Wstecz</button>
        <button onClick={() => navigate(`/lab/${projectId}/step/4`)} disabled={sections.length === 0 || isGenerating} className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors">
          Dalej → Treści
        </button>
      </div>
    </div>
  );
}
