import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Spin } from 'antd';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireSuperuser?: boolean;  // Require superuser access
}

export const ProtectedRoute = ({ children, requireSuperuser }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, user } = useAuthStore();

  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check superuser access if required
  if (requireSuperuser && user && !user.is_superuser) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};
