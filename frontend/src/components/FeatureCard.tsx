import React from 'react'

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
  iconBgClass: string
  isDark: boolean
}

const FeatureCard: React.FC<FeatureCardProps> = ({ 
  icon, 
  title, 
  description, 
  iconBgClass, 
  isDark 
}) => {
  return (
    <div className={`feature-card ${isDark ? 'dark' : 'light'}`}>
      <div className={`feature-icon ${iconBgClass}`}>
        {icon}
      </div>
      <h3 className={`feature-title ${isDark ? 'dark' : 'light'}`}>
        {title}
      </h3>
      <p className={`feature-description ${isDark ? 'dark' : 'light'}`}>
        {description}
      </p>
    </div>
  )
}

export default FeatureCard 