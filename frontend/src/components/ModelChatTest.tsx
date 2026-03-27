import { useState, useRef, useEffect } from 'react'
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Avatar,
  Upload,
  message,
  Spin,
  Tag,
  Divider,
  Empty,
  Tooltip,
  Badge,
} from 'antd'
import {
  SendOutlined,
  PictureOutlined,
  CloseOutlined,
  RobotOutlined,
  UserOutlined,
  DeleteOutlined,
  LoadingOutlined,
  MessageOutlined,
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd/es/upload'
import ReactMarkdown from 'react-markdown'
import type { ModelInstance } from '../types'
import { createChatCompletion } from '../api/vllm'

const { Text } = Typography
const { TextArea } = Input

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  images?: string[]
  timestamp: Date
  isStreaming?: boolean
}

interface ModelChatTestProps {
  instance: ModelInstance
}

const ModelChatTest = ({ instance }: ModelChatTestProps) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [previewImages, setPreviewImages] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<any>(null)

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 处理图片上传
  const handleUpload: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList)
    
    // 生成预览URL
    const previews = newFileList
      .filter(file => file.originFileObj)
      .map(file => URL.createObjectURL(file.originFileObj as Blob))
    
    // 清理旧的预览URL
    previewImages.forEach(url => {
      if (!previews.includes(url)) {
        URL.revokeObjectURL(url)
      }
    })
    
    setPreviewImages(previews)
  }

  // 移除图片
  const handleRemoveImage = (index: number) => {
    const newFileList = [...fileList]
    newFileList.splice(index, 1)
    setFileList(newFileList)
    
    const newPreviews = [...previewImages]
    URL.revokeObjectURL(newPreviews[index])
    newPreviews.splice(index, 1)
    setPreviewImages(newPreviews)
  }

  // 将图片转换为base64
  const convertImageToBase64 = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const base64 = reader.result as string
        // 移除 data:image/xxx;base64, 前缀
        const base64Data = base64.split(',')[1]
        resolve(base64Data)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() && fileList.length === 0) {
      message.warning('请输入消息或上传图片')
      return
    }

    const userMessageId = Date.now().toString()
    const assistantMessageId = (Date.now() + 1).toString()

    // 准备图片数据
    let imageBase64List: string[] = []
    if (fileList.length > 0) {
      try {
        imageBase64List = await Promise.all(
          fileList
            .filter(file => file.originFileObj)
            .map(file => convertImageToBase64(file.originFileObj as File))
        )
      } catch (error) {
        message.error('图片处理失败')
        return
      }
    }

    // 添加用户消息
    const userMessage: Message = {
      id: userMessageId,
      role: 'user',
      content: inputValue.trim(),
      images: previewImages.length > 0 ? [...previewImages] : undefined,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setFileList([])
    setPreviewImages([])
    setLoading(true)

    // 添加助手消息（占位）
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    }
    setMessages(prev => [...prev, assistantMessage])

    try {
      // 构建消息历史
      const historyMessages = messages
        .filter(m => !m.isStreaming)
        .map(m => ({
          role: m.role,
          content: m.content,
        }))

      // 构建当前消息内容
      let currentContent = inputValue.trim()
      
      // 如果有图片，构建多模态内容
      if (imageBase64List.length > 0) {
        // 使用OpenAI格式的多模态消息
        const multimodalContent = [
          { type: 'text', text: currentContent || '请描述这张图片' },
          ...imageBase64List.map(base64 => ({
            type: 'image_url',
            image_url: {
              url: `data:image/jpeg;base64,${base64}`,
            },
          })),
        ]
        
        const response = await createChatCompletion({
          model: instance.modelName,
          messages: [
            ...historyMessages,
            { role: 'user', content: multimodalContent as any },
          ],
          temperature: 0.7,
          max_tokens: 2048,
          stream: false,
        })

        const assistantContent = response.choices?.[0]?.message?.content || '无响应'
        
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMessageId
              ? { ...m, content: assistantContent, isStreaming: false }
              : m
          )
        )
      } else {
        // 纯文本对话
        const response = await createChatCompletion({
          model: instance.modelName,
          messages: [
            ...historyMessages,
            { role: 'user', content: currentContent },
          ],
          temperature: 0.7,
          max_tokens: 2048,
          stream: false,
        })

        const assistantContent = response.choices?.[0]?.message?.content || '无响应'
        
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantMessageId
              ? { ...m, content: assistantContent, isStreaming: false }
              : m
          )
        )
      }
    } catch (error: any) {
      console.error('对话请求失败:', error)
      const errorMessage = error.response?.data?.error?.message || error.message || '请求失败'
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantMessageId
            ? { ...m, content: `❌ 错误: ${errorMessage}`, isStreaming: false }
            : m
        )
      )
      message.error('对话请求失败')
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  // 清空对话
  const handleClear = () => {
    setMessages([])
    previewImages.forEach(url => URL.revokeObjectURL(url))
    setPreviewImages([])
    setFileList([])
    message.success('对话已清空')
  }

  // 处理按键
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 判断模型是否支持视觉
  const isVisionModel = instance.modelType === 'multimodal' || 
    instance.modelName.toLowerCase().includes('vision') ||
    instance.modelName.toLowerCase().includes('vl') ||
    instance.modelName.toLowerCase().includes('gpt-4v')

  return (
    <Card
      title={
        <Space>
          <MessageOutlined />
          <span>对话测试</span>
          <Badge 
            status={instance.status === 'running' ? 'success' : 'error'} 
            text={instance.status === 'running' ? '在线' : '离线'}
          />
        </Space>
      }
      extra={
        <Space>
          {isVisionModel && (
            <Tag color="purple" icon={<PictureOutlined />}>
              支持图片
            </Tag>
          )}
          <Tooltip title="清空对话">
            <Button
              icon={<DeleteOutlined />}
              size="small"
              onClick={handleClear}
              disabled={messages.length === 0}
            />
          </Tooltip>
        </Space>
      }
      style={{ height: '100%' }}
      bodyStyle={{ 
        height: 'calc(100% - 57px)', 
        padding: 0,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* 消息列表 */}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px',
          background: '#f5f5f5',
        }}
      >
        {messages.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              <Space direction="vertical" align="center">
                <Text type="secondary">开始与模型对话</Text>
                {isVisionModel && (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    支持上传图片进行多模态对话
                  </Text>
                )}
              </Space>
            }
            style={{ marginTop: 100 }}
          />
        ) : (
          <Space direction="vertical" style={{ width: '100%' }} size={16}>
            {messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  width: '100%',
                }}
              >
                <Space
                  align="start"
                  style={{
                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                    maxWidth: '85%',
                  }}
                >
                  <Avatar
                    icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                      backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a',
                      flexShrink: 0,
                    }}
                  />
                  <div
                    style={{
                      background: msg.role === 'user' ? '#1890ff' : '#fff',
                      color: msg.role === 'user' ? '#fff' : 'rgba(0, 0, 0, 0.85)',
                      padding: '12px 16px',
                      borderRadius: '12px',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      wordBreak: 'break-word',
                    }}
                  >
                    {/* 图片显示 */}
                    {msg.images && msg.images.length > 0 && (
                      <div style={{ marginBottom: 8 }}>
                        <Space wrap size={8}>
                          {msg.images.map((img, idx) => (
                            <img
                              key={idx}
                              src={img}
                              alt={`上传图片 ${idx + 1}`}
                              style={{
                                maxWidth: 120,
                                maxHeight: 120,
                                borderRadius: 8,
                                objectFit: 'cover',
                              }}
                            />
                          ))}
                        </Space>
                      </div>
                    )}
                    
                    {/* 文本内容 */}
                    {msg.role === 'assistant' ? (
                      <div className="markdown-content">
                        {msg.isStreaming && !msg.content ? (
                          <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />
                        ) : (
                          <ReactMarkdown
                            components={{
                              p: ({ children }) => <p style={{ margin: '4px 0' }}>{children}</p>,
                              code: ({ children }) => (
                                <code
                                  style={{
                                    background: 'rgba(0,0,0,0.05)',
                                    padding: '2px 6px',
                                    borderRadius: 4,
                                    fontFamily: 'monospace',
                                  }}
                                >
                                  {children}
                                </code>
                              ),
                              pre: ({ children }) => (
                                <pre
                                  style={{
                                    background: 'rgba(0,0,0,0.05)',
                                    padding: 12,
                                    borderRadius: 8,
                                    overflow: 'auto',
                                    fontSize: 12,
                                  }}
                                >
                                  {children}
                                </pre>
                              ),
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        )}
                      </div>
                    ) : (
                      <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                    )}
                    
                    {/* 时间戳 */}
                    <div
                      style={{
                        fontSize: 11,
                        opacity: 0.6,
                        marginTop: 4,
                        textAlign: 'right',
                      }}
                    >
                      {msg.timestamp.toLocaleTimeString('zh-CN', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>
                </Space>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </Space>
        )}
      </div>

      <Divider style={{ margin: 0 }} />

      {/* 输入区域 */}
      <div style={{ padding: '16px', background: '#fff' }}>
        {/* 图片预览 */}
        {previewImages.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <Space wrap size={8}>
              {previewImages.map((img, idx) => (
                <div key={idx} style={{ position: 'relative' }}>
                  <img
                    src={img}
                    alt={`预览 ${idx + 1}`}
                    style={{
                      width: 60,
                      height: 60,
                      objectFit: 'cover',
                      borderRadius: 8,
                      border: '1px solid #d9d9d9',
                    }}
                  />
                  <Button
                    type="primary"
                    danger
                    size="small"
                    icon={<CloseOutlined />}
                    style={{
                      position: 'absolute',
                      top: -8,
                      right: -8,
                      width: 20,
                      height: 20,
                      minWidth: 20,
                      padding: 0,
                      borderRadius: '50%',
                    }}
                    onClick={() => handleRemoveImage(idx)}
                  />
                </div>
              ))}
            </Space>
          </div>
        )}

        <Space.Compact style={{ width: '100%' }}>
          {/* 图片上传按钮 */}
          {isVisionModel && (
            <Upload
              accept="image/*"
              multiple
              showUploadList={false}
              fileList={fileList}
              onChange={handleUpload}
              beforeUpload={() => false}
              disabled={loading}
            >
              <Button
                icon={<PictureOutlined />}
                disabled={loading}
                style={{ height: 80 }}
              />
            </Upload>
          )}
          
          <TextArea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isVisionModel
                ? '输入消息，或上传图片进行多模态对话...'
                : '输入消息开始对话...'
            }
            autoSize={{ minRows: 3, maxRows: 6 }}
            disabled={loading}
            style={{ flex: 1 }}
          />
          
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            disabled={!inputValue.trim() && fileList.length === 0}
            style={{ height: 80, width: 80 }}
          />
        </Space.Compact>
        
        <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
          按 Enter 发送，Shift + Enter 换行
          {isVisionModel && ' · 支持拖拽或点击上传图片'}
        </Text>
      </div>
    </Card>
  )
}

export default ModelChatTest
