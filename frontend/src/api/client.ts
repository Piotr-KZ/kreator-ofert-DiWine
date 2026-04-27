/**
 * API client for Lab Creator backend.
 */

import axios from "axios";

const API_BASE = "/api/v1";

const api = axios.create({ baseURL: API_BASE });

// ─── Projects ───

export const createProject = (name: string, site_type: string) =>
  api.post("/projects", { name, site_type });

export const listProjects = () =>
  api.get("/projects");

export const getProject = (id: string) =>
  api.get(`/projects/${id}`);

export const updateProject = (id: string, data: Record<string, unknown>) =>
  api.patch(`/projects/${id}`, data);

export const deleteProject = (id: string) =>
  api.delete(`/projects/${id}`);

// ─── Sections ───

export const addSection = (projectId: string, block_code: string, position?: number) =>
  api.post(`/projects/${projectId}/sections`, { block_code, position });

export const updateSection = (projectId: string, sectionId: string, data: Record<string, unknown>) =>
  api.patch(`/projects/${projectId}/sections/${sectionId}`, data);

export const deleteSection = (projectId: string, sectionId: string) =>
  api.delete(`/projects/${projectId}/sections/${sectionId}`);

export const reorderSections = (projectId: string, section_ids: string[]) =>
  api.post(`/projects/${projectId}/sections/reorder`, { section_ids });

export const duplicateSection = (projectId: string, sectionId: string) =>
  api.post(`/projects/${projectId}/sections/${sectionId}/duplicate`);

// ─── AI ───

export const validateBrief = (projectId: string) =>
  api.post(`/projects/${projectId}/validate-brief`);

export const analyzeWebsite = (projectId: string, url: string) =>
  api.post(`/projects/${projectId}/analyze-website`, { url });

export const generateStructure = (projectId: string) =>
  api.post(`/projects/${projectId}/generate-structure`);

export const generateVisualConcept = (projectId: string) =>
  api.post(`/projects/${projectId}/generate-visual-concept`);

export const getVisualConcept = (projectId: string) =>
  api.get(`/projects/${projectId}/visual-concept`);

export const saveVisualConcept = (projectId: string, data: Record<string, unknown>) =>
  api.put(`/projects/${projectId}/visual-concept`, data);

export const generateContent = (projectId: string) =>
  api.post(`/projects/${projectId}/generate-content`);

export const regenerateSection = (projectId: string, sectionId: string, instruction?: string) =>
  api.post(`/projects/${projectId}/sections/${sectionId}/regenerate`, { instruction });

// ─── Blocks ───

export const listCategories = () =>
  api.get("/blocks/categories");

export const listBlocks = (category?: string) =>
  api.get("/blocks", { params: category ? { category } : {} });

export const listSiteTypes = () =>
  api.get("/site-types");

// ─── Chat ───

export const chatStream = async (
  projectId: string,
  message: string,
  step?: number,
  onChunk?: (text: string) => void,
  context?: Record<string, unknown>,
): Promise<void> => {
  const resp = await fetch(`${API_BASE}/projects/${projectId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, step, context }),
  });
  if (!resp.ok) throw new Error(`Chat error: ${resp.status}`);
  const reader = resp.body?.getReader();
  if (!reader) return;
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const payload = line.slice(6).trim();
      if (payload === "[DONE]") return;
      try {
        const parsed = JSON.parse(payload);
        if (parsed.text && onChunk) onChunk(parsed.text);
      } catch { /* skip */ }
    }
  }
};

// ─── Media / Unsplash ───

export const searchUnsplash = (query: string, orientation = 'landscape', width = 1200) =>
  api.get<{
    url: string | null;
    photo_id?: string;
    photographer_name?: string;
    photographer_url?: string;
    photo_page_url?: string;
  }>('/media/unsplash/search', { params: { query, orientation, width } });

export interface UnsplashPhotoMeta {
  url: string;
  photo_id: string;
  photographer_name: string;
  photographer_url: string;
  photo_page_url: string;
}

export const searchUnsplashGallery = (query: string, orientation = 'landscape', width = 800, count = 8) =>
  api.get<{ photos: UnsplashPhotoMeta[] }>('/media/unsplash/gallery', { params: { query, orientation, width, count } });

export const triggerUnsplashDownload = (photoId: string) =>
  api.get<{
    photographer_name: string | null;
    photographer_url: string | null;
    photo_page_url: string | null;
  }>(`/media/unsplash/trigger-download/${encodeURIComponent(photoId)}`);

// ─── Export ───

export const getPreviewUrl = (projectId: string) =>
  `${API_BASE}/projects/${projectId}/preview`;

export const exportHtml = async (projectId: string) => {
  const resp = await api.get(`/projects/${projectId}/export-html`, { responseType: "blob" });
  const url = window.URL.createObjectURL(resp.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = "strona.html";
  a.click();
  window.URL.revokeObjectURL(url);
};
