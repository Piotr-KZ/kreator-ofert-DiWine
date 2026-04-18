/**
 * Tests for Brief 41: AI Visibility Tab — user interaction flow.
 * 16 tests covering the AI Visibility component behavior.
 *
 * NOTE: Requires Vitest + @testing-library/react (same setup as test_creator.test.tsx).
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import AIVisibilityTab from "@/components/creator/AIVisibilityTab";
import type { AIVisibilityData } from "@/types/creator";

// ─── Helper ───

function renderTab(data: AIVisibilityData = {}, onChange = vi.fn()) {
  return { ...render(<AIVisibilityTab data={data} onChange={onChange} />), onChange };
}

// ============================================================================
// Rendering (3 tests)
// ============================================================================

describe("AIVisibilityTab — Rendering", () => {
  it("renders header and description", () => {
    renderTab();
    expect(screen.getByText("Widoczność AI")).toBeTruthy();
    expect(screen.getByText(/Wyszukiwarki AI/)).toBeTruthy();
    expect(screen.getByText(/Te dane NIE pojawią się na stronie/)).toBeTruthy();
  });

  it("renders company description textarea", () => {
    renderTab();
    expect(screen.getByPlaceholderText(/Czym się zajmujesz/)).toBeTruthy();
  });

  it("renders two column headers for profiles and websites", () => {
    renderTab();
    expect(screen.getByText("Profile społecznościowe")).toBeTruthy();
    expect(screen.getByText("Strony www i serwisy")).toBeTruthy();
  });
});

// ============================================================================
// Company Description (2 tests)
// ============================================================================

describe("AIVisibilityTab — Company Description", () => {
  it("displays existing description", () => {
    const { onChange } = renderTab({ description: "Firma testowa z 10-letnim doświadczeniem." });
    const textarea = screen.getByPlaceholderText(/Czym się zajmujesz/) as HTMLTextAreaElement;
    expect(textarea.value).toBe("Firma testowa z 10-letnim doświadczeniem.");
  });

  it("calls onChange when description is typed", () => {
    const { onChange } = renderTab();
    const textarea = screen.getByPlaceholderText(/Czym się zajmujesz/);
    fireEvent.change(textarea, { target: { value: "Nowy opis" } });
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ description: "Nowy opis" }));
  });
});

// ============================================================================
// Social Profiles (2 tests)
// ============================================================================

describe("AIVisibilityTab — Social Profiles", () => {
  it("renders existing social profiles", () => {
    renderTab({
      social_profiles: [
        { name: "Facebook", url: "https://facebook.com/test" },
        { name: "LinkedIn", url: "https://linkedin.com/company/test" },
      ],
    });
    const inputs = screen.getAllByPlaceholderText("https://...");
    expect(inputs.length).toBeGreaterThanOrEqual(2);
  });

  it("has add profile button with suggestions dropdown", () => {
    renderTab();
    const addBtn = screen.getByText("+ Dodaj profil");
    expect(addBtn).toBeTruthy();
    fireEvent.click(addBtn);
    // Should show suggestions
    expect(screen.getByText("Facebook")).toBeTruthy();
    expect(screen.getByText("LinkedIn")).toBeTruthy();
    expect(screen.getByText("Instagram")).toBeTruthy();
  });
});

// ============================================================================
// Websites (1 test)
// ============================================================================

describe("AIVisibilityTab — Websites", () => {
  it("has add website button without dropdown suggestions", () => {
    renderTab();
    const addBtn = screen.getByText("+ Dodaj stronę");
    expect(addBtn).toBeTruthy();
  });
});

// ============================================================================
// Company Categories (3 tests)
// ============================================================================

describe("AIVisibilityTab — Company Categories", () => {
  it("shows add category dropdown", () => {
    renderTab();
    const addCatBtn = screen.getAllByText(/Dodaj kategorię/);
    expect(addCatBtn.length).toBeGreaterThanOrEqual(1);
  });

  it("renders existing categories with items", () => {
    renderTab({
      categories: {
        uslugi: [
          { name: "Google Ads", description: "Kampanie PPC" },
          { name: "SEO", description: "Pozycjonowanie stron" },
        ],
      },
    });
    expect(screen.getByText("Usługi")).toBeTruthy();
    const nameInputs = screen.getAllByPlaceholderText("Nazwa");
    expect(nameInputs.length).toBeGreaterThanOrEqual(2);
  });

  it("calls onChange when adding a category item", () => {
    const { onChange } = renderTab({
      categories: {
        uslugi: [],
      },
    });
    const addBtn = screen.getByText(/Dodaj usługi/i);
    fireEvent.click(addBtn);
    expect(onChange).toHaveBeenCalled();
  });
});

// ============================================================================
// People (3 tests)
// ============================================================================

describe("AIVisibilityTab — People", () => {
  it("renders Kluczowe osoby header and add button", () => {
    renderTab();
    expect(screen.getByText("Kluczowe osoby")).toBeTruthy();
    expect(screen.getByText("+ Dodaj osobę")).toBeTruthy();
  });

  it("calls onChange when adding a person", () => {
    const { onChange } = renderTab();
    fireEvent.click(screen.getByText("+ Dodaj osobę"));
    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({
        people: [expect.objectContaining({ name: "", title: "" })],
      }),
    );
  });

  it("renders existing person with name and title", () => {
    renderTab({
      people: [
        { name: "Jan Kowalski", title: "CEO", categories: {} },
      ],
    });
    expect(screen.getByText(/Jan Kowalski/)).toBeTruthy();
    expect(screen.getByText(/CEO/)).toBeTruthy();
    expect(screen.getByDisplayValue("Jan Kowalski")).toBeTruthy();
  });
});

// ============================================================================
// Person Categories (2 tests)
// ============================================================================

describe("AIVisibilityTab — Person Categories", () => {
  it("renders person category items for kompetencje", () => {
    renderTab({
      people: [
        {
          name: "Jan",
          title: "Dev",
          categories: {
            kompetencje: [
              { name: "Python", description: "10 lat doświadczenia" },
            ],
          },
        },
      ],
    });
    expect(screen.getByText("Kompetencje")).toBeTruthy();
    expect(screen.getByDisplayValue("Python")).toBeTruthy();
  });

  it("renders special fields for doswiadczenie (period)", () => {
    renderTab({
      people: [
        {
          name: "Jan",
          title: "Dev",
          categories: {
            doswiadczenie: [
              { name: "FirmaABC", period: "2010-2020", description: "Developer" },
            ],
          },
        },
      ],
    });
    expect(screen.getByDisplayValue("FirmaABC")).toBeTruthy();
    expect(screen.getByDisplayValue("2010-2020")).toBeTruthy();
    expect(screen.getByPlaceholderText("np. 2010-2020")).toBeTruthy();
  });
});
