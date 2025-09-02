import React, { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { logSourceService, LogSource } from '../services/logSourceService'
import { authService } from '../services/authService'

interface LogSourceLogsPageProps {
  isDark: boolean
}

interface LogEntry {
  id: string
  timestamp: string
  level: 'CRITICAL' | 'INFO' | 'WARN' | 'ERROR' | 'DEBUG'
  message: string
  source: string
  trace_id?: string
  span_id?: string
  data?: Record<string, any>
  metadata?: Record<string, any>
}

const LogSourceLogsPage: React.FC<LogSourceLogsPageProps> = ({ isDark }) => {
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = `
      @keyframes slideInFromBottom {
        0% {
          opacity: 0;
          transform: translateY(20px) scale(0.95);
        }
        100% {
          opacity: 1;
          transform: translateY(0) scale(1);
        }
      }
      
      .animate-slideInFromBottom {
        animation: slideInFromBottom 0.5s ease-out forwards;
      }
    `
    document.head.appendChild(style)
    
    return () => {
      document.head.removeChild(style)
    }
  }, [])
  const { logSourceId } = useParams<{ logSourceId: string }>()
  const navigate = useNavigate()
  const [logSource, setLogSource] = useState<LogSource | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const maxRetries = 3
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const logsContainerRef = useRef<HTMLDivElement | null>(null)
  const [expandedLogs, setExpandedLogs] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (logSourceId) {
      setRetryCount(0)
      fetchLogSource()
    }
  }, [logSourceId])

  useEffect(() => {
    if (isStreaming && logSourceId) {
      connectWebSocket()
    } else {
      disconnectWebSocket()
    }

    return () => {
      disconnectWebSocket()
      setRetryCount(0)
      setConnectionError(null)
    }
  }, [isStreaming, logSourceId])

  useEffect(() => {
    if (logs.length > 0) {
      scrollToBottom()
    }
  }, [logs])

  const fetchLogSource = async () => {
    try {
      setLoading(true)
      setRetryCount(0)
      const data = await logSourceService.getLogSource(parseInt(logSourceId!))
      setLogSource(data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch log source details')
    } finally {
      setLoading(false)
    }
  }

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    setConnectionStatus('connecting')
    setConnectionError(null)

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/api/v1/follow/${logSourceId}`
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        // Connection is established but waiting for server confirmation
        setConnectionStatus('connecting')
        setConnectionError(null)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'connection_established') {
            setConnectionStatus('connected')
            setConnectionError(null)
            setRetryCount(0)
            startPingInterval()
          } else if (data.type === 'log') {
            const logEntry: LogEntry = {
              id: data.id || Date.now().toString(),
              timestamp: data.timestamp || new Date().toISOString(),
              level: data.level || 'INFO',
              message: data.message || '',
              source: data.source || 'unknown',
              trace_id: data.trace_id,
              span_id: data.span_id,
              data: data.data || {},
              metadata: data.metadata || {}
            }

            setLogs(prevLogs => {
              const newLogs = [...prevLogs, logEntry]
              return newLogs.slice(-1000)
            })
          } else if (data.type === 'error') {
            if (data.message === 'Authentication failed') {
              handleAuthenticationError()
            } else {
              setConnectionError(data.message)
              setConnectionStatus('error')
            }
          }
        } catch (err) {
          // Ignore WebSocket message parsing errors
        }
      }

      ws.onclose = (event) => {
        setConnectionStatus('disconnected')
        stopPingInterval()
        if (isStreaming && event.code !== 1000) {
          if (event.code === 1008) {
            handleAuthenticationError()
          } else {
            scheduleReconnect()
          }
        }
      }

      ws.onerror = (error) => {
        setConnectionStatus('error')
        setConnectionError('WebSocket connection error')
      }

    } catch (err) {
      setConnectionStatus('error')
      setConnectionError('Failed to create WebSocket connection')
    }
  }

  const handleAuthenticationError = async () => {
    try {
      if (retryCount >= maxRetries) {
        setConnectionStatus('error')
        setConnectionError('Maximum authentication retries exceeded. Please log in again or refresh the page.')
        setIsStreaming(false)
        return
      }

      setConnectionStatus('connecting')
      setConnectionError(`Authentication failed, refreshing token... (Attempt ${retryCount + 1}/${maxRetries})`)
      
      await authService.refreshToken()
      setRetryCount(prev => prev + 1)
      
      setTimeout(() => {
        if (isStreaming) {
          connectWebSocket()
        }
      }, 1000)
    } catch (refreshError) {
      setConnectionStatus('error')
      setConnectionError('Token refresh failed. Please log in again or refresh the page.')
      setIsStreaming(false)
    }
  }

  const disconnectWebSocket = () => {
    stopPingInterval()
    clearReconnectTimeout()
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User requested disconnect')
      wsRef.current = null
    }
    
    setConnectionStatus('disconnected')
    setConnectionError(null)
  }

  const startPingInterval = () => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
    }
    
    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)
  }

  const stopPingInterval = () => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
      pingIntervalRef.current = null
    }
  }

  const scheduleReconnect = () => {
    clearReconnectTimeout()
    if (retryCount < maxRetries) {
      reconnectTimeoutRef.current = setTimeout(() => {
        if (isStreaming) {
          setRetryCount(prev => prev + 1)
          connectWebSocket()
        }
      }, 5000)
    } else {
      setConnectionStatus('error')
      setConnectionError('Maximum reconnection attempts exceeded')
      setIsStreaming(false)
    }
  }

  const clearReconnectTimeout = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }

  const scrollToBottom = () => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop = logsContainerRef.current.scrollHeight
    }
  }

  const toggleLog = (logId: string) => {
    setExpandedLogs(prev => {
      const newSet = new Set(prev)
      if (newSet.has(logId)) {
        newSet.delete(logId)
      } else {
        newSet.add(logId)
      }
      return newSet
    })
  }

  const isLogExpanded = (logId: string) => {
    return expandedLogs.has(logId)
  }

  const handleBack = () => {
    navigate(`/dashboard/log-sources/${logSourceId}`)
  }

  const toggleStreaming = () => {
    if (isStreaming) {
      setIsStreaming(false)
      setRetryCount(0)
      setConnectionError(null)
    } else {
      setIsStreaming(true)
      setRetryCount(0)
      setConnectionError(null)
    }
  }

  const handleManualReconnect = () => {
    if (isStreaming) {
      setRetryCount(0)
      setConnectionError(null)
      connectWebSocket()
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'text-red-700'
      case 'ERROR':
        return 'text-red-500'
      case 'WARN':
        return 'text-yellow-500'
      case 'INFO':
        return 'text-blue-500'
      case 'DEBUG':
        return 'text-gray-500'
      default:
        return 'text-gray-500'
    }
  }

  const getLevelBgColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return isDark ? 'bg-red-700/30' : 'bg-red-100'
      case 'ERROR':
        return isDark ? 'bg-red-500/20' : 'bg-red-50'
      case 'WARN':
        return isDark ? 'bg-yellow-500/20' : 'bg-yellow-50'
      case 'INFO':
        return isDark ? 'bg-blue-500/20' : 'bg-blue-50'
      case 'DEBUG':
        return isDark ? 'bg-gray-500/20' : 'bg-gray-50'
      default:
        return isDark ? 'bg-gray-500/20' : 'bg-gray-50'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3
    })
  }

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-green-500'
      case 'connecting':
        return 'text-yellow-500'
      case 'error':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected'
      case 'connecting':
        return 'Connecting...'
      case 'error':
        return 'Connection Error'
      default:
        return 'Disconnected'
    }
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

      <div className={`rounded-lg border ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'}`}>
        <div className={`px-6 py-4 border-b ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Live Log Stream
              </h2>
              <div className={`flex items-center space-x-2 ${getConnectionStatusColor()}`}>
                <div className={`w-2 h-2 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 
                  connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
                  connectionStatus === 'error' ? 'bg-red-500' : 'bg-gray-500'
                }`}></div>
                <span className="text-sm font-medium">
                  {getConnectionStatusText()}
                </span>
                {retryCount > 0 && (
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'
                  }`}>
                    Retry {retryCount}/{maxRetries}
                  </span>
                )}
              </div>
              {connectionError && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-red-500">
                    {connectionError}
                  </span>
                  {connectionStatus === 'error' && isStreaming && (
                    <button
                      onClick={handleManualReconnect}
                      className={`px-3 py-1 rounded text-xs font-medium transition-all duration-200 ${
                        isDark 
                          ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                          : 'bg-blue-500 hover:bg-blue-600 text-white'
                      }`}
                    >
                      Retry
                    </button>
                  )}
                </div>
              )}
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={toggleStreaming}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isStreaming
                    ? isDark 
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-red-500 hover:bg-red-600 text-white'
                    : isDark
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-green-500 hover:bg-green-600 text-white'
                }`}
              >
                {isStreaming ? 'Stop' : 'Start'}
              </button>
              <button
                onClick={() => setLogs([])}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isDark 
                    ? 'bg-gray-600 hover:bg-gray-700 text-white' 
                    : 'bg-gray-500 hover:bg-gray-600 text-white'
                }`}
              >
                Clear
              </button>
            </div>
          </div>
        </div>

        <div 
          ref={logsContainerRef}
          className={`max-h-96 overflow-y-auto ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}
        >
          {logs.length === 0 ? (
            <div className="p-8 text-center">
              <div className={`text-lg ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                {isStreaming ? 'Waiting for logs...' : 'No logs available'}
              </div>
              {!isStreaming && (
                <p className={`text-sm mt-2 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  Click "Start" to begin streaming logs
                </p>
              )}
            </div>
          ) : (
            <div className="p-4 space-y-2">
              {logs.map((log, index) => (
                <div
                  key={log.id}
                  className={`border rounded-lg transition-all duration-500 ease-out transform ${
                    isDark ? 'border-gray-700 hover:bg-gray-800' : 'border-gray-200 hover:bg-white'
                  } ${
                    index === logs.length - 1 
                      ? 'animate-slideInFromBottom opacity-100 translate-y-0' 
                      : 'opacity-100'
                  }`}
                >
                  <button
                    onClick={() => toggleLog(log.id)}
                    className={`w-full text-left flex items-center space-x-4 p-3 border-b transition-colors duration-200 ${
                      isDark ? 'border-gray-700 bg-gray-800 hover:bg-gray-700' : 'border-gray-200 bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className={`flex-shrink-0 w-20 text-xs font-mono ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      {formatTimestamp(log.timestamp)}
                    </div>
                    <div className={`flex-shrink-0 px-2 py-1 rounded text-xs font-semibold ${getLevelBgColor(log.level)} ${getLevelColor(log.level)}`}>
                      {log.level}
                    </div>
                    <div className={`flex-1 text-sm font-mono ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>
                      {log.message}
                    </div>
                    <svg
                      className={`w-4 h-4 transition-transform duration-200 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}
                      style={{
                        transform: isLogExpanded(log.id) ? 'rotate(180deg)' : 'rotate(0deg)'
                      }}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {log.data && Object.keys(log.data).length > 0 && isLogExpanded(log.id) && (
                    <div className={`border-t ${isDark ? 'border-gray-700 bg-gray-800/50' : 'border-gray-200 bg-gray-50'}`}>
                      <div className="p-3">
                        <div className={`text-xs font-semibold ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                          Data:
                        </div>
                        <div className="mt-2 space-y-1">
                          {Object.entries(log.data).map(([key, value]) => (
                            <div key={key} className="flex items-start space-x-2">
                              <span className={`text-xs font-mono ${isDark ? 'text-blue-400' : 'text-blue-600'}`}>
                                {key}:
                              </span>
                              <span className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                                {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {log.metadata && Object.keys(log.metadata).length > 0 && isLogExpanded(log.id) && (
                    <div className={`border-t ${isDark ? 'border-gray-700 bg-gray-800/30' : 'border-gray-200 bg-gray-100'}`}>
                      <div className="p-3">
                        <div className={`text-xs font-semibold ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                          Metadata:
                        </div>
                        <div className="mt-2 space-y-1">
                          {Object.entries(log.metadata).map(([key, value]) => (
                            <div key={key} className="flex items-start space-x-2">
                              <span className={`text-xs font-mono ${isDark ? 'text-purple-400' : 'text-purple-600'}`}>
                                {key}:
                              </span>
                              <span className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                                {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {(log.trace_id || log.span_id) && isLogExpanded(log.id) && (
                    <div className={`border-t ${isDark ? 'border-gray-700 bg-gray-800/20' : 'border-gray-200 bg-gray-50'}`}>
                      <div className="p-3">
                        <div className={`text-xs font-semibold ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                          Trace:
                        </div>
                        <div className="mt-2 space-y-1">
                          {log.trace_id && (
                            <div className="flex items-start space-x-2">
                              <span className={`text-xs font-mono ${isDark ? 'text-cyan-400' : 'text-cyan-600'}`}>
                                trace_id:
                              </span>
                              <span className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                                {log.trace_id}
                              </span>
                            </div>
                          )}
                          {log.span_id && (
                            <div className="flex items-start space-x-2">
                              <span className={`text-xs font-mono ${isDark ? 'text-cyan-400' : 'text-cyan-600'}`}>
                                span_id:
                              </span>
                              <span className={`text-xs ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                                {log.span_id}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className={`px-6 py-3 border-t ${isDark ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-50'}`}>
          <div className="flex items-center justify-between text-sm">
            <span className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Showing {logs.length} log entries
            </span>
            <span className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Last updated: {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LogSourceLogsPage