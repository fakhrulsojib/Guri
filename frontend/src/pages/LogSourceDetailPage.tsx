import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { logSourceService, LogSource } from '../services/logSourceService'
import { formatLogSourceType, formatEnvironment, formatStatus } from '../utils/formatters'
import CreateLogSourceModal from '../components/CreateLogSourceModal'

interface LogSourceDetailPageProps {
  isDark: boolean
}

const LogSourceDetailPage: React.FC<LogSourceDetailPageProps> = ({ isDark }) => {
  const { logSourceId } = useParams<{ logSourceId: string }>()
  const navigate = useNavigate()
  const [logSource, setLogSource] = useState<LogSource | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [apiKey, setApiKey] = useState<string | null>(null)
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKeyLoading, setApiKeyLoading] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)

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
    navigate('/dashboard')
  }

  const handleUpdate = () => {
    setIsEditModalOpen(true)
  }

  const handleEditModalClose = () => {
    setIsEditModalOpen(false)
  }

  const handleEditSuccess = () => {
    setIsEditModalOpen(false)
    fetchLogSource()
  }

  const handleShowApiKey = async () => {
    if (apiKey) {
      setShowApiKey(!showApiKey)
      return
    }
    
    try {
      setApiKeyLoading(true)
      const response = await logSourceService.getLogSourceApiKey(parseInt(logSourceId!))
      setApiKey(response.api_key)
      setShowApiKey(true)
    } catch (err) {
      console.error('Failed to fetch API key:', err)
    } finally {
      setApiKeyLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className={`text-lg ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
          Loading log source details...
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
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={handleBack}
            className={`p-2 rounded-lg transition-all duration-200 ${
              isDark 
                ? 'text-gray-300 hover:text-white hover:bg-gray-700' 
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
            }`}
            aria-label="Back to dashboard"
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
              Log Source Details
            </p>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={() => navigate(`/dashboard/log-sources/${logSourceId}/logs`)}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              isDark 
                ? 'bg-green-600 hover:bg-green-700 text-white' 
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            Logs
          </button>
        <button
          onClick={handleUpdate}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            isDark 
              ? 'bg-blue-600 hover:bg-blue-700 text-white' 
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          Update Log Source
        </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="space-y-6">
        {/* Basic Information */}
        <div className={`rounded-lg border ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} p-6`}>
          <h2 className={`text-xl font-semibold mb-6 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Basic Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-5">
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-blue-500/20' : 'bg-blue-50'
                }`}>
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Name
                  </label>
                  <p className={`mt-1 text-lg font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {logSource.name}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-purple-500/20' : 'bg-purple-50'
                }`}>
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Description
                  </label>
                  <p className={`mt-1 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    {logSource.description || 'No description provided'}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-green-500/20' : 'bg-green-50'
                }`}>
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Source Type
                  </label>
                  <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full mt-1 ${
                    isDark ? 'bg-green-500/20 text-green-300' : 'bg-green-100 text-green-800'
                  }`}>
                    {formatLogSourceType(logSource.source_type)}
                  </span>
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-5">
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-orange-500/20' : 'bg-orange-50'
                }`}>
                  <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Environment
                  </label>
                  <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full mt-1 ${
                    isDark ? 'bg-orange-500/20 text-orange-300' : 'bg-orange-100 text-orange-800'
                  }`}>
                    {formatEnvironment(logSource.environment)}
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-emerald-500/20' : 'bg-emerald-50'
                }`}>
                  <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Status
                  </label>
                  <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full mt-1 ${
                    logSource.status === 'active' 
                      ? 'bg-emerald-100 text-emerald-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {formatStatus(logSource.status)}
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-indigo-500/20' : 'bg-indigo-50'
                }`}>
                  <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    API Key
                  </label>
                  <div className="mt-1 flex items-center space-x-2">
                    <button
                      onClick={handleShowApiKey}
                      disabled={apiKeyLoading}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                        apiKeyLoading
                          ? 'bg-gray-400 cursor-not-allowed'
                          : isDark 
                            ? 'bg-indigo-600 hover:bg-indigo-700 text-white' 
                            : 'bg-indigo-500 hover:bg-indigo-600 text-white'
                      }`}
                      aria-label="Show API key"
                    >
                      {apiKeyLoading ? 'Loading...' : showApiKey ? 'Hide' : 'Show'}
                    </button>
                    
                    {showApiKey && apiKey && (
                      <div className="relative inline-block">
                        <code className={`block px-3 py-2 pr-10 rounded-md text-sm font-mono break-all ${
                          isDark ? 'bg-gray-700 text-gray-200' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {apiKey}
                        </code>
                        <button
                          onClick={() => navigator.clipboard.writeText(apiKey)}
                          className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-1 rounded text-gray-500 hover:text-gray-700 transition-colors duration-200 ${
                            isDark ? 'hover:text-gray-300' : 'hover:text-gray-900'
                          }`}
                          aria-label="Copy API key to clipboard"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tags Section - Full Width */}
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                isDark ? 'bg-pink-500/20' : 'bg-pink-50'
              }`}>
                <svg className="w-6 h-6 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
              </div>
              <div className="flex-1">
                <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                  Tags
                </label>
                <div className="mt-2">
                  {logSource.tags && logSource.tags.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {logSource.tags.map((tag, index) => (
                        <span
                          key={index}
                          className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                            isDark 
                              ? 'bg-pink-500/20 text-pink-300' 
                              : 'bg-pink-100 text-pink-800'
                          }`}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      No tags
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Statistics & Metadata */}
        <div className={`rounded-lg border ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'} p-6`}>
          <h2 className={`text-xl font-semibold mb-6 ${isDark ? 'text-white' : 'text-gray-900'}`}>
            Statistics & Metadata
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-5">
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-blue-500/20' : 'bg-blue-50'
                }`}>
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Total Logs Received
                  </label>
                  <p className={`mt-1 text-3xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {logSource.log_count?.toLocaleString() || '0'}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-green-500/20' : 'bg-green-50'
                }`}>
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Last Log Received
                  </label>
                  <p className={`mt-1 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    {logSource.last_log_at 
                      ? new Date(logSource.last_log_at).toLocaleString()
                      : 'No logs received yet'
                    }
                  </p>
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-5">
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-purple-500/20' : 'bg-purple-50'
                }`}>
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Created
                  </label>
                  <p className={`mt-1 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    {new Date(logSource.created_at).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  isDark ? 'bg-orange-500/20' : 'bg-orange-50'
                }`}>
                  <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </div>
                <div className="flex-1">
                  <label className={`block text-xs font-medium uppercase tracking-wider ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                    Last Updated
                  </label>
                  <p className={`mt-1 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    {new Date(logSource.updated_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      <CreateLogSourceModal
        isOpen={isEditModalOpen}
        onClose={handleEditModalClose}
        onSuccess={handleEditSuccess}
        isDark={isDark}
        editMode={true}
        existingData={logSource}
      />
    </div>
  )
}

export default LogSourceDetailPage 