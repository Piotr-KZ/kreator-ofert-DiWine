import { apiClient } from './client';
import { User } from '../types/models';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  organization: {
    name: string;
    type: 'business' | 'individual';
    nip?: string;
    billing_street: string;
    billing_city: string;
    billing_postal_code: string;
    billing_country: string;
    phone?: string;
  };
}

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

  // Adjusted endpoint names based on backend
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
    apiClient.get(`/auth/magic-link/verify?token=${token}`),
};
