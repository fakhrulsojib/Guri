import React from 'react'
import { useAuth } from '../hooks/useAuth'

interface HeaderProps {
  isDark: boolean
}

const Header: React.FC<HeaderProps> = ({ isDark }) => {
  const { isAuthenticated, handleLogin, handleLogout } = useAuth()

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 p-4 ${isDark ? 'bg-gray-900/80 backdrop-blur-sm' : 'bg-white/80 backdrop-blur-sm'}`}>
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className={`w-8 h-8 rounded-lg ${isDark ? 'bg-blue-500' : 'bg-gradient-to-r from-blue-500 to-purple-600'} flex items-center justify-center`}>
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>Pulse AI</span>
        </div>
        
        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            <button
              onClick={handleLogout}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                isDark 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
            >
              Logout
            </button>
          ) : (
            <button
              onClick={handleLogin}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                isDark 
                  ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                  : 'bg-blue-500 hover:bg-blue-600 text-white'
              }`}
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