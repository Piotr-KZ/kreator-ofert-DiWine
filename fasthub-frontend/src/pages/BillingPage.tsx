import { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Button, Table, Tag, Space, message, Spin, Alert, Divider } from 'antd';
import { CreditCardOutlined, DownloadOutlined, CheckCircleOutlined, CloseCircleOutlined, StarOutlined, RocketOutlined, CrownOutlined } from '@ant-design/icons';
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
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <Paragraph style={{ marginTop: 24, color: '#999' }}>Loading billing information...</Paragraph>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: 600, margin: '50px auto' }}>
        <Alert 
          message="Error Loading Billing Data" 
          description={error} 
          type="error" 
          showIcon 
          style={{ borderRadius: 8 }}
        />
      </div>
    );
  }

  const plans = [
    {
      name: 'Free',
      price: 0,
      icon: <StarOutlined style={{ fontSize: 32, color: '#1890ff' }} />,
      features: ['Up to 5 users', 'Basic features', 'Email support', 'Community access'],
      recommended: false,
    },
    {
      name: 'Pro',
      price: 99,
      icon: <RocketOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
      features: ['Up to 50 users', 'Advanced features', 'Priority support', 'API access', 'Custom branding'],
      recommended: true,
    },
    {
      name: 'Enterprise',
      price: 299,
      icon: <CrownOutlined style={{ fontSize: 32, color: '#faad14' }} />,
      features: ['Unlimited users', 'All features', '24/7 support', 'Custom integrations', 'SLA', 'Dedicated account manager'],
      recommended: false,
    },
  ];

  const invoiceColumns = [
    {
      title: 'Invoice Number',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
      render: (text: string) => <Text strong style={{ fontSize: 14 }}>{text}</Text>,
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number, record: Invoice) => (
        <Text strong style={{ fontSize: 15, color: '#1890ff' }}>
          {amount} {record.currency}
        </Text>
      ),
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
        return (
          <Tag 
            color={colors[status]}
            style={{ 
              fontSize: 13, 
              padding: '4px 12px',
              borderRadius: 6
            }}
          >
            {status.toUpperCase()}
          </Tag>
        );
      },
    },
    {
      title: 'Issue Date',
      dataIndex: 'issue_date',
      key: 'issue_date',
      render: (date: string) => (
        <Text style={{ fontSize: 14 }}>
          {new Date(date).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
          })}
        </Text>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_: any, record: Invoice) => (
        <Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={() => handleDownloadInvoice(record.id)}
        >
          Download
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px 0' }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <Title level={2} style={{ marginBottom: 8 }}>Billing & Subscription</Title>
        <Paragraph style={{ fontSize: 16, color: '#666', marginBottom: 0 }}>
          Manage your subscription plan and billing information
        </Paragraph>
      </div>

      {/* Current Subscription */}
      {subscription && (
        <Card 
          title={
            <div>
              <Title level={4} style={{ marginBottom: 4 }}>Current Subscription</Title>
              <Text type="secondary">Your active plan and billing details</Text>
            </div>
          }
          style={{ marginBottom: 32, borderRadius: 8 }}
          bodyStyle={{ padding: '32px' }}
          extra={
            subscription.status === 'active' && (
              <Button 
                danger 
                icon={<CloseCircleOutlined />}
                onClick={handleCancelSubscription}
                size="large"
              >
                Cancel Subscription
              </Button>
            )
          }
        >
          <Row gutter={[32, 24]}>
            <Col xs={24} md={8}>
              <div style={{ marginBottom: 8 }}>
                <Text type="secondary" style={{ fontSize: 13 }}>Current Plan</Text>
              </div>
              <div>
                <Tag 
                  color="blue" 
                  style={{ 
                    fontSize: 16, 
                    padding: '8px 16px',
                    borderRadius: 6
                  }}
                >
                  {subscription.plan.toUpperCase()}
                </Tag>
              </div>
            </Col>
            <Col xs={24} md={8}>
              <div style={{ marginBottom: 8 }}>
                <Text type="secondary" style={{ fontSize: 13 }}>Status</Text>
              </div>
              <div>
                <Tag 
                  color={subscription.status === 'active' ? 'green' : 'red'}
                  icon={subscription.status === 'active' ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                  style={{ 
                    fontSize: 16, 
                    padding: '8px 16px',
                    borderRadius: 6
                  }}
                >
                  {subscription.status.toUpperCase()}
                </Tag>
              </div>
            </Col>
            <Col xs={24} md={8}>
              <div style={{ marginBottom: 8 }}>
                <Text type="secondary" style={{ fontSize: 13 }}>Next Billing Date</Text>
              </div>
              <div>
                <Text strong style={{ fontSize: 16 }}>
                  {new Date(subscription.current_period_end).toLocaleDateString('en-US', { 
                    month: 'long', 
                    day: 'numeric', 
                    year: 'numeric' 
                  })}
                </Text>
              </div>
            </Col>
          </Row>
        </Card>
      )}

      {/* Pricing Plans */}
      <div style={{ marginBottom: 32 }}>
        <Title level={3} style={{ marginBottom: 8 }}>Available Plans</Title>
        <Paragraph style={{ fontSize: 15, color: '#666' }}>
          Choose the plan that best fits your needs
        </Paragraph>
      </div>

      <Row gutter={[24, 24]} style={{ marginBottom: 48 }}>
        {plans.map((plan) => {
          const isCurrentPlan = subscription?.plan.toLowerCase() === plan.name.toLowerCase();
          
          return (
            <Col key={plan.name} xs={24} md={8}>
              <Card
                style={{ 
                  borderRadius: 8,
                  height: '100%',
                  border: plan.recommended ? '2px solid #52c41a' : '1px solid #f0f0f0',
                  position: 'relative'
                }}
                bodyStyle={{ padding: '32px' }}
              >
                {plan.recommended && (
                  <div style={{
                    position: 'absolute',
                    top: -12,
                    right: 24,
                    backgroundColor: '#52c41a',
                    color: 'white',
                    padding: '4px 16px',
                    borderRadius: 12,
                    fontSize: 13,
                    fontWeight: 600
                  }}>
                    RECOMMENDED
                  </div>
                )}
                
                <div style={{ textAlign: 'center', marginBottom: 24 }}>
                  <div style={{ marginBottom: 16 }}>
                    {plan.icon}
                  </div>
                  <Title level={3} style={{ marginBottom: 4 }}>{plan.name}</Title>
                  {isCurrentPlan && (
                    <Tag color="green" icon={<CheckCircleOutlined />} style={{ marginBottom: 16 }}>
                      Current Plan
                    </Tag>
                  )}
                </div>

                <div style={{ textAlign: 'center', marginBottom: 32 }}>
                  <Title level={1} style={{ margin: 0, fontSize: 48, color: '#1890ff' }}>
                    {plan.price}
                  </Title>
                  <Text type="secondary" style={{ fontSize: 16 }}>PLN / month</Text>
                </div>

                <Divider style={{ margin: '24px 0' }} />

                <ul style={{ paddingLeft: 20, marginBottom: 32 }}>
                  {plan.features.map((feature, idx) => (
                    <li key={idx} style={{ marginBottom: 12, fontSize: 15 }}>
                      <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                      {feature}
                    </li>
                  ))}
                </ul>

                {!isCurrentPlan && (
                  <Button 
                    type={plan.recommended ? 'primary' : 'default'}
                    size="large"
                    block 
                    onClick={() => handleUpgrade(plan.name.toLowerCase())}
                    style={{ height: 48, fontSize: 16 }}
                  >
                    Upgrade to {plan.name}
                  </Button>
                )}
              </Card>
            </Col>
          );
        })}
      </Row>

      {/* Invoices */}
      <Card 
        title={
          <div>
            <Title level={4} style={{ marginBottom: 4 }}>Billing History</Title>
            <Text type="secondary">View and download your invoices</Text>
          </div>
        }
        style={{ borderRadius: 8 }}
        bodyStyle={{ padding: 0 }}
      >
        <Table
          columns={invoiceColumns}
          dataSource={invoices}
          rowKey="id"
          pagination={{ 
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} invoices`
          }}
        />
      </Card>
    </div>
  );
}
