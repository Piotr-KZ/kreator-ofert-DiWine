import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Alert, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';

const { Title, Text } = Typography;

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    clearError();
    
    try {
      const registerData = {
        email: values.email,
        password: values.password,
        full_name: values.full_name,
      };

      await register(registerData);
      navigate('/dashboard');
    } catch (err) {
      console.error('Registration failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <Card style={{ width: 450, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>Create Account</Title>
          <Text type="secondary">Sign up for FastHub in seconds</Text>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            closable
            onClose={clearError}
            style={{ marginBottom: 16 }}
          />
        )}

        <Form
          name="register"
          onFinish={onFinish}
          layout="vertical"
        >
          <Form.Item
            name="full_name"
            rules={[{ required: true, message: 'Please input your full name!' }]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="Full Name" 
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please input your email!' },
              { type: 'email', message: 'Please enter a valid email!' }
            ]}
          >
            <Input 
              prefix={<MailOutlined />} 
              placeholder="Email" 
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Please input your password!' },
              { min: 8, message: 'Password must be at least 8 characters!' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password (min. 8 characters)"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              size="large"
              loading={loading}
            >
              Create Account
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              By signing up, you agree to our Terms of Service and Privacy Policy
            </Text>
          </div>
        </Form>

        <Divider />

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            Already have an account?{' '}
            <Link to="/login">Sign in</Link>
          </Text>
        </div>
      </Card>
    </div>
  );
}
