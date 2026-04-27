// Step3Kreator — adaptacja z makiety app.jsx (590 linii)
// Zmiany vs makieta: multi-page → single page, window.X → import, dane → store,
// top bar + stepper usunięte (już w LabLayout)

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useLabStore } from '@/store/labStore';
import { BLOCK_LIBRARY, CATEGORIES, BRAND_PALETTE, INITIAL_BRAND } from '@/config/blocks';
import type { Block } from '@/config/blocks';

// Helper z makiety — kontrast tekstu na tle koloru
function getContrastColor(hex: string) {
  const h = hex.replace('#', '');
  const r = parseInt(h.substr(0, 2), 16);
  const g = parseInt(h.substr(2, 2), 16);
  const b = parseInt(h.substr(4, 2), 16);
  return (0.299 * r + 0.587 * g + 0.114 * b) < 128 ? '#fff' : '#0F172A';
}

export default function Step3Kreator() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const { sections, projectName, addSection, removeSection, reorderSections, duplicateSection, updateSection: storeUpdateSection } = useLabStore();

  // Brand — local state (kolory bg/cta/gradient, nie ma tego w store)
  const [brand, setBrand] = React.useState(INITIAL_BRAND);
  const [brandOpen, setBrandOpen] = React.useState(false);

  // UI state
  const [aiOpen, setAiOpen] = React.useState(false);
  const [aiContext, setAiContext] = React.useState<{code: string; label: string; name: string} | null>(null);
  const [variantsModal, setVariantsModal] = React.useState<{mode: 'swap'|'add'; targetId?: string; insertAt?: number; restrictCat?: string} | null>(null);
  const [toast, setToast] = React.useState<{msg: string; icon: string} | null>(null);
  const [dragIdx, setDragIdx] = React.useState<number | null>(null);
  const [dragOverIdx, setDragOverIdx] = React.useState<number | null>(null);

  const showToast = (msg: string, icon = 'check') => {
    setToast({ msg, icon });
    clearTimeout((showToast as any)._t);
    (showToast as any)._t = setTimeout(() => setToast(null), 2200);
  };

  // Akcje na sekcjach — delegowane do store
  const move = (id: string, dir: number) => {
    const i = sections.findIndex(s => s.id === id);
    if (i < 0) return;
    const j = i + dir;
    if (j < 0 || j >= sections.length) return;
    const ids = sections.map(s => s.id);
    [ids[i], ids[j]] = [ids[j], ids[i]];
    reorderSections(ids);
    showToast('Przeniesiono sekcję', 'check');
  };

  const reorderByDrag = (fromIdx: number, toIdx: number) => {
    if (fromIdx === toIdx) return;
    const ids = sections.map(s => s.id);
    const [moved] = ids.splice(fromIdx, 1);
    ids.splice(toIdx, 0, moved);
    reorderSections(ids);
    showToast('Przeniesiono sekcję', 'check');
  };

  const del = (id: string) => {
    removeSection(id);
    showToast('Sekcja usunięta', 'trash');
  };

  const duplicate = (id: string) => {
    duplicateSection(id);
    showToast('Sekcja zduplikowana', 'copy');
  };

  const openAI = (sec?: typeof sections[0]) => {
    if (sec) {
      const b = BLOCK_LIBRARY.find(x => x.code === sec.block_code);
      setAiContext({ code: sec.block_code, label: b?.name || sec.block_code, name: b?.name || '' });
    } else {
      setAiContext(null);
    }
    setAiOpen(true);
  };

  const onPickFromModal = (block: Block) => {
    if (variantsModal?.mode === 'swap' && variantsModal.targetId) {
      storeUpdateSection(variantsModal.targetId, { block_code: block.code });
      showToast(`Zmieniono wariant na ${block.code}`, 'check');
    } else if (variantsModal?.mode === 'add') {
      const at = variantsModal.insertAt ?? sections.length;
      addSection(block.code, at);
      showToast(`Dodano sekcję ${block.code}`, 'plus');
    }
    setVariantsModal(null);
  };

  return (
    <div data-screen-label="01 Struktura strony">
      {/* MAIN */}
      <div style={{ maxWidth: 1180, margin: '0 auto', padding: '28px 24px 80px' }}>
        {/* Page heading */}
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 16, marginBottom: 20 }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '3px 10px', background: '#EEF2FF', color: '#6366F1', borderRadius: 11, fontSize: 11, fontWeight: 700, letterSpacing: 0.5, textTransform: 'uppercase', marginBottom: 10 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#6366F1' }}/>
              Krok 3 z 5 · Kreator
            </div>
            <h1 style={{ margin: 0, fontFamily: 'Instrument Serif, Georgia, serif', fontSize: 38, fontWeight: 400, letterSpacing: -0.5, color: '#0F172A' }}>
              Uloz <em style={{ color: '#6366F1', fontStyle: 'italic' }}>szkielet</em> swojej strony
            </h1>
            <p style={{ margin: '8px 0 0', color: '#64748B', fontSize: 14.5, lineHeight: 1.5, maxWidth: 640 }}>
              Kazdy klocek to jedna sekcja. Zmien wariant, dobierz kolor tla, przenies w gore/dol. Kliknij AI jesli potrzebujesz pomocy.
            </p>
          </div>
          <div style={{ flex: 1 }}/>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <div style={{ padding: '7px 12px', background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10, display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5 }}>
              <span style={{ color: '#64748B' }}>Sekcje:</span>
              <span style={{ fontWeight: 700, color: '#0F172A', fontSize: 14 }}>{sections.length}</span>
            </div>
            <BrandButton brand={brand} open={brandOpen} setOpen={setBrandOpen} onChange={setBrand} />
            <button onClick={() => openAI()} style={{
              padding: '8px 14px', background: 'linear-gradient(135deg, #6366F1, #EC4899)',
              color: '#fff', border: 'none', borderRadius: 10,
              fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer',
              display: 'inline-flex', alignItems: 'center', gap: 6,
              boxShadow: '0 2px 8px rgba(99,102,241,.3)',
            }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
              Asystent AI
            </button>
          </div>
        </div>

        {/* Sections list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {sections.map((s, i) => {
            const block = BLOCK_LIBRARY.find(b => b.code === s.block_code);
            const cat = block ? CATEGORIES[block.cat] : null;
            return (
              <React.Fragment key={s.id}>
                <div
                  draggable
                  onDragStart={() => setDragIdx(i)}
                  onDragEnd={() => { setDragIdx(null); setDragOverIdx(null); }}
                  onDragOver={(e) => { if (dragIdx != null) { e.preventDefault(); setDragOverIdx(i); } }}
                  onDrop={(e) => {
                    if (dragIdx == null) return;
                    e.preventDefault();
                    reorderByDrag(dragIdx, i);
                    setDragIdx(null); setDragOverIdx(null);
                  }}
                  style={{
                    position: 'relative',
                    opacity: dragIdx === i ? 0.4 : 1,
                    transform: dragOverIdx === i && dragIdx !== i ? 'translateY(4px)' : 'none',
                    transition: 'transform .15s, opacity .15s',
                  }}>
                  {/* Placeholder SectionCard — zostanie zastapiony w KROK 6 */}
                  <div style={{
                    padding: '14px 18px', background: '#fff', border: '1px solid #E2E8F0', borderRadius: 12,
                    display: 'flex', alignItems: 'center', gap: 14, cursor: 'grab',
                  }}>
                    {/* Drag handle */}
                    <div style={{ color: '#CBD5E1', cursor: 'grab' }}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 6h.01M8 12h.01M8 18h.01M16 6h.01M16 12h.01M16 18h.01"/></svg>
                    </div>
                    {/* Position */}
                    <div style={{ width: 28, height: 28, borderRadius: '50%', background: cat?.color || '#94A3B8', color: '#fff', display: 'grid', placeItems: 'center', fontSize: 11, fontWeight: 700, flexShrink: 0 }}>
                      {i + 1}
                    </div>
                    {/* Code + Name */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 11, color: cat?.color || '#94A3B8', fontWeight: 700 }}>{s.block_code}</span>
                        <span style={{ fontSize: 13, fontWeight: 500, color: '#0F172A' }}>{block?.name || s.block_code}</span>
                      </div>
                      <div style={{ fontSize: 11, color: '#94A3B8', marginTop: 2 }}>{block?.desc || ''}</div>
                    </div>
                    {/* Category badge */}
                    <div style={{ padding: '3px 8px', background: cat?.color ? cat.color + '18' : '#F1F5F9', color: cat?.color || '#64748B', borderRadius: 6, fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      {cat?.name || ''}
                    </div>
                    {/* Actions */}
                    <div style={{ display: 'flex', gap: 4 }}>
                      <button onClick={() => move(s.id, -1)} disabled={i === 0} style={{ width: 28, height: 28, border: '1px solid #E2E8F0', borderRadius: 6, background: '#fff', cursor: 'pointer', display: 'grid', placeItems: 'center', opacity: i === 0 ? 0.3 : 1 }}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2"><path d="M18 15l-6-6-6 6"/></svg>
                      </button>
                      <button onClick={() => move(s.id, 1)} disabled={i === sections.length - 1} style={{ width: 28, height: 28, border: '1px solid #E2E8F0', borderRadius: 6, background: '#fff', cursor: 'pointer', display: 'grid', placeItems: 'center', opacity: i === sections.length - 1 ? 0.3 : 1 }}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
                      </button>
                      <button onClick={() => setVariantsModal({ mode: 'swap', targetId: s.id, restrictCat: block?.cat })} style={{ width: 28, height: 28, border: '1px solid #E2E8F0', borderRadius: 6, background: '#fff', cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2"><path d="M7 16V4m0 0L3 8m4-4l4 4M17 8v12m0 0l4-4m-4 4l-4-4"/></svg>
                      </button>
                      <button onClick={() => duplicate(s.id)} style={{ width: 28, height: 28, border: '1px solid #E2E8F0', borderRadius: 6, background: '#fff', cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#475569" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                      </button>
                      <button onClick={() => openAI(s)} style={{ width: 28, height: 28, border: '1px solid #E2E8F0', borderRadius: 6, background: 'linear-gradient(135deg, #6366F1, #EC4899)', cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2"><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/></svg>
                      </button>
                      <button onClick={() => del(s.id)} style={{ width: 28, height: 28, border: '1px solid #FCA5A5', borderRadius: 6, background: '#FEF2F2', cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2"><path d="M3 6h18M8 6V4h8v2M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"/></svg>
                      </button>
                    </div>
                  </div>
                </div>
                {/* Add section button between cards */}
                {i < sections.length - 1 && (
                  <AddSectionBtn onClick={() => setVariantsModal({ mode: 'add', insertAt: i + 1 })} />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Empty state or add at end */}
        {sections.length === 0 ? (
          <AddSectionBtn onClick={() => setVariantsModal({ mode: 'add', insertAt: 0 })} />
        ) : (
          <div style={{ marginTop: 10 }}>
            <AddSectionBtn onClick={() => setVariantsModal({ mode: 'add', insertAt: sections.length })} />
          </div>
        )}

        {/* Next step button */}
        <div style={{ marginTop: 32, display: 'flex', justifyContent: 'flex-end' }}>
          <button onClick={() => navigate(`/lab/${projectId}/step/4`)} style={{
            padding: '10px 20px', background: 'linear-gradient(135deg, #6366F1, #EC4899)',
            color: '#fff', border: 'none', borderRadius: 10,
            fontFamily: 'inherit', fontSize: 14, fontWeight: 600, cursor: 'pointer',
            display: 'inline-flex', alignItems: 'center', gap: 6,
            boxShadow: '0 2px 8px rgba(99,102,241,.25)',
          }}>
            Dalej: Tresci
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

      {/* AI panel — stub, bedzie w osobnym pliku */}
      {aiOpen && (
        <div style={{ position: 'fixed', top: 0, right: 0, width: 380, height: '100vh', background: '#fff', boxShadow: '-4px 0 24px rgba(0,0,0,.1)', zIndex: 50, padding: 20, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>Asystent AI</h3>
            <button onClick={() => setAiOpen(false)} style={{ marginLeft: 'auto', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: 20, color: '#94A3B8' }}>x</button>
          </div>
          {aiContext && <p style={{ fontSize: 13, color: '#64748B' }}>Kontekst: {aiContext.label} ({aiContext.code})</p>}
          <p style={{ fontSize: 13, color: '#94A3B8', marginTop: 'auto' }}>Panel AI — zostanie podlaczony w kolejnych krokach</p>
        </div>
      )}

      {/* Blocks modal */}
      <BlocksModal
        open={!!variantsModal}
        onClose={() => setVariantsModal(null)}
        onPick={onPickFromModal}
        restrictCat={variantsModal?.restrictCat}
        title={variantsModal?.mode === 'swap' ? 'Wybierz inny wariant tej sekcji' : 'Dodaj nowa sekcje'}
      />

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)',
          background: '#0F172A', color: '#fff',
          padding: '10px 16px', borderRadius: 10,
          fontSize: 13, fontWeight: 500,
          display: 'flex', alignItems: 'center', gap: 8,
          boxShadow: '0 8px 24px rgba(0,0,0,.2)',
          zIndex: 1000, animation: 'toastIn .2s ease',
        }}>
          <span style={{ width: 18, height: 18, borderRadius: '50%', background: '#10B981', display: 'grid', placeItems: 'center' }}>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>
          </span>
          {toast.msg}
        </div>
      )}
    </div>
  );
}

// ─── AddSectionBtn (z makiety) ─────────────────────────
function AddSectionBtn({ onClick }: { onClick: () => void }) {
  return (
    <button onClick={onClick} style={{
      width: '100%', padding: '10px 0', background: 'transparent',
      border: '2px dashed #CBD5E1', borderRadius: 10,
      cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
      color: '#94A3B8', fontSize: 12, fontWeight: 600,
      transition: 'border-color .15s, color .15s',
    }}
    onMouseEnter={e => { (e.target as HTMLElement).style.borderColor = '#6366F1'; (e.target as HTMLElement).style.color = '#6366F1'; }}
    onMouseLeave={e => { (e.target as HTMLElement).style.borderColor = '#CBD5E1'; (e.target as HTMLElement).style.color = '#94A3B8'; }}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14"/></svg>
      Dodaj sekcje
    </button>
  );
}

// ─── BlocksModal (z makiety — biblioteka klockow) ─────
function BlocksModal({ open, onClose, onPick, restrictCat, title }: {
  open: boolean;
  onClose: () => void;
  onPick: (block: Block) => void;
  restrictCat?: string;
  title: string;
}) {
  const [search, setSearch] = React.useState('');
  const [activeCat, setActiveCat] = React.useState<string | null>(null);

  if (!open) return null;

  const effectiveCat = restrictCat || activeCat;
  const filtered = BLOCK_LIBRARY.filter(b => {
    if (effectiveCat && b.cat !== effectiveCat) return false;
    if (search && !b.name.toLowerCase().includes(search.toLowerCase()) && !b.code.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  // Group by category
  const grouped: Record<string, Block[]> = {};
  filtered.forEach(b => {
    if (!grouped[b.cat]) grouped[b.cat] = [];
    grouped[b.cat].push(b);
  });

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,.45)', zIndex: 60, display: 'grid', placeItems: 'center' }} onClick={onClose}>
      <div onClick={e => e.stopPropagation()} style={{ width: 640, maxHeight: '80vh', background: '#fff', borderRadius: 16, boxShadow: '0 24px 60px rgba(15,23,42,.3)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Header */}
        <div style={{ padding: '18px 20px 14px', borderBottom: '1px solid #E2E8F0' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>{title}</h3>
            <button onClick={onClose} style={{ marginLeft: 'auto', background: 'transparent', border: 'none', cursor: 'pointer', color: '#94A3B8', fontSize: 20, padding: 0, lineHeight: 1 }}>x</button>
          </div>
          <input
            type="text" placeholder="Szukaj klocka..." value={search} onChange={e => setSearch(e.target.value)}
            style={{ width: '100%', padding: '8px 12px', border: '1px solid #E2E8F0', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, outline: 'none' }}
          />
          {/* Category pills */}
          {!restrictCat && (
            <div style={{ display: 'flex', gap: 4, marginTop: 10, flexWrap: 'wrap' }}>
              <button onClick={() => setActiveCat(null)} style={{
                padding: '4px 10px', borderRadius: 6, border: '1px solid #E2E8F0', fontSize: 11, fontWeight: 600,
                background: !activeCat ? '#0F172A' : '#fff', color: !activeCat ? '#fff' : '#475569',
                cursor: 'pointer', fontFamily: 'inherit',
              }}>Wszystkie</button>
              {Object.entries(CATEGORIES).map(([key, cat]) => (
                <button key={key} onClick={() => setActiveCat(key)} style={{
                  padding: '4px 10px', borderRadius: 6, border: '1px solid #E2E8F0', fontSize: 11, fontWeight: 600,
                  background: activeCat === key ? cat.color : '#fff', color: activeCat === key ? '#fff' : cat.color,
                  cursor: 'pointer', fontFamily: 'inherit',
                }}>{cat.name}</button>
              ))}
            </div>
          )}
        </div>
        {/* Body */}
        <div style={{ flex: 1, overflow: 'auto', padding: 20 }}>
          {Object.entries(grouped).map(([catKey, blocks]) => {
            const cat = CATEGORIES[catKey];
            return (
              <div key={catKey} style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: cat?.color || '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={cat?.color || '#64748B'} strokeWidth="2"><path d={cat?.icon || ''}/></svg>
                  {cat?.name || catKey}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
                  {blocks.map(b => (
                    <button key={b.code} onClick={() => onPick(b)} style={{
                      padding: '10px 14px', background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10,
                      cursor: 'pointer', textAlign: 'left', fontFamily: 'inherit',
                      transition: 'border-color .15s, box-shadow .15s',
                    }}
                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = cat?.color || '#6366F1'; (e.currentTarget as HTMLElement).style.boxShadow = `0 2px 8px ${cat?.color || '#6366F1'}22`; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = '#E2E8F0'; (e.currentTarget as HTMLElement).style.boxShadow = 'none'; }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                        <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 10, color: cat?.color || '#94A3B8', fontWeight: 700 }}>{b.code}</span>
                        <span style={{ fontSize: 12.5, fontWeight: 600, color: '#0F172A' }}>{b.name}</span>
                        <span style={{ marginLeft: 'auto', fontSize: 9, color: '#94A3B8', fontWeight: 700, border: '1px solid #E2E8F0', padding: '1px 5px', borderRadius: 4 }}>{b.size}</span>
                      </div>
                      <div style={{ fontSize: 11, color: '#64748B', lineHeight: 1.4 }}>{b.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
          {filtered.length === 0 && (
            <div style={{ textAlign: 'center', padding: 40, color: '#94A3B8', fontSize: 13 }}>Brak wynikow</div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── BrandButton (z makiety — popover kolorow) ────────
function BrandButton({ brand, open, setOpen, onChange }: {
  brand: typeof INITIAL_BRAND;
  open: boolean;
  setOpen: (v: boolean) => void;
  onChange: (b: typeof INITIAL_BRAND) => void;
}) {
  const popRef = React.useRef<HTMLDivElement>(null);
  React.useEffect(() => {
    if (!open) return;
    const h = (e: MouseEvent) => { if (popRef.current && !popRef.current.contains(e.target as Node)) setOpen(false); };
    setTimeout(() => document.addEventListener('mousedown', h), 0);
    return () => document.removeEventListener('mousedown', h);
  }, [open]);

  const [picker, setPicker] = React.useState<{target: string; value: string; label: string} | null>(null);

  const bgPreview = brand.bgGradient ? `linear-gradient(135deg, ${brand.bg}, ${brand.bg2})` : brand.bg;
  const ctaPreview = brand.ctaGradient ? `linear-gradient(135deg, ${brand.cta}, ${brand.cta2})` : brand.cta;

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          padding: '6px 12px 6px 8px', background: open ? '#F1F5F9' : '#fff',
          border: '1px solid #E2E8F0', borderRadius: 8,
          display: 'inline-flex', alignItems: 'center', gap: 8,
          cursor: 'pointer', fontFamily: 'inherit', fontSize: 13, fontWeight: 500,
          color: '#334155', transition: 'background .15s',
        }}
      >
        <span style={{ display: 'inline-flex', gap: 3 }}>
          <span style={{ width: 16, height: 18, background: bgPreview, border: '1px solid rgba(0,0,0,.12)', borderRadius: 3 }}/>
          <span style={{ width: 16, height: 18, background: ctaPreview, border: '1px solid rgba(0,0,0,.12)', borderRadius: 3 }}/>
        </span>
        <span>Kolory brandu</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
      </button>

      {open && (
        <div ref={popRef} style={{
          position: 'absolute', top: 'calc(100% + 8px)', right: 0,
          width: 340, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 14,
          boxShadow: '0 16px 40px rgba(15,23,42,.15)', zIndex: 50, padding: 18,
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: 4 }}>
            <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>Kolory brandu</h3>
            <span style={{ marginLeft: 'auto', fontSize: 11, color: '#94A3B8' }}>dla calej strony</span>
          </div>
          <p style={{ margin: '0 0 16px', fontSize: 12, color: '#64748B', lineHeight: 1.5 }}>
            Klocki zaktualizuja sie od razu. Mozesz nadpisac per sekcja w karcie.
          </p>

          {/* TLO */}
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5 }}>Tlo sekcji</div>
            <label style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 11, color: '#64748B', cursor: 'pointer' }}>
              <input type="checkbox" checked={brand.bgGradient} onChange={e => onChange({ ...brand, bgGradient: e.target.checked })} style={{ margin: 0 }}/>
              gradient
            </label>
          </div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 18 }}>
            <button onClick={() => setPicker({ target: 'bg', value: brand.bg, label: brand.bgGradient ? 'Tlo — kolor 1' : 'Tlo sekcji' })}
              style={{ flex: 1, height: 56, borderRadius: 10, background: brand.bg, boxShadow: '0 0 0 1px #E2E8F0', border: 'none', cursor: 'pointer', position: 'relative', padding: 0 }}>
              <span style={{ position: 'absolute', bottom: 4, left: 0, right: 0, fontFamily: 'ui-monospace, monospace', fontSize: 10, color: getContrastColor(brand.bg), fontWeight: 600 }}>{brand.bg.toUpperCase()}</span>
            </button>
            {brand.bgGradient && (
              <button onClick={() => setPicker({ target: 'bg2', value: brand.bg2, label: 'Tlo — kolor 2' })}
                style={{ flex: 1, height: 56, borderRadius: 10, background: brand.bg2, boxShadow: '0 0 0 1px #E2E8F0', border: 'none', cursor: 'pointer', position: 'relative', padding: 0 }}>
                <span style={{ position: 'absolute', bottom: 4, left: 0, right: 0, fontFamily: 'ui-monospace, monospace', fontSize: 10, color: getContrastColor(brand.bg2), fontWeight: 600 }}>{brand.bg2.toUpperCase()}</span>
              </button>
            )}
          </div>

          {/* CTA */}
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5 }}>Kolor CTA</div>
            <label style={{ marginLeft: 'auto', display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 11, color: '#64748B', cursor: 'pointer' }}>
              <input type="checkbox" checked={brand.ctaGradient} onChange={e => onChange({ ...brand, ctaGradient: e.target.checked })} style={{ margin: 0 }}/>
              gradient
            </label>
          </div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
            <button onClick={() => setPicker({ target: 'cta', value: brand.cta, label: brand.ctaGradient ? 'CTA — kolor 1' : 'Kolor CTA' })}
              style={{ flex: 1, height: 56, borderRadius: 10, background: brand.cta, boxShadow: '0 0 0 1px #E2E8F0', border: 'none', cursor: 'pointer', position: 'relative', padding: 0 }}>
              <span style={{ position: 'absolute', bottom: 4, left: 0, right: 0, fontFamily: 'ui-monospace, monospace', fontSize: 10, color: getContrastColor(brand.cta), fontWeight: 600 }}>{brand.cta.toUpperCase()}</span>
            </button>
            {brand.ctaGradient && (
              <button onClick={() => setPicker({ target: 'cta2', value: brand.cta2, label: 'CTA — kolor 2' })}
                style={{ flex: 1, height: 56, borderRadius: 10, background: brand.cta2, boxShadow: '0 0 0 1px #E2E8F0', border: 'none', cursor: 'pointer', position: 'relative', padding: 0 }}>
                <span style={{ position: 'absolute', bottom: 4, left: 0, right: 0, fontFamily: 'ui-monospace, monospace', fontSize: 10, color: getContrastColor(brand.cta2), fontWeight: 600 }}>{brand.cta2.toUpperCase()}</span>
              </button>
            )}
          </div>
          <div style={{
            marginTop: 8, height: 36, borderRadius: 8, background: ctaPreview,
            display: 'grid', placeItems: 'center', color: '#fff', fontSize: 11, fontWeight: 600, letterSpacing: 0.3,
          }}>Podglad CTA →</div>

          <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #E2E8F0', display: 'flex', gap: 8 }}>
            <button onClick={() => onChange(INITIAL_BRAND)} style={{
              padding: '6px 10px', background: 'transparent', border: '1px solid #E2E8F0',
              borderRadius: 7, fontFamily: 'inherit', fontSize: 12, color: '#64748B', cursor: 'pointer',
            }}>Reset</button>
            <div style={{ flex: 1 }}/>
            <button onClick={() => setOpen(false)} style={{
              padding: '6px 14px', background: 'linear-gradient(135deg, #6366F1, #EC4899)',
              color: '#fff', border: 'none', borderRadius: 7,
              fontFamily: 'inherit', fontSize: 12, fontWeight: 600, cursor: 'pointer',
            }}>Gotowe</button>
          </div>
        </div>
      )}

      {picker && (
        <ColorPickerModal
          initial={picker.value}
          label={picker.label}
          onCancel={() => setPicker(null)}
          onConfirm={(val) => { onChange({ ...brand, [picker.target]: val }); setPicker(null); }}
        />
      )}
    </div>
  );
}

// ─── ColorPickerModal (z makiety) ──────────────────────
function ColorPickerModal({ initial, label, onConfirm, onCancel }: {
  initial: string; label: string; onConfirm: (v: string) => void; onCancel: () => void;
}) {
  const [val, setVal] = React.useState(initial);
  const swatches = ['#FFFFFF', '#F8FAFC', '#FEF7ED', '#FEF3C7', '#ECFDF5', '#EEF2FF', '#FCE7F3', '#0F172A', '#6366F1', '#10B981', '#F59E0B', '#EC4899', '#EF4444', '#0EA5E9', '#8B5CF6', '#334155'];
  return (
    <div onMouseDown={(e) => e.stopPropagation()} style={{
      position: 'fixed', inset: 0, background: 'rgba(15,23,42,.45)', zIndex: 100,
      display: 'grid', placeItems: 'center',
    }}>
      <div style={{ width: 340, background: '#fff', borderRadius: 14, boxShadow: '0 24px 60px rgba(15,23,42,.3)', padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: 14 }}>
          <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>{label}</h3>
          <button onClick={onCancel} style={{ marginLeft: 'auto', background: 'transparent', border: 'none', cursor: 'pointer', color: '#94A3B8', fontSize: 18, padding: 0, lineHeight: 1 }}>x</button>
        </div>
        <div style={{ height: 64, borderRadius: 10, background: val, boxShadow: '0 0 0 1px #E2E8F0', marginBottom: 14, display: 'grid', placeItems: 'center' }}>
          <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 13, fontWeight: 600, color: getContrastColor(val) }}>{val.toUpperCase()}</span>
        </div>
        <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Sugestie</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 5, marginBottom: 14 }}>
          {swatches.map(c => (
            <button key={c} onClick={() => setVal(c)} style={{
              aspectRatio: '1/1', background: c, border: val.toLowerCase() === c.toLowerCase() ? '2px solid #6366F1' : '1px solid #E2E8F0',
              borderRadius: 7, cursor: 'pointer', padding: 0,
            }}/>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <label style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 10px', border: '1px solid #E2E8F0', borderRadius: 8, cursor: 'pointer' }}>
            <div style={{ width: 18, height: 18, borderRadius: 4, background: val, border: '1px solid rgba(0,0,0,.1)' }}/>
            <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 12, color: '#475569' }}>wlasny</span>
            <input type="color" value={val} onChange={e => setVal(e.target.value)} style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer' }}/>
          </label>
          <input type="text" value={val} onChange={e => setVal(e.target.value)}
            style={{ flex: 1, padding: '6px 10px', border: '1px solid #E2E8F0', borderRadius: 8, fontFamily: 'ui-monospace, monospace', fontSize: 12, color: '#475569' }}/>
        </div>
        <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
          <button onClick={onCancel} style={{
            padding: '8px 14px', background: 'transparent', border: '1px solid #E2E8F0',
            borderRadius: 8, fontFamily: 'inherit', fontSize: 13, color: '#475569', cursor: 'pointer',
          }}>Anuluj</button>
          <div style={{ flex: 1 }}/>
          <button onClick={() => onConfirm(val)} style={{
            padding: '8px 18px', background: 'linear-gradient(135deg, #6366F1, #EC4899)',
            color: '#fff', border: 'none', borderRadius: 8,
            fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: 'pointer',
          }}>Gotowe</button>
        </div>
      </div>
    </div>
  );
}
