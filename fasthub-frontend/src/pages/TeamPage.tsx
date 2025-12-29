import { useEffect, useState } from 'react';
import { Table, Button, Space, Typography, Modal, Form, Input, Select, message, Tag, Card } from 'antd';
import { PlusOutlined, MailOutlined, UserAddOutlined } from '@ant-design/icons';
import { usersApi } from '../api/users';
import { User } from '../types/models';

const { Title, Paragraph } = Typography;
const { Option } = Select;

export default function TeamPage() {
  const [members, setMembers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [inviteModalVisible, setInviteModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchTeamMembers();
  }, []);

  const fetchTeamMembers = async () => {
    setLoading(true);
    try {
      const { data } = await usersApi.list({ per_page: 100 });
      setMembers(data.items || []);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch team members');
    } finally {
      setLoading(false);
    }
  };

  const handleInviteSubmit = async (values: any) => {
    try {
      // Note: Backend doesn't have /team/invite endpoint yet
      // Using placeholder message
      message.info('Team invite feature coming soon - backend endpoint not implemented');
      setInviteModalVisible(false);
      form.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to send invitation');
    }
  };

  const columns = [
    {
      title: 'Member',
      dataIndex: 'full_name',
      key: 'full_name',
      render: (text: string, record: User) => (
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
      render: (role: string) => {
        const colors: Record<string, string> = {
          superadmin: 'red',
          admin: 'orange',
          user: 'blue',
          viewer: 'green',
        };
        return <Tag color={colors[role] || 'default'}>{role.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Position',
      dataIndex: 'position',
      key: 'position',
      render: (text: string) => text || '-',
    },
    {
      title: 'Last Login',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      render: (date: string) => date ? new Date(date).toLocaleDateString() : 'Never',
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
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>Team</Title>
          <Paragraph type="secondary">Manage your team members and their roles</Paragraph>
        </div>
        <Button 
          type="primary" 
          icon={<UserAddOutlined />}
          onClick={() => setInviteModalVisible(true)}
        >
          Invite Member
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={members}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Invite Modal */}
      <Modal
        title="Invite Team Member"
        open={inviteModalVisible}
        onCancel={() => {
          setInviteModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Send Invitation"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleInviteSubmit}
        >
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please input email!' },
              { type: 'email', message: 'Please enter a valid email!' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="colleague@example.com" />
          </Form.Item>

          <Form.Item
            name="role"
            label="Role"
            rules={[{ required: true, message: 'Please select role!' }]}
            initialValue="user"
          >
            <Select>
              <Option value="viewer">Viewer - Can view only</Option>
              <Option value="user">User - Can view and edit</Option>
              <Option value="admin">Admin - Full access</Option>
            </Select>
          </Form.Item>

          <Form.Item name="message" label="Personal Message (Optional)">
            <Input.TextArea rows={3} placeholder="Add a personal message to the invitation..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
