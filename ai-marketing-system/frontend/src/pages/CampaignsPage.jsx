import { useState, useEffect } from 'react'
import { campaignsAPI, templatesAPI, segmentsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { Mail, Send, Plus, FileText, Users } from 'lucide-react'

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([])
  const [templates, setTemplates] = useState([])
  const [segments, setSegments] = useState([])
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [useTemplate, setUseTemplate] = useState(false)
  const [useSegment, setUseSegment] = useState(false)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    campaign_type: 'email',
    subject: '',
    content: '',
    template_id: null,
    segment_id: null,
    target_sport_type: '',
  })

  useEffect(() => {
    fetchCampaigns()
    fetchTemplates()
    fetchSegments()
  }, [])

  const fetchCampaigns = async () => {
    setLoading(true)
    try {
      const response = await campaignsAPI.getAll()
      setCampaigns(response.data)
    } catch (error) {
      toast.error('Failed to fetch campaigns')
    } finally {
      setLoading(false)
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await templatesAPI.getAll({ is_active: true })
      setTemplates(response.data)
    } catch (error) {
      console.error('Failed to fetch templates')
    }
  }

  const fetchSegments = async () => {
    try {
      const response = await segmentsAPI.list()
      setSegments(response)
    } catch (error) {
      console.error('Failed to fetch segments')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Prepare data - if using template, clear custom content
    const submitData = { ...formData }
    if (useTemplate && submitData.template_id) {
      // When using template, backend will use template content
      submitData.content = ''
      submitData.subject = '' // Template has its own subject
    } else {
      submitData.template_id = null
    }
    
    // If using segment, clear sport type filter (segment takes precedence)
    if (useSegment && submitData.segment_id) {
      submitData.target_sport_type = ''
    } else {
      submitData.segment_id = null
    }
    
    try {
      await campaignsAPI.create(submitData)
      toast.success('Campaign created successfully!')
      setShowForm(false)
      setFormData({
        name: '',
        description: '',
        campaign_type: 'email',
        subject: '',
        content: '',
        template_id: null,
        segment_id: null,
        target_sport_type: '',
      })
      setUseTemplate(false)
      setUseSegment(false)
      fetchCampaigns()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create campaign')
    }
  }

  const handleSendCampaign = async (id) => {
    if (
      !window.confirm(
        'Are you sure you want to send this campaign to all targeted leads?'
      )
    ) {
      return
    }

    try {
      const response = await campaignsAPI.send(id)
      toast.success(
        `Campaign is being sent to ${response.data.total_recipients} recipients!`
      )
      fetchCampaigns()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send campaign')
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-blue-100 text-blue-700'
      case 'completed':
        return 'bg-green-100 text-green-700'
      case 'draft':
        return 'bg-gray-100 text-gray-700'
      case 'scheduled':
        return 'bg-purple-100 text-purple-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">
            Manage your email marketing campaigns
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:shadow-lg transition-all font-medium"
        >
          <Plus size={20} />
          <span>New Campaign</span>
        </button>
      </div>

      {/* Campaign Form */}
      {showForm && (
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm p-5 sm:p-6 border border-gray-200">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">
            Create New Campaign
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Campaign Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
                placeholder="e.g., Spring Sale Announcement"
                className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 placeholder-gray-400 transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={2}
                placeholder="Brief description of this campaign..."
                className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 placeholder-gray-400 transition-all resize-none"
              />
            </div>

            {/* Template Toggle */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-3 mb-2">
                <FileText size={20} className="text-blue-600" />
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useTemplate}
                    onChange={(e) => {
                      setUseTemplate(e.target.checked)
                      if (e.target.checked) {
                        setFormData({ ...formData, subject: '', content: '' })
                      } else {
                        setFormData({ ...formData, template_id: null })
                      }
                    }}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm font-medium text-gray-900">
                    Use Email Template
                  </span>
                </label>
              </div>
              <p className="text-xs text-blue-700">
                {useTemplate 
                  ? 'Select a pre-designed template below. Variables will be automatically filled for each recipient.'
                  : 'Check this box to use a saved email template instead of custom content.'}
              </p>
            </div>

            {useTemplate ? (
              /* Template Selection */
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Template *
                </label>
                <select
                  value={formData.template_id || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, template_id: parseInt(e.target.value) || null })
                  }
                  required={useTemplate}
                  className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 transition-all"
                >
                  <option value="">Choose a template...</option>
                  {templates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name} ({template.category})
                    </option>
                  ))}
                </select>
                {templates.length === 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    No templates available. Create one in Email Templates first.
                  </p>
                )}
              </div>
            ) : (
              /* Custom Content */
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Subject *
                  </label>
                  <input
                    type="text"
                    value={formData.subject}
                    onChange={(e) =>
                      setFormData({ ...formData, subject: e.target.value })
                    }
                    required={!useTemplate}
                    placeholder="Your email subject line..."
                    className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 placeholder-gray-400 transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Content *
                  </label>
                  <textarea
                    value={formData.content}
                    onChange={(e) =>
                      setFormData({ ...formData, content: e.target.value })
                    }
                    required={!useTemplate}
                    rows={8}
                    placeholder="Write your email content here... You can use HTML for formatting."
                    className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none font-mono text-sm text-gray-900 placeholder-gray-400 transition-all resize-none"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    💡 Tip: Use the Content Generator to create AI-powered email content
                  </p>
                </div>
              </>
            )}

            {/* Segment Selection */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center gap-3 mb-2">
                <Users size={20} className="text-purple-600" />
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useSegment}
                    onChange={(e) => {
                      setUseSegment(e.target.checked)
                      if (e.target.checked) {
                        setFormData({ ...formData, target_sport_type: '' })
                      } else {
                        setFormData({ ...formData, segment_id: null })
                      }
                    }}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm font-medium text-gray-900">
                    Target Specific Segment
                  </span>
                </label>
              </div>
              <p className="text-xs text-purple-700">
                {useSegment 
                  ? 'Select a pre-defined lead segment to target specific audiences.'
                  : 'Check this box to use advanced segmentation instead of basic sport type filtering.'}
              </p>
            </div>

            {useSegment ? (
              /* Segment Selection */
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Segment *
                </label>
                <select
                  value={formData.segment_id || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, segment_id: parseInt(e.target.value) || null })
                  }
                  required={useSegment}
                  className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 transition-all"
                >
                  <option value="">Choose a segment...</option>
                  {segments.map((segment) => (
                    <option key={segment.id} value={segment.id}>
                      {segment.name} ({segment.lead_count} leads)
                    </option>
                  ))}
                </select>
                {segments.length === 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    No segments available. Create one in Lead Segments first.
                  </p>
                )}
              </div>
            ) : (
              /* Basic Sport Type Filter */
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Sport Type (Optional)
                </label>
                <select
                  value={formData.target_sport_type}
                  onChange={(e) =>
                    setFormData({ ...formData, target_sport_type: e.target.value })
                  }
                  className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 transition-all"
                >
                  <option value="">All Sports</option>
                  <option value="cycling">🚴 Cycling</option>
                  <option value="triathlon">🏊 Triathlon</option>
                  <option value="running">🏃 Running</option>
                </select>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <button
                type="submit"
                className="flex-1 flex items-center justify-center space-x-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white py-3 px-4 rounded-lg hover:shadow-lg transition-all font-medium"
              >
                <Mail size={18} />
                <span>Create Campaign</span>
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="sm:w-auto px-6 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Campaigns List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:gap-6">
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="bg-white rounded-xl sm:rounded-2xl shadow-sm p-5 sm:p-6 border border-gray-100 hover:shadow-lg transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-4">
                <div className="flex-1">
                  <div className="flex items-start flex-wrap gap-2 mb-2">
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900">
                      {campaign.name}
                    </h3>
                    <span
                      className={`px-2.5 py-1 text-xs font-semibold rounded-lg ${getStatusColor(
                        campaign.status
                      )}`}
                    >
                      {campaign.status}
                    </span>
                  </div>
                  {campaign.description && (
                    <p className="text-sm sm:text-base text-gray-600 mb-2">{campaign.description}</p>
                  )}
                  <p className="text-xs sm:text-sm text-gray-500">
                    Subject: <span className="font-medium text-gray-900">{campaign.subject}</span>
                  </p>
                </div>

                {campaign.status === 'draft' && (
                  <button
                    onClick={() => handleSendCampaign(campaign.id)}
                    className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:shadow-lg transition-all font-medium whitespace-nowrap"
                  >
                    <Send size={18} />
                    <span>Send Campaign</span>
                  </button>
                )}
              </div>

              {/* Campaign Stats */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 pt-4 border-t border-gray-100">
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Recipients</p>
                  <p className="text-lg sm:text-xl font-bold text-gray-900">
                    {campaign.total_recipients || 0}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Sent</p>
                  <p className="text-lg sm:text-xl font-bold text-gray-900">
                    {campaign.total_sent || 0}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Delivered</p>
                  <p className="text-lg sm:text-xl font-bold text-gray-900">
                    {campaign.total_delivered || 0}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Opened</p>
                  <p className="text-lg sm:text-xl font-bold text-emerald-600">
                    {campaign.total_opened || 0}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Clicked</p>
                  <p className="text-lg sm:text-xl font-bold text-indigo-600">
                    {campaign.total_clicked || 0}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && campaigns.length === 0 && (
        <div className="text-center py-12 sm:py-16 bg-gradient-to-br from-white to-gray-50 rounded-2xl border-2 border-dashed border-gray-300">
          <div className="max-w-md mx-auto px-4">
            <div className="inline-flex p-4 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl mb-4">
              <Mail className="h-10 w-10 sm:h-12 sm:w-12 text-primary-600" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-2">
              No campaigns yet
            </h3>
            <p className="text-sm sm:text-base text-gray-600 mb-6">
              Create your first email campaign to reach your opted-in leads
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:shadow-lg transition-all font-medium"
            >
              <Plus size={20} />
              <span>Create Your First Campaign</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
