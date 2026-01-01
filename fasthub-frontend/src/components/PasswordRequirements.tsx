import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { Space, Typography } from 'antd';

const { Text } = Typography;

interface PasswordRequirementsProps {
  password: string;
}

export default function PasswordRequirements({ password }: PasswordRequirementsProps) {
  const requirements = [
    {
      label: 'At least 8 characters',
      met: password.length >= 8,
    },
    {
      label: 'Contains uppercase letter (A-Z)',
      met: /[A-Z]/.test(password),
    },
    {
      label: 'Contains lowercase letter (a-z)',
      met: /[a-z]/.test(password),
    },
    {
      label: 'Contains number (0-9)',
      met: /[0-9]/.test(password),
    },
  ];

  return (
    <Space direction="vertical" size="small" style={{ marginTop: 8 }}>
      {requirements.map((req, index) => (
        <Space key={index} size="small">
          {req.met ? (
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
          ) : (
            <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
          )}
          <Text type={req.met ? 'success' : 'secondary'} style={{ fontSize: 13 }}>
            {req.label}
          </Text>
        </Space>
      ))}
    </Space>
  );
}
