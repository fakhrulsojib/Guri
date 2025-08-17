import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface User {
  id: string
  email: string
  email_verified: boolean
  name: string
  given_name: string
  family_name: string
  picture: string
  locale: string
  hd: string
  is_active: boolean
  created_at: string
  last_login: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  accessToken: string | null
  refreshToken: string | null
  isLoading: boolean
}

const getInitialAuthState = (): AuthState => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('auth')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch {
        return {
          user: null,
          isAuthenticated: false,
          accessToken: null,
          refreshToken: null,
          isLoading: false
        }
      }
    }
  }
  return {
    user: null,
    isAuthenticated: false,
    accessToken: null,
    refreshToken: null,
    isLoading: false
  }
}

const authSlice = createSlice({
  name: 'auth',
  initialState: getInitialAuthState(),
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
      localStorage.setItem('auth', JSON.stringify(state))
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
      state.isAuthenticated = true
      localStorage.setItem('auth', JSON.stringify(state))
    },
    setTokens: (state, action: PayloadAction<{ accessToken: string; refreshToken: string }>) => {
      state.accessToken = action.payload.accessToken
      state.refreshToken = action.payload.refreshToken
      localStorage.setItem('auth', JSON.stringify(state))
    },
    logout: (state) => {
      state.user = null
      state.isAuthenticated = false
      state.accessToken = null
      state.refreshToken = null
      localStorage.removeItem('auth')
    }
  }
})

export const { setLoading, setUser, setTokens, logout } = authSlice.actions
export default authSlice.reducer 