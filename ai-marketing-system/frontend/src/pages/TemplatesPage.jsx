import { useState, useEffect } from 'react'
import { templatesAPI } from '../services/api'
import toast from 'react-hot-toast'
import { 
  Mail, Plus, Edit, Trash2, Copy, Eye, Save, X, 
  FileText, CheckCircle, AlertCircle 
} from 'lucide-react'

export default function TemplatesPage() {
  const [templates, setTemplates] = useState([])
  const [categories, setCategories] = useState([])
  const [variables, setVariables] = useState({})
  const [loading, setLoading] = useState(false)
  const [showEditor, setShowEditor] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [previewHtml, setPreviewHtml] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [filterCategory, setFilterCategory] = useState('all')

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'general',
    subject: '',
    html_content: '',
    plain_text_content: '',
    is_active: true,
    is_default: false,
  })

  useEffect(() => {
    fetchTemplates()
    fetchCategories()
    fetchVariables()
  }, [filterCategory])

  const fetchTemplates = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterCategory !== 'all') params.category = filterCategory
      const response = await templatesAPI.getAll(params)
      setTemplates(response.data)
    } catch (error) {
      toast.error('Failed to fetch templates')
    } finally {
      setLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await templatesAPI.getCategories()
      setCategories(response.data.categories)
    } catch (error) {
      console.error('Failed to fetch categories')
    }
  }

  const fetchVariables = async () => {
    try {
      const response = await templatesAPI.getVariables()
      setVariables(response.data)
    } catch (error) {
      console.error('Failed to fetch variables')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (selectedTemplate) {
        await templatesAPI.update(selectedTemplate.id, formData)
        toast.success('Template updated successfully!')
      } else {
        await templatesAPI.create(formData)
        toast.success('Template created successfully!')
      }
      setShowEditor(false)
      resetForm()
      fetchTemplates()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save template')
    }
  }

  const handleEdit = (template) => {
    setSelectedTemplate(template)
    setFormData({
      name: template.name,
      description: template.description || '',
      category: template.category,
      subject: template.subject,
      html_content: template.html_content,
      plain_text_content: template.plain_text_content || '',
      is_active: template.is_active,
      is_default: template.is_default,
    })
    setShowEditor(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this template?')) return

    try {
      await templatesAPI.delete(id)
      toast.success('Template deleted successfully!')
      fetchTemplates()
    } catch (error) {
      toast.error('Failed to delete template')
    }
  }

  const handleDuplicate = async (id) => {
    try {
      await templatesAPI.duplicate(id)
      toast.success('Template duplicated successfully!')
      fetchTemplates()
    } catch (error) {
      toast.error('Failed to duplicate template')
    }
  }

  const handlePreview = async (template) => {
    try {
      const response = await templatesAPI.render({
        template_id: template.id,
        variables: {
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          sport_type: 'cycling',
          customer_type: 'athlete',
        },
      })
      setPreviewHtml(response.data.html_content)
      setShowPreview(true)
    } catch (error) {
      toast.error('Failed to preview template')
    }
  }

  const resetForm = () => {
    setSelectedTemplate(null)
    setFormData({
      name: '',
      description: '',
      category: 'general',
      subject: '',
      html_content: '',
      plain_text_content: '',
      is_active: true,
      is_default: false,
    })
  }

  const insertVariable = (variable) => {
    const textarea = document.getElementById('html_content')
    const cursorPos = textarea.selectionStart
    const textBefore = formData.html_content.substring(0, cursorPos)
    const textAfter = formData.html_content.substring(cursorPos)
    const newText = textBefore + `{{${variable}}}` + textAfter
    setFormData({ ...formData, html_content: newText })
    setTimeout(() => {
      textarea.focus()
      textarea.setSelectionRange(cursorPos + variable.length + 4, cursorPos + variable.length + 4)
    }, 0)
  }

  const getCategoryBadgeColor = (category) => {
    const colors = {
      welcome: 'bg-blue-100 text-blue-700',
      promotional: 'bg-green-100 text-green-700',
      newsletter: 'bg-purple-100 text-purple-700',
      transactional: 'bg-orange-100 text-orange-700',
      general: 'bg-gray-100 text-gray-700',
    }
    return colors[category] || colors.general
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Email Templates</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">
            Create and manage reusable email templates
          </p>
        </div>
        <button
          onClick={() => {
            resetForm()
            setShowEditor(true)
          }}
          className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={20} className="mr-2" />
          New Template
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-3 sm:p-4 border border-gray-100">
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <button
            onClick={() => setFilterCategory('all')}
            className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors flex-shrink-0 ${
              filterCategory === 'all'
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat.value}
              onClick={() => setFilterCategory(cat.value)}
              className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0 ${
                filterCategory === cat.value
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Templates List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : templates.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-6 sm:p-8 lg:p-12 text-center border border-gray-100">
          <Mail className="w-10 h-10 sm:w-12 sm:h-12 mx-auto text-gray-400 mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">
            No templates found
          </h3>
          <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6 px-4 sm:px-0">
            Create your first email template to get started
          </p>
          <button
            onClick={() => {
              resetForm()
              setShowEditor(true)
            }}
            className="inline-flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm sm:text-base"
          >
            <Plus size={18} className="mr-2" />
            Create Template
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {templates.map((template) => (
            <div
              key={template.id}
              className="bg-white rounded-xl shadow-sm p-4 sm:p-6 border border-gray-100 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-3 sm:mb-4">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <h3 className="text-base sm:text-lg font-semibold text-gray-900">
                      {template.name}
                    </h3>
                    {template.is_default && (
                      <span className="px-2 py-0.5 sm:py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded">
                        Default
                      </span>
                    )}
                  </div>
                  <span
                    className={`inline-block px-2 py-0.5 sm:py-1 text-xs font-medium rounded ${getCategoryBadgeColor(
                      template.category
                    )}`}
                  >
                    {template.category}
                  </span>
                </div>
                {template.is_active ? (
                  <CheckCircle size={18} className="text-green-500 sm:w-5 sm:h-5" />
                ) : (
                  <AlertCircle size={18} className="text-gray-400 sm:w-5 sm:h-5" />
                )}
              </div>

              {template.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {template.description}
                </p>
              )}

              <div className="text-xs text-gray-500 mb-4">
                <p className="font-medium mb-1">Subject:</p>
                <p className="italic line-clamp-1">{template.subject}</p>
              </div>

              <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                <span>Used: {template.usage_count} times</span>
                {template.last_used_at && (
                  <span>
                    Last used: {new Date(template.last_used_at).toLocaleDateString()}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-1 sm:gap-2">
                <button
                  onClick={() => handlePreview(template)}
                  className="flex-1 inline-flex items-center justify-center px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-xs sm:text-sm"
                >
                  <Eye size={14} className="mr-1 sm:w-4 sm:h-4" />
                  <span className="hidden xs:inline">Preview</span>
                </button>
                <button
                  onClick={() => handleEdit(template)}
                  className="p-1.5 sm:px-3 sm:py-2 bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors"
                >
                  <Edit size={14} className="sm:w-4 sm:h-4" />
                </button>
                <button
                  onClick={() => handleDuplicate(template.id)}
                  className="p-1.5 sm:px-3 sm:py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  <Copy size={14} className="sm:w-4 sm:h-4" />
                </button>
                <button
                  onClick={() => handleDelete(template.id)}
                  className="p-1.5 sm:px-3 sm:py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                >
                  <Trash2 size={14} className="sm:w-4 sm:h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Template Editor Modal */}
      {showEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
              <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900">
                {selectedTemplate ? 'Edit Template' : 'Create Template'}
              </h2>
              <button
                onClick={() => {
                  setShowEditor(false)
                  resetForm()
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 sm:space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Template Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., Welcome Email"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category *
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) =>
                      setFormData({ ...formData, category: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    {categories.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Brief description of this template"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Subject *
                </label>
                <input
                  type="text"
                  required
                  value={formData.subject}
                  onChange={(e) =>
                    setFormData({ ...formData, subject: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Welcome to {{company_name}}, {{first_name}}!"
                />
              </div>

              {/* Variables Helper */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm font-medium text-blue-900 mb-2">
                  Available Variables:
                </p>
                <div className="flex flex-wrap gap-2">
                  {variables.variables &&
                    Object.keys(variables.variables).map((varName) => (
                      <button
                        key={varName}
                        type="button"
                        onClick={() => insertVariable(varName)}
                        className="px-3 py-1 bg-white border border-blue-300 text-blue-700 rounded text-xs hover:bg-blue-100 transition-colors"
                        title={variables.variables[varName]}
                      >
                        {`{{${varName}}}`}
                      </button>
                    ))}
                </div>
                {variables.examples && (
                  <div className="mt-2 text-xs text-blue-700">
                    <p className="font-medium">Examples:</p>
                    <p>Simple: {variables.examples.simple}</p>
                    <p>With default: {variables.examples.with_default}</p>
                    <p>With filter: {variables.examples.with_filter}</p>
                  </div>
                )}
              </div>

              {/* HTML Content */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  HTML Content *
                </label>
                <textarea
                  id="html_content"
                  required
                  value={formData.html_content}
                  onChange={(e) =>
                    setFormData({ ...formData, html_content: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                  rows={15}
                  placeholder="Enter your HTML email content here. Use {{variable_name}} for dynamic content."
                />
                <p className="text-xs text-gray-500 mt-1">
                  Click variable buttons above to insert them at cursor position
                </p>
              </div>

              {/* Options */}
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) =>
                      setFormData({ ...formData, is_active: e.target.checked })
                    }
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Active</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_default}
                    onChange={(e) =>
                      setFormData({ ...formData, is_default: e.target.checked })
                    }
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">
                    Set as default for this category
                  </span>
                </label>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-4 pt-4 border-t border-gray-200">
                <button
                  type="submit"
                  className="flex-1 inline-flex items-center justify-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                >
                  <Save size={20} className="mr-2" />
                  {selectedTemplate ? 'Update Template' : 'Create Template'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowEditor(false)
                    resetForm()
                  }}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
              <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900">Template Preview</h2>
              <button
                onClick={() => {
                  setShowPreview(false)
                  setPreviewHtml('')
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-gray-50">
              <div
                className="bg-white rounded-lg shadow-sm p-3 sm:p-4"
                dangerouslySetInnerHTML={{ __html: previewHtml }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

