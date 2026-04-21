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

// ─── AI ───

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
