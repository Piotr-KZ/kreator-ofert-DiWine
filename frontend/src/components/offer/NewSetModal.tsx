/**
 * Modal for creating a new offer set — name, budget, bottle count, packaging selection.
 */

import { useState, useEffect } from 'react';
import { useOfferStore } from '@/store/offerStore';
import type { PackagingItem } from '@/types/offer';

interface Props {
  open: boolean;
  onClose: () => void;
  defaultBudget?: number;
}

export default function NewSetModal({ open, onClose, defaultBudget = 150 }: Props) {
  const { packagings, addSet } = useOfferStore();
  const [name, setName] = useState('');
  const [budget, setBudget] = useState(defaultBudget);
  const [bottleCount, setBottleCount] = useState(1);
  const [pkgId, setPkgId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Reset on open
  useEffect(() => {
    if (open) {
      setName('');
      setBudget(defaultBudget);
      setBottleCount(1);
      setPkgId('');
    }
  }, [open, defaultBudget]);

  if (!open) return null;

  const filtered = packagings.filter((p: PackagingItem) => p.bottles === bottleCount);

  const handleCreate = async () => {
    if (!name || !pkgId) return;
    setSubmitting(true);
    try {
      await addSet(name, pkgId, budget);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40" />
      <div className="relative bg-white rounded-2xl shadow-2xl w-[540px] p-6" onClick={e => e.stopPropagation()}>
        <h3 className="font-bold text-lg mb-4">Nowy zestaw prezentowy</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">Nazwa zestawu</label>
              <input
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-indigo-400 outline-none"
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="np. Wariant Premium"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">Budżet netto / szt.</label>
              <input
                type="number"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-bold focus:border-indigo-400 outline-none"
                value={budget}
                onChange={e => setBudget(Number(e.target.value) || 0)}
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-500 block mb-1">Ilość butelek wina</label>
            <div className="grid grid-cols-6 gap-1.5">
              {Array.from({ length: 12 }, (_, i) => i + 1).map(n => (
                <button
                  key={n}
                  onClick={() => { setBottleCount(n); setPkgId(''); }}
                  className={`py-2 rounded-lg border-2 text-sm font-bold ${
                    bottleCount === n
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                      : 'border-gray-200 text-gray-500 hover:border-gray-300'
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-500 block mb-1">
              Opakowanie (na {bottleCount} but.)
            </label>
            {filtered.length > 0 ? (
              <div className="space-y-1 max-h-36 overflow-y-auto">
                {filtered.map(p => (
                  <button
                    key={p.id}
                    onClick={() => setPkgId(p.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg border text-sm ${
                      pkgId === p.id ? 'border-green-400 bg-green-50' : 'border-gray-200'
                    }`}
                  >
                    <div>
                      <span className="font-bold">{p.name}</span>
                      <span className="text-[10px] text-gray-400 ml-2">{p.sweet_slots} slotów</span>
                    </div>
                    <span className="font-bold text-indigo-700">{p.price} zł</span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-xs text-gray-400 py-3 text-center">
                Brak opakowań na {bottleCount} butelek
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-5">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm text-gray-500">
            Anuluj
          </button>
          <button
            disabled={!name || !pkgId || submitting}
            onClick={handleCreate}
            className={`px-5 py-2 rounded-lg text-sm font-bold text-white ${
              !name || !pkgId || submitting ? 'bg-gray-300' : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
          >
            {submitting ? 'Tworzę...' : 'Stwórz zestaw'}
          </button>
        </div>
      </div>
    </div>
  );
}
