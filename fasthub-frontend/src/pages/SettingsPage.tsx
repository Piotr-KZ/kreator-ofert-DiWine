import { useEffect, useState } from 'react';
import { Tabs, Card, Form, Input, Button, message, Typography, Divider, Space, Modal, Select, Row, Col, Alert } from 'antd';
import { UserOutlined, LockOutlined, BankOutlined, MailOutlined, PhoneOutlined, ExclamationCircleOutlined, EditOutlined, SaveOutlined, CloseOutlined, DeleteOutlined, HomeOutlined, GlobalOutlined } from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';
import { useOrgStore } from '../store/orgStore';
import { authApi } from '../api/auth';
import PasswordRequirements from '../components/PasswordRequirements';

const { Title, Paragraph, Text } = Typography;

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
      setNewPassword('');
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
          <Alert
            message="This action cannot be undone"
            description="All data, users, and subscriptions will be permanently deleted."
            type="error"
            showIcon
            style={{ marginTop: 16 }}
          />
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
      label: (
        <span>
          <UserOutlined /> Profile
        </span>
      ),
      children: (
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          {/* Personal Information Card */}
          <Card 
            title={
              <div>
                <Title level={4} style={{ marginBottom: 4 }}>Personal Information</Title>
                <Text type="secondary">Update your personal details and contact information</Text>
              </div>
            }
            style={{ marginBottom: 24, borderRadius: 8 }}
            bodyStyle={{ padding: '32px' }}
          >
            <Form
              form={profileForm}
              layout="vertical"
              onFinish={handleProfileUpdate}
              size="large"
            >
              <Row gutter={24}>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="full_name"
                    label="Full Name"
                    rules={[{ required: true, message: 'Please input your full name!' }]}
                  >
                    <Input prefix={<UserOutlined style={{ color: '#1890ff' }} />} placeholder="John Doe" />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="email"
                    label="Email Address"
                    rules={[
                      { required: true, message: 'Please input your email!' },
                      { type: 'email', message: 'Please enter a valid email!' }
                    ]}
                  >
                    <Input prefix={<MailOutlined style={{ color: '#1890ff' }} />} disabled />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item name="position" label="Position / Job Title">
                <Input placeholder="e.g., Software Engineer, Product Manager" />
              </Form.Item>

              <Form.Item style={{ marginBottom: 0, marginTop: 32 }}>
                <Button type="primary" htmlType="submit" loading={loading} size="large" icon={<SaveOutlined />}>
                  Save Changes
                </Button>
              </Form.Item>
            </Form>
          </Card>

          {/* Password Change Card */}
          <Card 
            title={
              <div>
                <Title level={4} style={{ marginBottom: 4 }}>Security</Title>
                <Text type="secondary">Change your password to keep your account secure</Text>
              </div>
            }
            style={{ borderRadius: 8 }}
            bodyStyle={{ padding: '32px' }}
          >
            <Form
              form={passwordForm}
              layout="vertical"
              onFinish={handlePasswordChange}
              size="large"
            >
              <Form.Item
                name="current_password"
                label="Current Password"
                rules={[{ required: true, message: 'Please input your current password!' }]}
              >
                <Input.Password prefix={<LockOutlined style={{ color: '#1890ff' }} />} placeholder="Enter current password" />
              </Form.Item>

              <Row gutter={24}>
                <Col xs={24} md={12}>
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
                      prefix={<LockOutlined style={{ color: '#1890ff' }} />} 
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Enter new password"
                    />
                  </Form.Item>
                </Col>
                <Col xs={24} md={12}>
                  <Form.Item
                    name="confirm_password"
                    label="Confirm New Password"
                    rules={[{ required: true, message: 'Please confirm your new password!' }]}
                  >
                    <Input.Password prefix={<LockOutlined style={{ color: '#1890ff' }} />} placeholder="Confirm new password" />
                  </Form.Item>
                </Col>
              </Row>
              
              {newPassword && (
                <div style={{ marginBottom: 24 }}>
                  <PasswordRequirements password={newPassword} />
                </div>
              )}

              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" htmlType="submit" loading={loading} size="large" icon={<LockOutlined />}>
                  Change Password
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </div>
      ),
    },
    {
      key: 'organization',
      label: (
        <span>
          <BankOutlined /> Organization
        </span>
      ),
      children: (
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          {/* Organization Info Card */}
          <Card 
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <Title level={4} style={{ marginBottom: 4 }}>Organization Information</Title>
                  <Text type="secondary">Manage your organization details and billing information</Text>
                </div>
                {!isEditingOrg && organization && (
                  <Button 
                    type="primary" 
                    icon={<EditOutlined />}
                    onClick={() => setIsEditingOrg(true)}
                    size="large"
                  >
                    Edit
                  </Button>
                )}
              </div>
            }
            style={{ marginBottom: 24, borderRadius: 8 }}
            bodyStyle={{ padding: '32px' }}
          >
            {!isEditingOrg && organization ? (
              <div>
                {/* Read-only view with better spacing */}
                <div style={{ marginBottom: 32 }}>
                  <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Basic Information</Text>
                  <Divider style={{ margin: '12px 0 24px 0' }} />
                  <Row gutter={[24, 24]}>
                    <Col xs={24} md={12}>
                      <div style={{ marginBottom: 20 }}>
                        <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>Organization Name</Text>
                        <Text strong style={{ fontSize: 16 }}>{organization.name}</Text>
                      </div>
                    </Col>
                    <Col xs={24} md={12}>
                      <div style={{ marginBottom: 20 }}>
                        <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>Email</Text>
                        <Text strong style={{ fontSize: 16 }}>{organization.email || <Text type="secondary">—</Text>}</Text>
                      </div>
                    </Col>
                    <Col xs={24} md={12}>
                      <div style={{ marginBottom: 20 }}>
                        <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>Phone</Text>
                        <Text strong style={{ fontSize: 16 }}>{organization.phone || <Text type="secondary">—</Text>}</Text>
                      </div>
                    </Col>
                    <Col xs={24} md={12}>
                      <div style={{ marginBottom: 20 }}>
                        <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>NIP (Tax ID)</Text>
                        <Text strong style={{ fontSize: 16 }}>{organization.nip || <Text type="secondary">—</Text>}</Text>
                      </div>
                    </Col>
                  </Row>
                </div>
                
                <div>
                  <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Billing Address</Text>
                  <Divider style={{ margin: '12px 0 24px 0' }} />
                  <Row gutter={[24, 24]}>
                    <Col xs={24}>
                      <div style={{ marginBottom: 20 }}>
                        <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>Street</Text>
                        <Text strong style={{ fontSize: 16 }}>{organization.billing_street || <Text type="secondary">—</Text>}</Text>
                      </div>
                    </Col>
                    <Col xs={24} md={8}>
                      <div style={{ marginBottom: 20 }}>
                        <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>City</Text>
                        <Text strong style={{ fontSize: 16 }}>{organization.billing_city || <Text type="secondary">—</Text>}</Text>
                      </div>
                    </Col>
                    <Col xs={24} md={8}>
                      <div style={{ marginBottom: 20 }}>
                        <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>Postal Code</Text>
                        <Text strong style={{ fontSize: 16 }}>{organization.billing_postal_code || <Text type="secondary">—</Text>}</Text>
                      </div>
                    </Col>
                    <Col xs={24} md={8}>
                      <div style={{ marginBottom: 20 }}>
                        <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>Country</Text>
                        <Text strong style={{ fontSize: 16 }}>{organization.billing_country || <Text type="secondary">—</Text>}</Text>
                      </div>
                    </Col>
                  </Row>
                </div>
              </div>
            ) : (
              <Form
                form={orgForm}
                layout="vertical"
                onFinish={handleOrgUpdate}
                size="large"
              >
                <div style={{ marginBottom: 32 }}>
                  <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Basic Information</Text>
                  <Divider style={{ margin: '12px 0 24px 0' }} />
                  <Row gutter={24}>
                    <Col xs={24} md={12}>
                      <Form.Item
                        name="name"
                        label="Organization Name"
                        rules={[{ required: true, message: 'Please input organization name!' }]}
                      >
                        <Input prefix={<BankOutlined style={{ color: '#1890ff' }} />} placeholder="Acme Corporation" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                      <Form.Item
                        name="email"
                        label="Email"
                        rules={[
                          { type: 'email', message: 'Please enter a valid email!' }
                        ]}
                      >
                        <Input prefix={<MailOutlined style={{ color: '#1890ff' }} />} placeholder="contact@company.com" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
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
                        <Input prefix={<PhoneOutlined style={{ color: '#1890ff' }} />} placeholder="+48 123 456 789" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
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
                    </Col>
                  </Row>
                </div>

                <div>
                  <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Billing Address</Text>
                  <Divider style={{ margin: '12px 0 24px 0' }} />
                  <Form.Item
                    name="billing_street"
                    label="Street"
                  >
                    <Input prefix={<HomeOutlined style={{ color: '#1890ff' }} />} placeholder="ul. Przykładowa 123" />
                  </Form.Item>

                  <Row gutter={24}>
                    <Col xs={24} md={8}>
                      <Form.Item
                        name="billing_city"
                        label="City"
                      >
                        <Input placeholder="Kraków" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={8}>
                      <Form.Item
                        name="billing_postal_code"
                        label="Postal Code"
                        rules={[
                          {
                            pattern: /^[0-9]{2}-[0-9]{3}$/,
                            message: 'Format: XX-XXX (e.g., 30-001)'
                          }
                        ]}
                      >
                        <Input placeholder="30-001" maxLength={6} />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={8}>
                      <Form.Item
                        name="billing_country"
                        label="Country"
                      >
                        <Select
                          showSearch
                          placeholder="Select a country"
                          optionFilterProp="children"
                          suffixIcon={<GlobalOutlined style={{ color: '#1890ff' }} />}
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
                    </Col>
                  </Row>
                </div>

                <Form.Item style={{ marginBottom: 0, marginTop: 32 }}>
                  <Space size="middle">
                    <Button type="primary" htmlType="submit" loading={loading} size="large" icon={<SaveOutlined />}>
                      Save Changes
                    </Button>
                    <Button size="large" icon={<CloseOutlined />} onClick={() => {
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
          </Card>

          {/* Danger Zone Card */}
          <Card 
            style={{ 
              borderRadius: 8,
              border: '1px solid #ff4d4f',
              backgroundColor: '#fff1f0'
            }}
            bodyStyle={{ padding: '32px' }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 24 }}>
              <div style={{ flex: 1 }}>
                <Title level={4} style={{ color: '#ff4d4f', marginBottom: 8 }}>
                  <ExclamationCircleOutlined /> Danger Zone
                </Title>
                <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                  Once you delete your organization, there is no going back. All data, users, and subscriptions will be permanently deleted. Please be certain.
                </Paragraph>
              </div>
              <Button 
                danger 
                type="primary" 
                size="large"
                icon={<DeleteOutlined />}
                onClick={handleDeleteOrganization}
                loading={loading}
              >
                Delete Organization
              </Button>
            </div>
          </Card>
        </div>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px 0' }}>
      <div style={{ marginBottom: 32 }}>
        <Title level={2} style={{ marginBottom: 8 }}>Settings</Title>
        <Paragraph type="secondary" style={{ fontSize: 16 }}>
          Manage your account and organization settings
        </Paragraph>
      </div>
      
      <Tabs 
        defaultActiveKey="profile" 
        items={items} 
        size="large"
        tabBarStyle={{ marginBottom: 32 }}
      />
    </div>
  );
}
