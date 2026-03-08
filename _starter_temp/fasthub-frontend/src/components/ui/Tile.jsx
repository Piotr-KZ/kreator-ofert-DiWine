export default function Tile({ on, onClick, children, className }) {
  return (
    <button onClick={onClick}
      className={`text-left p-4 rounded-xl border-2 transition-all w-full ${on ? "border-green-400 bg-green-50" : "border-gray-200 bg-white hover:border-gray-300"} ${className || ""}`}>
      {children}
    </button>
  );
}
