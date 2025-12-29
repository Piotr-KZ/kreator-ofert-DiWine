import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Spin, Alert, Table, Tag } from 'antd';
import { UserOutlined, BankOutlined, CreditCardOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { superadminApi } from '../../api/superadmin';

const { Title, Paragraph } = Typography;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function MetricsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [recentUsers, setRecentUsers] = useState<any[]>([]);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [statsRes, usersRes] = await Promise.all([
        superadminApi.getMetrics(),
        superadminApi.getRecentUsers(),
      ]);
      
      setStats(statsRes.data);
      setRecentUsers(usersRes.data || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load metrics');
    } finally {
      setLoading(false);
    }
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

  // Mock data for charts
  const growthData = [
    { month: 'Jan', users: 400, orgs: 240, revenue: 2400 },
    { month: 'Feb', users: 300, orgs: 139, revenue: 2210 },
    { month: 'Mar', users: 200, orgs: 980, revenue: 2290 },
    { month: 'Apr', users: 278, orgs: 390, revenue: 2000 },
    { month: 'May', users: 189, orgs: 480, revenue: 2181 },
    { month: 'Jun', users: 239, orgs: 380, revenue: 2500 },
  ];

  const planDistribution = [
    { name: 'Free', value: 400 },
    { name: 'Pro', value: 300 },
    { name: 'Enterprise', value: 100 },
  ];

  const revenueChange = stats?.revenue_this_month > stats?.revenue_last_month;
  const revenuePercent = stats?.revenue_last_month 
    ? ((stats.revenue_this_month - stats.revenue_last_month) / stats.revenue_last_month * 100).toFixed(1)
    : 0;

  const userColumns = [
    {
      title: 'User',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (text: string, record: any) => (
        <div>
          <div><strong>{text || 'N/A'}</strong></div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.email}</div>
        </div>
      ),
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => <Tag color="blue">{role.toUpperCase()}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
  ];

  return (
    <div>
      <Title level={2}>System Metrics</Title>
      <Paragraph type="secondary">
        Overview of system-wide statistics and performance
      </Paragraph>

      {/* Key Metrics */}
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
              prefix={<BankOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Subscriptions"
              value={stats?.active_subscriptions || 0}
              suffix={`/ ${stats?.total_subscriptions || 0}`}
              prefix={<CreditCardOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Revenue This Month"
              value={stats?.revenue_this_month || 0}
              precision={2}
              suffix="PLN"
              prefix={revenueChange ? <RiseOutlined /> : <FallOutlined />}
              valueStyle={{ color: revenueChange ? '#3f8600' : '#cf1322' }}
            />
            <div style={{ fontSize: 12, color: '#999', marginTop: 8 }}>
              {revenueChange ? '+' : ''}{revenuePercent}% from last month
            </div>
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Growth Trends">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={growthData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="users" stroke="#8884d8" name="Users" />
                <Line type="monotone" dataKey="orgs" stroke="#82ca9d" name="Organizations" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Plan Distribution">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={planDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => entry.name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {planDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Revenue Chart */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="Monthly Revenue">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={growthData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="revenue" fill="#82ca9d" name="Revenue (PLN)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Recent Users */}
      <Card title="Recent Users">
        <Table
          columns={userColumns}
          dataSource={recentUsers}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}
