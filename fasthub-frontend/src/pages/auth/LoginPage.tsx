import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Alert, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';

const { Title, Text } = Typography;

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, error, clearError } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    clearError();
    
    try {
      await login(values.email, values.password);
      navigate('/dashboard');
    } catch (err) {
      console.error('Login failed:', err);
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
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>AutoFlow</Title>
          <Text type="secondary">Sign in to your account</Text>
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
          name="login"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
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
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password"
            />
          </Form.Item>

          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Link to="/forgot-password">
                <Text type="secondary">Forgot password?</Text>
              </Link>
            </div>
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              loading={loading}
            >
              Sign In
            </Button>
          </Form.Item>
        </Form>

        <Divider />

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            Don't have an account?{' '}
            <Link to="/register">Sign up</Link>
          </Text>
        </div>
      </Card>
    </div>
  );
}
