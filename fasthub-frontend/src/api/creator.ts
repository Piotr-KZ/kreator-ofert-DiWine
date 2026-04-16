/**
 * API client for WebCreator endpoints (Brief 30 + 31 + 34).
 */

import { apiClient } from "./client";
import type {
  AutomationGroup,
  BlockCategory,
  BlockTemplate,
  BriefData,
  CheckItem,
  ConfigData,
  FormSubmission,
  GenerateProgress,
  IntegrationCategory,
  Project,
  ProjectMaterial,
  ProjectSection,
  ProjectStats,
  PublishResult,
  ReadinessResult,
  SiteIntegration,
  StockPhoto,
  StyleData,
  ValidationItem,
} from "@/types/creator";

// ─── Projects ───

export const createProject = (name: string) =>
  apiClient.post<Project>("/projects", { name });

export const getProject = (projectId: string) =>
  apiClient.get<Project>(`/projects/${projectId}`);

export const updateProject = (projectId: string, data: Partial<Project>) =>
  apiClient.patch<Project>(`/projects/${projectId}`, data);

export const listProjects = () =>
  apiClient.get<Project[]>("/projects");

// ─── Brief (Step 1) ───

export const saveBrief = (projectId: string, data: Partial<BriefData>) =>
  apiClient.put(`/projects/${projectId}/brief`, data);

export const getBrief = (projectId: string) =>
  apiClient.get<Partial<BriefData>>(`/projects/${projectId}/brief`);

// ─── Style (Step 3) ───

export const saveStyle = (projectId: string, data: Partial<StyleData>) =>
  apiClient.put(`/projects/${projectId}/style`, data);

export const getStyle = (projectId: string) =>
  apiClient.get<Partial<StyleData>>(`/projects/${projectId}/style`);

// ─── Materials (Step 2) ───

