import axios from 'axios'

const API_BASE = '/api/v1'

// 系统概览
export const getSystemOverview = () => {
  return axios.get(`${API_BASE}/system/overview`)
}

// 用户管理
export const getUsers = () => {
  return axios.get(`${API_BASE}/users`)
}

export const createUser = (data: {
  username: string
  email: string
  password: string
  role: string
}) => {
  return axios.post(`${API_BASE}/users`, data)
}

export const updateUser = (userId: string, data: {
  username?: string
  email?: string
  role?: string
  status?: string
}) => {
  return axios.put(`${API_BASE}/users/${userId}`, data)
}

export const deleteUser = (userId: string) => {
  return axios.delete(`${API_BASE}/users/${userId}`)
}

// 角色管理
export const getRoles = () => {
  return axios.get(`${API_BASE}/roles`)
}

export const createRole = (data: {
  name: string
  description?: string
  permissions: string[]
}) => {
  return axios.post(`${API_BASE}/roles`, data)
}

export const updateRole = (roleId: string, data: {
  name?: string
  description?: string
  permissions?: string[]
}) => {
  return axios.put(`${API_BASE}/roles/${roleId}`, data)
}

export const deleteRole = (roleId: string) => {
  return axios.delete(`${API_BASE}/roles/${roleId}`)
}

// API Key 管理
export const getApiKeys = () => {
  return axios.get(`${API_BASE}/keys`)
}

export const createApiKey = (data: {
  name: string
  permissions: string[]
  expires_at?: string
}) => {
  return axios.post(`${API_BASE}/keys`, data)
}

export const revokeApiKey = (keyId: string) => {
  return axios.delete(`${API_BASE}/keys/${keyId}`)
}

// 系统配置
export const getSystemConfig = () => {
  return axios.get(`${API_BASE}/system/config`)
}

export const updateSystemConfig = (key: string, data: {
  value: string
  description?: string
}) => {
  return axios.put(`${API_BASE}/system/config/${key}`, data)
}

// 系统日志
export const getSystemLogs = (params?: {
  level?: string
  limit?: number
}) => {
  return axios.get(`${API_BASE}/system/logs`, { params })
}
