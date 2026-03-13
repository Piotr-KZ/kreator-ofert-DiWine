/**
 * Tests for WebCreator Steps 7-9.
 * Brief 35: 25 test specifications.
 *
 * NOTE: Requires Vitest + @testing-library/react.
 * These are test SPECIFICATIONS — they document expected behavior.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useCreatorStore } from "@/store/creatorStore";

// ─── Helper: render with router ───

function renderWithRouter(ui: React.ReactElement, path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/creator/:projectId/step/:step" element={ui} />
        <Route path="/creator/new" element={<div>New Project</div>} />
        <Route path="/dashboard" element={<div>Dashboard</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  useCreatorStore.getState().reset();
  useCreatorStore.setState({
    project: { id: "test-id", name: "Test Project" } as any,
    config: {},
    currentStep: 7,
  });
});

// ============================================================================
// Step7Config (10 tests)
// ============================================================================

describe("Step7Config", () => {
  it("renders 5 tabs", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    expect(screen.getByText("Formularze")).toBeTruthy();
    expect(screen.getByText("Social")).toBeTruthy();
    expect(screen.getByText("SEO")).toBeTruthy();
    expect(screen.getByText("Prawo")).toBeTruthy();
    expect(screen.getByText("Hosting")).toBeTruthy();
  });

  it("shows forms tab by default with email input", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    expect(screen.getByText("Formularze kontaktowe")).toBeTruthy();
    expect(screen.getByPlaceholderText("kontakt@firma.pl")).toBeTruthy();
  });

  it("switches to Social tab on click", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    fireEvent.click(screen.getByText("Social"));
    await waitFor(() => {
      expect(screen.getByText("Social Media")).toBeTruthy();
    });
  });

  it("shows SEO tab with char counters", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    fireEvent.click(screen.getByText("SEO"));
    await waitFor(() => {
      expect(screen.getByText(/Meta title/)).toBeTruthy();
      expect(screen.getByText(/\/60/)).toBeTruthy();
      expect(screen.getByText(/\/160/)).toBeTruthy();
    });
  });

  it("shows AI suggest button on SEO tab", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    fireEvent.click(screen.getByText("SEO"));
    await waitFor(() => {
      expect(screen.getByText("AI zaproponuj")).toBeTruthy();
    });
  });

  it("shows Legal tab with privacy policy radio", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    fireEvent.click(screen.getByText("Prawo"));
    await waitFor(() => {
      expect(screen.getByText("Polityka prywatności")).toBeTruthy();
      expect(screen.getByText("AI generuje")).toBeTruthy();
      expect(screen.getByText("Własna")).toBeTruthy();
    });
  });

  it("shows cookie banner toggle on Legal tab", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    fireEvent.click(screen.getByText("Prawo"));
    await waitFor(() => {
      expect(screen.getByText("Baner cookies")).toBeTruthy();
    });
  });

  it("shows Hosting tab with domain type radio", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    fireEvent.click(screen.getByText("Hosting"));
    await waitFor(() => {
      expect(screen.getByText("Typ domeny")).toBeTruthy();
      expect(screen.getByText("Subdomena FastHub")).toBeTruthy();
      expect(screen.getByText("Własna domena")).toBeTruthy();
    });
  });

  it("shows deploy method options", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    fireEvent.click(screen.getByText("Hosting"));
    await waitFor(() => {
      expect(screen.getByText("Automatycznie")).toBeTruthy();
      expect(screen.getByText("FTP")).toBeTruthy();
      expect(screen.getByText("Pobierz ZIP")).toBeTruthy();
    });
  });

  it("has Dalej button", async () => {
    const { default: Step7Config } = await import("@/pages/creator/Step7Config");
    renderWithRouter(<Step7Config />, "/creator/test-id/step/7");

    expect(screen.getByText(/Dalej/)).toBeTruthy();
  });
});

// ============================================================================
// Step8Readiness (8 tests)
// ============================================================================

describe("Step8Readiness", () => {
  it("renders title and description", async () => {
    vi.spyOn(useCreatorStore.getState(), "runReadinessCheck").mockResolvedValue({
      checks: [],
      can_publish: true,
      score: 0,
    });

    const { default: Step8Readiness } = await import("@/pages/creator/Step8Readiness");
    renderWithRouter(<Step8Readiness />, "/creator/test-id/step/8");

    expect(screen.getByText("Sprawdzenie gotowości")).toBeTruthy();
  });

  it("shows loading spinner initially", async () => {
    useCreatorStore.setState({ isValidating: true, readinessChecks: [] });
    vi.spyOn(useCreatorStore.getState(), "runReadinessCheck").mockImplementation(
      () => new Promise(() => {}),
    );

    const { default: Step8Readiness } = await import("@/pages/creator/Step8Readiness");
    renderWithRouter(<Step8Readiness />, "/creator/test-id/step/8");

    expect(screen.getByText("Sprawdzam...")).toBeTruthy();
  });

  it("shows score summary after check", async () => {
    useCreatorStore.setState({
      readinessChecks: [
        { key: "a", status: "pass", message: "OK" },
        { key: "b", status: "pass", message: "OK" },
        { key: "c", status: "warn", message: "Warn" },
      ],
    });
    vi.spyOn(useCreatorStore.getState(), "runReadinessCheck").mockResolvedValue({
      checks: [],
      can_publish: true,
      score: 2,
    });

    const { default: Step8Readiness } = await import("@/pages/creator/Step8Readiness");
    renderWithRouter(<Step8Readiness />, "/creator/test-id/step/8");

    expect(screen.getByText("2/3")).toBeTruthy();
  });

  it("shows checklist items with status icons", async () => {
    useCreatorStore.setState({
      readinessChecks: [
        { key: "pp", status: "pass", message: "Polityka prywatności OK" },
        { key: "seo", status: "warn", message: "Brak meta title" },
      ],
    });
    vi.spyOn(useCreatorStore.getState(), "runReadinessCheck").mockResolvedValue(null);

    const { default: Step8Readiness } = await import("@/pages/creator/Step8Readiness");
    renderWithRouter(<Step8Readiness />, "/creator/test-id/step/8");

    expect(screen.getByText("Polityka prywatności OK")).toBeTruthy();
    expect(screen.getByText("Brak meta title")).toBeTruthy();
  });

  it("shows Popraw button for fixable items", async () => {
    useCreatorStore.setState({
      readinessChecks: [
        { key: "pp", status: "error", message: "Brak polityki", fix_tab: "legal" },
      ],
    });
    vi.spyOn(useCreatorStore.getState(), "runReadinessCheck").mockResolvedValue(null);

    const { default: Step8Readiness } = await import("@/pages/creator/Step8Readiness");
    renderWithRouter(<Step8Readiness />, "/creator/test-id/step/8");

    expect(screen.getByText("Popraw →")).toBeTruthy();
  });

  it("disables Publikuję button when errors exist", async () => {
    useCreatorStore.setState({
      readinessChecks: [
        { key: "pp", status: "error", message: "Error" },
      ],
    });
    vi.spyOn(useCreatorStore.getState(), "runReadinessCheck").mockResolvedValue(null);

    const { default: Step8Readiness } = await import("@/pages/creator/Step8Readiness");
    renderWithRouter(<Step8Readiness />, "/creator/test-id/step/8");

    const btn = screen.getByText("Publikuję!");
    expect(btn.closest("button")?.disabled).toBe(true);
  });

  it("enables Publikuję button when no errors", async () => {
    useCreatorStore.setState({
      readinessChecks: [
        { key: "a", status: "pass", message: "OK" },
        { key: "b", status: "warn", message: "Warn" },
      ],
    });
    vi.spyOn(useCreatorStore.getState(), "runReadinessCheck").mockResolvedValue(null);

    const { default: Step8Readiness } = await import("@/pages/creator/Step8Readiness");
    renderWithRouter(<Step8Readiness />, "/creator/test-id/step/8");

    const btn = screen.getByText("Publikuję!");
    expect(btn.closest("button")?.disabled).toBe(false);
  });

  it("has Sprawdź ponownie button", async () => {
    useCreatorStore.setState({ readinessChecks: [] });
    vi.spyOn(useCreatorStore.getState(), "runReadinessCheck").mockResolvedValue(null);

    const { default: Step8Readiness } = await import("@/pages/creator/Step8Readiness");
    renderWithRouter(<Step8Readiness />, "/creator/test-id/step/8");

    expect(screen.getByText("Sprawdź ponownie")).toBeTruthy();
  });
});

// ============================================================================
// Step9Publish (7 tests)
// ============================================================================

describe("Step9Publish", () => {
  it("renders pre-publish summary", async () => {
    useCreatorStore.setState({
      config: {
        hosting: { domain_type: "subdomain", subdomain: "test-site", deploy_method: "auto" },
      },
    });

    const { default: Step9Publish } = await import("@/pages/creator/Step9Publish");
    renderWithRouter(<Step9Publish />, "/creator/test-id/step/9");

    expect(screen.getByText("Publikacja")).toBeTruthy();
    expect(screen.getByText("Test Project")).toBeTruthy();
    expect(screen.getByText("test-site.fasthub.site")).toBeTruthy();
  });

  it("shows deploy method in summary", async () => {
    useCreatorStore.setState({
      config: {
        hosting: { domain_type: "subdomain", subdomain: "test", deploy_method: "auto" },
      },
    });

    const { default: Step9Publish } = await import("@/pages/creator/Step9Publish");
    renderWithRouter(<Step9Publish />, "/creator/test-id/step/9");

    expect(screen.getByText("Automatycznie (FastHub)")).toBeTruthy();
  });

  it("shows Opublikuj button for auto deploy", async () => {
    useCreatorStore.setState({
      config: {
        hosting: { domain_type: "subdomain", subdomain: "test", deploy_method: "auto" },
      },
    });

    const { default: Step9Publish } = await import("@/pages/creator/Step9Publish");
    renderWithRouter(<Step9Publish />, "/creator/test-id/step/9");

    expect(screen.getByText("Opublikuj stronę")).toBeTruthy();
  });

  it("shows Pobierz ZIP for zip deploy", async () => {
    useCreatorStore.setState({
      config: {
        hosting: { domain_type: "subdomain", subdomain: "test", deploy_method: "zip" },
      },
    });

    const { default: Step9Publish } = await import("@/pages/creator/Step9Publish");
    renderWithRouter(<Step9Publish />, "/creator/test-id/step/9");

    expect(screen.getByText("Pobierz ZIP")).toBeTruthy();
  });

  it("shows loading state when publishing", async () => {
    useCreatorStore.setState({
      isPublishing: true,
      config: {
        hosting: { domain_type: "subdomain", subdomain: "test", deploy_method: "auto" },
      },
    });

    const { default: Step9Publish } = await import("@/pages/creator/Step9Publish");
    renderWithRouter(<Step9Publish />, "/creator/test-id/step/9");

    expect(screen.getByText("Publikuję...")).toBeTruthy();
  });

  it("shows success screen after publish", async () => {
    vi.spyOn(useCreatorStore.getState(), "publishProject").mockResolvedValue({
      subdomain: "test-site",
      url: "https://test-site.fasthub.site",
      status: "published",
      published_at: "2026-03-14T12:00:00",
    });

    useCreatorStore.setState({
      config: {
        hosting: { domain_type: "subdomain", subdomain: "test", deploy_method: "auto" },
      },
    });

    const { default: Step9Publish } = await import("@/pages/creator/Step9Publish");
    renderWithRouter(<Step9Publish />, "/creator/test-id/step/9");

    fireEvent.click(screen.getByText("Opublikuj stronę"));

    await waitFor(() => {
      expect(screen.getByText("Strona opublikowana!")).toBeTruthy();
    });
  });

  it("shows share buttons on success", async () => {
    vi.spyOn(useCreatorStore.getState(), "publishProject").mockResolvedValue({
      subdomain: "test-site",
      url: "https://test-site.fasthub.site",
      status: "published",
    });

    useCreatorStore.setState({
      config: {
        hosting: { domain_type: "subdomain", subdomain: "test", deploy_method: "auto" },
      },
    });

    const { default: Step9Publish } = await import("@/pages/creator/Step9Publish");
    renderWithRouter(<Step9Publish />, "/creator/test-id/step/9");

    fireEvent.click(screen.getByText("Opublikuj stronę"));

    await waitFor(() => {
      expect(screen.getByText("Facebook")).toBeTruthy();
      expect(screen.getByText("LinkedIn")).toBeTruthy();
      expect(screen.getByText("X (Twitter)")).toBeTruthy();
    });
  });
});
