import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import Header from './Header'
import ThemeToggle from './ThemeToggle'
import { DashboardLayoutProps, NavigationItem } from '../types'
import { LogSourcesIcon, ProfileIcon, SettingsIcon } from './icons'

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children, isDark, user, handleLogout }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const navigationItems: NavigationItem[] = [
    { 
      name: 'Log Sources', 
      path: '/dashboard', 
      icon: LogSourcesIcon,
      description: 'Manage your log sources and data streams'
    },
    { 
      name: 'Profile', 
      path: '/dashboard/profile', 
      icon: ProfileIcon,
      description: 'View and edit your profile information'
    },
    { 
      name: 'Settings', 
      path: '/dashboard/settings', 
      icon: SettingsIcon,
      description: 'Configure your account and application settings'
    },
  ]

  const handleNavigation = (path: string): void => {
    navigate(path)
  }

  const isActivePath = (path: string): boolean => {
    return location.pathname === path
  }

  return (
    <div className={`min-h-screen min-w-[1100px] ${isDark ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      <Header 
        isDark={isDark}
        isAuthenticated={true}
        user={user}
        handleLogin={() => {}} // Not used in dashboard
        handleLogout={handleLogout}
      />
      
      <div className="flex pt-20">
        <nav className={`w-64 min-h-screen ${isDark ? 'bg-gray-800' : 'bg-white'} border-r ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="p-6">
            <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'} mb-6`}>
              Dashboard
            </h2>
            <ul className="space-y-2">
              {navigationItems.map((item: NavigationItem) => {
                const isActive = isActivePath(item.path)
                const IconComponent = item.icon
                return (
                  <li key={item.path}>
                    <button
                      onClick={() => handleNavigation(item.path)}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                        isActive
                          ? isDark
                            ? 'bg-blue-600 text-white'
                            : 'bg-blue-100 text-blue-700'
                          : isDark
                            ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
                            : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                      }`}
                      aria-label={`Navigate to ${item.name}`}
                      title={item.description}
                    >
                      <IconComponent className="w-5 h-5" />
                      <span className="font-medium">{item.name}</span>
                    </button>
                  </li>
                )
              })}
            </ul>
          </div>
        </nav>
        
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
      
      <div className="fixed bottom-6 right-6 z-50">
        <ThemeToggle />
      </div>
    </div>
  )
}

export default DashboardLayout 