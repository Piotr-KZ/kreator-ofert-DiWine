import { apiClient } from './client';
import { AdminStats, User, Subscription, Organization } from '../types/models';
import { PaginatedResponse } from '../types/api';

export const superadminApi = {
  getMetrics: () =>
    apiClient.get<AdminStats>('/admin/stats'),

  getRecentUsers: () =>
    apiClient.get<User[]>('/admin/users/recent'),

  getRecentSubscriptions: () =>
    apiClient.get<Subscription[]>('/admin/subscriptions/recent'),

  broadcast: (message: { title: string; content: string }) =>
    apiClient.post('/admin/broadcast', message),

  getBlacklistStats: () =>
    apiClient.get('/admin/tokens/blacklist/stats'),

  clearBlacklist: () =>
    apiClient.post('/admin/tokens/blacklist/clear'),

  revokeToken: (token: string) =>
    apiClient.post('/admin/tokens/revoke-token', { token }),

  listOrganizations: () =>
    apiClient.get<PaginatedResponse<Organization>>('/admin/organizations'),
};
