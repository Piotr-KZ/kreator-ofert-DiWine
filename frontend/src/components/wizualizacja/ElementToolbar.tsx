import React from "react";
// Wiz — uniwersalny toolbar kontekstowy dla elementów
// Typy: text | input | button | section | image | formField

const FONT_FAMILIES = [
  { label: 'Fraunces', val: "'Fraunces', serif", type: 'h' },
  { label: 'Playfair Display', val: "'Playfair Display', serif", type: 'h' },
  { label: 'Instrument Serif', val: "'Instrument Serif', serif", type: 'h' },
  { label: 'DM Serif Display', val: "'DM Serif Display', serif", type: 'h' },
  { label: 'Cormorant Garamond', val: "'Cormorant Garamond', serif", type: 'h' },
  { label: 'Inter', val: "'Inter', sans-serif", type: 'b' },
  { label: 'Manrope', val: "'Manrope', sans-serif", type: 'b' },
  { label: 'Space Grotesk', val: "'Space Grotesk', sans-serif", type: 'b' },
  { label: 'IBM Plex Sans', val: "'IBM Plex Sans', sans-serif", type: 'b' },
  { label: 'JetBrains Mono', val: "'JetBrains Mono', monospace", type: 'm' },
];

const BRAND_COLORS = [
  { name: 'Atrament', val: '#1F2937' },
  { name: 'Grafit', val: '#475569' },
  { name: 'Mięta', val: '#6FAE8C' },
  { name: 'Mięta jasna', val: '#A8D5BA' },
  { name: 'Terakota', val: '#C2410C' },
  { name: 'Kremowy', val: '#FAF6EF' },
  { name: 'Biały', val: '#FFFFFF' },
  { name: 'Przezroczysty', val: 'transparent' },
];

// Ikony jednoliniowe (24x24)
const Icon = ({ name, size = 14 }) => {
  const paths = {
    bold: <path d="M7 5h6a3.5 3.5 0 010 7H7zm0 7h7a3.5 3.5 0 010 7H7z" strokeLinejoin="round"/>,
    italic: <><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></>,
    underline: <><path d="M6 4v7a6 6 0 0012 0V4"/><line x1="4" y1="20" x2="20" y2="20"/></>,
    alignLeft: <><line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/></>,
    alignCenter: <><line x1="18" y1="10" x2="6" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="18" y1="18" x2="6" y2="18"/></>,
    alignRight: <><line x1="21" y1="10" x2="7" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="21" y1="18" x2="7" y2="18"/></>,
    move: <><polyline points="5 9 2 12 5 15"/><polyline points="9 5 12 2 15 5"/><polyline points="15 19 12 22 9 19"/><polyline points="19 9 22 12 19 15"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/></>,
    copy: <><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></>,
    trash: <><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></>,
    close: <><path d="M18 6 6 18M6 6l12 12"/></>,
    image: <><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></>,
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">{paths[name]}</svg>
  );
};
export { Icon as WizIcon };

function detectElementType(el) {
  if (!el) return null;
  const tag = el.tagName;
  // Komponenty z markerem
  if (el.dataset?.component === 'form') return 'form';
  if (el.dataset?.component === 'testimonial') return 'testimonial';
  if (el.dataset?.formField === 'true') return 'formField';
  // Infografika — element wewnątrz infografiki (circle/bar/line/item)
  if (el.dataset?.infographicCircle === 'true') return 'infographicShape';
  if (el.dataset?.infographicBar === 'true') return 'infographicShape';
  if (el.dataset?.infographicLine === 'true') return 'infographicLine';
  if (el.dataset?.editableInfographic) return 'infographicContainer';
  if (el.dataset?.infographicItem === 'true') return 'infographicItem';
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) return 'input';
  if (tag === 'BUTTON' || el.getAttribute('role') === 'button' || el.dataset.cta === 'true') return 'button';
  if (tag === 'IMG' || el.dataset.editableImg === 'true') return 'image';
  if (tag === 'FORM') return 'form';
  if (['SECTION', 'NAV', 'FOOTER', 'HEADER', 'ARTICLE', 'ASIDE'].includes(tag)) return 'section';
  // Form field: label lub div owijający input/textarea
  if (el.querySelector?.('input, textarea, select')) {
    if (['LABEL', 'DIV'].includes(tag) && el.children.length <= 4) return 'formField';
  }
  return 'text';
}

// Klik w span wewnątrz button/a/img powinien wykryć rodzica
function resolveClickTarget(el) {
  if (!el) return el;
  // 1) Jawny CTA (span z data-cta) albo role=button albo button element
  const cta = el.closest?.('[data-cta="true"], button, [role="button"]');
  if (cta) return cta;
  // 2) Link stylowany jako przycisk (np. class zawiera btn/button/cta)
  const linkBtn = el.closest?.('a.btn, a[class*="button"], a[class*="Btn"]');
  if (linkBtn) return linkBtn;
  // 3) Obraz w wrapperze z data-editable-img
  const imgW = el.closest?.('[data-editable-img="true"]');
  if (imgW && el.tagName !== 'IMG') return imgW.querySelector('img') || imgW;
  return el;
}
export { resolveClickTarget };
export { detectElementType };

// Zaznacza cały tekst w elemencie (żeby execCommand działał)
function selectAllIn(el) {
  const range = document.createRange();
  range.selectNodeContents(el);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
}

// Aplikuje styl do SELEKCJI tekstu (window.getSelection) przez opakowanie <span>
// Jeśli nic nie zaznaczone — aplikuje do el.
function applyToSelectionOrEl(el, prop, val) {
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0 || sel.isCollapsed) {
    // Brak selekcji → cały element
    el.style[prop] = val;
    return false;
  }
  const range = sel.getRangeAt(0);
  // Sprawdź czy selekcja jest wewnątrz el
  if (!el.contains(range.commonAncestorContainer)) {
    el.style[prop] = val;
    return false;
  }
  try {
    const span = document.createElement('span');
    span.dataset.editableFragment = 'true';
    span.style[prop] = val;
    range.surroundContents(span);
    sel.removeAllRanges();
    return true;
  } catch (e) {
    // Selekcja przekracza granice — użyj extractContents
    try {
      const frag = range.extractContents();
      const span = document.createElement('span');
      span.dataset.editableFragment = 'true';
      span.style[prop] = val;
      span.appendChild(frag);
      range.insertNode(span);
      sel.removeAllRanges();
      return true;
    } catch (e2) {
      el.style[prop] = val;
      return false;
    }
  }
}

// Toggle format — zachowuje selekcję jeśli jest
function toggleTextFormat(el, prop) {
  const sel = window.getSelection();
  const hasSelection = sel && sel.rangeCount > 0 && !sel.isCollapsed && el.contains(sel.getRangeAt(0).commonAncestorContainer);

  if (hasSelection) {
    if (prop === 'bold') applyToSelectionOrEl(el, 'fontWeight', '700');
    else if (prop === 'italic') applyToSelectionOrEl(el, 'fontStyle', 'italic');
    else if (prop === 'underline') applyToSelectionOrEl(el, 'textDecoration', 'underline');
    return;
  }
  const cs = window.getComputedStyle(el);
  if (prop === 'bold') {
    const w = parseInt(cs.fontWeight) || 400;
    el.style.fontWeight = w >= 600 ? '400' : '700';
  } else if (prop === 'italic') {
    el.style.fontStyle = cs.fontStyle === 'italic' ? 'normal' : 'italic';
  } else if (prop === 'underline') {
    const curr = cs.textDecorationLine || '';
    el.style.textDecoration = curr.includes('underline') ? 'none' : 'underline';
  }
}

export { applyToSelectionOrEl };

// Reorder sekcji w górę/dół (zmiana kolejności w DOM)
function moveSection(el, dir) {
  const parent = el.parentElement;
  if (!parent) return;
  if (dir === 'up') {
    const prev = el.previousElementSibling;
    if (prev) parent.insertBefore(el, prev);
  } else {
    const next = el.nextElementSibling;
    if (next) parent.insertBefore(next, el);
  }
}
export { moveSection };

// Custom Slider — pointer-based, duży widoczny track, responsywny gdziekolwiek klikniesz/chwycisz.
// Propsy: value (number), min, max, step, onChange(val), accent (kolor).
function SliderV2({ value, min = 0, max = 100, step = 1, onChange, accent = '#0F172A', width = 'auto' }) {
  const trackRef = React.useRef(null);
  const [dragging, setDragging] = React.useState(false);

  const toValue = (clientX) => {
    const rect = trackRef.current.getBoundingClientRect();
    let pct = (clientX - rect.left) / rect.width;
    pct = Math.max(0, Math.min(1, pct));
    const raw = min + pct * (max - min);
    const snapped = Math.round(raw / step) * step;
    return Math.max(min, Math.min(max, snapped));
  };

  const onPointerDown = (e) => {
    e.preventDefault();
    e.stopPropagation();
    trackRef.current.setPointerCapture?.(e.pointerId);
    setDragging(true);
    onChange(toValue(e.clientX));
  };
  const onPointerMove = (e) => {
    if (!dragging) return;
    e.preventDefault();
    onChange(toValue(e.clientX));
  };
  const onPointerUp = (e) => {
    if (!dragging) return;
    setDragging(false);
    trackRef.current.releasePointerCapture?.(e.pointerId);
  };

  const pct = max > min ? ((value - min) / (max - min)) * 100 : 0;

  return (
    <div ref={trackRef}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
      onMouseDown={e => e.stopPropagation()}
      onClick={e => e.stopPropagation()}
      style={{
        position: 'relative', flex: 1, width, minWidth: 0,
        height: 28, display: 'flex', alignItems: 'center',
        cursor: 'pointer', touchAction: 'none',
        padding: '0 9px',
        boxSizing: 'border-box',
      }}>
      <div style={{
        width: '100%', height: 6, background: '#E2E8F0',
        borderRadius: 999, position: 'relative', pointerEvents: 'none',
      }}>
        <div style={{
          position: 'absolute', left: 0, top: 0, bottom: 0,
          width: pct + '%', background: accent, borderRadius: 999,
        }}/>
        <div style={{
          position: 'absolute', left: `calc(${pct}% - 9px)`, top: -6,
          width: 18, height: 18, borderRadius: 9,
          background: '#fff', border: `2px solid ${accent}`,
          boxShadow: dragging ? '0 0 0 6px ' + accent + '22' : '0 1px 3px rgba(15,23,42,.2)',
          transition: 'box-shadow .15s',
        }}/>
      </div>
    </div>
  );
}
export { SliderV2 as WizSlider };

// Editable NumberInput — top-level żeby nie tracił focus przy re-render UniToolbar
// Trzyma lokalny string state; commit na blur/Enter. ∆ step przez +/−.
function NumberInputV2({ value, onChange, min = 0, max = 999, step = 1, unit = 'px', width = 72 }) {
  const [local, setLocal] = React.useState(String(value));
  const [editing, setEditing] = React.useState(false);
  React.useEffect(() => { if (!editing) setLocal(String(value)); }, [value, editing]);
  const commit = () => {
    setEditing(false);
    const n = parseInt(local, 10);
    if (isNaN(n)) { setLocal(String(value)); return; }
    const clamped = Math.max(min, Math.min(max, n));
    setLocal(String(clamped));
    if (clamped !== value) onChange(clamped);
  };
  const bump = (delta) => {
    const next = Math.max(min, Math.min(max, value + delta));
    setLocal(String(next));
    if (next !== value) onChange(next);
  };
  return (
    <div style={{ display: 'inline-flex', alignItems: 'stretch', border: '1px solid #CBD5E1', borderRadius: 7, overflow: 'hidden', background: '#fff', width }}>
      <button type="button" onMouseDown={e => e.preventDefault()} onClick={() => bump(-step)}
        style={{ width: 26, border: 'none', background: '#F8FAFC', cursor: 'pointer', color: '#475569', fontSize: 14, fontWeight: 600, fontFamily: 'inherit', borderRight: '1px solid #E2E8F0' }}>−</button>
      <input type="text" inputMode="numeric" value={local}
        onFocus={e => { setEditing(true); e.target.select(); }}
        onChange={e => setLocal(e.target.value.replace(/[^\d-]/g, ''))}
        onBlur={commit}
        onKeyDown={e => {
          if (e.key === 'Enter') { e.preventDefault(); e.target.blur(); }
          else if (e.key === 'Escape') { setLocal(String(value)); setEditing(false); e.target.blur(); }
          else if (e.key === 'ArrowUp') { e.preventDefault(); bump(step); }
          else if (e.key === 'ArrowDown') { e.preventDefault(); bump(-step); }
        }}
        onClick={e => e.stopPropagation()}
        onMouseDown={e => e.stopPropagation()}
        style={{
          flex: 1, border: 'none', outline: 'none', textAlign: 'center',
          fontSize: 12.5, fontWeight: 600, color: '#0F172A',
          fontFamily: 'inherit', fontVariantNumeric: 'tabular-nums',
          padding: '0 4px', background: '#fff', minWidth: 0,
        }}/>
      <div style={{ padding: '0 6px', fontSize: 10.5, color: '#94A3B8', display: 'flex', alignItems: 'center', background: '#F8FAFC', borderLeft: '1px solid #E2E8F0' }}>{unit}</div>
      <button type="button" onMouseDown={e => e.preventDefault()} onClick={() => bump(step)}
        style={{ width: 26, border: 'none', background: '#F8FAFC', cursor: 'pointer', color: '#475569', fontSize: 14, fontWeight: 600, fontFamily: 'inherit', borderLeft: '1px solid #E2E8F0' }}>+</button>
    </div>
  );
}
export { NumberInputV2 as WizNumberInput };

