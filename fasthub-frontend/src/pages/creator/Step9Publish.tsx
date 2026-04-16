/**
 * Step9Publish — publish page with summary + success screen.
 * Brief 35: step 9.
 */

import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useCreatorStore } from "@/store/creatorStore";
import type { PublishResult } from "@/types/creator";

export default function Step9Publish() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { project, config, isPublishing, publishProject, exportZip } = useCreatorStore();

  const [result, setResult] = useState<PublishResult | null>(null);

  const hosting = config.hosting;
  const domain = hosting?.domain_type === "custom"
    ? hosting.custom_domain
    : `${hosting?.subdomain || "moja-strona"}.webcreator.site`;
  const deployMethod = hosting?.deploy_method || "auto";

  const handlePublish = async () => {
    const res = await publishProject();
    if (res) setResult(res);
  };

  const handleExportZip = async () => {
    await exportZip();
  };

  // Success screen
  if (result) {
    const shareUrl = encodeURIComponent(result.url);
    const shareText = encodeURIComponent(`Właśnie opublikowałem stronę: ${result.url}`);

    return (
      <div className="max-w-2xl mx-auto p-6 text-center">
        <div className="bg-green-50 rounded-2xl p-10 mb-8">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Strona opublikowana!</h1>
          <p className="text-gray-600 mb-4">Gratulacje! Twoja strona jest już dostępna online.</p>
          <a
            href={result.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium"
          >
            Otwórz stronę: {result.url}
          </a>
        </div>

        {/* Share */}
        <div className="mb-8">
          <p className="text-sm text-gray-500 mb-3">Podziel się:</p>
          <div className="flex justify-center gap-3">
            <a
              href={`https://www.facebook.com/sharer/sharer.php?u=${shareUrl}`}
              target="_blank" rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
            >
              Facebook
            </a>
            <a
              href={`https://www.linkedin.com/sharing/share-offsite/?url=${shareUrl}`}
              target="_blank" rel="noopener noreferrer"
              className="px-4 py-2 bg-blue-700 text-white rounded-lg text-sm hover:bg-blue-800"
            >
              LinkedIn
            </a>
            <a
              href={`https://twitter.com/intent/tweet?text=${shareText}`}
              target="_blank" rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm hover:bg-gray-800"
            >
              X (Twitter)
            </a>
          </div>
        </div>

        {/* Next steps */}
        <div className="flex justify-center gap-3">
          <button
            onClick={() => navigate("/dashboard")}
            className="px-6 py-2.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            Panel zarządzania
          </button>
          <button
            onClick={() => navigate(`/creator/${projectId}/step/6`)}
            className="px-6 py-2.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            Edytuj stronę
          </button>
          <button
            onClick={() => navigate("/creator/new")}
            className="px-6 py-2.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Utwórz kolejną
          </button>
        </div>
      </div>
    );
  }

  // Pre-publish screen
  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Publikacja</h1>
      <p className="text-gray-500 text-sm mb-6">Ostatni krok — opublikuj swoją stronę</p>

      {/* Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4 mb-6">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Nazwa projektu</span>
          <span className="font-medium">{project?.name}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Domena</span>
          <span className="font-medium">{domain}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Metoda wdrożenia</span>
          <span className="font-medium">
            {deployMethod === "auto" ? "Automatycznie (WebCreator)" : deployMethod === "ftp" ? "FTP" : "Pobierz ZIP"}
          </span>
        </div>
      </div>

      {/* Publish or download */}
      <div className="flex flex-col gap-3">
        {deployMethod === "zip" ? (
          <button onClick={handleExportZip}
            className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm font-medium">
            Pobierz ZIP
          </button>
        ) : (
          <>
            <button onClick={handlePublish} disabled={isPublishing}
              className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm font-medium">
              {isPublishing ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Publikuję...
                </span>
              ) : (
                "Opublikuj stronę"
              )}
            </button>
            <button onClick={handleExportZip}
              className="w-full py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm">
              Pobierz kopię ZIP
            </button>
          </>
        )}
      </div>

      {/* Back */}
      <div className="mt-6">
        <button onClick={() => navigate(`/creator/${projectId}/step/8`)}
          className="px-6 py-2.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">
          Wstecz
        </button>
      </div>
    </div>
  );
}
