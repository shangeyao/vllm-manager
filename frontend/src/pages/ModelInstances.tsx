import { useEffect, useState } from 'react'
import {
  Card,
  Input,
  List,
  Tag,
  Typography,
  Space,
  Badge,
  Row,
  Col,
  Empty,
  message,
  Button,
  Tooltip,
  Popconfirm,
} from 'antd'
import {
  SearchOutlined,
  DesktopOutlined,
  ClockCircleOutlined,
  ContainerOutlined,
  CopyOutlined,
  BarChartOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons'
import type { ModelInstance } from '../types'
import { 
  getModelInstances, 
  startInstance, 
  stopInstance, 
  restartInstance, 
  deleteInstance 
} from '../api/vllm'

const { Title, Text } = Typography

const ModelInstances = () => {
  const [instances, setInstances] = useState<ModelInstance[]>([])
  const [selectedInstance, setSelectedInstance] = useState<ModelInstance | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [operating, setOperating] = useState<string | null>(null)

  useEffect(() => {
    fetchInstances()
  }, [])

  const fetchInstances = async () => {
    setLoading(true)
    try {
      const data = await getModelInstances()
      setInstances(data)
      if (data.length > 0 && !selectedInstance) {
        setSelectedInstance(data[0])
      }
    } catch (error) {
      message.error('获取模型实例失败')
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async (instance: ModelInstance) => {
    setOperating(instance.id)
    try {
      await startInstance(instance.id)
      message.success('实例启动中')
      await fetchInstances()
    } catch (error) {
      message.error('启动实例失败')
    } finally {
      setOperating(null)
    }
  }

  const handleStop = async (instance: ModelInstance) => {
    setOperating(instance.id)
    try {
      await stopInstance(instance.id)
      message.success('实例停止中')
      await fetchInstances()
    } catch (error) {
      message.error('停止实例失败')
    } finally {
      setOperating(null)
    }
  }

  const handleRestart = async (instance: ModelInstance) => {
    setOperating(instance.id)
    try {
      await restartInstance(instance.id)
      message.success('实例重启中')
      await fetchInstances()
    } catch (error) {
      message.error('重启实例失败')
    } finally {
      setOperating(null)
    }
  }

  const handleDelete = async (instance: ModelInstance) => {
    setOperating(instance.id)
    try {
      await deleteInstance(instance.id)
      message.success('实例已删除')
      if (selectedInstance?.id === instance.id) {
        setSelectedInstance(null)
      }
      await fetchInstances()
    } catch (error) {
      message.error('删除实例失败')
    } finally {
      setOperating(null)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return '#52c41a'
      case 'stopped':
        return '#ff4d4f'
      case 'pending':
        return '#1890ff'
      case 'updating':
        return '#faad14'
      default:
        return '#d9d9d9'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running':
        return '运行中'
      case 'stopped':
        return '已停止'
      case 'pending':
        return '创建中'
      case 'error':
        return '异常'
      case 'updating':
        return '更新中'
      default:
        return status
    }
  }

  const getTypeTag = (type: string) => {
    return (
      <Tag
        style={{
          background: '#f5f5f5',
          border: 'none',
          color: '#666',
          fontSize: 12,
        }}
      >
        {type}
      </Tag>
    )
  }

  const filteredInstances = instances.filter(
    (instance) =>
      instance.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      instance.modelName.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    message.success('已复制到剪贴板')
  }

  return (
    <div style={{ padding: 24, background: '#f5f5f5', minHeight: '100vh' }}>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginBottom: 4 }}>模型实例</Title>
        <Text type="secondary">管理已部署的模型实例</Text>
      </div>

      <Row gutter={24}>
        {/* 左侧列表 */}
        <Col xs={24} lg={7}>
          <Card
            loading={loading}
            bodyStyle={{ padding: 0 }}
            style={{ borderRadius: 8 }}
          >
            {/* 搜索框 */}
            <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
              <Input
                placeholder="搜索实例名称或模型..."
                prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ borderRadius: 4 }}
              />
            </div>

            {/* 实例列表 */}
            <List
              dataSource={filteredInstances}
              renderItem={(instance) => (
                <List.Item
                  onClick={() => setSelectedInstance(instance)}
                  style={{
                    cursor: 'pointer',
                    background: selectedInstance?.id === instance.id ? '#f3e8ff' : '#fff',
                    borderLeft: selectedInstance?.id === instance.id ? '3px solid #7c3aed' : '3px solid transparent',
                    padding: '16px',
                    borderBottom: '1px solid #f0f0f0',
                  }}
                >
                  <div style={{ width: '100%' }}>
                    {/* 实例名称和状态点 */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <Text strong style={{ fontSize: 14 }}>{instance.name}</Text>
                      <Badge
                        color={getStatusColor(instance.status)}
                        style={{ marginLeft: 8 }}
                      />
                    </div>

                    {/* 模型名称 */}
                    <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                      {instance.modelName}
                    </Text>

                    {/* 类型和状态标签 */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      {getTypeTag(instance.modelType)}
                      <Tag
                        color={instance.status === 'running' ? 'purple' : instance.status === 'error' ? 'red' : 'blue'}
                        style={{
                          margin: 0,
                          borderRadius: 12,
                          fontSize: 12,
                        }}
                      >
                        {getStatusText(instance.status)}
                      </Tag>
                    </div>

                    {/* 操作按钮 */}
                    <Space size="small">
                      {instance.status === 'stopped' && (
                        <Tooltip title="启动">
                          <Button
                            type="text"
                            size="small"
                            icon={<PlayCircleOutlined />}
                            loading={operating === instance.id}
                            onClick={(e) => {
                              e.stopPropagation()
                              handleStart(instance)
                            }}
                          />
                        </Tooltip>
                      )}
                      {instance.status === 'running' && (
                        <Tooltip title="停止">
                          <Button
                            type="text"
                            size="small"
                            icon={<PauseCircleOutlined />}
                            loading={operating === instance.id}
                            onClick={(e) => {
                              e.stopPropagation()
                              handleStop(instance)
                            }}
                          />
                        </Tooltip>
                      )}
                      <Tooltip title="重启">
                        <Button
                          type="text"
                          size="small"
                          icon={<SyncOutlined />}
                          loading={operating === instance.id}
                          onClick={(e) => {
                            e.stopPropagation()
                            handleRestart(instance)
                          }}
                        />
                      </Tooltip>
                      <Popconfirm
                        title="确认删除？"
                        description="此操作将永久删除该实例"
                        onConfirm={(e) => {
                          e?.stopPropagation()
                          handleDelete(instance)
                        }}
                        okText="确认"
                        cancelText="取消"
                      >
                        <Tooltip title="删除">
                          <Button
                            type="text"
                            size="small"
                            danger
                            icon={<DeleteOutlined />}
                            loading={operating === instance.id}
                            onClick={(e) => e.stopPropagation()}
                          />
                        </Tooltip>
                      </Popconfirm>
                    </Space>
                  </div>
                </List.Item>
              )}
              locale={{ emptyText: <Empty description="暂无实例" /> }}
              style={{ maxHeight: 'calc(100vh - 280px)', overflow: 'auto' }}
            />
          </Card>
        </Col>

        {/* 右侧详情 */}
        <Col xs={24} lg={17}>
          {selectedInstance ? (
            <Card style={{ borderRadius: 8 }}>
              {/* 头部：实例名称和操作按钮 */}
              <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <Title level={4} style={{ margin: 0 }}>{selectedInstance.name}</Title>
                    <Tooltip title="复制实例名称">
                      <Button
                        type="text"
                        icon={<CopyOutlined />}
                        size="small"
                        onClick={() => handleCopy(selectedInstance.name)}
                      />
                    </Tooltip>
                  </div>
                  <Text type="secondary">{selectedInstance.modelName}</Text>
                </div>
                <Space>
                  {selectedInstance.status === 'stopped' && (
                    <Tooltip title="启动">
                      <Button
                        icon={<PlayCircleOutlined />}
                        type="primary"
                        loading={operating === selectedInstance.id}
                        onClick={() => handleStart(selectedInstance)}
                      >
                        启动
                      </Button>
                    </Tooltip>
                  )}
                  {selectedInstance.status === 'running' && (
                    <Tooltip title="停止">
                      <Button
                        icon={<PauseCircleOutlined />}
                        danger
                        loading={operating === selectedInstance.id}
                        onClick={() => handleStop(selectedInstance)}
                      >
                        停止
                      </Button>
                    </Tooltip>
                  )}
                  <Tooltip title="重启">
                    <Button
                      icon={<SyncOutlined />}
                      loading={operating === selectedInstance.id}
                      onClick={() => handleRestart(selectedInstance)}
                    >
                      重启
                    </Button>
                  </Tooltip>
                  <Popconfirm
                    title="确认删除？"
                    description="此操作将永久删除该实例"
                    onConfirm={() => handleDelete(selectedInstance)}
                    okText="确认"
                    cancelText="取消"
                  >
                    <Tooltip title="删除">
                      <Button icon={<DeleteOutlined />} danger>
                        删除
                      </Button>
                    </Tooltip>
                  </Popconfirm>
                </Space>
              </div>

              {/* 基本信息 */}
              <div style={{ marginBottom: 32 }}>
                <Title level={5} style={{ marginBottom: 16, fontSize: 16, fontWeight: 500 }}>基本信息</Title>
                <Row gutter={[48, 24]}>
                  <Col span={12}>
                    <div style={{ marginBottom: 8 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>模型类型</Text>
                    </div>
                    <Text style={{ fontSize: 14 }}>{selectedInstance.modelType}</Text>
                  </Col>
                  <Col span={12}>
                    <div style={{ marginBottom: 8 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>模型版本</Text>
                    </div>
                    <Text style={{ fontSize: 14 }}>{selectedInstance.version || 'pytorch-none'}</Text>
                  </Col>
                  <Col span={12}>
                    <div style={{ marginBottom: 8 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>状态</Text>
                    </div>
                    <Tag
                      color="purple"
                      style={{ borderRadius: 12 }}
                    >
                      {getStatusText(selectedInstance.status)}
                    </Tag>
                  </Col>
                  <Col span={12}>
                    <div style={{ marginBottom: 8 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>创建时间</Text>
                    </div>
                    <Space>
                      <ClockCircleOutlined style={{ color: '#8c8c8c' }} />
                      <Text style={{ fontSize: 14 }}>{selectedInstance.createdAt}</Text>
                    </Space>
                  </Col>
                </Row>
              </div>

              {/* 资源分配 */}
              <div style={{ marginBottom: 32 }}>
                <Title level={5} style={{ marginBottom: 16, fontSize: 16, fontWeight: 500 }}>资源分配</Title>
                <Row gutter={[48, 24]}>
                  <Col span={12}>
                    <div style={{ marginBottom: 8 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>副本数</Text>
                    </div>
                    <Text strong style={{ fontSize: 20 }}>{selectedInstance.replicas}</Text>
                  </Col>
                  <Col span={12}>
                    <div style={{ marginBottom: 8 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>GPU</Text>
                    </div>
                    <Space>
                      {selectedInstance.gpus.map((gpu) => (
                        <Tag
                          key={gpu}
                          icon={<DesktopOutlined />}
                          color="purple"
                          style={{ borderRadius: 4 }}
                        >
                          {gpu}
                        </Tag>
                      ))}
                    </Space>
                  </Col>
                </Row>
              </div>

              {/* 副本详情 */}
              {selectedInstance.replicas_detail && selectedInstance.replicas_detail.length > 0 && (
                <div>
                  <Title level={5} style={{ marginBottom: 16, fontSize: 16, fontWeight: 500 }}>副本详情</Title>
                  <Space direction="vertical" style={{ width: '100%' }} size="middle">
                    {selectedInstance.replicas_detail.map((replica, index) => (
                      <Card
                        key={replica.id}
                        size="small"
                        style={{
                          background: '#fafafa',
                          borderRadius: 8,
                          border: '1px solid #f0f0f0',
                        }}
                        bodyStyle={{ padding: 16 }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Space size="middle">
                            <ContainerOutlined style={{ color: '#8c8c8c', fontSize: 16 }} />
                            <div>
                              <Text strong style={{ fontSize: 14, display: 'block' }}>
                                {replica.id}
                              </Text>
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                工作节点: {replica.node}
                              </Text>
                            </div>
                          </Space>
                          <Tag
                            icon={<DesktopOutlined />}
                            color="purple"
                            style={{ borderRadius: 4 }}
                          >
                            {replica.gpu}
                          </Tag>
                        </div>
                      </Card>
                    ))}
                  </Space>
                </div>
              )}
            </Card>
          ) : (
            <Card style={{ borderRadius: 8 }}>
              <Empty description="请选择实例查看详情" />
            </Card>
          )}
        </Col>
      </Row>
    </div>
  )
}

export default ModelInstances
