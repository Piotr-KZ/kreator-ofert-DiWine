interface Step { num: number; name: string }

const STEPS: Step[] = [
  { num: 1, name: 'Email' },
  { num: 2, name: 'Weryfikacja' },
  { num: 3, name: 'Zestawy' },
  { num: 4, name: 'Kosztorys' },
  { num: 5, name: 'Struktura' },
  { num: 6, name: 'Treści' },
  { num: 7, name: 'Zdjęcia' },
  { num: 8, name: 'Eksport' },
];

interface Props {
  current: number;
  maxReached: number;
  onNavigate: (step: number) => void;
}

export default function OfferStepper({ current, maxReached, onNavigate }: Props) {
  return (
    <div className="bg-white border-b px-6 py-3 flex items-center gap-1">
      {STEPS.map((step, i) => {
        const done = step.num < current;
        const active = step.num === current;
        const reachable = step.num <= maxReached;
        return (
          <div key={step.num} className="flex items-center">
            {i > 0 && <div className="w-6 h-px bg-gray-200 mx-1" />}
            <button
              onClick={() => reachable ? onNavigate(step.num) : null}
              disabled={!reachable}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                active ? 'bg-indigo-50 text-indigo-700'
                : done ? 'text-green-600 hover:bg-green-50 cursor-pointer'
                : reachable ? 'text-gray-500 hover:bg-gray-50 cursor-pointer'
                : 'text-gray-300 cursor-default'
              }`}
            >
              <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                active ? 'bg-indigo-500 text-white' : done ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'
              }`}>{done ? '✓' : step.num}</span>
              {step.name}
            </button>
          </div>
        );
      })}
      <div className="flex-1" />
      <div className="w-28 bg-gray-200 rounded-full h-1.5">
        <div className="bg-indigo-500 h-1.5 rounded-full transition-all" style={{ width: `${(current / STEPS.length) * 100}%` }} />
      </div>
      <span className="text-[10px] text-gray-400 ml-2">{current}/{STEPS.length}</span>
    </div>
  );
}
