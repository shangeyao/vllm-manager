import { Layout, Menu, Avatar } from 'antd'
import {
  DashboardOutlined,
  AppstoreOutlined,
  PlusOutlined,
  ContainerOutlined,
  DesktopOutlined,
  SettingOutlined,
  BarChartOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Sider } = Layout

const Sidebar = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '工作台',
    },
    {
      key: 'models',
      icon: <AppstoreOutlined />,
      label: '模型管理',
      children: [
        {
          key: '/models/store',
          icon: <AppstoreOutlined />,
          label: '模型仓库',
        },
        {
          key: '/models/register',
          icon: <PlusOutlined />,
          label: '模型注册',
        },
        {
          key: '/models/instances',
          icon: <ContainerOutlined />,
          label: '模型实例',
        },
        {
          key: '/models/stats',
          icon: <BarChartOutlined />,
          label: '模型统计',
        },
      ],
    },
    {
      key: 'monitor',
      icon: <DesktopOutlined />,
      label: '监控中心',
      children: [
        {
          key: '/devices',
          icon: <DesktopOutlined />,
          label: '设备信息',
        },
      ],
    },
    {
      key: '/system',
      icon: <SettingOutlined />,
      label: '系统管理',
    },
  ]

  const getSelectedKey = () => {
    const path = location.pathname
    if (path === '/') return ['/']
    return [path]
  }

  const getOpenKeys = () => {
    const path = location.pathname
    if (path.startsWith('/models')) return ['models']
    if (path === '/devices') return ['monitor']
    return []
  }

  return (
    <Sider width={240} theme="light" style={{ boxShadow: '2px 0 8px rgba(0,0,0,0.06)' }}>
      <div style={{ padding: '16px 24px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <img src="/vllm-logo-only.png" alt="vLLM" style={{ width: 32, height: 32 }} />
        <span style={{ fontSize: 18, fontWeight: 600, color: '#1f2937' }}>vLLM</span>
      </div>
      <Menu
        mode="inline"
        selectedKeys={getSelectedKey()}
        defaultOpenKeys={getOpenKeys()}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        style={{ borderRight: 'none' }}
      />
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '16px 24px',
        borderTop: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
      }}>
        <Avatar icon={<UserOutlined />} style={{ background: '#7c3aed' }} />
        <div>
          <div style={{ fontSize: 14, fontWeight: 500, color: '#1f2937' }}>管理员</div>
          <div style={{ fontSize: 12, color: '#6b7280' }}>admin@vllm.io</div>
        </div>
      </div>
    </Sider>
  )
}

export default Sidebar
