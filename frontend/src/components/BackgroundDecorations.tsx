import React from 'react'

interface BackgroundDecorationsProps {
  isDark: boolean
}

const BackgroundDecorations: React.FC<BackgroundDecorationsProps> = ({ isDark }) => {
  const themeClass = isDark ? 'dark' : 'light'
  
  return (
    <div className="background-decorations">
      <div className={`blob top-20 right-20 w-80 h-80 ${themeClass}`}></div>
      <div className={`blob bottom-20 left-20 w-80 h-80 ${themeClass}`}></div>
    </div>
  )
}

export default BackgroundDecorations 