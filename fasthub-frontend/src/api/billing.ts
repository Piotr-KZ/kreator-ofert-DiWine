import { apiClient } from './client';
import { Subscription, Invoice } from '../types/models';

export const billingApi = {
  // Adjusted endpoint names based on backend
  getSubscription: () =>
    apiClient.get<Subscription>('/subscriptions/current'),

  upgrade: (plan: string) =>
    apiClient.post<{ checkout_url: string }>('/subscriptions/change-plan', { plan }),

  cancel: () =>
    apiClient.post('/subscriptions/cancel'),

  listInvoices: () =>
    apiClient.get<Invoice[]>('/invoices/'),

  getInvoice: (id: string) =>
    apiClient.get<Invoice>(`/invoices/${id}`),

  getInvoicePdf: (id: string) =>
    apiClient.get(`/invoices/${id}/pdf`, { responseType: 'blob' }),

  getBillingPortal: () =>
    apiClient.get<{ url: string }>('/subscriptions/billing-portal'),

  checkInvoice: () =>
    apiClient.get('/subscriptions/invoice/check'),
};
