import { apiClient } from './client';
import { AdminStats, User, Subscription, Organization } from '../types/models';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

export const superadminApi = {
  // Adjusted endpoint name based on backend
  getMetrics: () =>
    apiClient.get<AdminStats>('/admin/stats'),

  // Recent users
  getRecentUsers: () =>
    apiClient.get<User[]>('/admin/users/recent'),

  // Recent subscriptions
  getRecentSubscriptions: () =>
    apiClient.get<Subscription[]>('/admin/subscriptions/recent'),

  // Broadcast message to all users
  broadcast: (message: { title: string; content: string }) =>
    apiClient.post('/admin/broadcast', message),

  // Token blacklist management
  getBlacklistStats: () =>
    apiClient.get('/admin/tokens/blacklist/stats'),

  clearBlacklist: () =>
    apiClient.post('/admin/tokens/blacklist/clear'),

  revokeToken: (token: string) =>
    apiClient.post('/admin/tokens/revoke-token', { token }),

  // List all organizations (Super Admin only)
  listOrganizations: () =>
    apiClient.get<PaginatedResponse<Organization>>('/admin/organizations'),
};