// SubPanel — TOP-LEVEL, żeby React NIE remontował dzieci (suwaki, inputy) przy re-renderze rodzica.
// Position: fixed, omija edytowany element.
function SubPanelImpl({ children, width = 320, title, el, pos, onClose, onReset, snapshotEls }) {
  // Snapshot el.style.cssText + dataset na mount (dla Anuluj)
  // snapshotEls — dodatkowe elementy (np. [data-bg-layer]) do snapshotu
  const snapRef = React.useRef(null);
  if (snapRef.current === null) {
    const snap = (node) => ({
      style: node.getAttribute('style') || '',
      dataset: Object.assign({}, node.dataset),
    });
    snapRef.current = {
      main: snap(el),
      extras: (snapshotEls || []).map(n => n && { node: n, data: snap(n) }).filter(Boolean),
    };
  }
  const restore = () => {
    try {
      const { main, extras } = snapRef.current || {};
      if (main) {
        if (main.style) el.setAttribute('style', main.style);
        else el.removeAttribute('style');
        // Zresetuj dataset — usuń nowe klucze, przywróć oryginalne
        Object.keys(el.dataset).forEach(k => { if (!(k in main.dataset)) delete el.dataset[k]; });
        Object.entries(main.dataset).forEach(([k, v]) => { el.dataset[k] = v; });
      }
      extras?.forEach(({ node, data }) => {
        if (!node) return;
        if (data.style) node.setAttribute('style', data.style);
        else node.removeAttribute('style');
        Object.keys(node.dataset).forEach(k => { if (!(k in data.dataset)) delete node.dataset[k]; });
        Object.entries(data.dataset).forEach(([k, v]) => { node.dataset[k] = v; });
      });
    } catch (e) { console.warn('restore failed', e); }
  };
  const onCancel = () => { restore(); onClose?.(); };
  const rect = el.getBoundingClientRect();
  const margin = 12;
  const panelH = 380;
  let panelLeft = pos.left;
  let panelTop = pos.top + 44;
  const panelBottom = panelTop + Math.min(panelH, 360);
  const overlapsEl = panelBottom > rect.top && panelTop < rect.bottom
                    && panelLeft + width > rect.left && panelLeft < rect.right;
  if (overlapsEl) {
    if (rect.right + margin + width < window.innerWidth - margin) {
      panelLeft = rect.right + margin;
      panelTop = Math.max(pos.top, rect.top);
    } else if (rect.left - margin - width > margin) {
      panelLeft = rect.left - margin - width;
      panelTop = Math.max(pos.top, rect.top);
    } else if (rect.top > 240) {
      panelTop = rect.top - panelH - margin;
      if (panelTop < 64) panelTop = 64;
    }
  }
  if (panelLeft + width > window.innerWidth - margin) panelLeft = window.innerWidth - width - margin;
  if (panelLeft < margin) panelLeft = margin;
  if (panelTop < 64) panelTop = 64;
  if (panelTop + 300 > window.innerHeight - margin) panelTop = Math.max(64, window.innerHeight - 320);

  return (
    <div
      onClick={e => e.stopPropagation()}
      onMouseDown={e => e.stopPropagation()}
      style={{
        position: 'fixed', left: panelLeft, top: panelTop, zIndex: 9999,
        background: '#fff', borderRadius: 10,
        boxShadow: '0 20px 50px rgba(15,23,42,.3), 0 0 0 1px rgba(15,23,42,.1)',
        width: width,
        maxHeight: Math.min(560, window.innerHeight - 120), display: 'flex', flexDirection: 'column',
      }}>
      {title && (
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '10px 12px 8px', borderBottom: '1px solid #F1F5F9',
        }}>
          <div style={{ fontSize: 11.5, fontWeight: 700, color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.5 }}>{title}</div>
          <button onMouseDown={e => e.preventDefault()} onClick={onCancel}
            style={{
              width: 24, height: 24, border: 'none', background: '#F1F5F9',
              borderRadius: 6, cursor: 'pointer', display: 'inline-flex',
              alignItems: 'center', justifyContent: 'center', color: '#475569',
              fontFamily: 'inherit',
            }} title="Anuluj (nie zapisuj zmian)">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
      )}
      <div style={{ padding: 12, overflow: 'auto', flex: 1 }}>
        {children}
      </div>
      <div style={{
        padding: '8px 12px', borderTop: '1px solid #F1F5F9',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8,
      }}>
        {onReset ? (
          <button onMouseDown={e => e.preventDefault()} onClick={onReset}
            style={{
              padding: '6px 10px', border: '1px solid #E2E8F0', background: '#fff',
              color: '#475569', borderRadius: 6, cursor: 'pointer',
              fontSize: 11.5, fontWeight: 600, fontFamily: 'inherit',
              display: 'inline-flex', alignItems: 'center', gap: 5,
            }} title="Przywróć domyślne">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M3 12a9 9 0 109-9 9.75 9.75 0 00-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
            Domyślne
          </button>
        ) : <span/>}
        <div style={{ display: 'flex', gap: 6 }}>
          <button onMouseDown={e => e.preventDefault()} onClick={onCancel}
            style={{
              padding: '6px 12px', border: '1px solid #E2E8F0', background: '#fff',
              color: '#475569', borderRadius: 6, cursor: 'pointer',
              fontSize: 12, fontWeight: 600, fontFamily: 'inherit',
            }} title="Anuluj — przywróć stan sprzed zmian">Anuluj</button>
          <button onMouseDown={e => e.preventDefault()} onClick={onClose}
            style={{
              padding: '6px 14px', border: 'none', background: '#0F172A',
              color: '#fff', borderRadius: 6, cursor: 'pointer',
              fontSize: 12, fontWeight: 600, fontFamily: 'inherit',
            }} title="Zapisz zmiany">Zapisz</button>
        </div>
      </div>
    </div>
  );
}

