import React from 'react'
import Header from './Header'
import Footer from './Footer'
import BackgroundDecorations from './BackgroundDecorations'
import ThemeToggle from './ThemeToggle'
import { User } from '../types'

interface LayoutProps {
  children: React.ReactNode
  isDark: boolean
  isAuthenticated: boolean
  user: User | null
  handleLogin: () => void
  handleLogout: () => void
}

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  isDark, 
  isAuthenticated, 
  user, 
  handleLogin, 
  handleLogout
}) => {
  return (
    <div className={`app-container ${isDark ? 'dark' : 'light'}`}>
      <Header 
        isDark={isDark}
        isAuthenticated={isAuthenticated}
        user={user}
        handleLogin={handleLogin}
        handleLogout={handleLogout}
      />
      
      <main className="relative z-10 pt-20">
        {children}
      </main>
      
      <BackgroundDecorations isDark={isDark} />
      <Footer isDark={isDark} />
      
      <div className="fixed bottom-6 right-6 z-50">
        <ThemeToggle />
      </div>
    </div>
  )
}

export default Layout 