import React from 'react'
import { useAppSelector, useAppDispatch } from '../store/hooks'
import { toggleTheme } from '../store/slices/themeSlice'
import { SunIcon, MoonIcon } from './icons'

const ThemeToggle: React.FC = () => {
  const isDark = useAppSelector((state) => state.theme.isDark)
  const dispatch = useAppDispatch()

  return (
    <button
      onClick={() => dispatch(toggleTheme())}
      className="fixed top-6 right-6 z-50 p-3 rounded-full bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110"
      aria-label="Toggle theme"
    >
      {isDark ? (
        <SunIcon className="w-6 h-6 text-yellow-500" />
      ) : (
        <MoonIcon className="w-6 h-6 text-gray-700" />
      )}
    </button>
  )
}

export default ThemeToggle 