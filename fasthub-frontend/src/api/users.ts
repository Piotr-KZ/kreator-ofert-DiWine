import { apiClient } from './client';
import { User } from '../types/models';
import { UsersListResponse } from '../types/api';

export type { UsersListResponse };

export const usersApi = {
  list: (params?: { page?: number; per_page?: number; search?: string }) =>
    apiClient.get<UsersListResponse>('/users/', { params }),

  get: (id: string) =>
    apiClient.get<User>(`/users/${id}`),

  update: (id: string, data: Partial<User>) =>
    apiClient.patch<User>(`/users/${id}`, data),

  delete: (id: string) =>
    apiClient.delete(`/users/${id}`),

  getMe: () =>
    apiClient.get<User>('/users/me'),

  updateMe: (data: {
    full_name?: string;
    email?: string;
    phone?: string;
    position?: string;
    language?: string;
    timezone?: string;
  }) =>
    apiClient.patch<User>('/users/me', data),

  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<User>('/users/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
