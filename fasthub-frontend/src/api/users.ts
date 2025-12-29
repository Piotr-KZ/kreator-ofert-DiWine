import { apiClient } from './client';
import { User } from '../types/models';

export interface UsersListResponse {
  items: User[];
  total: number;
  page: number;
  per_page: number;
}

export const usersApi = {
  list: (params?: { page?: number; per_page?: number; search?: string }) =>
    apiClient.get<UsersListResponse>('/users/', { params }),

  get: (id: string) =>
    apiClient.get<User>(`/users/${id}`),

  update: (id: string, data: Partial<User>) =>
    apiClient.patch<User>(`/users/${id}`, data),

  delete: (id: string) =>
    apiClient.delete(`/users/${id}`),

  // Use PATCH /users/{id} for role change (backend doesn't have separate endpoint)
  changeRole: (id: string, role: string) =>
    apiClient.patch<User>(`/users/${id}`, { role }),

  // Get current user profile
  getMe: () =>
    apiClient.get<User>('/users/me'),
};
