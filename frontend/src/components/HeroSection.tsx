import React from 'react'

interface HeroSectionProps {
  isDark: boolean
}

const HeroSection: React.FC<HeroSectionProps> = ({ isDark }) => {
  return (
    <div className="hero-section">
      <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl mb-6 shadow-lg">
      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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