import { useEffect, useState } from 'react';
import { Tabs, Card, Form, Input, Button, message, Typography, Divider, Space, Modal, Select } from 'antd';
import { UserOutlined, LockOutlined, BankOutlined, MailOutlined, PhoneOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';
import { useOrgStore } from '../store/orgStore';
import { authApi } from '../api/auth';
import PasswordRequirements from '../components/PasswordRequirements';

const { Title, Paragraph } = Typography;

export default function SettingsPage() {
  const { user, fetchCurrentUser } = useAuthStore();
  const { organization, fetchOrganization, updateOrganization, deleteOrganization } = useOrgStore();
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [orgForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [isEditingOrg, setIsEditingOrg] = useState(false);

  useEffect(() => {
    fetchOrganization();
  }, []);

  useEffect(() => {
    if (user) {
      profileForm.setFieldsValue({
        full_name: user.full_name,
        email: user.email,
        position: user.position,
      });
    }
  }, [user]);

  useEffect(() => {
    if (organization) {
      orgForm.setFieldsValue({
        name: organization.name,
        email: organization.email,
        phone: organization.phone,
        billing_street: organization.billing_street,
        billing_city: organization.billing_city,
        billing_postal_code: organization.billing_postal_code,
        billing_country: organization.billing_country,
        nip: organization.nip,
      });
    }
  }, [organization]);

  const handleProfileUpdate = async (values: any) => {
    setLoading(true);
    try {
      // Note: Backend doesn't have /users/me PATCH endpoint
      // Using placeholder message
      message.info('Profile update feature coming soon - backend endpoint not fully implemented');
      await fetchCurrentUser();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (values: any) => {
    if (values.new_password !== values.confirm_password) {
      message.error('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await authApi.changePassword(values.current_password, values.new_password);
      message.success('Password changed successfully');
      passwordForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleOrgUpdate = async (values: any) => {
    setLoading(true);
    try {
      await updateOrganization(values);
      message.success('Organization updated successfully');
      setIsEditingOrg(false);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update organization');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteOrganization = () => {
    Modal.confirm({
      title: 'Delete Organization',
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p>Are you sure you want to delete this organization?</p>
          <p style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
            This action cannot be undone. All data, users, and subscriptions will be permanently deleted.
          </p>
        </div>
      ),
      okText: 'Delete',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        setLoading(true);
        try {
          await deleteOrganization();
          message.success('Organization deleted successfully');
          // Redirect to login after deletion
          window.location.href = '/login';
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Failed to delete organization');
        } finally {
          setLoading(false);
        }
      },
    });
  };

  const items = [
    {
      key: 'profile',
      label: 'Profile',
      children: (
        <Card>
          <Title level={4}>Personal Information</Title>
          <Paragraph type="secondary">Update your personal details</Paragraph>
          
          <Form
            form={profileForm}
            layout="vertical"
            onFinish={handleProfileUpdate}
            style={{ maxWidth: 600 }}
          >
            <Form.Item
              name="full_name"
              label="Full Name"
              rules={[{ required: true, message: 'Please input your full name!' }]}
            >
              <Input prefix={<UserOutlined />} />
            </Form.Item>

            <Form.Item
              name="email"
              label="Email"
              rules={[
                { required: true, message: 'Please input your email!' },
                { type: 'email', message: 'Please enter a valid email!' }
              ]}
            >
              <Input prefix={<MailOutlined />} disabled />
            </Form.Item>

            <Form.Item name="position" label="Position">
              <Input />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading}>
                Save Changes
              </Button>
            </Form.Item>
          </Form>

          <Divider />

          <Title level={4}>Change Password</Title>
          <Paragraph type="secondary">Update your password</Paragraph>
          
          <Form
            form={passwordForm}
            layout="vertical"
            onFinish={handlePasswordChange}
            style={{ maxWidth: 600 }}
          >
            <Form.Item
              name="current_password"
              label="Current Password"
              rules={[{ required: true, message: 'Please input your current password!' }]}
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <Form.Item
              name="new_password"
              label="New Password"
              rules={[
                { required: true, message: 'Please input your new password!' },
                { min: 8, message: 'Password must be at least 8 characters!' },
                {
                  pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                  message: 'Password must contain uppercase, lowercase, and number!'
                }
              ]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </Form.Item>
            
            {newPassword && <PasswordRequirements password={newPassword} />}

            <Form.Item
              name="confirm_password"
              label="Confirm New Password"
              rules={[{ required: true, message: 'Please confirm your new password!' }]}
            >
              <Input.Password prefix={<LockOutlined />} />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading}>
                Change Password
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'organization',
      label: 'Organization',
      children: (
        <Card>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <Title level={4} style={{ marginBottom: 0 }}>Organization Information</Title>
              <Paragraph type="secondary" style={{ marginBottom: 0 }}>Manage your organization details</Paragraph>
            </div>
            {!isEditingOrg && organization && (
              <Button type="primary" onClick={() => setIsEditingOrg(true)}>
                Edit
              </Button>
            )}
          </div>
          
          {!isEditingOrg && organization ? (
            <div style={{ maxWidth: 600 }}>
              <Divider orientation="left">Basic Information</Divider>
              <p><strong>Organization Name:</strong> {organization.name}</p>
              <p><strong>Email:</strong> {organization.email}</p>
              <p><strong>Phone:</strong> {organization.phone || 'Not provided'}</p>
              <p><strong>NIP (Tax ID):</strong> {organization.nip || 'Not provided'}</p>
              
              <Divider orientation="left">Billing Address</Divider>
              <p><strong>Street:</strong> {organization.billing_street || 'Not provided'}</p>
              <p><strong>City:</strong> {organization.billing_city || 'Not provided'}</p>
              <p><strong>Postal Code:</strong> {organization.billing_postal_code || 'Not provided'}</p>
              <p><strong>Country:</strong> {organization.billing_country || 'Not provided'}</p>
            </div>
          ) : (
            <Form
              form={orgForm}
              layout="vertical"
              onFinish={handleOrgUpdate}
              style={{ maxWidth: 600 }}
            >
              <Form.Item
                name="name"
                label="Organization Name"
                rules={[{ required: true, message: 'Please input organization name!' }]}
              >
                <Input prefix={<BankOutlined />} />
              </Form.Item>

              <Form.Item
                name="email"
                label="Email"
                rules={[
                  { type: 'email', message: 'Please enter a valid email!' }
                ]}
              >
                <Input prefix={<MailOutlined />} />
              </Form.Item>

              <Form.Item 
                name="phone" 
                label="Phone"
                rules={[
                  {
                    pattern: /^\+?[0-9]{9,15}$/,
                    message: 'Phone number must contain 9-15 digits (optionally starting with +)'
                  }
                ]}
              >
                <Input prefix={<PhoneOutlined />} placeholder="+48123456789" />
              </Form.Item>

              <Form.Item 
                name="nip" 
                label="NIP (Tax ID)"
                rules={[
                  {
                    pattern: /^[0-9]{10}$/,
                    message: 'NIP must be exactly 10 digits!'
                  }
                ]}
              >
                <Input placeholder="1234567890" maxLength={10} />
              </Form.Item>

              <Divider>Billing Address</Divider>

              <Form.Item
                name="billing_street"
                label="Street"
              >
                <Input placeholder="ul. Przykładowa 123" />
              </Form.Item>

              <Space style={{ display: 'flex' }}>
                <Form.Item
                  name="billing_city"
                  label="City"
                  style={{ flex: 1 }}
                >
                  <Input placeholder="Kraków" />
                </Form.Item>

                <Form.Item
                  name="billing_postal_code"
                  label="Postal Code"
                  rules={[
                    {
                      pattern: /^[0-9]{2}-[0-9]{3}$/,
                      message: 'Format: XX-XXX (e.g., 30-001)'
                    }
                  ]}
                  style={{ flex: 1 }}
                >
                  <Input placeholder="30-001" maxLength={6} />
                </Form.Item>
              </Space>

              <Form.Item
                name="billing_country"
                label="Country"
              >
                <Select
                  showSearch
                  placeholder="Select a country"
                  optionFilterProp="children"
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  options={[
                    { value: 'Polska', label: 'Polska' },
                    { value: 'Germany', label: 'Germany' },
                    { value: 'United Kingdom', label: 'United Kingdom' },
                    { value: 'France', label: 'France' },
                    { value: 'Spain', label: 'Spain' },
                    { value: 'Italy', label: 'Italy' },
                    { value: 'Netherlands', label: 'Netherlands' },
                    { value: 'Belgium', label: 'Belgium' },
                    { value: 'Austria', label: 'Austria' },
                    { value: 'Switzerland', label: 'Switzerland' },
                    { value: 'Czech Republic', label: 'Czech Republic' },
                    { value: 'Slovakia', label: 'Slovakia' },
                    { value: 'Hungary', label: 'Hungary' },
                    { value: 'Romania', label: 'Romania' },
                    { value: 'Bulgaria', label: 'Bulgaria' },
                    { value: 'United States', label: 'United States' },
                    { value: 'Canada', label: 'Canada' },
                    { value: 'Other', label: 'Other' },
                  ]}
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    Save Changes
                  </Button>
                  <Button onClick={() => {
                    setIsEditingOrg(false);
                    orgForm.setFieldsValue({
                      name: organization?.name,
                      email: organization?.email,
                      phone: organization?.phone,
                      billing_street: organization?.billing_street,
                      billing_city: organization?.billing_city,
                      billing_postal_code: organization?.billing_postal_code,
                      billing_country: organization?.billing_country,
                      nip: organization?.nip,
                    });
                  }}>
                    Cancel
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          )}

          <Divider />

          <Title level={4} style={{ color: '#ff4d4f' }}>Danger Zone</Title>
          <Paragraph type="secondary">
            Once you delete your organization, there is no going back. Please be certain.
          </Paragraph>
          <Button 
            danger 
            type="primary" 
            onClick={handleDeleteOrganization}
            loading={loading}
          >
            Delete Organization
          </Button>
        </Card>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Settings</Title>
      <Paragraph type="secondary">Manage your account and organization settings</Paragraph>
      
      <Tabs defaultActiveKey="profile" items={items} />
    </div>
  );
}
