interface ToggleProps {
  on?: boolean;
  onClick?: () => void;
  label?: string;
}

export default function Toggle({ on, onClick, label }: ToggleProps) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`w-10 h-6 rounded-full relative cursor-pointer transition-colors ${
          on ? "bg-green-500" : "bg-gray-300"
        }`}
        onClick={onClick}
      >
        <div
          className={`w-4 h-4 bg-white rounded-full absolute top-1 shadow transition-all ${
            on ? "right-1" : "left-1"
          }`}
        />
      </div>
      {label && (
        <span className="text-sm font-medium text-gray-700">{label}</span>
      )}
    </div>
  );
}
