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
  Divider,
  Empty,
  message,
  Tabs,
} from 'antd'
import {
  SearchOutlined,
  DesktopOutlined,
  ClockCircleOutlined,
  ContainerOutlined,
  MessageOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'
import type { ModelInstance } from '../types'
import { getModelInstances } from '../api/vllm'
import ModelChatTest from '../components/ModelChatTest'

const { Title, Text } = Typography

const ModelInstances = () => {
  const [instances, setInstances] = useState<ModelInstance[]>([])
  const [selectedInstance, setSelectedInstance] = useState<ModelInstance | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return '#52c41a'
      case 'stopped':
        return '#ff4d4f'
      case 'pending':
        return '#1890ff'
      default:
        return '#faad14'
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
      default:
        return status
    }
  }

  const getTypeTag = (type: string) => {
    const colors: { [key: string]: string } = {
      LLM: 'purple',
      embedding: 'blue',
      rerank: 'cyan',
      audio: 'orange',
      image: 'green',
    }
    return <Tag color={colors[type] || 'default'}>{type}</Tag>
  }

  const filteredInstances = instances.filter(
    (instance) =>
      instance.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      instance.modelName.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginBottom: 4 }}>模型实例</Title>
        <Text type="secondary">管理已部署的模型实例</Text>
      </div>

      <Row gutter={24}>
        {/* 左侧列表 */}
        <Col xs={24} lg={8}>
          <Card
            loading={loading}
            bodyStyle={{ padding: 0 }}
          >
            <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
              <Input
                placeholder="搜索实例名称或模型..."
                prefix={<SearchOutlined />}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <List
              dataSource={filteredInstances}
              renderItem={(instance) => (
                <List.Item
                  onClick={() => setSelectedInstance(instance)}
                  style={{
                    cursor: 'pointer',
                    background: selectedInstance?.id === instance.id ? '#f3e8ff' : 'transparent',
                    borderLeft: selectedInstance?.id === instance.id ? '3px solid #7c3aed' : '3px solid transparent',
                    padding: '16px',
                  }}
                >
                  <div style={{ width: '100%' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                      <Text strong>{instance.name}</Text>
                      <Badge color={getStatusColor(instance.status)} />
                    </div>
                    <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                      {instance.modelName}
                    </Text>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      {getTypeTag(instance.modelType)}
                      <Tag
                        color={instance.status === 'running' ? 'success' : instance.status === 'error' ? 'error' : 'processing'}
                        style={{ margin: 0 }}
                      >
                        {getStatusText(instance.status)}
                      </Tag>
                    </div>
                  </div>
                </List.Item>
              )}
              locale={{ emptyText: <Empty description="暂无实例" /> }}
            />
          </Card>
        </Col>

        {/* 右侧详情 */}
        <Col xs={24} lg={16}>
          {selectedInstance ? (
            <Tabs
              defaultActiveKey="chat"
              items={[
                {
                  key: 'chat',
                  label: (
                    <Space>
                      <MessageOutlined />
                      对话测试
                    </Space>
                  ),
                  children: (
                    <div style={{ height: 'calc(100vh - 280px)', minHeight: 500 }}>
                      <ModelChatTest instance={selectedInstance} />
                    </div>
                  ),
                },
                {
                  key: 'info',
                  label: (
                    <Space>
                      <InfoCircleOutlined />
                      实例信息
                    </Space>
                  ),
                  children: (
                    <Card>
                      {/* 基本信息 */}
                      <div style={{ marginBottom: 24 }}>
                        <Title level={5} style={{ marginBottom: 16 }}>基本信息</Title>
                        <Row gutter={[24, 16]}>
                          <Col span={12}>
                            <div style={{ marginBottom: 8 }}>
                              <Text type="secondary">模型类型</Text>
                            </div>
                            <Tag color="purple">{selectedInstance.modelType}</Tag>
                          </Col>
                          <Col span={12}>
                            <div style={{ marginBottom: 8 }}>
                              <Text type="secondary">模型版本</Text>
                            </div>
                            <Text>{selectedInstance.version}</Text>
                          </Col>
                          <Col span={12}>
                            <div style={{ marginBottom: 8 }}>
                              <Text type="secondary">状态</Text>
                            </div>
                            <Tag
                              color={selectedInstance.status === 'running' ? 'success' : selectedInstance.status === 'error' ? 'error' : 'processing'}
                            >
                              {getStatusText(selectedInstance.status)}
                            </Tag>
                          </Col>
                          <Col span={12}>
                            <div style={{ marginBottom: 8 }}>
                              <Text type="secondary">创建时间</Text>
                            </div>
                            <Space>
                              <ClockCircleOutlined />
                              <Text>{selectedInstance.createdAt}</Text>
                            </Space>
                          </Col>
                        </Row>
                      </div>

                      <Divider />

                      {/* 资源分配 */}
                      <div style={{ marginBottom: 24 }}>
                        <Title level={5} style={{ marginBottom: 16 }}>资源分配</Title>
                        <Row gutter={[24, 16]}>
                          <Col span={12}>
                            <div style={{ marginBottom: 8 }}>
                              <Text type="secondary">副本数</Text>
                            </div>
                            <Text strong style={{ fontSize: 24 }}>{selectedInstance.replicas}</Text>
                          </Col>
                          <Col span={12}>
                            <div style={{ marginBottom: 8 }}>
                              <Text type="secondary">GPU</Text>
                            </div>
                            <Space>
                              {selectedInstance.gpus.map((gpu) => (
                                <Tag key={gpu} icon={<DesktopOutlined />} color="purple">
                                  {gpu}
                                </Tag>
                              ))}
                            </Space>
                          </Col>
                        </Row>
                      </div>

                      <Divider />

                      {/* 副本详情 */}
                      {selectedInstance.replicas_detail && (
                        <div>
                          <Title level={5} style={{ marginBottom: 16 }}>副本详情</Title>
                          <Space direction="vertical" style={{ width: '100%' }}>
                            {selectedInstance.replicas_detail.map((replica) => (
                              <Card
                                key={replica.id}
                                size="small"
                                style={{ background: '#fafafa' }}
                              >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <Space>
                                    <ContainerOutlined />
                                    <Text strong>{replica.id}</Text>
                                    <Text type="secondary">工作节点: {replica.node}</Text>
                                  </Space>
                                  <Tag icon={<DesktopOutlined />} color="purple">
                                    {replica.gpu}
                                  </Tag>
                                </div>
                              </Card>
                            ))}
                          </Space>
                        </div>
                      )}
                    </Card>
                  ),
                },
              ]}
            />
          ) : (
            <Card>
              <Empty description="请选择实例查看详情" />
            </Card>
          )}
        </Col>
      </Row>
    </div>
  )
}

export default ModelInstances
