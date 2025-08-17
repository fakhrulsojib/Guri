import React from 'react'

interface BackgroundDecorationsProps {
  isDark: boolean
}

const BackgroundDecorations: React.FC<BackgroundDecorationsProps> = ({ isDark }) => {
  const themeClass = isDark ? 'dark' : 'light'
  
  return (
    <div className="background-decoration">
      <div className={`background-blob top-right ${themeClass}`}></div>
      <div className={`background-blob bottom-left ${themeClass}`}></div>
    </div>
  )
}

export default BackgroundDecorations 