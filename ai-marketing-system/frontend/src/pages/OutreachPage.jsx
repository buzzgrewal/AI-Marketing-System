import { useState, useEffect } from 'react'
import { outreachAPI, leadsAPI, segmentsAPI } from '../services/api'
import {
  Mail, Send, Users, Plus, Trash2, Play, Pause,
  TrendingUp, Eye, MousePointerClick, MessageCircle, Clock, CheckCircle
} from 'lucide-react'

export default function OutreachPage() {
  const [sequences, setSequences] = useState([])
  const [selectedSequence, setSelectedSequence] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [leads, setLeads] = useState([])
  const [segments, setSegments] = useState([])
  const [activeTab, setActiveTab] = useState('sequences') // sequences, create, analytics
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form states
  const [sequenceForm, setSequenceForm] = useState({
    name: '',
    description: '',
    stop_on_reply: true,
    max_retries: 3,
    segment_id: null,
    sequence_steps: [
      {
        step: 1,
        delay_days: 0,
        type: 'email',
        message_type: 'intro',
        subject: '',
        template: '',
        context: ''
      }
    ]
  })

  const [messageGenerator, setMessageGenerator] = useState({
    lead_id: null,
    message_type: 'intro',
    template: '',
    additional_context: ''
  })

  const [generatedMessage, setGeneratedMessage] = useState(null)
  const [selectedLeads, setSelectedLeads] = useState([])

  useEffect(() => {
    fetchSequences()
    fetchLeads()
    fetchSegments()
  }, [])

  useEffect(() => {
    if (selectedSequence) {
      fetchAnalytics(selectedSequence.id)
    }
  }, [selectedSequence])

  const fetchSequences = async () => {
    try {
      const response = await outreachAPI.getAllSequences()
      setSequences(response.data)
    } catch (err) {
      console.error('Error fetching sequences:', err)
    }
  }

  const fetchLeads = async () => {
    try {
      const response = await leadsAPI.getAll({ email_consent: true })
      setLeads(response.data)
    } catch (err) {
      console.error('Error fetching leads:', err)
    }
  }

  const fetchSegments = async () => {
    try {
      const segmentsList = await segmentsAPI.list()
      setSegments(segmentsList)
    } catch (err) {
      console.error('Error fetching segments:', err)
    }
  }

  const fetchAnalytics = async (sequenceId) => {
    try {
      const response = await outreachAPI.getSequenceAnalytics(sequenceId)
      setAnalytics(response.data)
    } catch (err) {
      console.error('Error fetching analytics:', err)
    }
  }

  const handleCreateSequence = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await outreachAPI.createSequence(sequenceForm)
      setSuccess('Sequence created successfully!')
      setSequenceForm({
        name: '',
        description: '',
        stop_on_reply: true,
        max_retries: 3,
        segment_id: null,
        sequence_steps: [
          {
            step: 1,
            delay_days: 0,
            type: 'email',
            message_type: 'intro',
            subject: '',
            template: '',
            context: ''
          }
        ]
      })
      fetchSequences()
      setActiveTab('sequences')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create sequence')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateMessage = async () => {
    if (!messageGenerator.lead_id) {
      setError('Please select a lead')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await outreachAPI.generateMessage(messageGenerator)
      setGeneratedMessage(response.data)
      setSuccess('Message generated successfully!')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate message')
    } finally {
      setLoading(false)
    }
  }

  const handleEnrollLeads = async (sequenceId) => {
    if (selectedLeads.length === 0) {
      setError('Please select leads to enroll')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await outreachAPI.enrollLeads(sequenceId, selectedLeads)
      setSuccess(`Enrolled ${response.data.results.enrolled} leads successfully!`)
      setSelectedLeads([])
      fetchSequences()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to enroll leads')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteSequence = async (sequenceId) => {
    if (!confirm('Are you sure you want to delete this sequence?')) return

    try {
      await outreachAPI.deleteSequence(sequenceId)
      setSuccess('Sequence deleted successfully!')
      fetchSequences()
      setSelectedSequence(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete sequence')
    }
  }

  const addSequenceStep = () => {
    const newStep = {
      step: sequenceForm.sequence_steps.length + 1,
      delay_days: 3,
      type: 'email',
      message_type: 'follow_up',
      subject: '',
      template: '',
      context: ''
    }
    setSequenceForm({
      ...sequenceForm,
      sequence_steps: [...sequenceForm.sequence_steps, newStep]
    })
  }

  const removeSequenceStep = (stepIndex) => {
    const updatedSteps = sequenceForm.sequence_steps.filter((_, i) => i !== stepIndex)
    setSequenceForm({
      ...sequenceForm,
      sequence_steps: updatedSteps
    })
  }

  const updateSequenceStep = (stepIndex, field, value) => {
    const updatedSteps = sequenceForm.sequence_steps.map((step, i) => {
      if (i === stepIndex) {
        return { ...step, [field]: value }
      }
      return step
    })
    setSequenceForm({
      ...sequenceForm,
      sequence_steps: updatedSteps
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Outreach Generation</h1>
          <p className="text-gray-600 mt-1">Create personalized, automated outreach sequences</p>
        </div>
        <button
          onClick={() => setActiveTab('create')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} />
          New Sequence
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
            onClick={() => setActiveTab('sequences')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'sequences'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Mail size={16} />
              Sequences
            </div>
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'create'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Plus size={16} />
              Create Sequence
            </div>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analytics'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            disabled={!selectedSequence}
          >
            <div className="flex items-center gap-2">
              <TrendingUp size={16} />
              Analytics
            </div>
          </button>
        </nav>
      </div>

      {/* Sequences Tab */}
      {activeTab === 'sequences' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sequences.map((sequence) => (
            <div
              key={sequence.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-200"
              onClick={() => {
                setSelectedSequence(sequence)
                setActiveTab('analytics')
              }}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{sequence.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{sequence.description}</p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  sequence.status === 'active' ? 'bg-green-100 text-green-800' :
                  sequence.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {sequence.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500">Enrolled</p>
                  <p className="text-2xl font-bold text-gray-900">{sequence.total_enrolled}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Sent</p>
                  <p className="text-2xl font-bold text-gray-900">{sequence.total_sent}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Opened</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {sequence.total_sent > 0
                      ? `${((sequence.total_opened / sequence.total_sent) * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Replied</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {sequence.total_sent > 0
                      ? `${((sequence.total_replied / sequence.total_sent) * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteSequence(sequence.id)
                  }}
                  className="flex-1 px-3 py-2 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50"
                >
                  <Trash2 size={14} className="inline mr-1" />
                  Delete
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedSequence(sequence)
                    // Show lead selection modal here
                  }}
                  className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  <Users size={14} className="inline mr-1" />
                  Enroll
                </button>
              </div>
            </div>
          ))}

          {sequences.length === 0 && (
            <div className="col-span-3 text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <Mail size={48} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Sequences Yet</h3>
              <p className="text-gray-600 mb-4">Create your first outreach sequence to get started</p>
              <button
                onClick={() => setActiveTab('create')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Sequence
              </button>
            </div>
          )}
        </div>
      )}

      {/* Create Sequence Tab */}
      {activeTab === 'create' && (
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Outreach Sequence</h2>

            <form onSubmit={handleCreateSequence} className="space-y-6">
              {/* Basic Info */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sequence Name *
                  </label>
                  <input
                    type="text"
                    value={sequenceForm.name}
                    onChange={(e) => setSequenceForm({ ...sequenceForm, name: e.target.value })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={sequenceForm.description}
                    onChange={(e) => setSequenceForm({ ...sequenceForm, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Segment (Optional)
                  </label>
                  <select
                    value={sequenceForm.segment_id || ''}
                    onChange={(e) => setSequenceForm({ ...sequenceForm, segment_id: e.target.value ? parseInt(e.target.value) : null })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All leads with consent</option>
                    {segments.map(segment => (
                      <option key={segment.id} value={segment.id}>{segment.name}</option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={sequenceForm.stop_on_reply}
                      onChange={(e) => setSequenceForm({ ...sequenceForm, stop_on_reply: e.target.checked })}
                      className="rounded text-blue-600"
                    />
                    <span className="text-sm text-gray-700">Stop sequence on reply</span>
                  </label>
                </div>
              </div>

              {/* Sequence Steps */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Sequence Steps</h3>
                  <button
                    type="button"
                    onClick={addSequenceStep}
                    className="px-3 py-1 text-sm bg-blue-100 text-blue-600 rounded hover:bg-blue-200"
                  >
                    <Plus size={16} className="inline mr-1" />
                    Add Step
                  </button>
                </div>

                {sequenceForm.sequence_steps.map((step, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900">Step {step.step}</h4>
                      {sequenceForm.sequence_steps.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeSequenceStep(index)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Delay (days)
                        </label>
                        <input
                          type="number"
                          value={step.delay_days}
                          onChange={(e) => updateSequenceStep(index, 'delay_days', parseInt(e.target.value))}
                          min="0"
                          className="w-full px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Message Type
                        </label>
                        <select
                          value={step.message_type}
                          onChange={(e) => updateSequenceStep(index, 'message_type', e.target.value)}
                          className="w-full px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="intro">Introduction</option>
                          <option value="follow_up">Follow-up</option>
                          <option value="promotional">Promotional</option>
                          <option value="re_engagement">Re-engagement</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Subject Line (optional, AI will generate if empty)
                      </label>
                      <input
                        type="text"
                        value={step.subject || ''}
                        onChange={(e) => updateSequenceStep(index, 'subject', e.target.value)}
                        className="w-full px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Template Instructions (optional)
                      </label>
                      <textarea
                        value={step.template || ''}
                        onChange={(e) => updateSequenceStep(index, 'template', e.target.value)}
                        rows={2}
                        placeholder="Provide specific instructions for AI message generation..."
                        className="w-full px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Submit Button */}
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setActiveTab('sequences')}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Sequence'}
                </button>
              </div>
            </form>
          </div>

          {/* Message Generator Section */}
          <div className="bg-white rounded-lg shadow-md p-6 mt-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">AI Message Generator</h3>
            <p className="text-sm text-gray-600 mb-4">
              Test the AI message generation for a specific lead before creating a sequence
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Lead
                </label>
                <select
                  value={messageGenerator.lead_id || ''}
                  onChange={(e) => setMessageGenerator({ ...messageGenerator, lead_id: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose a lead...</option>
                  {leads.map(lead => (
                    <option key={lead.id} value={lead.id}>
                      {lead.first_name} {lead.last_name} ({lead.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message Type
                </label>
                <select
                  value={messageGenerator.message_type}
                  onChange={(e) => setMessageGenerator({ ...messageGenerator, message_type: e.target.value })}
                  className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="intro">Introduction</option>
                  <option value="follow_up">Follow-up</option>
                  <option value="promotional">Promotional</option>
                  <option value="re_engagement">Re-engagement</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Context (Optional)
                </label>
                <textarea
                  value={messageGenerator.additional_context}
                  onChange={(e) => setMessageGenerator({ ...messageGenerator, additional_context: e.target.value })}
                  rows={3}
                  placeholder="Add any specific details or context for the message..."
                  className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={handleGenerateMessage}
                disabled={loading || !messageGenerator.lead_id}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? 'Generating...' : 'Generate Message'}
              </button>

              {generatedMessage && (
                <div className="mt-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
                  <h4 className="font-semibold text-gray-900 mb-2">Generated Message:</h4>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Subject:</p>
                      <p className="text-sm font-medium text-gray-900">{generatedMessage.subject}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Body:</p>
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">{generatedMessage.body}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Call to Action:</p>
                      <p className="text-sm font-medium text-blue-600">{generatedMessage.call_to_action}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && selectedSequence && analytics && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{selectedSequence.name}</h2>
              <p className="text-gray-600 mt-1">{selectedSequence.description}</p>
            </div>
            <button
              onClick={() => {
                setSelectedSequence(null)
                setActiveTab('sequences')
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Back to Sequences
            </button>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Enrolled</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{analytics.total_enrolled}</p>
                </div>
                <Users size={40} className="text-blue-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Open Rate</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">{analytics.open_rate}%</p>
                </div>
                <Eye size={40} className="text-green-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Click Rate</p>
                  <p className="text-3xl font-bold text-purple-600 mt-2">{analytics.click_rate}%</p>
                </div>
                <MousePointerClick size={40} className="text-purple-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Reply Rate</p>
                  <p className="text-3xl font-bold text-orange-600 mt-2">{analytics.reply_rate}%</p>
                </div>
                <MessageCircle size={40} className="text-orange-500" />
              </div>
            </div>
          </div>

          {/* Detailed Stats */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Sent</span>
                  <span className="font-semibold text-gray-900">{analytics.total_sent}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Opened</span>
                  <span className="font-semibold text-gray-900">{analytics.total_opened}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Clicked</span>
                  <span className="font-semibold text-gray-900">{analytics.total_clicked}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Replied</span>
                  <span className="font-semibold text-gray-900">{analytics.total_replied}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Completed</span>
                  <span className="font-semibold text-gray-900">{analytics.total_completed}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Enrollment Status</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 flex items-center gap-2">
                    <Clock size={16} className="text-blue-500" />
                    Active
                  </span>
                  <span className="font-semibold text-gray-900">{analytics.enrollment_status.active}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 flex items-center gap-2">
                    <CheckCircle size={16} className="text-green-500" />
                    Completed
                  </span>
                  <span className="font-semibold text-gray-900">{analytics.enrollment_status.completed}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 flex items-center gap-2">
                    <Pause size={16} className="text-yellow-500" />
                    Stopped
                  </span>
                  <span className="font-semibold text-gray-900">{analytics.enrollment_status.stopped}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 flex items-center gap-2">
                    <Trash2 size={16} className="text-red-500" />
                    Failed
                  </span>
                  <span className="font-semibold text-gray-900">{analytics.enrollment_status.failed}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
