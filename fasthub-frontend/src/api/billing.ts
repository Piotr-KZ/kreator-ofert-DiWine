import { apiClient } from './client';
import { Invoice, BillingPlan } from '../types/models';

export const billingApi = {
  // Subscription
  getSubscription: () =>
    apiClient.get('/billing/subscription'),

  // Usage
  getUsage: () =>
    apiClient.get('/billing/usage'),

  // Stripe Checkout (create payment session)
  createCheckout: (priceId: string, successUrl: string, cancelUrl: string) =>
    apiClient.post('/billing/checkout', {
      price_id: priceId,
      success_url: successUrl,
      cancel_url: cancelUrl,
    }),

  // Stripe Customer Portal
  createPortal: (returnUrl: string) =>
    apiClient.post('/billing/portal', { return_url: returnUrl }),

  // Catalog — plans (public)
  getPlans: () =>
    apiClient.get<BillingPlan[]>('/catalog/plans'),

  // Catalog — addons (public)
  getAddons: (plan?: string) =>
    apiClient.get('/catalog/addons', { params: plan ? { plan } : {} }),

  // Invoices (existing endpoints)
  listInvoices: () =>
    apiClient.get<Invoice[]>('/invoices/'),

  getInvoice: (id: string) =>
    apiClient.get<Invoice>(`/invoices/${id}`),

  getInvoicePdf: (id: string) =>
    apiClient.get(`/invoices/${id}/pdf`, { responseType: 'blob' }),

  // Subscription status (existing endpoint)
  getSubscriptionStatus: () =>
    apiClient.get('/subscription/status'),
};
