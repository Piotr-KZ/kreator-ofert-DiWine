import { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Alert, Result } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { authApi } from '../../api/auth';

const { Title, Text } = Typography;

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!token) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Card style={{ width: 400 }}>
          <Result
            status="error"
            title="Invalid Reset Link"
            subTitle="This password reset link is invalid or has expired."
            extra={
              <Link to="/forgot-password">
                <Button type="primary">Request New Link</Button>
              </Link>
            }
          />
        </Card>
      </div>
    );
  }

  const onFinish = async (values: { password: string; confirmPassword: string }) => {
    if (values.password !== values.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      await authApi.resetPassword(token, values.password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password');
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
        <Card style={{ width: 400 }}>
          <Result
            status="success"
            title="Password Reset Successful"
            subTitle="Redirecting to login..."
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
          <Title level={2}>Set New Password</Title>
          <Text type="secondary">Enter your new password</Text>
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
          name="reset-password"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Please input your new password!' },
              { min: 8, message: 'Password must be at least 8 characters!' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="New Password"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            rules={[
              { required: true, message: 'Please confirm your password!' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Confirm Password"
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              loading={loading}
            >
              Reset Password
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
