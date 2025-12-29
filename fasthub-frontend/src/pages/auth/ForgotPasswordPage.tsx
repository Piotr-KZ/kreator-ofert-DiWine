import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Alert, Result } from 'antd';
import { MailOutlined } from '@ant-design/icons';
import { authApi } from '../../api/auth';

const { Title, Text } = Typography;

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const onFinish = async (values: { email: string }) => {
    setLoading(true);
    setError(null);
    
    try {
      await authApi.forgotPassword(values.email);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send reset email');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}>
          <Result
            status="success"
            title="Check Your Email"
            subTitle="We've sent you a password reset link. Please check your inbox."
            extra={
              <Link to="/login">
                <Button type="primary">Back to Login</Button>
              </Link>
            }
          />
        </Card>
      </div>
    );
  }

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
          <Title level={2}>Reset Password</Title>
          <Text type="secondary">Enter your email to receive a reset link</Text>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 16 }}
          />
        )}

        <Form
          name="forgot-password"
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

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              loading={loading}
            >
              Send Reset Link
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Link to="/login">
              <Text type="secondary">Back to Login</Text>
            </Link>
          </div>
        </Form>
      </Card>
    </div>
  );
}
