import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import Header from './Header'
import ThemeToggle from './ThemeToggle'
import { DashboardLayoutProps, NavigationItem } from '../types'
import { LogSourcesIcon, ProfileIcon, SettingsIcon, ChevronLeftIcon, ChevronRightIcon } from './icons'

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children, isDark, user, handleLogout }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [isNavCollapsed, setIsNavCollapsed] = useState(false)

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

  const toggleNav = (): void => {
    setIsNavCollapsed(!isNavCollapsed)
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
      
      <div className="flex pt-20 min-w-[1100px]">
        <nav className={`${isNavCollapsed ? 'w-16' : 'w-56'} min-h-screen ${isDark ? 'bg-gray-800' : 'bg-white'} border-r ${isDark ? 'border-gray-700' : 'border-gray-200'} transition-all duration-300 relative`}>
          <div className={`${isNavCollapsed ? 'p-3' : 'p-6'}`}>
            <div className="flex items-center justify-between mb-6">
              {!isNavCollapsed && (
                <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  Dashboard
                </h2>
              )}
              <button
                onClick={toggleNav}
                className={`p-1 rounded-md transition-colors duration-200 ${
                  isDark 
                    ? 'text-gray-400 hover:text-white hover:bg-gray-700' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
                aria-label={isNavCollapsed ? 'Expand navigation' : 'Collapse navigation'}
                title={isNavCollapsed ? 'Expand navigation' : 'Collapse navigation'}
              >
                {isNavCollapsed ? (
                  <ChevronRightIcon className="w-4 h-4" />
                ) : (
                  <ChevronLeftIcon className="w-4 h-4" />
                )}
              </button>
            </div>
            <ul className="space-y-2">
              {navigationItems.map((item: NavigationItem) => {
                const isActive = isActivePath(item.path)
                const IconComponent = item.icon
                return (
                  <li key={item.path}>
                    <button
                      onClick={() => handleNavigation(item.path)}
                      className={`w-full flex items-center ${isNavCollapsed ? 'justify-center' : 'space-x-3'} px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                        isActive
                          ? isDark
                            ? 'bg-blue-600 text-white'
                            : 'bg-blue-100 text-blue-700'
                          : isDark
                            ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
                            : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                      }`}
                      aria-label={`Navigate to ${item.name}`}
                      title={isNavCollapsed ? item.description : undefined}
                    >
                      <div className={`${isNavCollapsed ? 'w-5 h-5 rounded-lg flex items-center justify-center' : ''}`}>
                        <IconComponent className="w-5 h-5" />
                      </div>
                      {!isNavCollapsed && (
                        <span className="font-medium">{item.name}</span>
                      )}
                    </button>
                  </li>
                )
              })}
            </ul>
          </div>
        </nav>
        
        <main className="flex-1 p-8 min-w-0">
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