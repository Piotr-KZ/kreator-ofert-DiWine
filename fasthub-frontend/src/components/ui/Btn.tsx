import React from "react";

interface BtnProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost" | "danger";
  className?: string;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
  loading?: boolean;
}

const styles: Record<string, string> = {
  primary: "bg-indigo-600 text-white hover:bg-indigo-700",
  secondary: "bg-gray-900 text-white hover:bg-gray-800",
  ghost: "bg-white text-gray-700 border-2 border-gray-200 hover:border-gray-300",
  danger: "bg-red-600 text-white hover:bg-red-700",
};

export default function Btn({
  children,
  onClick,
  variant = "primary",
  className,
  disabled,
  type = "button",
  loading,
}: BtnProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      type={type}
      className={`px-6 py-2.5 rounded-xl font-semibold text-sm transition-all ${styles[variant]} ${
        disabled || loading ? "opacity-50 cursor-not-allowed" : ""
      } ${className || ""}`}
    >
      {loading ? (
        <span className="flex items-center justify-center gap-2">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          {children}
        </span>
      ) : (
        children
      )}
    </button>
  );
}
