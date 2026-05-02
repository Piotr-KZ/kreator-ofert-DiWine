// Step3Kreator — adaptacja z makiety app.jsx (590 linii)
// Zmiany vs makieta: multi-page → single page, window.X → import, dane → store,
// top bar + stepper usunięte (już w LabLayout)

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useLabStore } from '@/store/labStore';
import { BLOCK_LIBRARY, CATEGORIES, BRAND_PALETTE, INITIAL_BRAND, getBlocksForSiteType, getCategoriesForSiteType } from '@/config/blocks';
import type { Block, Category } from '@/config/blocks';
import SectionCard from '@/components/kreator/SectionCard';

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
  const { sections, projectName, siteType, addSection, removeSection, reorderSections, duplicateSection, updateSection: storeUpdateSection, generateContent, isGenerating } = useLabStore();

  const availableBlocks = getBlocksForSiteType(siteType);
  const availableCategories = getCategoriesForSiteType(siteType);
  const isOffer = siteType === 'offer';

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
      const b = availableBlocks.find(x => x.code === sec.block_code) || BLOCK_LIBRARY.find(x => x.code === sec.block_code);
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
            const block = availableBlocks.find(b => b.code === s.block_code) || BLOCK_LIBRARY.find(b => b.code === s.block_code);
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
                  <SectionCard
                    section={s}
                    index={i}
                    total={sections.length}
                    brand={brand}
                    onUpdate={(patch) => storeUpdateSection(s.id, patch)}
                    onMove={(dir) => move(s.id, dir)}
                    onDelete={() => del(s.id)}
                    onDuplicate={() => duplicate(s.id)}
                    onAI={() => openAI(s)}
                    onOpenVariants={() => setVariantsModal({ mode: 'swap', targetId: s.id, restrictCat: block?.cat })}
                  />
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
          <button disabled={isGenerating} onClick={async () => { if (!isOffer) await generateContent(); navigate(`/lab/${projectId}/step/4`); }} style={{
            padding: '10px 20px', background: 'linear-gradient(135deg, #6366F1, #EC4899)',
            color: '#fff', border: 'none', borderRadius: 10,
            fontFamily: 'inherit', fontSize: 14, fontWeight: 600, cursor: isGenerating ? 'wait' : 'pointer',
            display: 'inline-flex', alignItems: 'center', gap: 6,
            boxShadow: '0 2px 8px rgba(99,102,241,.25)',
            opacity: isGenerating ? 0.7 : 1,
          }}>
            {isGenerating ? 'Generuję treści...' : 'Dalej: Tresci'}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

      {/* AI panel — pełny z makiety ai_panel.jsx */}
      <AIPanel open={aiOpen} onClose={() => setAiOpen(false)} context={aiContext} onToast={showToast} />

      {/* Blocks modal */}
      <BlocksModal
        open={!!variantsModal}
        onClose={() => setVariantsModal(null)}
        onPick={onPickFromModal}
        restrictCat={variantsModal?.restrictCat}
        title={variantsModal?.mode === 'swap' ? 'Wybierz inny wariant tej sekcji' : 'Dodaj nowa sekcje'}
        blocks={availableBlocks}
        categories={availableCategories}
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
export function BlocksModal({ open, onClose, onPick, restrictCat, title, blocks, categories }: {
  open: boolean;
  onClose: () => void;
  onPick: (block: Block) => void;
  restrictCat?: string;
  title: string;
  blocks?: Block[];
  categories?: Record<string, Category>;
}) {
  const [search, setSearch] = React.useState('');
  const [activeCat, setActiveCat] = React.useState<string | null>(null);

  if (!open) return null;

  const blockList = blocks || BLOCK_LIBRARY;
  const catList = categories || CATEGORIES;
  const effectiveCat = restrictCat || activeCat;
  const filtered = blockList.filter(b => {
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
      <div onClick={e => e.stopPropagation()} style={{ width: 820, maxHeight: '85vh', background: '#fff', borderRadius: 16, boxShadow: '0 24px 60px rgba(15,23,42,.3)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
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
              {Object.entries(catList).map(([key, cat]) => (
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
            const cat = catList[catKey];
            return (
              <div key={catKey} style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: cat?.color || '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={cat?.color || '#64748B'} strokeWidth="2"><path d={cat?.icon || ''}/></svg>
                  {cat?.name || catKey}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                  {blocks.map(b => (
                    <button key={b.code} onClick={() => onPick(b)} style={{
                      padding: 0, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10,
                      cursor: 'pointer', textAlign: 'left', fontFamily: 'inherit',
                      transition: 'border-color .15s, box-shadow .15s', overflow: 'hidden',
                    }}
                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = cat?.color || '#6366F1'; (e.currentTarget as HTMLElement).style.boxShadow = `0 2px 8px ${cat?.color || '#6366F1'}22`; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = '#E2E8F0'; (e.currentTarget as HTMLElement).style.boxShadow = 'none'; }}
                    >
                      {b.thumb && (
                        <div style={{ height: 80, background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', display: 'grid', placeItems: 'center' }}>
                          <svg width="140" height="60" viewBox="0 0 80 56" xmlns="http://www.w3.org/2000/svg" dangerouslySetInnerHTML={{ __html: b.thumb }}/>
                        </div>
                      )}
                      <div style={{ padding: '10px 12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                          <span style={{ fontFamily: 'ui-monospace, monospace', fontSize: 9, color: cat?.color || '#94A3B8', fontWeight: 700 }}>{b.code}</span>
                          <span style={{ marginLeft: 'auto', fontSize: 9, color: '#94A3B8', fontWeight: 700, border: '1px solid #E2E8F0', padding: '1px 5px', borderRadius: 4 }}>{b.size}</span>
                        </div>
                        <div style={{ fontSize: 11.5, fontWeight: 700, color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.3, marginBottom: 3 }}>{b.name}</div>
                        <div style={{ fontSize: 10.5, color: '#64748B', lineHeight: 1.3 }}>{b.desc}</div>
                      </div>
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

// ─── AIPanel (z makiety ai_panel.jsx) ───────────────────
function AIPanel({ open, onClose, context, onToast }: {
  open: boolean;
  onClose: () => void;
  context: { code: string; label: string; name: string } | null;
  onToast: (msg: string, icon?: string) => void;
}) {
  const [width, setWidth] = React.useState(Math.max(420, Math.round(window.innerWidth / 3)));
  const [messages, setMessages] = React.useState<Array<{ role: string; text: string }>>([
    { role: 'assistant', text: 'Czesc! Jestem twoim asystentem AI. Pomoge Ci ze struktura, wyborem klockow lub napisaniem tekstow. O co chcesz zapytac?' }
  ]);
  const [input, setInput] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [dragging, setDragging] = React.useState(false);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (!dragging) return;
    const onMove = (e: MouseEvent) => {
      const w = Math.min(Math.max(window.innerWidth - e.clientX, 360), window.innerWidth * 0.7);
      setWidth(w);
    };
    const onUp = () => setDragging(false);
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
    return () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); };
  }, [dragging]);

  React.useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  const send = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || loading) return;
    setInput('');
    setMessages(m => [...m, { role: 'user', text: msg }]);
    setLoading(true);
    // Stub — w przyszłości podłączymy do backendu
    setTimeout(() => {
      setMessages(m => [...m, { role: 'assistant', text: 'To jest wersja demo asystenta AI. Podłączenie do backendu nastąpi w kolejnym kroku integracji.' }]);
      setLoading(false);
    }, 800);
  };

  if (!open) return null;

  return (
    <>
      <div style={{
        position: 'fixed', inset: 0, background: 'rgba(15,23,42,.15)',
        zIndex: 150, animation: 'fadeIn .2s',
      }} onClick={onClose} />

      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0,
        width, background: '#fff',
        boxShadow: '-8px 0 30px rgba(15,23,42,.1)',
        zIndex: 151, display: 'flex', flexDirection: 'column',
      }}>
        {/* Resize handle */}
        <div
          onMouseDown={() => setDragging(true)}
          style={{
            position: 'absolute', left: -3, top: 0, bottom: 0, width: 6,
            cursor: 'ew-resize', zIndex: 2,
          }}
          title="Przesun aby zmienic szerokosc"
        >
          <div style={{ position: 'absolute', left: 2, top: '50%', transform: 'translateY(-50%)', width: 4, height: 40, borderRadius: 3, background: dragging ? '#6366F1' : '#CBD5E1', transition: 'background .15s' }}/>
        </div>

        {/* Header */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #6366F1, #EC4899)',
            display: 'grid', placeItems: 'center',
            boxShadow: '0 2px 8px rgba(99,102,241,.3)',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 15, fontWeight: 600 }}>Asystent AI</div>
            <div style={{ fontSize: 12, color: '#64748B' }}>
              {context ? <>Kontekst: <span style={{ fontFamily: 'ui-monospace, monospace', background: '#F1F5F9', padding: '1px 6px', borderRadius: 4, fontSize: 11 }}>{context.code}</span> · {context.label}</> : 'Bez kontekstu'}
            </div>
          </div>
          <button onClick={onClose} style={{ width: 34, height: 34, border: '1px solid #E2E8F0', background: '#fff', borderRadius: 8, cursor: 'pointer', display: 'grid', placeItems: 'center', color: '#64748B' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>

        {/* Messages */}
        <div ref={scrollRef} style={{ flex: 1, overflow: 'auto', padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
          {messages.map((m, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
              {m.role === 'assistant' && <div style={{ width: 26, height: 26, borderRadius: 7, background: 'linear-gradient(135deg, #6366F1, #EC4899)', flexShrink: 0, display: 'grid', placeItems: 'center' }}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/></svg>
              </div>}
              <div style={{
                maxWidth: '78%', padding: '10px 14px', borderRadius: 12,
                background: m.role === 'user' ? 'linear-gradient(135deg, #6366F1, #7C3AED)' : '#F1F5F9',
                color: m.role === 'user' ? '#fff' : '#0F172A',
                fontSize: 13.5, lineHeight: 1.5, whiteSpace: 'pre-wrap',
              }}>{m.text}</div>
            </div>
          ))}
          {loading && <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <div style={{ width: 26, height: 26, borderRadius: 7, background: 'linear-gradient(135deg, #6366F1, #EC4899)', flexShrink: 0 }}/>
            <div style={{ display: 'flex', gap: 4, padding: '10px 14px', background: '#F1F5F9', borderRadius: 12 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#94A3B8', animation: 'bounce 1s 0ms infinite' }}/>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#94A3B8', animation: 'bounce 1s 150ms infinite' }}/>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#94A3B8', animation: 'bounce 1s 300ms infinite' }}/>
            </div>
          </div>}
        </div>

        {/* Quick prompts */}
        {messages.length <= 1 && (
          <div style={{ padding: '0 20px 8px', display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {['Zaproponuj strukture', 'Jaki hero wybrac?', 'Skroc strukture', 'Sekcje pod SEO'].map((p, i) => (
              <button key={i} onClick={() => send(p)} style={{
                padding: '6px 10px', background: '#F1F5F9', border: '1px solid #E2E8F0',
                borderRadius: 14, fontSize: 12, color: '#334155',
                cursor: 'pointer', fontFamily: 'inherit',
              }}
                onMouseEnter={e => { e.currentTarget.style.background = '#EEF2FF'; e.currentTarget.style.color = '#6366F1'; }}
                onMouseLeave={e => { e.currentTarget.style.background = '#F1F5F9'; e.currentTarget.style.color = '#334155'; }}
              >{p}</button>
            ))}
          </div>
        )}

        {/* Input */}
        <div style={{ padding: 16, borderTop: '1px solid #E2E8F0', background: '#FAFBFC' }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 12, padding: 4 }}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
              placeholder="Zadaj pytanie... (Enter wysyla, Shift+Enter nowa linia)"
              rows={1}
              style={{
                flex: 1, border: 'none', outline: 'none', background: 'transparent',
                padding: '8px 10px', fontFamily: 'inherit', fontSize: 13.5, resize: 'none',
                maxHeight: 120,
              }}
            />
            <button
              onClick={() => send()}
              disabled={!input.trim() || loading}
              style={{
                width: 34, height: 34, border: 'none', borderRadius: 8,
                background: (!input.trim() || loading) ? '#CBD5E1' : 'linear-gradient(135deg, #6366F1, #EC4899)',
                color: '#fff', cursor: (!input.trim() || loading) ? 'not-allowed' : 'pointer',
                display: 'grid', placeItems: 'center',
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
