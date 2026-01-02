import { apiClient } from './client';
import { Member, MemberWithUser, MemberRole } from '../types/models';

export interface InviteMemberRequest {
  user_id: string;
  role: MemberRole;
}

export interface ChangeMemberRoleRequest {
  role: MemberRole;
}

export interface MemberListResponse {
  members: MemberWithUser[];
  total: number;
}

export const membersApi = {
  /**
   * Invite a user to an organization
   * POST /organizations/{organization_id}/members/invite
   */
  invite: (organizationId: string, data: InviteMemberRequest) =>
    apiClient.post<Member>(`/members/organizations/${organizationId}/members/invite`, data),

  /**
   * List all members of an organization
   * GET /organizations/{organization_id}/members
   */
  list: (organizationId: string) =>
    apiClient.get<MemberListResponse>(`/members/organizations/${organizationId}/members`),

  /**
   * Remove a member from an organization
   * DELETE /organizations/{organization_id}/members/{user_id}
   */
  remove: (organizationId: string, userId: string) =>
    apiClient.delete(`/members/organizations/${organizationId}/members/${userId}`),

  /**
   * Change a member's role in an organization
   * PATCH /organizations/{organization_id}/members/{user_id}/role
   */
  changeRole: (organizationId: string, userId: string, data: ChangeMemberRoleRequest) =>
    apiClient.patch<Member>(`/members/organizations/${organizationId}/members/${userId}/role`, data),
};
