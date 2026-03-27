import { useEffect, useRef, useState, useCallback } from 'react'
import {
  Card,
  Typography,
  Tag,
  Space,
  Button,
  Spin,
  Alert,
  Badge,
  Tooltip,
} from 'antd'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  DownloadOutlined,
  CodeOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'

const { Text } = Typography

interface LogEntry {
  timestamp: string
  level: string
  message: string
}

interface InstanceStatus {
  id: string
  model_name: string
  model_path: string
  port: number
  status: 'starting' | 'running' | 'stopping' | 'stopped' | 'error'
  status_message: string
  start_time: string
  log_count: number
}

interface ModelLaunchLogProps {
  instanceId: string
  onClose?: () => void
  onStarted?: () => void
}

const ModelLaunchLog = ({ instanceId, onClose, onStarted }: ModelLaunchLogProps) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [status, setStatus] = useState<InstanceStatus | null>(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)
  const autoScrollRef = useRef(true)

  // 自动滚动到底部
  const scrollToBottom = useCallback(() => {
    if (autoScrollRef.current && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [logs, scrollToBottom])

  // 建立 WebSocket 连接
  useEffect(() => {
    if (!instanceId) return

    const wsUrl = `ws://localhost:8000/ws/instances/${instanceId}/logs`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      setError(null)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        switch (data.type) {
          case 'history':
            // 历史日志
            setLogs(data.logs || [])
            break

          case 'log':
            // 新日志
            setLogs((prev) => [...prev, data.data])
            break

          case 'status':
            // 状态更新
            setStatus(data.data)
            if (data.data.status === 'running' && onStarted) {
              onStarted()
            }
            break

          case 'ping':
            // 心跳，忽略
            break

          case 'error':
            setError(data.error)
            break
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onerror = () => {
      setError('WebSocket 连接错误')
      setConnected(false)
    }

    ws.onclose = () => {
      setConnected(false)
    }

    return () => {
      ws.close()
    }
  }, [instanceId, onStarted])

  // 获取日志级别颜色
  const getLogLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'red'
      case 'WARN':
      case 'WARNING':
        return 'orange'
      case 'SUCCESS':
        return 'green'
      case 'DEBUG':
        return 'gray'
      default:
        return 'blue'
    }
  }

  // 获取状态图标
  const getStatusIcon = () => {
    if (!status) return <LoadingOutlined spin />

    switch (status.status) {
      case 'running':
        return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 24 }} />
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 24 }} />
      case 'starting':
        return <LoadingOutlined spin style={{ color: '#1890ff', fontSize: 24 }} />
      case 'stopping':
        return <LoadingOutlined spin style={{ color: '#faad14', fontSize: 24 }} />
      case 'stopped':
        return <CloseCircleOutlined style={{ color: '#d9d9d9', fontSize: 24 }} />
      default:
        return <InfoCircleOutlined style={{ fontSize: 24 }} />
    }
  }

  // 获取状态文本
  const getStatusText = () => {
    if (!status) return '连接中...'

    const statusMap: { [key: string]: string } = {
      starting: '启动中',
      running: '运行中',
      stopping: '停止中',
      stopped: '已停止',
      error: '启动失败',
    }

    return statusMap[status.status] || status.status
  }

  // 获取状态颜色
  const getStatusColor = () => {
    if (!status) return 'processing'

    const colorMap: { [key: string]: string } = {
      starting: 'blue',
      running: 'success',
      stopping: 'warning',
      stopped: 'default',
      error: 'error',
    }

    return colorMap[status.status] || 'default'
  }

  // 导出日志
  const exportLogs = () => {
    const logText = logs
      .map((log) => `[${log.timestamp}] [${log.level}] ${log.message}`)
      .join('\n')
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vllm-launch-${instanceId}-${new Date().toISOString()}.log`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // 处理滚动
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50
    autoScrollRef.current = isAtBottom
  }

  return (
    <Card
      title={
        <Space>
          <CodeOutlined />
          <span>vLLM 启动日志</span>
          {status && (
            <Tag color={getStatusColor()}>
              <Space>
                {getStatusIcon()}
                {getStatusText()}
              </Space>
            </Tag>
          )}
          <Badge
            status={connected ? 'success' : 'error'}
            text={connected ? '已连接' : '未连接'}
          />
        </Space>
      }
      extra={
        <Space>
          <Tooltip title="导出日志">
            <Button icon={<DownloadOutlined />} onClick={exportLogs} size="small">
              导出
            </Button>
          </Tooltip>
          {onClose && (
            <Button onClick={onClose} size="small">
              关闭
            </Button>
          )}
        </Space>
      }
      bodyStyle={{ padding: 0 }}
    >
      {/* 状态信息 */}
      {status && (
        <div style={{ padding: '16px 24px', background: '#fafafa', borderBottom: '1px solid #f0f0f0' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Text type="secondary">模型:</Text>
              <Text strong>{status.model_name}</Text>
            </Space>
            <Space>
              <Text type="secondary">路径:</Text>
              <Text code style={{ maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {status.model_path}
              </Text>
            </Space>
            <Space>
              <Text type="secondary">端口:</Text>
              <Tag color="blue">{status.port}</Tag>
            </Space>
            {status.status_message && (
              <Space>
                <Text type="secondary">状态信息:</Text>
                <Text>{status.status_message}</Text>
              </Space>
            )}
          </Space>
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <Alert
          message="连接错误"
          description={error}
          type="error"
          showIcon
          style={{ margin: 16 }}
        />
      )}

      {/* 日志内容 */}
      <div
        style={{
          height: 400,
          overflow: 'auto',
          padding: '16px 24px',
          fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
          fontSize: 13,
          lineHeight: '1.6',
          background: '#1e1e1e',
          color: '#d4d4d4',
        }}
        onScroll={handleScroll}
      >
        {logs.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#666', paddingTop: 100 }}>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 32 }} spin />} />
            <div style={{ marginTop: 16 }}>等待日志...</div>
          </div>
        ) : (
          logs.map((log, index) => (
            <div
              key={index}
              style={{
                marginBottom: 4,
                display: 'flex',
                alignItems: 'flex-start',
              }}
            >
              <span style={{ color: '#858585', marginRight: 12, minWidth: 180, fontSize: 12 }}>
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
              <Tag
                color={getLogLevelColor(log.level)}
                style={{
                  marginRight: 12,
                  minWidth: 60,
                  textAlign: 'center',
                  fontSize: 11,
                  padding: '0 4px',
                  lineHeight: '18px',
                }}
              >
                {log.level}
              </Tag>
              <span
                style={{
                  color:
                    log.level === 'ERROR'
                      ? '#f48771'
                      : log.level === 'WARN'
                      ? '#dcdcaa'
                      : log.level === 'SUCCESS'
                      ? '#4ec9b0'
                      : '#d4d4d4',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-all',
                }}
              >
                {log.message}
              </span>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>

      {/* 底部信息 */}
      <div
        style={{
          padding: '8px 24px',
          background: '#fafafa',
          borderTop: '1px solid #f0f0f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Text type="secondary" style={{ fontSize: 12 }}>
          共 {logs.length} 条日志
        </Text>
        <Space>
          <Button
            size="small"
            onClick={() => {
              autoScrollRef.current = true
              scrollToBottom()
            }}
          >
            滚动到底部
          </Button>
        </Space>
      </div>
    </Card>
  )
}

export default ModelLaunchLog
