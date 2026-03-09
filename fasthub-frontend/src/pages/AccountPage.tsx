import { lazy, Suspense, useState } from 'react';
import SidebarLayout from '@/components/layout/SidebarLayout';

const ProfileTab = lazy(() => import('./account/ProfileTab'));
const CompanyTab = lazy(() => import('./account/CompanyTab'));
const PlanTab = lazy(() => import('./account/PlanTab'));
const PaymentsTab = lazy(() => import('./account/PaymentsTab'));
const InvoicesTab = lazy(() => import('./account/InvoicesTab'));
const SecurityTab = lazy(() => import('./account/SecurityTab'));
const TeamTab = lazy(() => import('./account/TeamTab'));
const NotificationsTab = lazy(() => import('./account/NotificationsTab'));
const ApiTab = lazy(() => import('./account/ApiTab'));

const tabs = [
  { id: 'profile', name: 'Profil' },
  { id: 'company', name: 'Firma' },
  { id: 'plan', name: 'Plan' },
  { id: 'payments', name: 'Płatności' },
  { id: 'invoices', name: 'Faktury' },
  { id: 'security', name: 'Bezpieczeństwo' },
  { id: 'team', name: 'Zespół' },
  { id: 'notifications', name: 'Powiadomienia' },
  { id: 'api', name: 'API i webhook' },
];

const TAB_COMPONENTS: Record<string, React.LazyExoticComponent<() => JSX.Element>> = {
  profile: ProfileTab,
  company: CompanyTab,
  plan: PlanTab,
  payments: PaymentsTab,
  invoices: InvoicesTab,
  security: SecurityTab,
  team: TeamTab,
  notifications: NotificationsTab,
  api: ApiTab,
};

const Loading = () => (
  <div className="flex items-center justify-center py-12">
    <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
  </div>
);

export default function AccountPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const ActiveComponent = TAB_COMPONENTS[activeTab] || ProfileTab;

  return (
    <SidebarLayout tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab}>
      <Suspense fallback={<Loading />}>
        <ActiveComponent />
      </Suspense>
    </SidebarLayout>
  );
}
