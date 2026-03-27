import { Form, Select, InputNumber, Switch, Input, Tooltip, Space, Typography } from 'antd'
import { QuestionCircleOutlined } from '@ant-design/icons'
import { VLLM_PARAMS, getParamsByCategory, PARAM_CATEGORIES } from '../config/vllmParams'

const { Text } = Typography
const { Option } = Select

interface VLLMParamsFormProps {
  form: any
}

const VLLMParamsForm = (_props: VLLMParamsFormProps) => {
  // 渲染单个参数表单项
  const renderParamField = (paramName: string) => {
    const param = VLLM_PARAMS[paramName]
    if (!param) return null

    const label = (
      <Space>
        <span>{param.description}</span>
        <Tooltip title={`参数名: ${param.name}`}>
          <QuestionCircleOutlined style={{ color: '#999' }} />
        </Tooltip>
      </Space>
    )

    switch (param.type) {
      case 'int':
        return (
          <Form.Item
            key={param.name}
            name={param.name}
            label={label}
            initialValue={param.default}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={param.min}
              max={param.max}
              placeholder={`默认值: ${param.default ?? '无'}`}
            />
          </Form.Item>
        )

      case 'float':
        return (
          <Form.Item
            key={param.name}
            name={param.name}
            label={label}
            initialValue={param.default}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={param.min}
              max={param.max}
              step={0.1}
              placeholder={`默认值: ${param.default ?? '无'}`}
            />
          </Form.Item>
        )

      case 'bool':
        return (
          <Form.Item
            key={param.name}
            name={param.name}
            valuePropName="checked"
            initialValue={param.default}
          >
            <Switch
              checkedChildren="启用"
              unCheckedChildren="禁用"
            />
          </Form.Item>
        )

      case 'select':
        return (
          <Form.Item
            key={param.name}
            name={param.name}
            label={label}
            initialValue={param.default}
          >
            <Select
              allowClear
              placeholder={`默认值: ${param.default ?? '无'}`}
            >
              {param.choices?.map((choice) => (
                <Option key={choice} value={choice}>
                  {choice}
                </Option>
              ))}
            </Select>
          </Form.Item>
        )

      case 'str':
        return (
          <Form.Item
            key={param.name}
            name={param.name}
            label={label}
            initialValue={param.default}
          >
            <Input placeholder={`默认值: ${param.default ?? '无'}`} />
          </Form.Item>
        )

      default:
        return null
    }
  }

  // 渲染参数分类
  const renderCategory = (categoryKey: string, categoryLabel: string) => {
    const params = getParamsByCategory(categoryKey)
    if (params.length === 0) return null

    return (
      <div key={categoryKey} style={{ marginBottom: 24 }}>
        <Text strong style={{ fontSize: 16, display: 'block', marginBottom: 16 }}>
          {categoryLabel}
        </Text>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px 24px' }}>
          {params.map((param) => renderParamField(param.name))}
        </div>
      </div>
    )
  }

  return (
    <div>
      {PARAM_CATEGORIES.map((cat) => renderCategory(cat.key, cat.label))}
    </div>
  )
}

export default VLLMParamsForm
