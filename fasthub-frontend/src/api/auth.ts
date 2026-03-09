import { apiClient } from './client';
import { User } from '../types/models';
import { LoginRequest, LoginResponse, RegisterRequest } from '../types/api';

export type { LoginRequest, LoginResponse, RegisterRequest };

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<LoginResponse>('/auth/login', data),

  register: (data: RegisterRequest) =>
    apiClient.post<LoginResponse>('/auth/register', data),

  logout: () =>
    apiClient.post('/auth/logout'),

  refresh: (refreshToken: string) =>
    apiClient.post<LoginResponse>('/auth/refresh', { refresh_token: refreshToken }),

  getCurrentUser: () =>
    apiClient.get<User>('/auth/me'),

  verifyEmail: (token: string) =>
    apiClient.post('/auth/verify-email', { token }),

  forgotPassword: (email: string) =>
    apiClient.post('/auth/password-reset/request', { email }),

  resetPassword: (token: string, newPassword: string) =>
    apiClient.post('/auth/password-reset/confirm', { token, new_password: newPassword }),

  changePassword: (currentPassword: string, newPassword: string) =>
    apiClient.post('/auth/change-password', { current_password: currentPassword, new_password: newPassword }),

  // Magic link
  sendMagicLink: (email: string) =>
    apiClient.post('/auth/magic-link/send', { email }),

  verifyMagicLink: (token: string) =>
    apiClient.post('/auth/magic-link/verify', { token }),
};
