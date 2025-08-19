import React from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { toggleTheme } from '../store/slices/themeSlice'
import { SunIcon, MoonIcon } from './icons'

interface FooterProps {
  isDark: boolean
}

const Footer: React.FC<FooterProps> = ({ isDark }) => {
  const dispatch = useAppDispatch()
  const { isDark: themeIsDark } = useAppSelector(state => state.theme)

  return (
    <footer className={`fixed bottom-4 right-4 z-50 ${isDark ? 'text-white' : 'text-gray-900'}`}>
      <button
        onClick={() => dispatch(toggleTheme())}
        className={`p-2 rounded-lg transition-all duration-200 ${
          isDark 
            ? 'bg-gray-800 hover:bg-gray-700 text-yellow-400' 
            : 'bg-gray-200 hover:bg-gray-300 text-gray-600'
        }`}
        aria-label="Toggle theme"
      >
        {themeIsDark ? (
          <SunIcon className="w-5 h-5" />
        ) : (
          <MoonIcon className="w-5 h-5" />
        )}
      </button>
    </footer>
  )
}

export default Footer 