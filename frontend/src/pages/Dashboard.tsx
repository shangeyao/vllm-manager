import { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Typography, Space, Tag, Divider, message, Button } from 'antd'
import {
  ClusterOutlined,
  DesktopOutlined,
  DatabaseOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import dayjs from 'dayjs'
import type { ClusterOverview, ModelInstance, NodeInfo, UsageStats, TokenTrend, CallDistribution } from '../types'
import {
  getClusterOverview,
  getModelInstances,
  getNodes,
  getDashboardStats,
} from '../api/vllm'

const { Title, Text } = Typography

const Dashboard = () => {
  const [overview, setOverview] = useState<ClusterOverview | null>(null)
  const [instances, setInstances] = useState<ModelInstance[]>([])
  const [, setNodes] = useState<NodeInfo[]>([])
  const [usageStats, setUsageStats] = useState<UsageStats[]>([])
  const [callDistribution, setCallDistribution] = useState<CallDistribution[]>([])
  const [tokenTrend, setTokenTrend] = useState<TokenTrend[]>([])
  const [lastUpdate, setLastUpdate] = useState<string>('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchData()
    // 每30秒自动刷新
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [overviewData, instancesData, nodesData, dashboardStats] = await Promise.all([
        getClusterOverview(),
        getModelInstances(),
        getNodes(),
        getDashboardStats(),
      ])
      setOverview(overviewData)
      setInstances(instancesData)
      setNodes(nodesData)
      setUsageStats(dashboardStats.usageStats)
      setCallDistribution(dashboardStats.callDistribution)
      setTokenTrend(dashboardStats.tokenTrend)
      setLastUpdate(dayjs().format('HH:mm:ss'))
    } catch (error) {
      message.error('获取数据失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  // 计算统计数据
  const runningInstances = instances.filter(i => i.status === 'running')

  const getUsageChartOption = () => ({
    grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'value', show: false },
    yAxis: {
      type: 'category',
      data: usageStats.map(s => s.modelName).reverse(),
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: usageStats.map(s => s.usage).reverse(),
      itemStyle: {
        color: (params: any) => {
          const colors = ['#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe']
          return colors[params.dataIndex] || '#7c3aed'
        },
        borderRadius: [0, 4, 4, 0],
      },
      barWidth: 20,
    }],
  })

  const getPieChartOption = () => ({
    color: ['#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd', '#e9d5ff'],
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2,
      },
      label: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold',
        },
      },
      data: callDistribution,
    }],
  })

  const getLineChartOption = () => ({
    color: ['#7c3aed'],
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: tokenTrend.map(t => t.date),
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      axisLabel: { color: '#6b7280' },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
      axisLabel: { color: '#6b7280' },
    },
    series: [{
      type: 'line',
      smooth: true,
      data: tokenTrend.map(t => t.models ? Object.values(t.models).reduce((a, b) => (a as number) + (b as number), 0) : 0),
      showSymbol: false,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(124, 58, 237, 0.3)' },
            { offset: 1, color: 'rgba(124, 58, 237, 0.05)' },
          ],
        },
      },
    }],
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return <span className="status-badge status-running">运行中</span>
      case 'stopped':
        return <span className="status-badge status-stopped">已停止</span>
      case 'error':
        return <span className="status-badge status-stopped">异常</span>
      default:
        return <span className="status-badge status-pending">启动中</span>
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={4} style={{ marginBottom: 4 }}>工作台</Title>
          <Text type="secondary">集群资源和模型部署概览 · 最后更新: {lastUpdate}</Text>
        </div>
        <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>
          刷新
        </Button>
      </div>

      <Row gutter={[24, 24]}>
        {/* 集群概览 */}
        <Col xs={24} lg={12}>
          <Card
            title={<Space><ClusterOutlined /> 集群概览</Space>}
            extra={<Tag color="warning">{overview?.nodes.online || 0}/{overview?.nodes.total || 0} 节点在线</Tag>}
            className="stat-card"
            loading={loading}
          >
            <Row gutter={[24, 24]}>
              <Col span={12}>
                <Statistic
                  title={<Text type="secondary">节点在线</Text>}
                  value={overview?.nodes.online || 0}
                  suffix={`/ ${overview?.nodes.total || 0}`}
                  valueStyle={{ fontSize: 32, fontWeight: 600, color: '#1f2937' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title={<Text type="secondary">GPU 设备</Text>}
                  value={overview?.gpus.available || 0}
                  suffix={`/ ${overview?.gpus.total || 0}`}
                  valueStyle={{ fontSize: 32, fontWeight: 600, color: '#1f2937' }}
                />
              </Col>
              <Col span={24}>
                <div style={{ marginTop: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text type="secondary"><DesktopOutlined style={{ marginRight: 8 }} />GPU 平均使用率</Text>
                    <Text strong>{overview?.avgUtilization || 0}%</Text>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${overview?.avgUtilization || 0}%`,
                        background: 'linear-gradient(90deg, #7c3aed 0%, #a855f7 100%)',
                      }}
                    />
                  </div>
                </div>
              </Col>
              <Col span={24}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text type="secondary"><DatabaseOutlined style={{ marginRight: 8 }} />显存使用</Text>
                    <Text strong>{Math.round(overview?.memory.used || 0)} / {Math.round(overview?.memory.total || 0)} GB</Text>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${((overview?.memory.used || 0) / (overview?.memory.total || 1)) * 100}%`,
                        background: 'linear-gradient(90deg, #7c3aed 0%, #a855f7 100%)',
                      }}
                    />
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>

        {/* 模型部署 */}
        <Col xs={24} lg={12}>
          <Card
            title={<Space><ReloadOutlined /> 模型部署</Space>}
            extra={<Text type="secondary">{runningInstances.length} 运行中</Text>}
            className="stat-card"
            loading={loading}
          >
            <div style={{ maxHeight: 280, overflow: 'auto' }}>
              {runningInstances.length > 0 ? runningInstances.map((instance) => (
                <div key={instance.id} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <Text strong>{instance.name}</Text>
                    {getStatusBadge(instance.status)}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <DesktopOutlined style={{ color: '#6b7280', fontSize: 12 }} />
                    <Text type="secondary" style={{ fontSize: 12 }}>{'local'}</Text>
                    {instance.gpus?.map((gpu: string) => (
                      <Tag key={gpu} style={{ fontSize: 11 }}>{gpu}</Tag>
                    ))}
                  </div>
                  <Divider style={{ margin: '12px 0 0 0' }} />
                </div>
              )) : (
                <Text type="secondary">暂无运行中的模型</Text>
              )}
            </div>
          </Card>
        </Col>

        {/* 使用排行 */}
        <Col xs={24} lg={8}>
          <Card title="使用排行" className="stat-card" loading={loading}>
            {usageStats.length > 0 ? (
              <ReactECharts option={getUsageChartOption()} style={{ height: 200 }} />
            ) : (
              <Text type="secondary">暂无数据</Text>
            )}
          </Card>
        </Col>

        {/* 调用分布 */}
        <Col xs={24} lg={8}>
          <Card title="调用分布" className="stat-card" loading={loading}>
            {callDistribution.length > 0 ? (
              <ReactECharts option={getPieChartOption()} style={{ height: 200 }} />
            ) : (
              <Text type="secondary">暂无数据</Text>
            )}
          </Card>
        </Col>

        {/* Token 趋势 */}
        <Col xs={24} lg={8}>
          <Card title="Token 趋势" className="stat-card" loading={loading}>
            {tokenTrend.length > 0 ? (
              <ReactECharts option={getLineChartOption()} style={{ height: 200 }} />
            ) : (
              <Text type="secondary">暂无数据</Text>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
