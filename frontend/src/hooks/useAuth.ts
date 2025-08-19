import { useEffect, useRef, useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { setLoading, setUser, setAccessToken, logout } from '../store/slices/authSlice'
import { authService } from '../services/authService'

// Constants for better maintainability
const REFRESH_INTERVAL_MINUTES = 9
const REFRESH_INTERVAL_SECONDS = 45
const REFRESH_INTERVAL_MS = REFRESH_INTERVAL_MINUTES * 60 * 1000 + REFRESH_INTERVAL_SECONDS * 1000
const VERIFICATION_THRESHOLD_MS = 5 * 60 * 1000
const INITIAL_AUTH_DELAY_MS = 100
const SESSION_STORAGE_KEYS = {
  USER_DISPLAY: 'pulse_ai_user_display',
  LAST_VERIFICATION: 'pulse_ai_last_verification'
} as const

export const useAuth = () => {
  const dispatch = useAppDispatch()
  const { user, isAuthenticated, accessToken, isLoading } = useAppSelector(state => state.auth)
  const hasCheckedAuth = useRef(false)
  const isCheckingAuth = useRef(false)
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null)
  
  const startBackgroundRefresh = useCallback(() => {
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current)
    }
    
    refreshIntervalRef.current = setInterval(async () => {
      if (isAuthenticated) {
        try {
          await authService.refreshToken()
        } catch (error) {
          // Don't logout immediately, let the next API call handle it
        }
      }
    }, REFRESH_INTERVAL_MS)
  }, [isAuthenticated])

  const stopBackgroundRefresh = useCallback(() => {
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current)
      refreshIntervalRef.current = null
    }
  }, [])

  const checkAuthFromCookies = useCallback(async () => {
    if (isCheckingAuth.current) return
    
    try {
      isCheckingAuth.current = true
      dispatch(setLoading(true))
      
      const userInfo = await authService.getCurrentUserWithRefresh()
      dispatch(setUser(userInfo))
      dispatch(setAccessToken('authenticated'))
      
      startBackgroundRefresh()
      
      const safeUserData = {
        id: userInfo.id,
        name: userInfo.name,
        email: userInfo.email,
        picture: userInfo.picture
      }
      sessionStorage.setItem(SESSION_STORAGE_KEYS.USER_DISPLAY, JSON.stringify(safeUserData))
    } catch (error) {
      dispatch(logout())
      sessionStorage.removeItem(SESSION_STORAGE_KEYS.USER_DISPLAY)
      stopBackgroundRefresh()
    } finally {
      dispatch(setLoading(false))
      isCheckingAuth.current = false
    }
  }, [dispatch, startBackgroundRefresh, stopBackgroundRefresh])

  useEffect(() => {
    const checkInitialAuth = async () => {
      if (hasCheckedAuth.current) return
      
      const storedUserDisplay = sessionStorage.getItem(SESSION_STORAGE_KEYS.USER_DISPLAY)
      
      if (storedUserDisplay) {
        try {
          const userDisplayData = JSON.parse(storedUserDisplay)
          dispatch(setUser(userDisplayData))
          dispatch(setAccessToken('authenticated'))
          startBackgroundRefresh()
          
          const lastVerification = sessionStorage.getItem(SESSION_STORAGE_KEYS.LAST_VERIFICATION)
          const now = Date.now()
          const verificationAge = lastVerification ? now - parseInt(lastVerification) : Infinity
          
          if (verificationAge > VERIFICATION_THRESHOLD_MS) {
            await checkAuthFromCookies()
            sessionStorage.setItem(SESSION_STORAGE_KEYS.LAST_VERIFICATION, now.toString())
          }
        } catch (error) {
          dispatch(logout())
          sessionStorage.removeItem(SESSION_STORAGE_KEYS.USER_DISPLAY)
          stopBackgroundRefresh()
        }
      }
      
      const urlParams = new URLSearchParams(window.location.search)
      const auth = urlParams.get('auth')
      if (auth === 'success') {
        try {
          dispatch(setLoading(true))
          const userInfo = await authService.getCurrentUserWithRefresh()
          dispatch(setUser(userInfo))
          dispatch(setAccessToken('authenticated'))
          startBackgroundRefresh()
          
          const safeUserData = {
            id: userInfo.id,
            name: userInfo.name,
            email: userInfo.email,
            picture: userInfo.picture
          }
          sessionStorage.setItem(SESSION_STORAGE_KEYS.USER_DISPLAY, JSON.stringify(safeUserData))
          
          window.history.replaceState({}, document.title, window.location.pathname)
        } catch (error) {
          dispatch(logout())
        } finally {
          dispatch(setLoading(false))
        }
      }
      
      hasCheckedAuth.current = true
    }

    const timeoutId = setTimeout(checkInitialAuth, INITIAL_AUTH_DELAY_MS)
    return () => clearTimeout(timeoutId)
  }, [dispatch, checkAuthFromCookies, stopBackgroundRefresh])

  useEffect(() => {
    return () => {
      stopBackgroundRefresh()
    }
  }, [stopBackgroundRefresh])

  const handleLogin = () => {
    const loginUrl = authService.getGoogleLoginUrl()
    window.location.href = loginUrl
  }

  const handleLogout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      // Silent error handling for logout
    } finally {
      dispatch(logout())
      sessionStorage.removeItem(SESSION_STORAGE_KEYS.USER_DISPLAY)
      stopBackgroundRefresh()
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