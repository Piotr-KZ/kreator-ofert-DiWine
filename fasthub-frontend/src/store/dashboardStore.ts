/**
 * Dashboard store — Brief 36.
 * Manages sites list, stats, integrations, submissions for dashboard pages.
 */

import { create } from "zustand";
import {
  listProjects,
  getProjectStats,
  getIntegrationsCatalog,
  getAutomationTemplates,
  listSiteIntegrations,
  connectIntegration as apiConnect,
  disconnectIntegration as apiDisconnect,
  listFormSubmissions,
  markSubmissionRead as apiMarkRead,
} from "@/api/creator";
import type {
  AutomationGroup,
  FormSubmission,
  IntegrationCategory,
  Project,
  ProjectStats,
  SiteIntegration,
} from "@/types/creator";

type ActiveTab = "stats" | "integrations" | "automations" | "forms" | "seo";

interface DashboardState {
  // Data
  sites: Project[];
  selectedSiteId: string | null;
  stats: ProjectStats | null;
  integrations: SiteIntegration[];
  catalog: IntegrationCategory[];
  automations: AutomationGroup[];
  submissions: FormSubmission[];
  activeTab: ActiveTab;

  // Loading
  loading: boolean;
  error: string | null;

  // Actions
  loadSites: () => Promise<void>;
  selectSite: (siteId: string) => void;
  setActiveTab: (tab: ActiveTab) => void;
  loadStats: (projectId: string, period?: string) => Promise<void>;
  loadCatalog: () => Promise<void>;
  loadAutomations: () => Promise<void>;
  loadIntegrations: (projectId: string) => Promise<void>;
  doConnect: (projectId: string, provider: string, config: Record<string, string>) => Promise<void>;
  doDisconnect: (projectId: string, integrationId: string) => Promise<void>;
  loadSubmissions: (projectId: string) => Promise<void>;
  markRead: (projectId: string, submissionId: string, read: boolean) => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  sites: [],
  selectedSiteId: null,
  stats: null,
  integrations: [],
  catalog: [],
  automations: [],
  submissions: [],
  activeTab: "stats",
  loading: false,
  error: null,

  loadSites: async () => {
    set({ loading: true, error: null });
    try {
      const res = await listProjects();
      set({ sites: res.data, loading: false });
    } catch {
      set({ error: "Nie udało się załadować projektów", loading: false });
    }
  },

  selectSite: (siteId) => set({ selectedSiteId: siteId }),

  setActiveTab: (tab) => set({ activeTab: tab }),

  loadStats: async (projectId, period = "30d") => {
    try {
      const res = await getProjectStats(projectId, period);
      set({ stats: res.data });
    } catch {
      set({ stats: null });
    }
  },

  loadCatalog: async () => {
    try {
      const res = await getIntegrationsCatalog();
      set({ catalog: res.data });
    } catch {
      set({ catalog: [] });
    }
  },

  loadAutomations: async () => {
    try {
      const res = await getAutomationTemplates();
      set({ automations: res.data });
    } catch {
      set({ automations: [] });
    }
  },

  loadIntegrations: async (projectId) => {
    try {
      const res = await listSiteIntegrations(projectId);
      set({ integrations: res.data });
    } catch {
      set({ integrations: [] });
    }
  },

  doConnect: async (projectId, provider, config) => {
    const res = await apiConnect(projectId, provider, config);
    set({ integrations: [...get().integrations, res.data] });
  },

  doDisconnect: async (projectId, integrationId) => {
    await apiDisconnect(projectId, integrationId);
    set({ integrations: get().integrations.filter((i) => i.id !== integrationId) });
  },

  loadSubmissions: async (projectId) => {
    try {
      const res = await listFormSubmissions(projectId);
      set({ submissions: res.data });
    } catch {
      set({ submissions: [] });
    }
  },

  markRead: async (projectId, submissionId, read) => {
    await apiMarkRead(projectId, submissionId, read);
    set({
      submissions: get().submissions.map((s) =>
        s.id === submissionId ? { ...s, read } : s,
      ),
    });
  },
}));
