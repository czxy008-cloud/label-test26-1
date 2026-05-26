import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
  withCredentials: true
})

request.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data && typeof data === 'object' && 'code' in data) {
      if (data.code !== 0) {
        ElMessage.error(data.msg || '请求失败')
        return Promise.reject(data)
      }
      return data
    }
    return data
  },
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        const path = window.location.pathname
        if (path !== '/login' && path !== '/register') {
          localStorage.removeItem('swap_user')
          window.location.href = '/login'
        }
      } else {
        ElMessage.error(error.response.data?.msg || '网络错误')
      }
    } else {
      ElMessage.error('网络连接异常')
    }
    return Promise.reject(error.response?.data || error)
  }
)

export default request
