/**
 * Lab Creator Zustand store — single source of truth for 5-step flow.
 */

import { create } from "zustand";
import * as api from "@/api/client";
import { DEFAULT_BRAND, BLOCK_LIBRARY } from "@/types/lab";
import type { Brand, Gradient } from "@/types/lab";

export type { Brand, Gradient };

export interface Section {
  id: string;
  block_code: string;
  position: number;
  variant: string;
  slots_json: Record<string, unknown> | null;
  is_visible: boolean;
  // Brief 45 extended fields (stored in variant_config on backend)
  name?: string;
  bgColor?: string | Gradient | null;
  ctaColor?: string | Gradient | null;
  padding?: { top: number; right: number; bottom: number; left: number };
  brandWarning?: string;
  variant_config?: Record<string, unknown> | null;
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
  brand: Brand;

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
  setStep: (step: number) => void;
  setBrief: (field: string, value: string) => void;
  setStyle: (field: string, value: string) => void;
  setSiteType: (t: string) => void;
  setError: (e: string | null) => void;
  setBrand: (patch: Partial<Brand>) => void;
  updateSectionMeta: (sectionId: string, meta: Partial<Pick<Section, 'name' | 'bgColor' | 'ctaColor' | 'padding' | 'brandWarning'>>) => Promise<void>;
  duplicateSection: (sectionId: string) => Promise<void>;
  toggleHideSection: (sectionId: string) => void;
}

export const useLabStore = create<LabState>((set, get) => ({
  projectId: null,
  projectName: "",
  siteType: "company_card",
  brief: { description: "", target_audience: "", usp: "", tone: "profesjonalny", website: "" },
  style: { primary_color: "#4F46E5", secondary_color: "#F59E0B" },
  brand: { ...DEFAULT_BRAND },
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
      const styleJson = data.style_json || {};
      const loadedBrand: Brand = {
        ...DEFAULT_BRAND,
        ctaColor: styleJson.primary_color || DEFAULT_BRAND.ctaColor,
        ctaColor2: styleJson.secondary_color || DEFAULT_BRAND.ctaColor2,
        ...(styleJson.brand || {}),
      };
      // Hydrate section meta from variant_config
      const sections = (data.sections || []).map((s: Section) => {
        const vc = (s.variant_config || {}) as Record<string, unknown>;
        return {
          ...s,
          name: (vc.name as string) || BLOCK_LIBRARY.find(b => b.code === s.block_code)?.name || s.block_code,
          bgColor: (vc.bgColor as string | Gradient | null) ?? null,
          ctaColor: (vc.ctaColor as string | Gradient | null) ?? null,
          padding: (vc.padding as Section['padding']) ?? undefined,
        };
      });
      set({
        projectId: data.id,
        projectName: data.name,
        siteType: data.site_type || "company_card",
        brief: data.brief_json || { description: "", target_audience: "", usp: "", tone: "profesjonalny", website: "" },
        style: { primary_color: styleJson.primary_color || "#4F46E5", secondary_color: styleJson.secondary_color || "#F59E0B" },
        brand: loadedBrand,
        sections,
        visualConcept: data.visual_concept_json || null,
        currentStep: data.current_step || 1,
      });
    } finally {
      set({ isLoading: false });
    }
  },

  saveBrief: async () => {
    const { projectId, brief, brand, siteType } = get();
    if (!projectId) return;
    await api.updateProject(projectId, {
      brief_json: brief,
      style_json: {
        primary_color: brand.ctaColor,
        secondary_color: brand.ctaColor2,
        brand,                          // full Brand object stored here
      },
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
      const msg = e instanceof Error ? e.message : "Blad walidacji";
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
      const msg = e instanceof Error ? e.message : "Blad generowania struktury";
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
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Blad generowania visual concept";
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
      const msg = e instanceof Error ? e.message : "Blad generowania tresci";
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
      const msg = e instanceof Error ? e.message : "Błąd regeneracji sekcji";
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
      const msg = e instanceof Error ? e.message : "Błąd analizy strony";
      set({ error: msg });
      return null;
    } finally {
      set({ isGenerating: false });
    }
  },

  setStep: (step) => set({ currentStep: step }),
  setBrief: (field, value) => set({ brief: { ...get().brief, [field]: value } }),
  setStyle: (field, value) => set({ style: { ...get().style, [field]: value } }),
  setSiteType: (t) => set({ siteType: t }),
  setError: (e) => set({ error: e }),
  setBrand: (patch) => set({ brand: { ...get().brand, ...patch } }),

  updateSectionMeta: async (sectionId, meta) => {
    const { projectId } = get();
    if (!projectId) return;
    // Merge into variant_config on backend
    const section = get().sections.find(s => s.id === sectionId);
    const currentVc = (section?.variant_config || {}) as Record<string, unknown>;
    const newVc = { ...currentVc, ...meta };
    await api.updateSection(projectId, sectionId, { variant_config: newVc });
    set({
      sections: get().sections.map((s) =>
        s.id === sectionId ? { ...s, ...meta, variant_config: newVc } : s,
      ),
    });
  },

  duplicateSection: async (sectionId) => {
    const { projectId, sections } = get();
    if (!projectId) return;
    const orig = sections.find(s => s.id === sectionId);
    if (!orig) return;
    const pos = (orig.position ?? 0) + 1;
    const { data: resp } = await api.addSection(projectId, orig.block_code, pos);
    const newId: string | undefined = resp?.id ?? resp?.data?.id;
    if (orig.slots_json && newId) {
      await api.updateSection(projectId, newId, { slots_json: orig.slots_json });
    }
    await get().loadProject(projectId);
  },

  toggleHideSection: (sectionId) => {
    const orig = get().sections.find(s => s.id === sectionId);
    if (!orig) return;
    const newVisible = orig.is_visible !== false ? false : true;
    set({ sections: get().sections.map(s => s.id === sectionId ? { ...s, is_visible: newVisible } : s) });
    const { projectId } = get();
    if (projectId) {
      api.updateSection(projectId, sectionId, { is_visible: newVisible }).catch(() => {});
    }
  },
}));
