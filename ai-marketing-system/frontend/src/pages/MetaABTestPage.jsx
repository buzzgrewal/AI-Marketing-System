import { useState, useEffect } from 'react';
import { metaABTestsAPI } from '../services/api';
import {
  Facebook, Instagram, Play, Pause, Trophy, TrendingUp, BarChart3,
  Plus, Edit2, Trash2, Eye, RefreshCw, DollarSign, Users, MousePointer,
  Target, Zap, Settings, AlertCircle, CheckCircle
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import toast from 'react-hot-toast';

const MetaABTestPage = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('active');
  const [stats, setStats] = useState({
    total_tests: 0,
    running_tests: 0,
    completed_tests: 0,
    total_spend: 0,
    average_improvement: null,
    platform_breakdown: {}
  });

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    ad_account_id: '',
    platform: 'both',
    test_type: 'ad_creative',
    budget_per_variant: 50,
    duration_days: 7,
    target_audience: {
      age_min: 18,
      age_max: 65,
      genders: [1, 2],
      geo_locations: {
        countries: ['US'],
        location_types: ['home']
      },
      interests: []
    },
    success_metric: 'ctr',
    scheduled_start: null,
    variants: [
      {
        name: 'Variant A',
        description: '',
        headline: '',
        primary_text: '',
        description_text: '',
        call_to_action: 'LEARN_MORE',
        link_url: '',
        image_url: ''
      },
      {
        name: 'Variant B',
        description: '',
        headline: '',
        primary_text: '',
        description_text: '',
        call_to_action: 'LEARN_MORE',
        link_url: '',
        image_url: ''
      }
    ]
  });

  const [accountVerified, setAccountVerified] = useState(false);

  useEffect(() => {
    fetchTests();
    fetchStats();
  }, []);

  const fetchTests = async () => {
    try {
      setLoading(true);
      const response = await metaABTestsAPI.getAll();
      setTests(response.data);
    } catch (error) {
      console.error('Error fetching Meta A/B tests:', error);
      toast.error('Failed to fetch Meta A/B tests');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await metaABTestsAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const verifyAdAccount = async () => {
    if (!formData.ad_account_id) {
      toast.error('Please enter an Ad Account ID');
      return;
    }

    try {
      const response = await metaABTestsAPI.verifyAccount(formData.ad_account_id);
      setAccountVerified(true);
      toast.success(`Account verified: ${response.data.name}`);
    } catch (error) {
      setAccountVerified(false);
      toast.error('Failed to verify ad account. Please check the ID and permissions.');
    }
  };

  const handleCreate = () => {
    setFormData({
      name: '',
      description: '',
      ad_account_id: '',
      platform: 'both',
      test_type: 'ad_creative',
      budget_per_variant: 50,
      duration_days: 7,
      target_audience: {
        age_min: 18,
        age_max: 65,
        genders: [1, 2],
        geo_locations: {
          countries: ['US'],
          location_types: ['home']
        },
        interests: []
      },
      success_metric: 'ctr',
      scheduled_start: null,
      variants: [
        {
          name: 'Variant A',
          description: '',
          headline: '',
          primary_text: '',
          description_text: '',
          call_to_action: 'LEARN_MORE',
          link_url: '',
          image_url: ''
        },
        {
          name: 'Variant B',
          description: '',
          headline: '',
          primary_text: '',
          description_text: '',
          call_to_action: 'LEARN_MORE',
          link_url: '',
          image_url: ''
        }
      ]
    });
    setAccountVerified(false);
    setShowCreateModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!accountVerified) {
      toast.error('Please verify your ad account first');
      return;
    }

    try {
      await metaABTestsAPI.create(formData);
      toast.success('Meta A/B test created successfully!');
      setShowCreateModal(false);
      fetchTests();
      fetchStats();
    } catch (error) {
      console.error('Error creating Meta A/B test:', error);
      toast.error(error.response?.data?.detail || 'Failed to create Meta A/B test');
    }
  };

  const handleStart = async (testId) => {
    if (!window.confirm('Are you sure you want to start this test? This will begin spending your ad budget.')) {
      return;
    }

    try {
      await metaABTestsAPI.start(testId);
      toast.success('Meta A/B test started successfully!');
      fetchTests();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to start test');
    }
  };

  const handlePause = async (testId) => {
    try {
      await metaABTestsAPI.pause(testId);
      toast.success('Meta A/B test paused');
      fetchTests();
    } catch (error) {
      toast.error('Failed to pause test');
    }
  };

  const handleViewAnalysis = async (test) => {
    try {
      const response = await metaABTestsAPI.getAnalysis(test.id);
      setAnalysis(response.data);
      setSelectedTest(test);
      setShowAnalysisModal(true);
    } catch (error) {
      toast.error('Failed to fetch analysis');
    }
  };

  const handleRefreshResults = async (testId) => {
    try {
      toast.loading('Fetching latest results from Meta...');
      const response = await metaABTestsAPI.refreshResults(testId);
      toast.dismiss();
      toast.success('Results updated successfully');

      // If analysis modal is open, update it
      if (showAnalysisModal && selectedTest?.id === testId) {
        setAnalysis(response.data);
      }
    } catch (error) {
      toast.dismiss();
      toast.error('Failed to refresh results');
    }
  };

  const handleDeclareWinner = async (variantId) => {
    if (!window.confirm('Are you sure you want to declare this variant as the winner?')) {
      return;
    }

    try {
      await metaABTestsAPI.declareWinner(selectedTest.id, {
        winner_variant_id: variantId,
        apply_winner_to_campaign: true,
        end_test: true
      });
      toast.success('Winner declared successfully!');
      setShowAnalysisModal(false);
      fetchTests();
      fetchStats();
    } catch (error) {
      toast.error('Failed to declare winner');
    }
  };

  const addVariant = () => {
    if (formData.variants.length < 5) {
      setFormData({
        ...formData,
        variants: [
          ...formData.variants,
          {
            name: `Variant ${String.fromCharCode(65 + formData.variants.length)}`,
            description: '',
            headline: '',
            primary_text: '',
            description_text: '',
            call_to_action: 'LEARN_MORE',
            link_url: '',
            image_url: ''
          }
        ]
      });
    }
  };

  const removeVariant = (index) => {
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
      case 'running': return 'text-green-600 bg-green-100';
      case 'paused': return 'text-yellow-600 bg-yellow-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'draft': return 'text-gray-600 bg-gray-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'facebook': return <Facebook className="w-4 h-4 text-blue-600" />;
      case 'instagram': return <Instagram className="w-4 h-4 text-pink-600" />;
      case 'both': return (
        <div className="flex gap-1">
          <Facebook className="w-4 h-4 text-blue-600" />
          <Instagram className="w-4 h-4 text-pink-600" />
        </div>
      );
      default: return null;
    }
  };

  const filteredTests = tests.filter(test => {
    if (activeTab === 'active') return ['running', 'paused'].includes(test.status);
    if (activeTab === 'draft') return test.status === 'draft';
    if (activeTab === 'completed') return test.status === 'completed';
    return true;
  });

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <div className="flex gap-2">
              <Facebook className="w-8 h-8 text-blue-600" />
              <Instagram className="w-8 h-8 text-pink-600" />
            </div>
            Meta A/B Testing
          </h1>
          <p className="text-gray-600 mt-1">
            Test and optimize your Facebook and Instagram ads
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Create Test
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Tests</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_tests}</p>
            </div>
            <Zap className="w-8 h-8 text-blue-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Running</p>
              <p className="text-2xl font-bold text-green-600">{stats.running_tests}</p>
            </div>
            <Play className="w-8 h-8 text-green-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-blue-600">{stats.completed_tests}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-blue-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Spend</p>
              <p className="text-2xl font-bold text-gray-900">${stats.total_spend?.toFixed(2) || '0.00'}</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-500 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Improvement</p>
              <p className="text-2xl font-bold text-purple-600">
                {stats.average_improvement ? `+${stats.average_improvement.toFixed(1)}%` : 'N/A'}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-500 opacity-20" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          <button
            onClick={() => setActiveTab('active')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'active'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Active Tests
          </button>
          <button
            onClick={() => setActiveTab('draft')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'draft'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Drafts
          </button>
          <button
            onClick={() => setActiveTab('completed')}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'completed'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Completed
          </button>
        </nav>
      </div>

      {/* Tests List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : filteredTests.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <Zap className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No tests found</h3>
          <p className="text-gray-600 mb-6">Create your first Meta A/B test to start optimizing your ads</p>
          <button
            onClick={handleCreate}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Test
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredTests.map((test) => (
            <div key={test.id} className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getPlatformIcon(test.platform)}
                    <h3 className="text-lg font-semibold text-gray-900">{test.name}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(test.status)}`}>
                      {test.status}
                    </span>
                  </div>

                  {test.description && (
                    <p className="text-gray-600 text-sm mb-3">{test.description}</p>
                  )}

                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Target className="w-4 h-4" />
                      <span>{test.test_type.replace('_', ' ')}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <BarChart3 className="w-4 h-4" />
                      <span>{test.success_metric.toUpperCase()}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <DollarSign className="w-4 h-4" />
                      <span>${test.budget_per_variant}/day per variant</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      <span>{test.variants?.length || 0} variants</span>
                    </div>
                  </div>

                  {test.status === 'running' && test.variants && (
                    <div className="mt-4 grid grid-cols-2 lg:grid-cols-4 gap-3">
                      {test.variants.map((variant) => (
                        <div key={variant.id} className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs text-gray-600 mb-1">{variant.name}</p>
                          <p className="text-sm font-semibold text-gray-900">{variant.impressions || 0} impressions</p>
                          <p className="text-xs text-gray-600">CTR: {variant.ctr?.toFixed(2) || 0}%</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  {test.status === 'draft' && (
                    <button
                      onClick={() => handleStart(test.id)}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="Start Test"
                    >
                      <Play className="w-5 h-5" />
                    </button>
                  )}

                  {test.status === 'running' && (
                    <>
                      <button
                        onClick={() => handlePause(test.id)}
                        className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
                        title="Pause Test"
                      >
                        <Pause className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleRefreshResults(test.id)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Refresh Results"
                      >
                        <RefreshCw className="w-5 h-5" />
                      </button>
                    </>
                  )}

                  {['running', 'completed'].includes(test.status) && (
                    <button
                      onClick={() => handleViewAnalysis(test)}
                      className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                      title="View Analysis"
                    >
                      <BarChart3 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Test Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4">
              <h2 className="text-2xl font-semibold text-gray-900">Create Meta A/B Test</h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>

                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Ad Account ID *
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={formData.ad_account_id}
                        onChange={(e) => setFormData({ ...formData, ad_account_id: e.target.value })}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="1234567890"
                        required
                      />
                      <button
                        type="button"
                        onClick={verifyAdAccount}
                        className={`px-4 py-2 rounded-lg transition-colors ${
                          accountVerified
                            ? 'bg-green-100 text-green-700'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                      >
                        {accountVerified ? 'Verified ✓' : 'Verify'}
                      </button>
                    </div>
                    {!accountVerified && (
                      <p className="text-xs text-gray-500 mt-1">
                        Enter your Facebook Ad Account ID (without 'act_' prefix)
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Test Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                      disabled={!accountVerified}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Platform
                    </label>
                    <select
                      value={formData.platform}
                      onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={!accountVerified}
                    >
                      <option value="both">Facebook & Instagram</option>
                      <option value="facebook">Facebook Only</option>
                      <option value="instagram">Instagram Only</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Test Type
                    </label>
                    <select
                      value={formData.test_type}
                      onChange={(e) => setFormData({ ...formData, test_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={!accountVerified}
                    >
                      <option value="ad_creative">Ad Creative</option>
                      <option value="audience">Audience</option>
                      <option value="placement">Placement</option>
                      <option value="budget">Budget</option>
                      <option value="bidding">Bidding Strategy</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Success Metric
                    </label>
                    <select
                      value={formData.success_metric}
                      onChange={(e) => setFormData({ ...formData, success_metric: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={!accountVerified}
                    >
                      <option value="ctr">Click-Through Rate (CTR)</option>
                      <option value="conversions">Conversions</option>
                      <option value="cpm">Cost Per 1000 Impressions (CPM)</option>
                      <option value="cpc">Cost Per Click (CPC)</option>
                      <option value="roas">Return on Ad Spend (ROAS)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Budget per Variant ($/day)
                    </label>
                    <input
                      type="number"
                      value={formData.budget_per_variant}
                      onChange={(e) => setFormData({ ...formData, budget_per_variant: parseFloat(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      min="1"
                      step="0.01"
                      required
                      disabled={!accountVerified}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Test Duration (days)
                    </label>
                    <input
                      type="number"
                      value={formData.duration_days}
                      onChange={(e) => setFormData({ ...formData, duration_days: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      min="1"
                      max="30"
                      required
                      disabled={!accountVerified}
                    />
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows="2"
                      disabled={!accountVerified}
                    />
                  </div>
                </div>
              </div>

              {/* Variants */}
              {accountVerified && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
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
                            <label className="block text-xs text-gray-600 mb-1">Headline</label>
                            <input
                              type="text"
                              value={variant.headline}
                              onChange={(e) => updateVariant(index, 'headline', e.target.value)}
                              className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="Catchy headline"
                            />
                          </div>

                          <div className="col-span-2">
                            <label className="block text-xs text-gray-600 mb-1">Primary Text</label>
                            <textarea
                              value={variant.primary_text}
                              onChange={(e) => updateVariant(index, 'primary_text', e.target.value)}
                              className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              rows="2"
                              placeholder="Main ad copy"
                            />
                          </div>

                          <div className="col-span-2">
                            <label className="block text-xs text-gray-600 mb-1">Description</label>
                            <input
                              type="text"
                              value={variant.description_text}
                              onChange={(e) => updateVariant(index, 'description_text', e.target.value)}
                              className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="Additional description"
                            />
                          </div>

                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Call to Action</label>
                            <select
                              value={variant.call_to_action}
                              onChange={(e) => updateVariant(index, 'call_to_action', e.target.value)}
                              className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                              <option value="LEARN_MORE">Learn More</option>
                              <option value="SHOP_NOW">Shop Now</option>
                              <option value="SIGN_UP">Sign Up</option>
                              <option value="CONTACT_US">Contact Us</option>
                              <option value="GET_OFFER">Get Offer</option>
                              <option value="BOOK_NOW">Book Now</option>
                            </select>
                          </div>

                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Link URL</label>
                            <input
                              type="url"
                              value={variant.link_url}
                              onChange={(e) => updateVariant(index, 'link_url', e.target.value)}
                              className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="https://example.com"
                            />
                          </div>

                          <div className="col-span-2">
                            <label className="block text-xs text-gray-600 mb-1">Image URL</label>
                            <input
                              type="url"
                              value={variant.image_url}
                              onChange={(e) => updateVariant(index, 'image_url', e.target.value)}
                              className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="https://example.com/image.jpg"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors"
                  disabled={!accountVerified}
                >
                  Create Test
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Analysis Modal */}
      {showAnalysisModal && analysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-gray-900">Test Analysis</h2>
              <button
                onClick={() => handleRefreshResults(selectedTest.id)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Refresh Results"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Summary Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Total Impressions</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analysis.total_impressions?.toLocaleString() || 0}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Total Spend</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${analysis.total_spend?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Confidence Level</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analysis.confidence_level?.toFixed(1) || 0}%
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Improvement</p>
                  <p className="text-2xl font-bold text-green-600">
                    {analysis.improvement_percentage > 0 ? '+' : ''}
                    {analysis.improvement_percentage?.toFixed(1) || 0}%
                  </p>
                </div>
              </div>

              {/* Variant Performance */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Variant Performance</h3>
                <div className="space-y-3">
                  {analysis.variant_performance?.map((variant) => (
                    <div
                      key={variant.id}
                      className={`border rounded-lg p-4 ${
                        variant.id === analysis.winner_variant_id
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-gray-900">{variant.name}</span>
                          {variant.id === analysis.winner_variant_id && (
                            <Trophy className="w-5 h-5 text-yellow-500" />
                          )}
                        </div>
                        {analysis.statistical_significance && variant.id === analysis.winner_variant_id && (
                          <button
                            onClick={() => handleDeclareWinner(variant.id)}
                            className="px-3 py-1 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                          >
                            Declare Winner
                          </button>
                        )}
                      </div>
                      <div className="grid grid-cols-4 gap-2 text-sm">
                        <div>
                          <span className="text-gray-600">Metric Value:</span>
                          <span className="ml-1 font-semibold">{variant.metric_value?.toFixed(2)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Sample Size:</span>
                          <span className="ml-1 font-semibold">{variant.sample_size?.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Spend:</span>
                          <span className="ml-1 font-semibold">${variant.spend?.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Performance Over Time Chart */}
              {analysis.performance_over_time?.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Trends</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={analysis.performance_over_time}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="ctr" stroke="#3b82f6" name="CTR %" />
                        <Line type="monotone" dataKey="conversions" stroke="#10b981" name="Conversions" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {analysis.recommendations?.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
                  <div className="bg-blue-50 rounded-lg p-4">
                    <ul className="space-y-2">
                      {analysis.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-6 border-t">
                <button
                  onClick={() => setShowAnalysisModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MetaABTestPage;