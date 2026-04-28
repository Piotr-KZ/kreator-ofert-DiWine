/**
 * Lab Creator Zustand store — single source of truth for 5-step flow.
 */

import axios from "axios";
import { create } from "zustand";
import * as api from "@/api/client";

/** Extract user-friendly message from Axios / generic errors. */
function extractError(e: unknown, fallback = "Wystąpił błąd"): string {
  if (axios.isAxiosError(e)) {
    return e.response?.data?.detail || e.message || fallback;
  }
  return e instanceof Error ? e.message : fallback;
}

export interface Section {
  id: string;
  block_code: string;
  position: number;
  variant: string;
  slots_json: Record<string, unknown> | null;
  is_visible: boolean;
}

export interface VisualConceptSection {
  block_code: string;
  bg_type: string;
  bg_value: string;
  media_type: string;
  photo_query: string | null;
  separator_after: boolean;
}

export interface VisualConcept {
  style: string;
  bg_approach: string;
  separator_type: string;
  sections: VisualConceptSection[];
}

interface LabState {
  // Project
  projectId: string | null;
  projectName: string;
  siteType: string;

  // Step 1: Brief + Style
  brief: {
    description: string;
    target_audience: string;
    usp: string;
    tone: string;
    website: string;
  };
  style: {
    primary_color: string;
    secondary_color: string;
  };

  // Brand (Step 5 visual tweaks)
  brand: {
    fontHeading: string;
    fontBody: string;
    ctaColor: string;
    density: string;
  };

  // Step 2: Structure
  sections: Section[];

  // Step 3: Visual Concept
  visualConcept: VisualConcept | null;

  // UI state
  currentStep: number;
  isLoading: boolean;
  isGenerating: boolean;
  error: string | null;

  // Actions
  createProject: (name: string, siteType: string) => Promise<string>;
  loadProject: (id: string) => Promise<void>;
  saveBrief: () => Promise<void>;

  validateBrief: () => Promise<Array<{type: string; message: string; field?: string}>>;
  generateStructure: () => Promise<void>;
  addSection: (blockCode: string, position?: number) => Promise<void>;
  removeSection: (sectionId: string) => Promise<void>;
  reorderSections: (ids: string[]) => Promise<void>;
  updateSection: (sectionId: string, data: Record<string, unknown>) => Promise<void>;

  generateVisualConcept: () => Promise<void>;
  saveVisualConcept: (vc: VisualConcept) => Promise<void>;

  generateContent: () => Promise<void>;
  regenerateSection: (sectionId: string, instruction?: string) => Promise<void>;

  analyzeWebsite: () => Promise<Record<string, unknown> | null>;
  updateSlot: (sectionId: string, key: string, value: string) => Promise<void>;
  duplicateSection: (sectionId: string) => Promise<void>;
  updateBrand: (updates: Partial<LabState['brand']>) => Promise<void>;
  setStep: (step: number) => void;
  setBrief: (field: string, value: string) => void;
  setStyle: (field: string, value: string) => void;
  setSiteType: (t: string) => void;
  setError: (e: string | null) => void;
}

