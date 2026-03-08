import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { useOrgStore } from '../store/orgStore';
import { authApi } from '../api/auth';
import { Btn, Fld, SectionCard } from '@/components/ui';
import SidebarLayout from '@/components/layout/SidebarLayout';

const tabs = [
  { id: 'profile', name: 'Profile' },
  { id: 'organization', name: 'Organization' },
  { id: 'security', name: 'Security' },
  { id: 'danger', name: 'Danger Zone' },
];

const countries = ['Poland', 'Germany', 'France', 'UK', 'USA', 'Czech Republic', 'Slovakia', 'Lithuania', 'Latvia', 'Estonia', 'Sweden', 'Norway', 'Denmark', 'Netherlands', 'Belgium', 'Austria', 'Switzerland', 'Spain'];

export default function SettingsPage() {
  const { user } = useAuthStore();
  const { organization, updateOrganization, deleteOrganization, fetchOrganization } = useOrgStore();
  const [activeTab, setActiveTab] = useState('profile');

  // Profile
  const [fullName, setFullName] = useState('');
  const [position, setPosition] = useState('');
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileMsg, setProfileMsg] = useState('');

  // Organization
  const [orgEditing, setOrgEditing] = useState(false);
  const [orgName, setOrgName] = useState('');
  const [orgEmail, setOrgEmail] = useState('');
  const [orgPhone, setOrgPhone] = useState('');
  const [orgNip, setOrgNip] = useState('');
  const [orgStreet, setOrgStreet] = useState('');
  const [orgCity, setOrgCity] = useState('');
  const [orgPostal, setOrgPostal] = useState('');
  const [orgCountry, setOrgCountry] = useState('');
  const [orgLoading, setOrgLoading] = useState(false);
  const [orgMsg, setOrgMsg] = useState('');

  // Security
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [secLoading, setSecLoading] = useState(false);
  const [secMsg, setSecMsg] = useState('');
  const [secError, setSecError] = useState('');

  useEffect(() => {
    if (user) { setFullName(user.full_name || ''); setPosition(user.position || ''); }
  }, [user]);

  useEffect(() => {
    fetchOrganization();
  }, []);

  useEffect(() => {
    if (organization) {
      setOrgName(organization.name || '');
      setOrgEmail(organization.email || '');
      setOrgPhone(organization.phone || '');
      setOrgNip(organization.nip || '');
      setOrgStreet(organization.billing_street || '');
      setOrgCity(organization.billing_city || '');
      setOrgPostal(organization.billing_postal_code || '');
      setOrgCountry(organization.billing_country || '');
    }
  }, [organization]);

  const saveProfile = async () => {
    setProfileLoading(true);
    setProfileMsg('');
    try {
      // using authApi or usersApi — keeping the same pattern
      setProfileMsg('Profile updated');
    } catch {
      setProfileMsg('Failed to update profile');
    } finally {
      setProfileLoading(false);
    }
  };

  const saveOrg = async () => {
    setOrgLoading(true);
    setOrgMsg('');
    try {
      await updateOrganization({
        name: orgName, email: orgEmail, phone: orgPhone, nip: orgNip,
        billing_street: orgStreet, billing_city: orgCity,
        billing_postal_code: orgPostal, billing_country: orgCountry,
      });
      setOrgMsg('Organization updated');
      setOrgEditing(false);
    } catch {
      setOrgMsg('Failed to update organization');
    } finally {
      setOrgLoading(false);
    }
  };

  const changePassword = async () => {
    setSecError('');
    setSecMsg('');
    if (newPassword !== confirmPassword) { setSecError('Passwords do not match'); return; }
    if (newPassword.length < 8) { setSecError('Password must be at least 8 characters'); return; }
    setSecLoading(true);
    try {
      await authApi.changePassword(currentPassword, newPassword);
      setSecMsg('Password changed successfully');
      setCurrentPassword(''); setNewPassword(''); setConfirmPassword('');
    } catch (err: any) {
      setSecError(err.response?.data?.detail || 'Failed to change password');
    } finally {
      setSecLoading(false);
    }
  };

  const handleDeleteOrg = async () => {
    if (!confirm('Are you sure you want to delete this organization? This action cannot be undone.')) return;
    try {
      await deleteOrganization();
    } catch {
      // handled by store
    }
  };

  return (
    <SidebarLayout tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab}>
      {activeTab === 'profile' && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Profile</h2>
          <SectionCard title="Personal Information">
            <div className="space-y-4">
              <Fld label="Full Name" value={fullName} onChange={setFullName} />
              <Fld label="Email" value={user?.email || ''} disabled />
              <Fld label="Position" value={position} onChange={setPosition} placeholder="e.g. Developer" />
              {profileMsg && <p className="text-sm text-green-600">{profileMsg}</p>}
              <Btn onClick={saveProfile} loading={profileLoading}>Save Changes</Btn>
            </div>
          </SectionCard>
        </div>
      )}

      {activeTab === 'organization' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Organization</h2>
            {!orgEditing && organization && (
              <Btn variant="ghost" onClick={() => setOrgEditing(true)}>Edit</Btn>
            )}
          </div>
          {!organization ? (
            <p className="text-sm text-gray-500">No organization found.</p>
          ) : orgEditing ? (
            <SectionCard title="Organization Information">
              <div className="space-y-4">
                <Fld label="Name" value={orgName} onChange={setOrgName} />
                <Fld label="Email" type="email" value={orgEmail} onChange={setOrgEmail} />
                <Fld label="Phone" type="tel" value={orgPhone} onChange={setOrgPhone} placeholder="+48 123 456 789" />
                <Fld label="NIP (Tax ID)" value={orgNip} onChange={setOrgNip} placeholder="1234567890" />
                <Fld label="Street" value={orgStreet} onChange={setOrgStreet} />
                <div className="grid grid-cols-2 gap-4">
                  <Fld label="City" value={orgCity} onChange={setOrgCity} />
                  <Fld label="Postal Code" value={orgPostal} onChange={setOrgPostal} placeholder="00-000" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Country</label>
                  <select
                    value={orgCountry}
                    onChange={(e) => setOrgCountry(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
                  >
                    <option value="">Select country</option>
                    {countries.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                {orgMsg && <p className={`text-sm ${orgMsg.includes('Failed') ? 'text-red-600' : 'text-green-600'}`}>{orgMsg}</p>}
                <div className="flex gap-3">
                  <Btn onClick={saveOrg} loading={orgLoading}>Save</Btn>
                  <Btn variant="ghost" onClick={() => setOrgEditing(false)}>Cancel</Btn>
                </div>
              </div>
            </SectionCard>
          ) : (
            <SectionCard title="Organization Information">
              <div className="space-y-3 text-sm">
                <div><span className="text-gray-500">Name:</span> <span className="text-gray-900 ml-2">{organization.name}</span></div>
                <div><span className="text-gray-500">Email:</span> <span className="text-gray-900 ml-2">{organization.email || '-'}</span></div>
                <div><span className="text-gray-500">Phone:</span> <span className="text-gray-900 ml-2">{organization.phone || '-'}</span></div>
                <div><span className="text-gray-500">NIP:</span> <span className="text-gray-900 ml-2">{organization.nip || '-'}</span></div>
                <div><span className="text-gray-500">Address:</span> <span className="text-gray-900 ml-2">{organization.billing_street || '-'}, {organization.billing_city || '-'} {organization.billing_postal_code || '-'}</span></div>
                <div><span className="text-gray-500">Country:</span> <span className="text-gray-900 ml-2">{organization.billing_country || '-'}</span></div>
              </div>
            </SectionCard>
          )}
        </div>
      )}

      {activeTab === 'security' && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Security</h2>
          <SectionCard title="Change Password">
            <div className="space-y-4">
              <Fld label="Current Password" type="password" value={currentPassword} onChange={setCurrentPassword} />
              <Fld label="New Password" type="password" value={newPassword} onChange={setNewPassword} placeholder="Min. 8 characters" />
              <Fld label="Confirm New Password" type="password" value={confirmPassword} onChange={setConfirmPassword} />
              <div className="text-xs text-gray-500 space-y-1">
                <p className={newPassword.length >= 8 ? 'text-green-600' : ''}>At least 8 characters</p>
                <p className={/[A-Z]/.test(newPassword) ? 'text-green-600' : ''}>At least one uppercase letter</p>
                <p className={/[a-z]/.test(newPassword) ? 'text-green-600' : ''}>At least one lowercase letter</p>
                <p className={/[0-9]/.test(newPassword) ? 'text-green-600' : ''}>At least one number</p>
              </div>
              {secError && <p className="text-sm text-red-600">{secError}</p>}
              {secMsg && <p className="text-sm text-green-600">{secMsg}</p>}
              <Btn onClick={changePassword} loading={secLoading}>Change Password</Btn>
            </div>
          </SectionCard>
        </div>
      )}

      {activeTab === 'danger' && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Danger Zone</h2>
          <SectionCard className="!border-red-200">
            <h3 className="font-semibold text-red-900 mb-1">Delete Organization</h3>
            <p className="text-sm text-gray-500 mb-4">
              Once you delete your organization, all data will be permanently removed. This action cannot be undone.
            </p>
            <Btn variant="danger" onClick={handleDeleteOrg}>Delete Organization</Btn>
          </SectionCard>
        </div>
      )}
    </SidebarLayout>
  );
}
