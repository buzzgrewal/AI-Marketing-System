import { useState, useEffect } from 'react';
import { segmentsAPI } from '../services/api';
import { Users, Plus, Search, Edit2, Trash2, Copy, RefreshCw, Eye, Filter } from 'lucide-react';

// Default fields constant
const DEFAULT_FIELDS = [
  { name: 'sport_type', label: 'Sport Type', operators: ['equals', 'not_equals', 'contains'] },
  { name: 'name', label: 'Name', operators: ['equals', 'not_equals', 'contains', 'starts_with'] },
  { name: 'email', label: 'Email', operators: ['equals', 'not_equals', 'contains', 'ends_with'] },
  { name: 'location', label: 'Location', operators: ['equals', 'not_equals', 'contains'] },
  { name: 'company', label: 'Company', operators: ['equals', 'not_equals', 'contains'] },
  { name: 'lead_score', label: 'Lead Score', operators: ['equals', 'greater_than', 'less_than', 'between'] },
  { name: 'status', label: 'Status', operators: ['equals', 'not_equals'] },
  { name: 'created_at', label: 'Created Date', operators: ['before', 'after', 'between'] },
  { name: 'updated_at', label: 'Updated Date', operators: ['before', 'after', 'between'] },
];

const SegmentsPage = () => {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showEditor, setShowEditor] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [editingSegment, setEditingSegment] = useState(null);
  const [previewLeads, setPreviewLeads] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [availableFields, setAvailableFields] = useState(DEFAULT_FIELDS);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    segment_type: 'dynamic',
    tags: [],
    criteria: {
      logic: 'AND',
      conditions: [
        {
          field: 'sport_type',
          operator: 'equals',
          value: ''
        }
      ]
    }
  });

  const [tagInput, setTagInput] = useState('');
  const [stats, setStats] = useState({
    total_segments: 0,
    total_leads_in_segments: 0,
    most_used_segment: null
  });

  useEffect(() => {
    fetchSegments();
    fetchAvailableFields();
    fetchStats();
  }, []);

  const fetchSegments = async () => {
    try {
      setLoading(true);
      const data = await segmentsAPI.list();
      setSegments(data);
    } catch (error) {
      console.error('Error fetching segments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableFields = async () => {
    try {
      const fields = await segmentsAPI.getAvailableFields();
      // Ensure fields is always an array
      if (Array.isArray(fields) && fields.length > 0) {
        setAvailableFields(fields);
      } else {
        console.error('Invalid fields format received:', fields);
        // Keep default fields as fallback
        setAvailableFields(DEFAULT_FIELDS);
      }
    } catch (error) {
      console.error('Error fetching available fields:', error);
      // Keep default fields as fallback when API fails
      setAvailableFields(DEFAULT_FIELDS);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await segmentsAPI.getStats();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleCreate = () => {
    setEditingSegment(null);
    setFormData({
      name: '',
      description: '',
      segment_type: 'dynamic',
      tags: [],
      criteria: {
        logic: 'AND',
        conditions: [
          {
            field: 'sport_type',
            operator: 'equals',
            value: ''
          }
        ]
      }
    });
    setShowEditor(true);
  };

  const handleEdit = (segment) => {
    setEditingSegment(segment);
    setFormData({
      name: segment.name,
      description: segment.description || '',
      segment_type: segment.segment_type || segment.type || 'dynamic',
      tags: segment.tags || [],
      criteria: segment.criteria
    });
    setShowEditor(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this segment?')) {
      try {
        await segmentsAPI.delete(id);
        fetchSegments();
        fetchStats();
      } catch (error) {
        console.error('Error deleting segment:', error);
        alert('Failed to delete segment');
      }
    }
  };

  const handleDuplicate = async (id) => {
    try {
      await segmentsAPI.duplicate(id);
      fetchSegments();
    } catch (error) {
      console.error('Error duplicating segment:', error);
      alert('Failed to duplicate segment');
    }
  };

  const handleRefresh = async (id) => {
    try {
      await segmentsAPI.refresh(id);
      fetchSegments();
    } catch (error) {
      console.error('Error refreshing segment:', error);
      alert('Failed to refresh segment');
    }
  };

  const handlePreview = async (segment) => {
    try {
      setLoading(true);
      const response = await segmentsAPI.preview(segment.id);
      // Handle both array and object response formats
      const leads = Array.isArray(response) ? response : (response.leads || []);
      setPreviewLeads(leads);
      setEditingSegment(segment);
      setShowPreview(true);
    } catch (error) {
      console.error('Error previewing segment:', error);
      alert('Failed to preview segment');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingSegment) {
        await segmentsAPI.update(editingSegment.id, formData);
      } else {
        await segmentsAPI.create(formData);
      }
      setShowEditor(false);
      fetchSegments();
      fetchStats();
    } catch (error) {
      console.error('Error saving segment:', error);
      alert('Failed to save segment: ' + (error.response?.data?.detail || error.message));
    }
  };

  const addCondition = () => {
    const defaultField = availableFields[0]?.name || 'sport_type';
    const defaultOperator = getOperatorsForField(defaultField)[0] || 'equals';

    setFormData({
      ...formData,
      criteria: {
        ...formData.criteria,
        conditions: [
          ...formData.criteria.conditions,
          {
            field: defaultField,
            operator: defaultOperator,
            value: ''
          }
        ]
      }
    });
  };

  const removeCondition = (index) => {
    const newConditions = formData.criteria.conditions.filter((_, i) => i !== index);
    setFormData({
      ...formData,
      criteria: {
        ...formData.criteria,
        conditions: newConditions
      }
    });
  };

  const updateCondition = (index, field, value) => {
    const newConditions = [...formData.criteria.conditions];
    newConditions[index] = {
      ...newConditions[index],
      [field]: value
    };
    setFormData({
      ...formData,
      criteria: {
        ...formData.criteria,
        conditions: newConditions
      }
    });
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const removeTag = (tag) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(t => t !== tag)
    });
  };

  const getOperatorsForField = (fieldName) => {
    const field = availableFields.find(f => f.name === fieldName);
    return field?.operators || ['equals', 'not_equals'];
  };

  const filteredSegments = segments.filter(segment => {
    const matchesSearch = segment.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (segment.description && segment.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const segmentType = segment.segment_type || segment.type || 'dynamic';
    const matchesType = selectedType === 'all' || segmentType === selectedType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Lead Segments</h1>
          <p className="text-gray-600">Create and manage lead segments for targeted campaigns</p>
        </div>
        <button
          onClick={handleCreate}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New Segment
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Segments</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_segments}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Filter className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Leads in Segments</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_leads_in_segments}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Users className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Most Used Segment</p>
              <p className="text-lg font-semibold text-gray-900 truncate">
                {stats.most_used_segment || 'N/A'}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex gap-4 flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search segments..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option key="all" value="all">All Types</option>
            <option key="dynamic" value="dynamic">Dynamic</option>
            <option key="static" value="static">Static</option>
          </select>
        </div>
      </div>

      {/* Segments List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : filteredSegments.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>No segments found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredSegments.map((segment) => (
              <div key={segment.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{segment.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        (segment.segment_type || segment.type || 'dynamic') === 'dynamic'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {segment.segment_type || segment.type || 'dynamic'}
                      </span>
                    </div>
                    {segment.description && (
                      <p className="text-gray-600 mb-2">{segment.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        {segment.lead_count} leads
                      </span>
                      <span>Used in {segment.campaign_count} campaigns</span>
                      {segment.last_used && (
                        <span>Last used: {new Date(segment.last_used).toLocaleDateString()}</span>
                      )}
                    </div>
                    {segment.tags && segment.tags.length > 0 && (
                      <div className="flex gap-2 mt-2">
                        {segment.tags.map((tag, index) => (
                          <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => handlePreview(segment)}
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Preview leads"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleRefresh(segment.id)}
                      className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="Refresh count"
                    >
                      <RefreshCw className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDuplicate(segment.id)}
                      className="p-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                      title="Duplicate"
                    >
                      <Copy className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleEdit(segment)}
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <Edit2 className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(segment.id)}
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

      {/* Editor Modal */}
      {showEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">
                {editingSegment ? 'Edit Segment' : 'Create New Segment'}
              </h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Basic Info */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Segment Name *
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
                    rows="3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Segment Type *
                  </label>
                  <select
                    value={formData.segment_type}
                    onChange={(e) => setFormData({ ...formData, segment_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option key="dynamic" value="dynamic">Dynamic (Auto-updates)</option>
                    <option key="static" value="static">Static (Fixed)</option>
                  </select>
                  <p className="text-sm text-gray-500 mt-1">
                    Dynamic segments automatically update as leads change. Static segments are fixed at creation.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addTag();
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Add a tag..."
                    />
                    <button
                      type="button"
                      onClick={addTag}
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                    >
                      Add
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.tags.map((tag, index) => (
                      <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-2">
                        {tag}
                        <button
                          type="button"
                          onClick={() => removeTag(tag)}
                          className="hover:text-blue-900"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Segment Criteria */}
              <div className="border-t pt-6">
                <div className="flex items-center justify-between mb-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Segment Criteria *
                  </label>
                  <select
                    value={formData.criteria.logic}
                    onChange={(e) => setFormData({
                      ...formData,
                      criteria: { ...formData.criteria, logic: e.target.value }
                    })}
                    className="px-3 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option key="AND" value="AND">Match ALL conditions (AND)</option>
                    <option key="OR" value="OR">Match ANY condition (OR)</option>
                  </select>
                </div>

                <div className="space-y-3">
                  {formData.criteria.conditions.map((condition, index) => {
                    const operators = getOperatorsForField(condition.field);
                    const fieldValue = availableFields.find(f => f.name === condition.field)
                      ? condition.field
                      : availableFields[0]?.name || 'sport_type';
                    const operatorValue = operators.includes(condition.operator)
                      ? condition.operator
                      : operators[0] || 'equals';

                    return (
                    <div key={index} className="flex gap-2 items-start p-4 bg-gray-50 rounded-lg">
                      <div className="flex-1 grid grid-cols-3 gap-2">
                        <select
                          value={fieldValue}
                          onChange={(e) => updateCondition(index, 'field', e.target.value)}
                          className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        >
                          {availableFields.map((field) => (
                            <option key={field.name} value={field.name}>
                              {field.label}
                            </option>
                          ))}
                        </select>

                        <select
                          value={operatorValue}
                          onChange={(e) => updateCondition(index, 'operator', e.target.value)}
                          className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        >
                          {operators.map((op) => (
                            <option key={op} value={op}>
                              {op.replace('_', ' ')}
                            </option>
                          ))}
                        </select>

                        <input
                          type="text"
                          value={condition.value}
                          onChange={(e) => updateCondition(index, 'value', e.target.value)}
                          className="px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                          placeholder="Value"
                        />
                      </div>

                      {formData.criteria.conditions.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeCondition(index)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                    );
                  })}
                </div>

                <button
                  type="button"
                  onClick={addCondition}
                  className="mt-3 px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg hover:border-blue-500 hover:text-blue-600 w-full"
                >
                  + Add Condition
                </button>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => setShowEditor(false)}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingSegment ? 'Update Segment' : 'Create Segment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">
                Preview: {editingSegment?.name}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {previewLeads.length} leads match this segment
              </p>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {previewLeads.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Users className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>No leads match this segment</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {previewLeads.map((lead) => (
                    <div key={lead.id} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold text-gray-900">{lead.name}</h4>
                          <p className="text-sm text-gray-600">{lead.email}</p>
                        </div>
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                          {lead.sport_type}
                        </span>
                      </div>
                      {lead.location && (
                        <p className="text-sm text-gray-500 mt-2">{lead.location}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200">
              <button
                onClick={() => setShowPreview(false)}
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

export default SegmentsPage;

