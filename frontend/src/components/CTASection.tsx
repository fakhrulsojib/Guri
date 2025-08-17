import React from 'react'
import { useAuth } from '../hooks/useAuth'

interface CTASectionProps {
  isDark: boolean
}

const CTASection: React.FC<CTASectionProps> = ({ isDark }) => {
  const { isAuthenticated, isLoading, handleLogin } = useAuth()

  const handleCTAClick = () => {
    if (isAuthenticated) {
      // TODO: Navigate to dashboard when implemented
      console.log('Navigate to dashboard')
    } else {
      handleLogin()
    }
  }

  if (isLoading) {
    return (
      <div className="cta-section">
        <button className="cta-button" disabled>
          Loading...
        </button>
        <p className={`tech-stack ${isDark ? 'dark' : 'light'}`}>
          Powered by FastAPI • Kafka • PostgreSQL • ChromaDB
        </p>
      </div>
    )
  }

  return (
    <div className="cta-section">
      <button 
        className="cta-button"
        onClick={handleCTAClick}
      >
        {isAuthenticated ? 'Go To Dashboard' : 'Get Started'}
      </button>
      <p className={`tech-stack ${isDark ? 'dark' : 'light'}`}>
        Powered by FastAPI • Kafka • PostgreSQL • ChromaDB
      </p>
    </div>
  )
}

export default CTASection 