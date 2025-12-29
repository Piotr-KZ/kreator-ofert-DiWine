import { RouterProvider } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { router } from './router';

function App() {
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
