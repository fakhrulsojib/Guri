import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { User, AuthState } from '../../types'

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  accessToken: null,
  isLoading: false,
  lastUpdate: Date.now()
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
      state.isAuthenticated = true
      state.lastUpdate = Date.now()
    },
    setAccessToken: (state, action: PayloadAction<string>) => {
      state.accessToken = action.payload
    },
    logout: () => {
      return {
        ...initialState,
        lastUpdate: Date.now()
      }
    }
  }
})

export const { setLoading, setUser, setAccessToken, logout } = authSlice.actions
export default authSlice.reducer 