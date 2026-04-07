
import { useState, useRef, useEffect } from 'react'
import {
  Card,
  Select,
  Input,
  Button,
  Space,
  Typography,
  List,
  message,
  Divider,
  Slider,
  Form,
  Row,
  Col,
  Spin,
  Empty,
} from 'antd'
import {
  SendOutlined,
  ClearOutlined,
  ThunderboltOutlined,
  RobotOutlined,
  UserOutlined,
  StopOutlined,
} from '@ant-design/icons'
import { getModelInstances, createChatCompletion } from '../api/vllm'
import type { ModelInstance } from '../types'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input
const { Option } = Select

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

const ChatPlayground = () => {
  const [instances, setInstances] = useState&lt;ModelInstance[]&gt;([])
  const [selectedInstance, setSelectedInstance] = useState&lt;string&gt;('')
  const [messages, setMessages] = useState&lt;ChatMessage[]&gt;([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [instancesLoading, setInstancesLoading] = useState(false)
  const messagesEndRef = useRef&lt;HTMLDivElement&gt;(null)
  const [form] = Form.useForm()

  useEffect(() =&gt; {
    fetchInstances()
  }, [])

  useEffect(() =&gt; {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () =&gt; {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchInstances = async () =&gt; {
    setInstancesLoading(true)
    try {
      const data = await getModelInstances()
      const runningInstances = data.filter(i =&gt; i.status === 'running')
      setInstances(runningInstances)
      if (runningInstances.length &gt; 0 &amp;&amp; !selectedInstance) {
        setSelectedInstance(runningInstances[0].name)
      }
    } catch (error) {
      message.error('获取模型实例失败')
    } finally {
      setInstancesLoading(false)
    }
  }

  const handleSend = async () =&gt; {
    if (!inputValue.trim() || !selectedInstance || loading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    }

    setMessages(prev =&gt; [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      const values = form.getFieldsValue()
      const chatMessages = messages.map(m =&gt; ({
        role: m.role,
        content: m.content,
      }))
      chatMessages.push(userMessage)

      const response = await createChatCompletion({
        model: selectedInstance,
        messages: chatMessages,
        temperature: values.temperature || 0.7,
        max_tokens: values.maxTokens || 1024,
      })

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.choices?.[0]?.message?.content || '抱歉，没有收到回复',
        timestamp: new Date(),
      }

      setMessages(prev =&gt; [...prev, assistantMessage])
    } catch (error) {
      message.error('发送消息失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () =&gt; {
    setMessages([])
  }

  const getRunningInstances = () =&gt; {
    return instances.filter(i =&gt; i.status === 'running')
  }

  return (
    &lt;div style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column', gap: 16 }}&gt;
      {/* 页面标题和配置区 */}
      &lt;div&gt;
        &lt;div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}&gt;
          &lt;div&gt;
            &lt;Title level={4} style={{ marginBottom: 4 }}&gt;
              &lt;Space&gt;
                &lt;ThunderboltOutlined /&gt;
                模型测试台
              &lt;/Space&gt;
            &lt;/Title&gt;
            &lt;Text type="secondary"&gt;直接测试已部署的大语言模型&lt;/Text&gt;
          &lt;/div&gt;
          &lt;Button icon={&lt;ClearOutlined /&gt;} onClick={handleClear}&gt;
            清空对话
          &lt;/Button&gt;
        &lt;/div&gt;

        {/* 模型和参数配置 */}
        &lt;Card size="small" style={{ background: '#fafafa' }}&gt;
          &lt;Form form={form} layout="inline" initialValues={{ temperature: 0.7, maxTokens: 1024 }}&gt;
            &lt;Space wrap style={{ width: '100%' }}&gt;
              &lt;Form.Item label="选择模型" style={{ minWidth: 280 }}&gt;
                &lt;Select
                  placeholder="选择运行中的模型"
                  value={selectedInstance}
                  onChange={setSelectedInstance}
                  loading={instancesLoading}
                  style={{ width: 280 }}
                &gt;
                  {getRunningInstances().map((instance) =&gt; (
                    &lt;Option key={instance.name} value={instance.name}&gt;
                      {instance.name} ({instance.modelName})
                    &lt;/Option&gt;
                  ))}
                &lt;/Select&gt;
              &lt;/Form.Item&gt;

              &lt;Form.Item label="温度" style={{ minWidth: 200 }}&gt;
                &lt;Slider
                  min={0}
                  max={2}
                  step={0.1}
                  style={{ width: 150 }}
                  marks={{ 0: '0', 1: '1', 2: '2' }}
                  tooltip={{ formatter: (v) =&gt; v?.toFixed(1) }}
                  {...form.getFieldProps('temperature')}
                /&gt;
              &lt;/Form.Item&gt;

              &lt;Form.Item label="最大Token" style={{ minWidth: 150 }}&gt;
                &lt;Select style={{ width: 120 }} {...form.getFieldProps('maxTokens')}&gt;
                  &lt;Option value={256}&gt;256&lt;/Option&gt;
                  &lt;Option value={512}&gt;512&lt;/Option&gt;
                  &lt;Option value={1024}&gt;1024&lt;/Option&gt;
                  &lt;Option value={2048}&gt;2048&lt;/Option&gt;
                  &lt;Option value={4096}&gt;4096&lt;/Option&gt;
                &lt;/Select&gt;
              &lt;/Form.Item&gt;

              &lt;Button onClick={fetchInstances} icon={&lt;ClearOutlined /&gt;} size="small"&gt;
                刷新
              &lt;/Button&gt;
            &lt;/Space&gt;
          &lt;/Form&gt;
        &lt;/Card&gt;
      &lt;/div&gt;

      {/* 聊天区域 */}
      &lt;Card style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}&gt;
        {getRunningInstances().length === 0 ? (
          &lt;Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              &lt;Space direction="vertical"&gt;
                &lt;Text&gt;暂无运行中的模型&lt;/Text&gt;
                &lt;Text type="secondary"&gt;请先在模型仓库中部署一个模型&lt;/Text&gt;
              &lt;/Space&gt;
            }
          /&gt;
        ) : (
          &lt;&gt;
            {/* 消息列表 */}
            &lt;div style={{ flex: 1, overflowY: 'auto', paddingRight: 8, marginBottom: 16 }}&gt;
              {messages.length === 0 ? (
                &lt;div style={{ textAlign: 'center', padding: '40px 20px' }}&gt;
                  &lt;RobotOutlined style={{ fontSize: 48, color: '#999', marginBottom: 16 }} /&gt;
                  &lt;Text type="secondary"&gt;开始与模型对话吧！&lt;/Text&gt;
                &lt;/div&gt;
              ) : (
                &lt;List
                  dataSource={messages}
                  renderItem={(msg) =&gt; (
                    &lt;List.Item style={{ border: 'none', padding: '8px 0' }}&gt;
                      &lt;div
                        style={{
                          display: 'flex',
                          gap: 12,
                          width: '100%',
                          flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                        }}
                      &gt;
                        &lt;div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: msg.role === 'user' ? '#1890ff' : '#7c3aed',
                            color: '#fff',
                            flexShrink: 0,
                          }}
                        &gt;
                          {msg.role === 'user' ? &lt;UserOutlined /&gt; : &lt;RobotOutlined /&gt;}
                        &lt;/div&gt;
                        &lt;div
                          style={{
                            maxWidth: '70%',
                            background: msg.role === 'user' ? '#e6f7ff' : '#f9f0ff',
                            padding: '12px 16px',
                            borderRadius: 8,
                            borderTopLeftRadius: msg.role === 'user' ? 8 : 0,
                            borderTopRightRadius: msg.role === 'user' ? 0 : 8,
                          }}
                        &gt;
                          &lt;Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap' }}&gt;
                            {msg.content}
                          &lt;/Paragraph&gt;
                          {msg.timestamp &amp;&amp; (
                            &lt;Text type="secondary" style={{ fontSize: 11, marginTop: 4, display: 'block' }}&gt;
                              {msg.timestamp.toLocaleTimeString('zh-CN')}
                            &lt;/Text&gt;
                          )}
                        &lt;/div&gt;
                      &lt;/div&gt;
                    &lt;/List.Item&gt;
                  )}
                /&gt;
              )}
              {loading &amp;&amp; (
                &lt;div style={{ display: 'flex', gap: 12, padding: '8px 0' }}&gt;
                  &lt;div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: '#7c3aed',
                      color: '#fff',
                      flexShrink: 0,
                    }}
                  &gt;
                    &lt;RobotOutlined /&gt;
                  &lt;/div&gt;
                  &lt;div
                    style={{
                      background: '#f9f0ff',
                      padding: '12px 16px',
                      borderRadius: 8,
                      borderTopRightRadius: 0,
                    }}
                  &gt;
                    &lt;Spin size="small" /&gt;
                    &lt;Text type="secondary" style={{ marginLeft: 8 }}&gt;模型正在思考...&lt;/Text&gt;
                  &lt;/div&gt;
                &lt;/div&gt;
              )}
              &lt;div ref={messagesEndRef} /&gt;
            &lt;/div&gt;

            &lt;Divider style={{ margin: '8px 0' }} /&gt;

            {/* 输入区域 */}
            &lt;div&gt;
              &lt;Space.Compact style={{ width: '100%' }}&gt;
                &lt;TextArea
                  placeholder="输入您的消息..."
                  value={inputValue}
                  onChange={(e) =&gt; setInputValue(e.target.value)}
                  onPressEnter={(e) =&gt; {
                    if (!e.shiftKey) {
                      e.preventDefault()
                      handleSend()
                    }
                  }}
                  autoSize={{ minRows: 2, maxRows: 6 }}
                  disabled={!selectedInstance || loading}
                /&gt;
                &lt;Button
                  type="primary"
                  icon={loading ? &lt;StopOutlined /&gt; : &lt;SendOutlined /&gt;}
                  onClick={handleSend}
                  loading={loading}
                  disabled={!selectedInstance || !inputValue.trim()}
                  style={{ height: 'auto' }}
                &gt;
                  {loading ? '停止' : '发送'}
                &lt;/Button&gt;
              &lt;/Space.Compact&gt;
              &lt;Text type="secondary" style={{ fontSize: 12, marginTop: 4, display: 'block' }}&gt;
                按 Enter 发送，Shift + Enter 换行
              &lt;/Text&gt;
            &lt;/div&gt;
          &lt;/&gt;
        )}
      &lt;/Card&gt;
    &lt;/div&gt;
  )
}

export default ChatPlayground

