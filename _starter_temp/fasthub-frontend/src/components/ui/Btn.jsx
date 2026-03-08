export default function Btn({ children, onClick, variant = "primary", className, disabled }) {
  const styles = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-700",
    secondary: "bg-gray-900 text-white hover:bg-gray-800",
    ghost: "bg-white text-gray-700 border-2 border-gray-200 hover:border-gray-300",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };
  return (
    <button onClick={onClick} disabled={disabled}
      className={`px-6 py-2.5 rounded-xl font-semibold text-sm transition-all ${styles[variant]} ${disabled ? "opacity-50 cursor-not-allowed" : ""} ${className || ""}`}>
      {children}
    </button>
  );
}
