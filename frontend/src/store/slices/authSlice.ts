import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { User, AuthState } from '../../types'

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  accessToken: null,
  isLoading: false
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
    },
    setAccessToken: (state, action: PayloadAction<string>) => {
      state.accessToken = action.payload
    },
    logout: (state) => {
      state.user = null
      state.isAuthenticated = false
      state.accessToken = null
    }
  }
})

export const { setLoading, setUser, setAccessToken, logout } = authSlice.actions
export default authSlice.reducer 