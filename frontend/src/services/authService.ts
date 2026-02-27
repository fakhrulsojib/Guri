const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://fakhrulsojib.mooo.com'
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '105760145216-7ub4ppuqp57j6anc608t3ke2r0pmk1md.apps.googleusercontent.com'

import { csrfService } from './csrfService'

let refreshInFlight: Promise<any> | null = null
let getCurrentUserInFlight: Promise<any> | null = null

export const authService = {
  apiCallWithRetry: async <T>(
    apiCall: () => Promise<T>,
    retryCount: number = 1
  ): Promise<T> => {
    try {
      return await apiCall()
    } catch (error: any) {
      if (error.message === 'Unauthorized' && retryCount > 0) {
        try {
          await authService.refreshToken()
          return await apiCall()
        } catch (refreshError) {
          throw refreshError
        }
      }
      throw error
    }
  },

  getGoogleLoginUrl: () => {
    const clientId = GOOGLE_CLIENT_ID
    const redirectUri = `${VITE_BACKEND_URL}/auth/google/callback`
    const scope = 'email profile openid'

    return `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&scope=${encodeURIComponent(scope)}&access_type=offline&prompt=consent&state=${encodeURIComponent(window.location.origin)}`
  },

  getCurrentUser: async () => {
    if (getCurrentUserInFlight) {
      return getCurrentUserInFlight
    }

    getCurrentUserInFlight = (async () => {
      try {
        const response = await fetch(`/auth/me`, {
          credentials: 'include'
        })

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Unauthorized')
          }
          throw new Error('Failed to get user info')
        }
        const userData = await response.json()
        return userData
      } finally {
        getCurrentUserInFlight = null
      }
    })()

    return getCurrentUserInFlight
  },

  getCurrentUserWithRefresh: async () => {
    return authService.apiCallWithRetry(async () => {
      return await authService.getCurrentUser()
    })
  },

  logout: async () => {
    try {
      const headers = await csrfService.getHeaders()
      const response = await fetch(`/auth/logout`, {
        method: 'POST',
        headers,
        credentials: 'include'
      })

      if (!response.ok) {
        if (response.status === 403) {
          await csrfService.handleCSRFError()
          const retryHeaders = await csrfService.getHeaders()
          const retryResponse = await fetch(`/auth/logout`, {
            method: 'POST',
            headers: retryHeaders,
            credentials: 'include'
          })
          if (!retryResponse.ok) {
            throw new Error('Logout failed after CSRF retry')
          }
          return retryResponse.json()
        }
        throw new Error('Logout failed')
      }
      return response.json()
    } catch (error) {
      if (error instanceof Error && error.message === 'Failed to fetch CSRF token') {
        const response = await fetch(`/auth/logout`, {
          method: 'POST',
          credentials: 'include'
        })
        if (!response.ok) {
          throw new Error('Logout failed')
        }
        return response.json()
      }
      throw new Error('Logout failed')
    }
  },

  refreshToken: async () => {
    if (refreshInFlight) {
      return refreshInFlight
    }

    refreshInFlight = (async () => {
      const headers = await csrfService.getHeaders()
      const response = await fetch(`/auth/refresh`, {
        method: 'POST',
        headers,
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }
      const result = await response.json()
      return result
    })()

    try {
      return await refreshInFlight
    } finally {
      refreshInFlight = null
    }
  }
} 