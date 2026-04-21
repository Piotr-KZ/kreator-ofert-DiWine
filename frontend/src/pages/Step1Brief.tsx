import { useNavigate, useParams } from "react-router-dom";
import { useLabStore } from "@/store/labStore";

const TONES = [
  { value: "profesjonalny", label: "Profesjonalny" },
  { value: "przyjazny", label: "Przyjazny" },
  { value: "formalny", label: "Formalny" },
  { value: "kreatywny", label: "Kreatywny" },
  { value: "techniczny", label: "Techniczny" },
];

export default function Step1Brief() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { brief, style, siteType, setBrief, setStyle, setSiteType, saveBrief, isGenerating, generateStructure } = useLabStore();

  const handleNext = async () => {
    await saveBrief();
    await generateStructure();
    navigate(`/lab/${projectId}/step/2`);
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-xl font-bold text-gray-800">Brief + Styl wizualny</h1>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Opis firmy / produktu *
        </label>
        <textarea
          rows={4}
          value={brief.description}
          onChange={(e) => setBrief("description", e.target.value)}
          placeholder="Czym sie zajmuje firma? Jakie produkty/uslugi oferuje?"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-emerald-400 resize-none"
        />
      </div>

      {/* Target */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Dla kogo jest ta strona? *
        </label>
        <textarea
          rows={2}
          value={brief.target_audience}
          onChange={(e) => setBrief("target_audience", e.target.value)}
          placeholder="Kim sa klienci? Jakie maja potrzeby?"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-emerald-400 resize-none"
        />
      </div>

      {/* USP */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Co Cie wyroznia?
        </label>
        <textarea
          rows={2}
          value={brief.usp}
          onChange={(e) => setBrief("usp", e.target.value)}
          placeholder="Czym rozni sie od konkurencji?"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-emerald-400 resize-none"
        />
      </div>

      {/* Row: Tone + Site type */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ton komunikacji</label>
          <select
            value={brief.tone}
            onChange={(e) => setBrief("tone", e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-emerald-400 bg-white"
          >
            {TONES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Typ strony</label>
          <select
            value={siteType}
            onChange={(e) => setSiteType(e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-emerald-400 bg-white"
          >
            <option value="company_card">Wizytowka firmowa</option>
            <option value="company">Strona firmowa</option>
            <option value="lp_product">LP (produkt)</option>
            <option value="lp_service">LP (usluga)</option>
            <option value="expert">Strona eksperta</option>
          </select>
        </div>
      </div>

      {/* Colors */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Kolor glowny</label>
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={style.primary_color}
              onChange={(e) => setStyle("primary_color", e.target.value)}
              className="w-10 h-10 rounded-lg border border-gray-200 cursor-pointer"
            />
            <input
              type="text"
              value={style.primary_color}
              onChange={(e) => setStyle("primary_color", e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-200 rounded-xl text-sm font-mono"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Kolor drugorzedny</label>
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={style.secondary_color}
              onChange={(e) => setStyle("secondary_color", e.target.value)}
              className="w-10 h-10 rounded-lg border border-gray-200 cursor-pointer"
            />
            <input
              type="text"
              value={style.secondary_color}
              onChange={(e) => setStyle("secondary_color", e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-200 rounded-xl text-sm font-mono"
            />
          </div>
        </div>
      </div>

      {/* Submit */}
      <div className="pt-4">
        <button
          onClick={handleNext}
          disabled={!brief.description.trim() || isGenerating}
          className="w-full py-3 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {isGenerating ? "AI generuje strukture..." : "Generuj strukture →"}
        </button>
      </div>
    </div>
  );
}
