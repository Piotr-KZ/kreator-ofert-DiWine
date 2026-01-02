import { useEffect, useState } from 'react';
import { Table, Button, Space, Typography, Modal, Form, Input, Select, message, Popconfirm, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons';
import { usersApi } from '../api/users';
import { User } from '../types/models';

const { Title } = Typography;
const { Option } = Select;

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');
  
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchUsers();
  }, [page, pageSize, search]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const { data } = await usersApi.list({ page, per_page: pageSize, search });
      setUsers(data.items || []);
      setTotal(data.total || 0);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to fetch users';
      console.error('UsersPage error:', errorMsg);
      // Don't show error message on 403 (user not authenticated)
      if (error.response?.status !== 403) {
        message.error(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    form.setFieldsValue({
      full_name: user.full_name,
      email: user.email,
      is_superuser: user.is_superuser,
      position: user.position,
    });
    setEditModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await usersApi.delete(id);
      message.success('User deleted successfully');
      fetchUsers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to delete user');
    }
  };

  const handleEditSubmit = async (values: any) => {
    if (!editingUser) return;

    try {
      await usersApi.update(editingUser.id, values);
      message.success('User updated successfully');
      setEditModalVisible(false);
      setEditingUser(null);
      form.resetFields();
      fetchUsers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update user');
    }
  };

  const columns = [
    {
      title: 'Name',
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
      title: 'Super Admin',
      dataIndex: 'is_superuser',
      key: 'is_superuser',
      render: (isSuperuser: boolean) => (
        <Tag color={isSuperuser ? 'red' : 'default'}>
          {isSuperuser ? 'YES' : 'NO'}
        </Tag>
      ),
    },
    {
      title: 'Position',
      dataIndex: 'position',
      key: 'position',
      render: (text: string) => text || '-',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean, record: User) => (
        <div>
          <Tag color={isActive ? 'green' : 'red'}>
            {isActive ? 'Active' : 'Inactive'}
          </Tag>
          {record.is_verified && <Tag color="blue">Verified</Tag>}
        </div>
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
      render: (_: any, record: User) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete user"
            description="Are you sure you want to delete this user?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2} style={{ margin: 0 }}>Users</Title>
        <Space>
          <Input
            placeholder="Search users..."
            prefix={<SearchOutlined />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: 250 }}
          />
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} users`,
          onChange: (page, pageSize) => {
            setPage(page);
            setPageSize(pageSize);
          },
        }}
      />

      {/* Edit Modal */}
      <Modal
        title="Edit User"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          setEditingUser(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Save"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleEditSubmit}
        >
          <Form.Item
            name="full_name"
            label="Full Name"
            rules={[{ required: true, message: 'Please input full name!' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please input email!' },
              { type: 'email', message: 'Please enter a valid email!' }
            ]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="is_superuser"
            label="Super Admin"
            valuePropName="checked"
          >
            <Select>
              <Option value={false}>No - Regular User</Option>
              <Option value={true}>Yes - Super Admin (Global Access)</Option>
            </Select>
          </Form.Item>

          <Form.Item name="position" label="Position">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
