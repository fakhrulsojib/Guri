import React from 'react'
import { useAppSelector } from './store/hooks'
import HeroSection from './components/HeroSection'
import FeatureCard from './components/FeatureCard'
import CTASection from './components/CTASection'
import BackgroundDecorations from './components/BackgroundDecorations'
import Header from './components/Header'
import Footer from './components/Footer'
import { features } from './constants/features'

function App() {
  const { isDark } = useAppSelector(state => state.theme)

  return (
    <div className={`app-container ${isDark ? 'dark' : 'light'}`}>
      <Header isDark={isDark} />
      
      <main className="relative z-10 pt-20">
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
        
        <CTASection isDark={isDark} />
      </main>
      
      <BackgroundDecorations isDark={isDark} />
      <Footer isDark={isDark} />
    </div>
  )
}

export default App 