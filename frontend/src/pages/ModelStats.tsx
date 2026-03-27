import { useEffect, useState } from 'react'
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Select,
  Button,
  Empty,
} from 'antd'
import {
  ReloadOutlined,
  RiseOutlined,
  FallOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  UserOutlined,
  BarChartOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import dayjs from 'dayjs'
import type { ModelStats as ModelStatsType } from '../types'
import { getModelStats } from '../api/vllm'

const { Title, Text } = Typography
const { Option } = Select

const ModelStats = () => {
  const [stats, setStats] = useState<ModelStatsType | null>(null)
  const [loading, setLoading] = useState(false)
  const [timeRange, setTimeRange] = useState('7d')
  const [lastUpdate, setLastUpdate] = useState<string>('')

  useEffect(() => {
    fetchStats()
  }, [timeRange])

  const fetchStats = async () => {
    setLoading(true)
    try {
      const data = await getModelStats(timeRange)
      setStats(data)
      setLastUpdate(dayjs().format('HH:mm:ss'))
    } catch (error) {
      console.error('获取统计失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const getTrendIcon = (trend: number) => {
    if (trend > 0) {
      return <RiseOutlined style={{ color: '#52c41a' }} />
    }
    return <FallOutlined style={{ color: '#ff4d4f' }} />
  }

  const getTrendColor = (trend: number) => {
    return trend > 0 ? '#52c41a' : '#ff4d4f'
  }

  const getDailyTrendOption = () => {
    if (!stats?.dailyTrend) return {}
    return {
      color: ['#7c3aed'],
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: stats.dailyTrend.map(d => d.date),
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
        data: stats.dailyTrend.map(d => d.calls),
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
        showSymbol: false,
      }],
    }
  }

  const getLatencyDistributionOption = () => {
    if (!stats?.latencyDistribution) return {}
    return {
      color: ['#7c3aed', '#a78bfa', '#ddd6fe'],
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: stats.latencyDistribution.map(d => d.time),
        axisLine: { lineStyle: { color: '#e5e7eb' } },
        axisLabel: { color: '#6b7280' },
      },
      yAxis: {
        type: 'value',
        name: 'ms',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#f3f4f6' } },
        axisLabel: { color: '#6b7280' },
      },
      series: [
        {
          name: 'P50',
          type: 'line',
          smooth: true,
          data: stats.latencyDistribution.map(d => d.p50),
          showSymbol: false,
        },
        {
          name: 'P95',
          type: 'line',
          smooth: true,
          data: stats.latencyDistribution.map(d => d.p95),
          showSymbol: false,
        },
        {
          name: 'P99',
          type: 'line',
          smooth: true,
          data: stats.latencyDistribution.map(d => d.p99),
          showSymbol: false,
        },
      ],
      legend: {
        data: ['P50', 'P95', 'P99'],
        bottom: 0,
        icon: 'circle',
        itemWidth: 8,
        itemHeight: 8,
      },
    }
  }

  const getTokenDistributionOption = () => {
    if (!stats?.tokenDistribution) return {}
    return {
      color: ['#7c3aed', '#a78bfa'],
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: {
        type: 'value',
        show: false,
      },
      yAxis: {
        type: 'category',
        data: stats.tokenDistribution.map(d => d.model).reverse(),
        axisLine: { show: false },
        axisTick: { show: false },
      },
      series: [
        {
          name: '输入',
          type: 'bar',
          stack: 'total',
          data: stats.tokenDistribution.map(d => d.input).reverse(),
          itemStyle: { borderRadius: [0, 4, 4, 0] },
          barWidth: 20,
        },
        {
          name: '输出',
          type: 'bar',
          stack: 'total',
          data: stats.tokenDistribution.map(d => d.output).reverse(),
          itemStyle: { borderRadius: [0, 4, 4, 0] },
          barWidth: 20,
        },
      ],
      legend: {
        data: ['输入', '输出'],
        bottom: 0,
        icon: 'rect',
        itemWidth: 12,
        itemHeight: 12,
      },
    }
  }

  const getModelTypeDistributionOption = () => {
    if (!stats?.modelTypeDistribution) return {}
    return {
      color: ['#7c3aed', '#a78bfa', '#c4b5fd', '#e9d5ff'],
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
        data: stats.modelTypeDistribution,
      }],
    }
  }

  const getErrorDistributionOption = () => {
    if (!stats?.errorDistribution) return {}
    return {
      grid: { left: '3%', right: '15%', bottom: '3%', top: '3%', containLabel: true },
      xAxis: {
        type: 'value',
        show: false,
      },
      yAxis: {
        type: 'category',
        data: stats.errorDistribution.map(d => d.type).reverse(),
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#374151' },
      },
      series: [{
        type: 'bar',
        data: stats.errorDistribution.map(d => ({
          value: d.count,
          itemStyle: {
            color: d.type === '超时' ? '#ff4d4f' : d.type === '内存不足' ? '#faad14' : '#d9d9d9',
          },
        })).reverse(),
        barWidth: 16,
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => {
            const item = stats.errorDistribution[stats.errorDistribution.length - 1 - params.dataIndex]
            return `${item.count} (${item.percentage}%)`
          },
        },
      }],
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={4} style={{ marginBottom: 4 }}>模型统计</Title>
          <Text type="secondary">各模型的调用次数、Token 使用量等统计分析 · 最后更新: {lastUpdate}</Text>
        </div>
        <Space>
          <Select value={timeRange} onChange={setTimeRange} style={{ width: 120 }}>
            <Option value="24h">最近 24 小时</Option>
            <Option value="7d">最近 7 天</Option>
            <Option value="30d">最近 30 天</Option>
          </Select>
          <Button icon={<ReloadOutlined />} onClick={fetchStats} loading={loading}>
            刷新
          </Button>
        </Space>
      </div>

      {stats && (
        <>
          {/* 统计概览 */}
          <Card style={{ marginBottom: 24 }}>
            <Title level={5} style={{ marginBottom: 16 }}>
              <Space>
                <ThunderboltOutlined />
                统计概览
              </Space>
            </Title>
            <Row gutter={[24, 24]}>
              <Col xs={24} sm={12} md={6}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <ThunderboltOutlined style={{ color: '#6b7280' }} />
                    <Text type="secondary">总调用次数</Text>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <Text strong style={{ fontSize: 28 }}>{stats.overview.totalCalls}</Text>
                    <Space size={4}>
                      {getTrendIcon(stats.overview.callsTrend)}
                      <Text style={{ fontSize: 12, color: getTrendColor(stats.overview.callsTrend) }}>
                        {stats.overview.callsTrend > 0 ? '+' : ''}{stats.overview.callsTrend}%
                      </Text>
                    </Space>
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>较上周</Text>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <BarChartOutlined style={{ color: '#6b7280' }} />
                    <Text type="secondary">Token 使用量</Text>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <Text strong style={{ fontSize: 28 }}>{stats.overview.totalTokens}</Text>
                    <Space size={4}>
                      {getTrendIcon(stats.overview.tokensTrend)}
                      <Text style={{ fontSize: 12, color: getTrendColor(stats.overview.tokensTrend) }}>
                        {stats.overview.tokensTrend > 0 ? '+' : ''}{stats.overview.tokensTrend}%
                      </Text>
                    </Space>
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>较上周</Text>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <ClockCircleOutlined style={{ color: '#6b7280' }} />
                    <Text type="secondary">平均延迟</Text>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <Text strong style={{ fontSize: 28 }}>{stats.overview.avgLatency}</Text>
                    <Text style={{ fontSize: 14, color: '#6b7280' }}>ms</Text>
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>P99: {stats.overview.p99Latency}ms</Text>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <CheckCircleOutlined style={{ color: '#6b7280' }} />
                    <Text type="secondary">成功率</Text>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <Text strong style={{ fontSize: 28, color: '#52c41a' }}>{stats.overview.successRate}</Text>
                    <Text style={{ fontSize: 14, color: '#6b7280' }}>%</Text>
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>{stats.overview.failedCalls} 次失败</Text>
                </div>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <UserOutlined style={{ color: '#6b7280' }} />
                    <Text type="secondary">活跃用户</Text>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <Text strong style={{ fontSize: 28 }}>{stats.overview.activeUsers}</Text>
                    <Space size={4}>
                      {getTrendIcon(stats.overview.usersTrend)}
                      <Text style={{ fontSize: 12, color: getTrendColor(stats.overview.usersTrend) }}>
                        {stats.overview.usersTrend > 0 ? '+' : ''}{stats.overview.usersTrend}%
                      </Text>
                    </Space>
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>较上周</Text>
                </div>
              </Col>
            </Row>
          </Card>

          {/* 图表区域 */}
          <Row gutter={[24, 24]}>
            {/* 每日调用趋势 */}
            <Col xs={24} lg={12}>
              <Card title="每日调用趋势" className="stat-card">
                <ReactECharts option={getDailyTrendOption()} style={{ height: 280 }} />
              </Card>
            </Col>

            {/* 延迟分布 */}
            <Col xs={24} lg={12}>
              <Card title="延迟分布 (24h)" className="stat-card">
                <ReactECharts option={getLatencyDistributionOption()} style={{ height: 280 }} />
              </Card>
            </Col>

            {/* Token 使用量分布 */}
            <Col xs={24} lg={8}>
              <Card title="Token 使用量分布" className="stat-card">
                <ReactECharts option={getTokenDistributionOption()} style={{ height: 280 }} />
              </Card>
            </Col>

            {/* 模型类型占比 */}
            <Col xs={24} lg={8}>
              <Card title="模型类型占比" className="stat-card">
                <ReactECharts option={getModelTypeDistributionOption()} style={{ height: 280 }} />
              </Card>
            </Col>

            {/* 错误类型分布 */}
            <Col xs={24} lg={8}>
              <Card title="错误类型分布" className="stat-card">
                <ReactECharts option={getErrorDistributionOption()} style={{ height: 280 }} />
              </Card>
            </Col>
          </Row>
        </>
      )}

      {!stats && !loading && (
        <Card>
          <Empty description="暂无统计数据" />
        </Card>
      )}
    </div>
  )
}

export default ModelStats
