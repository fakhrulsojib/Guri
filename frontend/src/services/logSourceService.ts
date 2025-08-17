const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

export interface LogSource {
  id: number
  name: string
  description: string
  status: string
  environment: string
  created_at: string
  updated_at: string
}

export const logSourceService = {
  getLogSources: async (accessToken: string): Promise<LogSource[]> => {
    const response = await fetch(`${BACKEND_URL}/api/v1/log-sources`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    })
    if (!response.ok) {
      throw new Error('Failed to fetch log sources')
    }
    return response.json()
  },

  createLogSource: async (logSourceData: any, accessToken: string): Promise<LogSource> => {
    const response = await fetch(`${BACKEND_URL}/api/v1/log-sources`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify(logSourceData)
    })
    if (!response.ok) {
      throw new Error('Failed to create log source')
    }
    return response.json()
  }
} 