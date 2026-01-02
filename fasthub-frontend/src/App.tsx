import { RouterProvider } from 'react-router-dom';
import { ConfigProvider, Spin } from 'antd';
import { router } from './router';
import { useAuthStore } from './store/authStore';
import { useEffect } from 'react';

function App() {
  const { fetchCurrentUser, isLoading } = useAuthStore();
  
  // Initialize auth state once at app start
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchCurrentUser();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Show global loading spinner during initial auth check
  if (isLoading && !useAuthStore.getState().user) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }
  
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#667eea',
          borderRadius: 6,
        },
      }}
    >
      <RouterProvider router={router} />
    </ConfigProvider>
  );
}

export default App;
