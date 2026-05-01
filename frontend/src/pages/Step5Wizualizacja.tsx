import React from "react";
import { useLabStore } from "@/store/labStore";
import { ImagePicker } from "@/components/wizualizacja/WizRender";
import { SECTION_RENDERERS, EditCtx as SREditCtx } from "@/components/shared/SectionRenderers";
import { WIZ_SECTION_RENDERERS, DeviceCtx } from "@/components/wizualizacja/WizRender";
import { DENSITY_SCALE } from "@/components/tresci/ContentRenderer";
import { WizBlocksModal, wizInsertBlockAfter } from "@/components/wizualizacja/WizBlocks";
import { UniToolbar, resolveClickTarget, detectElementType } from "@/components/wizualizacja/ElementToolbar";
import { WizAIPanel } from "@/components/wizualizacja/AiWizPanel";
import { openInfographicGallery } from "@/components/wizualizacja/UnsplashGallery";
import { TweakPanel, TWEAKS_DEFAULT } from "@/components/wizualizacja/TweakPanel";
// Wizualizacja — ekran 5. Pełny podgląd strony z device switcher, Tweaki.

// Tweaks (domyślne) — persist via __edit_mode_set_keys
const WIZ_TWEAKS_DEFAULT = /*EDITMODE-BEGIN*/{
  ...TWEAKS_DEFAULT,
}/*EDITMODE-END*/;

// Font pairs
const FONT_PAIRS = {
  'Fraunces + Inter': { h: 'Fraunces', b: 'Inter' },
  'Instrument Serif + Inter': { h: 'Instrument Serif', b: 'Inter' },
  'Playfair Display + Inter': { h: 'Playfair Display', b: 'Inter' },
  'DM Serif Display + Manrope': { h: 'DM Serif Display', b: 'Manrope' },
  'Space Grotesk + Inter': { h: 'Space Grotesk', b: 'Inter' },
  'Cormorant + Inter': { h: 'Cormorant Garamond', b: 'Inter' },
};

// Lab Creator: sections from store (single page, no multi-page)

function mapFromStore(s) {
  const slots = s.slots_json || {};
  return { id: s.id, code: s.block_code, label: slots.label || s.block_code, bg: slots.bg || null, fields: slots };
}

function makeWizTypo(pair, density) {
  const d = DENSITY_SCALE[density] || DENSITY_SCALE[3];
  const bodySize = d.bodySize;
  const sc = d.scale;
  return {
    headingFont: pair.h, bodyFont: pair.b,
    body: bodySize, lineHeight: d.lineHeight, spacing: d.spacing,
    eyebrow: Math.round(bodySize * 0.8),
    h3: Math.round(bodySize * sc * sc),
    h2: Math.round(bodySize * sc * sc * sc),
    h1: Math.round(bodySize * sc * sc * sc * sc),
    heading: pair.h,
  };
}

// Device dimensions (scaled down in fit)
const DEVICES = {
  desktop: { w: 1440, label: 'Desktop', icon: 'M2 4h20v12H2z M8 20h8 M10 16v4 M14 16v4' },
  tablet:  { w: 820,  label: 'Tablet',  icon: 'M5 2h14a1 1 0 011 1v18a1 1 0 01-1 1H5a1 1 0 01-1-1V3a1 1 0 011-1z M11 19h2' },
  mobile:  { w: 390,  label: 'Mobile',  icon: 'M7 2h10a1 1 0 011 1v18a1 1 0 01-1 1H7a1 1 0 01-1-1V3a1 1 0 011-1z M10 19h4' },
};

