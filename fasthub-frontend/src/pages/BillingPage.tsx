import { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Button, Table, Tag, Space, message, Spin, Alert } from 'antd';
import { CreditCardOutlined, DownloadOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { billingApi } from '../api/billing';
import { Subscription, Invoice } from '../types/models';

const { Title, Paragraph, Text } = Typography;

export default function BillingPage() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [subRes, invRes] = await Promise.all([
        billingApi.getSubscription(),
        billingApi.listInvoices(),
      ]);
      
      setSubscription(subRes.data);
      setInvoices(invRes.data || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load billing data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (plan: string) => {
    try {
      const { data } = await billingApi.upgrade(plan);
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        message.success('Subscription upgraded successfully');
        fetchBillingData();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to upgrade subscription');
    }
  };

  const handleCancelSubscription = async () => {
    try {
      await billingApi.cancel();
      message.success('Subscription cancelled successfully');
      fetchBillingData();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to cancel subscription');
    }
  };

  const handleDownloadInvoice = async (id: string) => {
    try {
      const { data } = await billingApi.getInvoicePdf(id);
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error: any) {
      message.error('Failed to download invoice');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return <Alert message="Error" description={error} type="error" showIcon />;
  }

  const plans = [
    {
      name: 'Free',
      price: 0,
      features: ['Up to 5 users', 'Basic features', 'Email support'],
    },
    {
      name: 'Pro',
      price: 99,
      features: ['Up to 50 users', 'Advanced features', 'Priority support', 'API access'],
    },
    {
      name: 'Enterprise',
      price: 299,
      features: ['Unlimited users', 'All features', '24/7 support', 'Custom integrations', 'SLA'],
    },
  ];

  const invoiceColumns = [
    {
      title: 'Invoice Number',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number, record: Invoice) => `${amount} ${record.currency}`,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: Record<string, string> = {
          paid: 'green',
          open: 'blue',
          draft: 'default',
          void: 'red',
        };
        return <Tag color={colors[status]}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Issue Date',
      dataIndex: 'issue_date',
      key: 'issue_date',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Invoice) => (
        <Button
          type="link"
          icon={<DownloadOutlined />}
          onClick={() => handleDownloadInvoice(record.id)}
        >
          Download
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Billing & Subscription</Title>
      <Paragraph type="secondary">Manage your subscription and billing information</Paragraph>

      {/* Current Subscription */}
      {subscription && (
        <Card 
          title="Current Subscription" 
          style={{ marginBottom: 24 }}
          extra={
            subscription.status === 'active' && (
              <Button danger onClick={handleCancelSubscription}>
                Cancel Subscription
              </Button>
            )
          }
        >
          <Row gutter={16}>
            <Col span={8}>
              <Text strong>Plan:</Text>
              <div><Tag color="blue">{subscription.plan.toUpperCase()}</Tag></div>
            </Col>
            <Col span={8}>
              <Text strong>Status:</Text>
              <div>
                <Tag color={subscription.status === 'active' ? 'green' : 'red'}>
                  {subscription.status.toUpperCase()}
                </Tag>
              </div>
            </Col>
            <Col span={8}>
              <Text strong>Next Billing:</Text>
              <div>{new Date(subscription.current_period_end).toLocaleDateString()}</div>
            </Col>
          </Row>
        </Card>
      )}

      {/* Pricing Plans */}
      <Title level={3}>Available Plans</Title>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {plans.map((plan) => (
          <Col key={plan.name} xs={24} md={8}>
            <Card
              title={plan.name}
              extra={
                subscription?.plan.toLowerCase() === plan.name.toLowerCase() ? (
                  <Tag color="green" icon={<CheckCircleOutlined />}>Current</Tag>
                ) : null
              }
            >
              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                <Title level={2} style={{ margin: 0 }}>
                  {plan.price} PLN
                </Title>
                <Text type="secondary">per month</Text>
              </div>
              <ul style={{ paddingLeft: 20 }}>
                {plan.features.map((feature, idx) => (
                  <li key={idx} style={{ marginBottom: 8 }}>{feature}</li>
                ))}
              </ul>
              {subscription?.plan.toLowerCase() !== plan.name.toLowerCase() && (
                <Button 
                  type="primary" 
                  block 
                  style={{ marginTop: 16 }}
                  onClick={() => handleUpgrade(plan.name.toLowerCase())}
                >
                  Upgrade to {plan.name}
                </Button>
              )}
            </Card>
          </Col>
        ))}
      </Row>

      {/* Invoices */}
      <Card title="Invoices">
        <Table
          columns={invoiceColumns}
          dataSource={invoices}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}
