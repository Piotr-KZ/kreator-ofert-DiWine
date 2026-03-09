import { apiClient } from './client';
import { Organization } from '../types/models';

export const organizationsApi = {
  create: (data: { name: string }) =>
    apiClient.post<Organization>('/organizations/', data),

  getCurrent: () =>
    apiClient.get<Organization>('/organizations/me'),

  getMe: () =>
    apiClient.get<Organization>('/organizations/me'),

  get: (id: string) =>
    apiClient.get<Organization>(`/organizations/${id}`),

  update: (id: string, data: Partial<Organization>) =>
    apiClient.patch<Organization>(`/organizations/${id}`, data),

  transferOwnership: (id: string, newOwnerId: string) =>
    apiClient.post(`/organizations/${id}/transfer-ownership`, { new_owner_id: newOwnerId }),

  delete: (id: string) =>
    apiClient.delete(`/organizations/${id}`),

  uploadLogo: (orgId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<Organization>(`/organizations/${orgId}/logo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
