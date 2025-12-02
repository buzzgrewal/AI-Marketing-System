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
  register: (data) => api.post('/auth/register', data),
  login: (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getCurrentUser: () => api.get('/auth/me'),
}

// Leads API
export const leadsAPI = {
  getAll: (params) => api.get('/leads/', { params }),
  getById: (id) => api.get(`/leads/${id}`),
  create: (data) => api.post('/leads/', data),
  update: (id, data) => api.put(`/leads/${id}`, data),
  delete: (id) => api.delete(`/leads/${id}`),
  import: (file, consentConfirmed, source) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('consent_confirmed', consentConfirmed)
    formData.append('source', source)
    return api.post('/leads/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getStats: () => api.get('/leads/stats/overview'),
}

// Campaigns API
export const campaignsAPI = {
  getAll: (params) => api.get('/campaigns/', { params }),
  getById: (id) => api.get(`/campaigns/${id}`),
  create: (data) => api.post('/campaigns/', data),
  update: (id, data) => api.put(`/campaigns/${id}`, data),
  delete: (id) => api.delete(`/campaigns/${id}`),
  send: (id) => api.post(`/campaigns/${id}/send`),
  getStats: (id) => api.get(`/campaigns/${id}/stats`),
  getOverview: () => api.get('/campaigns/stats/overview'),
}

// Content API
export const contentAPI = {
  getAll: (params) => api.get('/content/', { params }),
  getById: (id) => api.get(`/content/${id}`),
  generate: (data) => api.post('/content/generate', data),
  update: (id, data) => api.put(`/content/${id}`, data),
  delete: (id) => api.delete(`/content/${id}`),
  updatePerformance: (id, data) => api.post(`/content/${id}/performance`, data),
  improve: (id, focus) => api.post(`/content/improve/${id}`, null, {
    params: { improvement_focus: focus },
  }),
}

// Email Templates API
export const templatesAPI = {
  getAll: (params) => api.get('/templates/', { params }),
  getById: (id) => api.get(`/templates/${id}`),
  create: (data) => api.post('/templates/', data),
  update: (id, data) => api.put(`/templates/${id}`, data),
  delete: (id) => api.delete(`/templates/${id}`),
  render: (data) => api.post('/templates/render', data),
  duplicate: (id) => api.post(`/templates/${id}/duplicate`),
  validate: (id) => api.get(`/templates/${id}/validate`),
  getCategories: () => api.get('/templates/categories/list'),
  getVariables: () => api.get('/templates/variables/list'),
}

// Social Media Scheduling API
export const scheduleAPI = {
  getAll: (params) => api.get('/schedule/', { params }),
  getById: (id) => api.get(`/schedule/${id}`),
  create: (data) => api.post('/schedule/', data),
  scheduleFromContent: (data) => api.post('/schedule/from-content', data),
  bulkSchedule: (data) => api.post('/schedule/bulk', data),
  update: (id, data) => api.put(`/schedule/${id}`, data),
  delete: (id) => api.delete(`/schedule/${id}`),
  postNow: (id) => api.post(`/schedule/${id}/post-now`),
  refreshMetrics: (id) => api.post(`/schedule/${id}/metrics/refresh`),
  getCalendar: (params) => api.get('/schedule/calendar', { params }),
  getStats: () => api.get('/schedule/stats/overview'),
  getPlatformsStatus: () => api.get('/schedule/platforms/status'),
}

// Segments API
export const segmentsAPI = {
  list: () => api.get('/segments/').then(res => res.data),
  getAll: (params) => api.get('/segments/', { params }),
  getById: (id) => api.get(`/segments/${id}`),
  create: (data) => api.post('/segments/', data),
  update: (id, data) => api.put(`/segments/${id}`, data),
  delete: (id) => api.delete(`/segments/${id}`),
  preview: (id) => api.get(`/segments/${id}/preview`).then(res => res.data),
  refresh: (id) => api.post(`/segments/${id}/refresh`),
  getLeads: (id, params) => api.get(`/segments/${id}/leads`, { params }),
  duplicate: (id) => api.post(`/segments/${id}/duplicate`),
  getAvailableFields: () => api.get('/segments/fields/available').then(res => res.data.fields || []),
  getStats: () => api.get('/segments/stats/overview').then(res => res.data),
}

// A/B Testing API
export const abTestsAPI = {
  getAll: (params) => api.get('/ab-tests/', { params }),
  getById: (id) => api.get(`/ab-tests/${id}`),
  getResults: (id) => api.get(`/ab-tests/${id}/results`),
  create: (data) => api.post('/ab-tests/', data),
  update: (id, data) => api.put(`/ab-tests/${id}`, data),
  delete: (id) => api.delete(`/ab-tests/${id}`),
  start: (id) => api.post(`/ab-tests/${id}/start`),
  declareWinner: (id, data) => api.post(`/ab-tests/${id}/declare-winner`, data),
  updateVariant: (testId, variantId, data) => api.put(`/ab-tests/${testId}/variants/${variantId}`, data),
  updateVariantMetrics: (testId, variantId, data) => api.put(`/ab-tests/${testId}/variants/${variantId}/metrics`, data),
  getStats: () => api.get('/ab-tests/stats'),
}

// Webhooks API
export const webhooksAPI = {
  getAll: (params) => api.get('/webhooks/', { params }),
  getById: (id) => api.get(`/webhooks/${id}`),
  create: (data) => api.post('/webhooks/', data),
  update: (id, data) => api.put(`/webhooks/${id}`, data),
  delete: (id) => api.delete(`/webhooks/${id}`),
  getEvents: (id, params) => api.get(`/webhooks/${id}/events`, { params }),
  test: (id, payload) => api.post(`/webhooks/${id}/test`, { payload }),
  reprocessEvent: (eventId) => api.post(`/webhooks/events/${eventId}/reprocess`),
  getStats: () => api.get('/webhooks/stats'),
  getProviders: () => api.get('/webhooks/providers'),
}

// Facebook Lead Ads API
export const facebookLeadsAPI = {
  verify: () => api.get('/facebook-leads/verify'),
  getPages: () => api.get('/facebook-leads/pages'),
  getForms: (pageId) => api.get(`/facebook-leads/pages/${pageId}/forms`),
  getFormDetails: (formId) => api.get(`/facebook-leads/forms/${formId}`),
  syncForm: (formId) => api.post(`/facebook-leads/forms/${formId}/sync`),
  previewLeads: (formId) => api.get(`/facebook-leads/forms/${formId}/preview`),
}

// Lead Forms (Website Form Builder) API
export const leadFormsAPI = {
  getAll: (params) => api.get('/forms/', { params }),
  getById: (id) => api.get(`/forms/${id}`),
  getBySlug: (slug) => api.get(`/forms/slug/${slug}`),
  create: (data) => api.post('/forms/', data),
  update: (id, data) => api.put(`/forms/${id}`, data),
  delete: (id) => api.delete(`/forms/${id}`),
  duplicate: (id) => api.post(`/forms/${id}/duplicate`),
  getStats: (id) => api.get(`/forms/${id}/stats`),
  submitForm: (slug, data) => api.post(`/forms/submit/${slug}`, data),
}

// Outreach API
export const outreachAPI = {
  // Messages
  getAllMessages: (params) => api.get('/outreach/messages', { params }),
  getMessage: (id) => api.get(`/outreach/messages/${id}`),
  createMessage: (data) => api.post('/outreach/messages', data),
  sendMessage: (id) => api.post(`/outreach/messages/${id}/send`),

  // Sequences
  getAllSequences: (params) => api.get('/outreach/sequences', { params }),
  getSequence: (id) => api.get(`/outreach/sequences/${id}`),
  createSequence: (data) => api.post('/outreach/sequences', data),
  updateSequence: (id, data) => api.put(`/outreach/sequences/${id}`, data),
  deleteSequence: (id) => api.delete(`/outreach/sequences/${id}`),

  // Enrollments
  enrollLeads: (sequenceId, leadIds) => api.post(`/outreach/sequences/${sequenceId}/enroll`, {
    sequence_id: sequenceId,
    lead_ids: leadIds
  }),
  getEnrollments: (sequenceId, params) => api.get(`/outreach/sequences/${sequenceId}/enrollments`, { params }),
  stopEnrollment: (sequenceId, leadId, reason) => api.post(`/outreach/sequences/${sequenceId}/enrollments/${leadId}/stop`, null, {
    params: { reason }
  }),

  // Analytics
  getSequenceAnalytics: (sequenceId) => api.get(`/outreach/sequences/${sequenceId}/analytics`),

  // AI Generation
  generateMessage: (data) => api.post('/outreach/generate-message', data),

  // Background processing
  processSequences: () => api.post('/outreach/process-sequences'),
}

// Retargeting API
export const retargetingAPI = {
  // Audiences
  getAllAudiences: (params) => api.get('/retargeting/audiences', { params }),
  getAudience: (id) => api.get(`/retargeting/audiences/${id}`),
  createAudience: (data) => api.post('/retargeting/audiences', data),
  updateAudience: (id, data) => api.put(`/retargeting/audiences/${id}`, data),
  deleteAudience: (id) => api.delete(`/retargeting/audiences/${id}`),
  syncAudience: (id) => api.post(`/retargeting/audiences/${id}/sync`),
  getAudienceAnalytics: (id) => api.get(`/retargeting/audiences/${id}/analytics`),

  // Events
  trackEvent: (data) => api.post('/retargeting/events', data),
  getAllEvents: (params) => api.get('/retargeting/events', { params }),
  getEventStats: (days) => api.get('/retargeting/events/stats', { params: { days } }),

  // Campaigns
  getAllCampaigns: (params) => api.get('/retargeting/campaigns', { params }),
  getCampaign: (id) => api.get(`/retargeting/campaigns/${id}`),
  createCampaign: (data) => api.post('/retargeting/campaigns', data),
  updateCampaign: (id, data) => api.put(`/retargeting/campaigns/${id}`, data),
  deleteCampaign: (id) => api.delete(`/retargeting/campaigns/${id}`),
  pauseCampaign: (id) => api.post(`/retargeting/campaigns/${id}/pause`),
  activateCampaign: (id) => api.post(`/retargeting/campaigns/${id}/activate`),
  getCampaignAnalytics: (id) => api.get(`/retargeting/campaigns/${id}/analytics`),
}

// Lead Tracking & Analytics API
export const leadTrackingAPI = {
  // Lifecycle Management
  transitionStage: (leadId, data) => api.post(`/lead-tracking/lifecycle/${leadId}/transition`, null, { params: data }),
  getLifecycleHistory: (leadId) => api.get(`/lead-tracking/lifecycle/${leadId}/history`),
  getCurrentStage: (leadId) => api.get(`/lead-tracking/lifecycle/${leadId}/current`),

  // Lead Scoring
  calculateScore: (leadId) => api.post(`/lead-tracking/scoring/${leadId}/calculate`),
  getScore: (leadId) => api.get(`/lead-tracking/scoring/${leadId}`),
  bulkCalculateScores: (leadIds) => api.post('/lead-tracking/scoring/bulk-calculate', { lead_ids: leadIds }),

  // Engagement Tracking
  trackEngagement: (leadId, data) => api.post(`/lead-tracking/engagement/${leadId}`, data),
  getEngagementHistory: (leadId, params) => api.get(`/lead-tracking/engagement/${leadId}/history`, { params }),
  getEngagementStats: (params) => api.get('/lead-tracking/engagement/stats/summary', { params }),

  // Attribution
  calculateAttribution: (leadId, data) => api.post(`/lead-tracking/attribution/${leadId}/calculate`, data),
  getAttributionHistory: (leadId) => api.get(`/lead-tracking/attribution/${leadId}`),
  getAttributionSummary: (params) => api.get('/lead-tracking/attribution/stats/summary', { params }),

  // Journey Tracking
  getJourney: (leadId) => api.get(`/lead-tracking/journey/${leadId}`),
  getJourneyStats: () => api.get('/lead-tracking/journey/stats/overview'),

  // Analytics & Reports
  getFunnel: (params) => api.get('/lead-tracking/analytics/funnel', { params }),
  getCohortAnalysis: (params) => api.get('/lead-tracking/analytics/cohort', { params }),
  getQualityDistribution: () => api.get('/lead-tracking/analytics/lead-quality'),
}

// Website Forms API
export const websiteFormsAPI = {
  getAll: (params) => api.get('/website-forms/', { params }),
  getById: (id) => api.get(`/website-forms/${id}`),
  create: (data) => api.post('/website-forms/', data),
  update: (id, data) => api.put(`/website-forms/${id}`, data),
  delete: (id) => api.delete(`/website-forms/${id}`),
  getStats: (id) => api.get(`/website-forms/${id}/stats`),
  getSubmissions: (id, params) => api.get(`/website-forms/${id}/submissions`, { params }),
  submitForm: (id, data) => api.post(`/website-forms/${id}/submissions`, data),
  getEmbedCode: (id) => api.get(`/website-forms/embed/${id}.js`),
}

// Lead Analytics API
export const leadAnalyticsAPI = {
  getSummary: (period = 'month') => api.get('/lead-analytics/summary', { params: { period } }),
  getAll: (params) => api.get('/lead-analytics/', { params }),
  create: (data) => api.post('/lead-analytics/', data),
  update: (id, data) => api.put(`/lead-analytics/${id}`, data),
  delete: (id) => api.delete(`/lead-analytics/${id}`),
  getSourcePerformance: (params) => api.get('/lead-analytics/sources', { params }),
  createSourcePerformance: (data) => api.post('/lead-analytics/sources', data),
  generateSampleData: (days = 30) => api.post('/lead-analytics/generate-sample-data', null, { params: { days } }),
}

// Meta A/B Tests API
export const metaABTestsAPI = {
  verifyAccount: (adAccountId) => api.get(`/meta-ab-tests/verify-account/${adAccountId}`),
  getAll: (params) => api.get('/meta-ab-tests/', { params }),
  getStats: () => api.get('/meta-ab-tests/stats'),
  getById: (id) => api.get(`/meta-ab-tests/${id}`),
  getAnalysis: (id) => api.get(`/meta-ab-tests/${id}/analysis`),
  create: (data) => api.post('/meta-ab-tests/', data),
  update: (id, data) => api.put(`/meta-ab-tests/${id}`, data),
  delete: (id) => api.delete(`/meta-ab-tests/${id}`),
  start: (id) => api.post(`/meta-ab-tests/${id}/start`),
  pause: (id) => api.post(`/meta-ab-tests/${id}/pause`),
  refreshResults: (id) => api.post(`/meta-ab-tests/${id}/refresh-results`),
  declareWinner: (id, data) => api.post(`/meta-ab-tests/${id}/declare-winner`, data),
}

// Shopify API
export const shopifyAPI = {
  getStores: () => api.get('/shopify/stores'),
  getStoreInfo: (storeId) => api.get(`/shopify/stores/${storeId}`),
  getProducts: (storeId, limit = 50) => api.get(`/shopify/stores/${storeId}/products`, { params: { limit } }),
  getCustomers: (storeId, limit = 50) => api.get(`/shopify/stores/${storeId}/customers`, { params: { limit } }),
  auditStore: (storeId) => api.get(`/shopify/stores/${storeId}/audit`),
  syncCustomers: (storeId) => api.post(`/shopify/stores/${storeId}/sync-customers`),
}

export default api
