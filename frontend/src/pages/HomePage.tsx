import React from 'react'
import HeroSection from '../components/HeroSection'
import FeatureCard from '../components/FeatureCard'
import CTASection from '../components/CTASection'
import { features } from '../constants/features'

interface HomePageProps {
  isDark: boolean
  isAuthenticated: boolean
  handleLogin: () => void
}

const HomePage: React.FC<HomePageProps> = ({ isDark, isAuthenticated, handleLogin }) => {
  return (
    <>
      <HeroSection isDark={isDark} />
      
      <section className="features-section">
        <div className="features-grid">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              iconBgClass={feature.iconBgClass}
              isDark={isDark}
            />
          ))}
        </div>
      </section>
      
      <CTASection 
        isDark={isDark} 
        isAuthenticated={isAuthenticated}
        handleLogin={handleLogin}
      />
    </>
  )
}

export default HomePage 