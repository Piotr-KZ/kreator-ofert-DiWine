/**
 * Zustand store for WebCreator (Brief 32 + 34).
 */

import { create } from "zustand";
import * as api from "@/api/creator";
import type {
  BriefData,
  ChatMessage,
  CheckItem,
  ConfigData,
  GenerateProgress,
  Project,
  ProjectMaterial,
  ProjectSection,
  PublishResult,
  ReadinessResult,
  StyleData,
  ValidationItem,
} from "@/types/creator";

const EMPTY_BRIEF: BriefData = {
  forWhom: "",
  siteType: "",
  companyName: "",
  whatYouDo: "",
  hasWebsite: false,
  currentUrl: "",
  industry: "",
  clientTypes: [],
  clientB2B: "",
  clientB2C: "",
  clientB2G: "",
  clientNGO: "",
  decisionMaker: "",
  clientValues: "",
  clientLikes: "",
  clientDislikes: "",
  clientNeeds: "",
  slogan: "",
  mission: "",
  usp: "",
  whyChooseUs: "",
  strengths: [],
  brandPos: "",
  writingStyle: "",
  mainGoal: "",
  siteContent: [],
  impressionCustom: "",
  impThink: [],
  impFeel: [],
  menuProposal: "",
  openToAI: false,
  extraWishes: "",
  contentVision: "",
};

const EMPTY_STYLE: StyleData = {
  palette_preset: "",
  color_primary: "",
  color_secondary: "",
  color_accent: "",
  heading_font: "",
  body_font: "",
  section_theme: "",
  border_radius: "rounded",
};

interface CreatorState {
  // Data
  project: Project | null;
  brief: BriefData;
  materials: ProjectMaterial[];
  style: StyleData;
  validationItems: ValidationItem[];
  chatMessages: ChatMessage[];
  sections: ProjectSection[];
  renderedHtml: string;
  renderedCss: string;
  config: ConfigData;
  readinessChecks: CheckItem[];
  isPublishing: boolean;
  publishResult: PublishResult | null;

  // Status
  isLoading: boolean;
  isSaving: boolean;
  lastSavedAt: Date | null;
  currentStep: number;
  isValidating: boolean;
  isChatting: boolean;
  isGenerating: boolean;
  generateProgress: GenerateProgress | null;
  activeSection: string | null;

  // Actions
  loadProject: (projectId: string) => Promise<void>;
  setBrief: (data: Partial<BriefData>) => void;
  setStyle: (data: Partial<StyleData>) => void;
  saveBrief: () => Promise<void>;
  saveStyle: () => Promise<void>;
  uploadMaterial: (file: File, type: string) => Promise<void>;
  addLink: (url: string, type: string, description?: string) => Promise<void>;
  deleteMaterial: (materialId: string) => Promise<void>;
  runValidation: () => Promise<void>;
  sendChatMessage: (message: string, context?: string) => Promise<void>;
  setStep: (step: number) => void;
  reset: () => void;

  // Brief 35 actions
  saveConfig: (data: Partial<ConfigData>) => Promise<void>;
  loadConfig: () => Promise<void>;
  runReadinessCheck: () => Promise<ReadinessResult | null>;
  publishProject: () => Promise<PublishResult | null>;
  exportZip: () => Promise<void>;

  // Brief 34 actions
  loadSections: () => Promise<void>;
  addSection: (blockCode: string, variant?: string) => Promise<ProjectSection | null>;
  updateSection: (sectionId: string, data: Partial<ProjectSection>) => Promise<void>;
  removeSection: (sectionId: string) => Promise<void>;
  reorderSections: (order: string[]) => Promise<void>;
  generateSite: () => Promise<boolean>;
  regenerateSection: (sectionId: string, instruction?: string) => Promise<void>;
  loadRenderedPage: () => Promise<void>;
  setActiveSection: (sectionId: string | null) => void;
}

