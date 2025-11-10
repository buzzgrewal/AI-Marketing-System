import { useState, useEffect } from 'react'
import { leadsAPI, campaignsAPI, contentAPI } from '../services/api'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { TrendingUp, Users, Mail, Sparkles } from 'lucide-react'

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function AnalyticsPage() {
  const [leadsStats, setLeadsStats] = useState(null)
  const [campaignsStats, setCampaignsStats] = useState(null)
  const [contentStats, setContentStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const [leadsRes, campaignsRes, contentRes] = await Promise.all([
        leadsAPI.getStats(),
        campaignsAPI.getOverview(),
        contentAPI.getAll(),
      ])

      setLeadsStats(leadsRes.data)
      setCampaignsStats(campaignsRes.data)

      // Process content stats
      const contents = contentRes.data
      const contentByType = contents.reduce((acc, content) => {
        acc[content.content_type] = (acc[content.content_type] || 0) + 1
        return acc
      }, {})

      const contentByStatus = contents.reduce((acc, content) => {
        acc[content.status] = (acc[content.status] || 0) + 1
        return acc
      }, {})

      setContentStats({
        total: contents.length,
        byType: contentByType,
        byStatus: contentByStatus,
        avgEngagement:
          contents.reduce((sum, c) => sum + (c.engagement_rate || 0), 0) /
            contents.length || 0,
      })
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Check if data is available
  if (!leadsStats || !campaignsStats || !contentStats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-gray-600 text-lg mb-2">No analytics data available</p>
          <p className="text-gray-500 text-sm">Try adding some leads, campaigns, or content first.</p>
        </div>
      </div>
    )
  }

  // Prepare chart data
  const leadsPieData = [
    { name: 'Opted In', value: leadsStats.opted_in || 0 },
    { name: 'Not Opted In', value: (leadsStats.total_leads || 0) - (leadsStats.opted_in || 0) },
  ]

  const campaignPerformanceData = [
    {
      name: 'Sent',
      value: campaignsStats.total_sent || 0,
    },
    {
      name: 'Open Rate',
      value: campaignsStats.avg_open_rate || 0,
    },
    {
      name: 'Click Rate',
      value: campaignsStats.avg_click_rate || 0,
    },
    {
      name: 'Conversion',
      value: campaignsStats.avg_conversion_rate || 0,
    },
  ]

  const contentTypeData = Object.entries(contentStats?.byType || {}).map(
    ([type, count]) => ({
      name: type.replace('_', ' '),
      value: count,
    })
  )

  const metrics = [
    {
      name: 'Total Leads',
      value: leadsStats.total_leads || 0,
      icon: Users,
      color: 'bg-blue-500',
      description: `${leadsStats.opt_in_rate?.toFixed(1) || 0}% opted in`,
    },
    {
      name: 'Campaigns Sent',
      value: campaignsStats.total_campaigns || 0,
      icon: Mail,
      color: 'bg-green-500',
      description: `${campaignsStats.active_campaigns || 0} active`,
    },
    {
      name: 'Content Generated',
      value: contentStats?.total || 0,
      icon: Sparkles,
      color: 'bg-purple-500',
      description: 'AI-powered pieces',
    },
    {
      name: 'Avg Engagement',
      value: `${contentStats?.avgEngagement?.toFixed(1) || 0}%`,
      icon: TrendingUp,
      color: 'bg-orange-500',
      description: 'Social media posts',
    },
  ]

  return (
    <div className="space-y-4 sm:space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm sm:text-base text-gray-600 mt-1">
          Track your marketing performance and insights
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {metrics.map((metric) => (
          <div
            key={metric.name}
            className="bg-white rounded-xl shadow-sm p-4 sm:p-6 border border-gray-200"
          >
            <div className="flex items-center justify-between mb-3 sm:mb-4">
              <div className={`${metric.color} p-2.5 sm:p-3 rounded-lg`}>
                <metric.icon className="text-white" size={20} />
              </div>
              <p className="text-2xl sm:text-3xl font-bold text-gray-900">{metric.value}</p>
            </div>
            <p className="text-sm font-medium text-gray-900">{metric.name}</p>
            <p className="text-xs text-gray-500 mt-1">{metric.description}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Leads Distribution */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Leads Distribution
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={leadsPieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {leadsPieData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Campaign Performance */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Campaign Performance
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={campaignPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Content Generation Stats */}
      {contentTypeData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Content by Type
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={contentTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8b5cf6" name="Count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-sm font-medium text-gray-600 mb-2">
            Lead Quality Score
          </h3>
          <p className="text-3xl font-bold text-gray-900 mb-1">
            {leadsStats.opt_in_rate?.toFixed(1) || 0}%
          </p>
          <p className="text-sm text-gray-500">
            {leadsStats.opted_in || 0} of {leadsStats.total_leads || 0} leads opted in
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-sm font-medium text-gray-600 mb-2">
            Email Performance
          </h3>
          <p className="text-3xl font-bold text-gray-900 mb-1">
            {campaignsStats.avg_open_rate?.toFixed(1) || 0}%
          </p>
          <p className="text-sm text-gray-500">
            Average open rate across campaigns
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-sm font-medium text-gray-600 mb-2">
            Conversion Rate
          </h3>
          <p className="text-3xl font-bold text-gray-900 mb-1">
            {campaignsStats.avg_conversion_rate?.toFixed(1) || 0}%
          </p>
          <p className="text-sm text-gray-500">From campaign recipients</p>
        </div>
      </div>

      {/* Insights */}
      <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6 border border-primary-200">
        <h2 className="text-lg font-bold text-gray-900 mb-4">
          Marketing Insights
        </h2>
        <div className="space-y-3">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">✓</span>
            </div>
            <p className="text-sm text-gray-700">
              Your opt-in rate of {leadsStats.opt_in_rate?.toFixed(1) || 0}% is{' '}
              {(leadsStats.opt_in_rate || 0) > 60 ? 'excellent' : 'good'}. Keep
              maintaining clear consent practices.
            </p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">✓</span>
            </div>
            <p className="text-sm text-gray-700">
              Campaign open rate of {campaignsStats.avg_open_rate?.toFixed(1) || 0}%{' '}
              {(campaignsStats.avg_open_rate || 0) > 20
                ? 'exceeds'
                : 'is approaching'}{' '}
              industry average. Consider A/B testing subject lines.
            </p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">✓</span>
            </div>
            <p className="text-sm text-gray-700">
              Use AI Content Generator more frequently to maintain consistent
              social media presence across platforms.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
