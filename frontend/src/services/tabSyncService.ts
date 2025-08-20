import { store } from '../store'
import { setUser, setAccessToken, logout } from '../store/slices/authSlice'

interface AuthMessage {
  type: 'AUTH_STATE' | 'LOGOUT'
  payload?: {
    user: any
    isAuthenticated: boolean
  }
}

class TabSyncService {
  private channel: BroadcastChannel | null = null
  private isInitialized = false

  initialize() {
    if (this.isInitialized || !window.BroadcastChannel) return

    this.channel = new BroadcastChannel('auth_channel')
    this.setupMessageListener()
    this.isInitialized = true
  }

  private setupMessageListener() {
    if (!this.channel) return

    this.channel.addEventListener('message', (event) => {
      const message: AuthMessage = event.data
      
      switch (message.type) {
        case 'AUTH_STATE':
          if (message.payload?.isAuthenticated && message.payload?.user) {
            store.dispatch(setUser(message.payload.user))
            store.dispatch(setAccessToken('authenticated'))
          }
          break
        case 'LOGOUT':
          store.dispatch(logout())
          break
      }
    })
  }

  broadcastAuthState(user: any, isAuthenticated: boolean) {
    if (!this.channel || !isAuthenticated) return

    const message: AuthMessage = {
      type: 'AUTH_STATE',
      payload: { user, isAuthenticated }
    }
    
    this.channel.postMessage(message)
  }

  broadcastLogout() {
    if (!this.channel) return

    const message: AuthMessage = { type: 'LOGOUT' }
    this.channel.postMessage(message)
  }

  cleanup() {
    if (this.channel) {
      this.channel.close()
      this.channel = null
    }
    this.isInitialized = false
  }
}

export const tabSyncService = new TabSyncService() 