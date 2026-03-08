export default function Lbl({ num, title, sub }) {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="w-7 h-7 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
        <span className="text-indigo-700 text-xs font-bold">{num}</span>
      </div>
      <div>
        <h3 className="font-semibold text-gray-900 text-sm">{title}</h3>
        {sub && <p className="text-xs text-gray-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}
