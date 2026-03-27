import { useEffect, useState } from 'react'
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Tag,
  Button,
  Statistic,
  Progress,
  Empty,
  message,
} from 'antd'
import {
  ReloadOutlined,
  ClusterOutlined,
  DesktopOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import type { NodeInfo } from '../types'
import { getNodes } from '../api/vllm'

const { Title, Text } = Typography

const DeviceInfo = () => {
  const [nodes, setNodes] = useState<NodeInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<string>('')

  useEffect(() => {
    fetchNodes()
  }, [])

  const fetchNodes = async () => {
    setLoading(true)
    try {
      const data = await getNodes()
      setNodes(data)
      setLastUpdate(dayjs().format('HH:mm:ss'))
    } catch (error) {
      message.error('获取设备信息失败')
    } finally {
      setLoading(false)
    }
  }

  const totalGPUs = nodes.reduce((acc, node) => acc + node.gpus.length, 0)
  const totalMemory = nodes.reduce((acc, node) => acc + node.memoryTotal, 0)
  const usedMemory = nodes.reduce((acc, node) => acc + node.memoryUsed, 0)
  const onlineNodes = nodes.filter((n) => n.status === 'online').length

  const getUtilizationColor = (value: number) => {
    if (value < 50) return '#52c41a'
    if (value < 80) return '#faad14'
    return '#ff4d4f'
  }

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={4} style={{ marginBottom: 4 }}>设备信息</Title>
          <Text type="secondary">集群节点和 GPU 设备状态管理 · 最后更新: {lastUpdate}</Text>
        </div>
        <Button icon={<ReloadOutlined />} onClick={fetchNodes} loading={loading}>
          刷新
        </Button>
      </div>

      {/* 设备概览 */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={5} style={{ marginBottom: 16 }}>
          <Space>
            <ClusterOutlined />
            设备概览
          </Space>
        </Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card size="small" style={{ background: '#fafafa' }}>
              <Statistic
                title={<Text type="secondary">节点状态</Text>}
                value={onlineNodes}
                suffix={`/ ${nodes.length}`}
                valueStyle={{ fontSize: 32, fontWeight: 600, color: '#1f2937' }}
                prefix={<ClusterOutlined style={{ color: '#7c3aed', marginRight: 8 }} />}
              />
              <Text type="secondary" style={{ fontSize: 12 }}>在线节点</Text>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card size="small" style={{ background: '#fafafa' }}>
              <Statistic
                title={<Text type="secondary">GPU 设备</Text>}
                value={totalGPUs}
                valueStyle={{ fontSize: 32, fontWeight: 600, color: '#1f2937' }}
                prefix={<DesktopOutlined style={{ color: '#7c3aed', marginRight: 8 }} />}
              />
              <Text type="secondary" style={{ fontSize: 12 }}>可用 GPU</Text>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card size="small" style={{ background: '#fafafa' }}>
              <Statistic
                title={<Text type="secondary">总显存</Text>}
                value={totalMemory}
                suffix="GB"
                valueStyle={{ fontSize: 32, fontWeight: 600, color: '#1f2937' }}
                prefix={<DatabaseOutlined style={{ color: '#7c3aed', marginRight: 8 }} />}
              />
              <Text type="secondary" style={{ fontSize: 12 }}>
                已使用 {usedMemory} GB ({Math.round((usedMemory / totalMemory) * 100)}%)
              </Text>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* 节点详情 */}
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {nodes.map((node) => (
          <Card key={node.id} loading={loading}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Space>
                <ClusterOutlined style={{ color: '#7c3aed' }} />
                <Text strong style={{ fontSize: 16 }}>{node.name}</Text>
                <Text type="secondary">{node.ip}</Text>
              </Space>
              <Tag color={node.status === 'online' ? 'success' : 'error'} icon={<CheckCircleOutlined />}>
                {node.status === 'online' ? '在线' : '离线'}
              </Tag>
            </div>

            <Row gutter={[24, 24]}>
              {/* CPU 和内存 */}
              <Col span={24}>
                <Row gutter={[24, 16]}>
                  <Col xs={24} md={12}>
                    <div style={{ marginBottom: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <Text type="secondary">CPU</Text>
                        <Text strong>{node.cpu}%</Text>
                      </div>
                      <Progress
                        percent={node.cpu}
                        strokeColor={getUtilizationColor(node.cpu)}
                        showInfo={false}
                        strokeWidth={8}
                      />
                    </div>
                  </Col>
                  <Col xs={24} md={12}>
                    <div style={{ marginBottom: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <Text type="secondary">内存</Text>
                        <Text strong>{node.memoryUsed}/{node.memoryTotal} GB</Text>
                      </div>
                      <Progress
                        percent={Math.round((node.memoryUsed / node.memoryTotal) * 100)}
                        strokeColor="#7c3aed"
                        showInfo={false}
                        strokeWidth={8}
                      />
                    </div>
                  </Col>
                </Row>
              </Col>

              {/* GPU 信息 */}
              {node.gpus.map((gpu) => (
                <Col xs={24} md={12} lg={6} key={gpu.id}>
                  <Card
                    size="small"
                    style={{
                      background: '#fafafa',
                      borderLeft: `3px solid ${getUtilizationColor(gpu.utilization)}`,
                    }}
                  >
                    <div style={{ marginBottom: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text strong>GPU {gpu.index}</Text>
                        <Text strong style={{ color: getUtilizationColor(gpu.utilization) }}>
                          {gpu.utilization}%
                        </Text>
                      </div>
                      <Progress
                        percent={gpu.utilization}
                        strokeColor={getUtilizationColor(gpu.utilization)}
                        showInfo={false}
                        strokeWidth={6}
                        style={{ marginTop: 4, marginBottom: 8 }}
                      />
                    </div>
                    <Space direction="vertical" size={2} style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>显存:</Text>
                        <Text style={{ fontSize: 12 }}>{gpu.memoryUsed}/{gpu.memoryTotal}GB</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>温度:</Text>
                        <Text style={{ fontSize: 12 }}>{gpu.temperature}°C</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>功耗:</Text>
                        <Text style={{ fontSize: 12 }}>{gpu.power}W</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>型号:</Text>
                        <Text style={{ fontSize: 12 }}>{gpu.name}</Text>
                      </div>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        ))}
      </Space>

      {nodes.length === 0 && !loading && (
        <Card>
          <Empty description="暂无设备信息" />
        </Card>
      )}
    </div>
  )
}

export default DeviceInfo
