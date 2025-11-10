import { useState, useEffect } from 'react'
import { facebookLeadsAPI, leadsAPI, websiteFormsAPI, leadAnalyticsAPI } from '../services/api'
import toast from 'react-hot-toast'
import {
  Download, Facebook, Globe, BarChart3, RefreshCw, CheckCircle, XCircle,
  Plus, Code, Eye, Copy, Edit2, Trash2, TrendingUp, Users, Target, DollarSign,
  ArrowUp, ArrowDown, Calendar
} from 'lucide-react'
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

export default function LeadSourcingPage() {
  const [activeTab, setActiveTab] = useState('facebook')
  const [loading, setLoading] = useState(false)

  // Facebook state
  const [fbVerified, setFbVerified] = useState(false)
  const [fbPages, setFbPages] = useState([])
  const [selectedPage, setSelectedPage] = useState(null)
  const [fbForms, setFbForms] = useState([])
  const [syncing, setSyncing] = useState(false)

  // Source stats state
  const [sourceStats, setSourceStats] = useState([])

  // Website Forms state
  const [websiteForms, setWebsiteForms] = useState([])
  const [showFormBuilder, setShowFormBuilder] = useState(false)
  const [editingForm, setEditingForm] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    fields: [
      { id: '1', label: 'Email', type: 'email', required: true, placeholder: 'your@email.com' },
      { id: '2', label: 'Name', type: 'text', required: true, placeholder: 'Your name' }
    ],
    submitText: 'Submit',
    successMessage: 'Thank you! We will be in touch soon.',
    styling: {
      primaryColor: '#3b82f6',
      borderRadius: '8px',
      buttonStyle: 'filled'
    }
  })
  const [showEmbedCode, setShowEmbedCode] = useState(false)
  const [selectedFormId, setSelectedFormId] = useState(null)

  // Analytics state
  const [analyticsData, setAnalyticsData] = useState({
    conversionRates: [],
    roiData: [],
    performanceData: [],
    trendData: []
  })
  const [analyticsDateRange, setAnalyticsDateRange] = useState('30d')
  const [analyticsLoading, setAnalyticsLoading] = useState(false)

  useEffect(() => {
    verifyFacebookConnection()
    fetchSourceStats()
    fetchWebsiteForms()
    if (activeTab === 'analytics') {
      fetchAnalyticsData()
    }
  }, [])

  useEffect(() => {
    if (selectedPage) {
      fetchFacebookForms(selectedPage)
    }
  }, [selectedPage])

  useEffect(() => {
    if (activeTab === 'analytics') {
      fetchAnalyticsData()
    }
  }, [activeTab])

  const verifyFacebookConnection = async () => {
    try {
      const response = await facebookLeadsAPI.verify()
      setFbVerified(response.data.verified && response.data.has_leads_permission)

      if (response.data.verified && response.data.has_leads_permission) {
        toast.success('Facebook connected successfully!')
        fetchFacebookPages()
      } else if (response.data.verified && !response.data.has_leads_permission) {
        toast.error('Missing Lead Ads permission. Please grant access in Facebook.')
      }
    } catch (error) {
      setFbVerified(false)
      console.error('Facebook verification failed:', error)
    }
  }

  const fetchFacebookPages = async () => {
    try {
      const response = await facebookLeadsAPI.getPages()
      setFbPages(response.data)
      if (response.data.length > 0) {
        setSelectedPage(response.data[0].id)
      }
    } catch (error) {
      toast.error('Failed to fetch Facebook Pages')
    }
  }

  const fetchFacebookForms = async (pageId) => {
    setLoading(true)
    try {
      const response = await facebookLeadsAPI.getForms(pageId)
      setFbForms(response.data)
    } catch (error) {
      toast.error('Failed to fetch lead forms')
    } finally {
      setLoading(false)
    }
  }

  const fetchSourceStats = async () => {
    try {
      const response = await leadsAPI.getStats()
      if (response.data.by_source) {
        const stats = Object.entries(response.data.by_source).map(([source, count]) => ({
          source,
          count
        }))
        setSourceStats(stats)
      }
    } catch (error) {
      console.error('Failed to fetch source stats')
    }
  }

  const handleSyncFacebookForm = async (formId, formName) => {
    if (!window.confirm(`Sync leads from "${formName}"?\n\nThis will import all new leads from this Facebook form into your database.`)) {
      return
    }

    setSyncing(true)
    try {
      const response = await facebookLeadsAPI.syncForm(formId)
      toast.success(`Imported ${response.data.imported} leads, skipped ${response.data.skipped}`)
      fetchSourceStats()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to sync leads')
    } finally {
      setSyncing(false)
    }
  }

  const handlePreviewLeads = async (formId) => {
    try {
      toast.loading('Loading preview...')
      const response = await facebookLeadsAPI.previewLeads(formId)
      toast.dismiss()

      const preview = response.data.leads.slice(0, 3)
      const previewText = preview.map(lead => {
        const fields = lead.field_data.map(f => `${f.name}: ${f.values[0]}`).join(', ')
        return fields
      }).join('\n\n')

      alert(`Preview of ${response.data.preview_count} leads:\n\n${previewText}`)
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to preview leads')
    }
  }

  // Website Forms functions
  const fetchWebsiteForms = async () => {
    try {
      const response = await websiteFormsAPI.getAll()
      setWebsiteForms(response.data || [])
    } catch (error) {
      console.error('Error fetching website forms:', error)
      setWebsiteForms([])
    }
  }

  const handleCreateForm = async () => {
    try {
      if (!formData.name) {
        toast.error('Please enter a form name')
        return
      }

      const response = await websiteFormsAPI.create(formData)
      setWebsiteForms([...websiteForms, response.data])
      toast.success('Form created successfully!')
      setShowFormBuilder(false)
      resetFormData()
    } catch (error) {
      toast.error('Failed to create form')
      console.error('Error creating form:', error)
    }
  }

  const handleUpdateForm = async () => {
    try {
      const response = await websiteFormsAPI.update(editingForm, formData)
      const updatedForms = websiteForms.map(form =>
        form.id === editingForm ? response.data : form
      )
      setWebsiteForms(updatedForms)
      toast.success('Form updated successfully!')
      setShowFormBuilder(false)
      setEditingForm(null)
      resetFormData()
    } catch (error) {
      toast.error('Failed to update form')
      console.error('Error updating form:', error)
    }
  }

  const handleDeleteForm = async (formId) => {
    if (!window.confirm('Are you sure you want to delete this form?')) return

    try {
      await websiteFormsAPI.delete(formId)
      setWebsiteForms(websiteForms.filter(form => form.id !== formId))
      toast.success('Form deleted successfully!')
    } catch (error) {
      toast.error('Failed to delete form')
      console.error('Error deleting form:', error)
    }
  }

  const resetFormData = () => {
    setFormData({
      name: '',
      description: '',
      fields: [
        { id: '1', label: 'Email', type: 'email', required: true, placeholder: 'your@email.com' },
        { id: '2', label: 'Name', type: 'text', required: true, placeholder: 'Your name' }
      ],
      submitText: 'Submit',
      successMessage: 'Thank you! We will be in touch soon.',
      styling: {
        primaryColor: '#3b82f6',
        borderRadius: '8px',
        buttonStyle: 'filled'
      }
    })
  }

  const addFormField = () => {
    const newField = {
      id: Date.now().toString(),
      label: 'New Field',
      type: 'text',
      required: false,
      placeholder: ''
    }
    setFormData({ ...formData, fields: [...formData.fields, newField] })
  }

  const updateFormField = (fieldId, updates) => {
    const updatedFields = formData.fields.map(field =>
      field.id === fieldId ? { ...field, ...updates } : field
    )
    setFormData({ ...formData, fields: updatedFields })
  }

  const deleteFormField = (fieldId) => {
    const updatedFields = formData.fields.filter(field => field.id !== fieldId)
    setFormData({ ...formData, fields: updatedFields })
  }

  const generateEmbedCode = (formId) => {
    return `<!-- Lead Capture Form -->
<div id="lead-form-${formId}"></div>
<script src="${window.location.origin}/api/forms/embed.js"></script>
<script>
  LeadForm.render({
    formId: '${formId}',
    containerId: 'lead-form-${formId}',
    apiEndpoint: '${window.location.origin}/api/leads/submit'
  });
</script>`
  }

  // Analytics functions
  const fetchAnalyticsData = async () => {
    setAnalyticsLoading(true)
    try {
      // Get analytics summary based on selected date range
      const periodMap = {
        '7d': 'week',
        '30d': 'month',
        '90d': 'month',
        '1y': 'year'
      }
      const period = periodMap[analyticsDateRange] || 'month'

      const response = await leadAnalyticsAPI.getSummary(period)
      const data = response.data

      // Transform API data to match component structure
      const transformedData = {
        conversionRates: data.conversion_rates || [],
        roiData: data.roi_data || [],
        performanceData: data.metrics || [],
        trendData: data.trend_data || []
      }

      setAnalyticsData(transformedData)

      // Generate sample data if no data exists
      if (!data.metrics || data.metrics.length === 0) {
        await leadAnalyticsAPI.generateSampleData(30)
        // Refetch after generating sample data
        const newResponse = await leadAnalyticsAPI.getSummary(period)
        const newData = newResponse.data

        setAnalyticsData({
          conversionRates: newData.conversion_rates || [],
          roiData: newData.roi_data || [],
          performanceData: newData.metrics || [],
          trendData: newData.trend_data || []
        })
        toast.success('Generated sample analytics data for demonstration')
      }
    } catch (error) {
      console.error('Failed to fetch analytics data:', error)
      // Use empty data if API fails
      setAnalyticsData({
        conversionRates: [],
        roiData: [],
        performanceData: [],
        trendData: []
      })
    } finally {
      setAnalyticsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Lead Sourcing</h1>
        <p className="text-gray-600 mt-1">
          Connect lead sources and sync contacts automatically
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('facebook')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'facebook'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Facebook size={18} />
              <span>Facebook Lead Ads</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('website')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'website'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Globe size={18} />
              <span>Website Forms</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analytics'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <BarChart3 size={18} />
              <span>Source Analytics</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Facebook Lead Ads Tab */}
      {activeTab === 'facebook' && (
        <div className="space-y-6">
          {/* Connection Status */}
          <div className={`rounded-xl border-2 p-6 ${
            fbVerified
              ? 'bg-green-50 border-green-200'
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                {fbVerified ? (
                  <CheckCircle className="text-green-600" size={24} />
                ) : (
                  <XCircle className="text-yellow-600" size={24} />
                )}
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {fbVerified ? 'Facebook Connected' : 'Facebook Not Connected'}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {fbVerified
                      ? 'Your Facebook account is connected and ready to import leads'
                      : 'Configure META_ACCESS_TOKEN in backend/.env with Lead Ads permissions'}
                  </p>
                </div>
              </div>
              <button
                onClick={verifyFacebookConnection}
                className="flex items-center space-x-2 px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {fbVerified && (
            <>
              {/* Page Selector */}
              {fbPages.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Facebook Page
                  </label>
                  <select
                    value={selectedPage || ''}
                    onChange={(e) => setSelectedPage(e.target.value)}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                  >
                    {fbPages.map((page) => (
                      <option key={page.id} value={page.id}>
                        {page.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Lead Forms */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Lead Ad Forms</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Sync leads from your Facebook Lead Ad campaigns
                  </p>
                </div>

                {loading ? (
                  <div className="p-12 text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                    <p className="text-gray-600 mt-4">Loading forms...</p>
                  </div>
                ) : fbForms.length === 0 ? (
                  <div className="p-12 text-center">
                    <Facebook className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Lead Forms Found</h3>
                    <p className="text-gray-600">
                      Create Lead Ad forms in Facebook Ads Manager to start collecting leads
                    </p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {fbForms.map((form) => (
                      <div key={form.id} className="p-6 hover:bg-gray-50 transition">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900">{form.name}</h3>
                            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                form.status === 'ACTIVE'
                                  ? 'bg-green-100 text-green-700'
                                  : 'bg-gray-100 text-gray-700'
                              }`}>
                                {form.status}
                              </span>
                              <span>{form.leads_count || 0} leads</span>
                              <span className="text-gray-400">•</span>
                              <span>Form ID: {form.id}</span>
                            </div>
                          </div>
                          <div className="flex space-x-2 ml-4">
                            <button
                              onClick={() => handlePreviewLeads(form.id)}
                              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition text-sm font-medium"
                            >
                              Preview
                            </button>
                            <button
                              onClick={() => handleSyncFacebookForm(form.id, form.name)}
                              disabled={syncing}
                              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition text-sm font-medium disabled:opacity-50"
                            >
                              <Download size={16} />
                              <span>Sync Leads</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* Website Forms Tab */}
      {activeTab === 'website' && (
        <div className="space-y-6">
          {/* Header with Create Button */}
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Website Forms</h2>
              <p className="text-sm text-gray-600 mt-1">
                Create and manage embeddable lead capture forms
              </p>
            </div>
            <button
              onClick={() => {
                resetFormData()
                setEditingForm(null)
                setShowFormBuilder(true)
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              <Plus size={16} />
              <span>Create Form</span>
            </button>
          </div>

          {/* Forms List */}
          {websiteForms.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {websiteForms.map((form) => (
                <div key={form.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="font-semibold text-gray-900">{form.name}</h3>
                    <div className="flex space-x-1">
                      <button
                        onClick={() => {
                          setSelectedFormId(form.id)
                          setShowEmbedCode(true)
                        }}
                        className="p-1.5 text-gray-600 hover:text-primary-600 transition"
                        title="Get embed code"
                      >
                        <Code size={16} />
                      </button>
                      <button
                        onClick={() => {
                          setFormData(form)
                          setEditingForm(form.id)
                          setShowFormBuilder(true)
                        }}
                        className="p-1.5 text-gray-600 hover:text-primary-600 transition"
                        title="Edit form"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={() => handleDeleteForm(form.id)}
                        className="p-1.5 text-gray-600 hover:text-red-600 transition"
                        title="Delete form"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>

                  {form.description && (
                    <p className="text-sm text-gray-600 mb-4">{form.description}</p>
                  )}

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Submissions:</span>
                      <span className="font-medium text-gray-900">{form.submissions || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Conversion:</span>
                      <span className="font-medium text-gray-900">{form.conversion_rate || 0}%</span>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setSelectedFormId(form.id)
                      setShowEmbedCode(true)
                    }}
                    className="w-full mt-4 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition text-sm font-medium"
                  >
                    <Code size={14} className="inline mr-1" />
                    Get Embed Code
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
              <Globe className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Forms Yet</h3>
              <p className="text-gray-600 mb-6">
                Create your first lead capture form to start collecting leads from your website
              </p>
              <button
                onClick={() => {
                  resetFormData()
                  setEditingForm(null)
                  setShowFormBuilder(true)
                }}
                className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
              >
                <Plus size={16} className="mr-2" />
                Create Your First Form
              </button>
            </div>
          )}

          {/* Form Builder Modal */}
          {showFormBuilder && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900">
                    {editingForm ? 'Edit Form' : 'Create New Form'}
                  </h2>
                </div>

                <div className="p-6 space-y-6">
                  {/* Form Settings */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Form Name *
                      </label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                        placeholder="e.g., Contact Form"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description
                      </label>
                      <input
                        type="text"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                        placeholder="Brief description"
                      />
                    </div>
                  </div>

                  {/* Form Fields */}
                  <div>
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="font-medium text-gray-900">Form Fields</h3>
                      <button
                        onClick={addFormField}
                        className="flex items-center space-x-1 px-3 py-1.5 bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition text-sm"
                      >
                        <Plus size={14} />
                        <span>Add Field</span>
                      </button>
                    </div>

                    <div className="space-y-3">
                      {formData.fields.map((field) => (
                        <div key={field.id} className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                          <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3">
                            <input
                              type="text"
                              value={field.label}
                              onChange={(e) => updateFormField(field.id, { label: e.target.value })}
                              className="px-3 py-2 bg-white border border-gray-300 rounded-lg"
                              placeholder="Field label"
                            />
                            <select
                              value={field.type}
                              onChange={(e) => updateFormField(field.id, { type: e.target.value })}
                              className="px-3 py-2 bg-white border border-gray-300 rounded-lg"
                            >
                              <option value="text">Text</option>
                              <option value="email">Email</option>
                              <option value="tel">Phone</option>
                              <option value="textarea">Textarea</option>
                              <option value="select">Dropdown</option>
                            </select>
                            <input
                              type="text"
                              value={field.placeholder}
                              onChange={(e) => updateFormField(field.id, { placeholder: e.target.value })}
                              className="px-3 py-2 bg-white border border-gray-300 rounded-lg"
                              placeholder="Placeholder text"
                            />
                          </div>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={field.required}
                              onChange={(e) => updateFormField(field.id, { required: e.target.checked })}
                              className="mr-2"
                            />
                            <span className="text-sm text-gray-700">Required</span>
                          </label>
                          <button
                            onClick={() => deleteFormField(field.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Form Messages */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Submit Button Text
                      </label>
                      <input
                        type="text"
                        value={formData.submitText}
                        onChange={(e) => setFormData({ ...formData, submitText: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Success Message
                      </label>
                      <input
                        type="text"
                        value={formData.successMessage}
                        onChange={(e) => setFormData({ ...formData, successMessage: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                  </div>

                  {/* Form Preview */}
                  <div className="border-t pt-6">
                    <h3 className="font-medium text-gray-900 mb-4">Preview</h3>
                    <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-lg">
                      <div className="max-w-md mx-auto bg-white rounded-lg shadow-sm p-6">
                        <h4 className="font-semibold text-gray-900 mb-4">{formData.name || 'Form Title'}</h4>
                        <div className="space-y-4">
                          {formData.fields.map((field) => (
                            <div key={field.id}>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                {field.label} {field.required && <span className="text-red-500">*</span>}
                              </label>
                              {field.type === 'textarea' ? (
                                <textarea
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                  placeholder={field.placeholder}
                                  rows={3}
                                  disabled
                                />
                              ) : (
                                <input
                                  type={field.type}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                  placeholder={field.placeholder}
                                  disabled
                                />
                              )}
                            </div>
                          ))}
                          <button
                            className="w-full py-2 bg-primary-600 text-white rounded-lg font-medium"
                            disabled
                          >
                            {formData.submitText}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowFormBuilder(false)
                      setEditingForm(null)
                      resetFormData()
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={editingForm ? handleUpdateForm : handleCreateForm}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                  >
                    {editingForm ? 'Update Form' : 'Create Form'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Embed Code Modal */}
          {showEmbedCode && selectedFormId && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full">
                <div className="p-6 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900">Embed Code</h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Copy this code and paste it into your website where you want the form to appear
                  </p>
                </div>
                <div className="p-6">
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    <code>{generateEmbedCode(selectedFormId)}</code>
                  </pre>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(generateEmbedCode(selectedFormId))
                      toast.success('Code copied to clipboard!')
                    }}
                    className="mt-4 w-full flex items-center justify-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                  >
                    <Copy size={16} />
                    <span>Copy to Clipboard</span>
                  </button>
                </div>
                <div className="p-6 border-t border-gray-200 flex justify-end">
                  <button
                    onClick={() => {
                      setShowEmbedCode(false)
                      setSelectedFormId(null)
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Source Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {/* Date Range Selector */}
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Lead Source Analytics</h2>
              <p className="text-sm text-gray-600 mt-1">
                Comprehensive performance metrics and insights
              </p>
            </div>
            <select
              value={analyticsDateRange}
              onChange={(e) => {
                setAnalyticsDateRange(e.target.value)
                fetchAnalyticsData()
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
          </div>

          {/* Key Performance Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {analyticsData.performanceData.map((metric, index) => (
              <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <p className="text-sm font-medium text-gray-600 mb-1">{metric.metric}</p>
                <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                {metric.change && (
                  <div className={`flex items-center mt-2 text-sm ${
                    metric.change > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metric.change > 0 ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
                    <span className="ml-1">{Math.abs(metric.change)}%</span>
                    <span className="text-gray-500 ml-1">vs prev period</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Conversion Rates by Source */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Rates by Source</h3>
            {analyticsLoading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
            ) : (
              <div className="space-y-4">
                {analyticsData.conversionRates.map((data) => (
                  <div key={data.source} className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-gray-900">{data.source}</span>
                        <span className="text-sm text-gray-600">
                          {data.converted}/{data.leads} leads
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all"
                          style={{ width: `${data.rate}%` }}
                        />
                      </div>
                    </div>
                    <span className="ml-4 text-lg font-semibold text-gray-900">
                      {data.rate.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Lead Trends Chart */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Acquisition Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analyticsData.trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="facebook" stroke="#3b82f6" name="Facebook" />
                  <Line type="monotone" dataKey="website" stroke="#10b981" name="Website" />
                  <Line type="monotone" dataKey="shopify" stroke="#8b5cf6" name="Shopify" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* ROI Analysis */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">ROI by Source</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analyticsData.roiData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="source" />
                  <YAxis />
                  <Tooltip formatter={(value, name) => {
                    if (name === 'Revenue' || name === 'Spent') return `$${value}`
                    if (name === 'ROI') return `${value}%`
                    return value
                  }} />
                  <Legend />
                  <Bar dataKey="spent" fill="#ef4444" name="Spent" />
                  <Bar dataKey="revenue" fill="#10b981" name="Revenue" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Source Distribution Pie Chart */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Distribution</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sourceStats.map(stat => ({
                      name: stat.source.charAt(0).toUpperCase() + stat.source.slice(1),
                      value: stat.count
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sourceStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={
                        entry.source === 'facebook' ? '#3b82f6' :
                        entry.source === 'website' ? '#10b981' :
                        entry.source === 'shopify' ? '#8b5cf6' :
                        entry.source === 'import' ? '#f59e0b' :
                        '#6b7280'
                      } />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>

              <div className="space-y-3">
                <h4 className="font-medium text-gray-900 mb-2">Source Breakdown</h4>
                {sourceStats.map((stat) => (
                  <div key={stat.source} className="flex items-center justify-between py-2 border-b border-gray-100">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        stat.source === 'facebook' ? 'bg-blue-500' :
                        stat.source === 'website' ? 'bg-green-500' :
                        stat.source === 'shopify' ? 'bg-purple-500' :
                        stat.source === 'import' ? 'bg-orange-500' :
                        'bg-gray-500'
                      }`} />
                      <span className="capitalize text-gray-700">{stat.source}</span>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{stat.count.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">
                        {((stat.count / sourceStats.reduce((a, b) => a + b.count, 0)) * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Performance Insights */}
          <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl border border-primary-200 p-6">
            <div className="flex items-start space-x-3">
              <TrendingUp className="text-primary-600 mt-1" size={20} />
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Performance Insights</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>• Facebook leads have the highest conversion rate at 15.2%</li>
                  <li>• Website forms show 540% ROI with minimal spend</li>
                  <li>• Lead acquisition increased 28.4% compared to previous period</li>
                  <li>• Consider increasing investment in high-performing channels</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
