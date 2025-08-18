const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const CSRF_ENDPOINT = import.meta.env.VITE_CSRF_ENDPOINT || '/api/v1/health/'

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

  private async refreshToken(): Promise<string> {
    this.isRefreshing = true
    
    try {
      const response = await fetch(`${BACKEND_URL}${CSRF_ENDPOINT}`, {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch CSRF token')
      }
      
      const token = response.headers.get('X-CSRF-Token')
      if (!token) {
        throw new Error('CSRF token not found in response')
      }
      
      this.csrfToken = token
      return token
    } catch (error) {
      console.error('Failed to refresh CSRF token:', error)
      throw error
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