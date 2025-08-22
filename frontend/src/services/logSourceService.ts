const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'https://fakhrulsojib.mooo.com'

import { csrfService } from './csrfService'

export interface LogSource {
  id: number
  name: string
  description: string
  source_type: string
  environment: string
  tags: string[]
  status: string
  created_at: string
  updated_at: string
  last_log_at?: string
  log_count: number
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
      const error = new Error('Failed to create log source')
      ;(error as any).response = response
      throw error
    }
    return response.json()
  },

  getLogSource: async (id: number): Promise<LogSource> => {
    const headers = await csrfService.getHeaders()
    
    const response = await fetch(`${BACKEND_URL}/api/v1/log-sources/${id}`, {
      headers,
      credentials: 'include'
    })
    
    if (!response.ok) {
      if (response.status === 403) {
        await csrfService.handleCSRFError()
        return logSourceService.getLogSource(id)
      }
      if (response.status === 404) {
        throw new Error('Log source not found')
      }
      throw new Error('Failed to fetch log source')
    }
    return response.json()
  },

  getLogSourceApiKey: async (id: number): Promise<{ api_key: string }> => {
    const headers = await csrfService.getHeaders()
    
    const response = await fetch(`${BACKEND_URL}/api/v1/log-sources/${id}/api-key`, {
      headers,
      credentials: 'include'
    })
    
    if (!response.ok) {
      if (response.status === 403) {
        await csrfService.handleCSRFError()
        return logSourceService.getLogSourceApiKey(id)
      }
      if (response.status === 404) {
        throw new Error('Log source not found')
      }
      throw new Error('Failed to fetch API key')
    }
    return response.json()
  }
} 