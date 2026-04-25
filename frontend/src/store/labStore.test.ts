import { describe, it, expect, beforeEach } from 'vitest';
import { useLabStore } from './labStore';

// Reset store before each test to avoid cross-test pollution
beforeEach(() => {
  useLabStore.setState({
    projectId: null,
    projectName: '',
    siteType: 'company_card',
    brief: { description: '', target_audience: '', usp: '', tone: 'profesjonalny', website: '' },
    style: { primary_color: '#4F46E5', secondary_color: '#F59E0B' },
    sections: [],
    visualConcept: null,
    currentStep: 1,
    isLoading: false,
    isGenerating: false,
    error: null,
  });
});

describe('labStore — initial state', () => {
  it('projectId is null by default', () => {
    const { projectId } = useLabStore.getState();
    expect(projectId).toBeNull();
  });

  it('sections is an empty array by default', () => {
    const { sections } = useLabStore.getState();
    expect(sections).toEqual([]);
  });

  it('isGenerating is false by default', () => {
    const { isGenerating } = useLabStore.getState();
    expect(isGenerating).toBe(false);
  });
});

describe('labStore — actions', () => {
  it('setBrief updates the specified field', () => {
    const { setBrief } = useLabStore.getState();
    setBrief('description', 'Firma budowlana z 20-letnim doświadczeniem');
    const { brief } = useLabStore.getState();
    expect(brief.description).toBe('Firma budowlana z 20-letnim doświadczeniem');
    // Other fields unchanged
    expect(brief.tone).toBe('profesjonalny');
  });

  it('setBrand merges partial patch without overwriting other fields', () => {
    const { setBrand } = useLabStore.getState();
    const before = useLabStore.getState().brand;
    setBrand({ ctaColor: '#FF0000' });
    const { brand } = useLabStore.getState();
    expect(brand.ctaColor).toBe('#FF0000');
    // Other brand fields preserved
    expect(brand.bgColor).toBe(before.bgColor);
    expect(brand.fontHeading).toBe(before.fontHeading);
  });

  it('setError stores error string and can be cleared', () => {
    const { setError } = useLabStore.getState();
    setError('Błąd połączenia z serwerem');
    expect(useLabStore.getState().error).toBe('Błąd połączenia z serwerem');
    setError(null);
    expect(useLabStore.getState().error).toBeNull();
  });
});
