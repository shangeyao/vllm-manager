import { Layout } from 'antd'

const { Header: AntHeader } = Layout

const Header = () => {
  return (
    <AntHeader style={{
      background: '#fff',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
    }}>
      <div style={{ fontSize: 16, fontWeight: 500, color: '#1f2937' }}>
        工作台
      </div>
    </AntHeader>
  )
}

export default Header
