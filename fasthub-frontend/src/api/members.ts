import { apiClient } from './client';
import { Member } from '../types/models';
import { InviteMemberRequest, ChangeMemberRoleRequest, MemberListResponse } from '../types/api';

export type { InviteMemberRequest, ChangeMemberRoleRequest, MemberListResponse };

export const membersApi = {
  /**
   * Invite a user to an organization by email
   * POST /organizations/{organization_id}/members
   */
  invite: (organizationId: string, data: InviteMemberRequest) =>
    apiClient.post<Member>(`/organizations/${organizationId}/members`, data),

  /**
   * List all members of an organization
   * GET /organizations/{organization_id}/members
   */
  list: (organizationId: string, params?: { page?: number; per_page?: number; search?: string; role?: string }) =>
    apiClient.get<MemberListResponse>(`/organizations/${organizationId}/members`, { params }),

  /**
   * Remove a member from an organization
   * DELETE /members/{member_id} (uses member UUID, NOT user_id)
   */
  remove: (memberId: string) =>
    apiClient.delete(`/members/${memberId}`),

  /**
   * Change a member's role in an organization
   * PATCH /members/{member_id} (uses member UUID, NOT user_id)
   */
  changeRole: (memberId: string, data: ChangeMemberRoleRequest) =>
    apiClient.patch<Member>(`/members/${memberId}`, data),
};
