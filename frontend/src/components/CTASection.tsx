import React from 'react'

interface CTASectionProps {
  isDark: boolean
}

const CTASection: React.FC<CTASectionProps> = ({ isDark }) => {
  return (
    <div className="cta-section">
      <button className="cta-button">
        Get Started
      </button>
      <p className={`tech-stack ${isDark ? 'dark' : 'light'}`}>
        Powered by FastAPI • Kafka • PostgreSQL • ChromaDB
      </p>
    </div>
  )
}

export default CTASection 