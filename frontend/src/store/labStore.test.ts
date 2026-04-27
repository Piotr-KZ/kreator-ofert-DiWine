import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useLabStore } from './labStore';

// Mock the API module — all store actions call api.*
vi.mock('@/api/client', () => ({
  createProject: vi.fn().mockResolvedValue({ data: { id: 'p1' } }),
  getProject: vi.fn().mockResolvedValue({
    data: {
      id: 'p1', name: 'Test', site_type: 'company_card',
      brief_json: null, style_json: null, sections: [], visual_concept_json: null, current_step: 1,
    },
  }),
  updateProject: vi.fn().mockResolvedValue({ data: {} }),
  addSection: vi.fn().mockResolvedValue({ data: {} }),
  deleteSection: vi.fn().mockResolvedValue({ data: {} }),
  reorderSections: vi.fn().mockResolvedValue({ data: {} }),
  updateSection: vi.fn().mockResolvedValue({ data: {} }),
  duplicateSection: vi.fn().mockResolvedValue({ data: {} }),
  generateStructure: vi.fn().mockResolvedValue({ data: {} }),
  generateContent: vi.fn().mockResolvedValue({ data: {} }),
  generateVisualConcept: vi.fn().mockResolvedValue({ data: {} }),
  saveVisualConcept: vi.fn().mockResolvedValue({ data: {} }),
  validateBrief: vi.fn().mockResolvedValue({ data: { items: [] } }),
  analyzeWebsite: vi.fn().mockResolvedValue({ data: {} }),
  regenerateSection: vi.fn().mockResolvedValue({ data: { slots_json: {} } }),
}));

const MOCK_SECTIONS = [
  { id: 's1', block_code: 'HE1', position: 0, variant: 'A', slots_json: { heading: 'Hello' }, is_visible: true },
  { id: 's2', block_code: 'PB1', position: 1, variant: 'A', slots_json: { heading: 'Problem' }, is_visible: true },
  { id: 's3', block_code: 'CT1', position: 2, variant: 'A', slots_json: { heading: 'CTA' }, is_visible: true },
];

function seedStore() {
  useLabStore.setState({
    projectId: 'p1',
    projectName: 'Test Project',
    sections: [...MOCK_SECTIONS.map(s => ({ ...s }))],
  });
}

beforeEach(() => {
  // Reset store to initial state
  useLabStore.setState({
    projectId: null,
    projectName: '',
    siteType: 'company_card',
    brief: { description: '', target_audience: '', usp: '', tone: 'profesjonalny', website: '' },
    style: { primary_color: '#4F46E5', secondary_color: '#F59E0B' },
    brand: { fontHeading: "'Fraunces', serif", fontBody: "'Inter', sans-serif", ctaColor: '#6FAE8C', density: 'normal' },
    sections: [],
    visualConcept: null,
    currentStep: 1,
    isLoading: false,
    isGenerating: false,
    error: null,
  });
});

// ── test_makiety_drag_drop — addSection dodaje klocek ────────
describe('addSection (drag & drop)', () => {
  it('calls API and reloads project to get new section', async () => {
    const { addSection } = useLabStore.getState();
    const apiClient = await import('@/api/client');

    // After addSection, loadProject is called which sets sections from response
    const updatedSections = [
      ...MOCK_SECTIONS,
      { id: 's4', block_code: 'FA1', position: 3, variant: 'A', slots_json: null, is_visible: true },
    ];
    (apiClient.getProject as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: { id: 'p1', name: 'Test', sections: updatedSections, current_step: 1 },
    });

    seedStore();
    await addSection('FA1', 3);

    expect(apiClient.addSection).toHaveBeenCalledWith('p1', 'FA1', 3);
    expect(useLabStore.getState().sections).toHaveLength(4);
    expect(useLabStore.getState().sections[3].block_code).toBe('FA1');
  });
});

// ── test_makiety_reorder — reorderSections zmienia kolejność ──
describe('reorderSections (reorder)', () => {
  it('reorders sections optimistically by new ID order', async () => {
    seedStore();
    const { reorderSections } = useLabStore.getState();

    // Reverse order: s3, s2, s1
    await reorderSections(['s3', 's2', 's1']);

    const sections = useLabStore.getState().sections;
    expect(sections[0].id).toBe('s3');
    expect(sections[0].position).toBe(0);
    expect(sections[1].id).toBe('s2');
    expect(sections[1].position).toBe(1);
    expect(sections[2].id).toBe('s1');
    expect(sections[2].position).toBe(2);
  });
});

// ── test_makiety_remove — removeSection usuwa sekcję ─────────
describe('removeSection (remove)', () => {
  it('removes section from store optimistically', async () => {
    seedStore();
    expect(useLabStore.getState().sections).toHaveLength(3);

    const { removeSection } = useLabStore.getState();
    await removeSection('s2');

    const sections = useLabStore.getState().sections;
    expect(sections).toHaveLength(2);
    expect(sections.map(s => s.id)).toEqual(['s1', 's3']);
  });
});

// ── test_kreator_color_picker — updateSection zmienia bgColor ─
describe('updateSection — color picker', () => {
  it('updates section bgColor via optimistic store update', async () => {
    seedStore();
    const { updateSection } = useLabStore.getState();

    await updateSection('s1', { slots_json: { ...MOCK_SECTIONS[0].slots_json, bg: '#FF0000' } });

    const section = useLabStore.getState().sections.find(s => s.id === 's1');
    expect(section?.slots_json).toMatchObject({ heading: 'Hello', bg: '#FF0000' });
  });
});

// ── test_kreator_variant_switch — zmiana wariantu zachowuje treść ──
describe('updateSection — variant switch', () => {
  it('changes variant while preserving slots_json content', async () => {
    seedStore();
    const { updateSection } = useLabStore.getState();

    const originalSlots = useLabStore.getState().sections.find(s => s.id === 's1')?.slots_json;

    await updateSection('s1', { variant: 'B' });

    const section = useLabStore.getState().sections.find(s => s.id === 's1');
    expect(section?.variant).toBe('B');
    // slots_json is preserved (not wiped)
    expect(section?.slots_json).toEqual(originalSlots);
  });
});

// ── test_wizualizacja_tweaks — updateBrand zmienia font/kolor ──
describe('updateBrand (tweaks)', () => {
  it('updates brand font and color globally', async () => {
    seedStore();
    const { updateBrand } = useLabStore.getState();

    await updateBrand({ fontHeading: "'Playfair Display', serif", ctaColor: '#E11D48' });

    const brand = useLabStore.getState().brand;
    expect(brand.fontHeading).toBe("'Playfair Display', serif");
    expect(brand.ctaColor).toBe('#E11D48');
    // Unchanged fields preserved
    expect(brand.fontBody).toBe("'Inter', sans-serif");
    expect(brand.density).toBe('normal');
  });
});
