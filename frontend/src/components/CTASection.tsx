import React from 'react'
import { useNavigate } from 'react-router-dom'

interface CTASectionProps {
  isDark: boolean
  isAuthenticated: boolean
  handleLogin: () => void
}

const CTASection: React.FC<CTASectionProps> = ({ isDark, isAuthenticated, handleLogin }) => {
  const navigate = useNavigate()

  const handleCTAClick = () => {
    if (isAuthenticated) {
      navigate('/dashboard')
    } else {
      handleLogin()
    }
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