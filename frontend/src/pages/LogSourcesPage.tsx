import React, { useEffect, useState } from 'react'
import { logSourceService, LogSource } from '../services/logSourceService'
import { useAppSelector } from '../store/hooks'

interface LogSourcesPageProps {
  isDark: boolean
}

const LogSourcesPage: React.FC<LogSourcesPageProps> = ({ isDark }) => {
  const [logSources, setLogSources] = useState<LogSource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchLogSources()
  }, [])

  const fetchLogSources = async () => {
    try {
      setLoading(true)
      const data = await logSourceService.getLogSources()
      setLogSources(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch log sources')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateLogSource = () => {
    // TODO: Implement log source creation form
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className={`text-lg ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
          Loading log sources...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-red-500">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className={`text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Log Sources
          </h1>
          <p className={`mt-2 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
            Manage your log sources and monitor their status
          </p>
        </div>
        
        <button
          onClick={handleCreateLogSource}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            isDark 
              ? 'bg-blue-600 hover:bg-blue-700 text-white' 
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          + Create Log Source
        </button>
      </div>

      {/* Log Sources List */}
      <div className={`rounded-lg border ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} overflow-hidden`}>
        {logSources.length === 0 ? (
          <div className="p-8 text-center">
            <div className={`text-6xl mb-4 ${isDark ? 'text-gray-600' : 'text-gray-300'}`}>
              📊
            </div>
            <h3 className={`text-lg font-medium mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              No log sources yet
            </h3>
            <p className={`${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
              Get started by creating your first log source to begin monitoring your applications.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className={`${isDark ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <tr>
                  <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-300' : 'text-gray-500'}`}>
                    Name
                  </th>
                  <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-300' : 'text-gray-500'}`}>
                    Description
                  </th>
                  <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-300' : 'text-gray-500'}`}>
                    Status
                  </th>
                  <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-300' : 'text-gray-500'}`}>
                    Environment
                  </th>
                  <th className={`px-4 py-3 text-left text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-300' : 'text-gray-500'}`}>
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className={`${isDark ? 'bg-gray-800 divide-gray-700' : 'bg-white divide-gray-200'}`}>
                {logSources.map((logSource) => (
                  <tr key={logSource.id} className={`${isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}`}>
                    <td className={`px-4 py-4 text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'} max-w-xs truncate`}>
                      {logSource.name}
                    </td>
                    <td className={`px-4 py-4 text-sm ${isDark ? 'text-gray-300' : 'text-gray-500'} max-w-xs truncate`}>
                      {logSource.description}
                    </td>
                    <td className="px-4 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        logSource.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {logSource.status}
                      </span>
                    </td>
                    <td className={`px-4 py-4 text-sm ${isDark ? 'text-gray-300' : 'text-gray-500'} max-w-xs truncate`}>
                      {logSource.environment}
                    </td>
                    <td className={`px-4 py-4 text-sm ${isDark ? 'text-gray-300' : 'text-gray-500'}`}>
                      {new Date(logSource.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default LogSourcesPage 