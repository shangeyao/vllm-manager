import { useEffect, useState, useRef } from 'react'
import {
  Card,
  Input,
  Tabs,
  Row,
  Col,
  Tag,
  Typography,
  Space,
  Button,
  Dropdown,
  Empty,
  Spin,
  message,
  Modal,
  Form,
  Select,
  Slider,
  InputNumber,
  Switch,
  Divider,
  Radio,
  Progress,
  Collapse,
  Tooltip,
  Alert,
  Drawer,
} from 'antd'
import {
  SearchOutlined,
  DownOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
  CodeOutlined,
  PictureOutlined,
  SoundOutlined,
  FileTextOutlined,
  DownloadOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
  EyeOutlined,
  SyncOutlined,
} from '@ant-design/icons'
import type { Model, ModelSpec } from '../types'
import { getModels, deployModel, downloadModel, getDownloadStatus, refreshModelList } from '../api/vllm'
import ModelLaunchLog from '../components/ModelLaunchLog'

const { Title, Text } = Typography
const { Option } = Select

// 模型类型定义
const modelTypes = [
  { key: 'all', label: '全部模型', icon: <DatabaseOutlined /> },
  { key: 'llm', label: '大语言模型', icon: <ThunderboltOutlined /> },
  { key: 'embedding', label: '向量模型', icon: <FileTextOutlined /> },
  { key: 'image', label: '图像模型', icon: <PictureOutlined /> },
  { key: 'audio', label: '音频模型', icon: <SoundOutlined /> },
  { key: 'multimodal', label: '多模态', icon: <CodeOutlined /> },
]

// 模型能力标签 - 支持 ModelScope 原始标签
const abilityLabels: Record<string, { color: string; label: string }> = {
  // 基础能力
  'chat': { color: 'blue', label: '对话' },
  'generate': { color: 'green', label: '生成' },
  'vision': { color: 'purple', label: '视觉' },
  'tools': { color: 'orange', label: '工具' },
  'embedding': { color: 'cyan', label: '嵌入' },
  'rerank': { color: 'magenta', label: '重排' },
  'code': { color: 'geekblue', label: '代码' },
  'audio': { color: 'gold', label: '音频' },
  // ModelScope 常见标签
  'nlp': { color: 'blue', label: 'NLP' },
  'cv': { color: 'purple', label: 'CV' },
  'audio-processing': { color: 'gold', label: '音频处理' },
  'multimodal': { color: 'orange', label: '多模态' },
  'text-generation': { color: 'green', label: '文本生成' },
  'text-classification': { color: 'cyan', label: '文本分类' },
  'feature-extraction': { color: 'geekblue', label: '特征提取' },
  'sentence-similarity': { color: 'lime', label: '句子相似度' },
  'question-answering': { color: 'volcano', label: '问答' },
  'summarization': { color: 'orange', label: '摘要' },
  'translation': { color: 'purple', label: '翻译' },
  'token-classification': { color: 'pink', label: 'Token分类' },
  'fill-mask': { color: 'cyan', label: '掩码填充' },
  'image-classification': { color: 'magenta', label: '图像分类' },
  'object-detection': { color: 'red', label: '目标检测' },
  'image-segmentation': { color: 'volcano', label: '图像分割' },
  'image-to-text': { color: 'gold', label: '图像描述' },
  'text-to-image': { color: 'purple', label: '文生图' },
  'automatic-speech-recognition': { color: 'blue', label: '语音识别' },
  'text-to-speech': { color: 'green', label: '语音合成' },
  'voice-activity-detection': { color: 'orange', label: '语音检测' },
  'tabular-classification': { color: 'geekblue', label: '表格分类' },
  'tabular-regression': { color: 'lime', label: '表格回归' },
  'reinforcement-learning': { color: 'red', label: '强化学习' },
  'robotics': { color: 'volcano', label: '机器人' },
}