export const uploadMaterial = (projectId: string, file: File, type: string) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("type", type);
  return apiClient.post<ProjectMaterial>(`/projects/${projectId}/materials`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const addLinkMaterial = (projectId: string, url: string, type: string, description?: string) =>
  apiClient.post<ProjectMaterial>(`/projects/${projectId}/materials/link`, { url, type, description });

export const listMaterials = (projectId: string) =>
  apiClient.get<ProjectMaterial[]>(`/projects/${projectId}/materials`);

export const deleteMaterial = (projectId: string, materialId: string) =>
  apiClient.delete(`/projects/${projectId}/materials/${materialId}`);

// ─── AI (Step 4) ───

export const runValidation = (projectId: string) =>
  apiClient.post<{ items: ValidationItem[] }>(`/projects/${projectId}/ai/validate`);

export const sendChatMessage = async (
  projectId: string,
  context: string,
  message: string,
  onChunk: (text: string) => void,
  onDone: () => void,
  onError?: (error: string) => void,
) => {
  const token =
    localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  const orgId = localStorage.getItem("current_organization_id");

  const response = await fetch(
    `${apiClient.defaults.baseURL}/projects/${projectId}/ai/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(orgId ? { "X-Organization-Id": orgId } : {}),
      },
      body: JSON.stringify({ context, message }),
    },
  );

  if (!response.ok || !response.body) {
    // Try to extract error detail from response
    try {
      const errorData = await response.json();
      const errorMsg = errorData.detail || "Błąd połączenia z AI";
      onError?.(errorMsg);
    } catch {
      onError?.("Błąd połączenia z AI. Spróbuj ponownie.");
    }
    onDone();
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6).trim();
        if (data === "[DONE]") {
          onDone();
          return;
        }
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) {
            onError?.(parsed.error);
          } else if (parsed.text) {
            onChunk(parsed.text);
          }
        } catch {
          // skip malformed
        }
      }
    }
  }
  onDone();
};

// ─── Sections (Step 5-6) ───

export const listSections = (projectId: string) =>
  apiClient.get<ProjectSection[]>(`/projects/${projectId}/sections`);

export const addSection = (projectId: string, blockCode: string, variant = "A") =>
  apiClient.post<ProjectSection>(`/projects/${projectId}/sections`, { block_code: blockCode, variant });

export const updateSection = (projectId: string, sectionId: string, data: Partial<ProjectSection>) =>
  apiClient.patch<ProjectSection>(`/projects/${projectId}/sections/${sectionId}`, data);

export const deleteSection = (projectId: string, sectionId: string) =>
  apiClient.delete(`/projects/${projectId}/sections/${sectionId}`);

export const reorderSections = (projectId: string, order: string[]) =>
  apiClient.post(`/projects/${projectId}/sections/reorder`, { order });

// ─── Blocks ───

export const listBlocks = (category?: string) =>
  apiClient.get<BlockTemplate[]>("/blocks", { params: category ? { category } : {} });

export const matchBlocks = (criteria: { category_code?: string; media_type?: string; layout_type?: string }) =>
  apiClient.post<BlockTemplate[]>("/blocks/match", criteria);

export const getBlock = (code: string) =>
  apiClient.get<BlockTemplate>(`/blocks/${code}`);

export const listCategories = () =>
  apiClient.get<BlockCategory[]>("/blocks/categories");

// ─── AI Generate Site (SSE) ───

export const generateSite = async (
  projectId: string,
  onProgress: (data: GenerateProgress) => void,
) => {
  const token =
    localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
  const orgId = localStorage.getItem("current_organization_id");

  const response = await fetch(
    `${apiClient.defaults.baseURL}/projects/${projectId}/ai/generate-site`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(orgId ? { "X-Organization-Id": orgId } : {}),
      },
    },
  );

  if (!response.ok || !response.body) {
    throw new Error("Generate site request failed");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const raw = line.slice(6).trim();
        try {
          const parsed = JSON.parse(raw) as GenerateProgress;
          onProgress(parsed);
        } catch {
          // skip malformed
        }
      }
    }
  }
};

// ─── AI per section ───

export const generateSectionContent = (projectId: string, sectionId: string, instruction?: string) =>
  apiClient.post<{ slots: Record<string, unknown> }>(
    `/projects/${projectId}/ai/generate-content/${sectionId}`,
    instruction ? { instruction } : {},
  );

export const renderPage = (projectId: string) =>
  apiClient.get<{ html: string; css: string }>(`/projects/${projectId}/render`);

export const visualReview = (projectId: string) =>
  apiClient.post(`/projects/${projectId}/ai/visual-review`);

// ─── Stock Photos ───

export const searchStockPhotos = (query: string, perPage = 12) =>
  apiClient.get<StockPhoto[]>("/stock-photos", { params: { query, per_page: perPage } });

export const downloadStockPhoto = (
  projectId: string,
  data: { url: string; slot_id: string; section_id: string; aspect_ratio?: string },
) =>
  apiClient.post<{ file_url: string }>(`/projects/${projectId}/stock-photos/download`, data);

// ─── Config (Step 7) ───

export const saveConfig = (projectId: string, data: Partial<ConfigData>) =>
  apiClient.put<{ config_json: ConfigData }>(`/projects/${projectId}/config`, data);

export const getConfig = (projectId: string) =>
  apiClient.get<{ config_json: ConfigData }>(`/projects/${projectId}/config`);

export const suggestSeo = (projectId: string) =>
  apiClient.post<{ meta_title: string; meta_description: string; og_title: string; og_description: string }>(
    `/projects/${projectId}/ai/suggest-seo`,
  );

// ─── Publishing (Steps 8-9) ───

export const checkReadiness = (projectId: string) =>
  apiClient.post<ReadinessResult>(`/projects/${projectId}/check-readiness`);

export const publishProject = (projectId: string) =>
  apiClient.post<PublishResult>(`/projects/${projectId}/publish`);

export const unpublishProject = (projectId: string) =>
  apiClient.post<{ status: string }>(`/projects/${projectId}/unpublish`);

export const republishProject = (projectId: string) =>
  apiClient.post<PublishResult>(`/projects/${projectId}/republish`);

export const exportZip = (projectId: string) =>
  apiClient.get<Blob>(`/projects/${projectId}/export-zip`, { responseType: "blob" });

// ─── Form Submissions ───

export const listFormSubmissions = (projectId: string) =>
  apiClient.get<FormSubmission[]>(`/projects/${projectId}/form-submissions`);

export const markSubmissionRead = (projectId: string, submissionId: string, read: boolean) =>
  apiClient.patch(`/projects/${projectId}/form-submissions/${submissionId}`, { read });

// ─── Dashboard (Brief 36) ───

export const getProjectStats = (projectId: string, period = "30d") =>
  apiClient.get<ProjectStats>(`/projects/${projectId}/stats`, { params: { period } });

export const getIntegrationsCatalog = () =>
  apiClient.get<IntegrationCategory[]>("/integrations/catalog");

export const getAutomationTemplates = () =>
  apiClient.get<AutomationGroup[]>("/integrations/automations");

export const listSiteIntegrations = (projectId: string) =>
  apiClient.get<SiteIntegration[]>(`/projects/${projectId}/integrations`);

export const connectIntegration = (projectId: string, provider: string, config_json: Record<string, string>) =>
  apiClient.post<SiteIntegration>(`/projects/${projectId}/integrations`, { provider, config_json });

export const disconnectIntegration = (projectId: string, integrationId: string) =>
  apiClient.delete(`/projects/${projectId}/integrations/${integrationId}`);

export const testIntegration = (projectId: string, integrationId: string) =>
  apiClient.post(`/projects/${projectId}/integrations/${integrationId}/test`);
