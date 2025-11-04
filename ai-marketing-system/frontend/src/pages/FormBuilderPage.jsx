import { useState, useEffect } from 'react'
import { leadFormsAPI } from '../services/api'
import {
  Plus, Trash2, Eye, Code, Copy, Settings, Save, Edit,
  GripVertical, Type, Mail, Phone, MessageSquare, CheckSquare, List
} from 'lucide-react'

const FIELD_TYPES = [
  { value: 'text', label: 'Text Input', icon: Type },
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'phone', label: 'Phone', icon: Phone },
  { value: 'textarea', label: 'Text Area', icon: MessageSquare },
  { value: 'select', label: 'Dropdown', icon: List },
  { value: 'checkbox', label: 'Checkbox', icon: CheckSquare },
]

export default function FormBuilderPage() {
  const [forms, setForms] = useState([])
  const [selectedForm, setSelectedForm] = useState(null)
  const [activeTab, setActiveTab] = useState('list') // list, builder, preview, embed
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [formConfig, setFormConfig] = useState({
    name: '',
    slug: '',
    title: '',
    description: '',
    submit_button_text: 'Submit',
    success_message: "Thank you! We'll be in touch soon.",
    fields: [
      { name: 'email', type: 'email', label: 'Email Address', required: true, placeholder: 'your@email.com' }
    ],
    theme_color: '#2563eb',
    background_color: '#ffffff',
    text_color: '#111827',
    redirect_url: '',
    enable_double_optin: false,
    require_consent: true,
    consent_text: 'I agree to receive marketing communications',
    enable_recaptcha: false,
    enable_honeypot: true,
    is_active: true
  })

  useEffect(() => {
    if (activeTab === 'list') {
      fetchForms()
    }
  }, [activeTab])

  const fetchForms = async () => {
    try {
      const response = await leadFormsAPI.getAll()
      setForms(response.data)
    } catch (err) {
      console.error('Error fetching forms:', err)
    }
  }

  const handleCreateForm = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await leadFormsAPI.create(formConfig)
      setSuccess('Form created successfully!')
      setSelectedForm(response.data)
      fetchForms()
      setTimeout(() => setActiveTab('embed'), 1000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create form')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateForm = async () => {
    if (!selectedForm) return

    setLoading(true)
    setError('')

    try {
      await leadFormsAPI.update(selectedForm.id, formConfig)
      setSuccess('Form updated successfully!')
      fetchForms()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update form')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteForm = async (formId) => {
    if (!confirm('Are you sure you want to delete this form?')) return

    try {
      await leadFormsAPI.delete(formId)
      setSuccess('Form deleted successfully!')
      fetchForms()
      if (selectedForm?.id === formId) {
        setSelectedForm(null)
        setActiveTab('list')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete form')
    }
  }

  const handleDuplicateForm = async (formId) => {
    try {
      await leadFormsAPI.duplicate(formId)
      setSuccess('Form duplicated successfully!')
      fetchForms()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to duplicate form')
    }
  }

  const handleEditForm = (form) => {
    setSelectedForm(form)
    setFormConfig({
      name: form.name,
      slug: form.slug,
      title: form.title,
      description: form.description,
      submit_button_text: form.submit_button_text,
      success_message: form.success_message,
      fields: form.fields,
      theme_color: form.theme_color,
      background_color: form.background_color,
      text_color: form.text_color,
      redirect_url: form.redirect_url || '',
      enable_double_optin: form.enable_double_optin,
      require_consent: form.require_consent,
      consent_text: form.consent_text,
      enable_recaptcha: form.enable_recaptcha,
      enable_honeypot: form.enable_honeypot,
      is_active: form.is_active
    })
    setActiveTab('builder')
  }

  const addField = (fieldType) => {
    const newField = {
      name: `field_${Date.now()}`,
      type: fieldType,
      label: `New ${fieldType} field`,
      required: false,
      placeholder: '',
      options: fieldType === 'select' ? ['Option 1', 'Option 2'] : undefined
    }
    setFormConfig({
      ...formConfig,
      fields: [...formConfig.fields, newField]
    })
  }

  const updateField = (index, updates) => {
    const updatedFields = formConfig.fields.map((field, i) =>
      i === index ? { ...field, ...updates } : field
    )
    setFormConfig({ ...formConfig, fields: updatedFields })
  }

  const removeField = (index) => {
    setFormConfig({
      ...formConfig,
      fields: formConfig.fields.filter((_, i) => i !== index)
    })
  }

  const moveField = (index, direction) => {
    const newFields = [...formConfig.fields]
    const newIndex = direction === 'up' ? index - 1 : index + 1
    if (newIndex < 0 || newIndex >= newFields.length) return

    [newFields[index], newFields[newIndex]] = [newFields[newIndex], newFields[index]]
    setFormConfig({ ...formConfig, fields: newFields })
  }

  const generateSlug = (name) => {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
  }

  const getEmbedCode = () => {
    if (!selectedForm) return ''

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    return `<!-- Lead Form Embed Code -->
<div id="lead-form-${selectedForm.slug}"></div>
<script>
  (function() {
    const formSlug = '${selectedForm.slug}';
    const apiUrl = '${apiUrl}';

    // Fetch form configuration
    fetch(\`\${apiUrl}/api/forms/slug/\${formSlug}\`)
      .then(res => res.json())
      .then(form => {
        const container = document.getElementById('lead-form-' + formSlug);

        // Build form HTML
        let html = \`
          <form id="form-\${formSlug}" style="max-width: 600px; margin: 0 auto; padding: 2rem; background-color: \${form.background_color}; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h2 style="color: \${form.text_color}; margin-bottom: 0.5rem;">\${form.title}</h2>
            \${form.description ? \`<p style="color: #6b7280; margin-bottom: 1.5rem;">\${form.description}</p>\` : ''}
        \`;

        form.fields.forEach(field => {
          html += \`
            <div style="margin-bottom: 1rem;">
              <label style="display: block; color: \${form.text_color}; margin-bottom: 0.5rem; font-weight: 500;">
                \${field.label} \${field.required ? '<span style="color: red;">*</span>' : ''}
              </label>
          \`;

          if (field.type === 'textarea') {
            html += \`<textarea name="\${field.name}" placeholder="\${field.placeholder}" \${field.required ? 'required' : ''} style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 1rem;"></textarea>\`;
          } else if (field.type === 'select') {
            html += \`<select name="\${field.name}" \${field.required ? 'required' : ''} style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 1rem;">\`;
            html += \`<option value="">Select...</option>\`;
            field.options.forEach(opt => {
              html += \`<option value="\${opt}">\${opt}</option>\`;
            });
            html += \`</select>\`;
          } else if (field.type === 'checkbox') {
            html += \`<input type="checkbox" name="\${field.name}" \${field.required ? 'required' : ''} style="margin-right: 0.5rem;">\`;
          } else {
            html += \`<input type="\${field.type}" name="\${field.name}" placeholder="\${field.placeholder}" \${field.required ? 'required' : ''} style="width: 100%; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 1rem;">\`;
          }

          html += \`</div>\`;
        });

        if (form.require_consent) {
          html += \`
            <div style="margin-bottom: 1rem;">
              <label style="display: flex; align-items: center; color: \${form.text_color};">
                <input type="checkbox" name="consent" required style="margin-right: 0.5rem;">
                <span style="font-size: 0.875rem;">\${form.consent_text}</span>
              </label>
            </div>
          \`;
        }

        html += \`
            <button type="submit" style="width: 100%; padding: 0.75rem; background-color: \${form.theme_color}; color: white; border: none; border-radius: 0.375rem; font-size: 1rem; font-weight: 600; cursor: pointer;">
              \${form.submit_button_text}
            </button>
            <div id="form-message-\${formSlug}" style="margin-top: 1rem; padding: 1rem; border-radius: 0.375rem; display: none;"></div>
          </form>
        \`;

        container.innerHTML = html;

        // Handle form submission
        document.getElementById('form-' + formSlug).addEventListener('submit', function(e) {
          e.preventDefault();

          const formData = new FormData(e.target);
          const data = {};
          for (let [key, value] of formData.entries()) {
            data[key] = value;
          }

          fetch(\`\${apiUrl}/api/forms/submit/\${formSlug}\`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          })
          .then(res => res.json())
          .then(result => {
            const msg = document.getElementById('form-message-' + formSlug);
            msg.style.display = 'block';
            msg.style.backgroundColor = '#d1fae5';
            msg.style.color = '#065f46';
            msg.textContent = form.success_message;
            e.target.reset();

            if (form.redirect_url) {
              setTimeout(() => window.location.href = form.redirect_url, 2000);
            }
          })
          .catch(err => {
            const msg = document.getElementById('form-message-' + formSlug);
            msg.style.display = 'block';
            msg.style.backgroundColor = '#fee2e2';
            msg.style.color = '#991b1b';
            msg.textContent = 'Failed to submit form. Please try again.';
          });
        });
      });
  })();
</script>`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Form Builder</h1>
          <p className="text-gray-600 mt-1">Create beautiful lead capture forms for your website</p>
        </div>
        <button
          onClick={() => {
            setSelectedForm(null)
            setFormConfig({
              name: '',
              slug: '',
              title: '',
              description: '',
              submit_button_text: 'Submit',
              success_message: "Thank you! We'll be in touch soon.",
              fields: [
                { name: 'email', type: 'email', label: 'Email Address', required: true, placeholder: 'your@email.com' }
              ],
              theme_color: '#2563eb',
              background_color: '#ffffff',
              text_color: '#111827',
              redirect_url: '',
              enable_double_optin: false,
              require_consent: true,
              consent_text: 'I agree to receive marketing communications',
              enable_recaptcha: false,
              enable_honeypot: true,
              is_active: true
            })
            setActiveTab('builder')
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus size={20} />
          New Form
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
            onClick={() => setActiveTab('list')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'list'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Forms
          </button>
          {(activeTab === 'builder' || activeTab === 'preview' || activeTab === 'embed') && (
            <>
              <button
                onClick={() => setActiveTab('builder')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'builder'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Edit size={16} className="inline mr-1" />
                Builder
              </button>
              <button
                onClick={() => setActiveTab('preview')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'preview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Eye size={16} className="inline mr-1" />
                Preview
              </button>
              <button
                onClick={() => setActiveTab('embed')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'embed'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                disabled={!selectedForm}
              >
                <Code size={16} className="inline mr-1" />
                Embed Code
              </button>
            </>
          )}
        </nav>
      </div>

      {/* Forms List Tab */}
      {activeTab === 'list' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {forms.map((form) => (
            <div
              key={form.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-200"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{form.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{form.title}</p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  form.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {form.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              <div className="space-y-2 mb-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Slug</span>
                  <span className="font-mono text-xs">{form.slug}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Submissions</span>
                  <span className="font-medium">{form.submission_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Fields</span>
                  <span className="font-medium">{form.fields?.length || 0}</span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleEditForm(form)}
                  className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  <Edit size={14} className="inline mr-1" />
                  Edit
                </button>
                <button
                  onClick={() => handleDuplicateForm(form.id)}
                  className="px-3 py-2 text-sm border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
                >
                  <Copy size={14} />
                </button>
                <button
                  onClick={() => handleDeleteForm(form.id)}
                  className="px-3 py-2 text-sm border border-red-300 text-red-600 rounded hover:bg-red-50"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}

          {forms.length === 0 && (
            <div className="col-span-3 text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <Settings size={48} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Forms Yet</h3>
              <p className="text-gray-600 mb-4">Create your first lead capture form</p>
              <button
                onClick={() => setActiveTab('builder')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Form
              </button>
            </div>
          )}
        </div>
      )}

      {/* Builder Tab */}
      {activeTab === 'builder' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Form Name *
                  </label>
                  <input
                    type="text"
                    value={formConfig.name}
                    onChange={(e) => {
                      const name = e.target.value
                      setFormConfig({
                        ...formConfig,
                        name,
                        slug: formConfig.slug || generateSlug(name)
                      })
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Newsletter Signup Form"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Slug (URL identifier) *
                  </label>
                  <input
                    type="text"
                    value={formConfig.slug}
                    onChange={(e) => setFormConfig({ ...formConfig, slug: generateSlug(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                    placeholder="newsletter-signup"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Form Title *
                  </label>
                  <input
                    type="text"
                    value={formConfig.title}
                    onChange={(e) => setFormConfig({ ...formConfig, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Subscribe to our newsletter"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formConfig.description}
                    onChange={(e) => setFormConfig({ ...formConfig, description: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Get the latest updates delivered to your inbox"
                  />
                </div>
              </div>
            </div>

            {/* Form Fields */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Form Fields</h3>
              </div>

              <div className="space-y-3 mb-4">
                {formConfig.fields.map((field, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center gap-3 mb-3">
                      <button
                        onClick={() => moveField(index, 'up')}
                        disabled={index === 0}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        <GripVertical size={16} />
                      </button>

                      <div className="flex-1 grid grid-cols-2 gap-3">
                        <input
                          type="text"
                          value={field.label}
                          onChange={(e) => updateField(index, { label: e.target.value })}
                          placeholder="Field Label"
                          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        />
                        <select
                          value={field.type}
                          onChange={(e) => updateField(index, { type: e.target.value })}
                          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        >
                          {FIELD_TYPES.map(ft => (
                            <option key={ft.value} value={ft.value}>{ft.label}</option>
                          ))}
                        </select>
                      </div>

                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={field.required}
                          onChange={(e) => updateField(index, { required: e.target.checked })}
                          className="rounded text-blue-600"
                        />
                        <span className="text-xs text-gray-600">Required</span>
                      </label>

                      <button
                        onClick={() => removeField(index)}
                        className="p-1 text-red-600 hover:text-red-700"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>

                    <input
                      type="text"
                      value={field.placeholder || ''}
                      onChange={(e) => updateField(index, { placeholder: e.target.value })}
                      placeholder="Placeholder text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                {FIELD_TYPES.map(fieldType => (
                  <button
                    key={fieldType.value}
                    onClick={() => addField(fieldType.value)}
                    className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    <fieldType.icon size={16} />
                    {fieldType.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Settings */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Submit Button Text
                  </label>
                  <input
                    type="text"
                    value={formConfig.submit_button_text}
                    onChange={(e) => setFormConfig({ ...formConfig, submit_button_text: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Success Message
                  </label>
                  <textarea
                    value={formConfig.success_message}
                    onChange={(e) => setFormConfig({ ...formConfig, success_message: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formConfig.require_consent}
                      onChange={(e) => setFormConfig({ ...formConfig, require_consent: e.target.checked })}
                      className="rounded text-blue-600"
                    />
                    <span className="text-sm text-gray-700">Require Consent</span>
                  </label>

                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formConfig.is_active}
                      onChange={(e) => setFormConfig({ ...formConfig, is_active: e.target.checked })}
                      className="rounded text-blue-600"
                    />
                    <span className="text-sm text-gray-700">Active</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel - Actions */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={selectedForm ? handleUpdateForm : handleCreateForm}
                  disabled={loading || !formConfig.name || !formConfig.slug || !formConfig.title}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Save size={16} className="inline mr-2" />
                  {loading ? 'Saving...' : selectedForm ? 'Update Form' : 'Create Form'}
                </button>

                <button
                  onClick={() => setActiveTab('preview')}
                  className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  <Eye size={16} className="inline mr-2" />
                  Preview
                </button>

                {selectedForm && (
                  <button
                    onClick={() => setActiveTab('embed')}
                    className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    <Code size={16} className="inline mr-2" />
                    Get Embed Code
                  </button>
                )}

                <button
                  onClick={() => {
                    setSelectedForm(null)
                    setActiveTab('list')
                  }}
                  className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Preview Tab */}
      {activeTab === 'preview' && (
        <div className="max-w-3xl mx-auto">
          <div
            className="rounded-lg p-8 shadow-lg"
            style={{
              backgroundColor: formConfig.background_color,
              color: formConfig.text_color
            }}
          >
            <h2 className="text-2xl font-bold mb-2">{formConfig.title || 'Form Title'}</h2>
            {formConfig.description && (
              <p className="text-gray-600 mb-6">{formConfig.description}</p>
            )}

            <form className="space-y-4">
              {formConfig.fields.map((field, index) => (
                <div key={index}>
                  <label className="block text-sm font-medium mb-2">
                    {field.label} {field.required && <span className="text-red-600">*</span>}
                  </label>
                  {field.type === 'textarea' ? (
                    <textarea
                      placeholder={field.placeholder}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                      rows={3}
                    />
                  ) : field.type === 'select' ? (
                    <select className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                      <option>Select...</option>
                      {field.options?.map((opt, i) => (
                        <option key={i}>{opt}</option>
                      ))}
                    </select>
                  ) : field.type === 'checkbox' ? (
                    <input type="checkbox" className="rounded text-blue-600" />
                  ) : (
                    <input
                      type={field.type}
                      placeholder={field.placeholder}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    />
                  )}
                </div>
              ))}

              {formConfig.require_consent && (
                <div className="flex items-start gap-2">
                  <input type="checkbox" className="mt-1 rounded text-blue-600" />
                  <span className="text-sm">{formConfig.consent_text}</span>
                </div>
              )}

              <button
                type="button"
                style={{ backgroundColor: formConfig.theme_color }}
                className="w-full px-4 py-3 text-white rounded-lg font-semibold"
              >
                {formConfig.submit_button_text}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Embed Code Tab */}
      {activeTab === 'embed' && selectedForm && (
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Embed Code</h3>
            <p className="text-gray-600 mb-4">
              Copy and paste this code into your website where you want the form to appear.
            </p>

            <div className="relative">
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{getEmbedCode()}</code>
              </pre>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(getEmbedCode())
                  setSuccess('Embed code copied to clipboard!')
                }}
                className="absolute top-2 right-2 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                <Copy size={14} className="inline mr-1" />
                Copy
              </button>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-900">
                <strong>Form URL:</strong> {import.meta.env.VITE_API_URL || 'http://localhost:8000'}/forms/{selectedForm.slug}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
