import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { logSourceService, LogSource } from '../services/logSourceService'

interface LogSourceLogsPageProps {
  isDark: boolean
}

const LogSourceLogsPage: React.FC<LogSourceLogsPageProps> = ({ isDark }) => {
  const { logSourceId } = useParams<{ logSourceId: string }>()
  const navigate = useNavigate()
  const [logSource, setLogSource] = useState<LogSource | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (logSourceId) {
      fetchLogSource()
    }
  }, [logSourceId])

  const fetchLogSource = async () => {
    try {
      setLoading(true)
      const data = await logSourceService.getLogSource(parseInt(logSourceId!))
      setLogSource(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch log source details')
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    navigate(`/dashboard/log-sources/${logSourceId}`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className={`text-lg ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
          Loading logs...
        </div>
      </div>
    )
  }

  if (error || !logSource) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-lg text-red-500 mb-4">
            {error || 'Log source not found'}
          </div>
          <button
            onClick={handleBack}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              isDark 
                ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            Back to Log Source
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <button
          onClick={handleBack}
          className={`p-2 rounded-lg transition-all duration-200 ${
            isDark 
              ? 'text-gray-300 hover:text-white hover:bg-gray-700' 
              : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
          }`}
          aria-label="Back to log source details"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div>
          <h1 className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            {logSource.name}
          </h1>
          <p className={`mt-2 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
            Logs
          </p>
        </div>
      </div>

      <div className={`rounded-lg border ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} p-6`}>
        <div className="text-center py-12">
          <div className={`text-2xl font-semibold ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
            Coming Soon
          </div>
          <p className={`mt-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            Log viewing functionality will be available soon.
          </p>
        </div>
      </div>
    </div>
  )
}

export default LogSourceLogsPage 