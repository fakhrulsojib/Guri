const BACKEND_URL = '' // use same-origin via Vite proxy in dev
const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL || 'http://localhost:3000'
const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '105760145216-7ub4ppuqp57j6anc608t3ke2r0pmk1md.apps.googleusercontent.com'

import { csrfService } from './csrfService'

let refreshInFlight: Promise<any> | null = null
let getCurrentUserInFlight: Promise<any> | null = null

export const authService = {
  getGoogleLoginUrl: () => {
    const clientId = GOOGLE_CLIENT_ID
    const redirectUri = `${VITE_BACKEND_URL}/auth/google/callback` // backend callback URL
    const scope = 'email profile openid'
    
    return `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&scope=${encodeURIComponent(scope)}&access_type=offline&prompt=consent&state=${encodeURIComponent(FRONTEND_URL)}`
  },

  getCurrentUser: async () => {
    if (getCurrentUserInFlight) {
      return getCurrentUserInFlight
    }

    getCurrentUserInFlight = (async () => {
      try {
        console.log('Fetching current user from /auth/me')
        const response = await fetch(`/auth/me`, {
          credentials: 'include'
        })
        
        if (!response.ok) {
          console.error('Failed to get user info, status:', response.status)
          throw new Error('Failed to get user info')
        }
        const userData = await response.json()
        console.log('User data received:', userData)
        return userData
      } finally {
        getCurrentUserInFlight = null
      }
    })()

    return getCurrentUserInFlight
  },

  getCurrentUserWithRefresh: async () => {
    try {
      return await authService.getCurrentUser()
    } catch (error: any) {
      console.log('getCurrentUser failed, attempting token refresh:', error.message)
      if (error.message === 'Failed to get user info') {
        await authService.refreshToken()
        return await authService.getCurrentUser()
      }
      throw error
    }
  },

  logout: async () => {
    const headers = await csrfService.getHeaders()
    const response = await fetch(`/auth/logout`, {
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
    if (refreshInFlight) {
      return refreshInFlight
    }

    refreshInFlight = (async () => {
      console.log('Attempting to refresh access token')
      const headers = await csrfService.getHeaders()
      const response = await fetch(`/auth/refresh`, {
        method: 'POST',
        headers,
        credentials: 'include'
      })
      
      if (!response.ok) {
        console.error('Token refresh failed, status:', response.status)
        if (response.status === 403) {
          await csrfService.handleCSRFError()
          const retryHeaders = await csrfService.getHeaders()
          const retryResp = await fetch(`/auth/refresh`, {
            method: 'POST',
            headers: retryHeaders,
            credentials: 'include'
          })
          if (!retryResp.ok) {
            throw new Error('Token refresh failed')
          }
          const retryResult = await retryResp.json()
          console.log('Token refresh successful (after retry):', retryResult)
          return retryResult
        }
        throw new Error('Token refresh failed')
      }
      const result = await response.json()
      console.log('Token refresh successful:', result)
      return result
    })()

    try {
      return await refreshInFlight
    } finally {
      refreshInFlight = null
    }
  }
} 