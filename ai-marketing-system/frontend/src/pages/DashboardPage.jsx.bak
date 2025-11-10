import { useState, useEffect } from 'react'
import { leadsAPI, campaignsAPI } from '../services/api'
import { Users, Mail, TrendingUp, Target } from 'lucide-react'

export default function DashboardPage() {
  const [leadsStats, setLeadsStats] = useState(null)
  const [campaignsStats, setCampaignsStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const [leadsRes, campaignsRes] = await Promise.all([
        leadsAPI.getStats(),
        campaignsAPI.getOverview(),
      ])
      setLeadsStats(leadsRes.data)
      setCampaignsStats(campaignsRes.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
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

  const stats = [
    {
      name: 'Total Leads',
      value: leadsStats?.total_leads || 0,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
    },
    {
      name: 'Opted-in Leads',
      value: leadsStats?.opted_in || 0,
      icon: Target,
      color: 'bg-green-500',
      change: `${leadsStats?.opt_in_rate?.toFixed(1)}%`,
    },
    {
      name: 'Active Campaigns',
      value: campaignsStats?.active_campaigns || 0,
      icon: Mail,
      color: 'bg-purple-500',
      change: `${campaignsStats?.total_campaigns || 0} total`,
    },
    {
      name: 'Avg Open Rate',
      value: `${campaignsStats?.avg_open_rate?.toFixed(1)}%` || '0%',
      icon: TrendingUp,
      color: 'bg-orange-500',
      change: `${campaignsStats?.avg_click_rate?.toFixed(1)}% CTR`,
    },
  ]

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-6 sm:p-8 text-white shadow-lg">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
          Welcome Back! 👋
        </h1>
        <p className="text-primary-100 mt-2 text-sm sm:text-base">
          Your AI Marketing Automation dashboard
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="bg-white rounded-xl sm:rounded-2xl shadow-sm p-5 sm:p-6 border border-gray-100 hover:shadow-lg hover:scale-105 transition-all duration-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-xs sm:text-sm font-medium text-gray-600">
                  {stat.name}
                </p>
                <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mt-2">
                  {stat.value}
                </p>
                <p className="text-xs sm:text-sm text-gray-500 mt-1">
                  {stat.change}
                </p>
              </div>
              <div className={`${stat.color} p-3 sm:p-4 rounded-xl shadow-md`}>
                <stat.icon className="text-white" size={20} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm p-5 sm:p-6 lg:p-8 border border-gray-100">
        <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <button
            onClick={() => (window.location.href = '/content')}
            className="group p-5 sm:p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-primary-500 hover:bg-gradient-to-br hover:from-primary-50 hover:to-primary-100 transition-all duration-200 text-center hover:scale-105"
          >
            <div className="text-3xl sm:text-4xl mb-2 group-hover:scale-110 transition-transform">
              ✨
            </div>
            <div className="font-semibold text-gray-900 text-sm sm:text-base">
              Generate Content
            </div>
            <div className="text-xs sm:text-sm text-gray-500 mt-1">
              Create AI-powered posts
            </div>
          </button>

          <button
            onClick={() => (window.location.href = '/leads')}
            className="group p-5 sm:p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-primary-500 hover:bg-gradient-to-br hover:from-primary-50 hover:to-primary-100 transition-all duration-200 text-center hover:scale-105"
          >
            <div className="text-3xl sm:text-4xl mb-2 group-hover:scale-110 transition-transform">
              👥
            </div>
            <div className="font-semibold text-gray-900 text-sm sm:text-base">
              Add Leads
            </div>
            <div className="text-xs sm:text-sm text-gray-500 mt-1">
              Import or create leads
            </div>
          </button>

          <button
            onClick={() => (window.location.href = '/campaigns')}
            className="group p-5 sm:p-6 border-2 border-dashed border-gray-300 rounded-xl hover:border-primary-500 hover:bg-gradient-to-br hover:from-primary-50 hover:to-primary-100 transition-all duration-200 text-center hover:scale-105 sm:col-span-2 lg:col-span-1"
          >
            <div className="text-3xl sm:text-4xl mb-2 group-hover:scale-110 transition-transform">
              📧
            </div>
            <div className="font-semibold text-gray-900 text-sm sm:text-base">
              New Campaign
            </div>
            <div className="text-xs sm:text-sm text-gray-500 mt-1">
              Launch email campaign
            </div>
          </button>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm p-5 sm:p-6 lg:p-8 border border-gray-100">
        <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">
          Getting Started
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
          <div className="flex items-start space-x-3 p-4 sm:p-5 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl hover:shadow-md transition-all">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
              1
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900 text-sm sm:text-base">
                Import Your Leads
              </p>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Upload your customer list with consent confirmation
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-4 sm:p-5 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl hover:shadow-md transition-all">
            <div className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
              2
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900 text-sm sm:text-base">
                Generate Content
              </p>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Use AI to create engaging social media posts and emails
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-4 sm:p-5 bg-gradient-to-br from-green-50 to-green-100 rounded-xl hover:shadow-md transition-all">
            <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
              3
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900 text-sm sm:text-base">
                Launch Campaigns
              </p>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Send targeted email campaigns to opted-in leads
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-4 sm:p-5 bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl hover:shadow-md transition-all">
            <div className="flex-shrink-0 w-8 h-8 bg-orange-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
              4
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900 text-sm sm:text-base">
                Track Performance
              </p>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Monitor analytics and optimize your marketing strategy
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
