import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface ThemeState {
    isDark: boolean
}

const getInitialTheme = (): boolean => {
    if (typeof window !== 'undefined') {
        const saved = localStorage.getItem('theme')
        if (saved !== null) {
            return saved === 'dark'
        }
    }
    return false
}

const initialState: ThemeState = {
    isDark: getInitialTheme(),
}

const themeSlice = createSlice({
    name: 'theme',
    initialState,
    reducers: {
        toggleTheme: (state) => {
            state.isDark = !state.isDark
            localStorage.setItem('theme', state.isDark ? 'dark' : 'light')
        },
        setTheme: (state, action: PayloadAction<boolean>) => {
            state.isDark = action.payload
            localStorage.setItem('theme', action.payload ? 'dark' : 'light')
        },
    },
})

export const { toggleTheme, setTheme } = themeSlice.actions
export default themeSlice.reducer 