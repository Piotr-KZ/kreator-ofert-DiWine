// @vitest-environment jsdom
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { VisualConcept } from '@/store/labStore';

// ── Mocks ──────────────────────────────────────────────────────
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
  useParams: () => ({ projectId: 'test-123' }),
}));

const mockGenerate = vi.fn();
const mockSave = vi.fn();
const mockSetError = vi.fn();

let mockState = {
  visualConcept: null as VisualConcept | null,
  sections: [] as unknown[],
  style: { primary_color: '#6366F1', secondary_color: '#EC4899' },
  projectName: 'Test Projekt',
  generateVisualConcept: mockGenerate,
  saveVisualConcept: mockSave,
  isGenerating: false,
  error: null as string | null,
  setError: mockSetError,
};

vi.mock('@/store/labStore', () => ({
  useLabStore: () => mockState,
}));

vi.mock('@/api/client', () => ({
  getPreviewUrl: (id: string) => `http://localhost:8003/preview/${id}`,
  exportHtml: vi.fn(),
}));

import Step5Visual from '../Step5Visual';

// ── Tests ──────────────────────────────────────────────────────
describe('Step5Visual page', () => {
  beforeEach(() => {
    mockGenerate.mockClear();
    mockSetError.mockClear();
    mockState = { ...mockState, visualConcept: null, isGenerating: false, error: null };
  });

  it('calls generateVisualConcept on mount when no concept exists', () => {
    render(<Step5Visual />);
    expect(mockGenerate).toHaveBeenCalledTimes(1);
  });

  it('shows loading spinner while generating', () => {
    mockState = { ...mockState, isGenerating: true };
    render(<Step5Visual />);
    expect(screen.getByText(/generuje kreację wizualną/i)).toBeInTheDocument();
  });

  it('shows error message when error is set and not generating', () => {
    mockState = { ...mockState, isGenerating: false, error: 'Błąd API' };
    render(<Step5Visual />);
    expect(screen.getByText('Błąd API')).toBeInTheDocument();
  });

  it('shows "Generuj kreację wizualną" button when no concept and no error', () => {
    render(<Step5Visual />);
    expect(screen.getByText(/generuj kreację wizualną/i)).toBeInTheDocument();
  });

  it('renders visual toolbar with project name when concept exists', () => {
    mockState = {
      ...mockState,
      visualConcept: {
        style: 'modern',
        bg_approach: 'light',
        separator_type: 'none',
        sections: [
          { block_code: 'NA1', bg_type: 'white', bg_value: '', media_type: 'none', photo_query: null, separator_after: false },
          { block_code: 'HE1', bg_type: 'dark', bg_value: '', media_type: 'image', photo_query: 'office', separator_after: false },
        ],
      },
    };
    render(<Step5Visual />);
    expect(screen.getByText('Kreacja wizualna')).toBeInTheDocument();
    expect(screen.getByText('Test Projekt')).toBeInTheDocument();
  });

  it('shows Preview button and switches to preview on click', () => {
    mockState = {
      ...mockState,
      visualConcept: {
        style: 'modern',
        bg_approach: 'light',
        separator_type: 'none',
        sections: [
          { block_code: 'HE1', bg_type: 'white', bg_value: '', media_type: 'none', photo_query: null, separator_after: false },
        ],
      },
    };
    render(<Step5Visual />);
    const previewBtn = screen.getByText('Podgląd');
    fireEvent.click(previewBtn);
    // After click we should see the close preview button
    expect(screen.getByText(/zamknij podgląd/i)).toBeInTheDocument();
  });
});
