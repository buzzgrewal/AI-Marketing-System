import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Just return the error, no auth redirect
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getCurrentUser: () => api.get('/api/auth/me'),
}

// Leads API
export const leadsAPI = {
  getAll: (params) => api.get('/api/leads/', { params }),
  getById: (id) => api.get(`/api/leads/${id}`),
  create: (data) => api.post('/api/leads/', data),
  update: (id, data) => api.put(`/api/leads/${id}`, data),
  delete: (id) => api.delete(`/api/leads/${id}`),
  import: (file, consentConfirmed, source) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('consent_confirmed', consentConfirmed)
    formData.append('source', source)
    return api.post('/api/leads/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getStats: () => api.get('/api/leads/stats/overview'),
}

// Campaigns API
export const campaignsAPI = {
  getAll: (params) => api.get('/api/campaigns/', { params }),
  getById: (id) => api.get(`/api/campaigns/${id}`),
  create: (data) => api.post('/api/campaigns/', data),
  update: (id, data) => api.put(`/api/campaigns/${id}`, data),
  delete: (id) => api.delete(`/api/campaigns/${id}`),
  send: (id) => api.post(`/api/campaigns/${id}/send`),
  getStats: (id) => api.get(`/api/campaigns/${id}/stats`),
  getOverview: () => api.get('/api/campaigns/stats/overview'),
}

// Content API
export const contentAPI = {
  getAll: (params) => api.get('/api/content/', { params }),
  getById: (id) => api.get(`/api/content/${id}`),
  generate: (data) => api.post('/api/content/generate', data),
  update: (id, data) => api.put(`/api/content/${id}`, data),
  delete: (id) => api.delete(`/api/content/${id}`),
  updatePerformance: (id, data) => api.post(`/api/content/${id}/performance`, data),
  improve: (id, focus) => api.post(`/api/content/improve/${id}`, null, {
    params: { improvement_focus: focus },
  }),
}

// Email Templates API
export const templatesAPI = {
  getAll: (params) => api.get('/api/templates/', { params }),
  getById: (id) => api.get(`/api/templates/${id}`),
  create: (data) => api.post('/api/templates/', data),
  update: (id, data) => api.put(`/api/templates/${id}`, data),
  delete: (id) => api.delete(`/api/templates/${id}`),
  render: (data) => api.post('/api/templates/render', data),
  duplicate: (id) => api.post(`/api/templates/${id}/duplicate`),
  validate: (id) => api.get(`/api/templates/${id}/validate`),
  getCategories: () => api.get('/api/templates/categories/list'),
  getVariables: () => api.get('/api/templates/variables/list'),
}

// Social Media Scheduling API
export const scheduleAPI = {
  getAll: (params) => api.get('/api/schedule/', { params }),
  getById: (id) => api.get(`/api/schedule/${id}`),
  create: (data) => api.post('/api/schedule/', data),
  scheduleFromContent: (data) => api.post('/api/schedule/from-content', data),
  bulkSchedule: (data) => api.post('/api/schedule/bulk', data),
  update: (id, data) => api.put(`/api/schedule/${id}`, data),
  delete: (id) => api.delete(`/api/schedule/${id}`),
  postNow: (id) => api.post(`/api/schedule/${id}/post-now`),
  refreshMetrics: (id) => api.post(`/api/schedule/${id}/metrics/refresh`),
  getCalendar: (params) => api.get('/api/schedule/calendar', { params }),
  getStats: () => api.get('/api/schedule/stats/overview'),
  getPlatformsStatus: () => api.get('/api/schedule/platforms/status'),
}

// Segments API
export const segmentsAPI = {
  list: () => api.get('/api/segments/').then(res => res.data),
  getAll: (params) => api.get('/api/segments/', { params }),
  getById: (id) => api.get(`/api/segments/${id}`),
  create: (data) => api.post('/api/segments/', data),
  update: (id, data) => api.put(`/api/segments/${id}`, data),
  delete: (id) => api.delete(`/api/segments/${id}`),
  preview: (id) => api.get(`/api/segments/${id}/preview`).then(res => res.data),
  refresh: (id) => api.post(`/api/segments/${id}/refresh`),
  getLeads: (id, params) => api.get(`/api/segments/${id}/leads`, { params }),
  duplicate: (id) => api.post(`/api/segments/${id}/duplicate`),
  getAvailableFields: () => api.get('/api/segments/fields/available').then(res => res.data.fields || []),
  getStats: () => api.get('/api/segments/stats/overview').then(res => res.data),
}

// A/B Testing API
export const abTestsAPI = {
  getAll: (params) => api.get('/api/ab-tests/', { params }),
  getById: (id) => api.get(`/api/ab-tests/${id}`),
  getResults: (id) => api.get(`/api/ab-tests/${id}/results`),
  create: (data) => api.post('/api/ab-tests/', data),
  update: (id, data) => api.put(`/api/ab-tests/${id}`, data),
  delete: (id) => api.delete(`/api/ab-tests/${id}`),
  start: (id) => api.post(`/api/ab-tests/${id}/start`),
  declareWinner: (id, data) => api.post(`/api/ab-tests/${id}/declare-winner`, data),
  updateVariant: (testId, variantId, data) => api.put(`/api/ab-tests/${testId}/variants/${variantId}`, data),
  updateVariantMetrics: (testId, variantId, data) => api.put(`/api/ab-tests/${testId}/variants/${variantId}/metrics`, data),
  getStats: () => api.get('/api/ab-tests/stats'),
}

// Webhooks API
export const webhooksAPI = {
  getAll: (params) => api.get('/api/webhooks/', { params }),
  getById: (id) => api.get(`/api/webhooks/${id}`),
  create: (data) => api.post('/api/webhooks/', data),
  update: (id, data) => api.put(`/api/webhooks/${id}`, data),
  delete: (id) => api.delete(`/api/webhooks/${id}`),
  getEvents: (id, params) => api.get(`/api/webhooks/${id}/events`, { params }),
  test: (id, payload) => api.post(`/api/webhooks/${id}/test`, { payload }),
  reprocessEvent: (eventId) => api.post(`/api/webhooks/events/${eventId}/reprocess`),
  getStats: () => api.get('/api/webhooks/stats'),
  getProviders: () => api.get('/api/webhooks/providers'),
}

// Facebook Lead Ads API
export const facebookLeadsAPI = {
  verify: () => api.get('/api/facebook-leads/verify'),
  getPages: () => api.get('/api/facebook-leads/pages'),
  getForms: (pageId) => api.get(`/api/facebook-leads/pages/${pageId}/forms`),
  getFormDetails: (formId) => api.get(`/api/facebook-leads/forms/${formId}`),
  syncForm: (formId) => api.post(`/api/facebook-leads/forms/${formId}/sync`),
  previewLeads: (formId) => api.get(`/api/facebook-leads/forms/${formId}/preview`),
}

// Lead Forms (Website Form Builder) API
export const leadFormsAPI = {
  getAll: (params) => api.get('/api/forms/', { params }),
  getById: (id) => api.get(`/api/forms/${id}`),
  getBySlug: (slug) => api.get(`/api/forms/slug/${slug}`),
  create: (data) => api.post('/api/forms/', data),
  update: (id, data) => api.put(`/api/forms/${id}`, data),
  delete: (id) => api.delete(`/api/forms/${id}`),
  duplicate: (id) => api.post(`/api/forms/${id}/duplicate`),
  getStats: (id) => api.get(`/api/forms/${id}/stats`),
  submitForm: (slug, data) => api.post(`/api/forms/submit/${slug}`, data),
}

// Outreach API
export const outreachAPI = {
  // Messages
  getAllMessages: (params) => api.get('/api/outreach/messages', { params }),
  getMessage: (id) => api.get(`/api/outreach/messages/${id}`),
  createMessage: (data) => api.post('/api/outreach/messages', data),
  sendMessage: (id) => api.post(`/api/outreach/messages/${id}/send`),

  // Sequences
  getAllSequences: (params) => api.get('/api/outreach/sequences', { params }),
  getSequence: (id) => api.get(`/api/outreach/sequences/${id}`),
  createSequence: (data) => api.post('/api/outreach/sequences', data),
  updateSequence: (id, data) => api.put(`/api/outreach/sequences/${id}`, data),
  deleteSequence: (id) => api.delete(`/api/outreach/sequences/${id}`),

  // Enrollments
  enrollLeads: (sequenceId, leadIds) => api.post(`/api/outreach/sequences/${sequenceId}/enroll`, {
    sequence_id: sequenceId,
    lead_ids: leadIds
  }),
  getEnrollments: (sequenceId, params) => api.get(`/api/outreach/sequences/${sequenceId}/enrollments`, { params }),
  stopEnrollment: (sequenceId, leadId, reason) => api.post(`/api/outreach/sequences/${sequenceId}/enrollments/${leadId}/stop`, null, {
    params: { reason }
  }),

  // Analytics
  getSequenceAnalytics: (sequenceId) => api.get(`/api/outreach/sequences/${sequenceId}/analytics`),

  // AI Generation
  generateMessage: (data) => api.post('/api/outreach/generate-message', data),

  // Background processing
  processSequences: () => api.post('/api/outreach/process-sequences'),
}

// Retargeting API
export const retargetingAPI = {
  // Audiences
  getAllAudiences: (params) => api.get('/api/retargeting/audiences', { params }),
  getAudience: (id) => api.get(`/api/retargeting/audiences/${id}`),
  createAudience: (data) => api.post('/api/retargeting/audiences', data),
  updateAudience: (id, data) => api.put(`/api/retargeting/audiences/${id}`, data),
  deleteAudience: (id) => api.delete(`/api/retargeting/audiences/${id}`),
  syncAudience: (id) => api.post(`/api/retargeting/audiences/${id}/sync`),
  getAudienceAnalytics: (id) => api.get(`/api/retargeting/audiences/${id}/analytics`),

  // Events
  trackEvent: (data) => api.post('/api/retargeting/events', data),
  getAllEvents: (params) => api.get('/api/retargeting/events', { params }),
  getEventStats: (days) => api.get('/api/retargeting/events/stats', { params: { days } }),

  // Campaigns
  getAllCampaigns: (params) => api.get('/api/retargeting/campaigns', { params }),
  getCampaign: (id) => api.get(`/api/retargeting/campaigns/${id}`),
  createCampaign: (data) => api.post('/api/retargeting/campaigns', data),
  updateCampaign: (id, data) => api.put(`/api/retargeting/campaigns/${id}`, data),
  deleteCampaign: (id) => api.delete(`/api/retargeting/campaigns/${id}`),
  pauseCampaign: (id) => api.post(`/api/retargeting/campaigns/${id}/pause`),
  activateCampaign: (id) => api.post(`/api/retargeting/campaigns/${id}/activate`),
  getCampaignAnalytics: (id) => api.get(`/api/retargeting/campaigns/${id}/analytics`),
}

// Lead Tracking & Analytics API
export const leadTrackingAPI = {
  // Lifecycle Management
  transitionStage: (leadId, data) => api.post(`/api/lead-tracking/lifecycle/${leadId}/transition`, null, { params: data }),
  getLifecycleHistory: (leadId) => api.get(`/api/lead-tracking/lifecycle/${leadId}/history`),
  getCurrentStage: (leadId) => api.get(`/api/lead-tracking/lifecycle/${leadId}/current`),

  // Lead Scoring
  calculateScore: (leadId) => api.post(`/api/lead-tracking/scoring/${leadId}/calculate`),
  getScore: (leadId) => api.get(`/api/lead-tracking/scoring/${leadId}`),
  bulkCalculateScores: (leadIds) => api.post('/api/lead-tracking/scoring/bulk-calculate', { lead_ids: leadIds }),

  // Engagement Tracking
  trackEngagement: (leadId, data) => api.post(`/api/lead-tracking/engagement/${leadId}`, data),
  getEngagementHistory: (leadId, params) => api.get(`/api/lead-tracking/engagement/${leadId}/history`, { params }),
  getEngagementStats: (params) => api.get('/api/lead-tracking/engagement/stats/summary', { params }),

  // Attribution
  calculateAttribution: (leadId, data) => api.post(`/api/lead-tracking/attribution/${leadId}/calculate`, data),
  getAttributionHistory: (leadId) => api.get(`/api/lead-tracking/attribution/${leadId}`),
  getAttributionSummary: (params) => api.get('/api/lead-tracking/attribution/stats/summary', { params }),

  // Journey Tracking
  getJourney: (leadId) => api.get(`/api/lead-tracking/journey/${leadId}`),
  getJourneyStats: () => api.get('/api/lead-tracking/journey/stats/overview'),

  // Analytics & Reports
  getFunnel: (params) => api.get('/api/lead-tracking/analytics/funnel', { params }),
  getCohortAnalysis: (params) => api.get('/api/lead-tracking/analytics/cohort', { params }),
  getQualityDistribution: () => api.get('/api/lead-tracking/analytics/lead-quality'),
}

// Website Forms API
export const websiteFormsAPI = {
  getAll: (params) => api.get('/api/website-forms/', { params }),
  getById: (id) => api.get(`/api/website-forms/${id}`),
  create: (data) => api.post('/api/website-forms/', data),
  update: (id, data) => api.put(`/api/website-forms/${id}`, data),
  delete: (id) => api.delete(`/api/website-forms/${id}`),
  getStats: (id) => api.get(`/api/website-forms/${id}/stats`),
  getSubmissions: (id, params) => api.get(`/api/website-forms/${id}/submissions`, { params }),
  submitForm: (id, data) => api.post(`/api/website-forms/${id}/submissions`, data),
  getEmbedCode: (id) => api.get(`/api/website-forms/embed/${id}.js`),
}

// Lead Analytics API
export const leadAnalyticsAPI = {
  getSummary: (period = 'month') => api.get('/api/lead-analytics/summary', { params: { period } }),
  getAll: (params) => api.get('/api/lead-analytics/', { params }),
  create: (data) => api.post('/api/lead-analytics/', data),
  update: (id, data) => api.put(`/api/lead-analytics/${id}`, data),
  delete: (id) => api.delete(`/api/lead-analytics/${id}`),
  getSourcePerformance: (params) => api.get('/api/lead-analytics/sources', { params }),
  createSourcePerformance: (data) => api.post('/api/lead-analytics/sources', data),
  generateSampleData: (days = 30) => api.post('/api/lead-analytics/generate-sample-data', null, { params: { days } }),
}

// Meta A/B Tests API
export const metaABTestsAPI = {
  verifyAccount: (adAccountId) => api.get(`/api/meta-ab-tests/verify-account/${adAccountId}`),
  getAll: (params) => api.get('/api/meta-ab-tests/', { params }),
  getStats: () => api.get('/api/meta-ab-tests/stats'),
  getById: (id) => api.get(`/api/meta-ab-tests/${id}`),
  getAnalysis: (id) => api.get(`/api/meta-ab-tests/${id}/analysis`),
  create: (data) => api.post('/api/meta-ab-tests/', data),
  update: (id, data) => api.put(`/api/meta-ab-tests/${id}`, data),
  delete: (id) => api.delete(`/api/meta-ab-tests/${id}`),
  start: (id) => api.post(`/api/meta-ab-tests/${id}/start`),
  pause: (id) => api.post(`/api/meta-ab-tests/${id}/pause`),
  refreshResults: (id) => api.post(`/api/meta-ab-tests/${id}/refresh-results`),
  declareWinner: (id, data) => api.post(`/api/meta-ab-tests/${id}/declare-winner`, data),
}

// Shopify API
export const shopifyAPI = {
  getStores: () => api.get('/api/shopify/stores'),
  getStoreInfo: (storeId) => api.get(`/api/shopify/stores/${storeId}`),
  getProducts: (storeId, limit = 50) => api.get(`/api/shopify/stores/${storeId}/products`, { params: { limit } }),
  getCustomers: (storeId, limit = 50) => api.get(`/api/shopify/stores/${storeId}/customers`, { params: { limit } }),
  auditStore: (storeId) => api.get(`/api/shopify/stores/${storeId}/audit`),
  syncCustomers: (storeId) => api.post(`/api/shopify/stores/${storeId}/sync-customers`),
}

export default api
