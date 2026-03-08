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

// SuperAdmin pages
import OrganizationsPage from './pages/superadmin/OrganizationsPage';
import MetricsPage from './pages/superadmin/MetricsPage';

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
