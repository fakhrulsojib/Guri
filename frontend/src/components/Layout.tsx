import React from 'react'
import Header from './Header'
import Footer from './Footer'
import BackgroundDecorations from './BackgroundDecorations'

interface LayoutProps {
  children: React.ReactNode
  isDark: boolean
}

const Layout: React.FC<LayoutProps> = ({ children, isDark }) => {
  return (
    <div className={`app-container ${isDark ? 'dark' : 'light'}`}>
      <Header isDark={isDark} />
      
      <main className="relative z-10 pt-20">
        {children}
      </main>
      
      <BackgroundDecorations isDark={isDark} />
      <Footer isDark={isDark} />
    </div>
  )
}

export default Layout 