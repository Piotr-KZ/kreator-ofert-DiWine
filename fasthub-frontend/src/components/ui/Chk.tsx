import React from "react";

interface ChkProps {
  on?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export default function Chk({ on, onClick, children }: ChkProps) {
  return (
    <button
      onClick={onClick}
      className={`text-left p-3 rounded-lg border-2 transition-all flex items-center gap-3 w-full ${
        on
          ? "border-green-400 bg-green-50"
          : "border-gray-200 bg-white hover:border-gray-300"
      }`}
    >
      <div
        className={`w-5 h-5 rounded flex-shrink-0 flex items-center justify-center border-2 ${
          on ? "bg-green-500 border-green-500" : "border-gray-300"
        }`}
      >
        {on && (
          <svg
            className="w-3 h-3 text-white"
            fill="none"
            stroke="currentColor"
            strokeWidth={3}
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M5 13l4 4L19 7"
            />
          </svg>
        )}
      </div>
      {children}
    </button>
  );
}