function _UnusedAIAssistant({ onClose, viewportEl }: { onClose: () => void; viewportEl: any }) {
  const [messages, setMessages] = React.useState([
    { role: 'ai', text: 'Cześć! Widzę Twoją stronę. Mogę przepisać sekcje, skrócić teksty, dopasować ton albo zasugerować zmiany. Co chcesz zrobić?' },
  ]);
  const [input, setInput] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const scrollRef = React.useRef(null);

  React.useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  const getContext = () => {
    if (!viewportEl) return '';
    // Wyciągnij strukturalny text z strony
    const sections = viewportEl.querySelectorAll('section, nav, footer');
    if (!sections.length) return viewportEl.innerText.slice(0, 3000);
    const out = [];
    sections.forEach((s, i) => {
      const txt = s.innerText.trim().replace(/\n{3,}/g, '\n\n');
      if (txt) out.push(`[Sekcja ${i + 1}]\n${txt}`);
    });
    return out.join('\n\n').slice(0, 4000);
  };

  const send = async () => {
    const msg = input.trim();
    if (!msg || loading) return;
    setInput('');
    setMessages(m => [...m, { role: 'user', text: msg }]);
    setLoading(true);
    try {
      const context = getContext();
      const prompt = `Jesteś asystentem edytorskim polskiego landing page kawiarni "Miętowa". Oto aktualna treść strony:\n\n${context}\n\nUżytkownik prosi: "${msg}"\n\nOdpowiedz po polsku, konkretnie. Jeśli proponujesz konkretne zmiany tekstu, zapisz je jasno (np. "Nagłówek → nowa wersja"). Bądź zwięzły (3–6 zdań lub bullety).`;
      const reply = await window.claude.complete(prompt);
      setMessages(m => [...m, { role: 'ai', text: reply.trim() }]);
    } catch (e) {
      setMessages(m => [...m, { role: 'ai', text: 'Błąd — spróbuj ponownie.', error: true }]);
    }
    setLoading(false);
  };

  const suggestions = [
    'Skróć sekcję hero',
    'Przepisz w cieplejszym tonie',
    'Dodaj konkret w sekcji Menu',
    'Zrób CTA mocniejsze',
  ];

  return (
    <div style={{
      position: 'fixed', top: 0, right: 0, bottom: 0, width: 420, zIndex: 360,
      background: '#fff', borderLeft: '1px solid #E2E8F0',
      boxShadow: '-10px 0 30px rgba(15,23,42,.08)',
      display: 'flex', flexDirection: 'column',
      fontFamily: 'Inter, sans-serif',
      animation: 'slideInRight .2s',
    }}>
      {/* Header */}
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 30, height: 30, borderRadius: 9,
          background: 'linear-gradient(135deg, #A8D5BA 0%, #6FAE8C 100%)',
          display: 'grid', placeItems: 'center', color: '#fff', fontSize: 15,
        }}>✨</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0F172A' }}>Asystent AI</div>
          <div style={{ fontSize: 11, color: '#64748B' }}>Widzi całą stronę — {activePageName()}</div>
        </div>
        <button onClick={onClose} style={{
          width: 30, height: 30, border: 'none', background: '#F1F5F9', borderRadius: 8, cursor: 'pointer', display: 'grid', placeItems: 'center',
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>
      {/* Messages */}
      <div ref={scrollRef} style={{ flex: 1, overflow: 'auto', padding: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%',
            background: m.role === 'user' ? '#0F172A' : '#F1F5F9',
            color: m.role === 'user' ? '#fff' : '#0F172A',
            padding: '10px 13px', borderRadius: 12,
            fontSize: 13, lineHeight: 1.5, whiteSpace: 'pre-wrap',
          }}>
            {m.text}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', padding: '10px 13px', background: '#F1F5F9', borderRadius: 12, fontSize: 13, color: '#64748B' }}>
            <span style={{ opacity: 0.6 }}>Myślę…</span>
          </div>
        )}
      </div>
      {/* Suggestions */}
      {messages.length === 1 && (
        <div style={{ padding: '0 18px 12px', display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {suggestions.map(s => (
            <button key={s} onClick={() => setInput(s)} style={{
              padding: '6px 10px', border: '1px solid #E2E8F0', background: '#fff',
              borderRadius: 999, fontSize: 11.5, color: '#334155', cursor: 'pointer', fontFamily: 'inherit',
            }}>{s}</button>
          ))}
        </div>
      )}
      {/* Input */}
      <div style={{ padding: '12px 18px 16px', borderTop: '1px solid #E2E8F0' }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
          <textarea
            value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Napisz co zmienić…" rows={1}
            style={{
              flex: 1, border: '1px solid #E2E8F0', borderRadius: 10,
              padding: '10px 12px', fontSize: 13, resize: 'none',
              fontFamily: 'inherit', outline: 'none', maxHeight: 120,
            }}/>
          <button onClick={send} disabled={loading || !input.trim()} style={{
            padding: '10px 14px', border: 'none',
            background: (loading || !input.trim()) ? '#E2E8F0' : '#0F172A',
            color: '#fff', borderRadius: 10, fontSize: 13, fontWeight: 600,
            cursor: (loading || !input.trim()) ? 'not-allowed' : 'pointer', fontFamily: 'inherit',
          }}>↑</button>
        </div>
      </div>
    </div>
  );
}
function activePageName() { return "Strona"; }

function _UnusedFormatToolbar({ toolbar, onClose }) {
  const el = toolbar.el;
  const [, force] = React.useReducer(x => x + 1, 0);

  const apply = (action) => {
    document.execCommand(action, false, null);
    force();
  };
  const setStyle = (prop, val) => {
    el.style[prop] = val;
    force();
  };
  const cs = window.getComputedStyle(el);

  const colors = ['#1F2937', '#6FAE8C', '#A8D5BA', '#C2410C', '#FAF6EF', '#ffffff'];
  const fonts = [
    { label: 'Nagłówkowy', val: "'Fraunces', serif" },
    { label: 'Tekstowy', val: "'Inter', sans-serif" },
    { label: 'Mono', val: "'JetBrains Mono', monospace" },
  ];

  // Pozycjonowanie
  const rect = el.getBoundingClientRect();
  const W = 520;
  let left = rect.left + rect.width / 2 - W / 2;
  let top = rect.bottom + 10;
  const margin = 12;
  if (left < margin) left = margin;
  if (left + W > window.innerWidth - margin) left = window.innerWidth - W - margin;
  if (top + 60 > window.innerHeight) top = rect.top - 60;

  const btnStyle = (active) => ({
    width: 30, height: 30, border: 'none',
    background: active ? '#0F172A' : 'transparent',
    color: active ? '#fff' : '#334155',
    borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 600,
    display: 'grid', placeItems: 'center', fontFamily: 'inherit',
  });

  const isBold = cs.fontWeight >= 600;
  const isItalic = cs.fontStyle === 'italic';
  const isUnderline = cs.textDecoration.includes('underline');
  const align = cs.textAlign;

  const Divider = () => <div style={{ width: 1, height: 20, background: '#E2E8F0', margin: '0 4px' }}/>;

  return (
    <div
      onMouseDown={e => e.preventDefault()}
      style={{
        position: 'fixed', left, top, zIndex: 350,
        background: '#fff', borderRadius: 10,
        boxShadow: '0 10px 30px rgba(15,23,42,.18), 0 0 0 1px rgba(15,23,42,.08)',
        padding: 6, fontFamily: 'Inter, sans-serif',
        display: 'inline-flex', alignItems: 'center', gap: 4,
        animation: 'popIn .12s',
      }}>
      {/* Font */}
      <select value={cs.fontFamily.includes('Fraunces') ? fonts[0].val : cs.fontFamily.includes('Mono') ? fonts[2].val : fonts[1].val}
        onChange={e => setStyle('fontFamily', e.target.value)}
        style={{ border: '1px solid #E2E8F0', padding: '5px 8px', borderRadius: 6, fontSize: 12, background: '#fff', fontFamily: 'inherit', cursor: 'pointer' }}>
        {fonts.map(f => <option key={f.val} value={f.val}>{f.label}</option>)}
      </select>
      {/* Rozmiar */}
      <div style={{ display: 'inline-flex', alignItems: 'center', border: '1px solid #E2E8F0', borderRadius: 6 }}>
        <button onClick={() => { const s = parseInt(cs.fontSize); setStyle('fontSize', (s - 2) + 'px'); }}
          style={{ width: 22, height: 26, border: 'none', background: 'transparent', cursor: 'pointer', fontSize: 14, color: '#64748B' }}>−</button>
        <div style={{ width: 28, textAlign: 'center', fontSize: 11, fontWeight: 600, color: '#334155' }}>{parseInt(cs.fontSize)}</div>
        <button onClick={() => { const s = parseInt(cs.fontSize); setStyle('fontSize', (s + 2) + 'px'); }}
          style={{ width: 22, height: 26, border: 'none', background: 'transparent', cursor: 'pointer', fontSize: 14, color: '#64748B' }}>+</button>
      </div>
      <Divider/>
      <button onClick={() => apply('bold')} style={btnStyle(isBold)} title="Bold"><b>B</b></button>
      <button onClick={() => apply('italic')} style={btnStyle(isItalic)} title="Italic"><i>I</i></button>
      <button onClick={() => apply('underline')} style={btnStyle(isUnderline)} title="Underline"><u>U</u></button>
      <Divider/>
      <button onClick={() => setStyle('textAlign', 'left')} style={btnStyle(align === 'left' || align === 'start')} title="Lewo">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/></svg>
      </button>
      <button onClick={() => setStyle('textAlign', 'center')} style={btnStyle(align === 'center')} title="Środek">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="10" x2="6" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="18" y1="18" x2="6" y2="18"/></svg>
      </button>
      <button onClick={() => setStyle('textAlign', 'right')} style={btnStyle(align === 'right' || align === 'end')} title="Prawo">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="21" y1="10" x2="7" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="21" y1="18" x2="7" y2="18"/></svg>
      </button>
      <Divider/>
      {/* Color swatches */}
      {colors.map(c => (
        <button key={c} onClick={() => setStyle('color', c)} title={c}
          style={{
            width: 22, height: 22, border: c === '#ffffff' ? '1px solid #E2E8F0' : 'none',
            background: c, borderRadius: '50%', cursor: 'pointer',
            outline: cs.color === c ? '2px solid #0F172A' : 'none', outlineOffset: 1,
          }}/>
      ))}
    </div>
  );
}

export default function Step5Wizualizacja() {
  const storeSections = useLabStore(s => s.sections);
  const updateSection = useLabStore(s => s.updateSection);
  const [tweaks, setTweaks] = React.useState(WIZ_TWEAKS_DEFAULT);
  const [device, setDevice] = React.useState<keyof typeof DEVICES>('desktop');
  const [tweaksOpen, setTweaksOpen] = React.useState(false);
  const [liveEdit, setLiveEdit] = React.useState(true);

  // ── Editing state for SectionRenderers ──
  const [wzSelected, setWzSelected] = React.useState(null);
  const [wzOverrides, setWzOverrides] = React.useState({});
  const [wzHovered, setWzHovered] = React.useState(null);
  const [wzContent, setWzContent] = React.useState(() => storeSections.map(mapFromStore));
  React.useEffect(() => { setWzContent(storeSections.map(mapFromStore)); }, [storeSections]);

  const wzGetOv = (sectionId, elId) => {
    const page = wzOverrides[sectionId] || {};
    return page[elId] || {};
  };
  const wzPatchOverride = (sectionId, elId, patch) => {
    setWzOverrides(prev => {
      const pageOv = prev[sectionId] || {};
      const elOv = pageOv[elId] || {};
      return { ...prev, [sectionId]: { ...pageOv, [elId]: { ...elOv, ...patch } } };
    });
  };
  const wzRemoveOverride = (sectionId, elId) => wzPatchOverride(sectionId, elId, { deleted: true });
  const wzCopyOverride = () => {};
  const wzUpdateSection = (id, patch) => {
    setWzContent(prev => prev.map(s => s.id === id ? { ...s, ...patch } : s));
  };
  const wzDuplicateSection = (id) => {
    setWzContent(prev => {
      const idx = prev.findIndex(s => s.id === id);
      if (idx < 0) return prev;
      const clone = { ...prev[idx], id: prev[idx].id + '-dup-' + Math.random().toString(36).slice(2, 6) };
      return [...prev.slice(0, idx + 1), clone, ...prev.slice(idx + 1)];
    });
  };
  const wzDeleteSection = (id) => setWzContent(prev => prev.filter(s => s.id !== id));
  const wzMoveSection = (id, dir) => {
    setWzContent(prev => {
      const idx = prev.findIndex(s => s.id === id);
      if (idx < 0) return prev;
      const target = dir === 'up' ? idx - 1 : idx + 1;
      if (target < 0 || target >= prev.length) return prev;
      const next = [...prev];
      [next[idx], next[target]] = [next[target], next[idx]];
      return next;
    });
  };
  const wzPushHistory = () => {};

  const wzHandleImageClick = (info) => {
    setPicker({
      current: info.current,
      category: 'Wnętrze',
      onPick: (url) => {
        // Update the section's image field in local state
        wzUpdateSection(info.sectionId, { fields: { ...(wzContent.find(s => s.id === info.sectionId)?.fields || {}), [info.field]: url } });
      },
    });
  };
  const wzEditCtx = {
    selected: wzSelected, select: setWzSelected,
    overrides: wzOverrides, getOv: wzGetOv,
    patchOverride: wzPatchOverride, removeOverride: wzRemoveOverride, copyOverride: wzCopyOverride,
    viewport: device, hoveredSection: wzHovered, setHoveredSection: setWzHovered,
    duplicateSection: wzDuplicateSection, deleteSection: wzDeleteSection, moveSection: wzMoveSection, pushHistory: wzPushHistory,
    onImageClick: wzHandleImageClick,
  };
  const hoverBtnStyle: React.CSSProperties = {
    border: 'none', background: 'transparent', color: '#fff', cursor: 'pointer',
    fontSize: 12, padding: '2px 5px', borderRadius: 4, lineHeight: 1, fontFamily: 'inherit',
  };
  const [fullscreen, setFullscreen] = React.useState(false);
  React.useEffect(() => {
    if (!fullscreen) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setFullscreen(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [fullscreen]);
  const [picker, setPicker] = React.useState(null);
  const [uniToolbar, setUniToolbar] = React.useState(null); // { el, kind }
  const [aiAssistOpen, setAiAssistOpen] = React.useState(false);
  const [dragMode, setDragMode] = React.useState(null); // {el} gdy aktywny
  const [editingEl, setEditingEl] = React.useState(null);
  const [blocksModal, setBlocksModal] = React.useState(null); // { afterEl }
  
  // activePageName removed — single page in Lab Creator
  const [published, setPublished] = React.useState(false);
  const [toast, setToast] = React.useState<{msg:string;icon?:string}|null>(null);
  const [editMode, setEditMode] = React.useState(false);
  // Synchronizuj klasę na body — CSS może reagować (np. hint na obrazach).
  React.useEffect(() => {
    document.body.classList.toggle('wiz-edit-on', editMode);
    return () => document.body.classList.remove('wiz-edit-on');
  }, [editMode]);
  const previewRef = React.useRef(null);
  const [previewScale, setPreviewScale] = React.useState(1);

  // Edit-mode plumbing
  React.useEffect(() => {
    const onMsg = (e) => {
      if (e.data?.type === '__activate_edit_mode') setEditMode(true);
      if (e.data?.type === '__deactivate_edit_mode') setEditMode(false);
    };
    window.addEventListener('message', onMsg);
    window.parent.postMessage({ type: '__edit_mode_available' }, '*');
    return () => window.removeEventListener('message', onMsg);
  }, []);

  // ===== NOWY jednolity system edycji =====
  // Reguły:
  //  - hover = outline (dashed mięta)
  //  - klik = ustaw element jako "zaznaczony" → pokaż UniToolbar z kontekstowymi kontrolkami
  //  - dblclick na tekst = tryb tekstowy (contentEditable)
  //  - toolbar → "Przesuń" = wchodzimy w dragMode, drag przesuwa element przez translate
  React.useEffect(() => {
    if (!liveEdit) return;
    const root = previewRef.current?.previousElementSibling;
    if (!root) return;

    // Expose helpers for ElementToolbar (uses window.* globals)
    (window as any).applyToSelectionOrEl = (el: HTMLElement, prop: string, val: string): boolean => {
      const sel = window.getSelection();
      if (sel && !sel.isCollapsed && el.contains(sel.anchorNode)) {
        try {
          const range = sel.getRangeAt(0);
          const span = document.createElement('span');
          span.style[prop as any] = val;
          range.surroundContents(span);
          return true;
        } catch { return false; }
      }
      return false;
    };
    (window as any).moveSection = (el: HTMLElement, dir: 'up' | 'down') => {
      const sectionEl = el.closest('[data-section-id]') as HTMLElement | null;
      if (!sectionEl) return;
      const id = sectionEl.dataset.sectionId;
      if (id) wzMoveSection(id, dir);
    };

    const EDITABLE_TEXT_TAGS = new Set(['H1','H2','H3','H4','H5','H6','P','SPAN','A','LI','STRONG','EM','DIV','BLOCKQUOTE','Q','CITE','LABEL','SMALL','TIME','DT','DD']);
    const isTextOnly = (el) => {
      if (!el.childNodes.length) return true;
      for (const c of el.childNodes) {
        if (c.nodeType === 1 && !['SPAN','STRONG','EM','B','I','BR'].includes(c.tagName)) return false;
      }
      return true;
    };

    const clearHover = () => {
      root.querySelectorAll('[data-wiz-hover]').forEach(el => {
        el.style.outline = '';
        el.style.outlineOffset = '';
        delete el.dataset.wizHover;
      });
    };

    const onHover = (e) => {
      if (dragMode) return;
      let t = e.target;
      if (t.closest('[data-no-edit]')) return;
      t = resolveClickTarget?.(t) || t;
      // Wybieralne: teksty, inputy, buttony, sekcje, obrazy
      const kind = detectElementType(t);
      if (!kind) return;
      if (kind === 'text' && !EDITABLE_TEXT_TAGS.has(t.tagName)) return;
      if (kind === 'text' && !isTextOnly(t)) return;

      clearHover();
      t.dataset.wizHover = kind;
      const col = kind === 'section' ? 'rgba(99,102,241,.5)' : 'rgba(168,213,186,.8)';
      t.style.outline = `2px dashed ${col}`;
      t.style.outlineOffset = kind === 'section' ? '-4px' : '2px';
    };
    const onLeave = (e) => {
      // Tylko hover outline — NIE ruszamy wizSelected
      let t = e.target;
      t = resolveClickTarget?.(t) || t;
      if (t.dataset?.wizHover && !t.dataset?.wizSelected) {
        t.style.outline = '';
        t.style.outlineOffset = '';
        delete t.dataset.wizHover;
      } else if (t.dataset?.wizHover && t.dataset?.wizSelected) {
        // zachowaj selected outline
        t.style.outline = '2px solid #6366F1';
        delete t.dataset.wizHover;
      }
    };

    const onClick = (e) => {
      let t = e.target;
      if (t.closest('[data-no-edit]')) return;
      t = resolveClickTarget?.(t) || t;
      const kind = detectElementType(t);
      if (!kind) return;
      if (kind === 'text' && !EDITABLE_TEXT_TAGS.has(t.tagName)) return;
      if (kind === 'text' && !isTextOnly(t)) return;
      // Linki: blokuj nawigację
      if (t.tagName === 'A' || t.closest('a')) e.preventDefault();
      e.stopPropagation();
      setUniToolbar({ el: t, kind });
      // Zaznaczenie
      root.querySelectorAll('[data-wiz-selected]').forEach(el => {
        el.style.outline = '';
        el.style.outlineOffset = '';
        delete el.dataset.wizSelected;
      });
      t.dataset.wizSelected = '1';
      t.style.outline = '2px solid #6366F1';
      t.style.outlineOffset = kind === 'section' ? '-4px' : '2px';
    };

    const onDbl = (e) => {
      const t = e.target;
      const kind = detectElementType(t);
      if (kind !== 'text' && kind !== 'button') return;
      if (!isTextOnly(t)) return;
      e.preventDefault();
      e.stopPropagation();
      t.contentEditable = 'true';
      t.style.outline = '2px solid #10B981';
      t.style.background = 'rgba(168,213,186,.15)';
      t.focus();
      const range = document.createRange();
      range.selectNodeContents(t);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      setEditingEl(t);
      const orig = t.innerText;
      const finish = () => {
        t.contentEditable = 'false';
        t.style.outline = '';
        t.style.background = '';
        t.removeEventListener('blur', finish);
        t.removeEventListener('keydown', onKey);
        setEditingEl(null);
      };
      const onKey = (ev) => {
        if (ev.key === 'Escape') { ev.preventDefault(); t.innerText = orig; t.blur(); }
      };
      t.addEventListener('blur', finish);
      t.addEventListener('keydown', onKey);
    };

    root.addEventListener('mouseover', onHover, true);
    root.addEventListener('mouseout', onLeave, true);
    root.addEventListener('click', onClick, true);
    root.addEventListener('dblclick', onDbl, true);
    return () => {
      root.removeEventListener('mouseover', onHover, true);
      root.removeEventListener('mouseout', onLeave, true);
      root.removeEventListener('click', onClick, true);
      root.removeEventListener('dblclick', onDbl, true);
      clearHover();
      delete (window as any).applyToSelectionOrEl;
      delete (window as any).moveSection;
    };
  }, [liveEdit, device, dragMode, wzContent]);

  // ===== DRAG MODE — dla sekcji: auto-reorder przez DOM swap =====
  React.useEffect(() => {
    if (!dragMode) return;
    const el = dragMode.el;
    const isSection = ['SECTION', 'NAV', 'FOOTER', 'HEADER', 'ARTICLE'].includes(el.tagName);
    el.style.cursor = 'grabbing';
    el.style.outline = '2px dashed #F59E0B';
    el.style.outlineOffset = '-4px';
    el.style.transition = 'transform .15s';

    let startX = 0, startY = 0, dragging = false;
    let ox = 0, oy = 0;
    const cs = window.getComputedStyle(el);
    const m = cs.transform.match(/matrix\(([^)]+)\)/);
    if (m) { const p = m[1].split(',').map(Number); if (p.length === 6) { ox = p[4]; oy = p[5]; } }

    const onDown = (e) => {
      dragging = true;
      startX = e.clientX;
      startY = e.clientY;
      e.preventDefault();
      e.stopPropagation();
    };
    const onMove = (e) => {
      if (!dragging) return;
      const dx = (e.clientX - startX) / previewScale;
      const dy = (e.clientY - startY) / previewScale;
      el.style.transform = `translate(${ox + dx}px, ${oy + dy}px)`;

      if (isSection) {
        // Auto-reorder: sprawdź czy punkt środka sekcji przekroczył 40% wysokości sąsiedniej
        const rect = el.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        const siblings = Array.from(el.parentElement.children).filter(s => s !== el);
        for (const sib of siblings) {
          const sr = sib.getBoundingClientRect();
          const threshold = sr.top + sr.height * 0.4;
          const thresholdEnd = sr.top + sr.height * 0.6;
          if (dy < 0 && midY < threshold && sib.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) {
            el.parentElement.insertBefore(el, sib);
            startY = e.clientY; ox = 0; oy = 0;
            el.style.transform = 'translate(0,0)';
            return;
          }
          if (dy > 0 && midY > thresholdEnd && el.compareDocumentPosition(sib) & Node.DOCUMENT_POSITION_FOLLOWING) {
            el.parentElement.insertBefore(el, sib.nextSibling);
            startY = e.clientY; ox = 0; oy = 0;
            el.style.transform = 'translate(0,0)';
            return;
          }
        }
      }
    };
    const onUp = () => {
      dragging = false;
      if (isSection) {
        el.style.transform = '';
      }
    };
    const onKey = (e) => { if (e.key === 'Escape') setDragMode(null); };
    el.addEventListener('mousedown', onDown, true);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    window.addEventListener('keydown', onKey);
    return () => {
      el.style.cursor = '';
      el.style.outline = '';
      el.style.outlineOffset = '';
      el.style.transition = '';
      el.removeEventListener('mousedown', onDown, true);
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
      window.removeEventListener('keydown', onKey);
    };
  }, [dragMode, previewScale]);

  // Akcje z toolbara
  const onToolbarAction = (action) => {
    if (!uniToolbar) return;
    const el = uniToolbar.el;
    if (action === 'move') {
      setDragMode({ el });
      setUniToolbar(null);
    } else if (action === 'duplicate') {
      const clone = el.cloneNode(true);
      el.parentNode.insertBefore(clone, el.nextSibling);
    } else if (action === 'delete') {
      if (window.confirm('Usunąć ten element?')) {
        el.remove();
        setUniToolbar(null);
      }
    } else if (action === 'replaceImage') {
      const imgEl = el.tagName === 'IMG' ? el : el.querySelector('img') || el;
      setPicker({
        current: imgEl.getAttribute('src') || '',
        category: el.dataset?.photoCategory || imgEl.dataset?.photoCategory || 'Wnętrze',
        onPick: (url) => {
          if (imgEl.tagName === 'IMG') { imgEl.src = url; }
          else {
            // placeholder div → replace with img
            const img = document.createElement('img');
            img.src = url;
            img.alt = '';
            img.dataset.editableImg = 'true';
            img.dataset.photoCategory = el.dataset?.photoCategory || 'Wnętrze';
            if (el.style.cssText) img.style.cssText = el.style.cssText;
            img.style.background = '';
            img.style.display = 'block';
            el.replaceWith(img);
          }
        },
      });
    } else if (action === 'addBlockAfter') {
      setBlocksModal({ afterEl: el });
      setUniToolbar(null);
    } else if (action === 'infographic-duplicate-step' || action === 'infographic-add-step') {
      // Klonuj pojedynczy krok i wstaw jako kolejny element w gridzie
      const container = el.parentElement;
      if (!container) return;
      const clone = el.cloneNode(true);
      // Wyczyść edytowalne zaznaczenia na klonie
      clone.querySelectorAll('[data-wiz-selected]').forEach(n => { n.style.outline = ''; delete n.dataset.wizSelected; });
      // Dla 'add' — auto-increment cyfry jeśli istnieje
      if (action === 'infographic-add-step') {
        const circle = clone.querySelector('[data-infographic-circle="true"]');
        if (circle && /^\d+$/.test(circle.textContent.trim())) {
          circle.textContent = String(parseInt(circle.textContent.trim()) + 1);
        }
      }
      el.insertAdjacentElement('afterend', clone);
    } else if (action === 'infographic-move-step-left') {
      const prev = el.previousElementSibling;
      if (prev && prev.dataset?.infographicItem === 'true') {
        el.parentElement.insertBefore(el, prev);
      }
    } else if (action === 'infographic-move-step-right') {
      const next = el.nextElementSibling;
      if (next && next.dataset?.infographicItem === 'true') {
        el.parentElement.insertBefore(next, el);
      }
    } else if (action === 'infographic-remove-step') {
      const container = el.parentElement;
      const siblings = container ? Array.from(container.querySelectorAll(':scope > [data-infographic-item="true"]')) : [];
      if (siblings.length <= 1) { alert('Nie możesz usunąć ostatniego kroku.'); return; }
      if (window.confirm('Usunąć ten krok?')) {
        el.remove();
        setUniToolbar(null);
      }
    } else if (action === 'infographic-select-container') {
      // Wyjdź z kroku/kółka/łącznika do kontenera całej infografiki
      const container = el.closest('[data-editable-infographic]');
      if (container) {
        // Usuń selekcję z obecnego elementu
        document.querySelectorAll('[data-wiz-selected]').forEach(n => {
          n.style.outline = '';
          n.style.outlineOffset = '';
          delete n.dataset.wizSelected;
        });
        // Zaznacz kontener
        container.dataset.wizSelected = '1';
        container.style.outline = '2px solid #6366F1';
        container.style.outlineOffset = '2px';
        setUniToolbar({ el: container, kind: 'infographicContainer' });
      }
    } else if (action === 'infographic-change-template') {
      // el = kontener z data-editable-infographic. Otwórz galerię, po wyborze
      // zamień CAŁĄ infografikę (kontener) na wybrany szablon w DOM.
      openInfographicGallery?.({
        onPick: (html) => {
          const tmp = document.createElement('div');
          tmp.innerHTML = html.trim();
          // Szukamy kontenera [data-editable-infographic] w szablonie
          const newNode = tmp.querySelector('[data-editable-infographic]') || tmp.firstElementChild;
          if (newNode && el.parentElement) {
            el.parentElement.replaceChild(newNode, el);
            setUniToolbar(null);
            showToast?.('Szablon podmieniony', 'check');
          }
        },
      });
    }
  };

  const patchTweak = (k, v) => {
    const next = { ...tweaks, [k]: v };
    setTweaks(next);
    window.parent.postMessage({ type: '__edit_mode_set_keys', edits: { [k]: v } }, '*');
  };

  const showToast = (msg, icon = 'check') => {
    setToast({ msg, icon });
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => setToast(null), 2600);
  };

  const publish = () => {
    setPublished(true);
    showToast('Strona opublikowana na mietowa.pl', 'rocket');
  };

  const colRef = React.useRef(null);

  // Scale preview to fit column. W trybie Podgląd (liveEdit=false) — 1:1 z przewijaniem.
  React.useLayoutEffect(() => {
    const fit = () => {
      const col = colRef.current;
      if (!col) return;
      if (!liveEdit) {
        // Podgląd: 1:1, pełna szerokość bez skalowania, scroll naturalny
        setPreviewScale(1);
        return;
      }
      const available = col.clientWidth - 48; // padding
      const target = DEVICES[device].w;
      setPreviewScale(Math.min(1, available / target));
    };
    fit();
    const ro = new ResizeObserver(fit);
    if (colRef.current) ro.observe(colRef.current);
    return () => ro.disconnect();
  }, [device, tweaksOpen, liveEdit]);

  // Sections from store (mapped to renderer format: code/bg)
  const sections = storeSections.map(s => ({ id: s.id, code: s.block_code, bg: s.slots_json?.bg || null }));

  const brandBundle = {
    cta: tweaks.brandColor,
    ctaSecondary: tweaks.accentColor,
  };

  const pair = FONT_PAIRS[tweaks.fontPair] || FONT_PAIRS['Fraunces + Inter'];
  const densitySpacing = tweaks.density === 'compact' ? 0.75 : tweaks.density === 'spacious' ? 1.25 : 1;

  return (
    <div data-screen-label="06 Wizualizacja" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* TOPBAR */}
      <div style={{
        background: '#fff', borderBottom: '1px solid #E2E8F0', padding: '12px 24px',
        display: 'flex', alignItems: 'center', gap: 16, position: 'sticky', top: 0, zIndex: 20,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #6366F1, #EC4899)', display: 'grid', placeItems: 'center', color: '#fff', fontWeight: 800, fontSize: 15, fontFamily: 'Instrument Serif', fontStyle: 'italic' }}>W</div>
          <div>
            <div style={{ fontSize: 11, color: '#94A3B8', letterSpacing: 0.5, textTransform: 'uppercase', fontWeight: 600 }}>Projekt</div>
            <div style={{ fontSize: 14, fontWeight: 600 }}>Strona Kawiarni Miętowa</div>
          </div>
        </div>

        <div style={{ flex: 1 }} />
        <StepperBold current={5} />
        <div style={{ flex: 1 }} />

        {/* Device switcher */}
        <div style={{ display: 'inline-flex', background: '#F1F5F9', padding: 3, borderRadius: 9, gap: 2 }}>
          {Object.entries(DEVICES).map(([k, d]) => (
            <button key={k} onClick={() => setDevice(k as keyof typeof DEVICES)} title={d.label}
              style={{
                padding: '6px 10px', border: 'none',
                background: device === k ? '#fff' : 'transparent',
                borderRadius: 6, cursor: 'pointer',
                color: device === k ? '#0F172A' : '#64748B',
                boxShadow: device === k ? '0 1px 2px rgba(15,23,42,.08)' : 'none',
                display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: device === k ? 600 : 500,
              }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">{d.icon.split(' M').map((p, i) => <path key={i} d={i === 0 ? p : 'M' + p}/>)}</svg>
              {d.label}
            </button>
          ))}
        </div>

        {/* Toggle: Edytuj / Podgląd */}
        <div style={{ display: 'inline-flex', background: '#F1F5F9', padding: 3, borderRadius: 9, gap: 2 }}>
          <button onClick={() => setLiveEdit(true)} title="Edycja inline"
            style={{
              padding: '6px 11px', border: 'none',
              background: liveEdit ? '#fff' : 'transparent',
              borderRadius: 6, cursor: 'pointer',
              color: liveEdit ? '#0F172A' : '#64748B',
              boxShadow: liveEdit ? '0 1px 2px rgba(15,23,42,.08)' : 'none',
              display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: liveEdit ? 600 : 500,
              fontFamily: 'inherit',
            }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Edytuj
          </button>
          <button onClick={() => setLiveEdit(false)} title="Podgląd"
            style={{
              padding: '6px 11px', border: 'none',
              background: !liveEdit ? '#fff' : 'transparent',
              borderRadius: 6, cursor: 'pointer',
              color: !liveEdit ? '#0F172A' : '#64748B',
              boxShadow: !liveEdit ? '0 1px 2px rgba(15,23,42,.08)' : 'none',
              display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: !liveEdit ? 600 : 500,
              fontFamily: 'inherit',
            }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            Podgląd
          </button>
        </div>

        {/* Pełny podgląd — otwiera fullscreen overlay */}
        <button onClick={() => { setLiveEdit(false); setFullscreen(true); }} title="Pełny ekran — podgląd strony 1:1"
          style={{
            padding: '7px 12px', border: '1px solid #E2E8F0',
            background: '#fff', borderRadius: 9, cursor: 'pointer',
            color: '#334155', fontSize: 12, fontWeight: 500,
            display: 'inline-flex', alignItems: 'center', gap: 6,
            fontFamily: 'inherit',
          }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M3 3h6M3 3v6M21 3h-6M21 3v6M21 21h-6M21 21v-6M3 21h6M3 21v-6"/>
          </svg>
          Pełny ekran
        </button>

        {/* Publikuj */}
        <button onClick={publish} disabled={published} style={{
          padding: '8px 16px',
          background: published ? '#DCFCE7' : 'linear-gradient(135deg, #10B981 0%, #14B8A6 100%)',
          color: published ? '#065F46' : '#fff',
          border: 'none', borderRadius: 9,
          fontFamily: 'inherit', fontSize: 13, fontWeight: 600,
          cursor: published ? 'default' : 'pointer',
          display: 'inline-flex', alignItems: 'center', gap: 7,
          boxShadow: published ? 'none' : '0 2px 8px rgba(16,185,129,.35)',
        }}>
          {published ? (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
              Opublikowano
            </>
          ) : (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 00-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 012-3.95A12.88 12.88 0 0122 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 01-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/></svg>
              Publikuj stronę
            </>
          )}
        </button>
      </div>

      {/* MAIN */}
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: tweaksOpen ? 'minmax(0,1fr) 320px' : '1fr', overflow: 'hidden' }}>

        {/* PREVIEW COLUMN */}
        <div ref={colRef} style={{ background: '#E5E7EB', padding: '20px 24px 40px', overflow: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {/* Browser chrome w/ page tabs */}
          <div style={{
            width: Math.min(DEVICES[device].w * previewScale, DEVICES[device].w),
            maxWidth: '100%',
            background: '#fff', borderRadius: '12px 12px 0 0',
            border: '1px solid #E2E8F0', borderBottom: 'none',
            padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 10,
            boxShadow: '0 2px 4px rgba(0,0,0,.04)',
            fontFamily: 'Inter, sans-serif',
          }}>
            <div style={{ display: 'flex', gap: 5 }}>
              <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#FF5F57' }}/>
              <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#FEBC2E' }}/>
              <span style={{ width: 11, height: 11, borderRadius: '50%', background: '#28C840' }}/>
            </div>
            <div style={{ flex: 1, display: 'flex', gap: 3, overflowX: 'auto' }}>
              <button style={{
                padding: '5px 11px',
                background: '#fff',
                border: '1px solid #E2E8F0',
                borderBottom: '1px solid #fff',
                borderRadius: '6px 6px 0 0',
                fontFamily: 'inherit', fontSize: 11.5, cursor: 'pointer',
                color: '#0F172A', fontWeight: 600,
                whiteSpace: 'nowrap',
                position: 'relative', marginBottom: -1,
              }}>Strona</button>
            </div>
            <div style={{ fontSize: 11, color: '#94A3B8', fontFamily: 'ui-monospace, monospace' }}>
              mietowa.pl{'/'}
            </div>
            {published && (
              <span style={{ fontSize: 10, padding: '2px 7px', background: '#DCFCE7', color: '#065F46', borderRadius: 4, fontWeight: 700, fontFamily: 'inherit' }}>LIVE</span>
            )}
          </div>

          {/* Scaled device frame */}
          <div style={{
            width: DEVICES[device].w * previewScale,
            height: 'auto',
            position: 'relative',
            maxWidth: '100%',
          }}>
            <div className={`viewport-${device}`} style={{
              width: DEVICES[device].w,
              transform: `scale(${previewScale})`,
              transformOrigin: 'top left',
              background: '#fff',
              borderRadius: '0 0 12px 12px',
              overflow: 'hidden',
              boxShadow: '0 20px 60px rgba(0,0,0,.15)',
              border: '1px solid #E2E8F0',
              borderTop: 'none',
              fontFamily: `'${pair.b}', sans-serif`,
              '--font-heading': `'${pair.h}', serif`,
              '--font-body': `'${pair.b}', sans-serif`,
            } as React.CSSProperties}>
              {(() => {
                const densityIdx = tweaks.density === 'compact' ? 2 : tweaks.density === 'spacious' ? 4 : 3;
                const typo = makeWizTypo(pair, densityIdx);
                const brand = { bg: tweaks.headerBg || '#FFFFFF', bg2: '#F1F5F9', cta: tweaks.brandColor, cta2: tweaks.accentColor, ctaGradient: true };
                return (
                  <DeviceCtx.Provider value={device}>
                  <SREditCtx.Provider value={wzEditCtx as any}>
                    {wzContent.map((s, idx) => {
                      const Renderer = WIZ_SECTION_RENDERERS[s.code] || SECTION_RENDERERS[s.code] || SECTION_RENDERERS.PLACEHOLDER;
                      if (!Renderer) return null;
                      return (
                        <div key={s.id} data-section-id={s.id}
                          onMouseEnter={() => setWzHovered(s.id)}
                          onMouseLeave={() => { if (wzHovered === s.id) setWzHovered(null); }}
                          style={{ position: 'relative' }}>
                          <Renderer s={s} brand={idx % 2 === 0 ? brand : { ...brand, bg: brand.bg2 }} typo={typo} device={device} update={(p) => wzUpdateSection(s.id, p)}/>
                          {wzHovered === s.id && liveEdit && !wzSelected && (
                            <div style={{
                              position: 'absolute', top: 6, right: 6, display: 'flex', gap: 4, zIndex: 20,
                              background: 'rgba(15,23,42,.85)', borderRadius: 8, padding: '4px 6px',
                              alignItems: 'center',
                            }}>
                              <span style={{ color: '#fff', fontSize: 10, fontWeight: 600, padding: '2px 6px', opacity: 0.7 }}>{s.label || s.code}</span>
                              {idx > 0 && <button onClick={() => wzMoveSection(s.id, 'up')} style={hoverBtnStyle} title="W górę">↑</button>}
                              {idx < wzContent.length - 1 && <button onClick={() => wzMoveSection(s.id, 'down')} style={hoverBtnStyle} title="W dół">↓</button>}
                              <button onClick={() => wzDuplicateSection(s.id)} style={hoverBtnStyle} title="Duplikuj">⧉</button>
                              <button onClick={() => wzDeleteSection(s.id)} style={{...hoverBtnStyle, color: '#FCA5A5'}} title="Usuń">✕</button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </SREditCtx.Provider>
                  </DeviceCtx.Provider>
                );
              })()}
            </div>
            {/* phantom div — measures real height so scaled preview scrolls correctly */}
            <div ref={previewRef} style={{
              position: 'absolute', top: 0, left: 0, width: 1, pointerEvents: 'none',
              height: 5800 * previewScale,
            }}/>
          </div>
        </div>

        {/* TWEAKS PANEL */}
        {tweaksOpen && (
          <div style={{ background: '#fff', borderLeft: '1px solid #E2E8F0', overflow: 'auto', padding: '20px 20px 40px' }}>
            <TweakPanel tweaks={tweaks} onPatch={patchTweak} />

            {/* Readiness checklist — informational */}
            <div style={{ marginTop: 24, padding: 16, background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 12 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.6, marginBottom: 10 }}>Gotowość</div>
              {[
                { l: 'Brand — kolory i logo', ok: true },
                { l: 'Treści — wszystkie sekcje wypełnione', ok: true },
                { l: 'Dane kontaktowe — adres, telefon, email', ok: true },
                { l: 'SEO — meta title i opis', ok: false },
                { l: 'Domena — mietowa.pl', ok: true },
              ].map((x, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '5px 0', fontSize: 12.5 }}>
                  <span style={{
                    width: 16, height: 16, borderRadius: '50%',
                    background: x.ok ? '#10B981' : '#F1F5F9',
                    border: x.ok ? 'none' : '1.5px solid #CBD5E1',
                    display: 'grid', placeItems: 'center',
                  }}>
                    {x.ok && <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="4" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>}
                  </span>
                  <span style={{ color: x.ok ? '#0F172A' : '#94A3B8', flex: 1 }}>{x.l}</span>
                  {!x.ok && <a style={{ color: '#6366F1', fontSize: 11.5, textDecoration: 'none', cursor: 'pointer', fontWeight: 500 }}>Uzupełnij →</a>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* IMAGE PICKER MODAL */}
      {picker && ImagePicker && (
        <ImagePicker picker={picker} onClose={() => setPicker(null)} />
      )}

      {/* BLOCKS LIBRARY MODAL — "Dodaj pod" */}
      {blocksModal && WizBlocksModal && (
        <WizBlocksModal
          open={true}
          onClose={() => setBlocksModal(null)}
          onPick={(block) => {
            if (wizInsertBlockAfter && blocksModal.afterEl) {
              wizInsertBlockAfter(blocksModal.afterEl, block);
            }
            setBlocksModal(null);
          }}
        />
      )}

      {/* UNIWERSALNY TOOLBAR kontekstowy */}
      {uniToolbar && UniToolbar && !editingEl && !dragMode && (
        <UniToolbar
          target={uniToolbar.el}
          kind={uniToolbar.kind}
          onClose={() => {
            if (uniToolbar.el?.dataset?.wizSelected) {
              uniToolbar.el.style.outline = '';
              delete uniToolbar.el.dataset.wizSelected;
            }
            setUniToolbar(null);
          }}
          onAction={onToolbarAction}
        />
      )}

      {/* HINT podczas drag mode */}
      {dragMode && (
        <div style={{
          position: 'fixed', top: 80, left: '50%', transform: 'translateX(-50%)',
          background: '#0F172A', color: '#fff', padding: '10px 18px', borderRadius: 10,
          fontSize: 12.5, fontWeight: 500, display: 'inline-flex', alignItems: 'center', gap: 10,
          boxShadow: '0 10px 30px rgba(0,0,0,.3)', zIndex: 400,
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <polyline points="5 9 2 12 5 15"/><polyline points="9 5 12 2 15 5"/><polyline points="15 19 12 22 9 19"/><polyline points="19 9 22 12 19 15"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/>
          </svg>
          Przeciągnij element. <kbd style={{ padding: '2px 6px', background: 'rgba(255,255,255,.15)', borderRadius: 4, fontFamily: 'ui-monospace, monospace', fontSize: 11 }}>Esc</kbd> aby zakończyć
          <button onClick={() => setDragMode(null)} style={{
            marginLeft: 4, padding: '4px 10px', background: '#fff', color: '#0F172A',
            border: 'none', borderRadius: 6, fontSize: 11, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
          }}>Gotowe</button>
        </div>
      )}

      {/* AI ASSISTANT — pływający przycisk + panel po prawej */}
      {!aiAssistOpen && liveEdit && (
        <button onClick={() => setAiAssistOpen(true)} title="Asystent AI"
          style={{
            position: 'fixed', bottom: 28, right: 28, zIndex: 200,
            width: 54, height: 54, borderRadius: '50%', border: 'none',
            background: 'linear-gradient(135deg, #A8D5BA 0%, #6FAE8C 100%)',
            color: '#fff', cursor: 'pointer',
            boxShadow: '0 8px 24px rgba(111,174,140,.4), 0 0 0 1px rgba(255,255,255,.2) inset',
            display: 'grid', placeItems: 'center',
            transition: 'transform .15s',
          }}
          onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.06)'}
          onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </button>
      )}
      {aiAssistOpen && WizAIPanel && (
        <WizAIPanel
          onClose={() => setAiAssistOpen(false)}
          getViewportEl={() => previewRef.current?.previousElementSibling}
          activePageName={'Strona'}
        />
      )}

      {/* TOAST */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)',
          background: '#0F172A', color: '#fff', padding: '10px 18px', borderRadius: 10,
          fontSize: 13, fontWeight: 500, display: 'inline-flex', alignItems: 'center', gap: 9,
          boxShadow: '0 10px 30px rgba(15,23,42,.3)', zIndex: 300,
          animation: 'toastIn .2s',
        }}>
          {toast.icon === 'rocket' ? (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 00-2.91-.09z"/>
              <path d="M12 15l-3-3a22 22 0 012-3.95A12.88 12.88 0 0122 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 01-4 2z"/>
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
          )}
          {toast.msg}
        </div>
      )}

      {/* ===== PEŁNY EKRAN — fullscreen podgląd strony ===== */}
      {fullscreen && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 500,
          background: '#0F172A',
          display: 'flex', flexDirection: 'column',
        }}>
          {/* top bar */}
          <div style={{
            height: 44, background: '#0F172A', color: '#fff',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '0 16px', borderBottom: '1px solid rgba(255,255,255,.08)',
            fontSize: 12,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 8, height: 8, borderRadius: 4, background: '#10B981',
                boxShadow: '0 0 0 3px rgba(16,185,129,.2)',
              }}/>
              <span style={{ fontWeight: 600 }}>Podgląd 1:1</span>
              <span style={{ color: 'rgba(255,255,255,.5)' }}>·</span>
              <span style={{ color: 'rgba(255,255,255,.7)' }}>{'Strona'}</span>
              <span style={{ color: 'rgba(255,255,255,.5)' }}>·</span>
              <span style={{ color: 'rgba(255,255,255,.7)' }}>{DEVICES[device].w}px</span>
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              {Object.keys(DEVICES).map(d => (
                <button key={d} onClick={() => setDevice(d as keyof typeof DEVICES)} style={{
                  padding: '4px 10px', border: '1px solid rgba(255,255,255,.15)',
                  background: device === d ? 'rgba(255,255,255,.12)' : 'transparent',
                  color: '#fff', borderRadius: 6, cursor: 'pointer',
                  fontSize: 11, fontWeight: 500, fontFamily: 'inherit',
                }}>{DEVICES[d].label}</button>
              ))}
              <div style={{ width: 1, height: 18, background: 'rgba(255,255,255,.15)', margin: '0 4px' }}/>
              <button onClick={() => setFullscreen(false)} style={{
                padding: '6px 12px', border: '1px solid rgba(255,255,255,.2)',
                background: 'rgba(255,255,255,.1)', color: '#fff',
                borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 600,
                fontFamily: 'inherit', display: 'inline-flex', alignItems: 'center', gap: 6,
              }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                Zamknij podgląd (Esc)
              </button>
            </div>
          </div>
          {/* stage — obszar do wyświetlenia iframe'a strony */}
          <div style={{ flex: 1, overflow: 'auto', display: 'flex', justifyContent: 'center', alignItems: 'flex-start', padding: device === 'desktop' ? 0 : 24 }}>
            <div style={{
              width: DEVICES[device].w,
              minHeight: '100%',
              background: '#fff',
              boxShadow: device === 'desktop' ? 'none' : '0 30px 60px rgba(0,0,0,.4)',
              borderRadius: device === 'desktop' ? 0 : 14,
              overflow: 'hidden',
              fontFamily: `'${pair.b}', sans-serif`,
              '--font-heading': `'${pair.h}', serif`,
              '--font-body': `'${pair.b}', sans-serif`,
            } as React.CSSProperties}>
              {(() => {
                const densityIdx = tweaks.density === 'compact' ? 2 : tweaks.density === 'spacious' ? 4 : 3;
                const typo = makeWizTypo(pair, densityIdx);
                const brand = { bg: tweaks.headerBg || '#FFFFFF', bg2: '#F1F5F9', cta: tweaks.brandColor, cta2: tweaks.accentColor, ctaGradient: true };
                return (
                  <DeviceCtx.Provider value={device}>
                  <SREditCtx.Provider value={wzEditCtx as any}>
                    {wzContent.map((s, idx) => {
                      const Renderer = WIZ_SECTION_RENDERERS[s.code] || SECTION_RENDERERS[s.code] || SECTION_RENDERERS.PLACEHOLDER;
                      if (!Renderer) return null;
                      return <Renderer key={s.id} s={s} brand={idx % 2 === 0 ? brand : { ...brand, bg: brand.bg2 }} typo={typo} device={device} update={(p: any) => wzUpdateSection(s.id, p)}/>;
                    })}
                  </SREditCtx.Provider>
                  </DeviceCtx.Provider>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StepperBold({ current }: { current: number }) {
  const steps = [
    { n: 1, name: 'Brief' }, { n: 2, name: 'Brand' }, { n: 3, name: 'Walidacja' },
    { n: 4, name: 'Struktura' }, { n: 5, name: 'Treści' }, { n: 6, name: 'Wizualizacja' },
  ];
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
      {steps.map((st, i) => {
        const done = st.n < current;
        const active = st.n === current;
        return (
          <React.Fragment key={st.n}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '5px 10px', borderRadius: 8,
              background: active ? 'rgba(99,102,241,.1)' : 'transparent',
              color: active ? '#6366F1' : (done ? '#64748B' : '#94A3B8'),
              fontSize: 12, fontWeight: active ? 600 : 500,
            }}>
              <span style={{
                width: 18, height: 18, borderRadius: '50%',
                background: active ? '#6366F1' : (done ? '#CBD5E1' : '#E2E8F0'),
                color: active ? '#fff' : '#64748B',
                display: 'grid', placeItems: 'center', fontSize: 10, fontWeight: 700,
              }}>{done ? '✓' : st.n}</span>
              {st.name}
            </div>
            {i < steps.length - 1 && <div style={{ width: 10, height: 1, background: '#CBD5E1' }}/>}
          </React.Fragment>
        );
      })}
    </div>
  );
}

