import { useEffect } from 'react';
import { useBillingStore } from '../store/billingStore';
import { billingApi } from '../api/billing';
import { BillingPlan } from '../types/models';
import { Tile, StatusBadge, Btn, SectionCard } from '@/components/ui';

const fallbackPlans = [
  { slug: 'free', name: 'Free', price_monthly: 0, features: ['1 user', 'Basic features', 'Community support'] },
  { slug: 'pro', name: 'Pro', price_monthly: 199, features: ['10 users', 'All features', 'Priority support', 'API access'], recommended: true },
  { slug: 'enterprise', name: 'Enterprise', price_monthly: 999, features: ['Unlimited users', 'All features', 'Dedicated support', 'Custom integrations', 'SLA'] },
];

function getPlanFeatures(plan: BillingPlan): string[] {
  const features: string[] = [];
  if (plan.max_team_members > 0) features.push(`${plan.max_team_members} users`);
  if (plan.max_processes > 0) features.push(`${plan.max_processes} processes`);
  if (plan.max_integrations > 0) features.push(`${plan.max_integrations} integrations`);
  if (plan.max_ai_operations_month > 0) features.push(`${plan.max_ai_operations_month} AI ops/month`);
  if (plan.max_file_storage_mb > 0) features.push(`${plan.max_file_storage_mb} MB storage`);
  return features.length > 0 ? features : ['Basic features'];
}

export default function BillingPage() {
  const { subscription, plans, isLoading, error, fetchSubscription, fetchPlans } = useBillingStore();

  useEffect(() => {
    fetchSubscription();
    fetchPlans();
  }, []);

  if (isLoading) {
    return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" /></div>;
  }

  const handleCheckout = async (plan: BillingPlan) => {
    try {
      const { data } = await billingApi.createCheckout(
        plan.slug,
        `${window.location.origin}/billing?success=true`,
        `${window.location.origin}/billing?canceled=true`,
      );
      if (data.payment_url) {
        window.location.href = data.payment_url;
      }
    } catch {
      // Stripe not configured
    }
  };

  const handlePortal = async () => {
    try {
      const { data } = await billingApi.createPortal(`${window.location.origin}/billing`);
      if (data.url) {
        window.location.href = data.url;
      }
    } catch {
      // Portal not available
    }
  };

  const displayPlans = plans.length > 0 ? plans : null;
  const currentPlanSlug = subscription?.plan?.slug || subscription?.subscription?.plan;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Billing</h1>

      {error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-amber-700">Billing information is not available. Payment integration coming soon.</p>
        </div>
      )}

      {/* Current Plan */}
      {subscription?.subscription && (
        <SectionCard title="Current Subscription" className="mb-6">
          <div className="flex items-center gap-4">
            <div>
              <p className="text-lg font-bold text-gray-900 capitalize">
                {subscription.plan?.name || subscription.subscription?.status || 'Active'} Plan
              </p>
              <p className="text-sm text-gray-500">
                Status: {subscription.subscription.status}
              </p>
            </div>
            <StatusBadge variant={subscription.subscription.status === 'active' ? 'success' : subscription.subscription.status === 'past_due' ? 'warning' : 'error'}>
              {subscription.subscription.status}
            </StatusBadge>
            <Btn variant="ghost" onClick={handlePortal}>Manage</Btn>
          </div>
        </SectionCard>
      )}

      {/* Plans from API */}
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Plans</h2>
      {displayPlans ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {displayPlans.map((plan) => {
            const isActive = currentPlanSlug === plan.slug;
            const features = getPlanFeatures(plan);
            return (
              <Tile key={plan.slug} on={isActive} className="relative">
                {plan.badge && (
                  <span className="absolute -top-2 left-4 bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full font-medium">
                    {plan.badge}
                  </span>
                )}
                <div className="pt-2">
                  <h3 className="font-bold text-gray-900">{plan.name}</h3>
                  {plan.description && <p className="text-sm text-gray-500 mt-1">{plan.description}</p>}
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {plan.price_monthly} <span className="text-sm font-normal text-gray-500">{plan.currency}/mo</span>
                  </p>
                  <ul className="mt-4 space-y-2">
                    {features.map((f) => (
                      <li key={f} className="flex items-center gap-2 text-sm text-gray-600">
                        <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        {f}
                      </li>
                    ))}
                  </ul>
                  <div className="mt-4">
                    {isActive ? (
                      <StatusBadge variant="success">Current Plan</StatusBadge>
                    ) : (
                      <Btn variant="ghost" className="w-full" onClick={() => handleCheckout(plan)}>
                        Choose Plan
                      </Btn>
                    )}
                  </div>
                </div>
              </Tile>
            );
          })}
        </div>
      ) : (
        /* Fallback hardcoded plans */
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {fallbackPlans.map((plan) => {
            const isActive = currentPlanSlug === plan.slug;
            return (
              <Tile key={plan.slug} on={isActive} className="relative">
                {'recommended' in plan && plan.recommended && (
                  <span className="absolute -top-2 left-4 bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full font-medium">
                    RECOMMENDED
                  </span>
                )}
                <div className="pt-2">
                  <h3 className="font-bold text-gray-900">{plan.name}</h3>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {plan.price_monthly} <span className="text-sm font-normal text-gray-500">PLN/mo</span>
                  </p>
                  <ul className="mt-4 space-y-2">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-center gap-2 text-sm text-gray-600">
                        <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        {f}
                      </li>
                    ))}
                  </ul>
                  <div className="mt-4">
                    {isActive ? (
                      <StatusBadge variant="success">Current Plan</StatusBadge>
                    ) : (
                      <Btn variant="ghost" className="w-full" disabled>
                        Coming Soon
                      </Btn>
                    )}
                  </div>
                </div>
              </Tile>
            );
          })}
        </div>
      )}

      {!subscription?.subscription && !error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-sm text-amber-700">Payment integration coming soon. Plan management will be available once billing is configured.</p>
        </div>
      )}
    </div>
  );
}
