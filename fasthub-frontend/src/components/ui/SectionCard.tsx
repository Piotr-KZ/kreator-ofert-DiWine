import React from "react";

interface SectionCardProps {
  title?: string;
  desc?: string;
  children?: React.ReactNode;
  className?: string;
}

export default function SectionCard({ title, desc, children, className }: SectionCardProps) {
  return (
    <div className={`bg-white border-2 border-gray-200 rounded-xl p-6 mb-4 ${className || ""}`}>
      {title && <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>}
      {desc && <p className="text-sm text-gray-500 mb-4">{desc}</p>}
      {children}
    </div>
  );
}
