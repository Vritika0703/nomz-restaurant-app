import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

// Types
export interface ApiError {
  message: string
  code?: string
  status?: number
  details?: Record<string, unknown>
}

export interface TokenResponse {
  access: string
  refresh: string
}

export interface AuthResponse extends TokenResponse {
  user: {
    id: number
    username: string
    email: string
    role: 'diner' | 'restaurant' | 'admin'
  }
}

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token management functions
export const getAccessToken = (): string | null => localStorage.getItem(TOKEN_KEY)
export const getRefreshToken = (): string | null => localStorage.getItem(REFRESH_TOKEN_KEY)

export const setTokens = (access: string, refresh: string): void => {
  localStorage.setItem(TOKEN_KEY, access)
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
}

export const clearTokens = (): void => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

// Request interceptor - add auth header
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle token refresh
let isRefreshing = false
let failedQueue: Array<{ resolve: Function; reject: Function }> = []

const processQueue = (error: AxiosError | null, token: string | null = null): void => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return apiClient(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      isRefreshing = true
      originalRequest._retry = true

      try {
        const refreshToken = getRefreshToken()
        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        const { data } = await axios.post<TokenResponse>(`${API_BASE_URL}/api/auth/token/refresh/`, {
          refresh: refreshToken,
        })

        setTokens(data.access, data.refresh)
        apiClient.defaults.headers.common.Authorization = `Bearer ${data.access}`
        originalRequest.headers.Authorization = `Bearer ${data.access}`

        processQueue(null, data.access)
        return apiClient(originalRequest)
      } catch (err) {
        processQueue(err as AxiosError)
        clearTokens()
        // Redirect to login
        window.location.href = '/login'
        return Promise.reject(err)
      } finally {
        isRefreshing = false
      }
    }

    // Transform error for consistent handling
    const apiError: ApiError = {
      message: error.response?.data?.detail || error.message || 'An error occurred',
      code: error.code,
      status: error.response?.status,
      details: error.response?.data,
    }

    return Promise.reject(apiError)
  }
)

export default apiClient
