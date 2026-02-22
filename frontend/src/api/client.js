import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Silent token refresh on 401
let refreshing = false
let refreshSubscribers = []

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb)
}

function onRefreshed(token) {
  refreshSubscribers.forEach((cb) => cb(token))
  refreshSubscribers = []
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    // Skip token refresh for auth token endpoints or when no token exists (e.g. failed login)
    const isTokenEndpoint = original.url?.includes('/auth/token/')
    const hasAccessToken = !!localStorage.getItem('access_token')
    if (error.response?.status === 401 && !original._retry && !isTokenEndpoint && hasAccessToken) {
      original._retry = true
      if (!refreshing) {
        refreshing = true
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(error)
        }
        try {
          const base = import.meta.env.VITE_API_BASE_URL || '/api/v1'
          const { data } = await axios.post(`${base}/auth/token/refresh/`, { refresh })
          localStorage.setItem('access_token', data.access)
          if (data.refresh) localStorage.setItem('refresh_token', data.refresh)
          onRefreshed(data.access)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(error)
        } finally {
          refreshing = false
        }
      }
      return new Promise((resolve) => {
        subscribeTokenRefresh((token) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(client(original))
        })
      })
    }
    return Promise.reject(error)
  },
)

export default client
