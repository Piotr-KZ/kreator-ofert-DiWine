import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import AppShell from './components/layout/AppShell';

// Auth pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';

// Main pages
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import UsersPage from './pages/UsersPage';
import TeamPage from './pages/TeamPage';
import BillingPage from './pages/BillingPage';
import SettingsPage from './pages/SettingsPage';
import AccountPage from './pages/AccountPage';

// SuperAdmin pages
import OrganizationsPage from './pages/superadmin/OrganizationsPage';
import MetricsPage from './pages/superadmin/MetricsPage';

// Dashboard pages
import DashboardLayout from './pages/dashboard/DashboardLayout';
import MySites from './pages/dashboard/MySites';
import SiteDashboard from './pages/dashboard/SiteDashboard';
import IntegrationsGlobal from './pages/dashboard/IntegrationsGlobal';

// Creator pages
import CreatorLayout from './pages/creator/CreatorLayout';
import CreateProject from './pages/creator/CreateProject';
import Step1Brief from './pages/creator/Step1Brief';
import Step2Materials from './pages/creator/Step2Materials';
import Step3Style from './pages/creator/Step3Style';
import Step4Validation from './pages/creator/Step4Validation';
import GeneratingOverlay from './pages/creator/GeneratingOverlay';
import Step5Wireframe from './pages/creator/Step5Wireframe';
import Step6Preview from './pages/creator/Step6Preview';
import Step7Config from './pages/creator/Step7Config';
import Step8Readiness from './pages/creator/Step8Readiness';
import Step9Publish from './pages/creator/Step9Publish';

export const router = createBrowserRouter([
  // Public routes
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/forgot-password',
    element: <ForgotPasswordPage />,
  },
  {
    path: '/reset-password',
    element: <ResetPasswordPage />,
  },
  {
    path: '/onboarding',
    element: (
      <ProtectedRoute>
        <OnboardingPage />
      </ProtectedRoute>
    ),
  },

  // Dashboard routes (Brief 36)
  {
    path: '/panel',
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <MySites /> },
      { path: 'sites/:siteId', element: <SiteDashboard /> },
      { path: 'integrations', element: <IntegrationsGlobal /> },
    ],
  },

  // Creator routes
  {
    path: '/creator/new',
    element: (
      <ProtectedRoute>
        <CreateProject />
      </ProtectedRoute>
    ),
  },
  {
    path: '/creator/:projectId',
    element: (
      <ProtectedRoute>
        <CreatorLayout />
      </ProtectedRoute>
    ),
    children: [
      { path: 'step/1', element: <Step1Brief /> },
      { path: 'step/2', element: <Step2Materials /> },
      { path: 'step/3', element: <Step3Style /> },
      { path: 'step/4', element: <Step4Validation /> },
      { path: 'generating', element: <GeneratingOverlay /> },
      { path: 'step/5', element: <Step5Wireframe /> },
      { path: 'step/6', element: <Step6Preview /> },
      { path: 'step/7', element: <Step7Config /> },
      { path: 'step/8', element: <Step8Readiness /> },
      { path: 'step/9', element: <Step9Publish /> },
    ],
  },

  // Protected routes
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      {
        path: '/',
        element: <DashboardPage />,
      },
      {
        path: '/dashboard',
        element: <DashboardPage />,
      },
      {
        path: '/users',
        element: <UsersPage />,
      },
      {
        path: '/team',
        element: <TeamPage />,
      },
      {
        path: '/billing',
        element: <BillingPage />,
      },
      {
        path: '/settings',
        element: <SettingsPage />,
      },
      {
        path: '/account',
        element: <AccountPage />,
      },

      // SuperAdmin routes
      {
        path: '/superadmin/organizations',
        element: (
          <ProtectedRoute requireSuperuser={true}>
            <OrganizationsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/superadmin/metrics',
        element: (
          <ProtectedRoute requireSuperuser={true}>
            <MetricsPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);
