import { useState, useEffect } from 'react'
import { facebookLeadsAPI, leadsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { Download, Facebook, Globe, BarChart3, RefreshCw, CheckCircle, XCircle } from 'lucide-react'

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

  useEffect(() => {
    verifyFacebookConnection()
    fetchSourceStats()
  }, [])

  useEffect(() => {
    if (selectedPage) {
      fetchFacebookForms(selectedPage)
    }
  }, [selectedPage])

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
                className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm"
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
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Globe className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Website Form Builder</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Create embeddable lead capture forms for your website. Coming next!
          </p>
          <div className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm">
            In Development
          </div>
        </div>
      )}

      {/* Source Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Leads by Source</h2>
              <p className="text-sm text-gray-600 mt-1">
                Overview of where your leads are coming from
              </p>
            </div>

            <div className="p-6">
              {sourceStats.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No lead sources available yet
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {sourceStats.map((stat) => (
                    <div key={stat.source} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <span className={`px-3 py-1 rounded text-sm font-medium capitalize ${
                          stat.source === 'shopify' ? 'bg-purple-100 text-purple-700' :
                          stat.source === 'facebook' ? 'bg-blue-100 text-blue-700' :
                          stat.source === 'website' ? 'bg-green-100 text-green-700' :
                          stat.source === 'import' ? 'bg-orange-100 text-orange-700' :
                          stat.source === 'event' ? 'bg-pink-100 text-pink-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {stat.source}
                        </span>
                        <span className="text-2xl font-bold text-gray-900">{stat.count}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">Total leads</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-dashed border-blue-200 p-8 text-center">
            <BarChart3 className="h-12 w-12 text-blue-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Advanced Analytics Coming Soon</h3>
            <p className="text-gray-600 max-w-md mx-auto">
              Detailed conversion rates, ROI tracking, and source performance analysis will be available soon
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
