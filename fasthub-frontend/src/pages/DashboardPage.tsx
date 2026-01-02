import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Spin, Alert, Button, Empty } from 'antd';
import { UserOutlined, TeamOutlined, CreditCardOutlined, RiseOutlined, PlusOutlined } from '@ant-design/icons';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { superadminApi } from '../api/superadmin';
import { usersApi } from '../api/users';
import { organizationsApi } from '../api/organizations';
import OnboardingModal from '../components/common/OnboardingModal';

const { Title } = Typography;

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
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return <Alert message="Error" description={error} type="error" showIcon />;
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
    <div>
      <Title level={2}>Dashboard</Title>
      <p style={{ color: '#666', marginBottom: 24 }}>
        Welcome back, {user?.full_name}! Here's what's happening with your account.
      </p>

      {/* Orphan User Empty State */}
      {!user?.is_superuser && stats?.total_organizations === 0 && (
        <Alert
          message="Welcome to AutoFlow!"
          description={
            <div>
              <p style={{ marginBottom: 16 }}>You're not part of any organization yet. Create your first organization to get started!</p>
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
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Users"
              value={stats?.total_users || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Organizations"
              value={stats?.total_organizations || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Subscriptions"
              value={stats?.active_subscriptions || 0}
              prefix={<CreditCardOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Revenue"
              value={stats?.revenue_this_month || 0}
              prefix={<RiseOutlined />}
              precision={2}
              suffix="PLN"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="User Growth" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="users" stroke="#8884d8" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Revenue" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="revenue" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Recent Users */}
      {recentUsers.length > 0 && (
        <Card title="Recent Users" style={{ marginTop: 24 }}>
          <div>
            {recentUsers.slice(0, 5).map((u: any) => (
              <div key={u.id} style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
                <strong>{u.full_name || u.email}</strong>
                <span style={{ color: '#999', marginLeft: 16 }}>{u.email}</span>
                <span style={{ float: 'right', color: '#999' }}>
                  {new Date(u.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
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
