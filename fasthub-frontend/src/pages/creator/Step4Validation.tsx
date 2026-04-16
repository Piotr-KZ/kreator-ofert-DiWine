/**
 * Step 4 — "Sprawdźmy czy wszystko się zgadza" — AI validation + chat.
 * Brief 32: 2-column layout, validation items, AI chat with SSE streaming.
 */

import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Btn from "@/components/ui/Btn";
import { useCreatorStore } from "@/store/creatorStore";

export default function Step4Validation() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const {
    validationItems,
    chatMessages,
    isValidating,
    isChatting,
    aiError,
    runValidation,
    sendChatMessage,
  } = useCreatorStore();

  const [message, setMessage] = useState("");
  const [activeTab, setActiveTab] = useState<"analysis" | "chat">("analysis");
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Run validation on mount
  useEffect(() => {
    if (validationItems.length === 0) {
      runValidation();
    }
  }, []);

  // Scroll chat to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleSendMessage = () => {
    if (!message.trim() || isChatting) return;
    sendChatMessage(message.trim(), "validation");
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const statusIcon = (status: string) => {
    switch (status) {
      case "ok": return <span className="text-green-500 text-lg">&#10003;</span>;
      case "warning": return <span className="text-amber-500 text-lg">&#9888;</span>;
      case "error": return <span className="text-red-500 text-lg">&#10007;</span>;
      default: return null;
    }
  };

  const statusCount = (s: string) => validationItems.filter((i) => i.status === s).length;

  const analysisPanel = (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">Analiza spójności</h2>

      {aiError && (
        <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 mb-4">
          <p className="font-medium">Błąd AI</p>
          <p>{aiError}</p>
        </div>
      )}

      {isValidating ? (
        <div className="flex items-center gap-3 text-gray-500 py-8">
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          AI analizuje Twoje dane...
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {validationItems.map((item) => (
              <div
                key={item.key}
                className={`flex items-start gap-3 p-3 rounded-xl border ${
                  item.status === "ok"
                    ? "border-green-200 bg-green-50"
                    : item.status === "warning"
                      ? "border-amber-200 bg-amber-50"
                      : "border-red-200 bg-red-50"
                }`}
              >
                <div className="flex-shrink-0 mt-0.5">{statusIcon(item.status)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-800">{item.message}</p>
                  {item.suggestion && (
                    <p className="text-xs text-gray-500 mt-1">{item.suggestion}</p>
                  )}
                </div>
                {(item.status === "warning" || item.status === "error") && (
                  <div className="flex gap-1 flex-shrink-0">
                    <button className="text-xs px-2 py-1 rounded bg-white border border-gray-200 hover:bg-gray-50 text-gray-600">
                      Zostaw
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {validationItems.length > 0 && (
            <div className="text-sm text-gray-600 pt-2 border-t border-gray-200">
              Dane spójne — {statusCount("warning")} sugestii, {statusCount("error")} problemów
            </div>
          )}

          <Btn variant="ghost" onClick={() => runValidation()} className="text-sm">
            Sprawdź ponownie
          </Btn>
        </>
      )}
    </div>
  );

  const chatPanel = (
    <div className="flex flex-col h-[500px]">
      <h2 className="text-lg font-semibold text-gray-800 mb-3">Chat z AI</h2>
      <p className="text-xs text-gray-500 mb-3">
        Zapytaj AI o sugestie lub poproś o wyjaśnienie.
      </p>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
        {chatMessages.length === 0 && !isChatting && (
          <div className="text-sm text-gray-400 text-center py-8">
            Zadaj pytanie o swój projekt...
          </div>
        )}
        {chatMessages.map((msg, i) => (
          <div
            key={i}
            className={`rounded-xl px-4 py-3 text-sm max-w-[85%] ${
              msg.role === "user"
                ? "bg-indigo-600 text-white ml-auto"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.content || (isChatting && i === chatMessages.length - 1 ? "..." : "")}</p>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <textarea
          rows={2}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Napisz wiadomość..."
          className="flex-1 px-4 py-2 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 resize-none"
          disabled={isChatting}
        />
        <Btn onClick={handleSendMessage} disabled={!message.trim() || isChatting} className="self-end">
          Wyślij
        </Btn>
      </div>
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto py-8 px-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Sprawdźmy czy wszystko się zgadza</h1>
        <p className="text-sm text-gray-500 mt-1">
          AI przeanalizował Twoje dane. Sprawdź wyniki i zadaj pytania.
        </p>
      </div>

      {/* Mobile: tabs */}
      <div className="md:hidden mb-4">
        <div className="flex bg-gray-100 rounded-xl p-1">
          <button
            onClick={() => setActiveTab("analysis")}
            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
              activeTab === "analysis" ? "bg-white shadow text-gray-900" : "text-gray-500"
            }`}
          >
            Analiza
          </button>
          <button
            onClick={() => setActiveTab("chat")}
            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
              activeTab === "chat" ? "bg-white shadow text-gray-900" : "text-gray-500"
            }`}
          >
            Chat
          </button>
        </div>
      </div>

      {/* Desktop: 2 columns */}
      <div className="hidden md:grid md:grid-cols-2 md:gap-6">
        <div>{analysisPanel}</div>
        <div className="border-l border-gray-200 pl-6">{chatPanel}</div>
      </div>

      {/* Mobile: active tab */}
      <div className="md:hidden">
        {activeTab === "analysis" ? analysisPanel : chatPanel}
      </div>

      {/* Przycisk DALEJ */}
      <div className="pt-8 pb-8">
        <Btn
          disabled={validationItems.length === 0}
          onClick={() => navigate(`/creator/${projectId}/generating`)}
          className="w-full py-3"
        >
          Wszystko OK — AI, stwórz mi stronę! →
        </Btn>
      </div>
    </div>
  );
}
