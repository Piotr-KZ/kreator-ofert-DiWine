import { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Typography, Space } from 'antd';
import {
  DashboardOutlined,
  UserOutlined,
  TeamOutlined,
  CreditCardOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BarChartOutlined,
  BankOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  // Auth init moved to App.tsx - no need to fetch here

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      label: 'Profile',
      icon: <UserOutlined />,
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      onClick: handleLogout,
    },
  ];

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      onClick: () => navigate('/dashboard'),
    },
    // Users page only for SuperAdmin
    ...(user?.is_superuser ? [{
      key: '/users',
      icon: <UserOutlined />,
      label: 'Users',
      onClick: () => navigate('/users'),
    }] : []),
    {
      key: '/team',
      icon: <TeamOutlined />,
      label: 'Team',
      onClick: () => navigate('/team'),
    },
    {
      key: '/billing',
      icon: <CreditCardOutlined />,
      label: 'Billing',
      onClick: () => navigate('/billing'),
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/settings'),
    },
  ];

  // Add SuperAdmin menu items if user is superadmin
  if (user?.role === 'superadmin') {
    menuItems.push(
      {
        key: 'superadmin',
        icon: <BankOutlined />,
        label: 'SuperAdmin',
        onClick: undefined,
      } as any,
      {
        key: '/superadmin/organizations',
        icon: <BankOutlined />,
        label: 'Organizations',
        onClick: () => navigate('/superadmin/organizations'),
      },
      {
        key: '/superadmin/metrics',
        icon: <BarChartOutlined />,
        label: 'Metrics',
        onClick: () => navigate('/superadmin/metrics'),
      }
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: 'white',
          fontSize: 20,
          fontWeight: 'bold'
        }}>
          {collapsed ? 'AF' : 'AutoFlow'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'all 0.2s' }}>
        <Header style={{ 
          padding: '0 24px', 
          background: '#fff', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,21,41,.08)'
        }}>
          <div>
            {collapsed ? (
              <MenuUnfoldOutlined 
                style={{ fontSize: 18, cursor: 'pointer' }}
                onClick={() => setCollapsed(false)}
              />
            ) : (
              <MenuFoldOutlined 
                style={{ fontSize: 18, cursor: 'pointer' }}
                onClick={() => setCollapsed(true)}
              />
            )}
          </div>
          
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" trigger={['click']}>
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <Text>{user?.full_name || user?.email}</Text>
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ 
          margin: '24px', 
          padding: 24, 
          background: '#fff',
          minHeight: 280 
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
