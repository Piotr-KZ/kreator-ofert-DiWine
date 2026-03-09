import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useOrgStore } from '../store/orgStore';
import { useBillingStore } from '../store/billingStore';
import { SectionCard, StatusBadge, Btn } from '@/components/ui';
import { superadminApi } from '../api/superadmin';
import { AdminStats } from '../types/models';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { organization, fetchOrganization } = useOrgStore();
  const { subscription, fetchSubscription } = useBillingStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        await fetchOrganization();
      } catch {
        // user may not have an org
      }
      try {
        await fetchSubscription();
      } catch {
        // billing may not be configured
      }
      if (user?.is_superuser) {
        try {
          const { data } = await superadminApi.getMetrics();
          setStats(data);
        } catch {
          // metrics may fail
        }
      }
      setLoading(false);
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  // No organization — show create prompt
  if (!organization) {
    return (
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
        <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-6">
          <h3 className="font-semibold text-indigo-900 mb-2">Get Started</h3>
          <p className="text-sm text-indigo-700 mb-4">
            You're not part of any organization yet. Create your first organization to get started!
          </p>
          <Btn onClick={() => navigate('/onboarding')}>Create Organization</Btn>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* Stats cards */}
      {user?.is_superuser && stats ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <SectionCard>
            <p className="text-sm text-gray-500">Total Users</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
          </SectionCard>
          <SectionCard>
            <p className="text-sm text-gray-500">Organizations</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total_organizations}</p>
          </SectionCard>
          <SectionCard>
            <p className="text-sm text-gray-500">Active Subscriptions</p>
            <p className="text-2xl font-bold text-gray-900">
              {stats.active_subscriptions}
              <span className="text-sm text-gray-400 font-normal"> / {stats.total_subscriptions}</span>
            </p>
          </SectionCard>
          <SectionCard>
            <p className="text-sm text-gray-500">Revenue This Month</p>
            <p className="text-2xl font-bold text-gray-900">{stats.revenue_this_month?.toFixed(2) || '0.00'} PLN</p>
          </SectionCard>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <SectionCard>
            <p className="text-sm text-gray-500">Organization</p>
            <p className="text-lg font-bold text-gray-900">{organization.name}</p>
          </SectionCard>
          <SectionCard>
            <p className="text-sm text-gray-500">Team Members</p>
            <p className="text-lg font-bold text-gray-900">{'user_count' in organization ? (organization as any).user_count : '-'}</p>
          </SectionCard>
          <SectionCard>
            <p className="text-sm text-gray-500">Subscription</p>
            <div className="flex items-center gap-2 mt-1">
              <p className="text-lg font-bold text-gray-900 capitalize">{subscription?.plan?.name || subscription?.plan || 'Free'}</p>
              <StatusBadge variant={subscription?.subscription?.status === 'active' || subscription?.status === 'active' ? 'success' : 'warning'}>
                {subscription?.subscription?.status || subscription?.status || 'none'}
              </StatusBadge>
            </div>
          </SectionCard>
          <SectionCard>
            <p className="text-sm text-gray-500">Type</p>
            <p className="text-lg font-bold text-gray-900 capitalize">{organization.type}</p>
          </SectionCard>
        </div>
      )}
    </div>
  );
}
