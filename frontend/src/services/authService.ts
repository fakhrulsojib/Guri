const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL || 'http://localhost:3000'
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '105760145216-7ub4ppuqp57j6anc608t3ke2r0pmk1md.apps.googleusercontent.com'

import { csrfService } from './csrfService'

export const authService = {
  getGoogleLoginUrl: () => {
    const clientId = '105760145216-7ub4ppuqp57j6anc608t3ke2r0pmk1md.apps.googleusercontent.com'
    const redirectUri = `${BACKEND_URL}/auth/google/callback`
    const scope = 'email profile openid'
    
    return `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&access_type=offline&prompt=consent&state=${encodeURIComponent(FRONTEND_URL)}`
  },

  getCurrentUser: async () => {
    const response = await fetch(`${BACKEND_URL}/auth/me`, {
      credentials: 'include'
    })
    
    if (!response.ok) {
      throw new Error('Failed to get user info')
    }
    return response.json()
  },

  getCurrentUserWithRefresh: async () => {
    try {
      return await authService.getCurrentUser()
    } catch (error) {
      if (error.message === 'Failed to get user info') {
        await authService.refreshToken()
        return await authService.getCurrentUser()
      }
      throw error
    }
  },

  logout: async () => {
    const headers = await csrfService.getHeaders()
    const response = await fetch(`${BACKEND_URL}/auth/logout`, {
      method: 'POST',
      headers,
      credentials: 'include'
    })
    
    if (!response.ok) {
      if (response.status === 403) {
        await csrfService.handleCSRFError()
        return authService.logout()
      }
      throw new Error('Logout failed')
    }
    return response.json()
  },

  refreshToken: async () => {
    const headers = await csrfService.getHeaders()
    const response = await fetch(`${BACKEND_URL}/auth/refresh`, {
      method: 'POST',
      headers,
      credentials: 'include'
    })
    
    if (!response.ok) {
      if (response.status === 403) {
        await csrfService.handleCSRFError()
        return authService.refreshToken()
      }
      throw new Error('Token refresh failed')
    }
    return response.json()
  }
} 