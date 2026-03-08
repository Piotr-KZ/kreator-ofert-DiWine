export default function SectionCard({ title, desc, children }) {
  return (
    <div className="bg-white border-2 border-gray-200 rounded-xl p-6 mb-4">
      {title && <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>}
      {desc && <p className="text-sm text-gray-500 mb-4">{desc}</p>}
      {children}
    </div>
  );
}
