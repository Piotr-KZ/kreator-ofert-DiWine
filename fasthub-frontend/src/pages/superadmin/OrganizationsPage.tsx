import { useEffect, useState } from 'react';
import { Table, Typography, Card, Tag, Space, Button, message, Alert } from 'antd';
import { BankOutlined, SearchOutlined } from '@ant-design/icons';
import { superadminApi } from '../../api/superadmin';
import { Organization } from '../../types/models';

const { Title, Paragraph } = Typography;

interface OrganizationWithStats extends Organization {
  users_count?: number;
  subscriptions_count?: number;
}

export default function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<OrganizationWithStats[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    setLoading(true);
    try {
      // Use superadmin API to list all organizations
      const { data } = await superadminApi.listOrganizations();
      setOrganizations(data.items || []);
    } catch (error: any) {
      console.error('Failed to fetch organizations:', error);
      message.error(error.response?.data?.detail || 'Failed to fetch organizations');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Organization',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: OrganizationWithStats) => (
        <div>
          <div>
            <BankOutlined style={{ marginRight: 8 }} />
            <strong>{name}</strong>
          </div>
          <div style={{ fontSize: 12, color: '#999' }}>
            {record.slug}
          </div>
        </div>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color={type === 'business' ? 'blue' : 'green'}>
          {type.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Members',
      dataIndex: 'users_count',
      key: 'users_count',
      render: (count?: number) => (
        <Tag color="blue">{count || 0} members</Tag>
      ),
    },
    {
      title: 'Location',
      key: 'location',
      render: (_: any, record: OrganizationWithStats) => (
        <span>{record.billing_city}, {record.billing_country}</span>
      ),
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
      render: (_: any, record: OrganizationWithStats) => (
        <Button 
          type="link" 
          icon={<SearchOutlined />}
          onClick={() => message.info('View details feature coming soon')}
        >
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

      <Alert
        message="Super Admin View"
        description="You are viewing all organizations across the entire platform. This view is only available to Super Admins."
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

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
