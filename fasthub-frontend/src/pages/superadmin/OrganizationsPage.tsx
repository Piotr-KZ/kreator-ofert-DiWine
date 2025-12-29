import { useEffect, useState } from 'react';
import { Table, Typography, Card, Tag, Space, Button, message } from 'antd';
import { BankOutlined, SearchOutlined } from '@ant-design/icons';
import { usersApi } from '../../api/users';

const { Title, Paragraph } = Typography;

export default function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    setLoading(true);
    try {
      // Note: Backend doesn't have /admin/organizations endpoint
      // Using users as placeholder
      const { data } = await usersApi.list({ per_page: 100 });
      
      // Group users by organization_id
      const orgMap = new Map();
      data.items?.forEach((user: any) => {
        if (!orgMap.has(user.organization_id)) {
          orgMap.set(user.organization_id, {
            id: user.organization_id,
            name: `Organization ${user.organization_id.slice(0, 8)}`,
            users_count: 0,
            created_at: user.created_at,
          });
        }
        const org = orgMap.get(user.organization_id);
        org.users_count++;
      });
      
      setOrganizations(Array.from(orgMap.values()));
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch organizations');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Organization ID',
      dataIndex: 'id',
      key: 'id',
      render: (id: string) => (
        <Space>
          <BankOutlined />
          <span>{id.slice(0, 12)}...</span>
        </Space>
      ),
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Users',
      dataIndex: 'users_count',
      key: 'users_count',
      render: (count: number) => <Tag color="blue">{count} users</Tag>,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: () => (
        <Button type="link" icon={<SearchOutlined />}>
          View Details
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Organizations</Title>
      <Paragraph type="secondary">
        Manage all organizations in the system
      </Paragraph>

      <Card>
        <Table
          columns={columns}
          dataSource={organizations}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  );
}
