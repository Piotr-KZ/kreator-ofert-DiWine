export default function Fld({ label, placeholder, value, onChange, large, disabled, error, type = "text" }) {
  const base = `w-full px-4 py-3 border-2 rounded-xl text-sm outline-none transition-all focus:ring-2 ${error ? "border-red-300 focus:border-red-400 focus:ring-red-100" : "border-gray-200 focus:border-indigo-400 focus:ring-indigo-100"} ${disabled ? "bg-gray-50 border-gray-100 text-gray-400" : ""}`;
  return (
    <div>
      {label && <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>}
      {large
        ? <textarea rows={typeof large === "number" ? large : 4} placeholder={placeholder} value={value || ""} onChange={e => onChange?.(e.target.value)} className={base + " resize-none"} disabled={disabled} />
        : <input type={type} placeholder={placeholder} value={value || ""} onChange={e => onChange?.(e.target.value)} className={base} disabled={disabled} />
      }
      {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    </div>
  );
}
