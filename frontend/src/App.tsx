import React from 'react'
import { useAppSelector } from './store/hooks'
import ThemeToggle from './components/ThemeToggle'
import FeatureCard from './components/FeatureCard'
import HeroSection from './components/HeroSection'
import CTASection from './components/CTASection'
import BackgroundDecorations from './components/BackgroundDecorations'
import { features } from './constants/features.tsx'

function App() {
  const isDark = useAppSelector((state) => state.theme.isDark)
  const themeClass = isDark ? 'dark' : 'light'

  return (
    <div className={`app-container ${themeClass}`}>
      <ThemeToggle />
      
      <div className="relative overflow-hidden">
        <BackgroundDecorations isDark={isDark} />
        
        <div className="main-content">
          <div className="content-wrapper">
            <HeroSection isDark={isDark} />

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

            <CTASection isDark={isDark} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App 