export const useCreatorStore = create<CreatorState>((set, get) => ({
  project: null,
  brief: { ...EMPTY_BRIEF },
  materials: [],
  style: { ...EMPTY_STYLE },
  validationItems: [],
  chatMessages: [],
  sections: [],
  renderedHtml: "",
  renderedCss: "",
  config: {},
  readinessChecks: [],
  isPublishing: false,
  publishResult: null,
  isLoading: false,
  isSaving: false,
  lastSavedAt: null,
  currentStep: 1,
  isValidating: false,
  isChatting: false,
  isGenerating: false,
  generateProgress: null,
  activeSection: null,

  loadProject: async (projectId: string) => {
    set({ isLoading: true });
    try {
      const { data: project } = await api.getProject(projectId);
      const { data: materials } = await api.listMaterials(projectId);

      set({
        project,
        brief: { ...EMPTY_BRIEF, ...(project.brief_json || {}) },
        style: { ...EMPTY_STYLE, ...(project.style_json || {}) },
        materials,
        validationItems: project.validation_json?.items || [],
        currentStep: project.current_step || 1,
        isLoading: false,
      });

      // Load sections if beyond step 4
      if ((project.current_step || 1) >= 5) {
        const { data: sections } = await api.listSections(projectId);
        set({ sections });
      }
    } catch (e) {
      console.error("Failed to load project:", e);
      set({ isLoading: false });
    }
  },

  setBrief: (data) => {
    set((s) => ({ brief: { ...s.brief, ...data } }));
  },

  setStyle: (data) => {
    set((s) => ({ style: { ...s.style, ...data } }));
  },

  saveBrief: async () => {
    const { project, brief } = get();
    if (!project) return;
    set({ isSaving: true });
    try {
      await api.saveBrief(project.id, brief);
      set({ isSaving: false, lastSavedAt: new Date() });
    } catch (e) {
      console.error("Failed to save brief:", e);
      set({ isSaving: false });
    }
  },

  saveStyle: async () => {
    const { project, style } = get();
    if (!project) return;
    set({ isSaving: true });
    try {
      await api.saveStyle(project.id, style);
      set({ isSaving: false, lastSavedAt: new Date() });
    } catch (e) {
      console.error("Failed to save style:", e);
      set({ isSaving: false });
    }
  },

  uploadMaterial: async (file, type) => {
    const { project } = get();
    if (!project) return;
    try {
      const { data: material } = await api.uploadMaterial(project.id, file, type);
      set((s) => ({ materials: [...s.materials, material] }));
    } catch (e) {
      console.error("Failed to upload material:", e);
    }
  },

  addLink: async (url, type, description) => {
    const { project } = get();
    if (!project) return;
    try {
      const { data: material } = await api.addLinkMaterial(project.id, url, type, description);
      set((s) => ({ materials: [...s.materials, material] }));
    } catch (e) {
      console.error("Failed to add link:", e);
    }
  },

  deleteMaterial: async (materialId) => {
    const { project } = get();
    if (!project) return;
    try {
      await api.deleteMaterial(project.id, materialId);
      set((s) => ({
        materials: s.materials.filter((m) => m.id !== materialId),
      }));
    } catch (e) {
      console.error("Failed to delete material:", e);
    }
  },

  runValidation: async () => {
    const { project } = get();
    if (!project) return;
    set({ isValidating: true });
    try {
      const { data } = await api.runValidation(project.id);
      set({ validationItems: data.items, isValidating: false });
    } catch (e) {
      console.error("Failed to run validation:", e);
      set({ isValidating: false });
    }
  },

  sendChatMessage: async (message, context = "validation") => {
    const { project, chatMessages } = get();
    if (!project) return;

    const userMsg: ChatMessage = { role: "user", content: message };
    const assistantMsg: ChatMessage = { role: "assistant", content: "" };
    set({
      chatMessages: [...chatMessages, userMsg, assistantMsg],
      isChatting: true,
    });

    try {
      await api.sendChatMessage(
        project.id,
        context,
        message,
        (text) => {
          set((s) => {
            const msgs = [...s.chatMessages];
            const last = msgs[msgs.length - 1];
            if (last?.role === "assistant") {
              msgs[msgs.length - 1] = { ...last, content: last.content + text };
            }
            return { chatMessages: msgs };
          });
        },
        () => {
          set({ isChatting: false });
        },
      );
    } catch (e) {
      console.error("Chat error:", e);
      set({ isChatting: false });
    }
  },

  setStep: (step) => set({ currentStep: step }),

  // ─── Brief 35 actions ───

  saveConfig: async (data) => {
    const { project } = get();
    if (!project) return;
    set({ isSaving: true });
    try {
      const { data: result } = await api.saveConfig(project.id, data);
      set({ config: result.config_json, isSaving: false, lastSavedAt: new Date() });
    } catch (e) {
      console.error("Failed to save config:", e);
      set({ isSaving: false });
    }
  },

  loadConfig: async () => {
    const { project } = get();
    if (!project) return;
    try {
      const { data: result } = await api.getConfig(project.id);
      set({ config: result.config_json });
    } catch (e) {
      console.error("Failed to load config:", e);
    }
  },

  runReadinessCheck: async () => {
    const { project } = get();
    if (!project) return null;
    set({ isValidating: true });
    try {
      const { data: result } = await api.checkReadiness(project.id);
      set({ readinessChecks: result.checks, isValidating: false });
      return result;
    } catch (e) {
      console.error("Failed to run readiness check:", e);
      set({ isValidating: false });
      return null;
    }
  },

  publishProject: async () => {
    const { project } = get();
    if (!project) return null;
    set({ isPublishing: true });
    try {
      const { data: result } = await api.publishProject(project.id);
      set({ isPublishing: false, publishResult: result });
      return result;
    } catch (e) {
      console.error("Failed to publish project:", e);
      set({ isPublishing: false });
      return null;
    }
  },

  exportZip: async () => {
    const { project } = get();
    if (!project) return;
    try {
      const { data: blob } = await api.exportZip(project.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${project.name.replace(/\s+/g, "_")}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Failed to export ZIP:", e);
    }
  },

  // ─── Brief 34 actions ───

  loadSections: async () => {
    const { project } = get();
    if (!project) return;
    try {
      const { data: sections } = await api.listSections(project.id);
      set({ sections });
    } catch (e) {
      console.error("Failed to load sections:", e);
    }
  },

  addSection: async (blockCode, variant = "A") => {
    const { project } = get();
    if (!project) return null;
    try {
      const { data: section } = await api.addSection(project.id, blockCode, variant);
      set((s) => ({ sections: [...s.sections, section] }));
      return section;
    } catch (e) {
      console.error("Failed to add section:", e);
      return null;
    }
  },

  updateSection: async (sectionId, data) => {
    const { project } = get();
    if (!project) return;
    try {
      const { data: updated } = await api.updateSection(project.id, sectionId, data);
      set((s) => ({
        sections: s.sections.map((sec) => (sec.id === sectionId ? updated : sec)),
      }));
    } catch (e) {
      console.error("Failed to update section:", e);
    }
  },

  removeSection: async (sectionId) => {
    const { project } = get();
    if (!project) return;
    try {
      await api.deleteSection(project.id, sectionId);
      set((s) => ({
        sections: s.sections.filter((sec) => sec.id !== sectionId),
        activeSection: s.activeSection === sectionId ? null : s.activeSection,
      }));
    } catch (e) {
      console.error("Failed to delete section:", e);
    }
  },

  reorderSections: async (order) => {
    const { project } = get();
    if (!project) return;
    // Optimistic: reorder locally
    set((s) => {
      const map = new Map(s.sections.map((sec) => [sec.id, sec]));
      const reordered = order.map((id, i) => {
        const sec = map.get(id);
        return sec ? { ...sec, position: i } : null;
      }).filter(Boolean) as ProjectSection[];
      return { sections: reordered };
    });
    try {
      await api.reorderSections(project.id, order);
    } catch (e) {
      console.error("Failed to reorder sections:", e);
      // Reload to fix
      get().loadSections();
    }
  },

  generateSite: async () => {
    const { project } = get();
    if (!project) return false;
    set({ isGenerating: true, generateProgress: null });
    try {
      await api.generateSite(project.id, (progress) => {
        set({ generateProgress: progress });
      });
      // Reload sections after generation
      const { data: sections } = await api.listSections(project.id);
      set({
        isGenerating: false,
        sections,
        currentStep: 5,
      });
      return true;
    } catch (e) {
      console.error("Failed to generate site:", e);
      set({ isGenerating: false });
      return false;
    }
  },

  regenerateSection: async (sectionId, instruction) => {
    const { project } = get();
    if (!project) return;
    set({ isSaving: true });
    try {
      const { data } = await api.generateSectionContent(project.id, sectionId, instruction);
      set((s) => ({
        sections: s.sections.map((sec) =>
          sec.id === sectionId ? { ...sec, slots_json: data.slots } : sec,
        ),
        isSaving: false,
      }));
    } catch (e) {
      console.error("Failed to regenerate section:", e);
      set({ isSaving: false });
    }
  },

  loadRenderedPage: async () => {
    const { project } = get();
    if (!project) return;
    try {
      const { data } = await api.renderPage(project.id);
      set({ renderedHtml: data.html, renderedCss: data.css });
    } catch (e) {
      console.error("Failed to load rendered page:", e);
    }
  },

  setActiveSection: (sectionId) => set({ activeSection: sectionId }),

  reset: () =>
    set({
      project: null,
      brief: { ...EMPTY_BRIEF },
      materials: [],
      style: { ...EMPTY_STYLE },
      validationItems: [],
      chatMessages: [],
      sections: [],
      renderedHtml: "",
      renderedCss: "",
      config: {},
      readinessChecks: [],
      isPublishing: false,
      publishResult: null,
      isLoading: false,
      isSaving: false,
      lastSavedAt: null,
      currentStep: 1,
      isGenerating: false,
      generateProgress: null,
      activeSection: null,
    }),
}));
