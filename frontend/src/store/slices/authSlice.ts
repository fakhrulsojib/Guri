import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { User, AuthState } from '../../types/auth'

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
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
    logout: (state) => {
      state.user = null
      state.isAuthenticated = false
    }
  }
})

export const { setLoading, setUser, logout } = authSlice.actions
export default authSlice.reducer 