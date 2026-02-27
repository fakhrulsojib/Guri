import { useEffect, useState } from 'react'
import { csrfService } from '../services/csrfService'

export const useCSRF = () => {
  const [isInitialized, setIsInitialized] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const initializeCSRF = async () => {
      try {
        await csrfService.getToken()
        setIsInitialized(true)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize CSRF protection')
      }
    }

    initializeCSRF()
  }, [])

  const refreshToken = async () => {
    try {
      setError(null)
      await csrfService.handleCSRFError()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh CSRF token')
    }
  }

  return {
    isInitialized,
    error,
    refreshToken
  }
} 