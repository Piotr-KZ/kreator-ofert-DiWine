/**
 * Step 3 — "Jak ma wyglądać" — visual style selection.
 * Brief 32: palettes, fonts, section themes, edges.
 */

import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Btn from "@/components/ui/Btn";
import Tile from "@/components/ui/Tile";
import { useAutoSave } from "@/hooks/useAutoSave";
import { useCreatorStore } from "@/store/creatorStore";
import { FONT_PAIRS, PALETTE_PRESETS, SECTION_THEMES } from "@/types/creator";

export default function Step3Style() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { style, setStyle, saveStyle } = useCreatorStore();

  // Auto-save style every 2s
  useAutoSave(style, saveStyle, 2000);

  // Load Google Fonts for preview
  useEffect(() => {
    const fonts = FONT_PAIRS.flatMap((p) => [p.heading, p.body]);
    const unique = [...new Set(fonts)];
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = `https://fonts.googleapis.com/css2?${unique.map((f) => `family=${f.replace(/ /g, "+")}`).join("&")}&display=swap`;
    document.head.appendChild(link);
    return () => { document.head.removeChild(link); };
  }, []);

  const isCustomPalette = style.palette_preset === "custom";
  const canProceed = style.palette_preset || style.color_primary;

  return (
    <div className="max-w-3xl mx-auto py-8 px-6 space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Jak ma wyglądać Twoja strona?</h1>
        <p className="text-sm text-gray-500 mt-1">
          Wybierz kolory, czcionki i styl wizualny.
        </p>
      </div>

      {/* Paleta kolorów */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Paleta kolorów</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {PALETTE_PRESETS.map((p) => (
            <Tile
              key={p.id}
              on={style.palette_preset === p.id}
              onClick={() =>
                setStyle({
                  palette_preset: p.id,
                  color_primary: p.colors[0],
                  color_secondary: p.colors[1],
                  color_accent: p.colors[2],
                })
              }
            >
              <div className="flex gap-1.5 mb-2">
                {p.colors.map((c, i) => (
                  <div key={i} className="w-8 h-8 rounded-lg border border-gray-200" style={{ backgroundColor: c }} />
                ))}
              </div>
              <div className="font-medium text-sm">{p.label}</div>
            </Tile>
          ))}
          <Tile on={isCustomPalette} onClick={() => setStyle({ palette_preset: "custom" })}>
            <div className="flex gap-1.5 mb-2">
              <div className="w-8 h-8 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center text-gray-400 text-xs">?</div>
              <div className="w-8 h-8 rounded-lg border-2 border-dashed border-gray-300" />
              <div className="w-8 h-8 rounded-lg border-2 border-dashed border-gray-300" />
            </div>
            <div className="font-medium text-sm">Własne kolory</div>
          </Tile>
        </div>

        {isCustomPalette && (
          <div className="grid grid-cols-3 gap-4 pt-2">
            <ColorPicker label="Dominujący" desc="Tło hero, przyciski, akcenty" value={style.color_primary || "#4F46E5"} onChange={(v) => setStyle({ color_primary: v })} />
            <ColorPicker label="Uzupełniający" desc="Ikony, ramki, sekcje" value={style.color_secondary || "#64748B"} onChange={(v) => setStyle({ color_secondary: v })} />
            <ColorPicker label="Dodatek" desc="Tła, hover, podkreślenia" value={style.color_accent || "#E0E7FF"} onChange={(v) => setStyle({ color_accent: v })} />
          </div>
        )}
      </section>

      {/* Czcionki */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Czcionki</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {FONT_PAIRS.map((fp) => (
            <Tile
              key={fp.id}
              on={style.heading_font === fp.heading && style.body_font === fp.body}
              onClick={() => setStyle({ heading_font: fp.heading, body_font: fp.body })}
            >
              <div className="mb-1" style={{ fontFamily: `'${fp.heading}', sans-serif` }}>
                <span className="text-lg font-bold">Abc</span>
              </div>
              <div style={{ fontFamily: `'${fp.body}', sans-serif` }}>
                <span className="text-sm text-gray-600">Abc tekst</span>
              </div>
              <div className="text-xs text-gray-400 mt-1">{fp.heading} + {fp.body}</div>
            </Tile>
          ))}
        </div>
      </section>

      {/* Motyw sekcji */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Motyw sekcji</h2>
        <div className="grid grid-cols-2 gap-3">
          {SECTION_THEMES.map((theme) => (
            <Tile
              key={theme.id}
              on={style.section_theme === theme.id}
              onClick={() => setStyle({ section_theme: theme.id })}
            >
              <div className="flex gap-0.5 mb-2">
                {theme.bars.map((color, i) => (
                  <div key={i} className="h-6 flex-1 rounded-sm border border-gray-200" style={{ backgroundColor: color }} />
                ))}
              </div>
              <div className="font-medium text-sm">{theme.label}</div>
            </Tile>
          ))}
        </div>
      </section>

      {/* Krawędzie */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Krawędzie</h2>
        <div className="grid grid-cols-2 gap-3">
          <Tile on={style.border_radius === "rounded"} onClick={() => setStyle({ border_radius: "rounded" })}>
            <div className="w-12 h-8 bg-indigo-100 rounded-xl border border-indigo-200 mb-2" />
            <div className="font-medium text-sm">Zaokrąglone</div>
          </Tile>
          <Tile on={style.border_radius === "sharp"} onClick={() => setStyle({ border_radius: "sharp" })}>
            <div className="w-12 h-8 bg-indigo-100 rounded-none border border-indigo-200 mb-2" />
            <div className="font-medium text-sm">Ostre</div>
          </Tile>
        </div>
      </section>

      {/* Przycisk DALEJ */}
      <div className="pt-4 pb-8">
        <Btn
          disabled={!canProceed}
          onClick={() => {
            saveStyle();
            navigate(`/creator/${projectId}/step/4`);
          }}
          className="w-full py-3"
        >
          Dalej — AI sprawdzi spójność →
        </Btn>
      </div>
    </div>
  );
}

// ─── Color picker helper ───

function ColorPicker({
  label,
  desc,
  value,
  onChange,
}: {
  label: string;
  desc: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <p className="text-xs text-gray-400 mb-2">{desc}</p>
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-10 h-10 rounded-lg cursor-pointer border-0"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 px-3 py-2 border-2 border-gray-200 rounded-lg text-sm font-mono"
          maxLength={7}
        />
      </div>
    </div>
  );
}
