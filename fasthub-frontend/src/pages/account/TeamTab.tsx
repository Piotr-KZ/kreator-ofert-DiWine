import { useEffect, useState } from 'react';
import { useOrgStore } from '@/store/orgStore';
import { membersApi } from '@/api/members';
import { Btn, Fld, SectionCard, StatusBadge, Chk } from '@/components/ui';
import Modal from '@/components/shared/Modal';
import type { MemberWithUser } from '@/types/models';

const DEFAULT_ROLES = ['owner', 'admin', 'editor', 'viewer'];
const PERMISSIONS = [
  'Tworzenie stron',
  'Edycja stron',
  'Publikacja stron',
  'Zapraszanie członków',
  'Zmiana ról',
  'Dostęp do faktur',
  'Zmiana ustawień',
];

const PERMISSION_MATRIX: Record<string, boolean[]> = {
  owner:  [true, true, true, true, true, true, true],
  admin:  [true, true, true, true, true, true, true],
  editor: [true, true, true, false, false, false, false],
  viewer: [false, false, false, false, false, false, false],
};

export default function TeamTab() {
  const { organization } = useOrgStore();
  const [members, setMembers] = useState<MemberWithUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteModal, setInviteModal] = useState(false);
  const [invEmail, setInvEmail] = useState('');
  const [invRole, setInvRole] = useState('editor');
  const [invLoading, setInvLoading] = useState(false);
  const [invMsg, setInvMsg] = useState('');
  const [deleteId, setDeleteId] = useState<string | null>(null);

  useEffect(() => {
    if (organization) loadMembers();
  }, [organization]);

  const loadMembers = async () => {
    if (!organization) return;
    setLoading(true);
    try {
      const data = await membersApi.list(organization.id);
      setMembers(data.members || []);
    } catch {
      // API may not be available
    } finally {
      setLoading(false);
    }
  };

  const invite = async () => {
    if (!organization || !invEmail) return;
    setInvLoading(true);
    setInvMsg('');
    try {
      await membersApi.invite(organization.id, { email: invEmail, role: invRole as any });
      setInvMsg('Zaproszenie wysłane');
      setInvEmail('');
      await loadMembers();
      setTimeout(() => setInviteModal(false), 1500);
    } catch (err: any) {
      setInvMsg(err.response?.data?.detail || 'Błąd wysyłania zaproszenia');
    } finally {
      setInvLoading(false);
    }
  };

  const changeRole = async (memberId: string, newRole: string) => {
    try {
      await membersApi.changeRole(memberId, { role: newRole as any });
      setMembers((prev) =>
        prev.map((m) => (m.id === memberId ? { ...m, role: newRole as any } : m))
      );
    } catch { /* */ }
  };

  const removeMember = async () => {
    if (!deleteId) return;
    try {
      await membersApi.remove(deleteId);
      setMembers((prev) => prev.filter((m) => m.id !== deleteId));
    } catch { /* */ }
    setDeleteId(null);
  };

  const initials = (name?: string) =>
    (name || 'U').split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Zespół</h2>

      <SectionCard title="Członkowie zespołu" desc="Zarządzaj kto ma dostęp do Twojego konta i z jakimi uprawnieniami.">
        <div className="mb-4">
          <Btn onClick={() => { setInviteModal(true); setInvMsg(''); }}>Zaproś członka</Btn>
        </div>

        {loading ? (
          <div className="flex justify-center py-4">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : members.length === 0 ? (
          <p className="text-sm text-gray-500">Brak członków zespołu</p>
        ) : (
          <div className="space-y-2">
            {members.map((m) => {
              const isOwner = m.role === 'owner';
              return (
                <div key={m.id} className="flex items-center justify-between py-3 border-b last:border-0">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 text-xs font-bold">
                      {initials(m.user?.full_name)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{m.user?.full_name || m.user?.email}</p>
                      <p className="text-xs text-gray-500">{m.user?.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {isOwner ? (
                      <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded">Właściciel</span>
                    ) : (
                      <select
                        value={m.role}
                        onChange={(e) => changeRole(m.id, e.target.value)}
                        className="text-sm border border-gray-200 rounded-lg px-2 py-1"
                      >
                        {DEFAULT_ROLES.filter((r) => r !== 'owner').map((r) => (
                          <option key={r} value={r}>{r}</option>
                        ))}
                      </select>
                    )}
                    {!isOwner && (
                      <Btn variant="ghost" onClick={() => setDeleteId(m.id)}>
                        <span className="text-red-600 text-sm">Usuń</span>
                      </Btn>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </SectionCard>

      {/* Invite Modal */}
      <Modal open={inviteModal} onClose={() => setInviteModal(false)} title="Zaproś członka zespołu">
        <div className="space-y-4">
          <Fld label="Email" type="email" value={invEmail} onChange={setInvEmail} placeholder="jan@firma.pl" />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Rola</label>
            <select
              value={invRole}
              onChange={(e) => setInvRole(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400"
            >
              {DEFAULT_ROLES.filter((r) => r !== 'owner').map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
          {invMsg && (
            <p className={`text-sm ${invMsg.includes('Błąd') ? 'text-red-600' : 'text-green-600'}`}>{invMsg}</p>
          )}
          <Btn onClick={invite} loading={invLoading}>Wyślij zaproszenie</Btn>
        </div>
      </Modal>

      {/* Delete Confirm Modal */}
      <Modal open={!!deleteId} onClose={() => setDeleteId(null)} title="Usuń członka">
        <div className="space-y-4">
          <p className="text-sm text-gray-600">Czy na pewno chcesz usunąć tego członka z zespołu?</p>
          <div className="flex gap-3">
            <Btn variant="danger" onClick={removeMember}>Usuń</Btn>
            <Btn variant="ghost" onClick={() => setDeleteId(null)}>Anuluj</Btn>
          </div>
        </div>
      </Modal>

      {/* Permission Matrix */}
      <SectionCard title="Matryca uprawnień">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2 font-medium">Uprawnienie</th>
                {DEFAULT_ROLES.map((r) => (
                  <th key={r} className="pb-2 font-medium text-center capitalize">{r === 'owner' ? 'Właściciel' : r}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {PERMISSIONS.map((perm, pi) => (
                <tr key={perm}>
                  <td className="py-2 text-gray-700">{perm}</td>
                  {DEFAULT_ROLES.map((role) => (
                    <td key={role} className="py-2 text-center">
                      <span className={`inline-block w-5 h-5 rounded ${PERMISSION_MATRIX[role]?.[pi] ? 'bg-green-500 text-white' : 'bg-gray-100'} text-xs flex items-center justify-center mx-auto`}>
                        {PERMISSION_MATRIX[role]?.[pi] ? '✓' : ''}
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}
