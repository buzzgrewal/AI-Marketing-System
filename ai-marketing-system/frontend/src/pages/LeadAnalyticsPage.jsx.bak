import { useState, useEffect } from 'react'
import {
  TrendingUp, Users, Target, Award, Activity,
  DollarSign, Calendar, BarChart3, PieChart, LineChart
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, PieChart as RePieChart, Pie, Cell,
  LineChart as ReLineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, FunnelChart, Funnel, LabelList
} from 'recharts'
import api, { leadTrackingAPI } from '../services/api'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function LeadAnalyticsPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(false)
  const [dateRange, setDateRange] = useState(90) // days

  // Data states
  const [funnelData, setFunnelData] = useState([])
  const [qualityData, setQualityData] = useState(null)
  const [engagementData, setEngagementData] = useState(null)
  const [attributionData, setAttributionData] = useState(null)
  const [journeyData, setJourneyData] = useState(null)
  const [cohortData, setCohortData] = useState([])

  useEffect(() => {
    if (activeTab === 'overview') {
      fetchAllData()
    } else if (activeTab === 'funnel') {
      fetchFunnelData()
    } else if (activeTab === 'quality') {
      fetchQualityData()
    } else if (activeTab === 'engagement') {
      fetchEngagementData()
    } else if (activeTab === 'attribution') {
      fetchAttributionData()
    } else if (activeTab === 'journey') {
      fetchJourneyData()
    } else if (activeTab === 'cohort') {
      fetchCohortData()
    }
  }, [activeTab, dateRange])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        fetchFunnelData(),
        fetchQualityData(),
        fetchEngagementData(),
        fetchAttributionData(),
        fetchJourneyData()
      ])
    } catch (error) {
      console.error('Error fetching analytics data:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchFunnelData = async () => {
    try {
      const response = await leadTrackingAPI.getFunnel({ days: dateRange })
      const funnel = response.data.funnel.map(item => ({
        name: item.stage.charAt(0).toUpperCase() + item.stage.slice(1),
        value: item.count,
        fill: COLORS[0]
      }))
      setFunnelData(funnel)
    } catch (error) {
      console.error('Error fetching funnel data:', error)
    }
  }

  const fetchQualityData = async () => {
    try {
      const response = await leadTrackingAPI.getQualityDistribution()
      setQualityData(response.data)
    } catch (error) {
      console.error('Error fetching quality data:', error)
    }
  }

  const fetchEngagementData = async () => {
    try {
      const response = await leadTrackingAPI.getEngagementStats({ days: dateRange })
      setEngagementData(response.data)
    } catch (error) {
      console.error('Error fetching engagement data:', error)
    }
  }

  const fetchAttributionData = async () => {
    try {
      const response = await leadTrackingAPI.getAttributionSummary({ days: dateRange })
      setAttributionData(response.data)
    } catch (error) {
      console.error('Error fetching attribution data:', error)
    }
  }

  const fetchJourneyData = async () => {
    try {
      const response = await leadTrackingAPI.getJourneyStats()
      setJourneyData(response.data)
    } catch (error) {
      console.error('Error fetching journey data:', error)
    }
  }

  const fetchCohortData = async () => {
    try {
      const response = await leadTrackingAPI.getCohortAnalysis({ cohort_type: 'monthly' })
      setCohortData(response.data.cohorts || [])
    } catch (error) {
      console.error('Error fetching cohort data:', error)
    }
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'funnel', name: 'Lifecycle Funnel', icon: TrendingUp },
    { id: 'quality', name: 'Lead Quality', icon: Award },
    { id: 'engagement', name: 'Engagement', icon: Activity },
    { id: 'attribution', name: 'Attribution', icon: Target },
    { id: 'journey', name: 'Journey Health', icon: LineChart },
    { id: 'cohort', name: 'Cohort Analysis', icon: Calendar }
  ]

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Lead Analytics & Insights</h1>
        <p className="text-gray-600">
          Comprehensive tracking, attribution, and performance metrics
        </p>
      </div>

      {/* Date Range Filter */}
      <div className="mb-6 flex items-center gap-4">
        <label className="text-sm font-medium text-gray-700">Time Period:</label>
        <select
          value={dateRange}
          onChange={(e) => setDateRange(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value={7}>Last 7 Days</option>
          <option value={30}>Last 30 Days</option>
          <option value={90}>Last 90 Days</option>
          <option value={180}>Last 6 Months</option>
          <option value={365}>Last Year</option>
        </select>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon size={18} />
                {tab.name}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {journeyData && (
                  <>
                    <MetricCard
                      icon={Users}
                      title="Total Journeys"
                      value={journeyData.total_journeys}
                      color="blue"
                    />
                    <MetricCard
                      icon={Calendar}
                      title="Avg Journey Duration"
                      value={`${Math.round(journeyData.average_journey_days)} days`}
                      color="green"
                    />
                    <MetricCard
                      icon={TrendingUp}
                      title="High Risk Leads"
                      value={journeyData.high_risk_count}
                      color="red"
                    />
                    <MetricCard
                      icon={DollarSign}
                      title="Total Lifetime Value"
                      value={`$${journeyData.total_lifetime_value?.toLocaleString() || 0}`}
                      color="purple"
                    />
                  </>
                )}
              </div>

              {/* Charts Row 1 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Lifecycle Funnel */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Lifecycle Funnel</h3>
                  {funnelData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={funnelData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-gray-500 text-center py-12">No funnel data available</p>
                  )}
                </div>

                {/* Lead Quality Distribution */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Quality by Grade</h3>
                  {qualityData && Object.keys(qualityData.by_grade || {}).length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <RePieChart>
                        <Pie
                          data={Object.entries(qualityData.by_grade).map(([grade, count]) => ({
                            name: grade,
                            value: count
                          }))}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) => `${name}: ${value}`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {Object.entries(qualityData.by_grade).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </RePieChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-gray-500 text-center py-12">No quality data available</p>
                  )}
                </div>
              </div>

              {/* Charts Row 2 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Engagement by Type */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement by Type</h3>
                  {engagementData && Object.keys(engagementData.by_type || {}).length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart
                        data={Object.entries(engagementData.by_type).map(([type, count]) => ({
                          type: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                          count
                        }))}
                        layout="vertical"
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" />
                        <YAxis dataKey="type" type="category" width={150} />
                        <Tooltip />
                        <Bar dataKey="count" fill="#10b981" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-gray-500 text-center py-12">No engagement data available</p>
                  )}
                </div>

                {/* Attribution by Type */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversions by Type</h3>
                  {attributionData && attributionData.conversions_by_type?.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={attributionData.conversions_by_type}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="type" />
                        <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                        <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                        <Tooltip />
                        <Legend />
                        <Bar yAxisId="left" dataKey="count" fill="#8b5cf6" name="Count" />
                        <Bar yAxisId="right" dataKey="total_value" fill="#10b981" name="Value ($)" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-gray-500 text-center py-12">No attribution data available</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Lifecycle Funnel Tab */}
          {activeTab === 'funnel' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Lead Lifecycle Funnel</h2>
              {funnelData.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={funnelData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" fill="#3b82f6" name="Leads in Stage" />
                    </BarChart>
                  </ResponsiveContainer>

                  {/* Stage Details Table */}
                  <div className="mt-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Stage Breakdown</h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Stage
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Count
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Percentage
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {funnelData.map((stage, index) => {
                            const total = funnelData.reduce((sum, s) => sum + s.value, 0)
                            const percentage = ((stage.value / total) * 100).toFixed(1)
                            return (
                              <tr key={index}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {stage.name}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {stage.value}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                  {percentage}%
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-12">No funnel data available</p>
              )}
            </div>
          )}

          {/* Lead Quality Tab */}
          {activeTab === 'quality' && (
            <div className="space-y-6">
              {qualityData ? (
                <>
                  {/* Quality Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <MetricCard
                      icon={Award}
                      title="Average Score"
                      value={Math.round(qualityData.average_score)}
                      color="blue"
                    />
                    <MetricCard
                      icon={TrendingUp}
                      title="Hot Leads"
                      value={qualityData.by_temperature?.hot || 0}
                      color="red"
                    />
                    <MetricCard
                      icon={Users}
                      title="Warm Leads"
                      value={qualityData.by_temperature?.warm || 0}
                      color="yellow"
                    />
                  </div>

                  {/* Charts */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribution by Grade</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <RePieChart>
                          <Pie
                            data={Object.entries(qualityData.by_grade || {}).map(([grade, count]) => ({
                              name: grade,
                              value: count
                            }))}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, value }) => `${name}: ${value}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {Object.entries(qualityData.by_grade || {}).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </RePieChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribution by Temperature</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={Object.entries(qualityData.by_temperature || {}).map(([temp, count]) => ({
                          temp: temp.charAt(0).toUpperCase() + temp.slice(1),
                          count
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="temp" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="count" fill="#f59e0b" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-12">No quality data available</p>
              )}
            </div>
          )}

          {/* Engagement Tab */}
          {activeTab === 'engagement' && (
            <div className="space-y-6">
              {engagementData ? (
                <>
                  {/* Engagement Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <MetricCard
                      icon={Activity}
                      title="Total Engagements"
                      value={engagementData.total_engagements}
                      color="blue"
                    />
                    <MetricCard
                      icon={DollarSign}
                      title="Revenue Attributed"
                      value={`$${engagementData.total_revenue_attributed?.toFixed(2) || 0}`}
                      color="green"
                    />
                    <MetricCard
                      icon={Target}
                      title="Engagement Types"
                      value={Object.keys(engagementData.by_type || {}).length}
                      color="purple"
                    />
                  </div>

                  {/* Charts */}
                  <div className="grid grid-cols-1 gap-6">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement by Type</h3>
                      <ResponsiveContainer width="100%" height={400}>
                        <BarChart
                          data={Object.entries(engagementData.by_type || {}).map(([type, count]) => ({
                            type: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                            count
                          }))}
                          layout="vertical"
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis type="number" />
                          <YAxis dataKey="type" type="category" width={200} />
                          <Tooltip />
                          <Bar dataKey="count" fill="#10b981" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement by Channel</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <RePieChart>
                          <Pie
                            data={Object.entries(engagementData.by_channel || {}).map(([channel, count]) => ({
                              name: channel || 'Unknown',
                              value: count
                            }))}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, value }) => `${name}: ${value}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {Object.entries(engagementData.by_channel || {}).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </RePieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-12">No engagement data available</p>
              )}
            </div>
          )}

          {/* Attribution Tab */}
          {activeTab === 'attribution' && (
            <div className="space-y-6">
              {attributionData ? (
                <>
                  {/* Attribution Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <MetricCard
                      icon={Target}
                      title="Total Conversions"
                      value={attributionData.total_conversions}
                      color="blue"
                    />
                    <MetricCard
                      icon={DollarSign}
                      title="Total Revenue"
                      value={`$${attributionData.total_revenue?.toLocaleString() || 0}`}
                      color="green"
                    />
                    <MetricCard
                      icon={Calendar}
                      title="Avg Journey"
                      value={`${Math.round(attributionData.average_journey_days)} days`}
                      color="purple"
                    />
                  </div>

                  {/* Charts */}
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversions by Type</h3>
                    {attributionData.conversions_by_type?.length > 0 ? (
                      <>
                        <ResponsiveContainer width="100%" height={400}>
                          <BarChart data={attributionData.conversions_by_type}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="type" />
                            <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                            <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                            <Tooltip />
                            <Legend />
                            <Bar yAxisId="left" dataKey="count" fill="#8b5cf6" name="Count" />
                            <Bar yAxisId="right" dataKey="total_value" fill="#10b981" name="Value ($)" />
                          </BarChart>
                        </ResponsiveContainer>

                        {/* Details Table */}
                        <div className="mt-8">
                          <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Details</h3>
                          <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                              <thead className="bg-gray-50">
                                <tr>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Type
                                  </th>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Count
                                  </th>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Total Value
                                  </th>
                                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Avg Value
                                  </th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200">
                                {attributionData.conversions_by_type.map((conv, index) => (
                                  <tr key={index}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                      {conv.type}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                      {conv.count}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                      ${conv.total_value?.toFixed(2) || 0}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                      ${(conv.total_value / conv.count)?.toFixed(2) || 0}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </>
                    ) : (
                      <p className="text-gray-500 text-center py-12">No attribution data available</p>
                    )}
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-12">No attribution data available</p>
              )}
            </div>
          )}

          {/* Journey Health Tab */}
          {activeTab === 'journey' && (
            <div className="space-y-6">
              {journeyData ? (
                <>
                  {/* Journey Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <MetricCard
                      icon={Users}
                      title="Total Journeys"
                      value={journeyData.total_journeys}
                      color="blue"
                    />
                    <MetricCard
                      icon={Calendar}
                      title="Avg Duration"
                      value={`${Math.round(journeyData.average_journey_days)} days`}
                      color="green"
                    />
                    <MetricCard
                      icon={TrendingUp}
                      title="High Risk"
                      value={journeyData.high_risk_count}
                      color="red"
                    />
                    <MetricCard
                      icon={DollarSign}
                      title="Lifetime Value"
                      value={`$${journeyData.total_lifetime_value?.toLocaleString() || 0}`}
                      color="purple"
                    />
                  </div>

                  {/* Engagement Trends */}
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement Trends</h3>
                    {journeyData.engagement_trends && Object.keys(journeyData.engagement_trends).length > 0 ? (
                      <ResponsiveContainer width="100%" height={300}>
                        <RePieChart>
                          <Pie
                            data={Object.entries(journeyData.engagement_trends).map(([trend, count]) => ({
                              name: trend.charAt(0).toUpperCase() + trend.slice(1),
                              value: count
                            }))}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, value }) => `${name}: ${value}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {Object.entries(journeyData.engagement_trends).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </RePieChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="text-gray-500 text-center py-12">No trend data available</p>
                    )}
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-12">No journey data available</p>
              )}
            </div>
          )}

          {/* Cohort Analysis Tab */}
          {activeTab === 'cohort' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Monthly Cohort Analysis</h2>
              {cohortData.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={400}>
                    <ReLineChart data={cohortData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="cohort"
                        tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      />
                      <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                      <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                      <Tooltip />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="total_leads" stroke="#3b82f6" name="Total Leads" />
                      <Line yAxisId="left" type="monotone" dataKey="customers" stroke="#10b981" name="Customers" />
                      <Line yAxisId="right" type="monotone" dataKey="conversion_rate" stroke="#f59e0b" name="Conversion Rate %" />
                    </ReLineChart>
                  </ResponsiveContainer>

                  {/* Cohort Table */}
                  <div className="mt-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Cohort Details</h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Cohort Month
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Total Leads
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Customers
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Conversion Rate
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {cohortData.map((cohort, index) => (
                            <tr key={index}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                {new Date(cohort.cohort).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {cohort.total_leads}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {cohort.customers}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {cohort.conversion_rate}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-12">No cohort data available</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

// Reusable Metric Card Component
function MetricCard({ icon: Icon, title, value, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600'
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  )
}
