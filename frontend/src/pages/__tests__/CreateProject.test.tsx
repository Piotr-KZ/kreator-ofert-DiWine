// @vitest-environment jsdom
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// ── Mocks ──────────────────────────────────────────────────────
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

const mockCreateProject = vi.fn().mockResolvedValue('proj-abc');
vi.mock('@/store/labStore', () => ({
  useLabStore: (selector: (s: unknown) => unknown) =>
    selector({ createProject: mockCreateProject }),
}));

vi.mock('@/api/client', () => ({
  listSiteTypes: () => Promise.resolve({ data: [
    { value: 'company_card', label: 'Strona firmowa' },
    { value: 'portfolio', label: 'Portfolio' },
  ]}),
}));

import CreateProject from '../CreateProject';

// ── Tests ──────────────────────────────────────────────────────
describe('CreateProject page', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    mockCreateProject.mockClear();
  });

  it('renders Lab Creator heading', () => {
    render(<CreateProject />);
    expect(screen.getByText('Lab Creator')).toBeInTheDocument();
  });

  it('renders project name input', () => {
    render(<CreateProject />);
    expect(screen.getByPlaceholderText('np. Firma XYZ')).toBeInTheDocument();
  });

  it('submit button is disabled when name is empty', () => {
    render(<CreateProject />);
    const btn = screen.getByRole('button', { name: /stworz projekt/i });
    expect(btn).toBeDisabled();
  });

  it('submit button is enabled after typing a name', () => {
    render(<CreateProject />);
    const input = screen.getByPlaceholderText('np. Firma XYZ');
    fireEvent.change(input, { target: { value: 'Moja Firma' } });
    const btn = screen.getByRole('button', { name: /stworz projekt/i });
    expect(btn).not.toBeDisabled();
  });

  it('calls createProject and navigates on submit', async () => {
    render(<CreateProject />);
    const input = screen.getByPlaceholderText('np. Firma XYZ');
    fireEvent.change(input, { target: { value: 'Moja Firma' } });
    const btn = screen.getByRole('button', { name: /stworz projekt/i });
    fireEvent.click(btn);
    // wait for async
    await vi.waitFor(() => {
      expect(mockCreateProject).toHaveBeenCalledWith('Moja Firma', 'company_card');
      expect(mockNavigate).toHaveBeenCalledWith('/lab/proj-abc/step/1');
    });
  });
});
