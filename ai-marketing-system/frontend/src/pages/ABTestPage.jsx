import { useState, useEffect } from 'react';
import { abTestsAPI, campaignsAPI, templatesAPI } from '../services/api';
import { FlaskConical, Plus, Play, Trophy, TrendingUp, BarChart3, Edit2, Trash2, Eye } from 'lucide-react';
import toast from 'react-hot-toast';

const ABTestPage = () => {
  const [tests, setTests] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showResultsModal, setShowResultsModal] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const [testResults, setTestResults] = useState(null);
  const [stats, setStats] = useState({
    total_tests: 0,
    running_tests: 0,
    completed_tests: 0,
    total_variants_tested: 0,
    average_improvement: null
  });

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    campaign_id: null,
    test_type: 'subject_line',
    sample_size_percentage: 20,
    success_metric: 'open_rate',
    auto_select_winner: true,
    variants: [
      { name: 'Variant A', description: '', subject: '', content: '', template_id: null, sender_name: '' },
      { name: 'Variant B', description: '', subject: '', content: '', template_id: null, sender_name: '' }
    ]
  });

  useEffect(() => {
    fetchTests();
    fetchCampaigns();
    fetchTemplates();
    fetchStats();
  }, []);

  const fetchTests = async () => {
    try {
      setLoading(true);
      const response = await abTestsAPI.getAll();
      setTests(response.data);
    } catch (error) {
      console.error('Error fetching A/B tests:', error);
      toast.error('Failed to fetch A/B tests');
    } finally {
      setLoading(false);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const response = await campaignsAPI.getAll();
      setCampaigns(response.data);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await templatesAPI.getAll({ is_active: true });
      setTemplates(response.data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await abTestsAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleCreate = () => {
    setFormData({
      name: '',
      description: '',
      campaign_id: null,
      test_type: 'subject_line',
      sample_size_percentage: 20,
      success_metric: 'open_rate',
      auto_select_winner: true,
      variants: [
        { name: 'Variant A', description: '', subject: '', content: '', template_id: null, sender_name: '' },
        { name: 'Variant B', description: '', subject: '', content: '', template_id: null, sender_name: '' }
      ]
    });
    setShowCreateModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await abTestsAPI.create(formData);
      toast.success('A/B test created successfully!');
      setShowCreateModal(false);
      fetchTests();
      fetchStats();
    } catch (error) {
      console.error('Error creating A/B test:', error);
      toast.error(error.response?.data?.detail || 'Failed to create A/B test');
    }
  };

  const handleStartTest = async (testId) => {
    if (!window.confirm('Are you sure you want to start this A/B test? This will send emails to the test sample.')) {
      return;
    }

    try {
      await abTestsAPI.start(testId);
      toast.success('A/B test started successfully!');
      fetchTests();
      fetchStats();
    } catch (error) {
      console.error('Error starting test:', error);
      toast.error(error.response?.data?.detail || 'Failed to start test');
    }
  };

  const handleViewResults = async (test) => {
    try {
      const response = await abTestsAPI.getResults(test.id);
      setTestResults(response.data);
      setSelectedTest(test);
      setShowResultsModal(true);
    } catch (error) {
      console.error('Error fetching results:', error);
      toast.error('Failed to fetch test results');
    }
  };

  const handleDeclareWinner = async (variantId) => {
    if (!window.confirm('Are you sure you want to declare this variant as the winner? This will complete the test.')) {
      return;
    }

    try {
      await abTestsAPI.declareWinner(selectedTest.id, {
        winner_variant_id: variantId,
        send_to_remaining: true
      });
      toast.success('Winner declared successfully!');
      setShowResultsModal(false);
      fetchTests();
      fetchStats();
    } catch (error) {
      console.error('Error declaring winner:', error);
      toast.error(error.response?.data?.detail || 'Failed to declare winner');
    }
  };

  const handleDelete = async (testId) => {
    if (!window.confirm('Are you sure you want to delete this A/B test?')) {
      return;
    }

    try {
      await abTestsAPI.delete(testId);
      toast.success('A/B test deleted successfully');
      fetchTests();
      fetchStats();
    } catch (error) {
      console.error('Error deleting test:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete test');
    }
  };

  const addVariant = () => {
    if (formData.variants.length >= 5) {
      toast.error('Maximum 5 variants allowed');
      return;
    }
    
    setFormData({
      ...formData,
      variants: [
        ...formData.variants,
        { 
          name: `Variant ${String.fromCharCode(65 + formData.variants.length)}`, 
          description: '', 
          subject: '', 
          content: '', 
          template_id: null, 
          sender_name: '' 
        }
      ]
    });
  };

  const removeVariant = (index) => {
    if (formData.variants.length <= 2) {
      toast.error('Minimum 2 variants required');
      return;
    }
    
    setFormData({
      ...formData,
      variants: formData.variants.filter((_, i) => i !== index)
    });
  };

  const updateVariant = (index, field, value) => {
    const newVariants = [...formData.variants];
    newVariants[index] = { ...newVariants[index], [field]: value };
    setFormData({ ...formData, variants: newVariants });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-700';
      case 'running': return 'bg-blue-100 text-blue-700';
      case 'completed': return 'bg-green-100 text-green-700';
      case 'cancelled': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const formatPercentage = (value) => {
    return value ? `${value.toFixed(2)}%` : '0.00%';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FlaskConical className="w-7 h-7" />
            A/B Testing
          </h1>
          <p className="text-gray-600">Optimize your campaigns with data-driven testing</p>
        </div>
        <button
          onClick={handleCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New A/B Test
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Tests</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_tests}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <FlaskConical className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Running</p>
              <p className="text-2xl font-bold text-blue-900">{stats.running_tests}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Play className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-green-900">{stats.completed_tests}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Trophy className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Variants Tested</p>
              <p className="text-2xl font-bold text-purple-900">{stats.total_variants_tested}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Improvement</p>
              <p className="text-2xl font-bold text-orange-900">
                {stats.average_improvement ? `${stats.average_improvement.toFixed(1)}%` : 'N/A'}
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Tests List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : tests.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <FlaskConical className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>No A/B tests found</p>
            <button
              onClick={handleCreate}
              className="mt-4 text-blue-600 hover:text-blue-700"
            >
              Create your first A/B test
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {tests.map((test) => (
              <div key={test.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{test.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(test.status)}`}>
                        {test.status}
                      </span>
                      {test.winner_variant_id && (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-700 flex items-center gap-1">
                          <Trophy className="w-3 h-3" />
                          Winner Declared
                        </span>
                      )}
                    </div>
                    {test.description && (
                      <p className="text-gray-600 mb-2">{test.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>Type: {test.test_type.replace('_', ' ')}</span>
                      <span>Sample: {test.sample_size_percentage}%</span>
                      <span>Metric: {test.success_metric.replace('_', ' ')}</span>
                      <span>{test.variants?.length || 0} variants</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {test.status === 'running' || test.status === 'completed' ? (
                      <button
                        onClick={() => handleViewResults(test)}
                        className="p-2 bg-gray-50 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="View results"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                    ) : null}
                    {test.status === 'draft' && (
                      <button
                        onClick={() => handleStartTest(test.id)}
                        className="p-2 bg-gray-50 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="Start test"
                      >
                        <Play className="w-5 h-5" />
                      </button>
                    )}
                    {test.status !== 'running' && (
                      <button
                        onClick={() => handleDelete(test.id)}
                        className="p-2 bg-gray-50 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    )}
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
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Create A/B Test</h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Campaign *
                  </label>
                  <select
                    value={formData.campaign_id || ''}
                    onChange={(e) => setFormData({ ...formData, campaign_id: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select campaign...</option>
                    {campaigns.map((campaign) => (
                      <option key={campaign.id} value={campaign.id}>
                        {campaign.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Type *
                  </label>
                  <select
                    value={formData.test_type}
                    onChange={(e) => setFormData({ ...formData, test_type: e.target.value })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="subject_line">Subject Line</option>
                    <option value="content">Content</option>
                    <option value="template">Template</option>
                    <option value="sender_name">Sender Name</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sample Size (%)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={formData.sample_size_percentage}
                    onChange={(e) => setFormData({ ...formData, sample_size_percentage: parseFloat(e.target.value) })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Success Metric
                  </label>
                  <select
                    value={formData.success_metric}
                    onChange={(e) => setFormData({ ...formData, success_metric: e.target.value })}
                    className="w-full px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="open_rate">Open Rate</option>
                    <option value="click_rate">Click Rate</option>
                    <option value="conversion_rate">Conversion Rate</option>
                  </select>
                </div>

                <div className="col-span-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.auto_select_winner}
                      onChange={(e) => setFormData({ ...formData, auto_select_winner: e.target.checked })}
                      className="form-checkbox h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">Automatically select winner when statistically significant</span>
                  </label>
                </div>
              </div>

              {/* Variants */}
              <div className="border-t pt-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Variants</h3>
                  <button
                    type="button"
                    onClick={addVariant}
                    className="text-sm text-blue-600 hover:text-blue-700"
                    disabled={formData.variants.length >= 5}
                  >
                    + Add Variant
                  </button>
                </div>

                <div className="space-y-4">
                  {formData.variants.map((variant, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <input
                          type="text"
                          value={variant.name}
                          onChange={(e) => updateVariant(index, 'name', e.target.value)}
                          className="text-lg font-semibold text-gray-900 border-0 border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none"
                          placeholder="Variant name"
                        />
                        {formData.variants.length > 2 && (
                          <button
                            type="button"
                            onClick={() => removeVariant(index)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="col-span-2">
                          <label className="block text-xs text-gray-600 mb-1">Description</label>
                          <input
                            type="text"
                            value={variant.description}
                            onChange={(e) => updateVariant(index, 'description', e.target.value)}
                            className="w-full px-3 py-2 text-sm bg-white text-gray-700 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        {(formData.test_type === 'subject_line' || formData.test_type === 'content') && (
                          <div className="col-span-2">
                            <label className="block text-xs text-gray-600 mb-1">Subject Line</label>
                            <input
                              type="text"
                              value={variant.subject}
                              onChange={(e) => updateVariant(index, 'subject', e.target.value)}
                              className="w-full px-3 py-2 text-sm bg-white text-gray-700 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                          </div>
                        )}

                        {formData.test_type === 'content' && (
                          <div className="col-span-2">
                            <label className="block text-xs text-gray-600 mb-1">Content</label>
                            <textarea
                              value={variant.content}
                              onChange={(e) => updateVariant(index, 'content', e.target.value)}
                              className="w-full px-3 py-2 text-sm bg-white text-gray-700 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              rows="3"
                            />
                          </div>
                        )}

                        {formData.test_type === 'template' && (
                          <div className="col-span-2">
                            <label className="block text-xs text-gray-600 mb-1">Template</label>
                            <select
                              value={variant.template_id || ''}
                              onChange={(e) => updateVariant(index, 'template_id', parseInt(e.target.value) || null)}
                              className="w-full px-3 py-2 text-sm bg-white text-gray-700 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                              <option value="">Select template...</option>
                              {templates.map((template) => (
                                <option key={template.id} value={template.id}>
                                  {template.name}
                                </option>
                              ))}
                            </select>
                          </div>
                        )}

                        {formData.test_type === 'sender_name' && (
                          <div className="col-span-2">
                            <label className="block text-xs text-gray-600 mb-1">Sender Name</label>
                            <input
                              type="text"
                              value={variant.sender_name}
                              onChange={(e) => updateVariant(index, 'sender_name', e.target.value)}
                              className="w-full px-3 py-2 text-sm bg-white text-gray-700 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-6 border-t">
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
                  Create A/B Test
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Results Modal */}
      {showResultsModal && testResults && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">{selectedTest?.name} - Results</h2>
              <p className="text-sm text-gray-600 mt-1">
                Total Recipients: {testResults.total_test_recipients} | 
                Success Metric: {selectedTest?.success_metric.replace('_', ' ')}
              </p>
            </div>

            <div className="p-6 space-y-6">
              {/* Overall Stats */}
              {testResults.statistical_significance > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Trophy className="w-5 h-5 text-green-600" />
                    <span className="font-semibold text-green-900">Statistical Significance Achieved</span>
                  </div>
                  <p className="text-sm text-green-700">
                    The best performing variant shows a {testResults.statistical_significance.toFixed(1)}% improvement over others.
                  </p>
                </div>
              )}

              {/* Variants Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {testResults.variants?.map((variant) => (
                  <div
                    key={variant.id}
                    className={`border rounded-lg p-4 ${
                      variant.is_winner ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900">{variant.name}</h3>
                      {variant.is_winner && (
                        <Trophy className="w-5 h-5 text-yellow-600" />
                      )}
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Sent:</span>
                        <span className="font-medium">{variant.total_sent}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Open Rate:</span>
                        <span className="font-medium">{formatPercentage(variant.open_rate)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Click Rate:</span>
                        <span className="font-medium">{formatPercentage(variant.click_rate)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Conversion Rate:</span>
                        <span className="font-medium">{formatPercentage(variant.conversion_rate)}</span>
                      </div>
                    </div>

                    {!variant.is_winner && selectedTest?.status === 'running' && (
                      <button
                        onClick={() => handleDeclareWinner(variant.id)}
                        className="mt-4 w-full px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                      >
                        Declare Winner
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 border-t border-gray-200">
              <button
                onClick={() => setShowResultsModal(false)}
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

export default ABTestPage;

