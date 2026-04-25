import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  DndContext, closestCenter, PointerSensor, useSensor, useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  SortableContext, useSortable, verticalListSortingStrategy, arrayMove,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useLabStore, type Section } from '@/store/labStore';
import {
  BLOCK_LIBRARY, CATEGORIES, bgColorToCSS,
} from '@/types/lab';
import type { Brand, Gradient } from '@/types/lab';
import { BlockPreview } from '@/lib/blocks';
import { ColorPicker } from '@/components/ColorPicker';

// ── Helpers ──

function getCatCode(code: string) { return code.replace(/\d+/g, ''); }

function getBrandBg(brand: Brand) {
  if (brand.ctaIsGradient) return `linear-gradient(135deg, ${brand.bgColor}, ${brand.bgColor})`;
  return brand.bgColor;
}

function brandForPreview(brand: Brand) {
  return { cta: brand.ctaColor, ctaSecondary: brand.ctaColor2 };
}

// ── Block Library Sidebar ──

interface SidebarProps {
  onAdd: (code: string) => void;
}

function BlockLibrarySidebar({ onAdd }: SidebarProps) {
  const [search, setSearch] = useState('');
  const [activeCat, setActiveCat] = useState<string | null>(null);

  const filtered = BLOCK_LIBRARY.filter(b => {
    const matchCat = !activeCat || b.cat === activeCat;
    const matchSearch = !search || b.name.toLowerCase().includes(search.toLowerCase()) || b.code.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  const cats = [...new Set(BLOCK_LIBRARY.map(b => b.cat))];

  return (
    <aside className="w-72 flex-shrink-0 bg-white border-r border-gray-100 flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100">
        <div className="text-sm font-bold text-slate-800 mb-2">Biblioteka klocków</div>
        <input
          type="text"
          placeholder="Szukaj klocka..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full h-8 px-3 text-xs border border-gray-200 rounded-lg outline-none focus:border-indigo-400 bg-gray-50"
        />
      </div>

      {/* Category chips */}
      <div className="px-3 py-2 border-b border-gray-100 flex flex-wrap gap-1">
        <button
          onClick={() => setActiveCat(null)}
          className={`px-2 py-0.5 rounded-md text-xs font-semibold transition-colors ${
            activeCat === null ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
          }`}
        >Wszystkie</button>
        {cats.map(cat => {
          const c = CATEGORIES[cat];
          return (
            <button
              key={cat}
              onClick={() => setActiveCat(activeCat === cat ? null : cat)}
              className="px-2 py-0.5 rounded-md text-xs font-semibold transition-colors"
              style={{
                background: activeCat === cat ? `${c.color}20` : '#F1F5F9',
                color: activeCat === cat ? c.color : '#64748B',
              }}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {/* Block list */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1.5">
        {filtered.map(block => {
          const cat = CATEGORIES[block.cat];
          return (
            <button
              key={block.code}
              onClick={() => onAdd(block.code)}
              className="w-full text-left rounded-xl border border-gray-100 bg-gray-50 hover:border-indigo-200 hover:bg-indigo-50 transition-all group overflow-hidden"
            >
              {/* Thumbnail */}
              <div className="h-24 overflow-hidden rounded-t-xl bg-white relative">
                <BlockPreview code={block.code} bg="#FFFFFF" />
              </div>
              {/* Info */}
              <div className="px-2.5 py-2 flex items-center gap-2">
                <span
                  className="text-[10px] font-bold font-mono px-1.5 py-0.5 rounded"
                  style={{ background: `${cat.color}18`, color: cat.color }}
                >
                  {block.code}
                </span>
                <span className="text-xs text-gray-600 truncate flex-1">{block.name}</span>
                <span className="text-[9px] text-gray-400 font-mono">{block.size}</span>
              </div>
            </button>
          );
        })}
        {filtered.length === 0 && (
          <div className="text-center text-gray-400 text-xs py-8">Brak wyników</div>
        )}
      </div>
    </aside>
  );
}

// ── Sortable Section Card ──

interface SectionCardProps {
  section: Section;
  index: number;
  total: number;
  onDelete: () => void;
  onDuplicate: () => void;
}

function SortableSectionCard({ section, index, total, onDelete, onDuplicate }: SectionCardProps) {
  const {
    attributes, listeners, setNodeRef, transform, transition, isDragging,
  } = useSortable({ id: section.id });

  const { brand, updateSectionMeta, updateSection } = useLabStore();

  const [localName, setLocalName] = useState(section.name ?? section.block_code);

  useEffect(() => {
    setLocalName(section.name ?? section.block_code);
  }, [section.name, section.block_code]);

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 50 : 'auto',
  };

  const block = BLOCK_LIBRARY.find(b => b.code === section.block_code);
  const catCode = getCatCode(section.block_code);
  const cat = CATEGORIES[catCode] ?? { name: catCode, color: '#6366F1', icon: '' };
  const sameCatBlocks = BLOCK_LIBRARY.filter(b => b.cat === catCode);

  const bgCSS = bgColorToCSS(section.bgColor, brand.bgColor);
  const brandBg = getBrandBg(brand);

  const handleBgChange = useCallback((v: string | Gradient | null) => {
    updateSectionMeta(section.id, { bgColor: v });
  }, [section.id, updateSectionMeta]);

  const handleCtaChange = useCallback((v: string | Gradient | null) => {
    updateSectionMeta(section.id, { ctaColor: v });
  }, [section.id, updateSectionMeta]);

  const handleNameBlur = useCallback(() => {
    if (localName !== (section.name ?? section.block_code)) {
      updateSectionMeta(section.id, { name: localName });
    }
  }, [localName, section.id, section.name, section.block_code, updateSectionMeta]);

  const handleVariantChange = useCallback((code: string) => {
    updateSection(section.id, { block_code: code });
  }, [section.id, updateSection]);

  const previewBg = section.bgColor ? bgCSS : brand.bgColor;
  const previewBrand = brandForPreview(brand);

  return (
    <div ref={setNodeRef} style={style} className="bg-white rounded-2xl border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all overflow-hidden">
      {/* Header strip */}
      <div className="flex items-center gap-2 px-3.5 py-2.5 border-b border-gray-100 bg-gradient-to-b from-gray-50 to-gray-100/50">
        {/* Drag handle */}
        <div
          {...attributes}
          {...listeners}
          className="text-gray-300 cursor-grab active:cursor-grabbing p-1 hover:text-gray-400"
          title="Przeciągnij aby zmienić kolejność"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="9" cy="6" r="1.5"/><circle cx="15" cy="6" r="1.5"/>
            <circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/>
            <circle cx="9" cy="18" r="1.5"/><circle cx="15" cy="18" r="1.5"/>
          </svg>
        </div>

        {/* Code badge */}
        <span
          className="text-[11px] font-bold font-mono px-2 py-0.5 rounded-md"
          style={{ background: `${cat.color}18`, color: cat.color }}
        >
          {section.block_code}
        </span>
        <span className="text-[10px] text-gray-400 font-medium uppercase tracking-wide">
          Sekcja {String(index + 1).padStart(2, '0')} / {total}
        </span>
        <div className="flex-1" />
        {/* Status */}
        <span className="inline-flex items-center gap-1 h-5 px-2 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          Aktywna
        </span>
      </div>

      {/* Body: 2.2fr preview + 1fr config */}
      <div className="grid" style={{ gridTemplateColumns: '2.2fr 1fr', minHeight: 280 }}>
        {/* Preview */}
        <div className="p-3.5 border-r border-gray-100 bg-slate-50 flex">
          <div className="flex-1 rounded-xl overflow-hidden shadow-sm" style={{ minHeight: 240 }}>
            <BlockPreview code={section.block_code} bg={previewBg} brand={previewBrand} />
          </div>
          {/* Size badge */}
          <div className="absolute" style={{ position: 'relative' }}>
            <span className="absolute bottom-2 left-2 text-[10px] font-mono bg-white/90 border border-gray-200 px-1.5 py-0.5 rounded text-gray-500">
              {block?.size ?? 'M'}
            </span>
          </div>
        </div>

        {/* Config */}
        <div className="p-4 flex flex-col gap-3.5">
          {/* Name */}
          <label className="block">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-1">Nazwa sekcji</span>
            <input
              value={localName}
              onChange={e => setLocalName(e.target.value)}
              onBlur={handleNameBlur}
              className="w-full h-8 px-2.5 border border-gray-200 rounded-lg text-sm outline-none focus:border-indigo-400 transition-colors"
            />
          </label>

          {/* Variant */}
          {sameCatBlocks.length > 1 && (
            <label className="block">
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-1">Wariant klocka</span>
              <select
                value={section.block_code}
                onChange={e => handleVariantChange(e.target.value)}
                className="w-full h-8 px-2 border border-gray-200 rounded-lg text-xs bg-white outline-none focus:border-indigo-400"
              >
                {sameCatBlocks.map(b => (
                  <option key={b.code} value={b.code}>{b.code} — {b.name}</option>
                ))}
              </select>
            </label>
          )}

          {/* Bg color */}
          <div>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-1.5">Kolor tła</span>
            <ColorPicker
              value={section.bgColor}
              brandValue={brandBg}
              onChange={handleBgChange}
            />
            {section.brandWarning && (
              <div className="mt-1.5 text-[10px] text-amber-600 bg-amber-50 border border-amber-200 rounded px-2 py-1 flex items-center gap-1">
                <span>⚠</span>{section.brandWarning}
              </div>
            )}
          </div>

          {/* CTA color */}
          <div>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-1.5">
              Kolor CTA <span className="normal-case font-normal text-gray-300">(opcjonalnie)</span>
            </span>
            <ColorPicker
              value={section.ctaColor}
              brandValue={brand.ctaColor}
              onChange={handleCtaChange}
            />
          </div>

          <div className="flex-1" />

          {/* Actions */}
          <div className="flex gap-1.5 pt-2.5 border-t border-gray-100">
            <ActionBtn onClick={onDuplicate} title="Duplikuj">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="9" y="9" width="13" height="13" rx="2"/>
                <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
              </svg>
            </ActionBtn>
            <ActionBtn onClick={onDelete} title="Usuń" danger>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
              </svg>
            </ActionBtn>
            <div className="flex-1" />
            {/* Hidden toggle */}
            <ActionBtn
              onClick={() => updateSection(section.id, { is_visible: !section.is_visible })}
              title={section.is_visible ? 'Ukryj sekcję' : 'Pokaż sekcję'}
            >
              {section.is_visible
                ? <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                : <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22"/></svg>
              }
            </ActionBtn>
          </div>
        </div>
      </div>
    </div>
  );
}

function ActionBtn({ onClick, title, danger, children }: { onClick: () => void; title?: string; danger?: boolean; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      title={title}
      className="w-8 h-8 border border-gray-200 bg-white rounded-lg grid place-items-center transition-all hover:bg-gray-50"
      style={{ color: danger ? '#EF4444' : '#64748B' }}
      onMouseEnter={e => {
        if (danger) {
          e.currentTarget.style.background = '#FEE2E2';
          e.currentTarget.style.borderColor = '#FCA5A5';
        }
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = '';
        e.currentTarget.style.borderColor = '';
      }}
    >
      {children}
    </button>
  );
}

// ── Main Page ──

export default function Step3Structure() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const {
    sections, brand, addSection, removeSection, reorderSections,
    generateStructure, isGenerating, error, setError,
  } = useLabStore();

  const startedRef = { current: false };

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  useEffect(() => {
    if (sections.length === 0 && !isGenerating && !startedRef.current) {
      startedRef.current = true;
      setError(null);
      generateStructure();
    }
  }, [sections.length, isGenerating]);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = sections.findIndex(s => s.id === active.id);
    const newIndex = sections.findIndex(s => s.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;
    const reordered = arrayMove(sections, oldIndex, newIndex);
    reorderSections(reordered.map(s => s.id));
  }, [sections, reorderSections]);

  const handleAdd = useCallback(async (code: string) => {
    await addSection(code, sections.length);
  }, [addSection, sections.length]);

  const handleDuplicate = useCallback(async (section: Section) => {
    await addSection(section.block_code, section.position + 1);
  }, [addSection]);

  const handleDelete = useCallback(async (id: string) => {
    if (confirm('Usunąć tę sekcję?')) await removeSection(id);
  }, [removeSection]);

  return (
    <div className="flex h-full overflow-hidden" style={{ minHeight: 'calc(100vh - 96px)' }}>
      {/* Sidebar */}
      <BlockLibrarySidebar onAdd={handleAdd} />

      {/* Main area */}
      <main className="flex-1 overflow-y-auto bg-slate-50">
        {/* Toolbar */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-100 px-6 py-3 flex items-center gap-3">
          <h1 className="text-base font-bold text-slate-800">Struktura strony</h1>
          <div className="flex-1" />
          <button
            onClick={() => { setError(null); generateStructure(); }}
            disabled={isGenerating}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-500 disabled:opacity-50 transition-colors"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/></svg>
            {isGenerating ? 'Generowanie...' : 'AI sugestia'}
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* Loading */}
          {isGenerating && sections.length === 0 && (
            <div className="text-center py-20">
              <div className="inline-flex items-center gap-3 bg-white border border-gray-200 px-6 py-4 rounded-2xl shadow-sm">
                <svg className="animate-spin w-5 h-5 text-indigo-500" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                <span className="text-sm font-medium text-gray-600">AI generuje strukturę strony...</span>
              </div>
            </div>
          )}

          {/* Error */}
          {!isGenerating && error && sections.length === 0 && (
            <div className="text-center py-12 space-y-4">
              <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-5 py-3 rounded-xl border border-red-200">
                <span>✗</span><span className="text-sm">{error}</span>
              </div>
              <div>
                <button onClick={() => { setError(null); generateStructure(); }} className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700">
                  Spróbuj ponownie
                </button>
              </div>
            </div>
          )}

          {/* Empty */}
          {!isGenerating && !error && sections.length === 0 && (
            <div className="text-center py-20 text-gray-400 text-sm">
              <p className="mb-4">Dodaj klocki z panelu po lewej lub wygeneruj strukturę AI.</p>
              <button onClick={() => generateStructure()} className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700">
                Generuj z AI
              </button>
            </div>
          )}

          {/* Section cards with DnD */}
          {sections.length > 0 && (
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
              <SortableContext items={sections.map(s => s.id)} strategy={verticalListSortingStrategy}>
                <div className="space-y-4">
                  {sections.map((section, idx) => (
                    <SortableSectionCard
                      key={section.id}
                      section={section}
                      index={idx}
                      total={sections.length}
                      onDelete={() => handleDelete(section.id)}
                      onDuplicate={() => handleDuplicate(section)}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
          )}

          {/* Brand summary bar */}
          {sections.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 flex items-center gap-3 text-xs text-gray-500">
              <span className="font-semibold text-gray-700">Brand:</span>
              <span className="w-5 h-5 rounded-md border border-gray-200 flex-shrink-0" style={{ background: brand.ctaColor }} />
              <span>{brand.ctaColor}</span>
              <span className="text-gray-300">|</span>
              <span>{brand.fontHeading}</span>
              <span className="text-gray-300">|</span>
              <span>{brand.density}</span>
            </div>
          )}
        </div>

        {/* Nav */}
        <div className="sticky bottom-0 bg-white border-t border-gray-100 px-6 py-3 flex justify-between">
          <button onClick={() => navigate(`/lab/${projectId}/step/2`)} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">
            ← Wstecz
          </button>
          <button
            onClick={() => navigate(`/lab/${projectId}/step/4`)}
            disabled={sections.length === 0 || isGenerating}
            className="px-6 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            Dalej → Treści
          </button>
        </div>
      </main>
    </div>
  );
}
