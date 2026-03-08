import { useEffect } from 'react';
import { useBillingStore } from '../store/billingStore';
import { Tile, StatusBadge, Btn, SectionCard } from '@/components/ui';

const plans = [
  { id: 'free', name: 'Free', price: '0', features: ['1 user', 'Basic features', 'Community support'] },
  { id: 'pro', name: 'Pro', price: '199', features: ['10 users', 'All features', 'Priority support', 'API access'], recommended: true },
  { id: 'enterprise', name: 'Enterprise', price: '999', features: ['Unlimited users', 'All features', 'Dedicated support', 'Custom integrations', 'SLA'] },
];

export default function BillingPage() {
  const { subscription, isLoading, error, fetchSubscription } = useBillingStore();

  useEffect(() => { fetchSubscription(); }, []);

  if (isLoading) {
    return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" /></div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Billing</h1>

      {error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-amber-700">Billing information is not available. Stripe integration coming soon.</p>
        </div>
      )}

      {/* Current Plan */}
      {subscription && (
        <SectionCard title="Current Subscription" className="mb-6">
          <div className="flex items-center gap-4">
            <div>
              <p className="text-lg font-bold text-gray-900 capitalize">{subscription.plan} Plan</p>
              <p className="text-sm text-gray-500">
                Period: {new Date(subscription.current_period_start).toLocaleDateString()} — {new Date(subscription.current_period_end).toLocaleDateString()}
              </p>
            </div>
            <StatusBadge variant={subscription.status === 'active' ? 'success' : subscription.status === 'past_due' ? 'warning' : 'error'}>
              {subscription.status}
            </StatusBadge>
          </div>
        </SectionCard>
      )}

      {/* Plans */}
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Plans</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {plans.map((plan) => {
          const isActive = subscription?.plan === plan.id;
          return (
            <Tile key={plan.id} on={isActive} className="relative">
              {plan.recommended && (
                <span className="absolute -top-2 left-4 bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full font-medium">
                  RECOMMENDED
                </span>
              )}
              <div className="pt-2">
                <h3 className="font-bold text-gray-900">{plan.name}</h3>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {plan.price} <span className="text-sm font-normal text-gray-500">PLN/mo</span>
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
                      Upgrade
                    </Btn>
                  )}
                </div>
              </div>
            </Tile>
          );
        })}
      </div>

      {!subscription && !error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-sm text-amber-700">Stripe integration coming soon. Plan management will be available once billing is configured.</p>
        </div>
      )}
    </div>
  );
}
