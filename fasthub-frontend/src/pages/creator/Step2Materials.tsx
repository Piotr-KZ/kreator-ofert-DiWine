/**
 * Step 2 — "Pokaż co masz" — materials upload + links.
 * Brief 32: uploads, links, inspiration, content vision.
 */

import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Btn from "@/components/ui/Btn";
import Fld from "@/components/ui/Fld";
import FileDropZone from "@/components/creator/FileDropZone";
import { useAutoSave } from "@/hooks/useAutoSave";
import { useCreatorStore } from "@/store/creatorStore";

export default function Step2Materials() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { brief, setBrief, saveBrief, materials, uploadMaterial, addLink, deleteMaterial } =
    useCreatorStore();

  // URLs state
  const [websiteUrls, setWebsiteUrls] = useState<string[]>([""]);
  const [competitorUrls, setCompetitorUrls] = useState<string[]>([""]);
  const [inspirationUrls, setInspirationUrls] = useState<string[]>([""]);
  const [inspirationComment, setInspirationComment] = useState("");

  // Auto-save content vision
  useAutoSave(brief.contentVision, saveBrief, 2000);

  const handleUpload = async (files: File[], type: string) => {
    for (const file of files) {
      await uploadMaterial(file, type);
    }
  };

  const handleAddUrl = async (url: string, type: string, description?: string) => {
    if (!url.trim()) return;
    await addLink(url.trim(), type, description);
  };

  const materialsByType = (type: string) =>
    materials.filter((m) => m.type === type);

  return (
    <div className="max-w-3xl mx-auto py-8 px-6 space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Pokaż nam swoje materiały</h1>
        <p className="text-sm text-gray-500 mt-1">
          Dodaj logo, zdjęcia, dokumenty i linki — AI wykorzysta je przy tworzeniu strony.
        </p>
      </div>

      {/* Obecne strony www */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-800">Twoje obecne strony www</h2>
        {websiteUrls.map((url, i) => (
          <div key={i} className="flex gap-2">
            <Fld
              placeholder="https://www.twoja-strona.pl"
              value={url}
              onChange={(v) => {
                const arr = [...websiteUrls];
                arr[i] = v;
                setWebsiteUrls(arr);
              }}
              type="url"
              className="flex-1"
            />
            <Btn
              variant="ghost"
              onClick={() => {
                handleAddUrl(url, "link");
                const arr = [...websiteUrls];
                arr[i] = "";
                setWebsiteUrls(arr);
              }}
              disabled={!url.trim()}
            >
              Dodaj
            </Btn>
          </div>
        ))}
        <button
          onClick={() => setWebsiteUrls([...websiteUrls, ""])}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Dodaj kolejną stronę
        </button>
        <MaterialList items={materialsByType("link")} onDelete={deleteMaterial} />
      </section>

      {/* Logo */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-800">Logo firmy</h2>
        <FileDropZone
          onFiles={(files) => handleUpload(files, "logo")}
          accept=".png,.jpg,.jpeg,.svg,.webp"
          multiple={false}
          hint="PNG, JPG, SVG — najlepiej transparentne tło"
        />
        <MaterialList items={materialsByType("logo")} onDelete={deleteMaterial} />
      </section>

      {/* Zdjęcia */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-800">Zdjęcia, grafiki, filmy</h2>
        <FileDropZone
          onFiles={(files) => handleUpload(files, "photo")}
          accept=".jpg,.jpeg,.png,.svg,.webp,.mp4,.mov"
          hint="JPG, PNG, SVG, MP4, MOV — max 50 MB"
        />
        <MaterialList items={materialsByType("photo")} onDelete={deleteMaterial} />
      </section>

      {/* Dokumenty */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-800">Oferty, prezentacje, opisy</h2>
        <FileDropZone
          onFiles={(files) => handleUpload(files, "document")}
          accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx"
          hint="PDF, Word, PowerPoint, Excel"
        />
        <MaterialList items={materialsByType("document")} onDelete={deleteMaterial} />
      </section>

      {/* Wizja treści */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-800">Wizja treści</h2>
        <Fld
          placeholder="Opisz jakie treści chcesz mieć na stronie. Co jest ważne? Jakie hasła, sekcje?"
          value={brief.contentVision || ""}
          onChange={(v) => setBrief({ contentVision: v })}
          large={5}
        />
      </section>

      {/* Konkurencja */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-800">Strony konkurencji</h2>
        {competitorUrls.map((url, i) => (
          <div key={i} className="flex gap-2">
            <Fld
              placeholder="https://www.konkurent.pl"
              value={url}
              onChange={(v) => {
                const arr = [...competitorUrls];
                arr[i] = v;
                setCompetitorUrls(arr);
              }}
              type="url"
              className="flex-1"
            />
            <Btn
              variant="ghost"
              onClick={() => {
                handleAddUrl(url, "competitor");
                const arr = [...competitorUrls];
                arr[i] = "";
                setCompetitorUrls(arr);
              }}
              disabled={!url.trim()}
            >
              Dodaj
            </Btn>
          </div>
        ))}
        <button
          onClick={() => setCompetitorUrls([...competitorUrls, ""])}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Dodaj kolejną stronę
        </button>
        <MaterialList items={materialsByType("competitor")} onDelete={deleteMaterial} />
      </section>

      {/* Inspiracje */}
      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-800">Inspiracje wizualne</h2>
        {inspirationUrls.map((url, i) => (
          <div key={i} className="flex gap-2">
            <Fld
              placeholder="https://www.inspiracja.pl"
              value={url}
              onChange={(v) => {
                const arr = [...inspirationUrls];
                arr[i] = v;
                setInspirationUrls(arr);
              }}
              type="url"
              className="flex-1"
            />
            <Btn
              variant="ghost"
              onClick={() => {
                handleAddUrl(url, "inspiration", inspirationComment);
                const arr = [...inspirationUrls];
                arr[i] = "";
                setInspirationUrls(arr);
              }}
              disabled={!url.trim()}
            >
              Dodaj
            </Btn>
          </div>
        ))}
        <button
          onClick={() => setInspirationUrls([...inspirationUrls, ""])}
          className="text-sm text-indigo-600 hover:text-indigo-700"
        >
          + Dodaj kolejną inspirację
        </button>
        <Fld
          label="Co Ci się w nich podoba?"
          value={inspirationComment}
          onChange={setInspirationComment}
          large={3}
          placeholder="Kolory, układ, czcionki, styl..."
        />
        <MaterialList items={materialsByType("inspiration")} onDelete={deleteMaterial} />
      </section>

      {/* Przycisk DALEJ */}
      <div className="pt-4 pb-8">
        <Btn
          onClick={() => navigate(`/creator/${projectId}/step/3`)}
          className="w-full py-3"
        >
          Dalej — dobierzmy styl wizualny →
        </Btn>
      </div>
    </div>
  );
}

// ─── Helper: Material list with delete ───

function MaterialList({
  items,
  onDelete,
}: {
  items: { id: string; original_filename?: string; external_url?: string; file_size?: number }[];
  onDelete: (id: string) => void;
}) {
  if (!items.length) return null;
  return (
    <div className="space-y-1">
      {items.map((m) => (
        <div key={m.id} className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2 text-sm">
          <span className="text-gray-700 truncate">
            {m.original_filename || m.external_url || "Plik"}
            {m.file_size ? ` (${(m.file_size / 1024).toFixed(0)} KB)` : ""}
          </span>
          <button onClick={() => onDelete(m.id)} className="text-gray-400 hover:text-red-500 ml-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
