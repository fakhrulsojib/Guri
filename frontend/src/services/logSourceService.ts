const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

import { csrfService } from './csrfService'

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
  getLogSources: async (): Promise<LogSource[]> => {
    const headers = await csrfService.getHeaders()
    
    const response = await fetch(`${BACKEND_URL}/api/v1/log-sources`, {
      headers,
      credentials: 'include'
    })
    
    if (!response.ok) {
      if (response.status === 403) {
        await csrfService.handleCSRFError()
        return logSourceService.getLogSources()
      }
      throw new Error('Failed to fetch log sources')
    }
    return response.json()
  },

  createLogSource: async (logSourceData: any): Promise<LogSource> => {
    const headers = await csrfService.getHeaders({
      'Content-Type': 'application/json'
    })
    
    const response = await fetch(`${BACKEND_URL}/api/v1/log-sources`, {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify(logSourceData)
    })
    
    if (!response.ok) {
      if (response.status === 403) {
        await csrfService.handleCSRFError()
        return logSourceService.createLogSource(logSourceData)
      }
      throw new Error('Failed to create log source')
    }
    return response.json()
  }
} 