import { store } from '../store'
import { setUser, setAccessToken, logout } from '../store/slices/authSlice'
import { authService } from './authService'



class AuthInterceptor {
  private isInitialized = false
  private isChecking = false

  async initialize() {
    if (this.isInitialized || this.isChecking) return
    
    this.isChecking = true
    
    try {
      const userInfo = await authService.getCurrentUserWithRefresh()
      store.dispatch(setUser(userInfo))
      store.dispatch(setAccessToken('authenticated'))
    } catch (error) {
      store.dispatch(logout())
    } finally {
      this.isChecking = false
      this.isInitialized = true
    }
  }

  async checkAuthStatus() {
    if (this.isChecking) return
    
    this.isChecking = true
    
    try {
      const userInfo = await authService.getCurrentUserWithRefresh()
      store.dispatch(setUser(userInfo))
      store.dispatch(setAccessToken('authenticated'))
      return true
    } catch (error) {
      store.dispatch(logout())
      return false
    } finally {
      this.isChecking = false
    }
  }

  isAuthenticated(): boolean {
    const state = store.getState()
    return state.auth.isAuthenticated && state.auth.user !== null
  }

  getCurrentUser() {
    const state = store.getState()
    return state.auth.user
  }

  reset() {
    this.isInitialized = false
    this.isChecking = false
  }
}

export const authInterceptor = new AuthInterceptor() 