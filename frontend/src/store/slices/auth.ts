import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from './index'

export interface User {
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

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  requires2FA: boolean
  sessionToken: string | null
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  requires2FA: false,
  sessionToken: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Login initial
    loginStart: (state) => {
      state.isLoading = true
      state.error = null
    },
    loginRequires2FA: (state, action: PayloadAction<string>) => {
      state.isLoading = false
      state.requires2FA = true
      state.sessionToken = action.payload
    },
    // Login success
    loginSuccess: (state, action: PayloadAction<User>) => {
      state.isLoading = false
      state.isAuthenticated = true
      state.user = action.payload
      state.error = null
      state.requires2FA = false
      state.sessionToken = null
    },
    // Login failure
    loginFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false
      state.error = action.payload
      state.requires2FA = false
      state.sessionToken = null
    },
    // Set user (from API response)
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
      state.isAuthenticated = true
    },
    // Logout
    logout: (state) => {
      state.user = null
      state.isAuthenticated = false
      state.error = null
      state.requires2FA = false
      state.sessionToken = null
    },
    // Clear error
    clearError: (state) => {
      state.error = null
    },
  },
})

export const { loginStart, loginRequires2FA, loginSuccess, loginFailure, setUser, logout, clearError } =
  authSlice.actions

export const selectAuth = (state: RootState) => state.auth
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated
export const selectUser = (state: RootState) => state.auth.user

export default authSlice.reducer
