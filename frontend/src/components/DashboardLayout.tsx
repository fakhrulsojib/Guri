import React from 'react'
import { useAuth } from '../hooks/useAuth'
import { useNavigate, useLocation } from 'react-router-dom'

interface DashboardLayoutProps {
  children: React.ReactNode
  isDark: boolean
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children, isDark }) => {
  const { handleLogout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const navItems = [
    { name: 'Log Sources', path: '/dashboard', icon: '📊' },
    { name: 'Profile', path: '/dashboard/profile', icon: '👤' },
    { name: 'Settings', path: '/dashboard/settings', icon: '⚙️' }
  ]

  const isActivePath = (path: string) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      {/* Top Header */}
      <header className={`${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b px-6 py-4`}>
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded-lg ${isDark ? 'bg-blue-500' : 'bg-gradient-to-r from-blue-500 to-purple-600'} flex items-center justify-center`}>
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="text-xl font-bold">Pulse AI Dashboard</span>
          </div>
          
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
        </div>
      </header>

      <div className="flex">
        {/* Left Navigation */}
        <nav className={`w-64 min-h-screen ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-r`}>
          <div className="p-6">
            <ul className="space-y-2">
              {navItems.map((item) => (
                <li key={item.path}>
                  <button
                    onClick={() => navigate(item.path)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 flex items-center space-x-3 ${
                      isActivePath(item.path)
                        ? `${isDark ? 'bg-blue-600 text-white' : 'bg-blue-100 text-blue-700'}`
                        : `${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`
                    }`}
                  >
                    <span className="text-lg">{item.icon}</span>
                    <span className="font-medium">{item.name}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout 