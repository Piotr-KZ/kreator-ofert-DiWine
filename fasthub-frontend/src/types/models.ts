export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'superadmin' | 'admin' | 'user' | 'viewer';
  is_active: boolean;
  is_verified: boolean;
  organization_id: string;
  position?: string;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  type: 'business' | 'individual';
  nip?: string;
  regon?: string;
  krs?: string;
  first_name?: string;
  last_name?: string;
  billing_street: string;
  billing_city: string;
  billing_postal_code: string;
  billing_country: string;
  email: string;
  phone?: string;
  logo_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  id: string;
  organization_id: string;
  plan: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'past_due' | 'canceled' | 'incomplete';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  stripe_subscription_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: string;
  organization_id: string;
  invoice_number: string;
  amount: number;
  currency: string;
  status: 'draft' | 'open' | 'paid' | 'void';
  issue_date: string;
  due_date?: string;
  paid_at?: string;
  invoice_pdf_url?: string;
  created_at: string;
}

export interface TeamMember {
  id: string;
  email: string;
  full_name: string;
  role: string;
  position?: string;
  is_active: boolean;
  is_verified: boolean;
  last_login_at?: string;
  created_at: string;
}

export interface Invitation {
  id: string;
  email: string;
  role: string;
  invited_by: string;
  expires_at: string;
  is_accepted: boolean;
  created_at: string;
}

export interface ApiToken {
  id: string;
  name: string;
  token: string;
  last_used_at?: string;
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_organizations: number;
  total_subscriptions: number;
  active_subscriptions: number;
  revenue_this_month: number;
  revenue_last_month: number;
}