export const useLabStore = create<LabState>((set, get) => ({
  projectId: null,
  projectName: "",
  siteType: "company_card",
  brief: { description: "", target_audience: "", usp: "", tone: "profesjonalny", website: "" },
  style: { primary_color: "#4F46E5", secondary_color: "#F59E0B" },
  brand: { fontHeading: "'Fraunces', serif", fontBody: "'Inter', sans-serif", ctaColor: "#6FAE8C", density: "normal" },
  sections: [],
  visualConcept: null,
  currentStep: 1,
  isLoading: false,
  isGenerating: false,
  error: null,

  createProject: async (name, siteType) => {
    const { data } = await api.createProject(name, siteType);
    set({ projectId: data.id, projectName: name, siteType });
    return data.id;
  },

  loadProject: async (id) => {
    set({ isLoading: true });
    try {
      const { data } = await api.getProject(id);
      set({
        projectId: data.id,
        projectName: data.name,
        siteType: data.site_type || "company_card",
        brief: data.brief_json || { description: "", target_audience: "", usp: "", tone: "profesjonalny", website: "" },
        style: data.style_json || { primary_color: "#4F46E5", secondary_color: "#F59E0B" },
        sections: data.sections || [],
        visualConcept: data.visual_concept_json || null,
        currentStep: data.current_step || 1,
      });
    } finally {
      set({ isLoading: false });
    }
  },

  saveBrief: async () => {
    const { projectId, brief, style, siteType } = get();
    if (!projectId) return;
    await api.updateProject(projectId, {
      brief_json: brief,
      style_json: style,
      site_type: siteType,
    });
  },

  validateBrief: async () => {
    const { projectId } = get();
    if (!projectId) return [];
    set({ isGenerating: true, error: null });
    try {
      const { data } = await api.validateBrief(projectId);
      return data.items || [];
    } catch (e: unknown) {
      const msg = extractError(e, "Blad walidacji");
      set({ error: msg });
      return [];
    } finally {
      set({ isGenerating: false });
    }
  },

  generateStructure: async () => {
    const { projectId } = get();
    if (!projectId) return;
    set({ isGenerating: true, error: null });
    try {
      await api.generateStructure(projectId);
      // Reload project to get sections
      await get().loadProject(projectId);
      set({ currentStep: 3 });
    } catch (e: unknown) {
      const msg = extractError(e, "Blad generowania struktury");
      set({ error: msg });
    } finally {
      set({ isGenerating: false });
    }
  },

  addSection: async (blockCode, position) => {
    const { projectId, sections } = get();
    if (!projectId) return;
    const pos = position !== undefined ? position : sections.length;
    await api.addSection(projectId, blockCode, pos);
    await get().loadProject(projectId);
  },

  removeSection: async (sectionId) => {
    const { projectId } = get();
    if (!projectId) return;
    await api.deleteSection(projectId, sectionId);
    set({ sections: get().sections.filter((s) => s.id !== sectionId) });
  },

  reorderSections: async (ids) => {
    const { projectId } = get();
    if (!projectId) return;
    await api.reorderSections(projectId, ids);
    // Optimistic update
    const sectionMap = new Map(get().sections.map((s) => [s.id, s]));
    const reordered = ids.map((id, i) => {
      const s = sectionMap.get(id)!;
      return { ...s, position: i };
    });
    set({ sections: reordered });
  },

  updateSection: async (sectionId, data) => {
    const { projectId } = get();
    if (!projectId) return;
    await api.updateSection(projectId, sectionId, data);
    set({
      sections: get().sections.map((s) =>
        s.id === sectionId ? { ...s, ...data } : s,
      ),
    });
  },

  generateVisualConcept: async () => {
    const { projectId } = get();
    if (!projectId) return;
    set({ isGenerating: true, error: null });
    try {
      const { data } = await api.generateVisualConcept(projectId);
      set({ visualConcept: data, currentStep: 5 });
      // Reload project to get sections with resolved Unsplash image URLs
      await get().loadProject(projectId);
    } catch (e: unknown) {
      const msg = extractError(e, "Blad generowania visual concept");
      set({ error: msg });
    } finally {
      set({ isGenerating: false });
    }
  },

  saveVisualConcept: async (vc) => {
    const { projectId } = get();
    if (!projectId) return;
    await api.saveVisualConcept(projectId, vc as unknown as Record<string, unknown>);
    set({ visualConcept: vc });
  },

  generateContent: async () => {
    const { projectId } = get();
    if (!projectId) return;
    set({ isGenerating: true, error: null });
    try {
      await api.generateContent(projectId);
      // Reload to get updated sections with content
      await get().loadProject(projectId);
      set({ currentStep: 4 });
    } catch (e: unknown) {
      const msg = extractError(e, "Blad generowania tresci");
      set({ error: msg });
    } finally {
      set({ isGenerating: false });
    }
  },

  regenerateSection: async (sectionId, instruction) => {
    const { projectId } = get();
    if (!projectId) return;
    set({ isGenerating: true, error: null });
    try {
      const { data } = await api.regenerateSection(projectId, sectionId, instruction);
      if (data.slots_json && Object.keys(data.slots_json).length > 0) {
        set({
          sections: get().sections.map((s) =>
            s.id === sectionId ? { ...s, slots_json: data.slots_json } : s,
          ),
        });
      }
    } catch (e: unknown) {
      const msg = extractError(e, "Błąd regeneracji sekcji");
      set({ error: msg });
    } finally {
      set({ isGenerating: false });
    }
  },

  analyzeWebsite: async () => {
    const { projectId, brief } = get();
    if (!projectId || !brief.website) return null;
    set({ isGenerating: true, error: null });
    try {
      const { data } = await api.analyzeWebsite(projectId, brief.website);
      if (data.error) {
        set({ error: data.error });
        return null;
      }
      return data;
    } catch (e: unknown) {
      const msg = extractError(e, "Błąd analizy strony");
      set({ error: msg });
      return null;
    } finally {
      set({ isGenerating: false });
    }
  },

  updateSlot: async (sectionId, key, value) => {
    const { projectId, sections } = get();
    if (!projectId) return;
    const section = sections.find((s) => s.id === sectionId);
    if (!section) return;
    const newSlots = { ...(section.slots_json || {}), [key]: value };
    await api.updateSection(projectId, sectionId, { slots_json: newSlots });
    set({
      sections: sections.map((s) =>
        s.id === sectionId ? { ...s, slots_json: newSlots } : s
      ),
    });
  },

  duplicateSection: async (sectionId) => {
    const { projectId } = get();
    if (!projectId) return;
    await api.duplicateSection(projectId, sectionId);
    await get().loadProject(projectId);
  },

  updateBrand: async (updates) => {
    const { projectId } = get();
    const newBrand = { ...get().brand, ...updates };
    set({ brand: newBrand });
    if (projectId) {
      await api.updateProject(projectId, { brand_json: newBrand });
    }
  },

  setStep: (step) => set({ currentStep: step }),
  setBrief: (field, value) => set({ brief: { ...get().brief, [field]: value } }),
  setStyle: (field, value) => set({ style: { ...get().style, [field]: value } }),
  setSiteType: (t) => set({ siteType: t }),
  setError: (e) => set({ error: e }),
}));
