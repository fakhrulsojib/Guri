import React from 'react'

interface HeroSectionProps {
  isDark: boolean
}

const HeroSection: React.FC<HeroSectionProps> = ({ isDark }) => {
  return (
    <div className="hero-section">
      <div className="logo-container">
        <svg className="logo-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <h1 className={`hero-title ${isDark ? 'dark' : 'light'}`}>
        Pulse AI
      </h1>
      <p className={`hero-subtitle ${isDark ? 'dark' : 'light'}`}>
        Your intelligent AI-powered log analytics platform
      </p>
    </div>
  )
}

export default HeroSection 