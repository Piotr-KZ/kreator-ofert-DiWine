import { useState } from 'react';
import { Modal, Form, Input, Button, Select, message, Typography } from 'antd';
import { HomeOutlined, PhoneOutlined, BankOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;

interface OnboardingModalProps {
  visible: boolean;
  organizationId: number;
  organizationName: string;
  onComplete: () => void;
  onSkip: () => void;
}

export default function OnboardingModal({
  visible,
  organizationId,
  organizationName,
  onComplete,
  onSkip,
}: OnboardingModalProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [orgType, setOrgType] = useState<'business' | 'individual'>('business');

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      
      await axios.patch(
        `${import.meta.env.VITE_API_URL}/organizations/${organizationId}/complete`,
        {
          name: values.org_name,
          type: orgType,
          nip: values.nip || null,
          phone: values.phone || null,
          billing_street: values.billing_street,
          billing_city: values.billing_city,
          billing_postal_code: values.billing_postal_code,
          billing_country: values.billing_country,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      message.success('Organization profile completed!');
      onComplete();
    } catch (error: any) {
      console.error('Failed to complete organization:', error);
      
      // Show validation errors
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          detail.forEach((err: any) => {
            message.error(err.msg || 'Validation error');
          });
        } else {
          message.error(detail);
        }
      } else {
        message.error('Failed to complete organization profile');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      open={visible}
      title={null}
      footer={null}
      closable={false}
      width={600}
      maskClosable={false}
    >
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Title level={3}>Complete Your Organization Profile</Title>
        <Text type="secondary">
          Add your organization details to unlock all features
        </Text>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          org_name: organizationName,
          billing_country: 'Poland',
        }}
      >
        <Form.Item
          label="Organization Name"
          name="org_name"
          rules={[
            { required: true, message: 'Please input organization name!' },
            { min: 1, max: 255, message: 'Name must be 1-255 characters' },
          ]}
        >
          <Input placeholder="Your Company Name" />
        </Form.Item>

        <Form.Item label="Organization Type">
          <Select value={orgType} onChange={setOrgType}>
            <Option value="business">Business</Option>
            <Option value="individual">Individual</Option>
          </Select>
        </Form.Item>

        {orgType === 'business' && (
          <Form.Item
            label="NIP (Tax ID)"
            name="nip"
            rules={[
              {
                pattern: /^\d{10}$|^\d{3}-\d{3}-\d{2}-\d{2}$|^\d{3}-?\d{2}-?\d{2}-?\d{3}$/,
                message: 'NIP must be 10 digits (e.g., 1234567890 or 123-456-78-90)',
              },
            ]}
          >
            <Input
              prefix={<BankOutlined />}
              placeholder="1234567890 or 123-456-78-90"
              maxLength={13}
            />
          </Form.Item>
        )}

        <Form.Item
          label="Phone"
          name="phone"
          rules={[
            {
              pattern: /^[\d\s\-\+\(\)]{9,20}$/,
              message: 'Phone must be 9-15 digits (e.g., +48 123 456 789)',
            },
          ]}
        >
          <Input
            prefix={<PhoneOutlined />}
            placeholder="+48 123 456 789"
            maxLength={20}
          />
        </Form.Item>

        <Title level={5} style={{ marginTop: 16 }}>
          Billing Address
        </Title>

        <Form.Item
          label="Street Address"
          name="billing_street"
          rules={[
            { required: true, message: 'Please input street address!' },
            { min: 1, max: 255, message: 'Address must be 1-255 characters' },
          ]}
        >
          <Input prefix={<HomeOutlined />} placeholder="ul. Przykładowa 123" />
        </Form.Item>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <Form.Item
            label="City"
            name="billing_city"
            rules={[
              { required: true, message: 'Required!' },
              { min: 1, max: 100, message: 'City must be 1-100 characters' },
            ]}
          >
            <Input placeholder="Warsaw" />
          </Form.Item>

          <Form.Item
            label="Postal Code"
            name="billing_postal_code"
            rules={[
              { required: true, message: 'Required!' },
              {
                pattern: /^\d{2}-?\d{3}$/,
                message: 'Postal code must be 5 digits (e.g., 00-001 or 00001)',
              },
            ]}
          >
            <Input placeholder="00-001" maxLength={6} />
          </Form.Item>
        </div>

        <Form.Item
          label="Country"
          name="billing_country"
          rules={[
            { required: true, message: 'Please input country!' },
            { min: 1, max: 100, message: 'Country must be 1-100 characters' },
          ]}
        >
          <Input placeholder="Poland" />
        </Form.Item>

        <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
          <Button onClick={onSkip} block>
            Skip for now
          </Button>
          <Button type="primary" htmlType="submit" block loading={loading}>
            Complete Profile
          </Button>
        </div>

        <div style={{ textAlign: 'center', marginTop: 12 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            You can complete this later in Settings
          </Text>
        </div>
      </Form>
    </Modal>
  );
}
