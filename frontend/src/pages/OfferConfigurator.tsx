/**
 * Offer Configurator — main page for building gift sets.
 * Layout: package visualization (left) + product shelves (right).
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useOfferStore } from '@/store/offerStore';
import NewSetModal from '@/components/offer/NewSetModal';
import OfferStepper from '@/components/offer/OfferStepper';
import OfferNavButtons from '@/components/offer/OfferNavButtons';
import type { Product, PackagingItem, SetItemData } from '@/types/offer';
import { WINE_COLORS } from '@/types/offer';

// ─── Color dot: circle = available, square = selected ───
function Dot({ color, selected, enabled, onClick }: {
  color: string; selected: boolean; enabled: boolean; onClick: () => void;
}) {
  return (
    <button
      onClick={enabled ? onClick : undefined}
      className="transition-all flex-shrink-0"
      title={selected ? 'Kliknij aby usunąć' : 'Kliknij aby dodać'}
      style={{
        width: 22, height: 22,
        borderRadius: selected ? 4 : 22,
        background: color,
        border: selected ? '3px solid #3B82F6' : '2px solid #d1d5db',
        opacity: enabled ? 1 : 0.2,
        cursor: enabled ? 'pointer' : 'default',
      }}
    />
  );
}

// ─── Expandable section ───
function Section({ title, open, onToggle, children }: {
  title: string; open: boolean; onToggle: () => void; children: React.ReactNode;
}) {
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100"
      >
        <span className="text-sm font-bold text-gray-900">{title}</span>
        <span className="text-gray-400 text-xs">{open ? '▶' : '▼'}</span>
      </button>
      {open && (
        <div className="p-3 border-t max-h-64 overflow-y-auto">{children}</div>
      )}
    </div>
  );
}

// ─── Error modal ───
function ErrorModal({ message, onClose }: { message: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/30" />
      <div className="relative bg-white rounded-xl shadow-xl px-6 py-5 max-w-xs text-center" onClick={e => e.stopPropagation()}>
        <div className="text-sm font-bold text-gray-900 mb-3">{message}</div>
        <button onClick={onClose} className="px-4 py-1.5 bg-indigo-600 text-white rounded-lg text-sm font-bold">OK</button>
      </div>
    </div>
  );
}

export default function OfferConfigurator() {
  const { offerId } = useParams<{ offerId: string }>();
  const navigate = useNavigate();
  const store = useOfferStore();
  const {
    offer, products, packagings, colors, occasions,
    activeSetId, error, isLoading, busy, catalogLoaded,
  } = store;

  const [showModal, setShowModal] = useState(false);
  const [openSection, setOpenSection] = useState<string>('wine');
  const [saved, setSaved] = useState(false);

  // Reset old state, load fresh offer — version guard prevents stale fetches
  useEffect(() => {
    store.resetOffer();
    store.loadCatalog();
    if (offerId) store.loadOffer(offerId);
    return () => store.resetOffer();
  }, [offerId]);

  if (!catalogLoaded || isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Ładowanie...</div>
      </div>
    );
  }

  if (!offer) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Oferta nie znaleziona</div>
      </div>
    );
  }

  const activeSet = offer.sets.find(s => s.id === activeSetId);
  const pkg: PackagingItem | undefined = activeSet?.packaging_id
    ? packagings.find(p => p.id === activeSet.packaging_id)
    : undefined;

  const occasion = occasions.find(o => o.code === offer.occasion_code);
  const allowedColors = occasion?.allowed_colors_json || null; // null = all allowed
  const isColorOk = (c: string) => !allowedColors || allowedColors.includes(c);

  // Counts for active set
  const wineCount = activeSet?.items.filter(i => i.item_type === 'wine').length || 0;
  const maxWines = pkg?.bottles || 0;
  const sweetSlotSum = activeSet?.items
    .filter(i => i.item_type === 'sweet' || i.item_type === 'decoration')
    .reduce((sum, i) => {
      const prod = products.find(p => p.id === i.product_id);
      return sum + (prod?.slot_size || 1);
    }, 0) || 0;
  const maxSlots = pkg?.sweet_slots || 0;
  const unitPrice = activeSet?.unit_price || 0;
  const budget = activeSet?.budget_per_unit || 150;
  const overBudget = unitPrice > budget;

  // Helpers
  const hasItemColor = (productId: string, colorCode: string) =>
    activeSet?.items.some(i => i.product_id === productId && i.color_code === colorCode) || false;

  const handleAddItem = async (productId: string, itemType: string, colorCode?: string) => {
    if (!activeSet || busy) return;
    await store.addItem(activeSet.id!, productId, itemType, colorCode);
  };

  const handleRemoveItem = async (productId: string, colorCode?: string) => {
    if (!activeSet || busy) return;
    const item = activeSet.items.find(
      i => i.product_id === productId && i.color_code === (colorCode || null)
    );
    if (item?.id) await store.removeItem(activeSet.id!, item.id);
  };

  const wines = products.filter(p => p.category === 'wine');
  const sweets = products.filter(p => p.category === 'sweet');
  const decorations = products.filter(p => p.category === 'decoration');

  return (
    <div className="h-screen flex flex-col bg-gray-50" style={{ fontFamily: "'Outfit', system-ui" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />

      {/* Error modal */}
      {error && <ErrorModal message={error} onClose={() => store.setError(null)} />}

      {/* New set modal */}
      <NewSetModal open={showModal} onClose={() => setShowModal(false)} defaultBudget={budget} />

      {/* Busy overlay */}
      {busy && (
        <div className="fixed inset-0 z-40 bg-white/30 pointer-events-auto" />
      )}

      {/* Top nav */}
      <nav className="bg-gray-950 px-6 py-2.5 flex items-center gap-3 flex-shrink-0">
        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600" />
        <span className="text-white font-bold text-sm">OfferCreator</span>
        <span className="text-gray-500 text-xs">
          / {offer.client_name || 'Klient'} / {offer.quantity} szt. / {offer.offer_number}
        </span>
      </nav>
      <OfferStepper current={3} maxReached={3} onNavigate={s => {
        if (s === 1) navigate('/offer/create');
        if (s === 4 && offerId) navigate(`/offer/${offerId}/content`);
      }} />

      {/* Set tabs */}
      <div className="bg-white border-b px-4 py-2 flex items-center gap-2 flex-shrink-0">
        {offer.sets.map(s => (
          <button
            key={s.id}
            onClick={() => store.setActiveSet(s.id!)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
              activeSetId === s.id
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-600 border border-gray-200'
            }`}
          >
            {s.name}
            <span className="ml-1 opacity-70">{s.unit_price.toFixed(0)} zł</span>
          </button>
        ))}
        <button
          onClick={() => !busy && setShowModal(true)}
          disabled={busy}
          className="px-3 py-1.5 rounded-lg text-xs font-semibold border-2 border-dashed border-gray-300 text-gray-400 hover:border-indigo-400 disabled:opacity-50"
        >
          + Nowy zestaw
        </button>
      </div>

      {/* Main content */}
      {activeSet && pkg ? (
        <div className="flex-1 overflow-hidden flex">
          {/* LEFT: Package visualization */}
          <div className="flex-1 p-5 overflow-y-auto flex justify-center">
            <div className="w-full max-w-md">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-bold text-gray-900">{activeSet.name}</span>
                <span className={`text-lg font-bold ${overBudget ? 'text-red-600' : 'text-indigo-700'}`}>
                  {unitPrice.toFixed(2)} zł
                  <span className="text-xs font-normal text-gray-400 ml-1">/ {budget} zł</span>
                </span>
              </div>

              {/* Budget bar */}
              <div className={`rounded-xl px-4 py-2 mb-3 ${
                overBudget ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'
              }`}>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">Budżet na sztukę</span>
                  <span className={`font-bold ${overBudget ? 'text-red-600' : 'text-green-700'}`}>
                    {overBudget
                      ? `Przekroczono o ${(unitPrice - budget).toFixed(2)} zł`
                      : `Zostało ${(budget - unitPrice).toFixed(2)} zł`
                    }
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      overBudget ? 'bg-red-500' : unitPrice / budget > 0.8 ? 'bg-amber-400' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min((unitPrice / budget) * 100, 100)}%` }}
                  />
                </div>
              </div>

              {/* Box visualization */}
              <div className="bg-gradient-to-b from-gray-200 to-gray-100 rounded-3xl border-2 border-gray-300 p-5 shadow-inner">
                <div className="text-[10px] font-bold text-gray-500 uppercase mb-1">
                  Opakowanie: {pkg.name} ({pkg.price} zł)
                </div>

                {/* Wine slots */}
                <div className="text-[10px] font-bold text-gray-400 uppercase mt-3 mb-2">
                  Wino ({wineCount}/{maxWines})
                </div>
                <div className="flex gap-2 mb-3">
                  {Array.from({ length: pkg.bottles }, (_, i) => {
                    const item = activeSet.items.filter(it => it.item_type === 'wine')[i];
                    const wine = item ? products.find(p => p.id === item.product_id) : null;
                    const wColor = item?.color_code ? (WINE_COLORS[item.color_code] || WINE_COLORS['czerwone']) : null;

                    return (
                      <div
                        key={i}
                        className="flex-1 rounded-xl border-2 relative"
                        style={{
                          background: wColor ? wColor.bg : '#EFF6FF',
                          borderColor: wine ? '#3B82F6' : '#CBD5E1',
                          borderStyle: wine ? 'solid' : 'dashed',
                          minHeight: 80,
                        }}
                      >
                        {wine ? (
                          <div className="p-3">
                            <div className="text-xs font-bold leading-tight" style={{ color: wColor?.text || '#fff' }}>
                              {wine.name}
                            </div>
                            <div className="text-[10px] mt-0.5" style={{ color: wColor?.text || '#fff', opacity: 0.7 }}>
                              {item?.color_code} / {wine.wine_type}
                            </div>
                            <div className="text-sm font-bold mt-1" style={{ color: wColor?.text || '#fff' }}>
                              {item?.unit_price.toFixed(2)} zł
                            </div>
                            <button
                              onClick={() => !busy && item?.id && store.removeItem(activeSet.id!, item.id)}
                              disabled={busy}
                              className="absolute top-1 right-1 w-5 h-5 rounded-full bg-black/30 text-white text-[10px] flex items-center justify-center hover:bg-black/50 disabled:opacity-50"
                            >
                              x
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center justify-center h-20 text-blue-300 text-xs">
                            Dodaj wino
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Sweet slots */}
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] font-bold text-gray-400 uppercase">
                    Słodycze i dodatki ({sweetSlotSum}/{maxSlots})
                  </span>
                  <span className="text-[9px] text-gray-400">Kolory:</span>
                  <div className="flex gap-0.5">
                    {(allowedColors || ['red','gold','green','blue','craft']).map(c => {
                      const col = colors.find(x => x.code === c);
                      return col ? (
                        <span key={c} className="w-3 h-3 rounded-full border border-white" style={{ background: col.hex_value }} />
                      ) : null;
                    })}
                  </div>
                </div>
                <div className="grid gap-1.5" style={{
                  gridTemplateColumns: `repeat(${Math.min(Math.ceil(maxSlots / 2), 4)}, 1fr)`,
                }}>
                  {(() => {
                    const sweetItems = activeSet.items.filter(it =>
                      it.item_type === 'sweet' || it.item_type === 'decoration'
                    );
                    // Build slot grid: each product fills slot_size cells
                    const cells: React.ReactNode[] = [];
                    let slotIdx = 0;
                    for (const item of sweetItems) {
                      const sweet = products.find(p => p.id === item.product_id);
                      const col = item.color_code ? colors.find(c => c.code === item.color_code) : null;
                      const size = sweet?.slot_size || 1;
                      const cols = Math.min(Math.ceil(maxSlots / 2), 4);
                      cells.push(
                        <div
                          key={item.id || slotIdx}
                          className="rounded-lg px-2 py-1.5 relative border-2 border-blue-400"
                          style={{
                            background: col?.hex_value || '#94A3B8',
                            minHeight: 36,
                            gridColumn: size > 1 ? `span ${Math.min(size, cols)}` : undefined,
                          }}
                        >
                          <div className="text-[9px] font-bold text-white leading-tight drop-shadow-sm">
                            {sweet?.name || '?'}{size > 1 ? ` (${size} sloty)` : ''}
                          </div>
                          <div className="text-[8px] text-white/80">{sweet?.base_price || 0} zł</div>
                          <button
                            onClick={() => !busy && item.id && store.removeItem(activeSet.id!, item.id!)}
                            disabled={busy}
                            className="absolute top-0.5 right-0.5 w-4 h-4 rounded-full bg-black/30 text-white text-[7px] flex items-center justify-center hover:bg-black/50 disabled:opacity-50"
                          >
                            x
                          </button>
                        </div>
                      );
                      slotIdx += size;
                    }
                    // Fill remaining empty slots
                    for (let i = slotIdx; i < maxSlots; i++) {
                      cells.push(
                        <div key={`empty-${i}`} className="rounded-lg border-2 border-dashed border-gray-300" style={{ background: '#EFF6FF', minHeight: 36 }} />
                      );
                    }
                    return cells;
                  })()}
                </div>
              </div>

              {/* Price breakdown */}
              <div className="mt-3 flex justify-between text-[11px] text-gray-500 px-1">
                <span>Opak: {pkg.price} zł</span>
                <span>Wina: {activeSet.items.filter(i => i.item_type === 'wine').reduce((s, i) => s + i.unit_price, 0).toFixed(0)} zł</span>
                <span>Słodycze: {activeSet.items.filter(i => i.item_type !== 'wine' && i.item_type !== 'personalization').reduce((s, i) => s + i.unit_price, 0).toFixed(0)} zł</span>
                <span className="font-bold text-gray-400">x{offer.quantity} = {activeSet.total_price.toFixed(0)} zł</span>
              </div>

              {/* Per-set save button */}
              <div className="mt-4 flex items-center gap-3">
                <button
                  onClick={() => {
                    setSaved(true);
                    setTimeout(() => setSaved(false), 2000);
                  }}
                  disabled={busy}
                  className="flex-1 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-50 disabled:opacity-50"
                >
                  {saved ? '✓ Zapisano' : `Zapisz zestaw ${activeSet.name}`}
                </button>
              </div>
            </div>
          </div>

          {/* RIGHT: Product shelves */}
          <div className="w-96 flex-shrink-0 flex flex-col mr-12 mt-4 mb-4">
            <div className="flex-1 overflow-y-auto space-y-2">

              {/* WINES */}
              <Section title="WINA" open={openSection === 'wine'} onToggle={() => setOpenSection(openSection === 'wine' ? '' : 'wine')}>
                <div className="space-y-1">
                  {wines.map(w => {
                    const wineColors = w.wine_color ? [w.wine_color] : [];
                    return (
                      <div key={w.id} className={`flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 bg-white text-xs ${busy ? 'opacity-60 pointer-events-none' : ''}`}>
                        <div className="flex gap-1 flex-shrink-0">
                          {wineColors.map(c => {
                            const sel = hasItemColor(w.id, c);
                            const wc = WINE_COLORS[c];
                            return (
                              <Dot
                                key={c}
                                color={wc?.bg || '#ccc'}
                                selected={sel}
                                enabled={!busy}
                                onClick={() => {
                                  if (busy) return;
                                  if (sel) handleRemoveItem(w.id, c);
                                  else handleAddItem(w.id, 'wine', c);
                                }}
                              />
                            );
                          })}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-bold text-gray-900 truncate">{w.name}</div>
                          <div className="text-[10px] text-gray-400">{w.wine_type}</div>
                        </div>
                        <span className="text-[10px] text-gray-400 line-through">{w.base_price.toFixed(0)}</span>
                        <span className="font-bold text-indigo-700">{w.base_price.toFixed(0)} zł</span>
                      </div>
                    );
                  })}
                </div>
              </Section>

              {/* SWEETS */}
              <Section title="SŁODYCZE" open={openSection === 'sweet'} onToggle={() => setOpenSection(openSection === 'sweet' ? '' : 'sweet')}>
                <div className="space-y-1">
                  {sweets.map(sw => (
                    <div key={sw.id} className={`flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 bg-white text-xs ${busy ? 'opacity-60 pointer-events-none' : ''}`}>
                      <div className="flex gap-1 flex-shrink-0">
                        {(sw.available_colors_json || []).map(c => {
                          const col = colors.find(x => x.code === c);
                          const sel = hasItemColor(sw.id, c);
                          const ok = isColorOk(c) && !busy;
                          return col ? (
                            <Dot
                              key={c}
                              color={col.hex_value}
                              selected={sel}
                              enabled={ok}
                              onClick={() => {
                                if (busy) return;
                                if (sel) handleRemoveItem(sw.id, c);
                                else handleAddItem(sw.id, 'sweet', c);
                              }}
                            />
                          ) : null;
                        })}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-gray-900 truncate">{sw.name}</div>
                      </div>
                      <span className="font-bold text-indigo-700">{sw.base_price} zł</span>
                    </div>
                  ))}
                </div>
              </Section>

              {/* DECORATIONS */}
              <Section title="DODATKI" open={openSection === 'deco'} onToggle={() => setOpenSection(openSection === 'deco' ? '' : 'deco')}>
                <div className="space-y-1">
                  {decorations.map(dec => (
                    <div key={dec.id} className={`flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 bg-white text-xs ${busy ? 'opacity-60 pointer-events-none' : ''}`}>
                      <div className="flex gap-1 flex-shrink-0">
                        {(dec.available_colors_json || []).map(c => {
                          const col = colors.find(x => x.code === c);
                          const sel = hasItemColor(dec.id, c);
                          const ok = isColorOk(c) && !busy;
                          return col ? (
                            <Dot
                              key={c}
                              color={col.hex_value}
                              selected={sel}
                              enabled={ok}
                              onClick={() => {
                                if (busy) return;
                                if (sel) handleRemoveItem(dec.id, c);
                                else handleAddItem(dec.id, 'decoration', c);
                              }}
                            />
                          ) : null;
                        })}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-gray-900 truncate">{dec.name}</div>
                      </div>
                      <span className="font-bold text-indigo-700">{dec.base_price} zł</span>
                    </div>
                  ))}
                </div>
              </Section>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-gray-400 mb-4">Brak zestawów. Dodaj pierwszy zestaw.</div>
            <button
              onClick={() => setShowModal(true)}
              className="px-5 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700"
            >
              + Nowy zestaw
            </button>
          </div>
        </div>
      )}

      {/* Bottom nav */}
      <div className="max-w-6xl mx-auto px-6 pb-6">
        <OfferNavButtons
          onBack={() => navigate('/offer/create')}
          backLabel="← Nowa oferta"
          onNext={() => navigate(`/offer/${offerId}/cost`)}
          nextLabel="Dalej — kosztorys"
          nextDisabled={!offer || offer.sets.length === 0}
        />
      </div>
    </div>
  );
}
