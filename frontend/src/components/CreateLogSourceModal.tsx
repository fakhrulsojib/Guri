import React, { useState } from 'react'
import { logSourceService } from '../services/logSourceService'
import { formatLogSourceType, formatEnvironment } from '../utils/formatters'

interface CreateLogSourceModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  isDark: boolean
  editMode?: boolean
  existingData?: any
}

interface LogSourceFormData {
  name: string
  description: string
  source_type: string
  environment: string
  tags: string[]
}

const CreateLogSourceModal: React.FC<CreateLogSourceModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  isDark,
  editMode = false,
  existingData = null
}) => {
  const [formData, setFormData] = useState<LogSourceFormData>({
    name: '',
    description: '',
    source_type: 'application',
    environment: 'development',
    tags: []
  })
  const [tagInput, setTagInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [focusedField, setFocusedField] = useState<string | null>(null)

  React.useEffect(() => {
    if (isOpen) {
      setError(null)
      setFieldErrors({})
      setFocusedField(null)
      
      if (editMode && existingData) {
        setFormData({
          name: existingData.name || '',
          description: existingData.description || '',
          source_type: existingData.source_type || 'application',
          environment: existingData.environment || 'development',
          tags: existingData.tags || []
        })
      } else {
        setFormData({
          name: '',
          description: '',
          source_type: 'application',
          environment: 'development',
          tags: []
        })
      }
    }
  }, [isOpen, editMode, existingData])

  React.useEffect(() => {
    const uniqueTags = Array.from(new Set(formData.tags))
    if (uniqueTags.length !== formData.tags.length) {
      setFormData(prev => ({
        ...prev,
        tags: uniqueTags
      }))
    }
  }, [formData.tags])

  const sourceTypes = ['application', 'system', 'security', 'audit', 'performance', 'custom']
  const environments = ['development', 'staging', 'production', 'testing']

  const validateForm = () => {
    const errors: Record<string, string> = {}
    
    if (!formData.name.trim()) {
      errors.name = 'Name is required'
    }
    
    if (formData.name.length > 100) {
      errors.name = 'Name must be less than 100 characters'
    }
    
    if (formData.description && formData.description.length > 500) {
      errors.description = 'Description must be less than 500 characters'
    }
    
    if (formData.tags.length > 10) {
      errors.tags = 'Maximum 10 tags allowed'
    }
    
    const uniqueTags = new Set(formData.tags)
    if (uniqueTags.size !== formData.tags.length) {
      errors.tags = 'Duplicate tags are not allowed'
    }
    
    for (const tag of formData.tags) {
      if (tag.length > 20) {
        errors.tags = 'Each tag must be 20 characters or less'
        break
      }
    }
    
    return errors
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const validationErrors = validateForm()
    if (Object.keys(validationErrors).length > 0) {
      setFieldErrors(validationErrors)
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      if (editMode && existingData) {
        await logSourceService.updateLogSource(existingData.id, {
          name: formData.name,
          description: formData.description,
          source_type: formData.source_type,
          environment: formData.environment,
          tags: formData.tags
        })
      } else {
        await logSourceService.createLogSource({
          name: formData.name,
          description: formData.description,
          source_type: formData.source_type,
          environment: formData.environment,
          tags: formData.tags
        })
      }
      
      onSuccess()
      onClose()
      resetForm()
    } catch (err: any) {
      setError(err.message || 'Failed to save log source')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      source_type: 'application',
      environment: 'development',
      tags: []
    })
    setTagInput('')
    setError(null)
    setFieldErrors({})
    setFocusedField(null)
  }

  const addTag = () => {
    const trimmedTag = tagInput.trim()
    
    if (!trimmedTag) {
      return
    }
    
    if (trimmedTag.length > 20) {
      setFieldErrors(prev => ({ ...prev, tags: 'Tag must be 20 characters or less' }))
      return
    }
    
    if (formData.tags.length >= 10) {
      setFieldErrors(prev => ({ ...prev, tags: 'Maximum 10 tags allowed' }))
      return
    }
    
    if (formData.tags.includes(trimmedTag)) {
      setFieldErrors(prev => ({ ...prev, tags: 'Tag already exists' }))
      return
    }
    
    setFormData(prev => ({
      ...prev,
      tags: [...prev.tags, trimmedTag]
    }))
    setTagInput('')
    setFieldErrors(prev => ({ ...prev, tags: '' }))
  }

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addTag()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={`w-full max-w-md mx-4 rounded-lg shadow-xl ${
        isDark ? 'bg-gray-800' : 'bg-white'
      }`}>
        <div className={`px-6 py-4 border-b ${
          isDark ? 'border-gray-700' : 'border-gray-200'
        }`}>
          <h2 className={`text-xl font-semibold ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}>
            {editMode ? 'Edit Log Source' : 'Create Log Source'}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => {
                const value = e.target.value
                if (value.length <= 100) {
                  setFormData(prev => ({ ...prev, name: value }))
                }
                if (fieldErrors.name) {
                  setFieldErrors(prev => ({ ...prev, name: '' }))
                }
              }}
              onFocus={() => setFocusedField('name')}
              onBlur={() => setFocusedField(null)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                fieldErrors.name 
                  ? `border-red-500 focus:ring-red-500 ${isDark ? 'bg-gray-700 text-white placeholder-gray-400' : 'bg-white text-gray-900 placeholder-gray-500'}`
                  : formData.name.length > 100
                    ? `border-yellow-500 focus:ring-yellow-500 ${isDark ? 'bg-gray-700 text-white placeholder-gray-400' : 'bg-white text-gray-900 placeholder-gray-500'}`
                    : isDark 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
              }`}
              placeholder="Enter log source name"
            />
            {focusedField === 'name' && (
              <div className="flex justify-between items-center text-xs mt-1">
                <span className={`${
                  formData.name.length > 100 
                    ? 'text-red-600' 
                    : formData.name.length >= 90 
                      ? 'text-yellow-600' 
                      : isDark 
                        ? 'text-gray-400' 
                        : 'text-gray-500'
                }`}>
                  {formData.name.length}/100 characters
                </span>
              </div>
            )}
            {fieldErrors.name && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.name}</p>
            )}
          </div>

          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => {
                const value = e.target.value
                if (value.length <= 500) {
                  setFormData(prev => ({ ...prev, description: value }))
                }
                if (fieldErrors.description) {
                  setFieldErrors(prev => ({ ...prev, description: '' }))
                }
              }}
              onFocus={() => setFocusedField('description')}
              onBlur={() => setFocusedField(null)}
              rows={3}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                fieldErrors.description 
                  ? `border-red-500 focus:ring-red-500 ${isDark ? 'bg-gray-700 text-white placeholder-gray-400' : 'bg-white text-gray-900 placeholder-gray-500'}`
                  : formData.description.length > 500
                    ? `border-yellow-500 focus:ring-yellow-500 ${isDark ? 'bg-gray-700 text-white placeholder-gray-400' : 'bg-white text-gray-900 placeholder-gray-500'}`
                    : isDark 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
              }`}
              placeholder="Enter description (optional)"
            />
                        {focusedField === 'description' && (
              <div className="flex justify-between items-center text-xs mt-1">
                <span className={`${
                  formData.description.length > 500 
                    ? 'text-red-600' 
                    : formData.description.length >= 450 
                      ? 'text-yellow-600' 
                      : isDark 
                        ? 'text-gray-400' 
                        : 'text-gray-500'
                }`}>
                  {formData.description.length}/500 characters
                </span>
              </div>
            )}
            {fieldErrors.description && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.description}</p>
            )}
          </div>

          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Source Type *
            </label>
            <select
              required
              value={formData.source_type}
              onChange={(e) => {
                setFormData(prev => ({ ...prev, source_type: e.target.value }))
                if (fieldErrors.source_type) {
                  setFieldErrors(prev => ({ ...prev, source_type: '' }))
                }
              }}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                fieldErrors.source_type 
                  ? `border-red-500 focus:ring-red-500 ${isDark ? 'bg-gray-700 text-white' : 'bg-white text-gray-900'}`
                  : isDark 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              {sourceTypes.map(type => (
                <option key={type} value={type}>
                  {formatLogSourceType(type)}
                </option>
              ))}
            </select>
            {fieldErrors.source_type && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.source_type}</p>
            )}
          </div>

          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Environment *
            </label>
            <select
              required
              value={formData.environment}
              onChange={(e) => {
                setFormData(prev => ({ ...prev, environment: e.target.value }))
                if (fieldErrors.environment) {
                  setFieldErrors(prev => ({ ...prev, environment: '' }))
                }
              }}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                fieldErrors.environment 
                  ? `border-red-500 focus:ring-red-500 ${isDark ? 'bg-gray-700 text-white' : 'bg-white text-gray-900'}`
                  : isDark 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              {environments.map(env => (
                <option key={env} value={env}>
                  {formatEnvironment(env)}
                </option>
              ))}
            </select>
            {fieldErrors.environment && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.environment}</p>
            )}
          </div>

          <div>
            <label className={`block text-sm font-medium mb-2 ${
              isDark ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Tags ({formData.tags.length}/10)
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => {
                  const value = e.target.value
                  if (value.length <= 20) {
                    setTagInput(value)
                  }
                  if (fieldErrors.tags) {
                    setFieldErrors(prev => ({ ...prev, tags: '' }))
                  }
                }}
                onFocus={() => setFocusedField('tags')}
                onBlur={() => setFocusedField(null)}
                onKeyPress={handleKeyPress}
                className={`flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  fieldErrors.tags 
                    ? `border-red-500 focus:ring-red-500 ${isDark ? 'bg-gray-700 text-white placeholder-gray-400' : 'bg-white text-gray-900 placeholder-gray-500'}`
                    : tagInput.length >= 20
                      ? `border-yellow-500 focus:ring-yellow-500 ${isDark ? 'bg-gray-700 text-white placeholder-gray-400' : 'bg-white text-gray-900 placeholder-gray-500'}`
                      : isDark 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                }`}
                placeholder="Add a tag"
              />
              <button
                type="button"
                onClick={addTag}
                disabled={formData.tags.length >= 10}
                className={`px-4 py-2 rounded-md font-medium ${
                  formData.tags.length >= 10
                    ? 'bg-gray-400 cursor-not-allowed'
                    : isDark 
                      ? 'bg-gray-600 hover:bg-gray-500 text-white' 
                      : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                }`}
              >
                Add
              </button>
            </div>
            {focusedField === 'tags' && (
              <div className="flex justify-between items-center text-xs">
                <span className={`${
                  tagInput.length >= 18 
                    ? 'text-yellow-600' 
                    : isDark 
                      ? 'text-gray-400' 
                      : 'text-gray-500'
                }`}>
                  {tagInput.length}/20 characters
                </span>
              </div>
            )}
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.tags.map((tag, index) => {
                  const isDuplicate = formData.tags.indexOf(tag) !== index
                  return (
                    <span
                      key={index}
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        isDuplicate
                          ? 'bg-red-100 text-red-800 border border-red-300'
                          : isDark 
                            ? 'bg-gray-600 text-gray-200' 
                            : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {tag}
                      {isDuplicate && (
                        <span className="ml-1 text-red-600 text-xs">⚠</span>
                      )}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="ml-1 text-gray-400 hover:text-gray-600"
                      >
                        ×
                      </button>
                    </span>
                  )
                })}
              </div>
            )}
            {fieldErrors.tags && (
              <p className="mt-1 text-sm text-red-500">{fieldErrors.tags}</p>
            )}
          </div>



          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className={`flex-1 px-4 py-2 border rounded-md font-medium ${
                isDark 
                  ? 'border-gray-600 text-gray-300 hover:bg-gray-700' 
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className={`flex-1 px-4 py-2 rounded-md font-medium ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : isDark
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-blue-500 hover:bg-blue-600'
              } text-white`}
            >
              {loading ? (editMode ? 'Updating...' : 'Creating...') : (editMode ? 'Update Log Source' : 'Create Log Source')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateLogSourceModal 