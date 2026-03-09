import client from './client';

// === 2FA ===

export const twoFactorApi = {
  setup: (password: string) =>
    client.post('/auth/2fa/setup', { password }).then((r) => r.data),

  verify: (code: string) =>
    client.post('/auth/2fa/verify', { code }).then((r) => r.data),

  authenticate: (tempToken: string, code: string) =>
    client.post('/auth/2fa/authenticate', { temp_token: tempToken, code }).then((r) => r.data),

  disable: (password: string, code: string) =>
    client.post('/auth/2fa/disable', { password, code }).then((r) => r.data),

  regenerateBackupCodes: (password: string, code: string) =>
    client.post('/auth/2fa/backup-codes/regenerate', { password, code }).then((r) => r.data),
};

// === Sessions ===

export interface SessionInfo {
  id: string;
  device_type: string;
  device_name: string;
  browser: string;
  os: string;
  ip_address: string;
  is_current: boolean;
  last_active_at: string;
  created_at: string;
}

export const sessionsApi = {
  list: (): Promise<SessionInfo[]> =>
    client.get('/auth/sessions').then((r) => r.data),

  revoke: (sessionId: string) =>
    client.delete(`/auth/sessions/${sessionId}`).then((r) => r.data),

  revokeAll: () =>
    client.delete('/auth/sessions').then((r) => r.data),
};

// === GUS ===

export interface GUSData {
  name: string;
  nip: string;
  regon: string;
  krs: string;
  legal_form: string;
  street: string;
  city: string;
  postal_code: string;
  status: string;
}

export const gusApi = {
  lookup: (nip: string): Promise<GUSData> =>
    client.get('/gus/lookup', { params: { nip } }).then((r) => r.data),
};

// === Webhooks ===

export interface WebhookEndpoint {
  id: string;
  organization_id: string;
  url: string;
  secret?: string;
  events: string[];
  is_active: boolean;
  description?: string;
  last_triggered_at?: string;
  last_status_code?: number;
  consecutive_failures: number;
  created_at: string;
}

export interface WebhookDelivery {
  id: string;
  endpoint_id: string;
  event_type: string;
  status_code?: number;
  response_time_ms?: number;
  success: boolean;
  error?: string;
  attempt: number;
  created_at: string;
}

export const webhooksApi = {
  list: (orgId: string): Promise<WebhookEndpoint[]> =>
    client.get(`/organizations/${orgId}/webhooks`).then((r) => r.data),

  create: (orgId: string, data: { url: string; events: string[]; description?: string }): Promise<WebhookEndpoint> =>
    client.post(`/organizations/${orgId}/webhooks`, data).then((r) => r.data),

  update: (orgId: string, webhookId: string, data: Partial<{ url: string; events: string[]; is_active: boolean; description: string }>) =>
    client.patch(`/organizations/${orgId}/webhooks/${webhookId}`, data).then((r) => r.data),

  remove: (orgId: string, webhookId: string) =>
    client.delete(`/organizations/${orgId}/webhooks/${webhookId}`).then((r) => r.data),

  rotateSecret: (orgId: string, webhookId: string): Promise<{ secret: string }> =>
    client.post(`/organizations/${orgId}/webhooks/${webhookId}/rotate-secret`).then((r) => r.data),

  test: (orgId: string, webhookId: string): Promise<{ success: boolean; status_code?: number; response_time_ms?: number }> =>
    client.post(`/organizations/${orgId}/webhooks/${webhookId}/test`).then((r) => r.data),

  deliveries: (orgId: string, webhookId: string): Promise<WebhookDelivery[]> =>
    client.get(`/organizations/${orgId}/webhooks/${webhookId}/deliveries`).then((r) => r.data),
};

// === Payments ===

export interface PaymentRecord {
  id: string;
  organization_id: string;
  subscription_id?: string;
  amount: number;
  currency: string;
  gateway_id: string;
  gateway_payment_id?: string;
  payment_method?: string;
  payment_method_details?: string;
  status: string;
  description?: string;
  completed_at?: string;
  failed_at?: string;
  refunded_at?: string;
  invoice_id?: string;
  created_at: string;
}

export const paymentsApi = {
  list: (limit = 50, offset = 0): Promise<PaymentRecord[]> =>
    client.get('/billing/payments', { params: { limit, offset } }).then((r) => r.data),

  get: (paymentId: string): Promise<PaymentRecord> =>
    client.get(`/billing/payments/${paymentId}`).then((r) => r.data),
};

// === Notifications ===

export interface NotificationPreferences {
  form_submission_email: boolean;
  form_submission_app: boolean;
  newsletter_signup_email: boolean;
  newsletter_signup_app: boolean;
  payment_completed_email: boolean;
  payment_completed_app: boolean;
  payment_failed_email: boolean;
  payment_failed_app: boolean;
  security_alerts_email: boolean;
  security_alerts_app: boolean;
  team_changes_email: boolean;
  team_changes_app: boolean;
  system_updates_email: boolean;
  system_updates_app: boolean;
}

export const notificationsApi = {
  getPreferences: (): Promise<NotificationPreferences> =>
    client.get('/notifications/preferences').then((r) => r.data),

  updatePreferences: (data: Partial<NotificationPreferences>) =>
    client.put('/notifications/preferences', data).then((r) => r.data),
};

// === GDPR ===

export const gdprApi = {
  requestDeletion: () =>
    client.post('/gdpr/deletion-request').then((r) => r.data),
};

// === API Tokens ===

export interface ApiTokenInfo {
  id: string;
  name: string;
  token?: string;
  last_used_at?: string;
  expires_at?: string;
  created_at: string;
}

export const apiTokensApi = {
  list: (): Promise<ApiTokenInfo[]> =>
    client.get('/api-tokens').then((r) => r.data),

  create: (data: { name: string; expires_in_days?: number }): Promise<ApiTokenInfo> =>
    client.post('/api-tokens', data).then((r) => r.data),

  remove: (tokenId: string) =>
    client.delete(`/api-tokens/${tokenId}`).then((r) => r.data),
};