// 语言标签 - 支持 ModelScope 语言标签
const languageLabels: Record<string, { color: string; label: string }> = {
  'zh': { color: 'red', label: '中文' },
  'en': { color: 'blue', label: '英文' },
  'multilingual': { color: 'purple', label: '多语言' },
  '中文': { color: 'red', label: '中文' },
  '英文': { color: 'blue', label: '英文' },
  '多语言': { color: 'purple', label: '多语言' },
  'chinese': { color: 'red', label: '中文' },
  'english': { color: 'blue', label: '英文' },
  'japanese': { color: 'pink', label: '日语' },
  'korean': { color: 'volcano', label: '韩语' },
  'french': { color: 'cyan', label: '法语' },
  'german': { color: 'geekblue', label: '德语' },
  'spanish': { color: 'orange', label: '西班牙语' },
  'russian': { color: 'magenta', label: '俄语' },
  'arabic': { color: 'lime', label: '阿拉伯语' },
}

const ModelStore = () => {
  const [activeTab, setActiveTab] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [abilityFilter, setAbilityFilter] = useState('all')
  const [languageFilter, setLanguageFilter] = useState('all')
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  
  // 部署对话框状态
  const [deployModalVisible, setDeployModalVisible] = useState(false)
  const [selectedModel, setSelectedModel] = useState<Model | null>(null)
  const [selectedSpec, setSelectedSpec] = useState<ModelSpec | null>(null)
  const deployForm = Form.useForm()[0]
  const [deploying, setDeploying] = useState(false)
  
  // 模型下载状态
  const [modelExists, setModelExists] = useState(false)
  const [modelLocalPath, setModelLocalPath] = useState<string>('')
  const [downloading, setDownloading] = useState(false)
  const [downloadProgress, setDownloadProgress] = useState(0)
  const [downloadStatus, setDownloadStatus] = useState<string>('')
  const [currentDownloadFile, setCurrentDownloadFile] = useState<string>('')
  const [downloadError, setDownloadError] = useState<string>('')
  const downloadPollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    setLoading(true)
    try {
      const data = await getModels()
      setModels(data)
    } catch (error) {
      message.error('获取模型列表失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  // 搜索状态 - 合并成一个搜索词
  const [refreshSearchQuery, setRefreshSearchQuery] = useState<string>('')

  // 刷新模型列表
  const handleRefreshModels = async () => {
    setRefreshing(true)
    try {
      const params: { searchQuery?: string } = {}
      if (refreshSearchQuery.trim()) {
        params.searchQuery = refreshSearchQuery.trim()
      }

      const result = await refreshModelList(params)
      if (result.success) {
        message.success(result.message)
        setLastUpdated(new Date())
        // 重新获取模型列表
        await fetchModels()
      }
    } catch (error) {
      message.error('刷新模型列表失败')
      console.error(error)
    } finally {
      setRefreshing(false)
    }
  }

  // 点击模型卡片
  const handleModelClick = async (model: Model) => {
    setSelectedModel(model)
    // 默认选择第一个规格
    const defaultSpec = model.specs?.[0] || null
    setSelectedSpec(defaultSpec)
    setDownloadProgress(0)
    setDownloadStatus('')
    setCurrentDownloadFile('')
    setDownloadError('')
    setModelLocalPath('')

    // 检查模型是否已下载
    if (defaultSpec?.model_id) {
      try {
        const status = await getDownloadStatus(defaultSpec.model_id)
        if (status.status === 'completed') {
          setModelExists(true)
          setModelLocalPath(status.local_path || '')
        } else {
          setModelExists(false)
          setModelLocalPath('')
        }
      } catch (error) {
        setModelExists(false)
        setModelLocalPath('')
      }
    }
    
    // 计算推荐的GPU内存利用率
    const recommendedGpuUtil = defaultSpec?.model_size_in_billions 
      ? Math.min(0.95, 0.7 + (defaultSpec.model_size_in_billions / 100))
      : 0.9
    
    deployForm.setFieldsValue({
      // 关键配置 - 模型选择
      modelSpec: defaultSpec?.model_format + '-' + defaultSpec?.model_size_in_billions + 'B',
      quantization: defaultSpec?.quantizations?.[0] || 'none',
      
      // 关键配置 - GPU设置
      tensorParallelSize: 1,
      gpuMemoryUtilization: Math.round(recommendedGpuUtil * 10) / 10,
      
      // 关键配置 - 上下文长度
      maxModelLen: model.contextLength || 8192,
      
      // 高级配置
      dtype: 'auto',
      device: 'auto',
      swapSpace: 4,
      enforceEager: false,
      enableChunkedPrefill: true,
      maxNumSeqs: 256,
      maxNumBatchedTokens: 2048,
      quantizationParamPath: '',
      kvCacheDtype: 'auto',
      seed: 0,
    })
    
    setDeployModalVisible(true)
  }

  // 处理模型规格变更
  const handleSpecChange = (value: string) => {
    if (!selectedModel?.specs) return
    const spec = selectedModel.specs.find(
      s => s.model_format + '-' + s.model_size_in_billions + 'B' === value
    )
    if (spec) {
      setSelectedSpec(spec)
      // 根据模型大小调整推荐的GPU内存利用率
      const recommendedGpuUtil = spec.model_size_in_billions 
        ? Math.min(0.95, 0.7 + (spec.model_size_in_billions / 100))
        : 0.9
      deployForm.setFieldsValue({
        quantization: spec.quantizations?.[0] || 'none',
        gpuMemoryUtilization: Math.round(recommendedGpuUtil * 10) / 10,
      })
    }
  }

  // 真实的 ModelScope 模型下载
  const handleDownloadModel = async () => {
    if (!selectedSpec?.model_id) {
      message.error('模型ID不存在')
      return
    }

    const modelId = selectedSpec.model_id
    setDownloading(true)
    setDownloadProgress(0)
    setDownloadStatus('starting')
    setDownloadError('')

    try {
      // 开始下载
      const result = await downloadModel(modelId)
      
      if (result.status === 'completed') {
        setModelExists(true)
        setModelLocalPath(result.local_path || '')
        setDownloading(false)
        setDownloadProgress(100)
        message.success('模型已存在于本地')
        return
      }

      message.success('开始下载模型')

      // 轮询下载状态
      const pollInterval = setInterval(async () => {
        try {
          const status = await getDownloadStatus(modelId)
          
          setDownloadProgress(status.progress)
          setDownloadStatus(status.status)
          setCurrentDownloadFile(status.current_file || '')
          
          if (status.error_message) {
            setDownloadError(status.error_message)
          }

          if (status.status === 'completed') {
            clearInterval(pollInterval)
            setDownloading(false)
            setModelExists(true)
            setModelLocalPath(status.local_path || '')
            setDownloadProgress(100)
            message.success('模型下载完成')
          } else if (status.status === 'failed') {
            clearInterval(pollInterval)
            setDownloading(false)
            message.error(`下载失败: ${status.error_message || '未知错误'}`)
          }
        } catch (error) {
          console.error('获取下载状态失败:', error)
        }
      }, 2000) // 每2秒查询一次

      // 保存轮询引用以便清理
      downloadPollingRef.current = pollInterval

      // 30分钟后自动停止轮询
      setTimeout(() => {
        if (pollInterval) {
          clearInterval(pollInterval)
          if (downloading) {
            setDownloading(false)
            message.warning('下载超时，请稍后刷新查看状态')
          }
        }
      }, 30 * 60 * 1000)

    } catch (error) {
      setDownloading(false)
      message.error('启动下载失败')
      console.error(error)
    }
  }

  // 清理轮询
  useEffect(() => {
    return () => {
      if (downloadPollingRef.current) {
        clearInterval(downloadPollingRef.current)
      }
    }
  }, [])

  // 部署模型
  const [deployInstanceId, setDeployInstanceId] = useState<string | null>(null)
  const [logDrawerVisible, setLogDrawerVisible] = useState(false)

  const handleDeploy = async (values: any) => {
    if (!selectedModel || !selectedSpec) return

    setDeploying(true)
    try {
      const result = await deployModel({
        modelName: selectedModel.name,
        modelId: selectedSpec.model_id,
        quantization: values.quantization,
        tensorParallelSize: values.tensorParallelSize,
        gpuMemoryUtilization: values.gpuMemoryUtilization,
        maxModelLen: values.maxModelLen,
        dtype: values.dtype,
        gpuIndices: values.gpuIndices,
        // 高级配置
        swapSpace: values.swapSpace,
        enforceEager: values.enforceEager,
        enableChunkedPrefill: values.enableChunkedPrefill,
        maxNumSeqs: values.maxNumSeqs,
        maxNumBatchedTokens: values.maxNumBatchedTokens,
        seed: values.seed,
      })

      // 显示启动日志
      if (result.instance_id) {
        setDeployInstanceId(result.instance_id)
        setLogDrawerVisible(true)
        message.success('模型部署已启动，正在初始化...')
      }

      setDeployModalVisible(false)
    } catch (error) {
      message.error('模型部署失败')
      console.error(error)
    } finally {
      setDeploying(false)
    }
  }

  const handleDeploySuccess = () => {
    message.success('模型启动成功！')
    setLogDrawerVisible(false)
    setDeployInstanceId(null)
  }

  // 过滤模型
  const filteredModels = models.filter((model) => {
    // 类型过滤
    if (activeTab !== 'all' && model.type !== activeTab) return false
    
    // 搜索过滤
    if (searchQuery && !model.name.toLowerCase().includes(searchQuery.toLowerCase())) return false
    
    // 能力过滤
    if (abilityFilter !== 'all' && !model.abilities?.includes(abilityFilter)) return false
    
    // 语言过滤
    if (languageFilter !== 'all' && !model.language?.includes(languageFilter)) return false
    
    return true
  })

  // 获取能力标签 - 使用 ModelScope 原始标签
  const renderAbilityTags = (abilities?: string[]) => {
    if (!abilities || abilities.length === 0) return null
    return abilities.slice(0, 5).map((ability) => {
      const config = abilityLabels[ability.toLowerCase()] || { color: 'default', label: ability }
      return (
        <Tag key={ability} color={config.color} style={{ fontSize: 11, margin: '2px' }}>
          {config.label}
        </Tag>
      )
    })
  }

  // 获取语言标签 - 使用 ModelScope 原始标签
  const renderLanguageTags = (languages?: string[]) => {
    if (!languages || languages.length === 0) return null
    return languages.slice(0, 4).map((lang) => {
      const config = languageLabels[lang.toLowerCase()] || { color: 'default', label: lang }
      return (
        <Tag key={lang} color={config.color} style={{ fontSize: 11, margin: '2px' }}>
          {config.label}
        </Tag>
      )
    })
  }

  // 过滤菜单项
  const abilityMenuItems = [
    { key: 'all', label: '全部' },
    { key: 'chat', label: '对话' },
    { key: 'generate', label: '生成' },
    { key: 'vision', label: '视觉' },
    { key: 'tools', label: '工具' },
    { key: 'embedding', label: '嵌入' },
    { key: 'code', label: '代码' },
  ]

  const languageMenuItems = [
    { key: 'all', label: '全部' },
    { key: 'zh', label: '中文' },
    { key: 'en', label: '英文' },
    { key: 'multilingual', label: '多语言' },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div>
            <Title level={4} style={{ marginBottom: 4 }}>模型仓库</Title>
            <Text type="secondary">
              浏览平台支持的所有模型，点击模型进行部署
              {lastUpdated && (
                <span style={{ marginLeft: 8, fontSize: 12 }}>
                  (上次更新: {lastUpdated.toLocaleTimeString()})
                </span>
              )}
            </Text>
          </div>
        </div>

        {/* 更新模型列表区域 */}
        <Card size="small" style={{ marginBottom: 16, background: '#fafafa' }}>
          <Space wrap style={{ width: '100%' }} align="center">
            <Text strong>更新模型列表:</Text>
            <Input
              placeholder="搜索发行商或模型名"
              style={{ width: 280 }}
              value={refreshSearchQuery}
              onChange={(e) => setRefreshSearchQuery(e.target.value)}
              allowClear
              prefix={<SearchOutlined />}
            />
            <Button
              icon={<SyncOutlined spin={refreshing} />}
              onClick={handleRefreshModels}
              loading={refreshing}
              type="primary"
            >
              {refreshing ? '更新' : '更新'}
            </Button>
            {refreshSearchQuery && (
              <Button
                onClick={() => {
                  setRefreshSearchQuery('')
                }}
              >
                清除
              </Button>
            )}
          </Space>
        </Card>
      </div>

      <Card>
        {/* 模型类型标签页 */}
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={modelTypes.map((type) => ({
            key: type.key,
            label: (
              <Space>
                {type.icon}
                {type.label}
              </Space>
            ),
          }))}
          style={{ marginBottom: 24 }}
        />

        {/* 过滤器和搜索 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
          <Space wrap>
            <Dropdown
              menu={{
                items: abilityMenuItems,
                onClick: ({ key }) => setAbilityFilter(key),
              }}
            >
              <Button>
                能力: {abilityMenuItems.find(i => i.key === abilityFilter)?.label} <DownOutlined />
              </Button>
            </Dropdown>
            <Dropdown
              menu={{
                items: languageMenuItems,
                onClick: ({ key }) => setLanguageFilter(key),
              }}
            >
              <Button>
                语言: {languageMenuItems.find(i => i.key === languageFilter)?.label} <DownOutlined />
              </Button>
            </Dropdown>
          </Space>
          <Input
            placeholder="搜索模型名称..."
            prefix={<SearchOutlined />}
            style={{ width: 280 }}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            allowClear
          />
        </div>

        {/* 模型列表 */}
        <Spin spinning={loading}>
          {filteredModels.length > 0 ? (
            <Row gutter={[16, 16]}>
              {filteredModels.map((model) => (
                <Col xs={24} sm={12} lg={8} xl={6} key={model.id}>
                  <Card
                    hoverable
                    className="model-card"
                    style={{ height: '100%', cursor: 'pointer' }}
                    onClick={() => handleModelClick(model)}
                  >
                    {/* 模型名称 */}
                    <div style={{ marginBottom: 12 }}>
                      <Text strong style={{ fontSize: 16, display: 'block' }} ellipsis={{ tooltip: model.name }}>
                        {model.name}
                      </Text>
                      {model.description && (
                        <Text type="secondary" style={{ fontSize: 12 }} ellipsis={{ tooltip: model.description }}>
                          {model.description}
                        </Text>
                      )}
                    </div>

                    {/* 能力标签 */}
                    <div style={{ marginBottom: 8, minHeight: 28 }}>
                      {renderAbilityTags(model.abilities)}
                    </div>

                    {/* 语言标签 */}
                    <div style={{ marginBottom: 12, minHeight: 28 }}>
                      {renderLanguageTags(model.language)}
                    </div>

                    {/* 模型信息 */}
                    <Space wrap size={4}>
                      {model.size && (
                        <Tag style={{ fontSize: 11 }}>
                          <DatabaseOutlined style={{ marginRight: 4 }} />
                          {model.size}
                        </Tag>
                      )}
                      {model.format && (
                        <Tag style={{ fontSize: 11 }}>
                          {model.format}
                        </Tag>
                      )}
                      {model.quantization && (
                        <Tag style={{ fontSize: 11 }}>
                          {model.quantization}
                        </Tag>
                      )}
                      {model.contextLength && (
                        <Tag style={{ fontSize: 11 }}>
                          {model.contextLength}K
                        </Tag>
                      )}
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <Empty 
              description={
                <Space direction="vertical" align="center">
                  <Text>暂无模型</Text>
                  {searchQuery && <Text type="secondary">请尝试调整搜索条件</Text>}
                </Space>
              }
              style={{ padding: 40 }}
            />
          )}
        </Spin>
      </Card>

      {/* 部署配置对话框 */}
      <Modal
        title={
          <Space>
            <SettingOutlined />
            <span>部署配置 - {selectedModel?.name}</span>
          </Space>
        }
        open={deployModalVisible}
        onCancel={() => {
          setDeployModalVisible(false)
          deployForm.resetFields()
        }}
        width={750}
        footer={null}
      >
        {selectedModel && (
          <>
            {/* 模型信息 */}
            <Alert
              message={
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong style={{ fontSize: 16 }}>{selectedModel.name}</Text>
                  <Text type="secondary">{selectedModel.description}</Text>
                  <Space wrap>
                    {selectedModel.abilities?.map(ability => (
                      <Tag key={ability} color={abilityLabels[ability]?.color || 'default'}>
                        {abilityLabels[ability]?.label || ability}
                      </Tag>
                    ))}
                  </Space>
                </Space>
              }
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            {/* 模型下载状态 */}
            {!modelExists && (
              <Alert
                message="模型未下载"
                description={
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Text>该模型需要先从 ModelScope 下载到本地</Text>
                    {downloading ? (
                      <div style={{ marginTop: 8 }}>
                        <Progress 
                          percent={Math.min(Math.round(downloadProgress), 100)} 
                          status={downloadStatus === 'failed' ? 'exception' : 'active'}
                          format={(percent) => `${percent?.toFixed(1)}%`}
                        />
                        <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 4 }}>
                          状态: {downloadStatus === 'starting' ? '准备中' : 
                                 downloadStatus === 'downloading' ? '下载中' : 
                                 downloadStatus}
                        </Text>
                        {currentDownloadFile && (
                          <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                            当前文件: {currentDownloadFile}
                          </Text>
                        )}
                        {downloadError && (
                          <Text type="danger" style={{ fontSize: 12, display: 'block' }}>
                            错误: {downloadError}
                          </Text>
                        )}
                      </div>
                    ) : (
                      <Button 
                        type="primary" 
                        icon={<DownloadOutlined />}
                        onClick={handleDownloadModel}
                        style={{ marginTop: 8 }}
                      >
                        下载模型
                      </Button>
                    )}
                  </Space>
                }
                type="warning"
                showIcon
                style={{ marginBottom: 16 }}
              />
            )}

            {modelExists && (
              <Alert
                message="模型已就绪"
                description={
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Text>模型已下载到本地，可以开始部署</Text>
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>Model ID: </Text>
                      <Text code style={{ fontSize: 12 }}>{selectedSpec?.model_id}</Text>
                    </div>
                    {modelLocalPath && (
                      <div>
                        <Text type="secondary" style={{ fontSize: 12 }}>保存路径: </Text>
                        <Text code style={{ fontSize: 12, wordBreak: 'break-all' }}>{modelLocalPath}</Text>
                      </div>
                    )}
                  </Space>
                }
                type="success"
                showIcon
                style={{ marginBottom: 16 }}
              />
            )}

            {/* 部署配置表单 */}
            <Form
              form={deployForm}
              layout="vertical"
              onFinish={handleDeploy}
            >
              {/* ========== 关键配置区域 ========== */}
              <div style={{ 
                padding: 16, 
                background: '#f0f5ff', 
                borderRadius: 8, 
                border: '1px solid #d6e4ff',
                marginBottom: 16 
              }}>
                <Space style={{ marginBottom: 16 }}>
                  <ThunderboltOutlined style={{ color: '#1890ff', fontSize: 18 }} />
                  <Text strong style={{ fontSize: 16, color: '#1890ff' }}>关键配置</Text>
                </Space>

                <Row gutter={16}>
                  {/* 模型规格 */}
                  <Col span={12}>
                    <Form.Item
                      name="modelSpec"
                      label={
                        <Space>
                          <span>模型规格</span>
                          <Tooltip title="选择模型的参数大小和格式">
                            <QuestionCircleOutlined style={{ color: '#999' }} />
                          </Tooltip>
                        </Space>
                      }
                      rules={[{ required: true, message: '请选择模型规格' }]}
                    >
                      <Select onChange={handleSpecChange} size="large">
                        {selectedModel.specs?.map((spec, index) => (
                          <Option 
                            key={index} 
                            value={spec.model_format + '-' + spec.model_size_in_billions + 'B'}
                          >
                            {spec.model_size_in_billions}B {spec.model_format}
                            {spec.model_hub && ` · ${spec.model_hub}`}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>

                  {/* 量化方式 */}
                  <Col span={12}>
                    <Form.Item
                      name="quantization"
                      label={
                        <Space>
                          <span>量化方式</span>
                          <Tooltip title="量化可以减少显存占用，但可能影响精度">
                            <QuestionCircleOutlined style={{ color: '#999' }} />
                          </Tooltip>
                        </Space>
                      }
                      rules={[{ required: true, message: '请选择量化方式' }]}
                    >
                      <Select size="large">
                        {selectedSpec?.quantizations?.map(q => (
                          <Option key={q} value={q}>
                            {q === 'none' ? '♦ 无量化 (FP16/BF16)' : 
                             q === '4-bit' ? '♦ 4-bit 量化 (推荐)' :
                             q === '8-bit' ? '♦ 8-bit 量化' :
                             q === 'fp8' ? '♦ FP8 量化 (H100)' : q}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  {/* GPU数量 */}
                  <Col span={12}>
                    <Form.Item
                      name="tensorParallelSize"
                      label={
                        <Space>
                          <span>GPU 数量</span>
                          <Tooltip title="多GPU并行可以运行更大的模型">
                            <QuestionCircleOutlined style={{ color: '#999' }} />
                          </Tooltip>
                        </Space>
                      }
                      rules={[{ required: true, message: '请设置GPU数量' }]}
                    >
                      <Radio.Group buttonStyle="solid" size="large">
                        <Radio.Button value={1}>1 卡</Radio.Button>
                        <Radio.Button value={2}>2 卡</Radio.Button>
                        <Radio.Button value={4}>4 卡</Radio.Button>
                        <Radio.Button value={8}>8 卡</Radio.Button>
                      </Radio.Group>
                    </Form.Item>
                  </Col>

                  {/* GPU索引选择 */}
                  <Col span={12}>
                    <Form.Item
                      name="gpuIndices"
                      label={
                        <Space>
                          <span>GPU 索引</span>
                          <Tooltip title="选择要使用的GPU索引，例如 [0] 或 [0,1]">
                            <QuestionCircleOutlined style={{ color: '#999' }} />
                          </Tooltip>
                        </Space>
                      }
                    >
                      <Select
                        mode="multiple"
                        placeholder="选择GPU索引"
                        size="large"
                        style={{ width: '100%' }}
                        options={[
                          { label: 'GPU 0', value: 0 },
                          { label: 'GPU 1', value: 1 },
                          { label: 'GPU 2', value: 2 },
                          { label: 'GPU 3', value: 3 },
                          { label: 'GPU 4', value: 4 },
                          { label: 'GPU 5', value: 5 },
                          { label: 'GPU 6', value: 6 },
                          { label: 'GPU 7', value: 7 },
                        ]}
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  {/* 上下文长度 */}
                  <Col span={12}>
                    <Form.Item
                      name="maxModelLen"
                      label={
                        <Space>
                          <span>上下文长度</span>
                          <Tooltip title="模型能处理的最大token数">
                            <QuestionCircleOutlined style={{ color: '#999' }} />
                          </Tooltip>
                        </Space>
                      }
                      rules={[{ required: true, message: '请设置上下文长度' }]}
                    >
                      <Select size="large">
                        <Option value={2048}>2K (低内存)</Option>
                        <Option value={4096}>4K (标准)</Option>
                        <Option value={8192}>8K (推荐)</Option>
                        <Option value={16384}>16K (长文本)</Option>
                        <Option value={32768}>32K (超长)</Option>
                        <Option value={131072}>128K (极限)</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                </Row>

                {/* GPU内存利用率 */}
                <Form.Item
                  name="gpuMemoryUtilization"
                  label={
                    <Space>
                      <span>GPU 内存利用率</span>
                      <Tooltip title="建议值：小模型(0.9) 大模型(0.85-0.95)">
                        <QuestionCircleOutlined style={{ color: '#999' }} />
                      </Tooltip>
                    </Space>
                  }
                  rules={[{ required: true, message: '请设置GPU内存利用率' }]}
                >
                  <Slider
                    min={0.5}
                    max={0.98}
                    step={0.01}
                    marks={{ 
                      0.5: '50%', 
                      0.7: '70%', 
                      0.85: { label: '85% 推荐', style: { color: '#52c41a' } },
                      0.95: '95%' 
                    }}
                    tooltip={{ formatter: (value) => `${Math.round((value || 0) * 100)}%` }}
                  />
                </Form.Item>
              </div>

              {/* ========== 高级配置区域 ========== */}
              <Collapse
                ghost
                items={[
                  {
                    key: '1',
                    label: (
                      <Space>
                        <SettingOutlined />
                        <span>高级配置</span>
                        <Tag color="blue">可选</Tag>
                      </Space>
                    ),
                    children: (
                      <div style={{ padding: '0 8px' }}>
                        <Row gutter={16}>
                          <Col span={12}>
                            <Form.Item
                              name="dtype"
                              label="数据类型"
                            >
                              <Select>
                                <Option value="auto">自动检测</Option>
                                <Option value="float16">FP16</Option>
                                <Option value="bfloat16">BF16 (推荐)</Option>
                                <Option value="float32">FP32</Option>
                              </Select>
                            </Form.Item>
                          </Col>
                          <Col span={12}>
                            <Form.Item
                              name="kvCacheDtype"
                              label="KV Cache 数据类型"
                            >
                              <Select>
                                <Option value="auto">与模型相同</Option>
                                <Option value="fp8">FP8 (节省显存)</Option>
                                <Option value="fp16">FP16</Option>
                              </Select>
                            </Form.Item>
                          </Col>
                        </Row>

                        <Row gutter={16}>
                          <Col span={12}>
                            <Form.Item
                              name="swapSpace"
                              label="CPU 交换空间 (GB)"
                            >
                              <Slider
                                min={0}
                                max={32}
                                step={1}
                                marks={{ 0: '0', 4: '4G', 16: '16G', 32: '32G' }}
                              />
                            </Form.Item>
                          </Col>
                          <Col span={12}>
                            <Form.Item
                              name="maxNumSeqs"
                              label="最大并发序列数"
                            >
                              <InputNumber min={1} max={1024} style={{ width: '100%' }} />
                            </Form.Item>
                          </Col>
                        </Row>

                        <Row gutter={16}>
                          <Col span={12}>
                            <Form.Item
                              name="enforceEager"
                              valuePropName="checked"
                            >
                              <Switch
                                checkedChildren="启用 Eager 模式"
                                unCheckedChildren="禁用 Eager 模式"
                              />
                            </Form.Item>
                          </Col>
                          <Col span={12}>
                            <Form.Item
                              name="enableChunkedPrefill"
                              valuePropName="checked"
                            >
                              <Switch
                                checkedChildren="启用 Chunked Prefill"
                                unCheckedChildren="禁用 Chunked Prefill"
                                defaultChecked
                              />
                            </Form.Item>
                          </Col>
                        </Row>

                        <Form.Item
                          name="seed"
                          label="随机种子 (0表示随机)"
                        >
                          <InputNumber min={0} style={{ width: '100%' }} />
                        </Form.Item>
                      </div>
                    ),
                  },
                ]}
              />

              <Divider style={{ margin: '16px 0' }} />

              {/* 操作按钮 */}
              <Form.Item style={{ marginBottom: 0 }}>
                <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                  <Button onClick={() => setDeployModalVisible(false)}>
                    取消
                  </Button>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={deploying}
                    disabled={!modelExists || downloading}
                    icon={<ThunderboltOutlined />}
                    size="large"
                  >
                    {modelExists ? '部署模型' : '请先下载模型'}
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </>
        )}
      </Modal>

      {/* 启动日志 Drawer */}
      <Drawer
        title={
          <Space>
            <EyeOutlined />
            <span>模型启动日志</span>
          </Space>
        }
        placement="right"
        width={800}
        onClose={() => setLogDrawerVisible(false)}
        open={logDrawerVisible}
      >
        {deployInstanceId && (
          <ModelLaunchLog
            instanceId={deployInstanceId}
            onClose={() => setLogDrawerVisible(false)}
            onStarted={handleDeploySuccess}
          />
        )}
      </Drawer>
    </div>
  )
}

export default ModelStore
