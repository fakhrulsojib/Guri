import { useEffect, useRef, useCallback, useState } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { setLoading, setUser, setAccessToken, logout } from '../store/slices/authSlice'
import { authService } from '../services/authService'
import { authInterceptor } from '../services/authInterceptor'
import { tabSyncService } from '../services/tabSyncService'
import { store } from '../store'

export const useAuth = () => {
  const dispatch = useAppDispatch()
  const { user, isAuthenticated, accessToken, isLoading } = useAppSelector(state => state.auth)
  const hasCheckedAuth = useRef(false)
  const isCheckingAuth = useRef(false)
  const [isInitialized, setIsInitialized] = useState(false)
  const lastBroadcastRef = useRef<string>('')



  const checkAuthFromCookies = useCallback(async () => {
    if (isCheckingAuth.current) return
    
    try {
      isCheckingAuth.current = true
      dispatch(setLoading(true))
      
      const success = await authInterceptor.checkAuthStatus()
      if (!success) {
        dispatch(logout())
      }
    } catch (error) {
      dispatch(logout())
    } finally {
      dispatch(setLoading(false))
      isCheckingAuth.current = false
    }
  }, [dispatch])

  useEffect(() => {
    const checkInitialAuth = async () => {
      if (hasCheckedAuth.current) return
      
      tabSyncService.initialize()
      await authInterceptor.initialize()
      
      const urlParams = new URLSearchParams(window.location.search)
      const auth = urlParams.get('auth')
      if (auth === 'success') {
        try {
          dispatch(setLoading(true))
          const success = await authInterceptor.checkAuthStatus()
          if (success) {
            window.history.replaceState({}, document.title, window.location.pathname)
          } else {
            dispatch(logout())
          }
        } catch (error) {
          dispatch(logout())
        } finally {
          dispatch(setLoading(false))
        }
      }
      
      hasCheckedAuth.current = true
      setIsInitialized(true)
    }

    const timeoutId = setTimeout(checkInitialAuth, 100)
    return () => clearTimeout(timeoutId)
  }, [dispatch, checkAuthFromCookies, isAuthenticated])

  useEffect(() => {
    if (isAuthenticated && user) {
      const userKey = `${user.id}-${isAuthenticated}`
      if (lastBroadcastRef.current !== userKey) {
        lastBroadcastRef.current = userKey
        tabSyncService.broadcastAuthState(user, isAuthenticated)
      }
    }
  }, [isAuthenticated, user])

  useEffect(() => {
    return () => {
      tabSyncService.cleanup()
    }
  }, [])


  const handleLogin = () => {
    if (isAuthenticated) {
      window.location.reload()
      return
    }
    
    const loginUrl = authService.getGoogleLoginUrl()
    window.location.href = loginUrl
  }

  const handleLogout = async () => {
    try {
      await authService.logout()
    } catch (error) {
    } finally {
      dispatch(logout())
      authInterceptor.reset()
      tabSyncService.broadcastLogout()
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }

  return {
    user,
    isAuthenticated,
    accessToken,
    isLoading,
    isInitialized,
    handleLogin,
    handleLogout
  }
} 