// Uniwersalny floating toolbar
function UniToolbar({ target, kind, onClose, onAction }) {
  const [, force] = React.useReducer(x => x + 1, 0);
  const [expanded, setExpanded] = React.useState(null);
  const [pos, setPos] = React.useState({ left: 0, top: 0, ready: false });
  const toolbarRef = React.useRef(null);
  const el = target;

  const cs = window.getComputedStyle(el);
  const setStyle = (prop, val) => { el.style[prop] = val; force(); };
  // Smart: aplikuj do selekcji jeśli istnieje, inaczej do el
  const setStyleSmart = (prop, val) => {
    const applied = window.applyToSelectionOrEl(el, prop, val);
    if (!applied) el.style[prop] = val;
    force();
  };

  // Aktualizacja pozycji toolbara (śledzi element przy scrollu)
  React.useLayoutEffect(() => {
    const update = () => {
      if (!el.isConnected) { onClose?.(); return; }
      const rect = el.getBoundingClientRect();
      // Mierz faktyczną szerokość toolbara jeśli już narysowany; fallback 600
      const W = toolbarRef.current?.offsetWidth || 600;
      const H = toolbarRef.current?.offsetHeight || 44;
      const margin = 12;
      let left = rect.left + rect.width / 2 - W / 2;
      let top = rect.top - H - 8;
      if (left < margin) left = margin;
      if (left + W > window.innerWidth - margin) left = window.innerWidth - W - margin;
      // Jeśli toolbar nie mieści się nad elementem → pokaż pod nim
      if (top < 64) {
        top = rect.bottom + 8;
        // Jeśli i pod nie ma miejsca → przypnij do górnej krawędzi viewportu
        if (top + H > window.innerHeight - margin) top = 64;
      }
      setPos({ left, top, ready: true });
    };
    update();
    // Drugie przebiegnięcie po narysowaniu (kiedy offsetWidth jest prawdziwe)
    const rafId = requestAnimationFrame(update);
    window.addEventListener('scroll', update, true);
    window.addEventListener('resize', update);
    const ro = new ResizeObserver(update);
    ro.observe(el);
    if (toolbarRef.current) ro.observe(toolbarRef.current);
    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('scroll', update, true);
      window.removeEventListener('resize', update);
      ro.disconnect();
    };
  }, [el]);

  const Btn = ({ children, onClick, active, title, wide, danger }) => (
    <button
      onMouseDown={e => e.preventDefault()}
      onClick={onClick}
      title={title}
      style={{
        padding: wide ? '0 9px' : 0, minWidth: wide ? 'auto' : 30,
        height: 30, border: 'none',
        background: active ? '#0F172A' : 'transparent',
        color: active ? '#fff' : danger ? '#B91C1C' : '#334155',
        borderRadius: 6, cursor: 'pointer',
        fontSize: 12, fontWeight: 600,
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 5,
        fontFamily: 'inherit',
      }}>{children}</button>
  );
  const Divider = () => <div style={{ width: 1, height: 20, background: '#E2E8F0', margin: '0 3px' }}/>;


  const ColorSwatches = ({ current, onPick }) => {
    const currentNorm = (current || '').toLowerCase();
    const matchesBrand = BRAND_COLORS.some(c =>
      c.val.toLowerCase() === currentNorm ||
      (c.val.startsWith('#') && currentNorm.startsWith('rgb') && window.rgbToHex?.(current)?.toLowerCase() === c.val.toLowerCase())
    );
    // Spróbuj zrobić HEX z current rgba/rgb
    const currentHex = current && current.startsWith('#') ? current.toUpperCase()
      : current && current.startsWith('rgb') ? (window.rgbToHex || (() => null))(current) : null;
    const isCustom = !matchesBrand && current && current !== 'transparent';
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 6 }}>
        {BRAND_COLORS.map(c => {
          const sel = c.val.toLowerCase() === currentNorm
            || (c.val.startsWith('#') && currentHex?.toLowerCase() === c.val.toLowerCase());
          return (
            <button key={c.val} onClick={() => onPick(c.val)} title={c.name}
              onMouseDown={e => e.preventDefault()}
              style={{
                width: 32, height: 32,
                background: c.val === 'transparent'
                  ? 'repeating-conic-gradient(#E2E8F0 0% 25%, transparent 0% 50%) 50% / 10px 10px'
                  : c.val,
                border: c.val === '#FFFFFF' || c.val === 'transparent' ? '1px solid #E2E8F0' : 'none',
                borderRadius: 8, cursor: 'pointer', padding: 0,
                outline: sel ? '2.5px solid #0F172A' : 'none',
                outlineOffset: sel ? 2 : 0,
              }}/>
          );
        })}
        {/* Plus wielokolorowy z custom color input */}
        <label title="Własny kolor"
          style={{
            width: 32, height: 32,
            background: 'conic-gradient(from 180deg, #EF4444, #F59E0B, #FDE047, #10B981, #3B82F6, #8B5CF6, #EC4899, #EF4444)',
            borderRadius: 8, cursor: 'pointer',
            display: 'grid', placeItems: 'center',
            outline: isCustom ? '2.5px solid #0F172A' : 'none',
            outlineOffset: isCustom ? 2 : 0,
            position: 'relative',
          }}>
          <span style={{
            width: 20, height: 20, borderRadius: '50%',
            background: isCustom ? (currentHex || current) : '#fff',
            display: 'grid', placeItems: 'center',
            color: isCustom ? (isLight(currentHex || '#ffffff') ? '#0F172A' : '#fff') : '#0F172A',
            fontSize: 13, fontWeight: 500, fontFamily: 'inherit',
            boxShadow: '0 0 0 1px rgba(0,0,0,.1)',
          }}>+</span>
          <input type="color" onChange={e => onPick(e.target.value)}
            onMouseDown={e => e.stopPropagation()}
            style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer', width: '100%', height: '100%' }}/>
        </label>
      </div>
    );
  };

  const NumberInput = ({ value, onChange, min = 0, max = 100, unit = 'px' }) => (
    <div style={{ display: 'inline-flex', alignItems: 'center', border: '1px solid #E2E8F0', borderRadius: 6, overflow: 'hidden' }}>
      <button onMouseDown={e => e.preventDefault()} onClick={() => onChange(Math.max(min, value - 1))}
        style={{ width: 24, height: 28, border: 'none', background: '#F8FAFC', cursor: 'pointer', color: '#64748B' }}>−</button>
      <div style={{ padding: '0 8px', fontSize: 12, fontWeight: 600, minWidth: 42, textAlign: 'center' }}>{value}{unit}</div>
      <button onMouseDown={e => e.preventDefault()} onClick={() => onChange(Math.min(max, value + 1))}
        style={{ width: 24, height: 28, border: 'none', background: '#F8FAFC', cursor: 'pointer', color: '#64748B' }}>+</button>
    </div>
  );

  // Render wg typu
  const isText = kind === 'text' || kind === 'button';
  const isBold = parseInt(cs.fontWeight) >= 600;
  const isItalic = cs.fontStyle === 'italic';
  const isUnderline = (cs.textDecorationLine || cs.textDecoration || '').includes('underline');
  const align = cs.textAlign;
  const currentFontFamily = cs.fontFamily;
  const fontSize = parseInt(cs.fontSize) || 16;
  const borderWidth = parseInt(cs.borderWidth) || 0;
  const borderColor = cs.borderColor;
  // borderRadius może być shorthand (4 wartości) — bierzemy top-left jako reprezentatywny.
  // UŻYWAMY cs.borderTopLeftRadius dla stabilności (nie "Npx Npx Npx Npx").
  const borderRadius = parseInt(cs.borderTopLeftRadius) || parseInt(cs.borderRadius) || 0;
  const bgColor = cs.backgroundColor;
  const color = cs.color;
  const padTop = parseInt(cs.paddingTop) || 0;
  const padBottom = parseInt(cs.paddingBottom) || 0;
  const padLeft = parseInt(cs.paddingLeft) || 0;
  const padRight = parseInt(cs.paddingRight) || 0;

  const closeExpanded = () => setExpanded(null);

  // Aplikuj bold/italic/underline — toggle na STYLU elementu (pewne)
  const applyFmt = (prop) => {
    toggleTextFormat(el, prop);
    force();
  };

  if (!pos.ready) return null;

  return (
    <>
    <div ref={toolbarRef}
      onMouseDown={e => e.preventDefault()}
      style={{
        position: 'fixed', left: pos.left, top: pos.top, zIndex: 9998,
        background: '#fff', borderRadius: 10,
        boxShadow: '0 10px 30px rgba(15,23,42,.22), 0 0 0 1px rgba(15,23,42,.08)',
        padding: 6, fontFamily: 'Inter, sans-serif',
        display: 'inline-flex', alignItems: 'center', gap: 3,
        minWidth: 200,
        animation: 'popIn .12s',
      }}>
      {/* Kontekstowa nazwa */}
      <div style={{ padding: '0 8px', fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5 }}>
        {kind === 'text' ? 'Tekst' :
         kind === 'button' ? 'Przycisk' :
         kind === 'input' ? 'Pole' :
         kind === 'section' ? 'Sekcja' :
         kind === 'image' ? 'Obraz' :
         kind === 'formField' ? 'Pole formularza' :
         kind === 'form' ? 'Formularz' :
         kind === 'testimonial' ? 'Opinia' :
         kind === 'infographicShape' ? 'Kształt' :
         kind === 'infographicItem' ? 'Krok' :
         kind === 'infographicContainer' ? 'Infografika' :
         kind === 'infographicLine' ? 'Łącznik' : ''}
      </div>
      <Divider/>

      {/* ==== TEXT & BUTTON ==== */}
      {isText && (
        <>
          {/* Font dropdown */}
          <Btn wide onClick={() => setExpanded(expanded === 'font' ? null : 'font')} title="Czcionka" active={expanded === 'font'}>
            <span style={{ fontSize: 11, maxWidth: 80, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {FONT_FAMILIES.find(f => currentFontFamily.includes(f.label))?.label || 'Inter'}
            </span>
            <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="6 9 12 15 18 9"/></svg>
          </Btn>
          {/* Font size */}
          <NumberInputV2 value={fontSize} onChange={v => setStyleSmart('fontSize', v + 'px')} min={8} max={200} step={1} width={110}/>
          <Divider/>
          <Btn onClick={() => applyFmt('bold')} active={isBold} title="Pogrubienie"><b style={{ fontSize: 13 }}>B</b></Btn>
          <Btn onClick={() => applyFmt('italic')} active={isItalic} title="Kursywa"><i style={{ fontSize: 13 }}>I</i></Btn>
          <Btn onClick={() => applyFmt('underline')} active={isUnderline} title="Podkreślenie"><u style={{ fontSize: 13 }}>U</u></Btn>
          <Divider/>
          <Btn onClick={() => setStyle('textAlign', 'left')} active={align === 'left' || align === 'start'} title="Do lewej"><Icon name="alignLeft"/></Btn>
          <Btn onClick={() => setStyle('textAlign', 'center')} active={align === 'center'} title="Do środka"><Icon name="alignCenter"/></Btn>
          <Btn onClick={() => setStyle('textAlign', 'right')} active={align === 'right' || align === 'end'} title="Do prawej"><Icon name="alignRight"/></Btn>
          <Divider/>
          <Btn onClick={() => setExpanded(expanded === 'color' ? null : 'color')} title="Kolor tekstu" active={expanded === 'color'}>
            <div style={{ display: 'grid', placeItems: 'center', gap: 1 }}>
              <span style={{ fontSize: 10, fontWeight: 700, lineHeight: 1 }}>A</span>
              <div style={{ width: 14, height: 3, background: color, borderRadius: 1, border: '1px solid rgba(0,0,0,.1)' }}/>
            </div>
          </Btn>
        </>
      )}

      {/* ==== BUTTON extra ==== */}
      {kind === 'button' && (
        <>
          <Divider/>
          <Btn wide onClick={() => setExpanded(expanded === 'bg' ? null : 'bg')} title="Tło / gradient" active={expanded === 'bg'}>
            <div style={{ width: 14, height: 14, borderRadius: 3, background: bgColor, border: '1px solid rgba(0,0,0,.15)' }}/>
            <span style={{ fontSize: 11 }}>Tło</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'border' ? null : 'border')} active={expanded === 'border'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
            <span style={{ fontSize: 11 }}>Ramka {borderWidth > 0 ? borderWidth+'px' : ''}</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'radius' ? null : 'radius')} title="Rogi" active={expanded === 'radius'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12c0-5 4-9 9-9"/></svg>
            <span style={{ fontSize: 11 }}>Rogi {borderRadius}px</span>
          </Btn>
        </>
      )}

      {/* ==== INPUT / FORM FIELD ==== */}
      {(kind === 'input' || kind === 'formField') && (
        <>
          <Btn wide onClick={() => setExpanded(expanded === 'border' ? null : 'border')} active={expanded === 'border'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
            <span style={{ fontSize: 11 }}>Ramka {borderWidth}px</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'radius' ? null : 'radius')} active={expanded === 'radius'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12c0-5 4-9 9-9"/></svg>
            <span style={{ fontSize: 11 }}>Rogi {borderRadius}px</span>
          </Btn>
          <Btn onClick={() => setExpanded(expanded === 'bg' ? null : 'bg')} title="Tło" active={expanded === 'bg'}>
            <div style={{ width: 16, height: 16, borderRadius: 4, background: bgColor, border: '1px solid rgba(0,0,0,.15)' }}/>
          </Btn>
          {kind === 'input' && (
            <Btn wide onClick={() => setExpanded(expanded === 'padding' ? null : 'padding')} active={expanded === 'padding'}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="1" strokeDasharray="2 2"/><rect x="7" y="7" width="10" height="10"/></svg>
              <span style={{ fontSize: 11 }}>Wielkość</span>
            </Btn>
          )}
        </>
      )}

      {/* ==== SECTION ==== */}
      {kind === 'section' && (
        <>
          <Btn onClick={() => { window.moveSection(el, 'up'); force(); }} title="Przenieś wyżej">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><polyline points="18 15 12 9 6 15"/></svg>
          </Btn>
          <Btn onClick={() => { window.moveSection(el, 'down'); force(); }} title="Przenieś niżej">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><polyline points="6 9 12 15 18 9"/></svg>
          </Btn>
          <Btn wide onClick={() => onAction?.('addBlockAfter')} title="Dodaj sekcję pod">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><path d="M12 5v14M5 12h14"/></svg>
            <span style={{ fontSize: 11 }}>Dodaj pod</span>
          </Btn>
          <Divider/>
          <Btn wide onClick={() => setExpanded(expanded === 'bg' ? null : 'bg')} active={expanded === 'bg'}>
            <div style={{ width: 14, height: 14, borderRadius: 3, background: bgColor, border: '1px solid rgba(0,0,0,.15)' }}/>
            <span style={{ fontSize: 11 }}>Tło</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'border' ? null : 'border')} active={expanded === 'border'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
            <span style={{ fontSize: 11 }}>Ramka {borderWidth > 0 ? borderWidth+'px' : ''}</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'padding' ? null : 'padding')} active={expanded === 'padding'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="1" strokeDasharray="2 2"/><rect x="7" y="7" width="10" height="10"/></svg>
            <span style={{ fontSize: 11 }}>Odstępy</span>
          </Btn>
        </>
      )}

      {/* ==== IMAGE ==== */}
      {kind === 'image' && (
        <>
          <Btn wide onClick={() => onAction?.('replaceImage')}>
            <Icon name="image"/>
            <span style={{ fontSize: 11 }}>Wymień</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'imgsize' ? null : 'imgsize')} active={expanded === 'imgsize'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
            <span style={{ fontSize: 11 }}>Rozmiar</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'imgpos' ? null : 'imgpos')} active={expanded === 'imgpos'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
            <span style={{ fontSize: 11 }}>Kadr</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'radius' ? null : 'radius')} active={expanded === 'radius'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12c0-5 4-9 9-9"/></svg>
            <span style={{ fontSize: 11 }}>Rogi {borderRadius}px</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'imgfilter' ? null : 'imgfilter')} active={expanded === 'imgfilter'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/></svg>
            <span style={{ fontSize: 11 }}>Filtr</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'border' ? null : 'border')} active={expanded === 'border'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
            <span style={{ fontSize: 11 }}>Ramka</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'imgshape' ? null : 'imgshape')} active={expanded === 'imgshape'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5"/></svg>
            <span style={{ fontSize: 11 }}>Kształt</span>
          </Btn>
        </>
      )}

      {/* ==== FORM (container całego formularza) ==== */}
      {kind === 'form' && (
        <>
          <Btn wide onClick={() => setExpanded(expanded === 'bg' ? null : 'bg')} active={expanded === 'bg'}>
            <div style={{ width: 14, height: 14, borderRadius: 3, background: bgColor, border: '1px solid rgba(0,0,0,.15)' }}/>
            <span style={{ fontSize: 11 }}>Tło</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'border' ? null : 'border')} active={expanded === 'border'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
            <span style={{ fontSize: 11 }}>Ramka {borderWidth > 0 ? borderWidth+'px' : ''}</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'radius' ? null : 'radius')} active={expanded === 'radius'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12c0-5 4-9 9-9"/></svg>
            <span style={{ fontSize: 11 }}>Rogi {borderRadius}px</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'padding' ? null : 'padding')} active={expanded === 'padding'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="1" strokeDasharray="2 2"/><rect x="7" y="7" width="10" height="10"/></svg>
            <span style={{ fontSize: 11 }}>Odstępy</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'shadow' ? null : 'shadow')} active={expanded === 'shadow'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="14" height="14" rx="2"/><path d="M7 21h14V7"/></svg>
            <span style={{ fontSize: 11 }}>Cień</span>
          </Btn>
          <Divider/>
          <Btn wide onClick={() => setExpanded(expanded === 'formFields' ? null : 'formFields')} active={expanded === 'formFields'} title="Zmień wygląd wszystkich pól w formularzu">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="6" width="18" height="4" rx="1"/><rect x="3" y="14" width="18" height="4" rx="1"/></svg>
            <span style={{ fontSize: 11 }}>Pola</span>
          </Btn>
        </>
      )}

      {/* ==== TESTIMONIAL (karta z opinią) ==== */}
      {kind === 'testimonial' && (
        <>
          <Btn wide onClick={() => setExpanded(expanded === 'bg' ? null : 'bg')} active={expanded === 'bg'}>
            <div style={{ width: 14, height: 14, borderRadius: 3, background: bgColor, border: '1px solid rgba(0,0,0,.15)' }}/>
            <span style={{ fontSize: 11 }}>Tło</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'border' ? null : 'border')} active={expanded === 'border'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
            <span style={{ fontSize: 11 }}>Ramka {borderWidth > 0 ? borderWidth+'px' : ''}</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'radius' ? null : 'radius')} active={expanded === 'radius'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12c0-5 4-9 9-9"/></svg>
            <span style={{ fontSize: 11 }}>Rogi {borderRadius}px</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'padding' ? null : 'padding')} active={expanded === 'padding'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="1" strokeDasharray="2 2"/><rect x="7" y="7" width="10" height="10"/></svg>
            <span style={{ fontSize: 11 }}>Odstępy</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'shadow' ? null : 'shadow')} active={expanded === 'shadow'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="14" height="14" rx="2"/><path d="M7 21h14V7"/></svg>
            <span style={{ fontSize: 11 }}>Cień</span>
          </Btn>
        </>
      )}

      {/* ==== INFOGRAPHIC SHAPE (circle / bar) ==== */}
      {kind === 'infographicShape' && (
        <>
          <button
            onMouseDown={e => e.preventDefault()}
            onClick={() => onAction?.('infographic-select-container')}
            title="Wybierz całą infografikę"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '6px 10px', height: 32,
              border: '1px solid #C7D2FE', background: '#EEF2FF', color: '#4338CA',
              borderRadius: 6, cursor: 'pointer', fontFamily: 'inherit',
              fontSize: 11, fontWeight: 600,
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
            Cała infografika
          </button>
          <Divider/>
          <Btn wide onClick={() => setExpanded(expanded === 'bg' ? null : 'bg')} title="Kolor wypełnienia" active={expanded === 'bg'}>
            <div style={{ width: 14, height: 14, borderRadius: 3, background: bgColor, border: '1px solid rgba(0,0,0,.15)' }}/>
            <span style={{ fontSize: 11 }}>Kolor</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'border' ? null : 'border')} active={expanded === 'border'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>
            <span style={{ fontSize: 11 }}>Ramka {borderWidth > 0 ? borderWidth+'px' : ''}</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'radius' ? null : 'radius')} title="Rogi" active={expanded === 'radius'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12c0-5 4-9 9-9"/></svg>
            <span style={{ fontSize: 11 }}>Rogi {borderRadius}px</span>
          </Btn>
          {el.dataset?.infographicCircle === 'true' && (
            <Btn wide onClick={() => setExpanded(expanded === 'icon' ? null : 'icon')} title="Ikona lub cyfra" active={expanded === 'icon'}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M12 2l3 7h7l-6 5 2 8-6-4-6 4 2-8-6-5h7z"/></svg>
              <span style={{ fontSize: 11 }}>Ikona</span>
            </Btn>
          )}
          <Divider/>
          <span style={{ fontSize: 10, color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, padding: '0 4px' }}>W</span>
          <NumberInputV2 value={parseInt(cs.width) || el.offsetWidth || 64} min={8} max={400} step={2} width={90}
            onChange={v => { el.style.width = v + 'px'; force(); }}/>
          <span style={{ fontSize: 10, color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, padding: '0 4px' }}>H</span>
          <NumberInputV2 value={parseInt(cs.height) || el.offsetHeight || 64} min={2} max={400} step={2} width={90}
            onChange={v => { el.style.height = v + 'px'; force(); }}/>
        </>
      )}

      {/* ==== INFOGRAPHIC LINE (łącznik między krokami) ==== */}
      {kind === 'infographicLine' && (
        <>
          <button
            onMouseDown={e => e.preventDefault()}
            onClick={() => onAction?.('infographic-select-container')}
            title="Wybierz całą infografikę"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '6px 10px', height: 32,
              border: '1px solid #C7D2FE', background: '#EEF2FF', color: '#4338CA',
              borderRadius: 6, cursor: 'pointer', fontFamily: 'inherit',
              fontSize: 11, fontWeight: 600,
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
            Cała infografika
          </button>
          <Divider/>
          <Btn wide onClick={() => setExpanded(expanded === 'bg' ? null : 'bg')} title="Kolor łącznika" active={expanded === 'bg'}>
            <div style={{ width: 14, height: 14, borderRadius: 3, background: bgColor, border: '1px solid rgba(0,0,0,.15)' }}/>
            <span style={{ fontSize: 11 }}>Kolor</span>
          </Btn>
          <Btn wide onClick={() => setExpanded(expanded === 'lineStyle' ? null : 'lineStyle')} title="Styl linii" active={expanded === 'lineStyle'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M3 12h18"/></svg>
            <span style={{ fontSize: 11 }}>Styl</span>
          </Btn>
          <Divider/>
          <span style={{ fontSize: 10, color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, padding: '0 4px' }}>Grubość</span>
          <NumberInputV2 value={parseInt(cs.height) || 2} min={1} max={20} step={1} width={80}
            onChange={v => { el.style.height = v + 'px'; force(); }}/>
        </>
      )}

      {/* ==== INFOGRAPHIC ITEM (pojedynczy krok) ==== */}
      {kind === 'infographicItem' && (
        <>
          <button
            onMouseDown={e => e.preventDefault()}
            onClick={() => onAction?.('infographic-select-container')}
            title="Wybierz całą infografikę"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '6px 10px', height: 32,
              border: '1px solid #C7D2FE', background: '#EEF2FF', color: '#4338CA',
              borderRadius: 6, cursor: 'pointer', fontFamily: 'inherit',
              fontSize: 11, fontWeight: 600,
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/></svg>
            Cała infografika
          </button>
          <Divider/>
          <Btn onClick={() => onAction?.('infographic-duplicate-step')} title="Duplikuj krok">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="8" y="8" width="12" height="12" rx="2"/><rect x="4" y="4" width="12" height="12" rx="2"/></svg>
            <span style={{ fontSize: 11 }}>Duplikuj</span>
          </Btn>
          <Btn onClick={() => onAction?.('infographic-add-step')} title="Dodaj krok obok">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M12 5v14M5 12h14"/></svg>
            <span style={{ fontSize: 11 }}>Dodaj</span>
          </Btn>
          <Btn onClick={() => onAction?.('infographic-move-step-left')} title="Przesuń w lewo">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M15 18l-6-6 6-6"/></svg>
          </Btn>
          <Btn onClick={() => onAction?.('infographic-move-step-right')} title="Przesuń w prawo">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M9 18l6-6-6-6"/></svg>
          </Btn>
          <Btn onClick={() => onAction?.('infographic-remove-step')} title="Usuń krok" danger>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M6 6l1 14a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-14"/></svg>
            <span style={{ fontSize: 11 }}>Usuń</span>
          </Btn>
        </>
      )}

      {/* ==== INFOGRAPHIC CONTAINER (cała infografika) ==== */}
      {kind === 'infographicContainer' && (
        <>
          <button
            onMouseDown={e => e.preventDefault()}
            onClick={() => onAction?.('infographic-change-template')}
            title="Wybierz inny szablon z galerii"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '6px 12px', height: 32,
              border: '1px solid #C7D2FE', background: '#EEF2FF', color: '#4338CA',
              borderRadius: 6, cursor: 'pointer', fontFamily: 'inherit',
              fontSize: 11, fontWeight: 700,
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
            Zmień szablon
          </button>
          <Divider/>
          <span style={{ fontSize: 10, color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, padding: '0 4px' }}>Kolumny</span>
          {[2,3,4,5,6].map(n => {
            const cur = (cs.gridTemplateColumns || '').match(/repeat\((\d+)/)?.[1] || '4';
            const active = parseInt(cur) === n;
            return (
              <Btn key={n} onClick={() => { el.style.gridTemplateColumns = `repeat(${n}, 1fr)`; force(); }} active={active}>
                <span style={{ fontSize: 12, fontWeight: 700 }}>{n}</span>
              </Btn>
            );
          })}
          <Divider/>
          <Btn wide onClick={() => setExpanded(expanded === 'gap' ? null : 'gap')} title="Odstępy między krokami" active={expanded === 'gap'}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M8 4v16M16 4v16"/></svg>
            <span style={{ fontSize: 11 }}>Odstęp {parseInt(cs.gap) || 0}px</span>
          </Btn>
        </>
      )}

      {/* ==== UNIVERSAL ACTIONS ==== */}
      <Divider/>
      {kind !== 'section' && <Btn onClick={() => onAction?.('move')} title="Przesuń (drag)"><Icon name="move"/></Btn>}
      <Btn onClick={() => onAction?.('duplicate')} title="Duplikuj"><Icon name="copy"/></Btn>
      <Btn onClick={() => onAction?.('delete')} title="Usuń"><Icon name="trash"/></Btn>
      <Divider/>
      <Btn onClick={onClose} title="Zamknij"><Icon name="close"/></Btn>
    </div>

    {/* ==== SUB-PANELE w portalu z bardzo wysokim z-index ==== */}
    {expanded === 'font' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={280} title="Czcionka i waga" onReset={() => { el.style.fontFamily=''; el.style.fontWeight=''; el.style.fontSize=''; force(); }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Rodzina</div>
        <div style={{ display: 'grid', gap: 2 }}>
          {FONT_FAMILIES.map(f => (
            <button key={f.val}
              onMouseDown={e => e.preventDefault()}
              onClick={() => { setStyleSmart('fontFamily', f.val); closeExpanded(); }}
              style={{
                padding: '8px 10px', border: 'none',
                background: currentFontFamily.includes(f.label) ? '#F1F5F9' : '#fff',
                borderRadius: 6, cursor: 'pointer', textAlign: 'left',
                fontFamily: f.val, fontSize: 14, display: 'flex', alignItems: 'center', gap: 10,
                color: '#0F172A',
              }}>
              <span style={{ flex: 1 }}>{f.label}</span>
              <span style={{ fontSize: 10, color: '#94A3B8', textTransform: 'uppercase', fontFamily: 'Inter, sans-serif' }}>
                {f.type === 'h' ? 'Nagłówek' : f.type === 'm' ? 'Mono' : 'Tekst'}
              </span>
            </button>
          ))}
        </div>
      </SubPanelImpl>
    )}
    {expanded === 'color' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} title="Kolor tekstu" onReset={() => { el.style.color=''; force(); }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>Kolor tekstu</div>
        <div style={{ fontSize: 11, color: '#64748B', marginBottom: 10 }}>
          Zaznacz fragment tekstu aby zmienić kolor tylko jego. Bez zaznaczenia — cały element.
        </div>
        <ColorSwatches current={color} onPick={v => {
          const applied = window.applyToSelectionOrEl(el, 'color', v);
          if (!applied) setStyle('color', v);
          closeExpanded();
          force();
        }}/>
      </SubPanelImpl>
    )}
    {expanded === 'bg' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={340} title="Tło"
        snapshotEls={kind === 'section' ? [el.querySelector(':scope > [data-bg-layer]')] : []}
        onReset={() => { el.style.background=''; el.style.backgroundImage=''; el.style.backgroundColor=''; force(); }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 10 }}>
          {kind === 'section' ? 'Tło sekcji' : kind === 'button' ? 'Tło przycisku' : 'Tło'}
        </div>
        <BgEditor el={el} kind={kind} onChange={() => force()}/>
      </SubPanelImpl>
    )}
    {expanded === 'border' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={340} title="Ramka" onReset={() => { el.style.borderWidth=''; el.style.borderStyle=''; el.style.borderColor=''; el.style.border=''; force(); }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Grubość</div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 14 }}>
          <NumberInputV2 value={borderWidth} min={0} max={20} step={1} width={110}
            onChange={v => {
              // Ustawiamy tylko width, żeby nie ruszać koloru ani stylu.
              el.style.borderWidth = v + 'px';
              // Ale jeśli dotąd nie było ramki — borderStyle musi być 'solid',
              // inaczej przeglądarka ignoruje width.
              if (v > 0 && (!cs.borderStyle || cs.borderStyle === 'none')) {
                el.style.borderStyle = 'solid';
              }
              force();
            }}/>
          <SliderV2 value={Math.min(borderWidth, 12)} min={0} max={12} step={1}
            onChange={v => {
              el.style.borderWidth = v + 'px';
              if (v > 0 && (!cs.borderStyle || cs.borderStyle === 'none')) el.style.borderStyle = 'solid';
              force();
            }}/>
        </div>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Kolor</div>
        <ColorSwatches current={borderColor} onPick={v => {
          el.style.borderColor = v;
          // Jeśli ramka niewidoczna — daj domyślną grubość 2px
          if (borderWidth === 0) {
            el.style.borderWidth = '2px';
            el.style.borderStyle = 'solid';
          }
          force();
        }}/>
        <div style={{ marginTop: 14, paddingTop: 10, borderTop: '1px solid #E2E8F0' }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Styl linii</div>
          <div style={{ display: 'flex', gap: 4 }}>
            {['solid', 'dashed', 'dotted', 'double', 'none'].map(s => (
              <button key={s} onMouseDown={e => e.preventDefault()}
                onClick={() => { el.style.borderStyle = s; force(); }}
                style={{
                  flex: 1, padding: '6px 8px',
                  border: cs.borderStyle === s ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  background: '#fff', cursor: 'pointer', borderRadius: 6,
                  fontSize: 11, fontWeight: 600, fontFamily: 'inherit',
                }}>{s === 'none' ? 'Brak' : s}</button>
            ))}
          </div>
        </div>
      </SubPanelImpl>
    )}
    {expanded === 'radius' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={300} title="Zaokrąglenie rogów" onReset={() => { el.style.borderRadius=''; force(); }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 12 }}>
          <NumberInputV2 value={borderRadius} onChange={v => setStyle('borderRadius', v + 'px')} min={0} max={999} step={1} width={110}/>
          <SliderV2 value={Math.min(borderRadius, 80)} min={0} max={80} step={1}
            onChange={v => setStyle('borderRadius', v + 'px')}/>
        </div>
        <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Presety</div>
        <div style={{ display: 'flex', gap: 4, marginBottom: 10 }}>
          {[0, 4, 8, 16, 24, 999].map(r => (
            <button key={r} onMouseDown={e => e.preventDefault()}
              onClick={() => setStyle('borderRadius', r + 'px')}
              title={r === 999 ? 'Pełne' : r + 'px'}
              style={{
                width: 40, height: 40, border: borderRadius === r ? '2px solid #0F172A' : '1px solid #E2E8F0',
                background: '#fff', cursor: 'pointer', borderRadius: 6, padding: 5,
              }}>
              <div style={{ width: '100%', height: '100%', border: '1.5px solid #334155', borderRadius: r === 999 ? 999 : r }}/>
            </button>
          ))}
        </div>
      </SubPanelImpl>
    )}
    {expanded === 'imgsize' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={320} title="Rozmiar obrazu" onReset={() => { const s=(()=>{try{return JSON.parse(el.dataset.origSnapshot||'null');}catch{return null;}})(); if(!s)return; el.style.width=s.w+'px'; el.style.height=s.h+'px'; el.style.maxWidth=s.declared?.maxW||''; el.style.maxHeight=s.declared?.maxH||''; const w=el.closest('[data-img-wrap]'); if(w){w.style.width=s.w+'px';w.style.maxWidth='';} force(); }}>
        {(() => {
          // Snapshot zapisywany w data-orig-snapshot (faktyczne wymiary piksele po render-ze AI)
          const currW = el.getBoundingClientRect().width;
          const currH = el.getBoundingClientRect().height;
          let snap = null;
          try { snap = JSON.parse(el.dataset.origSnapshot || 'null'); } catch {}
          const resetToOriginal = () => {
            if (!snap) return;
            // Ustaw dokładnie te piksele które AI pierwotnie wyrenderowało
            el.style.width = snap.w + 'px';
            el.style.height = snap.h + 'px';
            // Wyczyść max-y które mogłyby ograniczać
            el.style.maxWidth = snap.declared?.maxW || '';
            el.style.maxHeight = snap.declared?.maxH || '';
            // Wyczyść wrapper (wiz-img-wrap) żeby nie wymuszał szerokości
            const wrap = el.closest('[data-img-wrap]');
            if (wrap) {
              wrap.style.width = snap.w + 'px';
              wrap.style.maxWidth = '';
            }
            force();
          };
          const origLabel = snap ? `(${snap.w} × ${snap.h} px)` : '';
          const lockRatio = el.dataset.lockRatio === '1';
          const applyWidth = (v) => {
            el.style.width = v + 'px';
            if (lockRatio) {
              // Height oddajemy aspect-ratio
              el.style.height = 'auto';
            }
            const wrap = el.closest('[data-img-wrap]');
            if (wrap) {
              wrap.style.width = v + 'px';
              if (lockRatio) wrap.style.height = 'auto';
            }
            force();
          };
          const applyHeight = (v) => {
            if (lockRatio) {
              // Zamieniamy na wymuszenie width (height wyliczy aspect-ratio)
              el.style.width = v + 'px';
              el.style.height = 'auto';
              const wrap = el.closest('[data-img-wrap]');
              if (wrap) { wrap.style.width = v + 'px'; wrap.style.height = 'auto'; }
            } else {
              el.style.height = v + 'px';
            }
            force();
          };
          return (
            <>
              {lockRatio ? (
                <>
                  <div style={{
                    padding: '7px 10px', background: '#EFF6FF', border: '1px solid #BFDBFE',
                    borderRadius: 6, fontSize: 11, color: '#1E3A8A', marginBottom: 10,
                    display: 'flex', alignItems: 'center', gap: 6,
                  }}>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>
                    Proporcje 1:1 — jeden wymiar (kształt wymaga kwadratu).
                  </div>
                  <div style={{ display: 'grid', gap: 10, marginBottom: 14 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 90, fontSize: 11.5, color: '#475569', fontWeight: 500 }}>Rozmiar</div>
                      <NumberInputV2 value={Math.round(currW)} min={20} max={2000} step={10} width={120}
                        onChange={applyWidth}/>
                    </div>
                  </div>
                </>
              ) : (
                <div style={{ display: 'grid', gap: 10, marginBottom: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 90, fontSize: 11.5, color: '#475569', fontWeight: 500 }}>Szerokość</div>
                    <NumberInputV2 value={Math.round(currW)} min={20} max={2000} step={10} width={120}
                      onChange={applyWidth}/>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 90, fontSize: 11.5, color: '#475569', fontWeight: 500 }}>Wysokość</div>
                    <NumberInputV2 value={Math.round(currH)} min={20} max={2000} step={10} width={120}
                      onChange={applyHeight}/>
                  </div>
                </div>
              )}
              <div style={{ paddingTop: 10, borderTop: '1px solid #E2E8F0' }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Szybko</div>
                <div style={{ display: 'flex', gap: 4, marginBottom: 10 }}>
                  {[
                    { l: 'Małe', w: 300, h: 240, sq: 260 },
                    { l: 'Średnie', w: 500, h: 380, sq: 400 },
                    { l: 'Duże', w: 800, h: 560, sq: 560 },
                    { l: 'Pełne', w: '100%', h: 600, sq: 600 },
                  ].map(p => (
                    <button key={p.l} onMouseDown={e => e.preventDefault()}
                      onClick={() => {
                        if (lockRatio) {
                          el.style.width = p.sq + 'px';
                          el.style.height = 'auto';
                          const w = el.closest('[data-img-wrap]');
                          if (w) { w.style.width = p.sq + 'px'; w.style.height = 'auto'; }
                        } else {
                          el.style.width = typeof p.w === 'number' ? p.w + 'px' : p.w;
                          el.style.height = p.h + 'px';
                        }
                        force();
                      }}
                      style={{
                        flex: 1, padding: '6px 8px', border: '1px solid #E2E8F0',
                        background: '#fff', cursor: 'pointer', borderRadius: 6,
                        fontSize: 11, fontWeight: 600, fontFamily: 'inherit',
                      }}>{p.l}</button>
                  ))}
                </div>
                <button onMouseDown={e => e.preventDefault()}
                  onClick={resetToOriginal}
                  style={{
                    width: '100%', padding: '8px 12px',
                    border: '1px solid #CBD5E1', background: '#F8FAFC',
                    color: '#0F172A', borderRadius: 7, cursor: 'pointer',
                    fontSize: 12, fontWeight: 600, fontFamily: 'inherit',
                    display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  }}>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M3 12a9 9 0 109-9 9.75 9.75 0 00-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                  Przywróć rozmiar wyjściowy {origLabel}
                </button>
              </div>
            </>
          );
        })()}
      </SubPanelImpl>
    )}
    {expanded === 'imgpos' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={260} title="Kadrowanie" onReset={() => { el.style.objectFit=''; el.style.objectPosition=''; force(); }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Kadrowanie (object-position)</div>
        <div style={{ fontSize: 11, color: '#64748B', marginBottom: 12 }}>Przesuń punkt żeby wykadrować zdjęcie:</div>
        {(() => {
          const posStr = cs.objectPosition || '50% 50%';
          const parts = posStr.split(/\s+/).map(p => parseFloat(p));
          const px = isNaN(parts[0]) ? 50 : parts[0];
          const py = isNaN(parts[1]) ? 50 : parts[1];
          return (
            <>
              <div
                onMouseDown={e => e.preventDefault()}
                onClick={e => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  const nx = ((e.clientX - rect.left) / rect.width * 100).toFixed(0);
                  const ny = ((e.clientY - rect.top) / rect.height * 100).toFixed(0);
                  el.style.objectFit = 'cover';
                  el.style.objectPosition = `${nx}% ${ny}%`;
                  force();
                }}
                style={{
                  position: 'relative', width: '100%', aspectRatio: '16/10',
                  background: `url("${el.getAttribute('src')}") center/cover`,
                  borderRadius: 8, border: '2px solid #E2E8F0', cursor: 'crosshair',
                  overflow: 'hidden',
                }}>
                <div style={{
                  position: 'absolute', left: `${px}%`, top: `${py}%`,
                  transform: 'translate(-50%, -50%)',
                  width: 20, height: 20, borderRadius: '50%',
                  background: '#6366F1', border: '3px solid #fff',
                  boxShadow: '0 2px 8px rgba(0,0,0,.3)',
                }}/>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 11, color: '#64748B' }}>
                <span>X: {px}%</span>
                <span>Y: {py}%</span>
              </div>
              <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid #E2E8F0' }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Object-fit</div>
                <div style={{ display: 'flex', gap: 4 }}>
                  {['cover', 'contain', 'fill'].map(f => (
                    <button key={f} onMouseDown={e => e.preventDefault()}
                      onClick={() => { el.style.objectFit = f; force(); }}
                      style={{
                        flex: 1, padding: '6px 8px',
                        border: cs.objectFit === f ? '2px solid #0F172A' : '1px solid #E2E8F0',
                        background: '#fff', cursor: 'pointer', borderRadius: 6,
                        fontSize: 11, fontWeight: 600, fontFamily: 'inherit',
                      }}>{f}</button>
                  ))}
                </div>
              </div>
            </>
          );
        })()}
      </SubPanelImpl>
    )}
    {expanded === 'imgfilter' && (() => {
      // Model:
      //   preset  = string filter (mogą być hue-rotate, sepia itp.)
      //   adjust  = { brightness, contrast, blur, saturate, grayscale } — niezależne, stosowane NA presetcie
      // Końcowy style.filter = preset + adjust. Zmiana jednego nie kasuje drugiego.
      const PRESETS = [
        { id: 'none', l: 'Oryginał', f: '' },
        { id: 'bw', l: 'B&W', f: 'grayscale(1) contrast(1.05)' },
        { id: 'sepia', l: 'Sepia', f: 'sepia(0.85) saturate(1.1) brightness(0.95)' },
        { id: 'vintage', l: 'Vintage', f: 'sepia(0.5) contrast(0.9) brightness(1.05) saturate(1.2)' },
        { id: 'red', l: 'Czerwień', f: 'grayscale(1) sepia(1) hue-rotate(-30deg) saturate(4.5) brightness(0.95)' },
        { id: 'green', l: 'Zieleń', f: 'grayscale(1) sepia(1) hue-rotate(60deg) saturate(4) brightness(0.95)' },
        { id: 'blue', l: 'Niebieski', f: 'grayscale(1) sepia(1) hue-rotate(170deg) saturate(5) brightness(0.95)' },
        { id: 'violet', l: 'Fiolet', f: 'grayscale(1) sepia(1) hue-rotate(220deg) saturate(5) brightness(0.95)' },
        { id: 'cool', l: 'Chłód', f: 'saturate(0.9) hue-rotate(-8deg)' },
        { id: 'warm', l: 'Ciepło', f: 'sepia(0.25) saturate(1.2) brightness(1.02)' },
        { id: 'drama', l: 'Dramat', f: 'contrast(1.35) saturate(0.85) brightness(0.92)' },
        { id: 'bright', l: 'Jasne', f: 'brightness(1.12) contrast(0.95) saturate(1.1)' },
      ];
      const presetId = el.dataset.filterPreset || 'none';
      const currentPreset = PRESETS.find(p => p.id === presetId) || PRESETS[0];
      const adjust = el.dataset.filterAdjust ? JSON.parse(el.dataset.filterAdjust) : { brightness: 1, contrast: 1, blur: 0, saturate: 1, grayscale: 0 };
      const render = () => {
        const a = el.dataset.filterAdjust ? JSON.parse(el.dataset.filterAdjust) : adjust;
        const p = PRESETS.find(x => x.id === (el.dataset.filterPreset || 'none')) || PRESETS[0];
        const adj = `brightness(${a.brightness}) contrast(${a.contrast}) blur(${a.blur}px) saturate(${a.saturate}) grayscale(${a.grayscale})`;
        el.style.filter = (p.f ? p.f + ' ' : '') + adj;
        force();
      };
      const setPreset = (id) => { el.dataset.filterPreset = id; render(); };
      const setAdjust = (patch) => {
        const next = { ...adjust, ...patch };
        el.dataset.filterAdjust = JSON.stringify(next);
        render();
      };
      return (
        <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={340} title="Filtry"
          onReset={() => { delete el.dataset.filterPreset; delete el.dataset.filterAdjust; el.style.filter=''; force(); }}>
          {/* KROK 1 — preset (baza) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <div style={{
              width: 18, height: 18, borderRadius: '50%', background: '#0F172A', color: '#fff',
              fontSize: 10, fontWeight: 700, display: 'grid', placeItems: 'center',
            }}>1</div>
            <div style={{ fontSize: 10.5, fontWeight: 700, color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.5 }}>Wybierz kolor / nastrój</div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6, marginBottom: 14 }}>
            {PRESETS.map(p => (
              <button key={p.id} onMouseDown={e => e.preventDefault()}
                onClick={() => setPreset(p.id)}
                style={{
                  padding: '6px 4px',
                  border: presetId === p.id ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  background: presetId === p.id ? '#F1F5F9' : '#fff',
                  cursor: 'pointer', borderRadius: 6,
                  fontSize: 10.5, fontWeight: 600, fontFamily: 'inherit',
                }}>{p.l}</button>
            ))}
          </div>

          {/* KROK 2 — korekcje na bazie presetu */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, paddingTop: 10, borderTop: '1px solid #E2E8F0' }}>
            <div style={{
              width: 18, height: 18, borderRadius: '50%', background: '#0F172A', color: '#fff',
              fontSize: 10, fontWeight: 700, display: 'grid', placeItems: 'center',
            }}>2</div>
            <div style={{ fontSize: 10.5, fontWeight: 700, color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.5 }}>Dostrój parametry</div>
          </div>
          <FilterRow label="Jasność" value={Math.round(adjust.brightness * 100)} max={200} unit="%"
            onChange={v => setAdjust({ brightness: v/100 })}/>
          <FilterRow label="Kontrast" value={Math.round(adjust.contrast * 100)} max={200} unit="%"
            onChange={v => setAdjust({ contrast: v/100 })}/>
          <FilterRow label="Nasycenie" value={Math.round(adjust.saturate * 100)} max={200} unit="%"
            onChange={v => setAdjust({ saturate: v/100 })}/>
          <FilterRow label="Rozmycie" value={Math.round(adjust.blur)} max={20} unit="px"
            onChange={v => setAdjust({ blur: v })}/>
          <FilterRow label="Wyszarzenie" value={Math.round(adjust.grayscale * 100)} max={100} unit="%"
            onChange={v => setAdjust({ grayscale: v/100 })}/>
          <div style={{ fontSize: 10.5, color: '#94A3B8', marginTop: 6, fontStyle: 'italic' }}>
            Suwaki działają <b style={{ color: '#64748B' }}>na wybranym presecie</b> — nie kasują koloru.
          </div>
        </SubPanelImpl>
      );
    })()}

    {expanded === 'imgshape' && (() => {
      const curr = el.style.clipPath || '';
      const SHAPES = [
        { id: 'none', label: 'Brak', cp: '', lockRatio: null, icon: <rect x="3" y="3" width="18" height="18" rx="1" fill="none" stroke="currentColor" strokeWidth="1.8"/> },
        { id: 'circle', label: 'Koło', cp: 'circle(50% at 50% 50%)', lockRatio: 1, icon: <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8"/> },
        { id: 'ellipse', label: 'Elipsa', cp: 'ellipse(50% 40% at 50% 50%)', lockRatio: null, icon: <ellipse cx="12" cy="12" rx="10" ry="7" fill="none" stroke="currentColor" strokeWidth="1.8"/> },
        { id: 'triangle', label: 'Trójkąt', cp: 'polygon(50% 0%, 100% 100%, 0% 100%)', lockRatio: null, icon: <polygon points="12 3 22 21 2 21" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/> },
        { id: 'trapezoid', label: 'Trapez', cp: 'polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%)', lockRatio: null, icon: <polygon points="6 3 18 3 22 21 2 21" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/> },
        { id: 'hex', label: 'Sześciokąt', cp: 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)', lockRatio: 1, icon: <polygon points="7 3 17 3 22 12 17 21 7 21 2 12" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/> },
        { id: 'diamond', label: 'Romb', cp: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)', lockRatio: 1, icon: <polygon points="12 2 22 12 12 22 2 12" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round"/> },
        { id: 'arch', label: 'Łuk', cp: 'path("M 0 400 L 0 160 Q 0 0 200 0 Q 400 0 400 160 L 400 400 Z")', lockRatio: null, icon: <path d="M3 21V10a9 9 0 0118 0v11" fill="none" stroke="currentColor" strokeWidth="1.8"/> },
      ];
      const setShape = (s) => {
        el.style.clipPath = s.cp;
        // Zarządzaj aspect-ratio — nie wymuszaj width/height na sztywno
        if (s.lockRatio === 1) {
          el.style.aspectRatio = '1 / 1';
          // Wyzeruj height żeby aspectRatio miał pełną władzę (width rządzi)
          el.style.height = 'auto';
          const w = el.closest('[data-img-wrap]');
          if (w) { w.style.aspectRatio = '1 / 1'; w.style.height = 'auto'; }
          el.dataset.lockRatio = '1';
        } else {
          el.style.aspectRatio = '';
          delete el.dataset.lockRatio;
          const w = el.closest('[data-img-wrap]');
          if (w) w.style.aspectRatio = '';
        }
        force();
      };
      const isCurr = (cp) => curr === cp;
      return (
        <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={320} title="Kształt obrazu" onReset={() => { el.style.clipPath=''; el.style.borderRadius=''; el.style.aspectRatio=''; delete el.dataset.lockRatio; const w=el.closest('[data-img-wrap]'); if(w){w.style.aspectRatio='';} force(); }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6, marginBottom: 14 }}>
            {SHAPES.map(s => (
              <button key={s.id} onMouseDown={e => e.preventDefault()}
                onClick={() => setShape(s)}
                title={s.label}
                style={{
                  aspectRatio: '1', border: isCurr(s.cp) ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  background: '#F8FAFC', cursor: 'pointer', borderRadius: 8,
                  display: 'grid', placeItems: 'center', color: '#334155',
                }}>
                <svg width="28" height="28" viewBox="0 0 24 24">{s.icon}</svg>
              </button>
            ))}
          </div>
          {el.dataset.lockRatio === '1' && (
            <div style={{
              padding: '8px 10px', background: '#FEF3C7', border: '1px solid #FDE68A',
              borderRadius: 6, fontSize: 11, color: '#78350F', marginBottom: 12,
            }}>
              Ten kształt ma stałe proporcje 1:1. Zmiana rozmiaru zachowuje kwadrat.
            </div>
          )}
          <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Ścięcie narożników (linia prosta)</div>
          <CornerCut el={el} onApply={() => force()}/>
        </SubPanelImpl>
      );
    })()}

    {expanded === 'padding' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={340} title="Odstępy" onReset={() => { el.style.padding=''; el.style.paddingTop=''; el.style.paddingRight=''; el.style.paddingBottom=''; el.style.paddingLeft=''; force(); }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 10 }}>
          {kind === 'section' ? 'Odstępy sekcji' : 'Odstępy pola'}
        </div>
        <div style={{ display: 'grid', gap: 10 }}>
          <PadRow label="Góra" value={padTop} onChange={v => setStyle('paddingTop', v + 'px')} max={kind === 'section' ? 400 : 100} step={4}/>
          <PadRow label="Dół" value={padBottom} onChange={v => setStyle('paddingBottom', v + 'px')} max={kind === 'section' ? 400 : 100} step={4}/>
          <PadRow label="Lewa" value={padLeft} onChange={v => setStyle('paddingLeft', v + 'px')} max={kind === 'section' ? 300 : 100} step={4}/>
          <PadRow label="Prawa" value={padRight} onChange={v => setStyle('paddingRight', v + 'px')} max={kind === 'section' ? 300 : 100} step={4}/>
        </div>
        {kind === 'section' && (
          <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid #E2E8F0' }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Szybko</div>
            <div style={{ display: 'flex', gap: 4 }}>
              {[
                { l: 'Mały', v: 40 },
                { l: 'Średni', v: 80 },
                { l: 'Duży', v: 120 },
                { l: 'XL', v: 160 },
              ].map(p => (
                <button key={p.l} onMouseDown={e => e.preventDefault()}
                  onClick={() => { setStyle('paddingTop', p.v + 'px'); setStyle('paddingBottom', p.v + 'px'); }}
                  style={{
                    flex: 1, padding: '6px 8px', border: '1px solid #E2E8F0',
                    background: '#fff', cursor: 'pointer', borderRadius: 6,
                    fontSize: 11, fontWeight: 600, fontFamily: 'inherit',
                  }}>{p.l}</button>
              ))}
            </div>
          </div>
        )}
      </SubPanelImpl>
    )}

    {expanded === 'shadow' && (() => {
      const PRESETS = [
        { name: 'Brak', val: 'none' },
        { name: 'Delikatny', val: '0 2px 8px rgba(15,23,42,.08)' },
        { name: 'Miękki', val: '0 8px 24px rgba(15,23,42,.10)' },
        { name: 'Średni', val: '0 12px 32px rgba(15,23,42,.14)' },
        { name: 'Mocny', val: '0 20px 50px rgba(15,23,42,.22)' },
        { name: 'Unoszący', val: '0 30px 60px -15px rgba(15,23,42,.30)' },
        { name: 'Ostry', val: '6px 6px 0 rgba(15,23,42,.90)' },
        { name: 'Ciepły', val: '0 14px 30px rgba(194,65,12,.18)' },
      ];
      const activePreset = el.dataset.shadowPreset || (!el.style.boxShadow ? 'Brak' : null);
      return (
        <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={340} title="Cień" onReset={() => { el.style.boxShadow=''; delete el.dataset.shadowPreset; force(); }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 10 }}>Styl cienia</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6 }}>
            {PRESETS.map(p => {
              const active = activePreset === p.name;
              return (
                <button key={p.name} onMouseDown={e => e.preventDefault()}
                  onClick={() => {
                    el.style.boxShadow = p.val === 'none' ? '' : p.val;
                    el.dataset.shadowPreset = p.name;
                    force();
                  }}
                  title={p.name}
                  style={{
                    position: 'relative',
                    padding: '8px 4px 12px',
                    border: active ? '2px solid #6366F1' : '1px solid #E2E8F0',
                    background: active ? '#EEF2FF' : '#fff',
                    cursor: 'pointer', borderRadius: 8,
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
                    fontSize: 10, fontWeight: active ? 700 : 600, fontFamily: 'inherit',
                    color: active ? '#4338CA' : '#334155',
                    outline: 'none',
                  }}>
                  {active && (
                    <div style={{ position: 'absolute', top: 3, right: 3, width: 14, height: 14, borderRadius: '50%', background: '#6366F1', display: 'grid', placeItems: 'center' }}>
                      <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="4" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                  )}
                  <div style={{ width: 34, height: 20, borderRadius: 4, background: '#fff', border: '1px solid #E2E8F0', boxShadow: p.val === 'none' ? 'none' : p.val, marginTop: 4 }}/>
                  <span>{p.name}</span>
                </button>
              );
            })}
          </div>
          <div style={{ marginTop: 10, fontSize: 11, color: '#64748B' }}>
            Cień sprawia, że karta/formularz „unosi się" — daje głębię.
          </div>
        </SubPanelImpl>
      );
    })()}

    {expanded === 'formFields' && (() => {
      // Znajdź pola: prawdziwe inputy + "udawane" div z data-form-field
      const realFields = Array.from(el.querySelectorAll('input, textarea, select'));
      const fakeFields = Array.from(el.querySelectorAll('[data-form-field="true"]'));
      const targets = [...realFields, ...fakeFields];
      // Odczyt z pierwszego pola
      const sample = targets[0];
      const sampleCs = sample ? getComputedStyle(sample) : null;
      const sampleBw = sampleCs ? parseInt(sampleCs.borderWidth) || 0 : 1;
      const sampleBr = sampleCs ? parseInt(sampleCs.borderRadius) || 0 : 8;
      const sampleBg = sampleCs ? sampleCs.backgroundColor : '#ffffff';
      const sampleBc = sampleCs ? sampleCs.borderColor : '#e2e8f0';
      const applyAll = (prop, val) => {
        targets.forEach(t => { t.style[prop] = val; });
        force();
      };
      return (
        <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={360} title={`Styl pól (${targets.length})`} onReset={() => { targets.forEach(t => { t.style.borderWidth=''; t.style.borderColor=''; t.style.borderRadius=''; t.style.background=''; t.style.backgroundColor=''; t.style.padding=''; }); force(); }}>
          {targets.length === 0 ? (
            <div style={{ fontSize: 12, color: '#64748B', padding: 12, background: '#F8FAFC', borderRadius: 6 }}>
              Nie znaleziono pól w tym formularzu.
            </div>
          ) : (
            <>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Grubość ramki</div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 14 }}>
                <NumberInputV2 value={sampleBw} min={0} max={12} step={1} width={100}
                  onChange={v => { applyAll('borderWidth', v + 'px'); applyAll('borderStyle', 'solid'); }}/>
                <SliderV2 value={Math.min(sampleBw, 12)} min={0} max={12} step={1}
                  onChange={v => { applyAll('borderWidth', v + 'px'); applyAll('borderStyle', 'solid'); }}/>
              </div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Kolor ramki</div>
              <div style={{ marginBottom: 14 }}>
                <ColorSwatches current={sampleBc} onPick={v => applyAll('borderColor', v)}/>
              </div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Zaokrąglenie rogów</div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 14 }}>
                <NumberInputV2 value={sampleBr} min={0} max={40} step={1} width={100}
                  onChange={v => applyAll('borderRadius', v + 'px')}/>
                <SliderV2 value={Math.min(sampleBr, 40)} min={0} max={40} step={1}
                  onChange={v => applyAll('borderRadius', v + 'px')}/>
              </div>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Tło pól</div>
              <ColorSwatches current={sampleBg} onPick={v => applyAll('backgroundColor', v)}/>
              <div style={{ marginTop: 14, paddingTop: 10, borderTop: '1px solid #E2E8F0', fontSize: 11, color: '#64748B' }}>
                Zmiany dotyczą wszystkich pól w tym formularzu naraz.
              </div>
            </>
          )}
        </SubPanelImpl>
      );
    })()}

    {expanded === 'icon' && (() => {
      const circle = el;
      // 24 ikon SVG + 10 cyfr/liter
      const ICONS = [
        { id: 'num-1', label: '1', content: '1', font: true },
        { id: 'num-2', label: '2', content: '2', font: true },
        { id: 'num-3', label: '3', content: '3', font: true },
        { id: 'num-4', label: '4', content: '4', font: true },
        { id: 'num-5', label: '5', content: '5', font: true },
        { id: 'num-6', label: '6', content: '6', font: true },
        { id: 'check', label: 'Check', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>' },
        { id: 'star', label: 'Gwiazda', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3 7h7l-6 5 2 8-6-4-6 4 2-8-6-5h7z"/></svg>' },
        { id: 'heart', label: 'Serce', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 21s-7-4.5-9.5-9A5.5 5.5 0 0112 6a5.5 5.5 0 019.5 6c-2.5 4.5-9.5 9-9.5 9z"/></svg>' },
        { id: 'coffee', label: 'Kawa', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 8h13v5a5 5 0 01-5 5H9a5 5 0 01-5-5V8zM17 10h2a2 2 0 110 4h-2"/></svg>' },
        { id: 'phone', label: 'Telefon', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014 2h3a2 2 0 012 1.7c.1.9.3 1.8.6 2.6a2 2 0 01-.5 2L8 9.5a16 16 0 006 6l1.2-1.2a2 2 0 012-.5c.8.3 1.7.5 2.6.6A2 2 0 0122 16.9z"/></svg>' },
        { id: 'mail', label: 'Mail', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 6L2 7"/></svg>' },
        { id: 'home', label: 'Dom', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 11l9-8 9 8v9a2 2 0 01-2 2h-4v-7h-6v7H5a2 2 0 01-2-2z"/></svg>' },
        { id: 'bell', label: 'Dzwonek', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 8a6 6 0 00-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 01-3.4 0"/></svg>' },
        { id: 'zap', label: 'Błyskawica', svg: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L3 14h7l-1 8 10-12h-7z"/></svg>' },
        { id: 'shield', label: 'Tarcza', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l8 4v6c0 5-3.5 9-8 10-4.5-1-8-5-8-10V6z"/></svg>' },
        { id: 'clock', label: 'Zegar', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2" stroke-linecap="round"/></svg>' },
        { id: 'user', label: 'Osoba', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a6 6 0 016-6h4a6 6 0 016 6v2"/></svg>' },
        { id: 'users', label: 'Ludzie', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M2 21v-2a5 5 0 015-5h4a5 5 0 015 5v2M16 14a4 4 0 014 4v3"/></svg>' },
        { id: 'gift', label: 'Prezent', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="8" width="18" height="13" rx="1"/><path d="M3 12h18M12 8v13M8 8a2 2 0 010-4c2 0 4 4 4 4s2-4 4-4a2 2 0 010 4"/></svg>' },
        { id: 'map', label: 'Pinezka', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s-7-7-7-12a7 7 0 0114 0c0 5-7 12-7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>' },
        { id: 'leaf', label: 'Liść', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M21 3C13 3 5 10 5 18c0 2 1 3 1 3s1-8 7-11c6-3 8-7 8-7z"/><path d="M6 21c5-4 11-6 15-6"/></svg>' },
        { id: 'camera', label: 'Aparat', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>' },
        { id: 'book', label: 'Książka', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20V2H6.5A2.5 2.5 0 004 4.5zM4 19.5V22h16"/></svg>' },
        { id: 'pencil', label: 'Ołówek', svg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 20h9M16.5 3.5a2 2 0 013 3L7 19l-4 1 1-4z"/></svg>' },
      ];
      const setIcon = (icon) => {
        // Zachowaj styl circle: kolor, rozmiar, tło — zmień tylko zawartość
        if (icon.font) {
          circle.innerHTML = icon.content;
          circle.style.fontFamily = '';
          circle.style.fontSize = '';
        } else {
          circle.innerHTML = icon.svg;
          const svg = circle.querySelector('svg');
          if (svg) {
            const size = Math.max(16, Math.min(parseInt(cs.width) || 64, parseInt(cs.height) || 64) * 0.5);
            svg.setAttribute('width', size);
            svg.setAttribute('height', size);
          }
        }
        circle.dataset.infographicIcon = icon.id;
        force();
      };
      const currentIconId = circle.dataset.infographicIcon || null;
      return (
        <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={360} title="Ikona lub cyfra"
          onReset={() => { circle.innerHTML = '1'; delete circle.dataset.infographicIcon; force(); }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Cyfry</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 6, marginBottom: 14 }}>
            {ICONS.filter(i => i.font).map(ic => (
              <button key={ic.id} onClick={() => setIcon(ic)}
                style={{
                  aspectRatio: '1', borderRadius: 8,
                  border: currentIconId === ic.id ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  outline: currentIconId === ic.id ? '2px solid #0F172A' : 'none', outlineOffset: 1,
                  background: '#fff', cursor: 'pointer',
                  fontFamily: 'Fraunces, serif', fontSize: 18, fontWeight: 600, color: '#0F172A',
                }}>{ic.content}</button>
            ))}
          </div>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>Ikony</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 6 }}>
            {ICONS.filter(i => !i.font).map(ic => (
              <button key={ic.id} onClick={() => setIcon(ic)} title={ic.label}
                style={{
                  aspectRatio: '1', borderRadius: 8,
                  border: currentIconId === ic.id ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  outline: currentIconId === ic.id ? '2px solid #0F172A' : 'none', outlineOffset: 1,
                  background: '#fff', cursor: 'pointer',
                  display: 'grid', placeItems: 'center', color: '#0F172A',
                }}>
                <span style={{ display: 'grid', placeItems: 'center', width: 20, height: 20 }}
                  dangerouslySetInnerHTML={{ __html: ic.svg.replace('<svg ', '<svg width="20" height="20" ') }}/>
              </button>
            ))}
          </div>
          <div style={{ fontSize: 11, color: '#64748B', marginTop: 12, padding: 10, background: '#F8FAFC', borderRadius: 6 }}>
            Ikona dziedziczy kolor z kółka (<code>currentColor</code>). Żeby zmienić kolor ikony — zmień kolor wypełnienia kółka.
          </div>
        </SubPanelImpl>
      );
    })()}

    {expanded === 'lineStyle' && (() => {
      const line = el;
      const STYLES = [
        { id: 'solid', label: 'Ciągła', apply: () => { line.style.backgroundImage = ''; line.style.background = bgColor; } },
        { id: 'dashed', label: 'Przerywana', apply: () => {
          const c = bgColor;
          line.style.backgroundImage = `linear-gradient(to right, ${c} 50%, transparent 50%)`;
          line.style.backgroundSize = '12px 100%';
          line.style.backgroundRepeat = 'repeat-x';
        } },
        { id: 'dotted', label: 'Kropkowana', apply: () => {
          const c = bgColor;
          line.style.backgroundImage = `radial-gradient(circle, ${c} 1.5px, transparent 2px)`;
          line.style.backgroundSize = '8px 100%';
          line.style.backgroundRepeat = 'repeat-x';
        } },
        { id: 'none', label: 'Brak', apply: () => { line.style.display = 'none'; } },
      ];
      const current = line.dataset.lineStyle || 'solid';
      return (
        <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={260} title="Styl łącznika"
          onReset={() => { line.style.backgroundImage=''; line.style.background=''; line.style.display=''; delete line.dataset.lineStyle; force(); }}>
          <div style={{ display: 'grid', gap: 6 }}>
            {STYLES.map(s => (
              <button key={s.id} onClick={() => { s.apply(); line.dataset.lineStyle = s.id; line.style.display = s.id === 'none' ? 'none' : ''; force(); }}
                style={{
                  padding: '10px 12px', borderRadius: 6,
                  border: current === s.id ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  background: '#fff', cursor: 'pointer', textAlign: 'left',
                  fontSize: 13, fontWeight: current === s.id ? 700 : 500, color: '#0F172A',
                }}>{s.label}</button>
            ))}
          </div>
        </SubPanelImpl>
      );
    })()}

    {expanded === 'gap' && (
      <SubPanelImpl el={el} pos={pos} onClose={() => setExpanded(null)} width={280} title="Odstęp między krokami"
        onReset={() => { el.style.gap=''; force(); }}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <SliderV2 value={parseInt(cs.gap) || 0} min={0} max={80} step={2} onChange={v => { el.style.gap = v + 'px'; force(); }}/>
          <NumberInputV2 value={parseInt(cs.gap) || 0} min={0} max={80} step={2} width={80} onChange={v => { el.style.gap = v + 'px'; force(); }}/>
        </div>
      </SubPanelImpl>
    )}

    </>
  );
}

function PadRow({ label, value, onChange, max = 100, step = 4 }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{ width: 70, fontSize: 11.5, color: '#475569', fontWeight: 500 }}>{label}</div>
      <SliderV2 value={Math.min(value, max)} min={0} max={max} step={step} onChange={onChange}/>
      <NumberInputV2 value={value} min={0} max={max} step={step} onChange={onChange} width={84}/>
    </div>
  );
}

export { UniToolbar };

// Ekspozycja helperów
(function exposeToolbarHelpers() {
  // Z tego scope'u nie mamy jeszcze dostępu do rgbToHex, ale to hoisted function
  // więc jest dostępne.
  try { window.rgbToHex = rgbToHex; } catch {}
  try { window.isLight = isLight; } catch {}
})();

// Suwak z propagation-stop — używany w filtrach obrazu
function FilterRow({ label, value, onChange, max = 100, unit = '%' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
      <div style={{ width: 86, fontSize: 11.5, color: '#475569', fontWeight: 500 }}>{label}</div>
      <SliderV2 value={value} min={0} max={max} step={1} onChange={onChange}/>
      <div style={{ width: 44, fontSize: 11.5, fontWeight: 600, color: '#0F172A', fontVariantNumeric: 'tabular-nums', textAlign: 'right' }}>
        {value}{unit}
      </div>
    </div>
  );
}

// CornerCut — ścięcie narożników (linia prosta), 4 checkboxy + suwak wielkości
function CornerCut({ el, onApply }) {
  const [state, setState] = React.useState(() => {
    // Wczytaj z data-atr jeśli jest
    const saved = el.dataset.cornerCut;
    if (saved) {
      try { return JSON.parse(saved); } catch {}
    }
    return { tl: false, tr: false, bl: false, br: false, size: 20 };
  });

  const apply = (next) => {
    setState(next);
    el.dataset.cornerCut = JSON.stringify(next);
    const { tl, tr, bl, br, size } = next;
    if (!tl && !tr && !bl && !br) {
      el.style.clipPath = '';
      onApply?.();
      return;
    }
    const s = size;
    // Polygon obchodzi prostokąt clockwise od top-left
    const points = [];
    // TL corner
    if (tl) { points.push(`0 ${s}%`); points.push(`${s}% 0`); }
    else    { points.push(`0 0`); }
    // TR corner
    if (tr) { points.push(`${100-s}% 0`); points.push(`100% ${s}%`); }
    else    { points.push(`100% 0`); }
    // BR corner
    if (br) { points.push(`100% ${100-s}%`); points.push(`${100-s}% 100%`); }
    else    { points.push(`100% 100%`); }
    // BL corner
    if (bl) { points.push(`${s}% 100%`); points.push(`0 ${100-s}%`); }
    else    { points.push(`0 100%`); }
    el.style.clipPath = `polygon(${points.join(', ')})`;
    onApply?.();
  };

  const Cb = ({ on, onClick, label }) => (
    <button onMouseDown={e => e.preventDefault()} onClick={onClick}
      style={{
        flex: 1, padding: '8px 6px',
        border: on ? '2px solid #0F172A' : '1px solid #E2E8F0',
        background: on ? '#0F172A' : '#fff',
        color: on ? '#fff' : '#334155',
        cursor: 'pointer', borderRadius: 6,
        fontSize: 10, fontWeight: 600, fontFamily: 'inherit',
      }}>{label}</button>
  );

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4, marginBottom: 10 }}>
        <Cb on={state.tl} onClick={() => apply({ ...state, tl: !state.tl })} label="↖ L-górny"/>
        <Cb on={state.tr} onClick={() => apply({ ...state, tr: !state.tr })} label="↗ P-górny"/>
        <Cb on={state.bl} onClick={() => apply({ ...state, bl: !state.bl })} label="↙ L-dolny"/>
        <Cb on={state.br} onClick={() => apply({ ...state, br: !state.br })} label="↘ P-dolny"/>
      </div>
      <FilterRow label="Wielkość" value={state.size} max={50} unit="%"
        onChange={v => apply({ ...state, size: v })}/>
    </div>
  );
}

// ====== BG EDITOR — solid / gradient ======
function BgEditor({ el, kind, onChange }) {
  // Parsuj aktualny background — rozpoznaj gradient/solid/image
  const parseBg = () => {
    // Najpierw sprawdź layer (nowy model dla sekcji)
    const layer = el.querySelector ? el.querySelector(':scope > [data-bg-layer="1"]') : null;
    if (layer) {
      const bgStr = layer.style.backgroundImage || '';
      const urlMatch = bgStr.match(/url\(["']?([^"')]+)["']?\)/);
      if (urlMatch) {
        return {
          mode: 'image',
          url: urlMatch[1],
          overlay: parseFloat(el.dataset.bgOverlay || '0') || 0,
          blur: 0,
          fit: el.dataset.bgFit || 'cover',
        };
      }
    }
    const inlineImg = el.style.backgroundImage || '';
    const inlineBg = el.style.background || '';
    const bgStr = inlineImg || inlineBg;
    const bgColor = window.getComputedStyle(el).backgroundColor;
    // Url bezpośrednio na sekcji (stary model) — migruj przy wyborze
    const urlMatch = bgStr.match(/url\(["']?([^"')]+)["']?\)/);
    if (urlMatch && !bgStr.match(/linear-gradient\(\s*\d/)) {
      return { mode: 'image', url: urlMatch[1], overlay: 0, blur: 0, fit: 'cover' };
    }
    const gradMatch = bgStr.match(/linear-gradient\(([^)]+)\)/);
    if (gradMatch) {
      const parts = splitTopLevel(gradMatch[1]);
      let angle = '135deg';
      let c1 = '#A8D5BA', c2 = '#6FAE8C';
      if (parts[0] && (parts[0].includes('deg') || parts[0].startsWith('to '))) {
        angle = parts[0].trim();
        c1 = stripStop(parts[1] || c1);
        c2 = stripStop(parts[parts.length - 1] || c2);
      } else {
        c1 = stripStop(parts[0] || c1);
        c2 = stripStop(parts[parts.length - 1] || c2);
      }
      return { mode: 'gradient', angle, c1, c2 };
    }
    return { mode: 'solid', solid: rgbToHex(bgColor) };
  };

  const [state, setState] = React.useState(parseBg);
  const [savedPresets, setSavedPresets] = React.useState(() => {
    try { return JSON.parse(localStorage.getItem('miet_grad_presets') || '[]'); } catch { return []; }
  });

  const persistPresets = (list) => {
    setSavedPresets(list);
    try { localStorage.setItem('miet_grad_presets', JSON.stringify(list)); } catch {}
  };

  const applySolid = (val) => {
    // Usuń warstwę tła (jeśli była)
    const layer = el.querySelector ? el.querySelector(':scope > [data-bg-layer="1"]') : null;
    if (layer) layer.remove();
    delete el.dataset.bgMode;
    delete el.dataset.bgUrl;
    delete el.dataset.bgOverlay;
    delete el.dataset.bgFit;
    // Reset longhand + shorthand, potem ustawiamy kolor
    el.style.backgroundImage = 'none';
    el.style.setProperty('background-image', 'none', 'important');
    el.style.backgroundColor = val;
    el.style.setProperty('background-color', val, 'important');
    setState({ ...state, mode: 'solid', solid: val });
    onChange?.();
  };
  const applyGradient = (angle, c1, c2) => {
    const layer = el.querySelector ? el.querySelector(':scope > [data-bg-layer="1"]') : null;
    if (layer) layer.remove();
    delete el.dataset.bgMode;
    delete el.dataset.bgUrl;
    delete el.dataset.bgOverlay;
    delete el.dataset.bgFit;
    const val = `linear-gradient(${angle}, ${c1}, ${c2})`;
    // Czyścimy bgColor żeby gradient był widoczny
    el.style.backgroundColor = 'transparent';
    el.style.setProperty('background-color', 'transparent', 'important');
    el.style.backgroundImage = val;
    el.style.setProperty('background-image', val, 'important');
    setState({ mode: 'gradient', angle, c1, c2 });
    onChange?.();
  };

  const applyImage = (url, overlay = 0, blur = 0, fit = 'cover') => {
    // Użyjemy oddzielnej warstwy <div data-bg-layer> wewnątrz sekcji:
    //   - ona trzyma background-image + filter (filtry kolorów i rozmycie nie wpływają na tekst)
    //   - treść sekcji leży nad warstwą (position: relative, z-index: 1)
    // Dzięki temu filtry kolorów/rozmycie działają TYLKO na zdjęcie, nie na teksty.
    if (getComputedStyle(el).position === 'static') el.style.position = 'relative';

    // Upewnij się że warstwa istnieje
    let layer = el.querySelector(':scope > [data-bg-layer="1"]');
    if (!layer) {
      layer = document.createElement('div');
      layer.setAttribute('data-bg-layer', '1');
      layer.setAttribute('aria-hidden', 'true');
      layer.style.cssText = 'position:absolute;inset:0;z-index:0;pointer-events:none;';
      el.insertBefore(layer, el.firstChild);
      // Zapewnij że dzieci (poza layerem) są nad warstwą
      Array.from(el.children).forEach(ch => {
        if (ch !== layer && getComputedStyle(ch).position === 'static') {
          ch.style.position = 'relative';
          ch.style.zIndex = '1';
        }
      });
    }

    // Overlay (ciemny półprzezroczysty)
    const a = overlay;
    const bgImage = a > 0
      ? `linear-gradient(rgba(0,0,0,${a}), rgba(0,0,0,${a})), url("${url}")`
      : `url("${url}")`;
    layer.style.backgroundImage = bgImage;
    layer.style.backgroundSize = fit;
    layer.style.backgroundPosition = 'center';
    layer.style.backgroundRepeat = 'no-repeat';

    // Filtr (preset + adjust) zastosuj z dataset sekcji
    applyBgFilterToLayer();

    // Sekcja sama ma przeźroczyste tło (żeby layer było widać)
    el.style.backgroundColor = 'transparent';
    el.style.setProperty('background-color', 'transparent', 'important');
    el.style.backgroundImage = '';
    el.style.setProperty('background-image', 'none', 'important');

    el.dataset.bgMode = 'image';
    el.dataset.bgUrl = url;
    el.dataset.bgOverlay = String(overlay);
    el.dataset.bgFit = fit;

    setState({ mode: 'image', url, overlay, blur, fit });
    onChange?.();
  };

  // Zastosuj aktualnie zapisane filtry tła do warstwy (wywołują to zarówno applyImage jak i edycja filtrów)
  const applyBgFilterToLayer = () => {
    const layer = el.querySelector(':scope > [data-bg-layer="1"]');
    if (!layer) return;
    const BG_PRESETS_MAP = {
      none: '', bw: 'grayscale(1) contrast(1.05)',
      sepia: 'sepia(0.85) saturate(1.1) brightness(0.95)',
      vintage: 'sepia(0.5) contrast(0.9) brightness(1.05) saturate(1.2)',
      red: 'grayscale(1) sepia(1) hue-rotate(-30deg) saturate(4.5) brightness(0.95)',
      green: 'grayscale(1) sepia(1) hue-rotate(60deg) saturate(4) brightness(0.95)',
      blue: 'grayscale(1) sepia(1) hue-rotate(170deg) saturate(5) brightness(0.95)',
      violet: 'grayscale(1) sepia(1) hue-rotate(220deg) saturate(5) brightness(0.95)',
      cool: 'saturate(0.9) hue-rotate(-8deg)',
      warm: 'sepia(0.25) saturate(1.2) brightness(1.02)',
      drama: 'contrast(1.35) saturate(0.85) brightness(0.92)',
      bright: 'brightness(1.12) contrast(0.95) saturate(1.1)',
    };
    const pid = el.dataset.bgFilterPreset || 'none';
    const p = BG_PRESETS_MAP[pid] || '';
    let a = { brightness: 1, contrast: 1, blur: 0, saturate: 1, grayscale: 0 };
    try { a = { ...a, ...JSON.parse(el.dataset.bgFilterAdjust || '{}') }; } catch {}
    const adj = `brightness(${a.brightness}) contrast(${a.contrast}) blur(${a.blur}px) saturate(${a.saturate}) grayscale(${a.grayscale})`;
    layer.style.filter = (p ? p + ' ' : '') + adj;
  };

  const PRESET_GRADIENTS = [
    { n: 'Mięta', a: '135deg', c1: '#A8D5BA', c2: '#6FAE8C' },
    { n: 'Terakota', a: '135deg', c1: '#FED7AA', c2: '#C2410C' },
    { n: 'Zachód', a: '135deg', c1: '#FDE68A', c2: '#F472B6' },
    { n: 'Ocean', a: '135deg', c1: '#BFDBFE', c2: '#1E40AF' },
    { n: 'Kremowy', a: '180deg', c1: '#FAF6EF', c2: '#E9DBC2' },
    { n: 'Noc', a: '135deg', c1: '#1E293B', c2: '#0F172A' },
  ];

  const ANGLES = [
    { deg: '0deg', icon: '↑' },
    { deg: '45deg', icon: '↗' },
    { deg: '90deg', icon: '→' },
    { deg: '135deg', icon: '↘' },
    { deg: '180deg', icon: '↓' },
    { deg: '225deg', icon: '↙' },
    { deg: '270deg', icon: '←' },
    { deg: '315deg', icon: '↖' },
  ];

  const BRAND = [
    '#1F2937', '#475569', '#6FAE8C', '#A8D5BA',
    '#C2410C', '#FED7AA', '#FAF6EF', '#FFFFFF',
    '#1E40AF', '#BFDBFE', '#7C3AED', '#EC4899',
    '#FDE68A', '#10B981', '#F59E0B', '#0F172A',
  ];

  const allGradPresets = [...PRESET_GRADIENTS, ...savedPresets];
  const currentMatchesPreset = state.mode === 'gradient' && allGradPresets.some(p => p.a === state.angle && p.c1.toLowerCase() === state.c1.toLowerCase() && p.c2.toLowerCase() === state.c2.toLowerCase());

  return (
    <div>
      {/* Mode tabs */}
      <div style={{ display: 'inline-flex', background: '#F1F5F9', padding: 2, borderRadius: 7, gap: 1, marginBottom: 12, width: '100%' }}>
        {(kind === 'section' ? ['solid', 'gradient', 'image', 'filter'] : ['solid', 'gradient']).map(m => {
          // Filter dostępny tylko jeśli na sekcji JEST już zdjęcie (layer)
          const hasImageLayer = !!(el.querySelector && el.querySelector(':scope > [data-bg-layer="1"]'));
          const disabled = m === 'filter' && !hasImageLayer;
          return (
            <button key={m}
              disabled={disabled}
              onClick={() => {
                if (disabled) return;
                // Tylko zmień mode w state — NIE aplikuj jeszcze na sekcję.
                // Apply nastąpi kiedy user wybierze konkretny kolor/gradient/zdjęcie.
                setState(s => ({ ...s, mode: m }));
              }}
              title={disabled ? 'Najpierw wybierz zdjęcie w tle' : ''}
              style={{
                flex: 1, padding: '6px 6px', border: 'none',
                background: state.mode === m ? '#fff' : 'transparent',
                borderRadius: 5, cursor: disabled ? 'not-allowed' : 'pointer',
                fontFamily: 'inherit', fontSize: 11, fontWeight: state.mode === m ? 600 : 500,
                color: disabled ? '#CBD5E1' : (state.mode === m ? '#0F172A' : '#64748B'),
                boxShadow: state.mode === m ? '0 1px 2px rgba(0,0,0,.06)' : 'none',
                opacity: disabled ? 0.55 : 1,
              }}>{m === 'solid' ? 'Kolor' : m === 'gradient' ? 'Gradient' : m === 'image' ? 'Zdjęcie' : 'Filtry'}</button>
          );
        })}
      </div>

      {state.mode === 'solid' && (
        <SolidPicker
          value={state.solid}
          brand={BRAND}
          onApply={applySolid}
        />
      )}

      {state.mode === 'gradient' && (
        <>
          {/* Preview */}
          <div style={{
            height: 48, borderRadius: 8,
            background: `linear-gradient(${state.angle}, ${state.c1}, ${state.c2})`,
            border: '1px solid #E2E8F0', marginBottom: 10,
          }}/>

          {/* Presety */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5 }}>Presety</div>
            {!currentMatchesPreset && (
              <button
                onClick={() => persistPresets([...savedPresets, { n: 'Mój ' + (savedPresets.length + 1), a: state.angle, c1: state.c1, c2: state.c2 }])}
                style={{
                  fontSize: 10, padding: '2px 7px', border: '1px solid #E2E8F0',
                  background: '#fff', cursor: 'pointer', borderRadius: 5,
                  fontFamily: 'inherit', fontWeight: 600, color: '#475569',
                }}>+ Zapisz</button>
            )}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 5, marginBottom: 10 }}>
            {allGradPresets.map((p, i) => {
              const active = state.angle === p.a && state.c1.toLowerCase() === p.c1.toLowerCase() && state.c2.toLowerCase() === p.c2.toLowerCase();
              return (
                <button key={p.n + i}
                  onClick={() => applyGradient(p.a, p.c1, p.c2)}
                  title={p.n}
                  style={{
                    height: 28, border: active ? '2px solid #0F172A' : '1px solid #E2E8F0',
                    background: `linear-gradient(${p.a}, ${p.c1}, ${p.c2})`,
                    borderRadius: 6, cursor: 'pointer',
                  }}/>
              );
            })}
          </div>

          {/* Color 1 */}
          <ColorRow label="Kolor 1" value={state.c1} brand={BRAND}
            onChange={c => applyGradient(state.angle, c, state.c2)} />
          {/* Color 2 */}
          <ColorRow label="Kolor 2" value={state.c2} brand={BRAND}
            onChange={c => applyGradient(state.angle, state.c1, c)} />

          {/* Angle */}
          <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 5, marginTop: 4 }}>Kierunek</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 4 }}>
            {ANGLES.map(a => (
              <button key={a.deg}
                onClick={() => applyGradient(a.deg, state.c1, state.c2)}
                style={{
                  height: 28, border: state.angle === a.deg ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  background: '#fff', cursor: 'pointer', borderRadius: 6,
                  fontSize: 13, fontWeight: 700, fontFamily: 'inherit',
                }}>{a.icon}</button>
            ))}
          </div>
        </>
      )}

      {state.mode === 'image' && (
        <ImageBgPanel state={state} applyImage={applyImage}/>
      )}

      {state.mode === 'filter' && (
        <BgFilterPanel el={el} applyBgFilterToLayer={applyBgFilterToLayer} onChange={onChange}/>
      )}
    </div>
  );
}

// Panel dla tła typu image — osobny komponent żeby hooki działały
function ImageBgPanel({ state, applyImage }) {
  const lib = (window.PHOTO_LIBRARY && window.PHOTO_LIBRARY.Wnętrze ? window.PHOTO_LIBRARY : null);
  const categories = lib ? Object.keys(lib) : [];
  const [cat, setCat] = React.useState(categories[0] || 'Wnętrze');
  const photos = lib ? (lib[cat] || []) : [];
  const fileInputRef = React.useRef(null);
  const onUpload = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = (ev) => applyImage(ev.target.result, state.overlay, 0, state.fit);
    reader.readAsDataURL(f);
  };
  return (
    <>
      {/* Biblioteka miniatur — od razu widoczna (większe) */}
      {lib && (
        <>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5 }}>Biblioteka zdjęć</div>
            <button onClick={() => fileInputRef.current?.click()}
              style={{
                fontSize: 10.5, padding: '3px 9px', border: '1px solid #E2E8F0',
                background: '#fff', cursor: 'pointer', borderRadius: 5,
                fontFamily: 'inherit', fontWeight: 600, color: '#475569',
              }}>+ Wgraj</button>
            <input ref={fileInputRef} type="file" accept="image/*" onChange={onUpload} style={{ display: 'none' }}/>
          </div>
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 8 }}>
            {categories.map(c => (
              <button key={c} onClick={() => setCat(c)}
                style={{
                  padding: '4px 10px', border: cat === c ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  background: cat === c ? '#F1F5F9' : '#fff',
                  borderRadius: 999, fontSize: 10.5, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
                }}>{c}</button>
            ))}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6, marginBottom: 14, maxHeight: 240, overflowY: 'auto' }}>
            {photos.map(url => (
              <button key={url} onClick={() => applyImage(url, state.overlay, 0, state.fit)}
                style={{
                  aspectRatio: '4/3', backgroundImage: `url("${url}")`,
                  backgroundSize: 'cover', backgroundPosition: 'center',
                  border: state.url === url ? '3px solid #0F172A' : '1px solid #E2E8F0',
                  borderRadius: 6, cursor: 'pointer', padding: 0,
                }}/>
            ))}
          </div>
        </>
      )}

      {/* Aktualnie wybrane */}
      {state.url && (
        <>
          <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Aktualnie</div>
          <div style={{
            height: 80, borderRadius: 8, marginBottom: 12,
            background: state.overlay > 0
              ? `linear-gradient(rgba(0,0,0,${state.overlay}), rgba(0,0,0,${state.overlay})), url("${state.url}") center/cover`
              : `url("${state.url}") center/cover`,
            border: '1px solid #E2E8F0',
          }}/>

          <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Przyciemnienie</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <SliderV2 value={Math.round(state.overlay * 100)} min={0} max={85} step={5}
              onChange={v => applyImage(state.url, v / 100, 0, state.fit)}/>
            <div style={{ width: 40, fontSize: 11, fontWeight: 600, color: '#0F172A', textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>
              {Math.round(state.overlay * 100)}%
            </div>
          </div>

          <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 6 }}>Dopasowanie</div>
          <div style={{ display: 'flex', gap: 4 }}>
            {[
              { v: 'cover', l: 'Wypełnij' },
              { v: 'contain', l: 'Zmieść' },
              { v: 'auto', l: 'Oryginalny' },
            ].map(f => (
              <button key={f.v} onClick={() => applyImage(state.url, state.overlay, 0, f.v)}
                style={{
                  flex: 1, padding: '6px 8px',
                  border: state.fit === f.v ? '2px solid #0F172A' : '1px solid #E2E8F0',
                  background: '#fff', cursor: 'pointer', borderRadius: 6,
                  fontSize: 11, fontWeight: 600, fontFamily: 'inherit',
                }}>{f.l}</button>
            ))}
          </div>
        </>
      )}
    </>
  );
}

