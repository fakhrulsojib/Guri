export const formatEnumValue = (value: string): string => {
  if (!value) return value
  
  return value
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

export const formatLogSourceType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'application': 'Application',
    'system': 'System',
    'security': 'Security',
    'audit': 'Audit',
    'performance': 'Performance',
    'custom': 'Custom'
  }
  return typeMap[type] || formatEnumValue(type)
}

export const formatEnvironment = (env: string): string => {
  const envMap: Record<string, string> = {
    'development': 'Development',
    'staging': 'Staging',
    'production': 'Production',
    'testing': 'Testing'
  }
  return envMap[env] || formatEnumValue(env)
}

export const formatStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    'active': 'Active',
    'inactive': 'Inactive',
    'suspended': 'Suspended',
    'deleted': 'Deleted'
  }
  return statusMap[status] || formatEnumValue(status)
} 