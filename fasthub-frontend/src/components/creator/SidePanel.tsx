/**
 * SidePanel — shared right panel for Steps 5 & 6.
 * Brief 34: Chat AI, section list, add section button, style info (step 6).
 */

import { useRef, useEffect, useState } from "react";
import Btn from "@/components/ui/Btn";
import { useCreatorStore } from "@/store/creatorStore";
import type { ProjectSection } from "@/types/creator";

interface SidePanelProps {
  step: 5 | 6;
  onScrollToSection?: (sectionId: string) => void;
  onAddSection: () => void;
  onVisualReview?: () => void;
}

export default function SidePanel({ step, onScrollToSection, onAddSection, onVisualReview }: SidePanelProps) {
  const {
    sections,
    activeSection,
    setActiveSection,
    chatMessages,
    isChatting,
    sendChatMessage,
    style,
  } = useCreatorStore();

  const [chatOpen, setChatOpen] = useState(false);
  const [message, setMessage] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleSend = () => {
    if (!message.trim() || isChatting) return;
    sendChatMessage(message.trim(), "editing");
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSectionClick = (sec: ProjectSection) => {
    setActiveSection(sec.id);
    onScrollToSection?.(sec.id);
  };

  return (
    <aside className="w-[260px] flex-shrink-0 bg-white border-l border-gray-200 flex flex-col h-full overflow-y-auto">
      {/* Chat toggle */}
      <div className="p-3 border-b border-gray-100">
        <button
          onClick={() => setChatOpen(!chatOpen)}
          className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-indigo-50 text-indigo-700 text-sm font-medium hover:bg-indigo-100 transition-colors"
        >
          <span>Chat z AI</span>
          <svg className={`w-4 h-4 transition-transform ${chatOpen ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {chatOpen && (
          <div className="mt-3 flex flex-col h-[280px]">
            <div className="flex-1 overflow-y-auto space-y-2 mb-2 pr-1">
              {chatMessages.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-4">Zadaj pytanie o projekt...</p>
              )}
              {chatMessages.map((msg, i) => (
                <div
                  key={i}
                  className={`rounded-lg px-3 py-2 text-xs max-w-[95%] ${
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
            <div className="flex gap-1">
              <textarea
                rows={2}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Napisz..."
                className="flex-1 px-2 py-1.5 border border-gray-200 rounded-lg text-xs outline-none focus:border-indigo-400 resize-none"
                disabled={isChatting}
              />
              <button
                onClick={handleSend}
                disabled={!message.trim() || isChatting}
                className="px-2 py-1 bg-indigo-600 text-white rounded-lg text-xs hover:bg-indigo-700 disabled:opacity-50 self-end"
              >
                Wyslij
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Visual review button (step 6 only) */}
      {step === 6 && onVisualReview && (
        <div className="px-3 py-2 border-b border-gray-100">
          <button
            onClick={onVisualReview}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-50 text-amber-700 text-sm font-medium hover:bg-amber-100 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Podglad AI
          </button>
        </div>
      )}

      {/* Sections list */}
      <div className="flex-1 p-3">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Sekcje</h3>
        <div className="space-y-0.5">
          {sections.map((sec) => (
            <button
              key={sec.id}
              onClick={() => handleSectionClick(sec)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                activeSection === sec.id
                  ? "bg-indigo-50 text-indigo-700 font-medium"
                  : "text-gray-700 hover:bg-gray-50"
              }`}
            >
              <span className="text-[10px] text-gray-400 font-mono w-6">{sec.block_code}</span>
              <span className="truncate">
                {(sec.slots_json?.title as string) || sec.block_code}
              </span>
            </button>
          ))}
        </div>

        <button
          onClick={onAddSection}
          className="w-full mt-3 flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-lg border-2 border-dashed border-gray-200 text-gray-500 text-sm hover:border-indigo-300 hover:text-indigo-600 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Dodaj sekcje
        </button>
      </div>

      {/* Style info (step 6 only) */}
      {step === 6 && style.color_primary && (
        <div className="p-3 border-t border-gray-100">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Style</h3>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-gray-600">Kolory:</span>
            <div className="flex gap-1">
              {[style.color_primary, style.color_secondary, style.color_accent].filter(Boolean).map((c, i) => (
                <div key={i} className="w-5 h-5 rounded border border-gray-200" style={{ backgroundColor: c }} />
              ))}
            </div>
          </div>
          {style.heading_font && (
            <div className="text-xs text-gray-600">
              Font: <span className="font-medium">{style.heading_font}</span>
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
