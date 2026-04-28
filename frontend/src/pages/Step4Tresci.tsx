import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import { SECTION_RENDERERS, EditCtx } from "@/components/shared/SectionRenderers";
import { DENSITY_SCALE, FONT_OPTIONS } from "@/components/tresci/ContentRenderer";
import { useLabStore } from "@/store/labStore";
// Tresci — main app


function makeTypo({ density, headingFont, bodyFont }) {
  const d = DENSITY_SCALE[density] || DENSITY_SCALE[3];
  const bodySize = d.bodySize;
  const s = d.scale;
  return {
    headingFont,
    bodyFont,
    body: bodySize,
    lineHeight: d.lineHeight,
    spacing: d.spacing,
    eyebrow: Math.round(bodySize * 0.8),
    h3: Math.round(bodySize * s * s),
    h2: Math.round(bodySize * s * s * s),
    h1: Math.round(bodySize * s * s * s * s),
    // kompatybilność wsteczna:
    heading: headingFont,
  };
}

// Lab Creator: single page, sections from store
// (multi-page removed — Lab Creator has 1 page)


// Map store section → renderer format (code/fields/bg)
function mapFromStore(s) {
  const slots = s.slots_json || {};
  return { id: s.id, code: s.block_code, label: slots.label || s.block_code, bg: slots.bg || null, fields: slots };
}

