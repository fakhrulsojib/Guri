import React from 'react'

interface FooterProps {
  isDark: boolean
}

const Footer: React.FC<FooterProps> = ({ isDark }) => {
  return (
    <footer className={`fixed bottom-4 right-4 z-50 ${isDark ? 'text-white' : 'text-gray-900'}`}>
      {/* Footer content can be added here in the future */}
    </footer>
  )
}

export default Footer 