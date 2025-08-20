import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAppSelector } from './store/hooks'
import Layout from './components/Layout'
import DashboardLayout from './components/DashboardLayout'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import { useAuth } from './hooks/useAuth'
import { useCSRF } from './hooks/useCSRF'

function App() {
  const { isDark } = useAppSelector(state => state.theme)
  const { isAuthenticated, isLoading: authLoading, isInitialized: authInitialized, user, handleLogin, handleLogout } = useAuth()
  const { isInitialized: csrfInitialized, error } = useCSRF()





  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-800 mb-4">CSRF Protection Error</h1>
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!csrfInitialized || !authInitialized || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing security...</p>
        </div>
      </div>
    )
  }

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* Home Route */}
        <Route path="/" element={
          <Layout 
            isDark={isDark} 
            isAuthenticated={isAuthenticated}
            user={user}
            handleLogin={handleLogin}
            handleLogout={handleLogout}
          >
            <HomePage 
              isDark={isDark} 
              isAuthenticated={isAuthenticated}
              handleLogin={handleLogin}
            />
          </Layout>
        } />
        
        {/* Dashboard Routes - Protected */}
        <Route path="/dashboard" element={
          isAuthenticated ? (
            <DashboardLayout 
              isDark={isDark}
              user={user}
              handleLogout={handleLogout}
            >
              <DashboardPage isDark={isDark} />
            </DashboardLayout>
          ) : (
            <Navigate to="/" replace />
          )
        } />
        
        {/* Profile Route - Protected */}
        <Route path="/dashboard/profile" element={
          isAuthenticated ? (
            <DashboardLayout 
              isDark={isDark}
              user={user}
              handleLogout={handleLogout}
            >
              <div className="p-6">
                <h1 className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Profile
                </h1>
                <p className={`mt-2 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  Profile page coming soon...
                </p>
              </div>
            </DashboardLayout>
          ) : (
            <Navigate to="/" replace />
          )
        } />
        
        {/* Settings Route - Protected */}
        <Route path="/dashboard/settings" element={
          isAuthenticated ? (
            <DashboardLayout 
              isDark={isDark}
              user={user}
              handleLogout={handleLogout}
            >
              <div className="p-6">
                <h1 className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Settings
                </h1>
                <p className={`mt-2 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                  Settings page coming soon...
                </p>
              </div>
            </DashboardLayout>
          ) : (
            <Navigate to="/" replace />
          )
        } />
      </Routes>
    </Router>
  )
}

export default App 