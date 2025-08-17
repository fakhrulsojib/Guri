import { useEffect, useRef } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { setLoading, setUser, setTokens, logout } from '../store/slices/authSlice'
import { authService } from '../services/authService'

export const useAuth = () => {
  const dispatch = useAppDispatch()
  const { user, isAuthenticated, accessToken, refreshToken, isLoading } = useAppSelector(state => state.auth)
  const hasProcessed = useRef(false)

  useEffect(() => {
    const handleCallback = async () => {
      if (hasProcessed.current) return
      
      const urlParams = new URLSearchParams(window.location.search)
      const error = urlParams.get('error')
      const auth = urlParams.get('auth')
      
      if (error === 'auth_failed') {
        hasProcessed.current = true
        dispatch(logout())
        window.history.replaceState({}, document.title, window.location.pathname)
        return
      }
      
      if (auth === 'success' && !isAuthenticated) {
        try {
          hasProcessed.current = true
          dispatch(setLoading(true))
          
          const accessToken = urlParams.get('access_token')
          const refreshToken = urlParams.get('refresh_token')
          
          if (accessToken && refreshToken) {
            dispatch(setTokens({
              accessToken: accessToken,
              refreshToken: refreshToken
            }))
            
            try {
              const userInfo = await authService.getCurrentUser(accessToken)
              dispatch(setUser(userInfo))
            } catch (userError) {
              throw new Error('Failed to get user info from backend')
            }
          }
          
          window.history.replaceState({}, document.title, window.location.pathname)
        } catch (error) {
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

  const handleLogin = () => {
    const loginUrl = authService.getGoogleLoginUrl()
    window.location.href = loginUrl
  }

  const handleLogout = async () => {
    try {
      if (refreshToken) {
        await authService.logout(refreshToken)
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      dispatch(logout())
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    handleLogin,
    handleLogout
  }
} 