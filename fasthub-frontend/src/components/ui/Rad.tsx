import React from "react";

interface RadProps {
  on?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export default function Rad({ on, onClick, children }: RadProps) {
  return (
    <button
      onClick={onClick}
      className={`text-left p-3.5 rounded-xl border-2 transition-all flex items-center gap-4 w-full ${
        on
          ? "border-green-400 bg-green-50"
          : "border-gray-200 bg-white hover:border-gray-300"
      }`}
    >
      <div
        className={`w-4 h-4 rounded-full flex-shrink-0 border-2 flex items-center justify-center ${
          on ? "border-green-500" : "border-gray-300"
        }`}
      >
        {on && <div className="w-2 h-2 rounded-full bg-green-500" />}
      </div>
      {children}
    </button>
  );
}
