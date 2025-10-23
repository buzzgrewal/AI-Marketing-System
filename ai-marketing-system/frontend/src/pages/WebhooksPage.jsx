import { useState, useEffect } from 'react';
import { webhooksAPI } from '../services/api';
import { Webhook, Plus, Copy, Eye, Trash2, RefreshCw, Activity, CheckCircle, XCircle, Clock } from 'lucide-react';
import toast from 'react-hot-toast';

const WebhooksPage = () => {
  const [webhooks, setWebhooks] = useState([]);
  const [providers, setProviders] = useState([]);
  const [selectedWebhook, setSelectedWebhook] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEventsModal, setShowEventsModal] = useState(false);
  const [stats, setStats] = useState({
    total_webhooks: 0,
    active_webhooks: 0,
    total_events_received: 0,
    total_events_processed: 0,
    total_events_failed: 0,
    events_by_type: {},
    recent_events: []
  });

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    provider: 'generic',
    event_type: 'email_open',
    secret_key: '',
    verify_signature: true,
    is_active: true
  });

  useEffect(() => {
    fetchWebhooks();
    fetchProviders();
    fetchStats();
  }, []);

  const fetchWebhooks = async () => {
    try {
      setLoading(true);
      const response = await webhooksAPI.getAll();
      setWebhooks(response.data);
    } catch (error) {
      console.error('Error fetching webhooks:', error);
      toast.error('Failed to fetch webhooks');
    } finally {
      setLoading(false);
    }
  };

  const fetchProviders = async () => {
    try {
      const response = await webhooksAPI.getProviders();
      setProviders(response.data);
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await webhooksAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleCreate = () => {
    setFormData({
      name: '',
      description: '',
      provider: 'generic',
      event_type: 'email_open',
      secret_key: '',
      verify_signature: true,
      is_active: true
    });
    setShowCreateModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await webhooksAPI.create(formData);
      toast.success('Webhook created successfully!');
      setShowCreateModal(false);
      fetchWebhooks();
      fetchStats();
    } catch (error) {
      console.error('Error creating webhook:', error);
      toast.error(error.response?.data?.detail || 'Failed to create webhook');
    }
  };

  const handleDelete = async (webhookId) => {
    if (!window.confirm('Are you sure you want to delete this webhook?')) {
      return;
    }

    try {
      await webhooksAPI.delete(webhookId);
      toast.success('Webhook deleted successfully');
      fetchWebhooks();
      fetchStats();
    } catch (error) {
      console.error('Error deleting webhook:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete webhook');
    }
  };

  const handleViewEvents = async (webhook) => {
    try {
      setSelectedWebhook(webhook);
      const response = await webhooksAPI.getEvents(webhook.id);
      setEvents(response.data);
      setShowEventsModal(true);
    } catch (error) {
      console.error('Error fetching events:', error);
      toast.error('Failed to fetch webhook events');
    }
  };

  const handleCopyURL = (webhook) => {
    const url = webhook.webhook_url;
    navigator.clipboard.writeText(url);
    toast.success('Webhook URL copied to clipboard!');
  };

  const handleToggleActive = async (webhook) => {
    try {
      await webhooksAPI.update(webhook.id, { is_active: !webhook.is_active });
      toast.success(`Webhook ${!webhook.is_active ? 'enabled' : 'disabled'}`);
      fetchWebhooks();
    } catch (error) {
      console.error('Error toggling webhook:', error);
      toast.error('Failed to update webhook');
    }
  };

  const handleTest = async (webhookId) => {
    try {
      const testPayload = {
        event_type: 'test',
        email: 'test@example.com',
        campaign_id: 1,
        timestamp: new Date().toISOString()
      };
      
      await webhooksAPI.test(webhookId, testPayload);
      toast.success('Test event sent successfully!');
      fetchStats();
    } catch (error) {
      console.error('Error testing webhook:', error);
      toast.error('Failed to send test event');
    }
  };

  const handleReprocessEvent = async (eventId) => {
    try {
      await webhooksAPI.reprocessEvent(eventId);
      toast.success('Event queued for reprocessing');
      
      // Refresh events if modal is open
      if (selectedWebhook) {
        const response = await webhooksAPI.getEvents(selectedWebhook.id);
        setEvents(response.data);
      }
    } catch (error) {
      console.error('Error reprocessing event:', error);
      toast.error('Failed to reprocess event');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      default:
        return <Activity className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'processed':
        return 'bg-green-100 text-green-700';
      case 'failed':
        return 'bg-red-100 text-red-700';
      case 'pending':
        return 'bg-yellow-100 text-yellow-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const selectedProvider = providers.find(p => p.provider === formData.provider);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Webhook className="w-7 h-7" />
            Webhooks
          </h1>
          <p className="text-gray-600">Track email and campaign events automatically</p>
        </div>
        <button
          onClick={handleCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New Webhook
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Webhooks</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_webhooks}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Webhook className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active</p>
              <p className="text-2xl font-bold text-green-900">{stats.active_webhooks}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Events Received</p>
              <p className="text-2xl font-bold text-purple-900">{stats.total_events_received}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Processed</p>
              <p className="text-2xl font-bold text-green-900">{stats.total_events_processed}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Failed</p>
              <p className="text-2xl font-bold text-red-900">{stats.total_events_failed}</p>
            </div>
            <div className="p-3 bg-red-100 rounded-lg">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Webhooks List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : webhooks.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Webhook className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>No webhooks configured</p>
            <button
              onClick={handleCreate}
              className="mt-4 text-blue-600 hover:text-blue-700"
            >
              Create your first webhook
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {webhooks.map((webhook) => (
              <div key={webhook.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{webhook.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        webhook.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {webhook.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
                        {webhook.provider}
                      </span>
                    </div>
                    {webhook.description && (
                      <p className="text-gray-600 mb-2">{webhook.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-2">
                      <span>Event: {webhook.event_type}</span>
                      <span>Received: {webhook.total_events_received}</span>
                      <span>Processed: {webhook.total_events_processed}</span>
                      <span>Failed: {webhook.total_events_failed}</span>
                    </div>
                    <div className="bg-gray-50 p-2 rounded border border-gray-200 font-mono text-xs text-gray-700 flex items-center justify-between">
                      <span className="truncate mr-2">{webhook.webhook_url}</span>
                      <button
                        onClick={() => handleCopyURL(webhook)}
                        className="text-blue-600 hover:text-blue-700"
                        title="Copy URL"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => handleViewEvents(webhook)}
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="View events"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleTest(webhook.id)}
                      className="p-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                      title="Send test event"
                    >
                      <Activity className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleToggleActive(webhook)}
                      className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title={webhook.is_active ? 'Disable' : 'Enable'}
                    >
                      <RefreshCw className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(webhook.id)}
                      className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Create Webhook</h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Webhook Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="2"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Provider *
                  </label>
                  <select
                    value={formData.provider}
                    onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {providers.map((provider) => (
                      <option key={provider.provider} value={provider.provider}>
                        {provider.provider.charAt(0).toUpperCase() + provider.provider.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Event Type *
                  </label>
                  <select
                    value={formData.event_type}
                    onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {selectedProvider?.supported_events.map((event) => (
                      <option key={event} value={event}>
                        {event.replace('_', ' ')}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {selectedProvider?.requires_signature && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Secret Key (optional)
                    </label>
                    <input
                      type="text"
                      value={formData.secret_key}
                      onChange={(e) => setFormData({ ...formData, secret_key: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Leave empty to auto-generate"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Used for webhook signature verification. Will be auto-generated if not provided.
                    </p>
                  </div>

                  <div>
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={formData.verify_signature}
                        onChange={(e) => setFormData({ ...formData, verify_signature: e.target.checked })}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">Verify webhook signatures</span>
                    </label>
                  </div>
                </>
              )}

              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Active (start receiving events immediately)</span>
                </label>
              </div>

              {selectedProvider?.documentation_url && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-700">
                    📘 <a href={selectedProvider.documentation_url} target="_blank" rel="noopener noreferrer" className="underline">
                      View {selectedProvider.provider} webhook documentation
                    </a>
                  </p>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Create Webhook
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Events Modal */}
      {showEventsModal && selectedWebhook && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">
                Webhook Events: {selectedWebhook.name}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {events.length} events received
              </p>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {events.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Activity className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>No events received yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {events.map((event) => (
                    <div key={event.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(event.status)}
                          <span className="font-semibold text-gray-900">{event.event_type}</span>
                          <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(event.status)}`}>
                            {event.status}
                          </span>
                        </div>
                        <span className="text-sm text-gray-500">
                          {new Date(event.received_at).toLocaleString()}
                        </span>
                      </div>
                      
                      {event.email && (
                        <p className="text-sm text-gray-600 mb-2">Email: {event.email}</p>
                      )}
                      
                      {event.error_message && (
                        <div className="bg-red-50 border border-red-200 rounded p-2 mb-2">
                          <p className="text-sm text-red-700">{event.error_message}</p>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        {event.campaign_id && <span>Campaign: #{event.campaign_id}</span>}
                        {event.lead_id && <span>Lead: #{event.lead_id}</span>}
                        {event.status === 'failed' && (
                          <button
                            onClick={() => handleReprocessEvent(event.id)}
                            className="text-blue-600 hover:text-blue-700"
                          >
                            Reprocess
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200">
              <button
                onClick={() => setShowEventsModal(false)}
                className="w-full px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WebhooksPage;

