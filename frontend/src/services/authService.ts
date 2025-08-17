const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL || 'http://localhost:3000'
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '105760145216-7ub4ppuqp57j6anc608t3ke2r0pmk1md.apps.googleusercontent.com'

export const authService = {
  getGoogleLoginUrl: () => {
    const clientId = '105760145216-7ub4ppuqp57j6anc608t3ke2r0pmk1md.apps.googleusercontent.com'
    const redirectUri = `${BACKEND_URL}/auth/google/callback`
    const scope = 'email profile openid'
    
    return `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scope}&access_type=offline&prompt=consent&state=${encodeURIComponent(FRONTEND_URL)}`
  },

  getCurrentUser: async () => {
    const accessToken = localStorage.getItem('access_token')
    if (!accessToken) {
      throw new Error('No access token found')
    }

    const response = await fetch(`${BACKEND_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error('Failed to get user info')
    }
    return response.json()
  },

  logout: async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      return { message: 'No refresh token found' }
    }

    const response = await fetch(`${BACKEND_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    })
    
    if (!response.ok) {
      throw new Error('Logout failed')
    }
    return response.json()
  }
} 