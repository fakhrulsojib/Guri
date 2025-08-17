import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAppSelector } from './store/hooks'
import Layout from './components/Layout'
import DashboardLayout from './components/DashboardLayout'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import { useAuth } from './hooks/useAuth'

function App() {
  const { isDark } = useAppSelector(state => state.theme)
  const { isAuthenticated } = useAuth()

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* Home Route */}
        <Route path="/" element={
          <Layout isDark={isDark}>
            <HomePage isDark={isDark} />
          </Layout>
        } />
        
        {/* Dashboard Routes - Protected */}
        <Route path="/dashboard" element={
          isAuthenticated ? (
            <DashboardLayout isDark={isDark}>
              <DashboardPage isDark={isDark} />
            </DashboardLayout>
          ) : (
            <Navigate to="/" replace />
          )
        } />
        
        {/* Profile Route - Protected */}
        <Route path="/dashboard/profile" element={
          isAuthenticated ? (
            <DashboardLayout isDark={isDark}>
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
            <DashboardLayout isDark={isDark}>
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