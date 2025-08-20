import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAppDispatch } from '../store/hooks'
import { setUser, setAccessToken } from '../store/slices/authSlice'

const GoogleCallback: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get('code')
        const error = searchParams.get('error')
        const state = searchParams.get('state')

        if (error) {
          setError(`OAuth error: ${error}`)
          setIsProcessing(false)
          return
        }

        if (!code) {
          setError('No authorization code received')
          setIsProcessing(false)
          return
        }

        // Exchange the code for tokens by calling the backend
        const response = await fetch('/auth/google/callback', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        })

        if (!response.ok) {
          throw new Error('Failed to exchange code for tokens')
        }

        // Get the user info
        const userResponse = await fetch('/auth/me', {
          credentials: 'include',
        })

        if (!userResponse.ok) {
          throw new Error('Failed to get user info')
        }

        const userInfo = await userResponse.json()

        // Set authentication state
        dispatch(setUser(userInfo))
        dispatch(setAccessToken('authenticated'))

        // Redirect to dashboard or home
        const redirectUrl = state || '/'
        navigate(redirectUrl, { replace: true })

      } catch (err) {

        setError(err instanceof Error ? err.message : 'Authentication failed')
        setIsProcessing(false)
      }
    }

    handleCallback()
  }, [searchParams, navigate, dispatch])

  if (isProcessing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Completing authentication...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-800 mb-4">Authentication Error</h1>
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={() => navigate('/')} 
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return null
}

export default GoogleCallback 