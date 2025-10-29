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
  getAvailableFields: () => api.get('/api/segments/fields/available').then(res => res.data),
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

export default api