// BgFilterPanel — filtry dla tła-zdjęcia sekcji (ten sam układ co dla obrazków)
function BgFilterPanel({ el, applyBgFilterToLayer, onChange }) {
  const PRESETS = [
    { id: 'none', l: 'Oryginał' },
    { id: 'bw', l: 'B&W' },
    { id: 'sepia', l: 'Sepia' },
    { id: 'vintage', l: 'Vintage' },
    { id: 'red', l: 'Czerwień' },
    { id: 'green', l: 'Zieleń' },
    { id: 'blue', l: 'Niebieski' },
    { id: 'violet', l: 'Fiolet' },
    { id: 'cool', l: 'Chłód' },
    { id: 'warm', l: 'Ciepło' },
    { id: 'drama', l: 'Dramat' },
    { id: 'bright', l: 'Jasne' },
  ];
  const [, setTick] = React.useState(0);
  const force = () => { setTick(x => x + 1); onChange?.(); };
  const presetId = el.dataset.bgFilterPreset || 'none';
  const adjust = (() => {
    try { return { brightness: 1, contrast: 1, blur: 0, saturate: 1, grayscale: 0, ...JSON.parse(el.dataset.bgFilterAdjust || '{}') }; }
    catch { return { brightness: 1, contrast: 1, blur: 0, saturate: 1, grayscale: 0 }; }
  })();
  const setPreset = (id) => { el.dataset.bgFilterPreset = id; applyBgFilterToLayer(); force(); };
  const setAdjust = (patch) => {
    const next = { ...adjust, ...patch };
    el.dataset.bgFilterAdjust = JSON.stringify(next);
    applyBgFilterToLayer();
    force();
  };
  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <div style={{
          width: 18, height: 18, borderRadius: '50%', background: '#0F172A', color: '#fff',
          fontSize: 10, fontWeight: 700, display: 'grid', placeItems: 'center',
        }}>1</div>
        <div style={{ fontSize: 10.5, fontWeight: 700, color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.5 }}>Wybierz kolor / nastrój</div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 6, marginBottom: 14 }}>
        {PRESETS.map(p => (
          <button key={p.id} onMouseDown={e => e.preventDefault()}
            onClick={() => setPreset(p.id)}
            style={{
              padding: '6px 4px',
              border: presetId === p.id ? '2px solid #0F172A' : '1px solid #E2E8F0',
              background: presetId === p.id ? '#F1F5F9' : '#fff',
              cursor: 'pointer', borderRadius: 6,
              fontSize: 10.5, fontWeight: 600, fontFamily: 'inherit',
            }}>{p.l}</button>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, paddingTop: 10, borderTop: '1px solid #E2E8F0' }}>
        <div style={{
          width: 18, height: 18, borderRadius: '50%', background: '#0F172A', color: '#fff',
          fontSize: 10, fontWeight: 700, display: 'grid', placeItems: 'center',
        }}>2</div>
        <div style={{ fontSize: 10.5, fontWeight: 700, color: '#0F172A', textTransform: 'uppercase', letterSpacing: 0.5 }}>Dostrój parametry</div>
      </div>
      <FilterRow label="Jasność" value={Math.round(adjust.brightness * 100)} max={200} unit="%"
        onChange={v => setAdjust({ brightness: v / 100 })}/>
      <FilterRow label="Kontrast" value={Math.round(adjust.contrast * 100)} max={200} unit="%"
        onChange={v => setAdjust({ contrast: v / 100 })}/>
      <FilterRow label="Nasycenie" value={Math.round(adjust.saturate * 100)} max={200} unit="%"
        onChange={v => setAdjust({ saturate: v / 100 })}/>
      <FilterRow label="Rozmycie" value={Math.round(adjust.blur)} max={20} unit="px"
        onChange={v => setAdjust({ blur: v })}/>
      <FilterRow label="Wyszarzenie" value={Math.round(adjust.grayscale * 100)} max={100} unit="%"
        onChange={v => setAdjust({ grayscale: v / 100 })}/>

      <button onMouseDown={e => e.preventDefault()}
        onClick={() => {
          delete el.dataset.bgFilterPreset;
          delete el.dataset.bgFilterAdjust;
          applyBgFilterToLayer();
          force();
        }}
        style={{
          marginTop: 10, width: '100%', padding: '7px 12px',
          border: '1px solid #E2E8F0', background: '#F8FAFC',
          borderRadius: 6, cursor: 'pointer',
          fontSize: 11.5, fontWeight: 600, fontFamily: 'inherit', color: '#475569',
        }}>Wyczyść filtry</button>
    </>
  );
}
function splitTopLevel(s) {
  const out = []; let depth = 0; let cur = '';
  for (const ch of s) {
    if (ch === '(') depth++;
    else if (ch === ')') depth--;
    if (ch === ',' && depth === 0) { out.push(cur.trim()); cur = ''; }
    else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}
function stripStop(s) {
  return s.split(/\s+/)[0];
}
function rgbToHex(c) {
  if (!c) return '#FFFFFF';
  if (c.startsWith('#')) return c;
  if (c === 'transparent' || c === 'rgba(0, 0, 0, 0)') return '#FFFFFF';
  const m = c.match(/\d+/g);
  if (!m || m.length < 3) return '#FFFFFF';
  return '#' + m.slice(0,3).map(n => parseInt(n).toString(16).padStart(2,'0')).join('').toUpperCase();
}
function toHex(c) {
  if (!c) return '#000000';
  if (c.startsWith('#')) return c.length === 7 ? c.toUpperCase() : '#000000';
  return rgbToHex(c);
}
function isLight(hex) {
  if (!hex || !hex.startsWith('#') || hex.length !== 7) return true;
  const r = parseInt(hex.slice(1,3), 16);
  const g = parseInt(hex.slice(3,5), 16);
  const b = parseInt(hex.slice(5,7), 16);
  // perceptual luminance
  return (0.299*r + 0.587*g + 0.114*b) > 140;
}

// SolidPicker — paleta + plus + custom z OK
function SolidPicker({ value, brand, onApply }) {
  const [pickerOpen, setPickerOpen] = React.useState(false);
  const [draft, setDraft] = React.useState(toHex(value));
  const currentHex = toHex(value);
  const isCustomValue = currentHex && !brand.map(c => c.toUpperCase()).includes(currentHex);
  return (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 6, marginBottom: 10 }}>
        {brand.map(c => {
          const selected = currentHex === c.toUpperCase();
          return (
            <button key={c} onClick={() => onApply(c)} title={c}
              style={{
                width: '100%', aspectRatio: '1',
                background: c,
                border: c === '#FFFFFF' ? '1px solid #E2E8F0' : 'none',
                borderRadius: 8, cursor: 'pointer', padding: 0,
                outline: selected ? '2.5px solid #0F172A' : 'none',
                outlineOffset: selected ? 2 : 0,
                position: 'relative',
              }}/>
          );
        })}
        {/* Plus — wielokolorowy tło z plusem */}
        <button onClick={() => { setDraft(currentHex || '#6FAE8C'); setPickerOpen(true); }}
          title="Własny kolor"
          style={{
            width: '100%', aspectRatio: '1',
            // Conic-gradient w kółko — tęcza
            background: 'conic-gradient(from 180deg, #EF4444, #F59E0B, #FDE047, #10B981, #3B82F6, #8B5CF6, #EC4899, #EF4444)',
            border: 'none',
            borderRadius: 8, cursor: 'pointer',
            display: 'grid', placeItems: 'center',
            padding: 0, position: 'relative',
            outline: isCustomValue ? '2.5px solid #0F172A' : 'none',
            outlineOffset: isCustomValue ? 2 : 0,
          }}>
          <span style={{
            width: '60%', height: '60%', borderRadius: '50%',
            background: isCustomValue ? currentHex : '#fff',
            display: 'grid', placeItems: 'center',
            color: isCustomValue ? (isLight(currentHex) ? '#0F172A' : '#fff') : '#0F172A',
            fontSize: 16, fontWeight: 500, fontFamily: 'inherit',
            boxShadow: '0 0 0 1px rgba(0,0,0,.1)',
          }}>+</span>
        </button>
      </div>
      {pickerOpen && (
        <div style={{ marginTop: 10, padding: 10, border: '1px solid #E2E8F0', borderRadius: 8, background: '#F8FAFC' }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
            <input type="color" value={draft} onChange={e => setDraft(e.target.value)}
              style={{ width: 44, height: 36, borderRadius: 6, border: '1px solid #E2E8F0', cursor: 'pointer', padding: 2, background: '#fff' }}/>
            <input type="text" value={draft}
              onChange={e => setDraft(e.target.value)}
              style={{ flex: 1, padding: '8px 10px', border: '1px solid #E2E8F0', borderRadius: 6, fontSize: 12, fontFamily: 'ui-monospace, monospace', background: '#fff' }}/>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            <button onClick={() => setPickerOpen(false)}
              style={{ flex: 1, padding: '7px 10px', border: '1px solid #E2E8F0', background: '#fff', cursor: 'pointer', borderRadius: 6, fontSize: 12, fontWeight: 500, fontFamily: 'inherit', color: '#64748B' }}>
              Anuluj
            </button>
            <button onClick={() => { onApply(draft); setPickerOpen(false); }}
              style={{ flex: 1, padding: '7px 10px', border: 'none', background: '#0F172A', color: '#fff', cursor: 'pointer', borderRadius: 6, fontSize: 12, fontWeight: 600, fontFamily: 'inherit' }}>
              OK
            </button>
          </div>
        </div>
      )}
    </>
  );
}

