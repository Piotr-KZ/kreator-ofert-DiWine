import { useEffect, useState } from 'react';
import { useBillingStore } from '@/store/billingStore';
import { billingApi } from '@/api/billing';
import { Btn, SectionCard, StatusBadge, Tile, Toggle } from '@/components/ui';
import type { BillingPlan, UsageItem } from '@/types/models';

export default function PlanTab() {
  const { subscription, plans, fetchSubscription, fetchPlans } = useBillingStore();
  const [usage, setUsage] = useState<UsageItem[]>([]);
  const [yearly, setYearly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        await Promise.all([fetchSubscription(), fetchPlans()]);
        try {
          const u = await billingApi.getUsage();
          setUsage(Array.isArray(u) ? u : []);
        } catch {
          // Usage endpoint may not exist yet
        }
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const statusVariant = (s?: string) => {
    if (s === 'active') return 'success';
    if (s === 'trialing') return 'info';
    if (s === 'past_due') return 'warning';
    return 'error';
  };

  const progressColor = (pct: number) => {
    if (pct >= 90) return 'bg-red-500';
    if (pct >= 70) return 'bg-amber-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Plan i abonament</h2>

      <SectionCard title="Aktualny plan">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-lg font-semibold text-gray-900">
            {subscription?.plan || 'Free'}
          </span>
          <StatusBadge variant={statusVariant(subscription?.status)}>
            {subscription?.status || 'brak'}
          </StatusBadge>
        </div>
        {subscription?.current_period_end && (
          <p className="text-sm text-gray-500 mb-4">
            Następne odnowienie: {new Date(subscription.current_period_end).toLocaleDateString('pl-PL')}
          </p>
        )}

        {usage.length > 0 && (
          <div className="space-y-3">
            {usage.map((item) => {
              const pct = item.limit > 0 ? Math.min((item.current / item.limit) * 100, 100) : 0;
              return (
                <div key={item.resource}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{item.resource}</span>
                    <span className="text-gray-900 font-medium">{item.current} / {item.limit}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div className={`h-2 rounded-full ${progressColor(pct)}`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </SectionCard>

      <SectionCard title="Dostępne plany">
        <div className="flex items-center gap-3 mb-6">
          <span className="text-sm text-gray-600">Miesięcznie</span>
          <Toggle on={yearly} onClick={() => setYearly(!yearly)} />
          <span className="text-sm text-gray-600">Rocznie</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {plans.map((plan) => {
            const isCurrent = subscription?.plan?.toLowerCase() === plan.slug?.toLowerCase();
            const price = yearly ? plan.price_yearly : plan.price_monthly;
            const period = yearly ? '/rok' : '/mies.';

            return (
              <Tile key={plan.slug} on={isCurrent}>
                <div className="p-2">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-bold text-gray-900">{plan.name}</span>
                    {plan.badge && (
                      <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">{plan.badge}</span>
                    )}
                  </div>
                  <div className="mb-3">
                    <span className="text-2xl font-bold text-gray-900">{price}</span>
                    <span className="text-sm text-gray-500"> {plan.currency}{period}</span>
                  </div>
                  {plan.description && (
                    <p className="text-xs text-gray-500 mb-3">{plan.description}</p>
                  )}
                  <ul className="text-xs text-gray-600 space-y-1 mb-4">
                    <li>Zespół: do {plan.max_team_members} osób</li>
                    <li>Dysk: {plan.max_file_storage_mb} MB</li>
                    <li>Procesy: {plan.max_processes}</li>
                  </ul>
                  <Btn
                    variant={isCurrent ? 'ghost' : 'primary'}
                    disabled={isCurrent}
                    className="w-full"
                  >
                    {isCurrent ? 'Aktualny plan' : 'Wybierz plan'}
                  </Btn>
                </div>
              </Tile>
            );
          })}
        </div>
      </SectionCard>
    </div>
  );
}
