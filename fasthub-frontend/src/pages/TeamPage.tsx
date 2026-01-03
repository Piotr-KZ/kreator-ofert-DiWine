import { useEffect, useState } from 'react';
import { Table, Button, Space, Typography, Modal, Form, Input, Select, message, Tag, Card, Popconfirm, Dropdown } from 'antd';
import { UserAddOutlined, MoreOutlined, DeleteOutlined, EditOutlined, CrownOutlined } from '@ant-design/icons';
import { membersApi } from '../api/members';
import { MemberWithUser, MemberRole } from '../types/models';
import { useOrgStore } from '../store/orgStore';
import { useAuthStore } from '../store/authStore';

const { Title, Paragraph } = Typography;
const { Option } = Select;

interface TeamMemberDisplay {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: MemberRole;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  last_login_at?: string;
  joined_at: string;
}

export default function TeamPage() {
  const [members, setMembers] = useState<TeamMemberDisplay[]>([]);
  const [loading, setLoading] = useState(false);
  const [inviteModalVisible, setInviteModalVisible] = useState(false);
  const [changeRoleModalVisible, setChangeRoleModalVisible] = useState(false);
  const [selectedMember, setSelectedMember] = useState<TeamMemberDisplay | null>(null);
  const [form] = Form.useForm();
  const [roleForm] = Form.useForm();
  
  const { organization, fetchOrganization } = useOrgStore();
  const currentUser = useAuthStore(state => state.user);

  useEffect(() => {
    fetchOrganization();
  }, []);

  useEffect(() => {
    if (organization) {
      fetchTeamMembers();
    }
  }, [organization]);

  const fetchTeamMembers = async () => {
    if (!organization) return;
    
    setLoading(true);
    try {
      const { data } = await membersApi.list(organization.id);
      
      // Transform MemberWithUser[] to TeamMemberDisplay[]
      const displayMembers: TeamMemberDisplay[] = data.members.map((member: MemberWithUser) => ({
        id: member.id,
        user_id: member.user_id,
        email: member.user.email,
        full_name: member.user.full_name,
        role: member.role,
        is_active: member.user.is_active,
        is_verified: member.user.is_verified,
        is_superuser: member.user.is_superuser,
        last_login_at: member.user.last_login_at,
        joined_at: member.joined_at,
      }));
      
      setMembers(displayMembers);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to fetch team members';
      console.error('TeamPage error:', errorMsg);
      if (error.response?.status !== 403) {
        message.error(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };



  const handleInviteSubmit = async (values: any) => {
    if (!organization) return;
    
    try {
      await membersApi.invite(organization.id, {
        email: values.email,
        role: values.role,
      });
      
      message.success('Invitation sent successfully!');
      setInviteModalVisible(false);
      form.resetFields();
      fetchTeamMembers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to send invitation');
    }
  };

  const handleRemoveMember = async (member: TeamMemberDisplay) => {
    if (!organization) return;
    
    try {
      await membersApi.remove(organization.id, member.user_id);
      message.success('Member removed successfully!');
      fetchTeamMembers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to remove member');
    }
  };

  const handleChangeRole = async (values: any) => {
    if (!organization || !selectedMember) return;
    
    try {
      await membersApi.changeRole(organization.id, selectedMember.user_id, {
        role: values.role,
      });
      
      message.success('Role changed successfully!');
      setChangeRoleModalVisible(false);
      roleForm.resetFields();
      setSelectedMember(null);
      fetchTeamMembers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to change role');
    }
  };

  const openChangeRoleModal = (member: TeamMemberDisplay) => {
    setSelectedMember(member);
    roleForm.setFieldsValue({ role: member.role });
    setChangeRoleModalVisible(true);
  };

  const isOwner = (member: TeamMemberDisplay) => {
    return organization?.owner_id === member.user_id;
  };

  const canManageMembers = () => {
    if (!currentUser || !organization) return false;
    
    // Super admins can manage all
    if (currentUser.is_superuser) return true;
    
    // Organization owners can manage all
    if (organization.owner_id === currentUser.id) return true;
    
    // Check if current user is admin in this organization
    const currentMember = members.find(m => m.user_id === currentUser.id);
    return currentMember?.role === 'admin';
  };



  const columns = [
    {
      title: 'Member',
      dataIndex: 'full_name',
      key: 'full_name',
      sorter: (a: TeamMemberDisplay, b: TeamMemberDisplay) => 
        (a.full_name || '').localeCompare(b.full_name || ''),
      render: (text: string, record: TeamMemberDisplay) => (
        <div>
          <div>
            <strong>{text || 'N/A'}</strong>
            {isOwner(record) && (
              <Tag color="gold" icon={<CrownOutlined />} style={{ marginLeft: 8 }}>
                Owner
              </Tag>
            )}
            {record.is_superuser && (
              <Tag color="red" style={{ marginLeft: 8 }}>
                Super Admin
              </Tag>
            )}
          </div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.email}</div>
        </div>
      ),
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      sorter: (a: TeamMemberDisplay, b: TeamMemberDisplay) => 
        a.role.localeCompare(b.role),
      render: (role: MemberRole) => {
        const colors: Record<MemberRole, string> = {
          admin: 'orange',
          viewer: 'green',
        };
        return <Tag color={colors[role]}>{role.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Joined',
      dataIndex: 'joined_at',
      key: 'joined_at',
      sorter: (a: TeamMemberDisplay, b: TeamMemberDisplay) => 
        new Date(a.joined_at).getTime() - new Date(b.joined_at).getTime(),
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Last Login',
      dataIndex: 'last_login_at',
      key: 'last_login_at',
      sorter: (a: TeamMemberDisplay, b: TeamMemberDisplay) => {
        if (!a.last_login_at) return 1;
        if (!b.last_login_at) return -1;
        return new Date(a.last_login_at).getTime() - new Date(b.last_login_at).getTime();
      },
      render: (date: string) => date ? new Date(date).toLocaleDateString() : 'Never',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: TeamMemberDisplay) => {
        // Cannot manage owner
        if (isOwner(record)) {
          return <span style={{ color: '#999' }}>-</span>;
        }

        // Only admins/owners can manage members
        if (!canManageMembers()) {
          return <span style={{ color: '#999' }}>-</span>;
        }

        const menuItems = [
          {
            key: 'change-role',
            icon: <EditOutlined />,
            label: 'Change Role',
            onClick: () => openChangeRoleModal(record),
          },
          {
            key: 'remove',
            icon: <DeleteOutlined />,
            label: 'Remove Member',
            danger: true,
            onClick: () => {
              Modal.confirm({
                title: 'Remove Member',
                content: `Are you sure you want to remove ${record.full_name} from the organization?`,
                okText: 'Remove',
                okType: 'danger',
                onOk: () => handleRemoveMember(record),
              });
            },
          },
        ];

        return (
          <Dropdown menu={{ items: menuItems }} trigger={['click']}>
            <Button type="text" icon={<MoreOutlined />} />
          </Dropdown>
        );
      },
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>Team</Title>
          <Paragraph type="secondary">
            Manage your team members and their roles
            {organization && ` in ${organization.name}`}
          </Paragraph>
        </div>
        {canManageMembers() && (
          <Button 
            type="primary" 
            icon={<UserAddOutlined />}
            onClick={() => setInviteModalVisible(true)}
          >
            Invite Member
          </Button>
        )}
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={members}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Invite Modal */}
      <Modal
        title="Invite Team Member"
        open={inviteModalVisible}
        onCancel={() => {
          setInviteModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Send Invitation"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleInviteSubmit}
        >
          <Form.Item
            name="email"
            label="Email Address"
            rules={[
              { required: true, message: 'Please input email address!' },
              { type: 'email', message: 'Please enter a valid email address!' }
            ]}
            help="Enter the email address of the person you want to invite"
          >
            <Input 
              placeholder="user@example.com"
              type="email"
            />
          </Form.Item>

          <Form.Item
            name="role"
            label="Role"
            rules={[{ required: true, message: 'Please select role!' }]}
            initialValue="viewer"
          >
            <Select>
              <Option value="viewer">Viewer - Can view only</Option>
              <Option value="admin">Admin - Can manage members and organization</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Change Role Modal */}
      <Modal
        title="Change Member Role"
        open={changeRoleModalVisible}
        onCancel={() => {
          setChangeRoleModalVisible(false);
          roleForm.resetFields();
          setSelectedMember(null);
        }}
        onOk={() => roleForm.submit()}
        okText="Change Role"
      >
        <Form
          form={roleForm}
          layout="vertical"
          onFinish={handleChangeRole}
        >
          <Paragraph>
            Change role for <strong>{selectedMember?.full_name}</strong>
          </Paragraph>
          
          <Form.Item
            name="role"
            label="New Role"
            rules={[{ required: true, message: 'Please select role!' }]}
          >
            <Select>
              <Option value="viewer">Viewer - Can view only</Option>
              <Option value="admin">Admin - Can manage members and organization</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
