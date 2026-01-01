import { useEffect, useState } from 'react';
import { Tabs, Card, Form, Input, Button, message, Typography, Divider, Space } from 'antd';
import { UserOutlined, LockOutlined, BankOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';
import { useOrgStore } from '../store/orgStore';
import { authApi } from '../api/auth';
import PasswordRequirements from '../components/PasswordRequirements';

const { Title, Paragraph } = Typography;

export default function SettingsPage() {
  const { user, fetchCurrentUser } = useAuthStore();
  const { organization, fetchOrganization, updateOrganization } = useOrgStore();
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [orgForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [newPassword, setNewPassword] = useState('');

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
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update organization');
    } finally {
      setLoading(false);
    }
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
          <Title level={4}>Organization Information</Title>
          <Paragraph type="secondary">Manage your organization details</Paragraph>
          
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
                { required: true, message: 'Please input email!' },
                { type: 'email', message: 'Please enter a valid email!' }
              ]}
            >
              <Input prefix={<MailOutlined />} />
            </Form.Item>

            <Form.Item name="phone" label="Phone">
              <Input prefix={<PhoneOutlined />} />
            </Form.Item>

            <Form.Item name="nip" label="NIP (Tax ID)">
              <Input />
            </Form.Item>

            <Divider>Billing Address</Divider>

            <Form.Item
              name="billing_street"
              label="Street"
              rules={[{ required: true, message: 'Please input street!' }]}
            >
              <Input />
            </Form.Item>

            <Space style={{ display: 'flex' }}>
              <Form.Item
                name="billing_city"
                label="City"
                rules={[{ required: true, message: 'Required!' }]}
                style={{ flex: 1 }}
              >
                <Input />
              </Form.Item>

              <Form.Item
                name="billing_postal_code"
                label="Postal Code"
                rules={[{ required: true, message: 'Required!' }]}
                style={{ flex: 1 }}
              >
                <Input />
              </Form.Item>
            </Space>

            <Form.Item
              name="billing_country"
              label="Country"
              rules={[{ required: true, message: 'Please input country!' }]}
            >
              <Input />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading}>
                Save Changes
              </Button>
            </Form.Item>
          </Form>
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
