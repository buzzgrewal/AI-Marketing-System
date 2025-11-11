import { useState, useEffect } from 'react'
import { retargetingAPI } from '../services/api'
import {
  Target, Users, Plus, Trash2, Eye, TrendingUp, DollarSign,
  MousePointerClick, Activity, Zap, RefreshCw, Play, Pause
} from 'lucide-react'

export default function RetargetingPage() {
  const [audiences, setAudiences] = useState([])
  const [campaigns, setCampaigns] = useState([])
  const [eventStats, setEventStats] = useState(null)
  const [selectedAudience, setSelectedAudience] = useState(null)
  const [selectedCampaign, setSelectedCampaign] = useState(null)
  const [activeTab, setActiveTab] = useState('audiences') // audiences, campaigns, events
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form states
  const [audienceForm, setAudienceForm] = useState({
    name: '',
    description: '',
    platform: 'meta',
    audience_type: 'custom',
    criteria: {
      sport_type: '',
      customer_type: '',
      status: '',
      events: [],
      timeframe_days: 30,
      exclude_purchasers: false,
      exclude_purchase_days: 30,
      min_engagement_score: 0
    }
  })

  const [campaignForm, setCampaignForm] = useState({
    name: '',
    description: '',
    audience_id: null,
    platform: 'meta',
    budget_daily: 50,
    budget_total: 1000,
    currency: 'USD',
    ad_creative: {
      headline: '',
      primary_text: '',
      description: '',
      call_to_action: 'Learn More'
    }
  })

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const fetchData = async () => {
    try {
      if (activeTab === 'audiences') {
        const response = await retargetingAPI.getAllAudiences()
        setAudiences(response.data)
      } else if (activeTab === 'campaigns') {
        const response = await retargetingAPI.getAllCampaigns()
        setCampaigns(response.data)
      } else if (activeTab === 'events') {
        const response = await retargetingAPI.getEventStats(30)
        setEventStats(response.data)
      }
    } catch (err) {
      console.error('Error fetching data:', err)
    }
  }

  const handleCreateAudience = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await retargetingAPI.createAudience(audienceForm)
      setSuccess('Audience created successfully!')
      setAudienceForm({
        name: '',
        description: '',
        platform: 'meta',
        audience_type: 'custom',
        criteria: {
          sport_type: '',
          customer_type: '',
          status: '',
          events: [],
          timeframe_days: 30,
          exclude_purchasers: false,
          exclude_purchase_days: 30,
          min_engagement_score: 0
        }
      })
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create audience')
    } finally {
      setLoading(false)
    }
  }

  const handleSyncAudience = async (audienceId) => {
    setLoading(true)
    setError('')

    try {
      await retargetingAPI.syncAudience(audienceId)
      setSuccess('Audience sync started! This may take a few minutes.')
      setTimeout(fetchData, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to sync audience')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteAudience = async (audienceId) => {
    if (!confirm('Are you sure you want to delete this audience?')) return

    try {
      await retargetingAPI.deleteAudience(audienceId)
      setSuccess('Audience deleted successfully!')
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete audience')
    }
  }

  const handleCreateCampaign = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await retargetingAPI.createCampaign(campaignForm)
      setSuccess('Campaign created successfully!')
      setCampaignForm({
        name: '',
        description: '',
        audience_id: null,
        platform: 'meta',
        budget_daily: 50,
        budget_total: 1000,
        currency: 'USD',
        ad_creative: {
          headline: '',
          primary_text: '',
          description: '',
          call_to_action: 'Learn More'
        }
      })
      setActiveTab('campaigns')
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create campaign')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleCampaign = async (campaignId, currentStatus) => {
    try {
      if (currentStatus === 'active') {
        await retargetingAPI.pauseCampaign(campaignId)
        setSuccess('Campaign paused')
      } else {
        await retargetingAPI.activateCampaign(campaignId)
        setSuccess('Campaign activated')
      }
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update campaign')
    }
  }

  const handleDeleteCampaign = async (campaignId) => {
    if (!confirm('Are you sure you want to delete this campaign?')) return

    try {
      await retargetingAPI.deleteCampaign(campaignId)
      setSuccess('Campaign deleted successfully!')
      fetchData()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete campaign')
    }
  }

  const handleEventTypeToggle = (eventType) => {
    const currentEvents = audienceForm.criteria.events || []
    const newEvents = currentEvents.includes(eventType)
      ? currentEvents.filter(e => e !== eventType)
      : [...currentEvents, eventType]

    setAudienceForm({
      ...audienceForm,
      criteria: {
        ...audienceForm.criteria,
        events: newEvents
      }
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ad Retargeting</h1>
          <p className="text-gray-600 mt-1">Build audiences and run retargeting campaigns on Meta and Google</p>
        </div>
        <button
          onClick={() => setActiveTab(activeTab === 'audiences' ? 'create-audience' : 'create-campaign')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} />
          {activeTab === 'audiences' ? 'New Audience' : 'New Campaign'}
        </button>
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
          {success}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('audiences')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'audiences' || activeTab === 'create-audience'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Users size={16} />
              Audiences
            </div>
          </button>
          <button
            onClick={() => setActiveTab('campaigns')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'campaigns' || activeTab === 'create-campaign'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Target size={16} />
              Campaigns
            </div>
          </button>
          <button
            onClick={() => setActiveTab('events')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'events'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Activity size={16} />
              Events
            </div>
          </button>
        </nav>
      </div>

      {/* Audiences Tab */}
      {activeTab === 'audiences' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {audiences.map((audience) => (
            <div
              key={audience.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-200"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{audience.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{audience.description}</p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  audience.status === 'active' ? 'bg-green-100 text-green-800' :
                  audience.status === 'syncing' ? 'bg-blue-100 text-blue-800' :
                  audience.status === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {audience.status}
                </span>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Platform</span>
                  <span className="text-sm font-medium text-gray-900 capitalize">{audience.platform}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Audience Size</span>
                  <span className="text-sm font-medium text-gray-900">{audience.actual_size.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Last Synced</span>
                  <span className="text-sm font-medium text-gray-900">
                    {audience.last_sync_at
                      ? new Date(audience.last_sync_at).toLocaleDateString()
                      : 'Never'}
                  </span>
                </div>
              </div>

              {audience.error_message && (
                <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                  {audience.error_message}
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={() => handleSyncAudience(audience.id)}
                  disabled={loading || audience.status === 'syncing'}
                  className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  <RefreshCw size={14} className="inline mr-1" />
                  Sync
                </button>
                <button
                  onClick={() => handleDeleteAudience(audience.id)}
                  className="px-3 py-2 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}

          {audiences.length === 0 && (
            <div className="col-span-3 text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <Users size={48} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Audiences Yet</h3>
              <p className="text-gray-600 mb-4">Create your first retargeting audience to get started</p>
              <button
                onClick={() => setActiveTab('create-audience')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Audience
              </button>
            </div>
          )}
        </div>
      )}

      {/* Create Audience Tab */}
      {activeTab === 'create-audience' && (
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Retargeting Audience</h2>

            <form onSubmit={handleCreateAudience} className="space-y-6">
              {/* Basic Info */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Audience Name *
                  </label>
                  <input
                    type="text"
                    value={audienceForm.name}
                    onChange={(e) => setAudienceForm({ ...audienceForm, name: e.target.value })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={audienceForm.description}
                    onChange={(e) => setAudienceForm({ ...audienceForm, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Platform
                    </label>
                    <select
                      value={audienceForm.platform}
                      onChange={(e) => setAudienceForm({ ...audienceForm, platform: e.target.value })}
                      className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="meta">Meta (Facebook/Instagram)</option>
                      <option value="google">Google Ads</option>
                      <option value="both">Both Platforms</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Audience Type
                    </label>
                    <select
                      value={audienceForm.audience_type}
                      onChange={(e) => setAudienceForm({ ...audienceForm, audience_type: e.target.value })}
                      className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="custom">Custom Audience</option>
                      <option value="lookalike">Lookalike Audience</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Audience Criteria */}
              <div className="border-t pt-6 space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Audience Criteria</h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Event-Based Targeting
                  </label>
                  <p className="text-sm text-gray-600 mb-3">
                    Target users who performed specific events within the timeframe
                  </p>

                  <div className="grid grid-cols-2 gap-3">
                    {['page_view', 'add_to_cart', 'purchase', 'lead', 'signup'].map(eventType => (
                      <label key={eventType} className="flex items-center gap-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={audienceForm.criteria.events.includes(eventType)}
                          onChange={() => handleEventTypeToggle(eventType)}
                          className="form-checkbox h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700 capitalize">{eventType.replace('_', ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timeframe (days)
                  </label>
                  <input
                    type="number"
                    value={audienceForm.criteria.timeframe_days}
                    onChange={(e) => setAudienceForm({
                      ...audienceForm,
                      criteria: { ...audienceForm.criteria, timeframe_days: parseInt(e.target.value) }
                    })}
                    min="1"
                    max="180"
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">Target users who performed events in the last X days</p>
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={audienceForm.criteria.exclude_purchasers}
                      onChange={(e) => setAudienceForm({
                        ...audienceForm,
                        criteria: { ...audienceForm.criteria, exclude_purchasers: e.target.checked }
                      })}
                      className="w-4 h-4 rounded text-blue-600 bg-white border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:ring-offset-0 accent-blue-600"
                    />
                    <span className="text-sm text-gray-700">Exclude recent purchasers</span>
                  </label>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end gap-3 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => setActiveTab('audiences')}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Audience'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="bg-white rounded-lg shadow-md p-6 border border-gray-200"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{campaign.description}</p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                  campaign.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {campaign.status}
                </span>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-500">Impressions</p>
                  <p className="text-xl font-bold text-gray-900">{campaign.impressions.toLocaleString()}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-500">Clicks</p>
                  <p className="text-xl font-bold text-gray-900">{campaign.clicks.toLocaleString()}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-500">CTR</p>
                  <p className="text-xl font-bold text-blue-600">{campaign.ctr.toFixed(2)}%</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-500">ROAS</p>
                  <p className="text-xl font-bold text-green-600">{campaign.roas.toFixed(2)}x</p>
                </div>
              </div>

              <div className="space-y-2 mb-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Spend</span>
                  <span className="font-medium">${campaign.spend.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Revenue</span>
                  <span className="font-medium text-green-600">${campaign.revenue.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Conversions</span>
                  <span className="font-medium">{campaign.conversions}</span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleToggleCampaign(campaign.id, campaign.status)}
                  className={`flex-1 px-3 py-2 text-sm rounded ${
                    campaign.status === 'active'
                      ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                      : 'bg-green-100 text-green-700 hover:bg-green-200'
                  }`}
                >
                  {campaign.status === 'active' ? (
                    <>
                      <Pause size={14} className="inline mr-1" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play size={14} className="inline mr-1" />
                      Activate
                    </>
                  )}
                </button>
                <button
                  onClick={() => handleDeleteCampaign(campaign.id)}
                  className="px-3 py-2 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}

          {campaigns.length === 0 && (
            <div className="col-span-2 text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <Target size={48} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Campaigns Yet</h3>
              <p className="text-gray-600 mb-4">Create your first retargeting campaign</p>
              <button
                onClick={() => setActiveTab('create-campaign')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Campaign
              </button>
            </div>
          )}
        </div>
      )}

      {/* Events Tab */}
      {activeTab === 'events' && eventStats && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Events</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{eventStats.total_events.toLocaleString()}</p>
                </div>
                <Activity size={40} className="text-blue-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Conversion Value</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">${eventStats.total_conversion_value.toFixed(2)}</p>
                </div>
                <DollarSign size={40} className="text-green-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Event Types</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {Object.keys(eventStats.events_by_type).length}
                  </p>
                </div>
                <Zap size={40} className="text-purple-500" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Type (Last 30 Days)</h3>
            <div className="space-y-3">
              {Object.entries(eventStats.events_by_type).map(([eventType, count]) => (
                <div key={eventType} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {eventType.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">{count.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