// ColorRow — kwadracik koloru który po kliku otwiera mini-pickera (live update).
// Picker pozostaje otwarty przy live zmianie z <input type="color">.
// Zamyka się: klik w swatch, klik w tło (overlay), albo ponowny klik w kwadracik.
function ColorRow({ label, value, brand, onChange }) {
  // Inline style — etykieta + mini paleta + custom swatch (picker). Zawsze widoczne, bez rozwijania.
  const colorInputRef = React.useRef(null);
  const hex = toHex(value).toUpperCase();
  const isCustom = !brand.some(c => c.toUpperCase() === hex);
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: .5, marginBottom: 6 }}>{label}</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(10, 1fr)', gap: 4 }}>
        {brand.map(c => {
          const active = hex === c.toUpperCase();
          return (
            <button key={c} type="button" onClick={() => onChange(c)}
              style={{
                aspectRatio: '1 / 1', background: c,
                border: active ? '2px solid #0F172A' : (c === '#FFFFFF' ? '1px solid #E2E8F0' : 'none'),
                borderRadius: 5, cursor: 'pointer', padding: 0,
                boxShadow: active ? '0 0 0 2px #fff inset' : 'none',
              }}/>
          );
        })}
        {/* Custom color swatch — pokazuje aktualny custom, otwiera native color picker */}
        <button type="button" onClick={() => colorInputRef.current?.click()}
          title={isCustom ? hex : 'Wybierz własny kolor'}
          style={{
            aspectRatio: '1 / 1',
            background: isCustom
              ? value
              : 'conic-gradient(from 180deg, #EF4444, #F59E0B, #FDE047, #10B981, #3B82F6, #8B5CF6, #EC4899, #EF4444)',
            border: isCustom ? '2px solid #0F172A' : '1px solid #E2E8F0',
            borderRadius: 5, cursor: 'pointer', padding: 0,
            display: 'grid', placeItems: 'center',
            position: 'relative',
          }}>
          {!isCustom && (
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round" style={{ filter: 'drop-shadow(0 0 1px rgba(0,0,0,.5))' }}>
              <path d="M12 5v14M5 12h14"/>
            </svg>
          )}
          <input ref={colorInputRef} type="color" value={toHex(value)}
            onChange={e => onChange(e.target.value)}
            style={{ position: 'absolute', opacity: 0, pointerEvents: 'none', width: 0, height: 0 }}/>
        </button>
      </div>
    </div>
  );
}
