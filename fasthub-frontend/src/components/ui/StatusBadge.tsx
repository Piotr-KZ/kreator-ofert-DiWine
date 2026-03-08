import React from "react";

interface StatusBadgeProps {
  status?: string;
  variant?: "success" | "warning" | "error" | "info" | "neutral";
  children?: React.ReactNode;
}

const STYLES: Record<string, string> = {
  success: "bg-green-100 text-green-700",
  warning: "bg-amber-100 text-amber-700",
  error: "bg-red-100 text-red-700",
  info: "bg-indigo-100 text-indigo-700",
  neutral: "bg-gray-100 text-gray-500",
};

export default function StatusBadge({
  status,
  variant = "neutral",
  children,
}: StatusBadgeProps) {
  return (
    <span
      className={`text-xs px-2 py-0.5 rounded-full font-medium ${
        STYLES[variant] || STYLES.neutral
      }`}
    >
      {children || status}
    </span>
  );
}
