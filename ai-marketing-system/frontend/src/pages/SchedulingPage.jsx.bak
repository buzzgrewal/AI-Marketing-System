import { useState, useEffect } from 'react'
import { scheduleAPI, contentAPI } from '../services/api'
import toast from 'react-hot-toast'
import {
  Calendar,
  Clock,
  Plus,
  Send,
  Edit,
  Trash2,
  Eye,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle,
  Facebook,
  Instagram,
  Twitter,
  Linkedin,
  TrendingUp,
} from 'lucide-react'

const platformIcons = {
  facebook: Facebook,
  instagram: Instagram,
  twitter: Twitter,
  linkedin: Linkedin,
}

const platformColors = {
  facebook: 'bg-blue-100 text-blue-700 border-blue-200',
  instagram: 'bg-pink-100 text-pink-700 border-pink-200',
  twitter: 'bg-sky-100 text-sky-700 border-sky-200',
  linkedin: 'bg-indigo-100 text-indigo-700 border-indigo-200',
}

export default function SchedulingPage() {
  const [scheduledPosts, setScheduledPosts] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [viewMode, setViewMode] = useState('list') // list or calendar
  const [filterStatus, setFilterStatus] = useState('scheduled')
  const [filterPlatform, setFilterPlatform] = useState('all')

  const [formData, setFormData] = useState({
    platform: 'facebook',
    post_text: '',
    image_url: '',
    hashtags: '',
    scheduled_time: '',
    timezone: 'UTC',
    auto_post: true,
  })

  useEffect(() => {
    fetchScheduledPosts()
    fetchStats()
  }, [filterStatus, filterPlatform])

  const fetchScheduledPosts = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filterStatus !== 'all') params.status = filterStatus
      if (filterPlatform !== 'all') params.platform = filterPlatform
      const response = await scheduleAPI.getAll(params)
      setScheduledPosts(response.data)
    } catch (error) {
      toast.error('Failed to fetch scheduled posts')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await scheduleAPI.getStats()
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await scheduleAPI.create(formData)
      toast.success('Post scheduled successfully!')
      setShowForm(false)
      setFormData({
        platform: 'facebook',
        post_text: '',
        image_url: '',
        hashtags: '',
        scheduled_time: '',
        timezone: 'UTC',
        auto_post: true,
      })
      fetchScheduledPosts()
      fetchStats()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to schedule post')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Cancel this scheduled post?')) return

    try {
      await scheduleAPI.delete(id)
      toast.success('Post cancelled successfully!')
      fetchScheduledPosts()
      fetchStats()
    } catch (error) {
      toast.error('Failed to cancel post')
    }
  }

  const handlePostNow = async (id) => {
    if (!window.confirm('Post this immediately?')) return

    try {
      await scheduleAPI.postNow(id)
      toast.success('Posting now...')
      fetchScheduledPosts()
    } catch (error) {
      toast.error('Failed to post')
    }
  }

  const handleRefreshMetrics = async (id) => {
    try {
      const response = await scheduleAPI.refreshMetrics(id)
      toast.success('Metrics updated!')
      fetchScheduledPosts()
    } catch (error) {
      toast.error('Failed to refresh metrics')
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      scheduled: {
        color: 'bg-yellow-100 text-yellow-700 border-yellow-200',
        icon: Clock,
        text: 'Scheduled',
      },
      posting: {
        color: 'bg-blue-100 text-blue-700 border-blue-200',
        icon: RefreshCw,
        text: 'Posting...',
      },
      posted: {
        color: 'bg-green-100 text-green-700 border-green-200',
        icon: CheckCircle,
        text: 'Posted',
      },
      failed: {
        color: 'bg-red-100 text-red-700 border-red-200',
        icon: XCircle,
        text: 'Failed',
      },
      cancelled: {
        color: 'bg-gray-100 text-gray-700 border-gray-200',
        icon: AlertCircle,
        text: 'Cancelled',
      },
    }

    const badge = badges[status] || badges.scheduled
    const Icon = badge.icon

    return (
      <span
        className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium border ${badge.color}`}
      >
        <Icon size={12} />
        {badge.text}
      </span>
    )
  }

  const formatDateTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  }

  const isUpcoming = (scheduledTime) => {
    return new Date(scheduledTime) > new Date()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Social Media Scheduling</h1>
          <p className="text-gray-600 mt-1">
            Schedule and manage your social media posts
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={20} className="mr-2" />
          Schedule Post
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Scheduled</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.total_scheduled}
                </p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Clock size={24} className="text-yellow-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Posted</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.total_posted}
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle size={24} className="text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">This Week</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.upcoming_week}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Calendar size={24} className="text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Failed</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.total_failed}
                </p>
              </div>
              <div className="p-3 bg-red-100 rounded-lg">
                <XCircle size={24} className="text-red-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Engagement</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.avg_engagement_rate}%
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <TrendingUp size={24} className="text-purple-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-100">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All</option>
              <option value="scheduled">Scheduled</option>
              <option value="posted">Posted</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Platform
            </label>
            <select
              value={filterPlatform}
              onChange={(e) => setFilterPlatform(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Platforms</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
              <option value="twitter">Twitter</option>
              <option value="linkedin">LinkedIn</option>
            </select>
          </div>
        </div>
      </div>

      {/* Posts List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : scheduledPosts.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-gray-100">
          <Calendar size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No scheduled posts found
          </h3>
          <p className="text-gray-600 mb-6">
            Schedule your first social media post to get started
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus size={20} className="mr-2" />
            Schedule Post
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {scheduledPosts.map((post) => {
            const PlatformIcon = platformIcons[post.platform] || Calendar
            const platformColor = platformColors[post.platform] || 'bg-gray-100'

            return (
              <div
                key={post.id}
                className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 ${platformColor} rounded-lg border`}>
                      <PlatformIcon size={20} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 capitalize">
                        {post.platform}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {formatDateTime(post.scheduled_time)}
                      </p>
                    </div>
                  </div>
                  {getStatusBadge(post.status)}
                </div>

                <p className="text-gray-700 mb-3 line-clamp-3">{post.post_text}</p>

                {post.hashtags && (
                  <p className="text-sm text-blue-600 mb-3">{post.hashtags}</p>
                )}

                {post.image_url && (
                  <div className="mb-3">
                    <img
                      src={post.image_url}
                      alt="Post"
                      className="w-full h-48 object-cover rounded-lg"
                    />
                  </div>
                )}

                {post.status === 'posted' && (
                  <div className="bg-gray-50 rounded-lg p-3 mb-3">
                    <div className="grid grid-cols-4 gap-2 text-center">
                      <div>
                        <p className="text-xs text-gray-600">Likes</p>
                        <p className="text-sm font-semibold">{post.likes_count}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Comments</p>
                        <p className="text-sm font-semibold">{post.comments_count}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Shares</p>
                        <p className="text-sm font-semibold">{post.shares_count}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600">Reach</p>
                        <p className="text-sm font-semibold">{post.reach}</p>
                      </div>
                    </div>
                  </div>
                )}

                {post.error_message && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-3">
                    <p className="text-sm text-red-700">{post.error_message}</p>
                  </div>
                )}

                <div className="flex items-center gap-2 flex-wrap">
                  {post.status === 'scheduled' && isUpcoming(post.scheduled_time) && (
                    <>
                      <button
                        onClick={() => handlePostNow(post.id)}
                        className="inline-flex items-center px-3 py-1.5 bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors text-sm"
                      >
                        <Send size={14} className="mr-1" />
                        Post Now
                      </button>
                      <button
                        onClick={() => handleDelete(post.id)}
                        className="inline-flex items-center px-3 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm"
                      >
                        <Trash2 size={14} className="mr-1" />
                        Cancel
                      </button>
                    </>
                  )}

                  {post.status === 'posted' && (
                    <>
                      <button
                        onClick={() => handleRefreshMetrics(post.id)}
                        className="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                      >
                        <RefreshCw size={14} className="mr-1" />
                        Refresh Metrics
                      </button>
                      {post.platform_url && (
                        <a
                          href={post.platform_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm"
                        >
                          <Eye size={14} className="mr-1" />
                          View Post
                        </a>
                      )}
                    </>
                  )}

                  {post.status === 'failed' && (
                    <button
                      onClick={() => handleDelete(post.id)}
                      className="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                    >
                      <Trash2 size={14} className="mr-1" />
                      Remove
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Scheduling Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Schedule Post</h2>
              <button
                onClick={() => setShowForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Platform *
                </label>
                <select
                  value={formData.platform}
                  onChange={(e) =>
                    setFormData({ ...formData, platform: e.target.value })
                  }
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="facebook">Facebook</option>
                  <option value="instagram">Instagram</option>
                  <option value="twitter">Twitter</option>
                  <option value="linkedin">LinkedIn</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Post Text *
                </label>
                <textarea
                  value={formData.post_text}
                  onChange={(e) =>
                    setFormData({ ...formData, post_text: e.target.value })
                  }
                  required
                  rows={5}
                  placeholder="Write your post content..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.post_text.length} characters
                  {formData.platform === 'twitter' && ' (max 280 for Twitter)'}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image URL
                </label>
                <input
                  type="url"
                  value={formData.image_url}
                  onChange={(e) =>
                    setFormData({ ...formData, image_url: e.target.value })
                  }
                  placeholder="https://..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                {formData.platform === 'instagram' && (
                  <p className="text-xs text-orange-600 mt-1">
                    Instagram posts require an image
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hashtags
                </label>
                <input
                  type="text"
                  value={formData.hashtags}
                  onChange={(e) =>
                    setFormData({ ...formData, hashtags: e.target.value })
                  }
                  placeholder="#cycling #triathlon #running"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Scheduled Time *
                </label>
                <input
                  type="datetime-local"
                  value={formData.scheduled_time}
                  onChange={(e) =>
                    setFormData({ ...formData, scheduled_time: e.target.value })
                  }
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="auto_post"
                  checked={formData.auto_post}
                  onChange={(e) =>
                    setFormData({ ...formData, auto_post: e.target.checked })
                  }
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <label htmlFor="auto_post" className="text-sm text-gray-700">
                  Auto-post at scheduled time (uncheck for manual approval)
                </label>
              </div>

              <div className="flex items-center gap-4 pt-4 border-t border-gray-200">
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                >
                  Schedule Post
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

