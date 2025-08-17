import React from 'react'
import { useAppSelector } from './store/hooks'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'

function App() {
  const { isDark } = useAppSelector(state => state.theme)

  return (
    <Layout isDark={isDark}>
      <HomePage isDark={isDark} />
    </Layout>
  )
}

export default App 