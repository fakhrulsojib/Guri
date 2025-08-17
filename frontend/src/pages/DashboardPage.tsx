import React from 'react'
import LogSourcesPage from './LogSourcesPage'

interface DashboardPageProps {
  isDark: boolean
}

const DashboardPage: React.FC<DashboardPageProps> = ({ isDark }) => {
  return <LogSourcesPage isDark={isDark} />
}

export default DashboardPage 