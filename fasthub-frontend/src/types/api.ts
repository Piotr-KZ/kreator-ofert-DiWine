import { MemberRole, MemberWithUser } from './models';

// Paginated response wrapper
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

// Auth
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
}

// Members
export interface InviteMemberRequest {
  email: string;
  role: MemberRole;
}

export interface ChangeMemberRoleRequest {
  role: MemberRole;
}

export interface MemberListResponse {
  members: MemberWithUser[];
  total: number;
}

// Users
export interface UsersListResponse {
  items: import('./models').User[];
  total: number;
  page: number;
  per_page: number;
}
