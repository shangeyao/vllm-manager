import { useState, useEffect } from 'react'
import {
  Card,
  Tabs,
  Table,
  Button,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Descriptions,
  Progress,
  Statistic,
  Row,
  Col,
  Typography,
  List,
  Badge,
  Alert
} from 'antd'
import {
  UserOutlined,
  SafetyOutlined,
  KeyOutlined,
  FileTextOutlined,
  DashboardOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  ReloadOutlined
} from '@ant-design/icons'
import {
  getSystemOverview,
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  getRoles,
  createRole,
  updateRole,
  deleteRole,
  getApiKeys,
  createApiKey,
  revokeApiKey,
  getSystemLogs
} from '../api/system'

const { Title, Text } = Typography
const { TabPane } = Tabs
const { Option } = Select

// 系统概览组件
const SystemOverview = () => {
  const [overview, setOverview] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const fetchOverview = async () => {
    setLoading(true)
    try {
      const res = await getSystemOverview()
      setOverview(res.data)
    } catch (error) {
      message.error('获取系统概览失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOverview()
  }, [])

  if (!overview) return null

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="系统版本"
              value={overview.version}
              prefix={<DashboardOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="运行时间"
              value={overview.uptime}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="活跃模型"
              value={overview.active_models}
              suffix="个"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="总请求数"
              value={overview.total_requests}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="资源使用情况" loading={loading}>
            <div style={{ marginBottom: 16 }}>
              <Text>CPU 使用率</Text>
              <Progress percent={overview.cpu_usage} status="active" />
            </div>
            <div style={{ marginBottom: 16 }}>
              <Text>内存使用率</Text>
              <Progress percent={overview.memory_usage} status="active" />
            </div>
            <div>
              <Text>存储使用率</Text>
              <Progress
                percent={Math.round((overview.storage_used / overview.storage_total) * 100)}
                status="active"
              />
              <Text type="secondary">
                {overview.storage_used.toFixed(1)} GB / {overview.storage_total.toFixed(1)} GB
              </Text>
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="数据库状态" loading={loading}>
            <Descriptions column={1}>
              <Descriptions.Item label="连接状态">
                <Badge status="success" text={overview.database_status} />
              </Descriptions.Item>
              <Descriptions.Item label="存储使用">
                {overview.storage_used.toFixed(2)} GB
              </Descriptions.Item>
              <Descriptions.Item label="总存储">
                {overview.storage_total.toFixed(2)} GB
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

// 用户管理组件
const UserManagement = () => {
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<any>(null)
  const [form] = Form.useForm()

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const res = await getUsers()
      setUsers(res.data)
    } catch (error) {
      message.error('获取用户列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleCreate = async (values: any) => {
    try {
      await createUser(values)
      message.success('用户创建成功')
      setModalVisible(false)
      form.resetFields()
      fetchUsers()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败')
    }
  }

  const handleUpdate = async (values: any) => {
    try {
      await updateUser(editingUser.id, values)
      message.success('用户更新成功')
      setModalVisible(false)
      setEditingUser(null)
      form.resetFields()
      fetchUsers()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败')
    }
  }

  const handleDelete = async (userId: string) => {
    try {
      await deleteUser(userId)
      message.success('用户删除成功')
      fetchUsers()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Tag color={role === 'admin' ? 'red' : role === 'user' ? 'blue' : 'green'}>
          {role === 'admin' ? '管理员' : role === 'user' ? '用户' : '访客'}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Badge status={status === 'active' ? 'success' : 'error'} text={status === 'active' ? '正常' : '禁用'} />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingUser(record)
              form.setFieldsValue(record)
              setModalVisible(true)
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除该用户吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingUser(null)
            form.resetFields()
            setModalVisible(true)
          }}
        >
          新增用户
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={users}
        loading={loading}
        rowKey="id"
      />

      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setModalVisible(false)
          setEditingUser(null)
          form.resetFields()
        }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={editingUser ? handleUpdate : handleCreate}
        >
          <Form.Item
            name="username"
            label="用户名"
            rules={[{ required: !editingUser, message: '请输入用户名' }]}
          >
            <Input disabled={!!editingUser} />
          </Form.Item>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: !editingUser, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input />
          </Form.Item>
          {!editingUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password />
            </Form.Item>
          )}
          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select>
              <Option value="admin">管理员</Option>
              <Option value="user">用户</Option>
              <Option value="viewer">访客</Option>
            </Select>
          </Form.Item>
          {editingUser && (
            <Form.Item name="status" label="状态">
              <Select>
                <Option value="active">正常</Option>
                <Option value="disabled">禁用</Option>
              </Select>
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  )
}

// 角色管理组件
const RoleManagement = () => {
  const [roles, setRoles] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRole, setEditingRole] = useState<any>(null)
  const [form] = Form.useForm()

  const availablePermissions = [
    'models:read',
    'models:write',
    'models:deploy',
    'users:read',
    'users:write',
    'roles:read',
    'roles:write',
    'keys:read',
    'keys:write',
    'system:read',
    'system:write',
  ]

  const fetchRoles = async () => {
    setLoading(true)
    try {
      const res = await getRoles()
      setRoles(res.data)
    } catch (error) {
      message.error('获取角色列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRoles()
  }, [])

  const handleCreate = async (values: any) => {
    try {
      await createRole(values)
      message.success('角色创建成功')
      setModalVisible(false)
      form.resetFields()
      fetchRoles()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败')
    }
  }

  const handleUpdate = async (values: any) => {
    try {
      await updateRole(editingRole.id, values)
      message.success('角色更新成功')
      setModalVisible(false)
      setEditingRole(null)
      form.resetFields()
      fetchRoles()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败')
    }
  }

  const handleDelete = async (roleId: string) => {
    try {
      await deleteRole(roleId)
      message.success('角色删除成功')
      fetchRoles()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const columns = [
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '权限',
      dataIndex: 'permissions',
      key: 'permissions',
      render: (permissions: string[]) => (
        <Space wrap>
          {permissions?.map((perm) => (
            <Tag key={perm}>{perm}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingRole(record)
              form.setFieldsValue(record)
              setModalVisible(true)
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除该角色吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingRole(null)
            form.resetFields()
            setModalVisible(true)
          }}
        >
          新增角色
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={roles}
        loading={loading}
        rowKey="id"
      />

      <Modal
        title={editingRole ? '编辑角色' : '新增角色'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setModalVisible(false)
          setEditingRole(null)
          form.resetFields()
        }}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={editingRole ? handleUpdate : handleCreate}
        >
          <Form.Item
            name="name"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input disabled={!!editingRole} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="permissions" label="权限">
            <Select mode="multiple" placeholder="选择权限">
              {availablePermissions.map((perm) => (
                <Option key={perm} value={perm}>{perm}</Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

// API Key 管理组件
const ApiKeyManagement = () => {
  const [keys, setKeys] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [newKey, setNewKey] = useState<string | null>(null)
  const [form] = Form.useForm()

  const availablePermissions = [
    'models:read',
    'models:write',
    'chat:write',
    'completions:write',
    'embeddings:write',
  ]

  const fetchKeys = async () => {
    setLoading(true)
    try {
      const res = await getApiKeys()
      setKeys(res.data)
    } catch (error) {
      message.error('获取 API Key 列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchKeys()
  }, [])

  const handleCreate = async (values: any) => {
    try {
      const res = await createApiKey(values)
      setNewKey(res.data.key)
      message.success('API Key 创建成功')
      fetchKeys()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败')
    }
  }

  const handleRevoke = async (keyId: string) => {
    try {
      await revokeApiKey(keyId)
      message.success('API Key 已撤销')
      fetchKeys()
    } catch (error) {
      message.error('撤销失败')
    }
  }

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Key',
      dataIndex: 'key',
      key: 'key',
      render: (key: string) => (
        <Text copyable={{ text: key, onCopy: () => message.success('已复制') }}>
          {key ? `${key.substring(0, 20)}...` : '***'}
        </Text>
      ),
    },
    {
      title: '权限',
      dataIndex: 'permissions',
      key: 'permissions',
      render: (permissions: string[]) => (
        <Space wrap>
          {permissions?.map((perm) => (
            <Tag key={perm}>{perm}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Badge status={status === 'active' ? 'success' : 'error'} text={status === 'active' ? '正常' : '已撤销'} />
      ),
    },
    {
      title: '最后使用',
      dataIndex: 'last_used_at',
      key: 'last_used_at',
      render: (date: string) => date ? new Date(date).toLocaleString() : '从未使用',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          {record.status === 'active' && (
            <Popconfirm
              title="确定要撤销该 API Key 吗？"
              onConfirm={() => handleRevoke(record.id)}
            >
              <Button type="link" danger icon={<DeleteOutlined />}>
                撤销
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setNewKey(null)
            form.resetFields()
            setModalVisible(true)
          }}
        >
          创建 API Key
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={keys}
        loading={loading}
        rowKey="id"
      />

      <Modal
        title="创建 API Key"
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setModalVisible(false)
          setNewKey(null)
          form.resetFields()
        }}
        footer={newKey ? [
          <Button key="close" onClick={() => {
            setModalVisible(false)
            setNewKey(null)
            form.resetFields()
          }}>
            关闭
          </Button>
        ] : undefined}
      >
        {newKey ? (
          <Alert
            message="API Key 创建成功"
            description={
              <div>
                <Text>请立即复制并保存您的 API Key，它只会显示一次：</Text>
                <div style={{ marginTop: 8, padding: 8, background: '#f5f5f5', borderRadius: 4 }}>
                  <Text code copyable={{ text: newKey }}>{newKey}</Text>
                </div>
              </div>
            }
            type="success"
            showIcon
          />
        ) : (
          <Form
            form={form}
            layout="vertical"
            onFinish={handleCreate}
          >
            <Form.Item
              name="name"
              label="名称"
              rules={[{ required: true, message: '请输入名称' }]}
            >
              <Input placeholder="例如：生产环境密钥" />
            </Form.Item>
            <Form.Item name="permissions" label="权限">
              <Select mode="multiple" placeholder="选择权限">
                {availablePermissions.map((perm) => (
                  <Option key={perm} value={perm}>{perm}</Option>
                ))}
              </Select>
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  )
}

// 系统日志组件
const SystemLogs = () => {
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const res = await getSystemLogs({ limit: 100 })
      setLogs(res.data.logs)
    } catch (error) {
      message.error('获取系统日志失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [])

  return (
    <Card
      title="系统日志"
      extra={
        <Button icon={<ReloadOutlined />} onClick={fetchLogs}>
          刷新
        </Button>
      }
    >
      <List
        loading={loading}
        dataSource={logs}
        renderItem={(log) => (
          <List.Item>
            <div style={{ width: '100%' }}>
              <Space>
                <Tag color={log.level === 'ERROR' ? 'red' : log.level === 'WARN' ? 'orange' : 'blue'}>
                  {log.level}
                </Tag>
                <Text type="secondary">{new Date(log.timestamp).toLocaleString()}</Text>
                <Text>{log.message}</Text>
              </Space>
            </div>
          </List.Item>
        )}
      />
    </Card>
  )
}

// 主组件
const SystemManagement = () => {
  return (
    <div>
      <Title level={2}>系统管理</Title>
      <Tabs defaultActiveKey="overview" type="card">
        <TabPane
          tab={<span><DashboardOutlined />系统概览</span>}
          key="overview"
        >
          <SystemOverview />
        </TabPane>
        <TabPane
          tab={<span><UserOutlined />用户管理</span>}
          key="users"
        >
          <UserManagement />
        </TabPane>
        <TabPane
          tab={<span><SafetyOutlined />角色管理</span>}
          key="roles"
        >
          <RoleManagement />
        </TabPane>
        <TabPane
          tab={<span><KeyOutlined />密钥管理</span>}
          key="keys"
        >
          <ApiKeyManagement />
        </TabPane>
        <TabPane
          tab={<span><FileTextOutlined />系统日志</span>}
          key="logs"
        >
          <SystemLogs />
        </TabPane>
      </Tabs>
    </div>
  )
}

export default SystemManagement
