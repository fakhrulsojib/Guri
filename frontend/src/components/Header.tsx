import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { HeaderProps } from '../types'
import { LightningIcon } from './icons'

const Header: React.FC<HeaderProps> = ({ 
  isDark, 
  isAuthenticated, 
  user, 
  handleLogin, 
  handleLogout
}) => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogoClick = (): void => {
    navigate('/')
  }

  const handleDashboardClick = (): void => {
    navigate('/dashboard')
  }

  const isOnDashboardPage = location.pathname.startsWith('/dashboard')

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 p-4 ${isDark ? 'bg-gray-900/80 backdrop-blur-sm' : 'bg-white/80 backdrop-blur-sm'}`}>
      <div className="w-full flex justify-between items-center">
        <button 
          onClick={handleLogoClick}
          className="flex items-center space-x-2 hover:opacity-80 transition-opacity duration-200 cursor-pointer"
          aria-label="Navigate to home page"
        >
          <div className={`w-8 h-8 rounded-lg ${isDark ? 'bg-blue-500' : 'bg-gradient-to-r from-blue-500 to-purple-600'} flex items-center justify-center`}>
            <LightningIcon className="w-5 h-5 text-white" />
          </div>
          <span className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Pulse AI</span>
        </button>
        
        <div className="flex items-center space-x-4">
          {isAuthenticated && user ? (
            <>
              <span className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                {user.name || user.email}
              </span>
              {!isOnDashboardPage && (
                <button
                  onClick={handleDashboardClick}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                    isDark 
                      ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                  aria-label="Navigate to dashboard"
                >
                  Dashboard
                </button>
              )}
              <button
                onClick={handleLogout}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  isDark 
                    ? 'bg-red-600 hover:bg-red-700 text-white' 
                    : 'bg-red-500 hover:bg-red-600 text-white'
                }`}
                aria-label="Logout from application"
              >
                Logout
              </button>
            </>
          ) : (
            <button
              onClick={handleLogin}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                isDark 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              }`}
              aria-label="Login to application"
            >
              Login
            </button>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header 