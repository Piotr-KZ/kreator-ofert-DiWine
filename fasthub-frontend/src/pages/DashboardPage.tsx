import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Spin, Alert, Button, Space } from 'antd';
import { UserOutlined, TeamOutlined, CreditCardOutlined, RiseOutlined, PlusOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { superadminApi } from '../api/superadmin';
import { usersApi } from '../api/users';
import { organizationsApi } from '../api/organizations';
import OnboardingModal from '../components/common/OnboardingModal';

const { Title, Paragraph, Text } = Typography;

export default function DashboardPage() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [recentUsers, setRecentUsers] = useState<any[]>([]);
  const [organization, setOrganization] = useState<any>(null);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    // Only fetch if user is authenticated
    if (user) {
      fetchDashboardData();
    }
  }, [user?.id]); // Only re-fetch when user ID changes, not on every user object change

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      if (user?.role === 'superadmin') {
        // SuperAdmin dashboard
        const [statsRes, usersRes] = await Promise.all([
          superadminApi.getMetrics(),
          superadminApi.getRecentUsers(),
        ]);
        
        setStats(statsRes.data);
        setRecentUsers(usersRes.data);
      } else {
        // Regular user dashboard
        try {
          const orgRes = await organizationsApi.getCurrent();
          setOrganization(orgRes.data);
          setStats({
            total_users: orgRes.data.member_count || 0,
            total_organizations: 1,
            total_subscriptions: orgRes.data.subscription_status === 'active' ? 1 : 0,
            active_subscriptions: orgRes.data.subscription_status === 'active' ? 1 : 0,
          });
        } catch (err: any) {
          // User has no organization
          if (err.response?.status === 404) {
            setOrganization(null);
            setStats({
              total_users: 0,
              total_organizations: 0,
              total_subscriptions: 0,
              active_subscriptions: 0,
            });
          } else {
            throw err;
          }
        }
        setRecentUsers([]);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to load dashboard data';
      console.error('Dashboard error:', errorMsg);
      setError(errorMsg);
      // Don't retry on 403/404 errors
      if (err.response?.status === 403 || err.response?.status === 404) {
        console.warn('API endpoint not available or forbidden');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
    // Refresh organization data
    fetchDashboardData();
  };

  const handleOnboardingSkip = () => {
    setShowOnboarding(false);
    // Store skip flag in localStorage to not show again this session
    localStorage.setItem('onboarding_skipped', 'true');
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <Paragraph style={{ marginTop: 24, color: '#999' }}>Loading dashboard...</Paragraph>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: 600, margin: '50px auto' }}>
        <Alert 
          message="Error Loading Dashboard" 
          description={error} 
          type="error" 
          showIcon 
          style={{ borderRadius: 8 }}
        />
      </div>
    );
  }

  // Mock chart data
  const chartData = [
    { name: 'Jan', users: 400, revenue: 2400 },
    { name: 'Feb', users: 300, revenue: 1398 },
    { name: 'Mar', users: 200, revenue: 9800 },
    { name: 'Apr', users: 278, revenue: 3908 },
    { name: 'May', users: 189, revenue: 4800 },
    { name: 'Jun', users: 239, revenue: 3800 },
  ];

  return (
    <div style={{ padding: '24px 0' }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <Title level={2} style={{ marginBottom: 8 }}>Dashboard</Title>
        <Paragraph style={{ fontSize: 16, color: '#666', marginBottom: 0 }}>
          Welcome back, <Text strong>{user?.full_name}</Text>! Here's what's happening with your account.
        </Paragraph>
      </div>

      {/* Orphan User Empty State */}
      {!user?.is_superuser && stats?.total_organizations === 0 && (
        <Alert
          message={
            <Text strong style={{ fontSize: 16 }}>Welcome to FastHub!</Text>
          }
          description={
            <div style={{ marginTop: 12 }}>
              <Paragraph style={{ marginBottom: 20, fontSize: 15 }}>
                You're not part of any organization yet. Create your first organization to get started!
              </Paragraph>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                onClick={() => navigate('/onboarding')}
                size="large"
              >
                Create Your First Organization
              </Button>
            </div>
          }
          type="info"
          showIcon
          style={{ 
            marginBottom: 32, 
            borderRadius: 8,
            padding: '24px',
            border: '1px solid #1890ff'
          }}
        />
      )}

      {/* Stats Cards */}
      <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card 
            style={{ borderRadius: 8, height: '100%' }}
            bodyStyle={{ padding: '28px' }}
          >
            <Statistic
              title={<Text style={{ fontSize: 14, color: '#666' }}>Total Users</Text>}
              value={stats?.total_users || 0}
              prefix={<UserOutlined style={{ color: '#52c41a', fontSize: 24 }} />}
              valueStyle={{ color: '#52c41a', fontSize: 32, fontWeight: 600 }}
            />
            <div style={{ marginTop: 12 }}>
              <Text type="secondary" style={{ fontSize: 13 }}>
                <ArrowUpOutlined style={{ color: '#52c41a' }} /> +12% from last month
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card 
            style={{ borderRadius: 8, height: '100%' }}
            bodyStyle={{ padding: '28px' }}
          >
            <Statistic
              title={<Text style={{ fontSize: 14, color: '#666' }}>Organizations</Text>}
              value={stats?.total_organizations || 0}
              prefix={<TeamOutlined style={{ color: '#1890ff', fontSize: 24 }} />}
              valueStyle={{ color: '#1890ff', fontSize: 32, fontWeight: 600 }}
            />
            <div style={{ marginTop: 12 }}>
              <Text type="secondary" style={{ fontSize: 13 }}>
                <ArrowUpOutlined style={{ color: '#52c41a' }} /> +5% from last month
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card 
            style={{ borderRadius: 8, height: '100%' }}
            bodyStyle={{ padding: '28px' }}
          >
            <Statistic
              title={<Text style={{ fontSize: 14, color: '#666' }}>Active Subscriptions</Text>}
              value={stats?.active_subscriptions || 0}
              prefix={<CreditCardOutlined style={{ color: '#faad14', fontSize: 24 }} />}
              valueStyle={{ color: '#faad14', fontSize: 32, fontWeight: 600 }}
            />
            <div style={{ marginTop: 12 }}>
              <Text type="secondary" style={{ fontSize: 13 }}>
                <ArrowDownOutlined style={{ color: '#ff4d4f' }} /> -2% from last month
              </Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card 
            style={{ borderRadius: 8, height: '100%' }}
            bodyStyle={{ padding: '28px' }}
          >
            <Statistic
              title={<Text style={{ fontSize: 14, color: '#666' }}>Revenue This Month</Text>}
              value={stats?.revenue_this_month || 0}
              prefix={<RiseOutlined style={{ color: '#722ed1', fontSize: 24 }} />}
              precision={2}
              suffix="PLN"
              valueStyle={{ color: '#722ed1', fontSize: 32, fontWeight: 600 }}
            />
            <div style={{ marginTop: 12 }}>
              <Text type="secondary" style={{ fontSize: 13 }}>
                <ArrowUpOutlined style={{ color: '#52c41a' }} /> +18% from last month
              </Text>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
        <Col xs={24} lg={12}>
          <Card 
            title={
              <div>
                <Title level={4} style={{ marginBottom: 4 }}>User Growth</Title>
                <Text type="secondary">Monthly active users over time</Text>
              </div>
            }
            bordered={false}
            style={{ borderRadius: 8, height: '100%' }}
            bodyStyle={{ padding: '32px' }}
          >
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="name" 
                  stroke="#999"
                  style={{ fontSize: 13 }}
                />
                <YAxis 
                  stroke="#999"
                  style={{ fontSize: 13 }}
                />
                <Tooltip 
                  contentStyle={{ 
                    borderRadius: 8, 
                    border: '1px solid #f0f0f0',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                />
                <Legend 
                  wrapperStyle={{ fontSize: 14 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="users" 
                  stroke="#1890ff" 
                  strokeWidth={3}
                  activeDot={{ r: 6 }} 
                  name="Users"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card 
            title={
              <div>
                <Title level={4} style={{ marginBottom: 4 }}>Revenue</Title>
                <Text type="secondary">Monthly revenue in PLN</Text>
              </div>
            }
            bordered={false}
            style={{ borderRadius: 8, height: '100%' }}
            bodyStyle={{ padding: '32px' }}
          >
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="name" 
                  stroke="#999"
                  style={{ fontSize: 13 }}
                />
                <YAxis 
                  stroke="#999"
                  style={{ fontSize: 13 }}
                />
                <Tooltip 
                  contentStyle={{ 
                    borderRadius: 8, 
                    border: '1px solid #f0f0f0',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                />
                <Legend 
                  wrapperStyle={{ fontSize: 14 }}
                />
                <Bar 
                  dataKey="revenue" 
                  fill="#52c41a" 
                  radius={[8, 8, 0, 0]}
                  name="Revenue (PLN)"
                />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Recent Users */}
      {recentUsers.length > 0 && (
        <Card 
          title={
            <div>
              <Title level={4} style={{ marginBottom: 4 }}>Recent Users</Title>
              <Text type="secondary">Latest registered users</Text>
            </div>
          }
          style={{ borderRadius: 8 }}
          bodyStyle={{ padding: '32px' }}
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {recentUsers.slice(0, 5).map((u: any) => (
              <div 
                key={u.id} 
                style={{ 
                  padding: '16px 0', 
                  borderBottom: '1px solid #f0f0f0',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <Text strong style={{ fontSize: 15, display: 'block', marginBottom: 4 }}>
                    {u.full_name || u.email}
                  </Text>
                  <Text type="secondary" style={{ fontSize: 13 }}>{u.email}</Text>
                </div>
                <Text type="secondary" style={{ fontSize: 13 }}>
                  {new Date(u.created_at).toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric', 
                    year: 'numeric' 
                  })}
                </Text>
              </div>
            ))}
          </Space>
        </Card>
      )}

      {/* Onboarding Modal */}
      {organization && showOnboarding && (
        <OnboardingModal
          visible={showOnboarding}
          organizationId={organization.id}
          organizationName={organization.name}
          onComplete={handleOnboardingComplete}
          onSkip={handleOnboardingSkip}
        />
      )}
    </div>
  );
}
