import apiClient, { AuthResponse, TokenResponse, setTokens, clearTokens } from './client'

// Types
export interface LoginCredentials {
  username: string
  password: string
}

export interface TwoFactorVerification {
  token: string
  code: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
  role: 'diner' | 'restaurant' | 'admin'
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirm {
  token: string
  uid: string
  new_password: string
  new_password_confirm: string
}

export interface CurrentUser {
  id: number
  username: string
  email: string
  role: 'diner' | 'restaurant' | 'admin'
  profile: {
    is_approved?: boolean
    is_rejected?: boolean
    is_flagged?: boolean
  }
}

// Auth API endpoints
export const authApi = {
  // Login - returns temporary token that needs 2FA verification
  login: async (credentials: LoginCredentials): Promise<{ session_token: string; requires_2fa: boolean }> => {
    const { data } = await apiClient.post('/api/auth/login/', credentials)
    return data
  },

  // Verify 2FA code
  verify2FA: async (verification: TwoFactorVerification): Promise<AuthResponse> => {
    const { data } = await apiClient.post('/api/auth/verify-2fa/', verification)
    setTokens(data.access, data.refresh)
    return data
  },

  // Register new user
  register: async (userData: RegisterData): Promise<AuthResponse> => {
    const { data } = await apiClient.post('/api/auth/register/', userData)
    setTokens(data.access, data.refresh)
    return data
  },

  // Get current user info
  getCurrentUser: async (): Promise<CurrentUser> => {
    const { data } = await apiClient.get('/api/auth/user/')
    return data
  },

  // Refresh access token
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const { data } = await apiClient.post('/api/auth/token/refresh/', {
      refresh: refreshToken,
    })
    return data
  },

  // Logout
  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/api/auth/logout/')
    } finally {
      clearTokens()
    }
  },

  // Request password reset
  requestPasswordReset: async (email: string): Promise<{ detail: string }> => {
    const { data } = await apiClient.post('/api/auth/password-reset/', { email })
    return data
  },

  // Confirm password reset
  confirmPasswordReset: async (resetData: PasswordResetConfirm): Promise<{ detail: string }> => {
    const { data } = await apiClient.post('/api/auth/password-reset-confirm/', resetData)
    return data
  },

  // Verify token validity
  verifyToken: async (): Promise<{ valid: boolean }> => {
    try {
      await apiClient.get('/api/auth/verify-token/')
      return { valid: true }
    } catch {
      return { valid: false }
    }
  },
}

export default authApi
