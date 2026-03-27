import { useState } from 'react'
import {
  Card,
  Tabs,
  Form,
  Input,
  Select,
  Radio,
  Button,
  Row,
  Col,
  Typography,
  Space,
  Collapse,
  Tag,
  Tooltip,
  message,
} from 'antd'
import {
  CopyOutlined,
  PlusOutlined,
  MinusCircleOutlined,
} from '@ant-design/icons'

const { Title, Text } = Typography
const { TextArea } = Input

const modelTypes = [
  { key: 'llm', label: '大语言模型' },
  { key: 'image', label: '图像模型' },
  { key: 'embedding', label: 'Embedding' },
  { key: 'rerank', label: 'Rerank' },
  { key: 'audio', label: '音频模型' },
  { key: 'other', label: '其他模型' },
]

const modelFormats = [
  { value: 'pytorch', label: 'PyTorch' },
  { value: 'gguf', label: 'GGUF' },
  { value: 'gptq', label: 'GPTQ' },
  { value: 'awq', label: 'AWQ' },
  { value: 'fp8', label: 'FP8' },
  { value: 'mlx', label: 'MLX' },
]

const ModelRegister = () => {
  const [activeTab, setActiveTab] = useState('llm')
  const [form] = Form.useForm()
  const [jsonPreview, setJsonPreview] = useState<any>({
    model_name: 'custom-llm',
    model_description: 'This is a model description.',
    virtualenv: { packages: [] },
    context_length: 2048,
    model_lang: ['en'],
    model_ability: ['generate'],
    model_family: '',
    model_specs: [{
      model_uri: '/path/to/llama-2',
      model_size_in_billions: '7',
      model_format: 'pytorch',
      quantization: 'none',
    }],
    chat_template: '',
    stop_token_ids: [],
    stop: [],
  })

  const handleFormChange = () => {
    const values = form.getFieldsValue()
    setJsonPreview({
      ...jsonPreview,
      model_name: values.modelName || 'custom-llm',
      model_description: values.description || 'This is a model description.',
      context_length: values.contextLength || 2048,
      model_lang: values.language || ['en'],
      model_ability: values.abilities || ['generate'],
      model_specs: [{
        model_uri: values.modelPath || '/path/to/llama-2',
        model_size_in_billions: values.modelSize || '7',
        model_format: values.modelFormat || 'pytorch',
        quantization: values.quantization || 'none',
      }],
    })
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      console.log('Form values:', values)
      message.success('模型注册成功！')
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  const copyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(jsonPreview, null, 2))
    message.success('JSON 已复制到剪贴板')
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginBottom: 4 }}>模型注册</Title>
        <Text type="secondary">注册自定义模型到平台</Text>
      </div>

      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={modelTypes.map((type) => ({
            key: type.key,
            label: type.label,
          }))}
          style={{ marginBottom: 24 }}
        />

        <Row gutter={24}>
          <Col xs={24} lg={16}>
            <Form
              form={form}
              layout="vertical"
              onValuesChange={handleFormChange}
              initialValues={{
                modelName: 'custom-llm',
                description: 'This is a model description.',
                contextLength: 2048,
                language: ['English'],
                abilities: ['Generate'],
                modelFormat: 'pytorch',
                modelPath: '/path/to/llama-2',
                modelSize: '7',
              }}
            >
              {/* 基础信息 */}
              <div style={{ marginBottom: 24 }}>
                <Title level={5} style={{ marginBottom: 16 }}>基础信息</Title>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="模型名称"
                      name="modelName"
                      rules={[{ required: true, message: '请输入模型名称' }]}
                      tooltip="模型名称需唯一，用于标识模型"
                    >
                      <Input placeholder="请输入模型名称" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="模型描述"
                      name="description"
                    >
                      <Input placeholder="请输入模型描述" />
                    </Form.Item>
                  </Col>
                </Row>
              </div>

              {/* 类型配置 */}
              <div style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
                  <Title level={5} style={{ margin: 0, marginRight: 8 }}>类型配置</Title>
                  <Tag color="purple">大语言模型</Tag>
                </div>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="上下文长度"
                      name="contextLength"
                      rules={[{ required: true, message: '请输入上下文长度' }]}
                    >
                      <Input type="number" placeholder="请输入上下文长度" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="模型系列"
                      name="modelFamily"
                      rules={[{ required: true, message: '请选择或输入模型系列' }]}
                    >
                      <Select
                        placeholder="选择或输入模型系列"
                        allowClear
                        showSearch
                        options={[
                          { value: 'llama', label: 'LLaMA' },
                          { value: 'qwen', label: 'Qwen' },
                          { value: 'baichuan', label: 'Baichuan' },
                          { value: 'chatglm', label: 'ChatGLM' },
                        ]}
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="模型语言"
                      name="language"
                      rules={[{ required: true, message: '请选择模型语言' }]}
                    >
                      <Radio.Group>
                        <Radio value="English">English</Radio>
                        <Radio value="Chinese">Chinese</Radio>
                      </Radio.Group>
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="模型能力"
                      name="abilities"
                      rules={[{ required: true, message: '请选择模型能力' }]}
                    >
                      <Radio.Group>
                        <Radio value="Generate">Generate</Radio>
                        <Radio value="Chat">Chat</Radio>
                        <Radio value="Vision">Vision</Radio>
                        <Radio value="Tools">Tools</Radio>
                      </Radio.Group>
                    </Form.Item>
                  </Col>
                </Row>
              </div>

              {/* 模型规格 */}
              <div style={{ marginBottom: 24 }}>
                <Title level={5} style={{ marginBottom: 16 }}>模型规格</Title>
                <Form.List name="specs">
                  {(fields, { add, remove }) => (
                    <>
                      {fields.map(({ key, name, ...restField }) => (
                        <Card
                          key={key}
                          size="small"
                          title={`规格 #${name + 1}`}
                          extra={
                            fields.length > 1 && (
                              <MinusCircleOutlined onClick={() => remove(name)} />
                            )
                          }
                          style={{ marginBottom: 16 }}
                        >
                          <Form.Item
                            {...restField}
                            name={[name, 'modelFormat']}
                            label="模型格式"
                          >
                            <Radio.Group>
                              {modelFormats.map((format) => (
                                <Radio key={format.value} value={format.value}>
                                  {format.label}
                                </Radio>
                              ))}
                            </Radio.Group>
                          </Form.Item>
                          <Row gutter={16}>
                            <Col span={12}>
                              <Form.Item
                                {...restField}
                                name={[name, 'modelPath']}
                                label="模型路径"
                              >
                                <Input placeholder="请输入模型路径" />
                              </Form.Item>
                            </Col>
                            <Col span={12}>
                              <Form.Item
                                {...restField}
                                name={[name, 'modelSize']}
                                label="模型大小 (B)"
                              >
                                <Input placeholder="请输入模型大小" />
                              </Form.Item>
                            </Col>
                          </Row>
                        </Card>
                      ))}
                      <Button
                        type="dashed"
                        onClick={() => add()}
                        block
                        icon={<PlusOutlined />}
                      >
                        添加规格
                      </Button>
                    </>
                  )}
                </Form.List>
              </div>

              {/* 高级配置 */}
              <Collapse
                ghost
                style={{ marginBottom: 24 }}
                items={[
                  {
                    key: '1',
                    label: '高级配置',
                    children: (
                      <>
                        <Form.Item label="Chat Template" name="chatTemplate">
                          <TextArea rows={4} placeholder="请输入 Chat Template" />
                        </Form.Item>
                        <Form.Item label="Stop Token IDs" name="stopTokenIds">
                          <Select mode="tags" placeholder="输入 Stop Token IDs" />
                        </Form.Item>
                        <Form.Item label="Stop Words" name="stopWords">
                          <Select mode="tags" placeholder="输入 Stop Words" />
                        </Form.Item>
                      </>
                    ),
                  },
                ]}
              />

              {/* 操作按钮 */}
              <Form.Item>
                <Space>
                  <Button>取消</Button>
                  <Button type="primary" onClick={handleSubmit} icon={<PlusOutlined />}>
                    注册模型
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Col>

          {/* JSON 预览 */}
          <Col xs={24} lg={8}>
            <Card
              title="JSON 预览"
              extra={
                <Tooltip title="复制 JSON">
                  <Button type="text" icon={<CopyOutlined />} onClick={copyJson} />
                </Tooltip>
              }
              style={{ background: '#f8fafc' }}
            >
              <pre style={{
                margin: 0,
                padding: 16,
                background: '#1e293b',
                borderRadius: 8,
                color: '#e2e8f0',
                fontSize: 12,
                overflow: 'auto',
                maxHeight: 600,
              }}>
                {JSON.stringify(jsonPreview, null, 2)}
              </pre>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  )
}

export default ModelRegister
