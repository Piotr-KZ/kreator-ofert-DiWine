import { useEffect, useState } from 'react';
import { membersApi } from '../api/members';
import { MemberWithUser, MemberRole } from '../types/models';
import { useAuthStore } from '../store/authStore';
import { useOrgStore } from '../store/orgStore';
import { Btn, Fld, Rad, StatusBadge } from '@/components/ui';
import Modal from '@/components/shared/Modal';

export default function TeamPage() {
  const { user } = useAuthStore();
  const { organization } = useOrgStore();
  const [members, setMembers] = useState<MemberWithUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<MemberRole>('viewer');
  const [inviteLoading, setInviteLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMembers = async () => {
    setLoading(true);
    try {
      const { data } = await membersApi.list();
      setMembers(data.items || data || []);
    } catch (err: any) {
      if (err.response?.status !== 403 && err.response?.status !== 404) {
        setError(err.response?.data?.detail || 'Failed to fetch members');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchMembers(); }, []);

  const canManage = user?.is_superuser || (organization && members.some(m => m.user_id === user?.id && m.role === 'admin'));

  const handleInvite = async () => {
    if (!inviteEmail) return;
    setInviteLoading(true);
    try {
      await membersApi.invite({ email: inviteEmail, role: inviteRole });
      setInviteOpen(false);
      setInviteEmail('');
      setInviteRole('viewer');
      fetchMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to invite member');
    } finally {
      setInviteLoading(false);
    }
  };

  const handleChangeRole = async (memberId: string, role: MemberRole) => {
    try {
      await membersApi.changeRole(memberId, role);
      fetchMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to change role');
    }
  };

  const handleRemove = async (memberId: string) => {
    if (!confirm('Are you sure you want to remove this member?')) return;
    try {
      await membersApi.remove(memberId);
      fetchMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove member');
    }
  };

  const adminCount = members.filter(m => m.role === 'admin').length;
  const activeCount = members.filter(m => m.user?.is_active).length;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Team</h1>
          <p className="text-sm text-gray-500 mt-1">
            {members.length} members &middot; {activeCount} active &middot; {adminCount} admins
          </p>
        </div>
        {canManage && (
          <Btn onClick={() => setInviteOpen(true)}>Invite Member</Btn>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4 flex items-center justify-between">
          <p className="text-sm text-red-700">{error}</p>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" /></div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left px-4 py-3 text-xs uppercase text-gray-500 font-medium">Name</th>
                <th className="text-left px-4 py-3 text-xs uppercase text-gray-500 font-medium">Role</th>
                <th className="text-left px-4 py-3 text-xs uppercase text-gray-500 font-medium">Status</th>
                <th className="text-left px-4 py-3 text-xs uppercase text-gray-500 font-medium">Joined</th>
                {canManage && <th className="text-right px-4 py-3 text-xs uppercase text-gray-500 font-medium">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {members.map((member) => (
                <tr key={member.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{member.user?.full_name || 'N/A'}</p>
                      <p className="text-xs text-gray-500">{member.user?.email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge variant={member.role === 'admin' ? 'info' : 'success'}>
                      {member.role}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge variant={member.user?.is_active ? 'success' : 'error'}>
                      {member.user?.is_active ? 'Active' : 'Inactive'}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(member.joined_at || member.created_at).toLocaleDateString()}
                  </td>
                  {canManage && (
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleChangeRole(member.id, member.role === 'admin' ? 'viewer' : 'admin')}
                          className="text-xs text-indigo-600 hover:text-indigo-700"
                        >
                          {member.role === 'admin' ? 'Make Viewer' : 'Make Admin'}
                        </button>
                        <button
                          onClick={() => handleRemove(member.id)}
                          className="text-xs text-red-600 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
              {members.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-sm text-gray-500">No team members found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Invite Modal */}
      <Modal open={inviteOpen} onClose={() => setInviteOpen(false)} title="Invite Member" footer={
        <>
          <Btn variant="ghost" onClick={() => setInviteOpen(false)}>Cancel</Btn>
          <Btn onClick={handleInvite} loading={inviteLoading}>Send Invite</Btn>
        </>
      }>
        <div className="space-y-4">
          <Fld label="Email" type="email" placeholder="colleague@example.com" value={inviteEmail} onChange={setInviteEmail} />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <div className="space-y-2">
              <Rad on={inviteRole === 'viewer'} onClick={() => setInviteRole('viewer')}>
                <div><p className="text-sm font-medium">Viewer</p><p className="text-xs text-gray-500">Read-only access</p></div>
              </Rad>
              <Rad on={inviteRole === 'admin'} onClick={() => setInviteRole('admin')}>
                <div><p className="text-sm font-medium">Admin</p><p className="text-xs text-gray-500">Full management access</p></div>
              </Rad>
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
}
