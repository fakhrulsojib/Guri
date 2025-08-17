import { useEffect, useRef } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { setLoading, setUser, setAccessToken, logout } from '../store/slices/authSlice'
import { authService } from '../services/authService'

export const useAuth = () => {
  const dispatch = useAppDispatch()
  const { user, isAuthenticated, accessToken, isLoading } = useAppSelector(state => state.auth)
  const hasProcessed = useRef(false)

  const getAccessTokenFromStorage = () => {
    return localStorage.getItem('access_token') || null
  }

  const getRefreshTokenFromStorage = () => {
    return localStorage.getItem('refresh_token') || null
  }

  useEffect(() => {
    const handleCallback = async () => {
      if (hasProcessed.current) return
      
      const urlParams = new URLSearchParams(window.location.search)
      const error = urlParams.get('error')
      const auth = urlParams.get('auth')
      const accessToken = urlParams.get('access_token')
      const refreshToken = urlParams.get('refresh_token')
      
      if (error === 'auth_failed') {
        hasProcessed.current = true
        dispatch(logout())
        window.history.replaceState({}, document.title, window.location.pathname)
        return
      }
      
      if (auth === 'success' && !isAuthenticated && accessToken && refreshToken) {
        try {
          hasProcessed.current = true
          dispatch(setLoading(true))
          
          localStorage.setItem('access_token', accessToken)
          localStorage.setItem('refresh_token', refreshToken)
          
          dispatch(setAccessToken(accessToken))
          
          try {
            const userInfo = await authService.getCurrentUser()
            dispatch(setUser(userInfo))
          } catch (userError) {
            throw new Error('Failed to get user info from backend')
          }
          
          window.history.replaceState({}, document.title, window.location.pathname)
        } catch (error) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          dispatch(logout())
        } finally {
          dispatch(setLoading(false))
        }
      }
      
      if (!error && !auth && !isAuthenticated) {
        window.history.replaceState({}, document.title, window.location.pathname)
      }
    }

    handleCallback()
  }, [dispatch, isAuthenticated])

  useEffect(() => {
    const checkExistingAuth = async () => {
      if (isAuthenticated || hasProcessed.current) return
      
      const token = getAccessTokenFromStorage()
      if (token && !isAuthenticated) {
        try {
          hasProcessed.current = true
          dispatch(setLoading(true))
          dispatch(setAccessToken(token))
          
          const userInfo = await authService.getCurrentUser()
          dispatch(setUser(userInfo))
        } catch (error) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          dispatch(logout())
        } finally {
          dispatch(setLoading(false))
        }
      }
    }

    checkExistingAuth()
  }, [dispatch, isAuthenticated])

  const handleLogin = () => {
    const loginUrl = authService.getGoogleLoginUrl()
    window.location.href = loginUrl
  }

  const handleLogout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      dispatch(logout())
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }

  return {
    user,
    isAuthenticated,
    accessToken,
    isLoading,
    handleLogin,
    handleLogout
  }
} 