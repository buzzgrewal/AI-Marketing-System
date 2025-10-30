import { useState, useEffect } from 'react'
import { leadsAPI } from '../services/api'
import toast from 'react-hot-toast'
import { UserPlus, Upload, Search, Filter } from 'lucide-react'

export default function LeadsPage() {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterConsent, setFilterConsent] = useState('all')
  const [filterSource, setFilterSource] = useState('all')

  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    location: '',
    sport_type: 'cycling',
    customer_type: 'athlete',
    source: 'manual',
    email_consent: false,
    sms_consent: false,
    consent_source: 'manual',
    notes: '',
  })

  useEffect(() => {
    fetchLeads()
  }, [searchTerm, filterConsent, filterSource])

  const fetchLeads = async () => {
    setLoading(true)
    try {
      const params = {}
      if (searchTerm) params.search = searchTerm
      if (filterConsent !== 'all') {
        params.email_consent = filterConsent === 'opted_in'
      }
      if (filterSource !== 'all') {
        params.source = filterSource
      }

      const response = await leadsAPI.getAll(params)
      setLeads(response.data)
    } catch (error) {
      toast.error('Failed to fetch leads')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await leadsAPI.create(formData)
      toast.success('Lead added successfully!')
      setShowForm(false)
      setFormData({
        email: '',
        first_name: '',
        last_name: '',
        phone: '',
        location: '',
        sport_type: 'cycling',
        customer_type: 'athlete',
        source: 'manual',
        email_consent: false,
        sms_consent: false,
        consent_source: 'manual',
        notes: '',
      })
      fetchLeads()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add lead')
    }
  }

  const handleFileImport = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const confirmed = window.confirm(
      'Do you confirm that all contacts in this file have given explicit consent to be contacted?'
    )

    if (!confirmed) {
      e.target.value = ''
      return
    }

    try {
      toast.loading('Importing leads...')
      const response = await leadsAPI.import(file, true, 'csv_import')
      toast.dismiss()
      toast.success(
        `Imported ${response.data.imported} leads, skipped ${response.data.skipped}`
      )
      fetchLeads()
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to import leads')
    }
    e.target.value = ''
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Leads</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">
            Manage your contact database
          </p>
        </div>
        <div className="flex gap-2 sm:gap-3">
          <label className="flex-1 sm:flex-none flex items-center justify-center space-x-2 px-3 sm:px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition cursor-pointer text-sm">
            <Upload size={18} />
            <span className="hidden sm:inline">Import CSV</span>
            <span className="sm:hidden">Import</span>
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileImport}
              className="hidden"
            />
          </label>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex-1 sm:flex-none flex items-center justify-center space-x-2 px-3 sm:px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition text-sm font-medium"
          >
            <UserPlus size={18} />
            <span>Add Lead</span>
          </button>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <div className="flex-1 relative">
          <Search
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
            size={20}
          />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search leads..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm sm:text-base"
          />
        </div>
        <select
          value={filterSource}
          onChange={(e) => setFilterSource(e.target.value)}
          className="px-3 sm:px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm sm:text-base"
        >
          <option value="all">All Sources</option>
          <option value="manual">Manual</option>
          <option value="shopify">Shopify</option>
          <option value="facebook">Facebook</option>
          <option value="website">Website</option>
          <option value="import">Import</option>
          <option value="event">Event</option>
          <option value="other">Other</option>
        </select>
        <select
          value={filterConsent}
          onChange={(e) => setFilterConsent(e.target.value)}
          className="px-3 sm:px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm sm:text-base"
        >
          <option value="all">All Leads</option>
          <option value="opted_in">Opted In</option>
          <option value="not_opted_in">Not Opted In</option>
        </select>
      </div>

      {/* Add Lead Form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Add New Lead</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  First Name
                </label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) =>
                    setFormData({ ...formData, first_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name
                </label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) =>
                    setFormData({ ...formData, last_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) =>
                    setFormData({ ...formData, phone: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sport Type
                </label>
                <select
                  value={formData.sport_type}
                  onChange={(e) =>
                    setFormData({ ...formData, sport_type: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                >
                  <option value="cycling">Cycling</option>
                  <option value="triathlon">Triathlon</option>
                  <option value="running">Running</option>
                  <option value="multiple">Multiple</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Customer Type
                </label>
                <select
                  value={formData.customer_type}
                  onChange={(e) =>
                    setFormData({ ...formData, customer_type: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                >
                  <option value="athlete">Athlete</option>
                  <option value="coach">Coach</option>
                  <option value="team">Team</option>
                  <option value="bike_fitter">Bike Fitter</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lead Source
                </label>
                <select
                  value={formData.source}
                  onChange={(e) =>
                    setFormData({ ...formData, source: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                >
                  <option value="manual">Manual Entry</option>
                  <option value="website">Website Form</option>
                  <option value="facebook">Facebook</option>
                  <option value="event">Event Registration</option>
                  <option value="import">Import/CSV</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="email_consent"
                  checked={formData.email_consent}
                  onChange={(e) =>
                    setFormData({ ...formData, email_consent: e.target.checked })
                  }
                  className="w-4 h-4 text-primary-600"
                />
                <label htmlFor="email_consent" className="text-sm text-gray-700">
                  Email consent obtained
                </label>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="sms_consent"
                  checked={formData.sms_consent}
                  onChange={(e) =>
                    setFormData({ ...formData, sms_consent: e.target.checked })
                  }
                  className="w-4 h-4 text-primary-600"
                />
                <label htmlFor="sms_consent" className="text-sm text-gray-700">
                  SMS consent obtained
                </label>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition"
              >
                Add Lead
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Leads List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {/* Desktop Table View */}
          <div className="hidden md:block bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sport
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Source
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Consent
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {lead.first_name} {lead.last_name}
                          </div>
                          <div className="text-sm text-gray-500">{lead.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {lead.sport_type || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {lead.customer_type || '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded capitalize ${
                          lead.source === 'shopify' ? 'bg-purple-100 text-purple-700' :
                          lead.source === 'facebook' ? 'bg-blue-100 text-blue-700' :
                          lead.source === 'website' ? 'bg-green-100 text-green-700' :
                          lead.source === 'import' ? 'bg-orange-100 text-orange-700' :
                          lead.source === 'event' ? 'bg-pink-100 text-pink-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {lead.source || 'manual'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex space-x-1">
                          {lead.email_consent && (
                            <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded">
                              Email
                            </span>
                          )}
                          {lead.sms_consent && (
                            <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                              SMS
                            </span>
                          )}
                          {!lead.email_consent && !lead.sms_consent && (
                            <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                              None
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded ${
                            lead.status === 'customer'
                              ? 'bg-green-100 text-green-700'
                              : lead.status === 'engaged'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          {lead.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Mobile Card View */}
          <div className="md:hidden space-y-3">
            {leads.map((lead) => (
              <div
                key={lead.id}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-4"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-gray-900">
                      {lead.first_name} {lead.last_name}
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">{lead.email}</p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${
                      lead.status === 'customer'
                        ? 'bg-green-100 text-green-700'
                        : lead.status === 'engaged'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {lead.status}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                  <div>
                    <span className="text-gray-500">Sport:</span>{' '}
                    <span className="font-medium text-gray-900">
                      {lead.sport_type || '-'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Type:</span>{' '}
                    <span className="font-medium text-gray-900">
                      {lead.customer_type || '-'}
                    </span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-gray-500">Source:</span>{' '}
                    <span className={`px-2 py-0.5 text-xs font-medium rounded capitalize ${
                      lead.source === 'shopify' ? 'bg-purple-100 text-purple-700' :
                      lead.source === 'facebook' ? 'bg-blue-100 text-blue-700' :
                      lead.source === 'website' ? 'bg-green-100 text-green-700' :
                      lead.source === 'import' ? 'bg-orange-100 text-orange-700' :
                      lead.source === 'event' ? 'bg-pink-100 text-pink-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {lead.source || 'manual'}
                    </span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1">
                  {lead.email_consent && (
                    <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded">
                      Email
                    </span>
                  )}
                  {lead.sms_consent && (
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                      SMS
                    </span>
                  )}
                  {!lead.email_consent && !lead.sms_consent && (
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
                      No Consent
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {!loading && leads.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <UserPlus className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No leads yet</h3>
          <p className="text-gray-600 mb-4">
            Add your first lead or import from CSV
          </p>
        </div>
      )}
    </div>
  )
}
