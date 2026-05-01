interface Props {
  onBack?: () => void;
  onNext?: () => void;
  nextLabel?: string;
  nextDisabled?: boolean;
  backLabel?: string;
}

export default function OfferNavButtons({ onBack, onNext, nextLabel = 'Dalej', nextDisabled = false, backLabel = '← Wróć' }: Props) {
  return (
    <div className="flex items-center gap-3 mt-6 pt-4 border-t border-gray-200">
      {onBack && <button onClick={onBack} className="px-4 py-2 text-sm font-semibold bg-white text-gray-700 border border-gray-200 rounded-lg hover:border-gray-300">{backLabel}</button>}
      <div className="flex-1" />
      {onNext && <button onClick={onNext} disabled={nextDisabled} className={`px-6 py-2.5 text-sm font-bold text-white rounded-lg ${nextDisabled ? 'bg-gray-300' : 'bg-indigo-600 hover:bg-indigo-700'}`}>{nextLabel}</button>}
    </div>
  );
}
