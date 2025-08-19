const BACKEND_URL = '' // same-origin via Vite proxy
const CSRF_ENDPOINT = import.meta.env.VITE_CSRF_ENDPOINT || '/api/v1/health'

class CSRFService {
  private csrfToken: string | null = null
  private isRefreshing = false

  async getToken(): Promise<string> {
    if (this.csrfToken && !this.isRefreshing) {
      return this.csrfToken
    }

    if (this.isRefreshing) {
      await this.waitForToken()
      return this.csrfToken!
    }

    return this.refreshToken()
  }

  // Check if we have a valid token without fetching
  hasValidToken(): boolean {
    return this.csrfToken !== null && !this.isRefreshing
  }

  // Check if token is still valid (not expired)
  private isTokenValid(): boolean {
    if (!this.csrfToken) return false
    
    // For development, assume token is valid for 5 minutes
    // In production, you might want to check actual expiration
    return true
  }

  private async refreshToken(): Promise<string> {
    this.isRefreshing = true
    
    try {
      console.log('Fetching CSRF token from:', CSRF_ENDPOINT)
      const response = await fetch(`${CSRF_ENDPOINT}`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        console.error('CSRF endpoint returned error:', response.status, response.statusText)
        throw new Error(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
      }
      
      const token = response.headers.get('X-CSRF-Token')
      if (!token) {
        console.warn('No CSRF token in response headers, using fallback')
        // Use a fallback token for development
        this.csrfToken = 'dev-csrf-token'
        return this.csrfToken
      }
      
      this.csrfToken = token
      console.log('CSRF token obtained successfully')
      
      // Set a timeout to clear the token after 5 minutes (development)
      setTimeout(() => {
        console.log('CSRF token expired, clearing...')
        this.csrfToken = null
      }, 5 * 60 * 1000) // 5 minutes
      
      return token
    } catch (error) {
      console.error('Failed to refresh CSRF token:', error)
      // Use fallback token for development
      this.csrfToken = 'dev-csrf-token'
      return this.csrfToken
    } finally {
      this.isRefreshing = false
    }
  }

  private async waitForToken(): Promise<void> {
    while (this.isRefreshing) {
      await new Promise(resolve => setTimeout(resolve, 50))
    }
  }

  async getHeaders(baseHeaders: Record<string, string> = {}): Promise<Record<string, string>> {
    console.log('getHeaders called - checking if we need to fetch CSRF token...')
    const token = await this.getToken()
    return {
      ...baseHeaders,
      'X-CSRF-Token': token
    }
  }

  clearToken(): void {
    this.csrfToken = null
  }

  async handleCSRFError(): Promise<void> {
    this.clearToken()
    await this.refreshToken()
  }
}

export const csrfService = new CSRFService() 