export default function Step4Tresci() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const storeSections = useLabStore(s => s.sections);
  const storeUpdateSlot = useLabStore(s => s.updateSlot);
  const generateVisualConcept = useLabStore(s => s.generateVisualConcept);
  const [isGeneratingVC, setIsGeneratingVC] = React.useState(false);
  const [content, setContent] = React.useState(() => storeSections.map(mapFromStore));
  React.useEffect(() => { setContent(storeSections.map(mapFromStore)); }, [storeSections]);

  const [density, setDensity] = React.useState(3);
  const [headingFont, setHeadingFont] = React.useState('Fraunces');
  const [bodyFont, setBodyFont] = React.useState('Plus Jakarta Sans');
  const [viewport, setViewport] = React.useState('desktop');
  const [selected, setSelected] = React.useState(null); // {sectionId, elId, rect, ...handlers}
  const [overrides, setOverrides] = React.useState({}); // { pageId__sectionId: { elId: { ..., perBreakpoint: {mobile:{...}, tablet:{...}} } } }
  const [aiChatOpen, setAiChatOpen] = React.useState(false);
  const [aiMessages, setAiMessages] = React.useState([
    { role: 'ai', text: 'Cześć! Znam brief Miętowej i widzę wszystkie sekcje. Powiedz, co mam przepisać, poprawić albo dodać. Możesz też kliknąć konkretny tekst i ja go zmienię.' },
  ]);
  const [typoOpen, setTypoOpen] = React.useState(false);
  const [toast, setToast] = React.useState(null);
  const [hoveredSection, setHoveredSection] = React.useState(null);
  const [aiDiff, setAiDiff] = React.useState(null); // { scope, prompt, changes: [{sectionId, elId, label, before, after}] }
  const [ghostUndo, setGhostUndo] = React.useState(null); // { label, snapshot, expiresAt }

  // Undo/Redo — jeden stack dla wszystkich mutacji
  const historyRef = React.useRef({ past: [], future: [] });
  const pushHistory = React.useCallback((label) => {
    historyRef.current.past.push({
      label,
      snapshot: JSON.parse(JSON.stringify({ content, overrides })),
    });
    if (historyRef.current.past.length > 50) historyRef.current.past.shift();
    historyRef.current.future = [];
  }, [content, overrides]);
  const undo = React.useCallback(() => {
    const h = historyRef.current;
    if (!h.past.length) return false;
    const entry = h.past.pop();
    h.future.push({ label: entry.label, snapshot: JSON.parse(JSON.stringify({ content, overrides })) });
    setContent(entry.snapshot.content);
    setOverrides(entry.snapshot.overrides);
    return entry.label;
  }, [content, overrides]);
  const redo = React.useCallback(() => {
    const h = historyRef.current;
    if (!h.future.length) return false;
    const entry = h.future.pop();
    h.past.push({ label: entry.label, snapshot: JSON.parse(JSON.stringify({ content, overrides })) });
    setContent(entry.snapshot.content);
    setOverrides(entry.snapshot.overrides);
    return entry.label;
  }, [content, overrides]);

  const brand = { bg: '#FFFFFF', bg2: '#F1F5F9', cta: '#6366F1', cta2: '#EC4899', ctaGradient: true };

  const ovKey = (sectionId) => sectionId;
  const getOv = (sectionId, elId) => {
    const page = overrides[ovKey(sectionId)] || {};
    const base = page[elId] || {};
    // If in mobile/tablet viewport, merge per-breakpoint on top
    if (viewport !== 'desktop' && base.perBp && base.perBp[viewport]) {
      return { ...base, ...base.perBp[viewport], __activeBp: viewport };
    }
    return base;
  };

  const updateSection = (id, patch) => { pushHistory('Edycja sekcji'); setContent(prev => prev.map(s => s.id === id ? { ...s, ...patch } : s)); };

  const patchOverride = (sectionId, elId, patch, opts = {}) => {
    const bp = opts.bp || (viewport !== 'desktop' ? viewport : null);
    if (!opts.noHistory) pushHistory('Edycja stylu');
    setOverrides(prev => {
      const k = ovKey(sectionId);
      const pageOv = prev[k] || {};
      const elOv = pageOv[elId] || {};
      if (bp) {
        // Write into perBp[bp]
        const perBp = elOv.perBp || {};
        const bpOv = { ...(perBp[bp] || {}), ...patch };
        return { ...prev, [k]: { ...pageOv, [elId]: { ...elOv, perBp: { ...perBp, [bp]: bpOv } } } };
      }
      return { ...prev, [k]: { ...pageOv, [elId]: { ...elOv, ...patch } } };
    });
  };
  const removeOverride = (sectionId, elId) => { pushHistory('Usuń element'); patchOverride(sectionId, elId, { deleted: true }, { noHistory: true }); };
  const copyOverride = (sectionId, elId) => { showToast('Skopiowano element 📋'); };

  // Sekcja operations (quick actions)
  const duplicateSection = (id) => {
    pushHistory('Duplikuj sekcję');
    setContent(prev => {
      const idx = prev.findIndex(s => s.id === id);
      if (idx < 0) return prev;
      const clone = { ...prev[idx], id: prev[idx].id + '-dup-' + Math.random().toString(36).slice(2, 6) };
      return [...prev.slice(0, idx + 1), clone, ...prev.slice(idx + 1)];
    });
    showToast('Zduplikowano sekcję');
  };
  const deleteSection = (id) => {
    pushHistory('Usuń sekcję');
    setContent(prev => prev.filter(s => s.id !== id));
    showToast('Usunięto sekcję');
  };
  const moveSection = (id, dir) => {
    pushHistory('Przesuń sekcję');
    setContent(prev => {
      const idx = prev.findIndex(s => s.id === id);
      if (idx < 0) return prev;
      const target = dir === 'up' ? idx - 1 : idx + 1;
      if (target < 0 || target >= prev.length) return prev;
      const next = prev.slice();
      [next[idx], next[target]] = [next[target], next[idx]];
      return next;
    });
  };

  const stageWidth = viewport === 'mobile' ? 390 : viewport === 'tablet' ? 768 : 1440;

  const containerRef = React.useRef(null);
  const [containerW, setContainerW] = React.useState(1200);
  React.useLayoutEffect(() => {
    const update = () => { if (containerRef.current) setContainerW(containerRef.current.clientWidth); };
    update();
    const ro = new ResizeObserver(update);
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);
  const fitScale = Math.min(1, (containerW - 40) / stageWidth);

  React.useEffect(() => {
    const h = (e) => {
      if (e.key === 'Escape') { setSelected(null); setTypoOpen(false); setAiDiff(null); }
      // Undo / Redo
      const meta = e.metaKey || e.ctrlKey;
      if (meta && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        const label = undo();
        if (label) showToast('↶ Cofnięto: ' + label);
      }
      if (meta && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault();
        const label = redo();
        if (label) showToast('↷ Przywrócono: ' + label);
      }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [undo, redo]);

  // Click outside deselects
  React.useEffect(() => {
    const h = (e) => {
      if (e.target.closest('[data-element-toolbar]')) return;
      if (e.target.closest('[contenteditable]')) return;
      setSelected(null);
    };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 2200); };

  const editCtxValue = {
    selected,
    select: setSelected,
    overrides,
    getOv,
    patchOverride,
    removeOverride,
    copyOverride,
    viewport,
    hoveredSection,
    setHoveredSection,
    duplicateSection,
    deleteSection,
    moveSection,
    pushHistory,
    hideImages: true,
  };

  return (
    <EditCtx.Provider value={editCtxValue}>
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Toolbar — typografia, undo/redo, device switcher */}
      <div style={{
        height: 48, borderBottom: '1px solid #E2E8F0', background: '#fff',
        display: 'flex', alignItems: 'center', padding: '0 24px', gap: 16, position: 'sticky', top: 0, zIndex: 40,
      }}>
        <TypoPopover
          open={typoOpen} setOpen={setTypoOpen}
          density={density} setDensity={setDensity}
          headingFont={headingFont} setHeadingFont={setHeadingFont}
          bodyFont={bodyFont} setBodyFont={setBodyFont}
        />

        <div style={{ display: 'inline-flex', gap: 2, padding: 3, background: '#F1F5F9', borderRadius: 8 }}>
          <button onClick={() => { const l = undo(); if (l) showToast('↶ Cofnięto'); }}
            title="Cofnij (Cmd+Z)"
            disabled={!historyRef.current.past.length}
            style={{ width: 30, height: 28, border: 'none', background: 'transparent', cursor: 'pointer', borderRadius: 6, color: '#64748B', display: 'grid', placeItems: 'center', opacity: historyRef.current.past.length ? 1 : 0.35 }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M9 14l-4-4 4-4"/><path d="M5 10h9a6 6 0 010 12h-2"/></svg>
          </button>
          <button onClick={() => { const l = redo(); if (l) showToast('↷ Przywrócono'); }}
            title="Przywróć (Cmd+Shift+Z)"
            disabled={!historyRef.current.future.length}
            style={{ width: 30, height: 28, border: 'none', background: 'transparent', cursor: 'pointer', borderRadius: 6, color: '#64748B', display: 'grid', placeItems: 'center', opacity: historyRef.current.future.length ? 1 : 0.35 }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M15 14l4-4-4-4"/><path d="M19 10h-9a6 6 0 000 12h2"/></svg>
          </button>
        </div>

        <DeviceSwitcher viewport={viewport} setViewport={setViewport}/>

        <div style={{ flex: 1 }}/>

        <button disabled={isGeneratingVC} onClick={async () => {
          setIsGeneratingVC(true);
          try { await generateVisualConcept(); } catch(_) { /* handled by store */ } finally { setIsGeneratingVC(false); }
          navigate(`/lab/${projectId}/step/5`);
        }} style={{
          padding: '8px 18px', background: isGeneratingVC ? '#94A3B8' : 'linear-gradient(135deg, #6366F1, #EC4899)',
          color: '#fff', border: 'none', borderRadius: 8,
          fontFamily: 'inherit', fontSize: 13, fontWeight: 600, cursor: isGeneratingVC ? 'wait' : 'pointer',
          display: 'inline-flex', alignItems: 'center', gap: 6,
          boxShadow: '0 2px 8px rgba(99,102,241,.25)',
          opacity: isGeneratingVC ? 0.7 : 1,
        }}>
          {isGeneratingVC ? 'Generuję wizualizację…' : 'Dalej: Wizualizacja'}
          {!isGeneratingVC && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M5 12h14M13 5l7 7-7 7"/></svg>}
        </button>
      </div>

      {/* Canvas */}
      <div style={{ flex: 1, padding: '24px 24px 120px', background: '#F5F6FA', position: 'relative' }}>
        <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ fontSize: 10, fontWeight: 600, color: '#6366F1', textTransform: 'uppercase', letterSpacing: 0.8 }}>● Krok 4 z 5 · Treści</div>
          <div style={{ fontSize: 13, color: '#64748B' }}>
            Kliknij dowolny tekst. Najedź na sekcję by ją zduplikować, usunąć lub przesunąć.
            {viewport !== 'desktop' && (
              <span style={{ marginLeft: 10, padding: '3px 9px', background: '#FEF3C7', color: '#92400E', borderRadius: 999, fontSize: 11, fontWeight: 600 }}>
                ✎ Tryb {viewport === 'mobile' ? 'Mobile' : 'Tablet'} — zmiany zapisują się tylko dla tego ekranu
              </span>
            )}
          </div>
        </div>

        <div ref={containerRef} style={{ width: '100%', position: 'relative' }}>
          <div style={{
            width: stageWidth, transformOrigin: 'top left', transform: `scale(${fitScale})`,
            margin: '0 auto', height: 'auto',
          }}>
            <div style={{
              width: stageWidth, background: '#fff', borderRadius: 16, overflow: 'hidden',
              boxShadow: '0 4px 20px rgba(15,23,42,.08), 0 0 0 1px rgba(15,23,42,.06)',
            }}>
              {content.map((s, idx) => {
                const Renderer = SECTION_RENDERERS[s.code] || SECTION_RENDERERS.PLACEHOLDER;
                if (!Renderer) return null;
                const typo = makeTypo({ density, headingFont, bodyFont });
                return (
                  <div key={s.id}
                    onMouseEnter={() => setHoveredSection(s.id)}
                    onMouseLeave={() => setHoveredSection(prev => prev === s.id ? null : prev)}
                    style={{ position: 'relative' }}>
                    <Renderer s={s} brand={brand} typo={typo} update={p => updateSection(s.id, p)}/>
                    {hoveredSection === s.id && !selected && (
                      <SectionHoverActions
                        scale={fitScale}
                        label={s.title || s.code}
                        canUp={idx > 0}
                        canDown={idx < content.length - 1}
                        onDup={() => duplicateSection(s.id)}
                        onDel={() => deleteSection(s.id)}
                        onUp={() => moveSection(s.id, 'up')}
                        onDown={() => moveSection(s.id, 'down')}
                        onVariant={() => showToast('Wybór wariantu — otwórz Strukturę')}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Ghost undo — pojawia się po AI edit na 10s */}
      {ghostUndo && (
        <GhostUndo
          label={ghostUndo.label}
          onUndo={() => {
            setContent(ghostUndo.snapshot.content);
            setOverrides(ghostUndo.snapshot.overrides);
            setGhostUndo(null);
            showToast('↶ Cofnięto zmianę AI');
          }}
          onDismiss={() => setGhostUndo(null)}
        />
      )}

      {/* AI Diff modal */}
      {aiDiff && (
        <AiDiffModal
          diff={aiDiff}
          onAccept={() => {
            setGhostUndo({
              label: aiDiff.prompt,
              snapshot: JSON.parse(JSON.stringify({ content, overrides })),
            });
            setTimeout(() => setGhostUndo(prev => prev ? null : prev), 10000);
            setAiDiff(null);
            showToast('✨ AI zastosował zmiany');
          }}
          onReject={() => { setAiDiff(null); showToast('Odrzucono propozycję AI'); }}
        />
      )}

      {/* Element toolbar (fixed positioning near selected element) */}
      {selected && (
        <ElementToolbar
          key={selected.sectionId + '|' + selected.elId}
          selected={selected}
          liveOv={getOv(selected.sectionId, selected.elId)}
          viewport={viewport}
          onPatch={(patch) => patchOverride(selected.sectionId, selected.elId, patch)}
          onCopy={() => { copyOverride(selected.sectionId, selected.elId); setSelected(null); }}
          onRemove={() => { removeOverride(selected.sectionId, selected.elId); setSelected(null); showToast('Usunięto element'); }}
          onAi={() => setAiChatOpen(true)}
        />
      )}

      {aiChatOpen && (
        <AiChat
          messages={aiMessages}
          selected={selected}
          onSend={(text) => {
            setAiMessages(prev => [...prev, { role: 'user', text }]);
            // Simulate AI generating a diff
            setTimeout(() => {
              const scope = selected ? 'element' : 'page';
              const changes = buildMockAiDiff({ scope, selected, content, prompt: text });
              setAiMessages(prev => [...prev, { role: 'ai', text: `Przygotowałem ${changes.length} ${changes.length === 1 ? 'zmianę' : 'zmiany'}. Zobacz diff po prawej i zdecyduj co przyjąć.` }]);
              setAiDiff({ scope, prompt: text, changes });
            }, 700);
          }}
          onClose={() => setAiChatOpen(false)}
        />
      )}

      {/* AI FAB - zawsze dostępny */}
      {!aiChatOpen && (
        <button onClick={() => setAiChatOpen(true)}
          style={{
            position: 'fixed', right: 24, bottom: 24, zIndex: 60,
            padding: '12px 18px', background: 'linear-gradient(135deg, #6366F1, #EC4899)',
            color: '#fff', border: 'none', borderRadius: 999,
            fontSize: 13, fontWeight: 600, cursor: 'pointer',
            display: 'inline-flex', alignItems: 'center', gap: 8,
            boxShadow: '0 12px 30px rgba(99,102,241,.35), 0 4px 10px rgba(15,23,42,.15)',
            fontFamily: 'inherit',
          }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
          AI asystent
        </button>
      )}

      {toast && (
        <div style={{
          position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)',
          padding: '10px 18px', background: '#0F172A', color: '#fff',
          borderRadius: 10, fontSize: 13, fontWeight: 500,
          animation: 'toastIn .25s', zIndex: 100, boxShadow: '0 8px 24px rgba(15,23,42,.3)',
        }}>{toast}</div>
      )}
    </div>
    </EditCtx.Provider>
  );
}

// StepperBold removed — stepper is in LabLayout

function DeviceSwitcher({ viewport, setViewport }) {
  const items = [
    { id: 'desktop', label: 'Desktop', w: 1440, icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg> },
    { id: 'tablet', label: 'Tablet', w: 768, icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="5" y="2" width="14" height="20" rx="2"/></svg> },
    { id: 'mobile', label: 'Mobile', w: 390, icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="6" y="2" width="12" height="20" rx="2"/></svg> },
  ];
  return (
    <div style={{ display: 'flex', gap: 2, padding: 3, background: '#F1F5F9', borderRadius: 9 }}>
      {items.map(it => (
        <button key={it.id} onClick={() => setViewport(it.id)}
          title={`${it.label} — ${it.w}px`}
          style={{
            padding: '5px 10px', border: 'none', borderRadius: 7,
            background: viewport === it.id ? '#fff' : 'transparent',
            color: viewport === it.id ? '#0F172A' : '#64748B',
            fontSize: 12, fontWeight: 500, cursor: 'pointer',
            display: 'inline-flex', alignItems: 'center', gap: 6,
            boxShadow: viewport === it.id ? '0 1px 2px rgba(15,23,42,.08)' : 'none',
          }}>
          {it.icon} {it.label}
        </button>
      ))}
    </div>
  );
}

function TypoPopover({ open, setOpen, density, setDensity, headingFont, setHeadingFont, bodyFont, setBodyFont }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (!open) return;
    const h = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    setTimeout(() => document.addEventListener('mousedown', h), 0);
    return () => document.removeEventListener('mousedown', h);
  }, [open]);
  const densityLabels = { 1: 'Kompakt', 2: 'Zwarty', 3: 'Komfort', 4: 'Przestronny', 5: 'Luźny' };
  return (
    <div style={{ position: 'relative' }}>
      <button onClick={() => setOpen(!open)} style={{
        padding: '6px 12px 6px 10px', background: open ? '#F1F5F9' : '#fff',
        border: '1px solid #E2E8F0', borderRadius: 8,
        display: 'inline-flex', alignItems: 'center', gap: 10,
        cursor: 'pointer', fontSize: 13, fontWeight: 500, color: '#334155',
      }}>
        <span style={{ fontFamily: `'${headingFont}', serif`, fontSize: 16, fontWeight: 700, lineHeight: 1 }}>Aa</span>
        <span style={{ fontSize: 11, color: '#94A3B8' }}>/</span>
        <span style={{ fontFamily: `'${bodyFont}', sans-serif`, fontSize: 13, fontWeight: 500, lineHeight: 1 }}>Aa</span>
        <span>Typografia</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      {open && (
        <div ref={ref} style={{
          position: 'absolute', top: 'calc(100% + 8px)', left: 0,
          width: 380, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 14,
          boxShadow: '0 16px 40px rgba(15,23,42,.15)', zIndex: 50, padding: 20,
          animation: 'slideUp .15s',
        }}>
          <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: 14 }}>
            <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>Typografia globalna</h3>
            <span style={{ marginLeft: 'auto', fontSize: 11, color: '#94A3B8' }}>dla całej strony</span>
          </div>

          <FontSelect label="Font nagłówków" value={headingFont} onChange={setHeadingFont} sample="Miętowa"/>
          <div style={{ height: 12 }}/>
          <FontSelect label="Font treści" value={bodyFont} onChange={setBodyFont} sample="Kawa palona dziś rano"/>

          <div style={{ height: 16 }}/>
          <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Gęstość tekstu</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <input type="range" min={1} max={5} step={1} value={density} onChange={e => setDensity(+e.target.value)}
              style={{ flex: 1, accentColor: '#6366F1' }}/>
            <div style={{ width: 88, fontSize: 12, color: '#0F172A', fontWeight: 600, textAlign: 'right' }}>{densityLabels[density]}</div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: '#94A3B8', marginTop: 4, fontFamily: 'ui-monospace, monospace' }}>
            <span>kompakt</span><span>komfort</span><span>luźny</span>
          </div>
          <div style={{ marginTop: 10, padding: '10px 12px', background: '#F8FAFC', borderRadius: 8, border: '1px solid #E2E8F0' }}>
            <div style={{ fontFamily: `'${headingFont}', serif`, fontSize: DENSITY_SCALE[density].bodySize * DENSITY_SCALE[density].scale * DENSITY_SCALE[density].scale, fontWeight: 700, lineHeight: 1.1, color: '#0F172A', letterSpacing: '-0.01em' }}>Nagłówek</div>
            <div style={{ fontFamily: `'${bodyFont}', sans-serif`, fontSize: DENSITY_SCALE[density].bodySize, lineHeight: DENSITY_SCALE[density].lineHeight, color: '#475569', marginTop: 4 }}>Przykładowy paragraf z treścią strony.</div>
          </div>

          <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #E2E8F0', display: 'flex', gap: 8 }}>
            <button onClick={() => { setHeadingFont('Fraunces'); setBodyFont('Plus Jakarta Sans'); setDensity(3); }} style={{
              padding: '6px 10px', background: 'transparent', border: '1px solid #E2E8F0',
              borderRadius: 7, fontSize: 12, color: '#64748B', cursor: 'pointer',
            }}>↺ Reset</button>
            <div style={{ flex: 1 }}/>
            <button onClick={() => setOpen(false)} style={{
              padding: '6px 14px', background: 'linear-gradient(135deg, #6366F1, #EC4899)',
              color: '#fff', border: 'none', borderRadius: 7, fontSize: 12, fontWeight: 600, cursor: 'pointer',
            }}>Gotowe</button>
          </div>
        </div>
      )}
    </div>
  );
}

function FontSelect({ label, value, onChange, sample }) {
  const [open, setOpen] = React.useState(false);
  const cats = ['Sans', 'Serif', 'Mono'];
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (!open) return;
    const h = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    setTimeout(() => document.addEventListener('mousedown', h), 0);
    return () => document.removeEventListener('mousedown', h);
  }, [open]);
  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <div style={{ fontSize: 10.5, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>{label}</div>
      <button onClick={() => setOpen(!open)} style={{
        width: '100%', padding: '10px 12px', background: '#F8FAFC',
        border: '1px solid #E2E8F0', borderRadius: 8, cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 12, textAlign: 'left',
      }}>
        <span style={{ fontFamily: `'${value}', sans-serif`, fontSize: 18, fontWeight: 600, color: '#0F172A', flexShrink: 0, minWidth: 32 }}>Aa</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 500, color: '#0F172A' }}>{value}</div>
          <div style={{ fontFamily: `'${value}', sans-serif`, fontSize: 12, color: '#64748B', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{sample}</div>
        </div>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      {open && (
        <div style={{
          position: 'absolute', top: 'calc(100% + 4px)', left: 0, right: 0,
          background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10,
          boxShadow: '0 16px 40px rgba(15,23,42,.15)', zIndex: 60, maxHeight: 320, overflow: 'auto', padding: 6,
        }}>
          {cats.map(cat => (
            <div key={cat}>
              <div style={{ fontSize: 9.5, fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.8, padding: '8px 8px 4px' }}>{cat}</div>
              {FONT_OPTIONS.filter(f => f.cat === cat).map(f => (
                <button key={f.id} onClick={() => { onChange(f.id); setOpen(false); }}
                  style={{
                    width: '100%', padding: '8px 10px', background: value === f.id ? 'rgba(99,102,241,.08)' : 'transparent',
                    border: 'none', borderRadius: 7, cursor: 'pointer',
                    display: 'flex', alignItems: 'center', gap: 12, textAlign: 'left',
                  }}
                  onMouseEnter={e => { if (value !== f.id) e.currentTarget.style.background = '#F8FAFC'; }}
                  onMouseLeave={e => { if (value !== f.id) e.currentTarget.style.background = 'transparent'; }}>
                  <span style={{ fontFamily: `'${f.id}'`, fontSize: 20, fontWeight: 600, color: '#0F172A', minWidth: 32 }}>Aa</span>
                  <span style={{ flex: 1, fontSize: 13, color: '#0F172A', fontWeight: value === f.id ? 600 : 400 }}>{f.name}</span>
                  {value === f.id && <span style={{ color: '#6366F1', fontSize: 14 }}>✓</span>}
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ===== Floating Element Toolbar ===== */

function ElementToolbar({ selected, liveOv, viewport, onPatch, onCopy, onRemove, onAi }) {
  const { rect } = selected;
  const ov = liveOv || {};
  const [fontOpen, setFontOpen] = React.useState(false);
  const [colorOpen, setColorOpen] = React.useState(false);
  const toolbarRef = React.useRef(null);
  const [pos, setPos] = React.useState({ top: 0, left: 0 });

  // Position above the selected element. rect is in viewport coords, toolbar is position:fixed.
  React.useLayoutEffect(() => {
    if (!rect) return;
    const tbW = toolbarRef.current ? toolbarRef.current.offsetWidth : 520;
    const tbH = 44;
    let top = rect.top - tbH - 8;
    if (top < 72) top = rect.bottom + 8; // flip under if too close to topbar
    let left = rect.left + rect.width / 2 - tbW / 2;
    left = Math.max(12, Math.min(window.innerWidth - tbW - 12, left));
    setPos({ top, left });
  }, [rect]);

  const fonts = ['Inter', 'Manrope', 'Plus Jakarta Sans', 'Space Grotesk', 'Fraunces', 'Playfair Display', 'Instrument Serif', 'DM Serif Display', 'Cormorant', 'JetBrains Mono'];
  const colors = ['#0F172A', '#334155', '#64748B', '#94A3B8', '#6366F1', '#EC4899', '#B45309', '#059669', '#DC2626', '#FFFFFF'];
  const sizes = [
    { v: 0.7, l: 'XS' }, { v: 0.85, l: 'S' }, { v: 1, l: 'M' },
    { v: 1.2, l: 'L' }, { v: 1.5, l: 'XL' }, { v: 2, l: '2XL' },
  ];

  return (
    <div ref={toolbarRef}
      data-element-toolbar
      onMouseDown={e => e.stopPropagation()}
      style={{
        position: 'fixed', top: pos.top, left: pos.left, zIndex: 80,
        display: 'inline-flex', alignItems: 'center', gap: 2,
        background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10,
        padding: 4, boxShadow: '0 8px 24px rgba(15,23,42,.15), 0 2px 6px rgba(15,23,42,.06)',
        fontFamily: 'Inter, sans-serif',
        animation: 'slideUp .12s',      }}>

      {viewport !== 'desktop' && (
        <div style={{
          padding: '3px 9px', background: '#FEF3C7', color: '#92400E',
          borderRadius: 6, fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
          letterSpacing: 0.4, marginRight: 4,
        }}>
          tylko {viewport === 'mobile' ? 'mobile' : 'tablet'}
        </div>
      )}

      {/* Font */}
      <div style={{ position: 'relative' }}>
        <TbBtn onClick={() => { setFontOpen(!fontOpen); setColorOpen(false); }} title="Font">
          <span style={{ fontFamily: `'${ov.fontFamily || 'inherit'}', sans-serif`, fontWeight: 600 }}>
            {(ov.fontFamily || 'Font').length > 14 ? (ov.fontFamily || 'Font').slice(0, 12) + '…' : (ov.fontFamily || 'Font')}
          </span>
          <Caret/>
        </TbBtn>
        {fontOpen && (
          <FlyMenu onClose={() => setFontOpen(false)}>
            <FlyHeader>Font</FlyHeader>
            <FlyItem active={!ov.fontFamily} onClick={() => { onPatch({ fontFamily: null }); setFontOpen(false); }}>
              <span style={{ color: '#64748B', fontSize: 12 }}>Domyślny (z typografii)</span>
            </FlyItem>
            <FlyDivider/>
            {fonts.map(f => (
              <FlyItem key={f} active={ov.fontFamily === f} onClick={() => { onPatch({ fontFamily: f }); setFontOpen(false); }}>
                <span style={{ fontFamily: `'${f}', sans-serif`, fontSize: 14 }}>{f}</span>
              </FlyItem>
            ))}
          </FlyMenu>
        )}
      </div>

      <TbDivider/>

      {/* Size */}
      <div style={{ display: 'inline-flex', background: '#F1F5F9', borderRadius: 6, padding: 2, gap: 1 }}>
        {sizes.map(sz => (
          <button key={sz.v} onClick={() => onPatch({ fontSize: sz.v === 1 ? null : sz.v })}
            title={`Rozmiar ${sz.l}`}
            style={{
              padding: '3px 7px', border: 'none', borderRadius: 4,
              background: (ov.fontSize || 1) === sz.v ? '#fff' : 'transparent',
              color: (ov.fontSize || 1) === sz.v ? '#0F172A' : '#64748B',
              fontSize: 10.5, fontWeight: 700, cursor: 'pointer',
              boxShadow: (ov.fontSize || 1) === sz.v ? '0 1px 2px rgba(0,0,0,.06)' : 'none',
              fontFamily: 'inherit',
            }}>{sz.l}</button>
        ))}
      </div>

      <TbDivider/>

      {/* Weight */}
      <div style={{ display: 'inline-flex', background: '#F1F5F9', borderRadius: 6, padding: 2, gap: 1 }}>
        {[400, 500, 600, 700].map(w => (
          <button key={w} onClick={() => onPatch({ fontWeight: w })}
            title={`Waga ${w}`}
            style={{
              padding: '3px 7px', border: 'none', borderRadius: 4,
              background: (ov.fontWeight || 400) === w ? '#fff' : 'transparent',
              color: (ov.fontWeight || 400) === w ? '#0F172A' : '#64748B',
              fontSize: 11, fontWeight: w, cursor: 'pointer',
              boxShadow: (ov.fontWeight || 400) === w ? '0 1px 2px rgba(0,0,0,.06)' : 'none',
              fontFamily: 'inherit',
            }}>{ w === 400 ? 'R' : w === 500 ? 'Md' : w === 600 ? 'Sb' : 'B' }</button>
        ))}
      </div>

      <TbDivider/>

      {/* Italic / Underline */}
      <TbToggle active={!!ov.italic} onClick={() => onPatch({ italic: !ov.italic })} title="Kursywa">
        <span style={{ fontStyle: 'italic', fontFamily: 'Georgia, serif', fontWeight: 600 }}>I</span>
      </TbToggle>
      <TbToggle active={!!ov.underline} onClick={() => onPatch({ underline: !ov.underline })} title="Podkreślenie">
        <span style={{ textDecoration: 'underline', fontWeight: 600 }}>U</span>
      </TbToggle>

      <TbDivider/>

      {/* Color */}
      <div style={{ position: 'relative' }}>
        <TbBtn onClick={() => { setColorOpen(!colorOpen); setFontOpen(false); }} title="Kolor">
          <span style={{ width: 14, height: 14, borderRadius: 4, background: ov.color || '#0F172A', border: '1px solid rgba(0,0,0,.1)', display: 'inline-block' }}/>
          <span style={{ fontSize: 11, fontWeight: 600 }}>A</span>
          <Caret/>
        </TbBtn>
        {colorOpen && (
          <FlyMenu onClose={() => setColorOpen(false)} width={192}>
            <FlyHeader>Kolor tekstu</FlyHeader>
            <div style={{ padding: '4px 8px 10px', display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 6 }}>
              {colors.map(c => (
                <button key={c} onClick={() => { onPatch({ color: c }); setColorOpen(false); }}
                  title={c}
                  style={{
                    width: 28, height: 28, borderRadius: 6,
                    background: c, border: ov.color === c ? '2px solid #6366F1' : '1px solid rgba(0,0,0,.12)',
                    cursor: 'pointer', padding: 0,
                  }}/>
              ))}
            </div>
            <FlyDivider/>
            <div style={{ padding: '6px 10px 10px' }}>
              <input type="color" value={ov.color || '#0F172A'} onChange={e => onPatch({ color: e.target.value })}
                style={{ width: '100%', height: 30, border: 'none', background: 'none', cursor: 'pointer' }}/>
            </div>
            <FlyItem onClick={() => { onPatch({ color: null }); setColorOpen(false); }}>
              <span style={{ color: '#64748B', fontSize: 12 }}>↺ Domyślny kolor</span>
            </FlyItem>
          </FlyMenu>
        )}
      </div>

      <TbDivider/>

      {/* Align */}
      <TbToggle active={ov.align === 'left'} onClick={() => onPatch({ align: ov.align === 'left' ? null : 'left' })} title="Lewo">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="19" y2="18"/></svg>
      </TbToggle>
      <TbToggle active={ov.align === 'center'} onClick={() => onPatch({ align: ov.align === 'center' ? null : 'center' })} title="Środek">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
      </TbToggle>
      <TbToggle active={ov.align === 'right'} onClick={() => onPatch({ align: ov.align === 'right' ? null : 'right' })} title="Prawo">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="5" y1="18" x2="21" y2="18"/></svg>
      </TbToggle>

      <TbDivider/>

      <TbBtn onClick={onAi} title="AI — przepisz ten tekst">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
        <span style={{ color: '#6366F1', fontWeight: 600 }}>AI</span>
      </TbBtn>
      <TbBtn onClick={onCopy} title="Kopiuj">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      </TbBtn>
      <TbBtn onClick={onRemove} title="Usuń element" danger>
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
      </TbBtn>
    </div>
  );
}

function TbBtn({ children, onClick, title, danger }) {
  return <button onMouseDown={e => e.preventDefault()} onClick={onClick} title={title}
    style={{
      padding: '6px 9px', background: 'transparent', border: 'none', borderRadius: 6,
      cursor: 'pointer', fontSize: 11.5, color: danger ? '#DC2626' : '#334155',
      display: 'inline-flex', alignItems: 'center', gap: 5, fontFamily: 'inherit',
    }}
    onMouseEnter={e => e.currentTarget.style.background = danger ? '#FEF2F2' : '#F1F5F9'}
    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>{children}</button>;
}

function TbToggle({ active, onClick, title, children }) {
  return <button onMouseDown={e => e.preventDefault()} onClick={onClick} title={title}
    style={{
      padding: '5px 7px', background: active ? '#0F172A' : 'transparent',
      border: 'none', borderRadius: 6, cursor: 'pointer',
      color: active ? '#fff' : '#334155', fontSize: 12,
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center', minWidth: 24, minHeight: 24,
      fontFamily: 'inherit',
    }}
    onMouseEnter={e => { if (!active) e.currentTarget.style.background = '#F1F5F9'; }}
    onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent'; }}>{children}</button>;
}

function TbDivider() { return <div style={{ width: 1, height: 20, background: '#E2E8F0', margin: '0 2px' }}/>; }
function Caret() { return <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M6 9l6 6 6-6"/></svg>; }

function FlyMenu({ children, onClose, width = 220 }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    const h = (e) => { if (ref.current && !ref.current.contains(e.target)) onClose(); };
    setTimeout(() => document.addEventListener('mousedown', h), 0);
    return () => document.removeEventListener('mousedown', h);
  }, []);
  return (
    <div ref={ref} style={{
      position: 'absolute', top: 'calc(100% + 6px)', left: 0,
      width, background: '#fff', border: '1px solid #E2E8F0', borderRadius: 10,
      boxShadow: '0 12px 30px rgba(15,23,42,.15)', zIndex: 90, padding: 4,
      maxHeight: 340, overflow: 'auto', animation: 'slideUp .12s',
    }}>{children}</div>
  );
}
function FlyHeader({ children }) {
  return <div style={{ fontSize: 10, fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.6, padding: '6px 10px 4px' }}>{children}</div>;
}
function FlyItem({ children, onClick, active }) {
  return <button onMouseDown={e => e.preventDefault()} onClick={onClick}
    style={{
      width: '100%', padding: '7px 10px', background: active ? 'rgba(99,102,241,.08)' : 'transparent',
      border: 'none', borderRadius: 6, cursor: 'pointer', textAlign: 'left',
      color: '#0F172A', fontFamily: 'inherit',
    }}
    onMouseEnter={e => { if (!active) e.currentTarget.style.background = '#F8FAFC'; }}
    onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent'; }}>{children}</button>;
}
function FlyDivider() { return <div style={{ height: 1, background: '#E2E8F0', margin: '4px 0' }}/>; }

/* ===== AI Chat (persistent side panel) ===== */

function AiChat({ messages, selected, onSend, onClose }) {
  const [input, setInput] = React.useState('');
  const scrollRef = React.useRef(null);
  const inputRef = React.useRef(null);

  React.useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  React.useEffect(() => { setTimeout(() => inputRef.current && inputRef.current.focus(), 60); }, []);

  const send = () => {
    if (!input.trim()) return;
    onSend(input.trim());
    setInput('');
  };

  const suggestions = selected
    ? ['Skróć ten tekst o połowę', 'Napisz ciepło i swojsko', 'Dodaj konkretny szczegół', 'Mocniejszy CTA']
    : ['Zmień ton na bardziej swojski', 'Dopisz sekcję o tarasie', 'Wszystkie CTA bardziej konkretne', 'Skróć wszystkie paragrafy'];

  return (
    <div style={{
      position: 'fixed', right: 24, bottom: 24, width: 400, height: 560, zIndex: 95,
      background: '#fff', borderRadius: 16,
      boxShadow: '0 24px 60px rgba(15,23,42,.22), 0 2px 8px rgba(15,23,42,.08)',
      border: '1px solid #E2E8F0',
      display: 'flex', flexDirection: 'column', overflow: 'hidden',
      animation: 'slideUp .18s',
      fontFamily: 'Inter, sans-serif',
    }}>
      {/* Header */}
      <div style={{
        padding: '14px 16px', borderBottom: '1px solid #E2E8F0',
        display: 'flex', alignItems: 'center', gap: 10,
        background: 'linear-gradient(135deg, rgba(99,102,241,.04), rgba(236,72,153,.04))',
      }}>
        <div style={{
          width: 32, height: 32, borderRadius: 9,
          background: 'linear-gradient(135deg, #6366F1, #EC4899)',
          display: 'grid', placeItems: 'center', color: '#fff',
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
        </div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#0F172A' }}>AI asystent</div>
          <div style={{ fontSize: 11, color: '#64748B' }}>
            {selected ? `Edytujesz: ${selected.elId.replace(/-/g, ' ')}` : 'Cała strona w kontekście'}
          </div>
        </div>
        <button onClick={onClose} style={{
          marginLeft: 'auto', width: 28, height: 28, background: 'transparent',
          border: 'none', borderRadius: 7, cursor: 'pointer', color: '#64748B',
          display: 'grid', placeItems: 'center', fontSize: 18,
        }}
          onMouseEnter={e => e.currentTarget.style.background = '#F1F5F9'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>×</button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} style={{ flex: 1, overflow: 'auto', padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            maxWidth: '85%',
            alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
            padding: '9px 12px',
            background: m.role === 'user' ? 'linear-gradient(135deg, #6366F1, #EC4899)' : '#F1F5F9',
            color: m.role === 'user' ? '#fff' : '#0F172A',
            borderRadius: m.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
            fontSize: 13, lineHeight: 1.45,
          }}>{m.text}</div>
        ))}
      </div>

      {/* Suggestions */}
      <div style={{ padding: '8px 12px 0', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {suggestions.map(s => (
          <button key={s} onClick={() => onSend(s)}
            style={{
              padding: '5px 10px', background: '#fff', border: '1px solid #E2E8F0',
              borderRadius: 999, fontSize: 11.5, color: '#475569',
              cursor: 'pointer', fontFamily: 'inherit', whiteSpace: 'nowrap',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366F1'; e.currentTarget.style.color = '#6366F1'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.color = '#475569'; }}>{s}</button>
        ))}
      </div>

      {/* Input */}
      <div style={{ padding: 12, borderTop: '1px solid #E2E8F0', marginTop: 10 }}>
        <div style={{
          display: 'flex', alignItems: 'flex-end', gap: 8,
          padding: '8px 10px', background: '#F8FAFC',
          border: '1px solid #E2E8F0', borderRadius: 12,
        }}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder={selected ? 'Jak zmienić zaznaczony tekst?' : 'Co chcesz poprawić na stronie?'}
            rows={1}
            style={{
              flex: 1, border: 'none', background: 'transparent', outline: 'none',
              resize: 'none', fontSize: 13, fontFamily: 'inherit', color: '#0F172A',
              minHeight: 20, maxHeight: 100, lineHeight: 1.5, padding: 2,
            }}/>
          <button onClick={send} disabled={!input.trim()}
            style={{
              width: 32, height: 32, background: input.trim() ? 'linear-gradient(135deg, #6366F1, #EC4899)' : '#E2E8F0',
              color: input.trim() ? '#fff' : '#94A3B8', border: 'none', borderRadius: 8,
              cursor: input.trim() ? 'pointer' : 'not-allowed',
              display: 'grid', placeItems: 'center', flexShrink: 0,
            }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </button>
        </div>
      </div>
    </div>
  );
}

/* ===== Section Hover Actions ===== */

function SectionHoverActions({ scale = 1, label, canUp, canDown, onDup, onDel, onUp, onDown, onVariant }) {
  // The canvas is transform-scaled; we counter-scale this overlay so icons stay readable
  const inv = scale ? 1 / scale : 1;
  return (
    <div style={{
      position: 'absolute', top: 8, right: 8, zIndex: 20,
      pointerEvents: 'none',
      transform: `scale(${inv})`, transformOrigin: 'top right',
    }}>
      <div style={{ pointerEvents: 'auto', display: 'inline-flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6 }}>
        <div style={{
          padding: '3px 9px', background: '#0F172A', color: '#fff',
          borderRadius: 6, fontSize: 10.5, fontWeight: 600, fontFamily: 'Inter, sans-serif',
          letterSpacing: 0.2,
        }}>{label}</div>
        <div style={{
          display: 'inline-flex', gap: 1, padding: 3, background: '#fff',
          border: '1px solid rgba(15,23,42,.1)', borderRadius: 8,
          boxShadow: '0 4px 14px rgba(15,23,42,.12)',
          fontFamily: 'Inter, sans-serif',
        }}>
          <SecAct title="Przesuń w górę" disabled={!canUp} onClick={onUp}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M18 15l-6-6-6 6"/></svg>
          </SecAct>
          <SecAct title="Przesuń w dół" disabled={!canDown} onClick={onDown}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M6 9l6 6 6-6"/></svg>
          </SecAct>
          <div style={{ width: 1, background: '#E2E8F0', margin: '2px 2px' }}/>
          <SecAct title="Zmień wariant" onClick={onVariant}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          </SecAct>
          <SecAct title="Duplikuj" onClick={onDup}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </SecAct>
          <SecAct title="Usuń sekcję" danger onClick={onDel}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
          </SecAct>
        </div>
      </div>
    </div>
  );
}

function SecAct({ children, onClick, title, disabled, danger }) {
  return (
    <button disabled={disabled} onClick={onClick} title={title}
      style={{
        width: 30, height: 28, border: 'none', borderRadius: 6,
        background: 'transparent',
        color: disabled ? '#CBD5E1' : (danger ? '#DC2626' : '#334155'),
        cursor: disabled ? 'not-allowed' : 'pointer',
        display: 'grid', placeItems: 'center', fontFamily: 'inherit',
      }}
      onMouseEnter={e => { if (!disabled) e.currentTarget.style.background = danger ? '#FEF2F2' : '#F1F5F9'; }}
      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
      {children}
    </button>
  );
}

/* ===== Ghost Undo banner ===== */

function GhostUndo({ label, onUndo, onDismiss }) {
  const [timeLeft, setTimeLeft] = React.useState(10);
  React.useEffect(() => {
    const t = setInterval(() => setTimeLeft(prev => {
      if (prev <= 1) { clearInterval(t); onDismiss(); return 0; }
      return prev - 1;
    }), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <div style={{
      position: 'fixed', bottom: 90, left: '50%', transform: 'translateX(-50%)',
      zIndex: 98, display: 'inline-flex', alignItems: 'center', gap: 12,
      padding: '10px 14px 10px 16px', background: '#0F172A', color: '#fff',
      borderRadius: 10, boxShadow: '0 12px 30px rgba(15,23,42,.3)',
      fontFamily: 'Inter, sans-serif', fontSize: 13,
      animation: 'slideUp .2s',
    }}>
      <span>AI przepisał: <b style={{ opacity: 0.85 }}>„{label.length > 32 ? label.slice(0, 30) + '…' : label}"</b></span>
      <button onClick={onUndo} style={{
        padding: '5px 12px', background: 'rgba(255,255,255,.14)', color: '#fff',
        border: 'none', borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer',
        fontFamily: 'inherit',
      }}>↶ Cofnij ({timeLeft}s)</button>
      <button onClick={onDismiss} style={{
        padding: 0, width: 22, height: 22, background: 'transparent', color: 'rgba(255,255,255,.6)',
        border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 16, lineHeight: 1,
      }}>×</button>
    </div>
  );
}

/* ===== AI Diff modal ===== */

function AiDiffModal({ diff, onAccept, onReject }) {
  return (
    <div onMouseDown={onReject} style={{
      position: 'fixed', inset: 0, background: 'rgba(15,23,42,.42)', zIndex: 110,
      display: 'grid', placeItems: 'center', padding: 20, fontFamily: 'Inter, sans-serif',
    }}>
      <div onMouseDown={e => e.stopPropagation()} style={{
        width: 'min(780px, 100%)', maxHeight: '85vh', background: '#fff', borderRadius: 16,
        boxShadow: '0 30px 60px rgba(15,23,42,.3)', display: 'flex', flexDirection: 'column',
        overflow: 'hidden',
      }}>
        <div style={{
          padding: '18px 22px', borderBottom: '1px solid #E2E8F0',
          background: 'linear-gradient(135deg, rgba(99,102,241,.05), rgba(236,72,153,.05))',
          display: 'flex', alignItems: 'center', gap: 12,
        }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg, #6366F1, #EC4899)', color: '#fff', display: 'grid', placeItems: 'center' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></svg>
          </div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#0F172A' }}>AI propozycja zmian</div>
            <div style={{ fontSize: 12, color: '#64748B', marginTop: 2 }}>
              Prośba: „{diff.prompt}" · {diff.changes.length} {diff.changes.length === 1 ? 'zmiana' : 'zmiany'}
            </div>
          </div>
          <button onClick={onReject} style={{
            marginLeft: 'auto', width: 32, height: 32, background: 'transparent',
            border: 'none', borderRadius: 8, cursor: 'pointer', color: '#64748B',
            fontSize: 20, display: 'grid', placeItems: 'center',
          }}>×</button>
        </div>

        <div style={{ flex: 1, overflow: 'auto', padding: 22, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {diff.changes.map((c, i) => (
            <div key={i} style={{ border: '1px solid #E2E8F0', borderRadius: 12, overflow: 'hidden' }}>
              <div style={{
                padding: '8px 14px', background: '#F8FAFC', borderBottom: '1px solid #E2E8F0',
                fontSize: 11, fontWeight: 600, color: '#64748B', textTransform: 'uppercase', letterSpacing: 0.5,
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                <span style={{ color: '#6366F1' }}>●</span> {c.label}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0 }}>
                <div style={{ padding: 14, background: '#FEF2F2', borderRight: '1px solid #E2E8F0' }}>
                  <div style={{ fontSize: 10, fontWeight: 600, color: '#991B1B', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>− Obecnie</div>
                  <div style={{ fontSize: 13.5, color: '#334155', lineHeight: 1.5 }}>{c.before}</div>
                </div>
                <div style={{ padding: 14, background: '#F0FDF4' }}>
                  <div style={{ fontSize: 10, fontWeight: 600, color: '#166534', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>+ AI proponuje</div>
                  <div style={{ fontSize: 13.5, color: '#0F172A', lineHeight: 1.5, fontWeight: 500 }}>{c.after}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div style={{
          padding: '14px 22px', borderTop: '1px solid #E2E8F0',
          display: 'flex', alignItems: 'center', gap: 10, background: '#FAFBFC',
        }}>
          <div style={{ fontSize: 12, color: '#94A3B8' }}>Po akceptacji będziesz mógł cofnąć przez 10 sekund.</div>
          <div style={{ flex: 1 }}/>
          <button onClick={onReject} style={{
            padding: '9px 16px', background: '#fff', border: '1px solid #E2E8F0',
            borderRadius: 8, fontSize: 13, fontWeight: 500, color: '#475569', cursor: 'pointer', fontFamily: 'inherit',
          }}>Odrzuć</button>
          <button onClick={onAccept} style={{
            padding: '9px 18px', background: 'linear-gradient(135deg, #6366F1, #EC4899)',
            color: '#fff', border: 'none', borderRadius: 8, fontSize: 13, fontWeight: 600,
            cursor: 'pointer', fontFamily: 'inherit',
          }}>✓ Zastosuj wszystkie</button>
        </div>
      </div>
    </div>
  );
}

/* ===== Mock AI diff generator ===== */

function buildMockAiDiff({ scope, selected, content, prompt }) {
  const p = prompt.toLowerCase();
  if (scope === 'element' && selected) {
    const mockBefore = 'Kawa palona u lokalnego wypalarza, ciasta pieczone codziennie rano. Przyjdź — pies też.';
    let after = mockBefore;
    if (p.includes('skr')) after = 'Lokalna kawa, codzienne ciasta. Pies mile widziany.';
    else if (p.includes('swojsk') || p.includes('ciepl')) after = 'Kawa od sąsiada z wypalarni, ciasta prosto z pieca. Wpadnij z psem na pogaduchy.';
    else if (p.includes('cta') || p.includes('mocn')) after = 'Kawa palona lokalnie, ciasta pieczone codziennie. Zarezerwuj stolik →';
    else after = 'Lokalna kawa, świeże ciasta, pies mile widziany — wszystko w sercu Ruskiej.';
    return [{
      sectionId: selected.sectionId, elId: selected.elId,
      label: `${selected.elId.replace(/-/g, ' ')} · ${selected.sectionId}`,
      before: mockBefore, after,
    }];
  }
  // Global — zrób 3 zmiany
  return [
    { sectionId: 'hero', elId: 'title', label: 'Hero · tytuł',
      before: 'Mała kawiarnia z wielkim sercem na Ruskiej',
      after: 'Twoja przystań przy Ruskiej 12' },
    { sectionId: 'hero', elId: 'body', label: 'Hero · opis',
      before: 'Kawa od lokalnego palarza, ciasta codziennie rano z naszego pieca, pies mile widziany.',
      after: 'Kawa palona 200m stąd, ciasta z pieca zanim otworzymy. Pies pije wodę ze swojej miski.' },
    { sectionId: 'cta', elId: 'button', label: 'CTA · przycisk',
      before: 'Dowiedz się więcej',
      after: 'Zarezerwuj stolik' },
  ];
}

