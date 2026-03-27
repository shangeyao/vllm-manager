import { Layout } from 'antd'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import ModelStore from './pages/ModelStore'
import ModelRegister from './pages/ModelRegister'
import ModelInstances from './pages/ModelInstances'
import DeviceInfo from './pages/DeviceInfo'
import ModelStats from './pages/ModelStats'
import SystemManagement from './pages/SystemManagement'
import './App.css'

const { Content } = Layout

function App() {
  return (
    <BrowserRouter>
      <Layout style={{ minHeight: '100vh' }}>
        <Sidebar />
        <Layout>
          <Header />
          <Content style={{ margin: '24px', background: '#f5f5f5' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/models/store" element={<ModelStore />} />
              <Route path="/models/register" element={<ModelRegister />} />
              <Route path="/models/instances" element={<ModelInstances />} />
              <Route path="/devices" element={<DeviceInfo />} />
              <Route path="/models/stats" element={<ModelStats />} />
              <Route path="/system" element={<SystemManagement />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </BrowserRouter>
  )
}

export default App
