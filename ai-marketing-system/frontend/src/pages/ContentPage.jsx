import { useState, useEffect } from 'react'
import { contentAPI, scheduleAPI, shopifyAPI } from '../services/api'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Sparkles, Copy, Download, ThumbsUp, RefreshCw, Trash2, Calendar, Store, ShoppingBag } from 'lucide-react'

export default function ContentPage() {
  const navigate = useNavigate()
  const [contents, setContents] = useState([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [selectedContent, setSelectedContent] = useState(null)
  const [scheduleTime, setScheduleTime] = useState('')

  const [formData, setFormData] = useState({
    content_type: 'social_post',
    platform: 'facebook',
    topic: '',
    tone: 'professional',
    target_audience: 'cyclists and triathletes',
    additional_context: '',
    include_image: false,
    product_image_base64: null,
  })
  
  const [productImagePreview, setProductImagePreview] = useState(null)

  // Shopify state
  const [shopifyStores, setShopifyStores] = useState([])
  const [selectedStore, setSelectedStore] = useState(null)
  const [shopifyProducts, setShopifyProducts] = useState([])
  const [loadingShopify, setLoadingShopify] = useState(false)
  const [imageSource, setImageSource] = useState('upload') // 'upload' or 'shopify'

  useEffect(() => {
    fetchContents()
  }, [])

  // Fetch Shopify stores when include_image is checked
  useEffect(() => {
    if (formData.include_image && shopifyStores.length === 0) {
      fetchShopifyStores()
    }
  }, [formData.include_image])

  // Fetch products when a store is selected
  useEffect(() => {
    if (selectedStore) {
      fetchShopifyProducts(selectedStore)
    }
  }, [selectedStore])

  const fetchShopifyStores = async () => {
    try {
      const response = await shopifyAPI.getStores()
      setShopifyStores(response.data || [])
      // Auto-select first store if available
      if (response.data && response.data.length > 0) {
        setSelectedStore(response.data[0].id)
      }
    } catch (error) {
      console.error('Failed to fetch Shopify stores:', error)
    }
  }

  const fetchShopifyProducts = async (storeId) => {
    setLoadingShopify(true)
    try {
      const response = await shopifyAPI.getProducts(storeId, 50)
      setShopifyProducts(response.data.products || [])
    } catch (error) {
      console.error('Failed to fetch Shopify products:', error)
      toast.error('Failed to load Shopify products')
    } finally {
      setLoadingShopify(false)
    }
  }

  const handleShopifyImageSelect = async (imageUrl, productTitle) => {
    try {
      // Fetch the image and convert to base64
      const response = await fetch(imageUrl)
      const blob = await response.blob()

      const reader = new FileReader()
      reader.onload = (e) => {
        const base64String = e.target.result
        const base64Data = base64String.split(',')[1]

        setFormData({ ...formData, product_image_base64: base64Data })
        setProductImagePreview(base64String)
        toast.success(`Selected: ${productTitle}`)
      }
      reader.onerror = () => {
        toast.error('Failed to load image')
      }
      reader.readAsDataURL(blob)
    } catch (error) {
      console.error('Failed to fetch Shopify image:', error)
      toast.error('Failed to load Shopify image')
    }
  }

  const fetchContents = async () => {
    setLoading(true)
    try {
      const response = await contentAPI.getAll()
      setContents(response.data)
    } catch (error) {
      toast.error('Failed to fetch contents')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    setGenerating(true)

    try {
      await contentAPI.generate(formData)
      toast.success('Content generated successfully!')
      setShowForm(false)
      setFormData({
        content_type: 'social_post',
        platform: 'facebook',
        topic: '',
        tone: 'professional',
        target_audience: 'cyclists and triathletes',
        additional_context: '',
        include_image: false,
        product_image_base64: null,
      })
      setProductImagePreview(null)
      setImageSource('upload')
      fetchContents()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate content')
    } finally {
      setGenerating(false)
    }
  }

  const handleApprove = async (id) => {
    try {
      await contentAPI.update(id, { status: 'approved' })
      toast.success('Content approved!')
      fetchContents()
    } catch (error) {
      toast.error('Failed to approve content')
    }
  }

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  const handleSchedule = (content) => {
    setSelectedContent(content)
    setShowScheduleModal(true)
  }

  const handleScheduleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedContent || !scheduleTime) return

    try {
      await scheduleAPI.scheduleFromContent({
        content_id: selectedContent.id,
        scheduled_time: scheduleTime,
        timezone: 'UTC',
        auto_post: true,
      })
      toast.success('Content scheduled successfully!')
      setShowScheduleModal(false)
      setSelectedContent(null)
      setScheduleTime('')
      fetchContents()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to schedule content')
    }
  }
  
  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file')
      return
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image must be smaller than 5MB')
      return
    }
    
    // Read file as base64
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64String = e.target.result
      // Remove the data URL prefix (data:image/jpeg;base64,)
      const base64Data = base64String.split(',')[1]
      
      setFormData({ ...formData, product_image_base64: base64Data })
      setProductImagePreview(base64String)
      toast.success('Product image uploaded!')
    }
    reader.onerror = () => {
      toast.error('Failed to read image file')
    }
    reader.readAsDataURL(file)
  }
  
  const handleRemoveImage = () => {
    setFormData({ ...formData, product_image_base64: null })
    setProductImagePreview(null)
    setImageSource('upload')
    // Reset file input
    const fileInput = document.getElementById('product-image-upload')
    if (fileInput) fileInput.value = ''
  }

  const handleImprove = async (id) => {
    try {
      toast.loading('Improving content...')
      await contentAPI.improve(id, 'engagement')
      toast.dismiss()
      toast.success('Content improved!')
      fetchContents()
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to improve content')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this content? This action cannot be undone.')) {
      return
    }

    try {
      await contentAPI.delete(id)
      toast.success('Content deleted successfully!')
      fetchContents()
    } catch (error) {
      toast.error('Failed to delete content')
    }
  }

  const handleDownloadImage = (imageUrl, contentTitle) => {
    try {
      // Extract filename from the image URL (e.g., /uploads/generated_20251028_183015.png)
      const filename = imageUrl.split('/').pop()

      // Create a temporary link element to download via the new endpoint
      const link = document.createElement('a')
      link.href = `http://localhost:8000/api/content/download-image/${filename}`
      link.download = contentTitle
        ? `${contentTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.png`
        : filename

      // Append to body, click, and remove
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast.success('Image download started!')
    } catch (error) {
      toast.error('Failed to download image')
      console.error('Download error:', error)
    }
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
            Content Generator
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">
            Generate AI-powered marketing content
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:shadow-lg transition-all font-medium"
        >
          <Sparkles size={20} />
          <span>Generate Content</span>
        </button>
      </div>

      {/* Generation Form */}
      {showForm && (
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-sm p-5 sm:p-6 border border-gray-200">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">
            Generate New Content
          </h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content Type *
                </label>
                <select
                  value={formData.content_type}
                  onChange={(e) =>
                    setFormData({ ...formData, content_type: e.target.value })
                  }
                  className="w-full px-3 sm:px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base bg-white text-gray-900 transition-all"
                >
                  <option value="social_post">📱 Social Media Post</option>
                  <option value="email_template">📧 Email Template</option>
                  <option value="ad_copy">📢 Ad Copy</option>
                </select>
              </div>

              {formData.content_type !== 'email_template' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Platform *
                  </label>
                  <select
                    value={formData.platform}
                    onChange={(e) =>
                      setFormData({ ...formData, platform: e.target.value })
                    }
                    className="w-full px-3 sm:px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base bg-white text-gray-900 transition-all"
                  >
                    <option value="facebook">Facebook</option>
                    <option value="instagram">Instagram</option>
                    <option value="twitter">Twitter/X</option>
                    <option value="linkedin">LinkedIn</option>
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tone *
                </label>
                <select
                  value={formData.tone}
                  onChange={(e) =>
                    setFormData({ ...formData, tone: e.target.value })
                  }
                  className="w-full px-3 sm:px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base bg-white text-gray-900 transition-all"
                >
                  <option value="professional">💼 Professional</option>
                  <option value="casual">😊 Casual</option>
                  <option value="friendly">🤝 Friendly</option>
                  <option value="enthusiastic">🎉 Enthusiastic</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Audience
                </label>
                <input
                  type="text"
                  value={formData.target_audience}
                  onChange={(e) =>
                    setFormData({ ...formData, target_audience: e.target.value })
                  }
                  placeholder="e.g., cyclists and triathletes"
                  className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 placeholder-gray-400 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Topic / Subject *
              </label>
              <input
                type="text"
                value={formData.topic}
                onChange={(e) =>
                  setFormData({ ...formData, topic: e.target.value })
                }
                required
                placeholder="e.g., New triathlon bike saddle launch"
                className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 placeholder-gray-400 transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                value={formData.additional_context}
                onChange={(e) =>
                  setFormData({ ...formData, additional_context: e.target.value })
                }
                rows={3}
                placeholder="Any additional details, product features, or specific points to mention..."
                className="w-full px-3 sm:px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm sm:text-base text-gray-900 placeholder-gray-400 transition-all resize-none"
              />
            </div>

            {/* Image Generation Options */}
            <div className="space-y-4">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="include_image"
                    checked={formData.include_image}
                    onChange={(e) =>
                      setFormData({ ...formData, include_image: e.target.checked })
                    }
                    className="w-4 h-4 sm:w-5 sm:h-5 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
                  />
                  <label htmlFor="include_image" className="text-xs sm:text-sm text-gray-700 font-medium">
                    🖼️ Generate AI image for visual content
                  </label>
                </div>
              </div>

              {/* Product Image Upload - Only show when include_image is checked */}
              {formData.include_image && (
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-lg border-2 border-dashed border-purple-200">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-semibold text-gray-800 flex items-center gap-2">
                        <span>✨</span>
                        <span>Upload Your Product Image (Optional)</span>
                      </label>
                    </div>

                    <p className="text-xs text-gray-600">
                      Upload your own product photo or select from your Shopify store, and let AI enhance it with professional backgrounds, lighting, and effects!
                    </p>

                    {/* Image Source Tabs */}
                    <div className="flex gap-2 mt-3">
                      <button
                        type="button"
                        onClick={() => setImageSource('upload')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          imageSource === 'upload'
                            ? 'bg-purple-600 text-white shadow-md'
                            : 'bg-white text-gray-600 hover:bg-purple-100 border border-purple-200'
                        }`}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        Upload
                      </button>
                      <button
                        type="button"
                        onClick={() => setImageSource('shopify')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          imageSource === 'shopify'
                            ? 'bg-purple-600 text-white shadow-md'
                            : 'bg-white text-gray-600 hover:bg-purple-100 border border-purple-200'
                        }`}
                      >
                        <Store size={16} />
                        Shopify Store
                      </button>
                    </div>

                    {/* Upload Tab Content */}
                    {imageSource === 'upload' && !productImagePreview && (
                      <div className="mt-2">
                        <label
                          htmlFor="product-image-upload"
                          className="flex flex-col items-center justify-center w-full h-32 border-2 border-purple-300 border-dashed rounded-lg cursor-pointer bg-white hover:bg-purple-50 transition-colors"
                        >
                          <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <svg
                              className="w-8 h-8 mb-2 text-purple-500"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                              />
                            </svg>
                            <p className="text-xs text-gray-600 font-medium">
                              Click to upload product image
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              PNG, JPG or WEBP (max 5MB)
                            </p>
                          </div>
                          <input
                            id="product-image-upload"
                            type="file"
                            className="hidden"
                            accept="image/*"
                            onChange={handleImageUpload}
                          />
                        </label>
                      </div>
                    )}

                    {/* Shopify Tab Content */}
                    {imageSource === 'shopify' && !productImagePreview && (
                      <div className="mt-2 space-y-3">
                        {/* Store Selector */}
                        {shopifyStores.length > 0 && (
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Select Store
                            </label>
                            <select
                              value={selectedStore || ''}
                              onChange={(e) => setSelectedStore(Number(e.target.value))}
                              className="w-full px-3 py-2 text-sm border border-purple-200 rounded-lg bg-white text-gray-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                            >
                              {shopifyStores.map((store) => (
                                <option key={store.id} value={store.id}>
                                  {store.name}
                                </option>
                              ))}
                            </select>
                          </div>
                        )}

                        {/* Products Gallery */}
                        {loadingShopify ? (
                          <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                            <span className="ml-3 text-sm text-gray-600">Loading products...</span>
                          </div>
                        ) : shopifyProducts.length > 0 ? (
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-2">
                              Select a Product Image ({shopifyProducts.filter(p => p.images?.length > 0).length} products with images)
                            </label>
                            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-64 overflow-y-auto p-2 bg-white rounded-lg border border-purple-200">
                              {shopifyProducts
                                .filter((product) => product.images && product.images.length > 0)
                                .map((product) => (
                                  <button
                                    key={product.id}
                                    type="button"
                                    onClick={() => handleShopifyImageSelect(product.images[0].src, product.title)}
                                    className="group relative aspect-square rounded-lg overflow-hidden border-2 border-transparent hover:border-purple-500 transition-all focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    title={product.title}
                                  >
                                    <img
                                      src={product.images[0].src}
                                      alt={product.title}
                                      className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                                      <div className="absolute bottom-0 left-0 right-0 p-1">
                                        <p className="text-white text-xs truncate font-medium">
                                          {product.title}
                                        </p>
                                      </div>
                                    </div>
                                  </button>
                                ))}
                            </div>
                          </div>
                        ) : shopifyStores.length === 0 ? (
                          <div className="text-center py-6 bg-white rounded-lg border border-purple-200">
                            <Store className="mx-auto h-10 w-10 text-gray-400 mb-2" />
                            <p className="text-sm text-gray-600">No Shopify stores connected</p>
                            <p className="text-xs text-gray-500 mt-1">Connect a Shopify store to select product images</p>
                          </div>
                        ) : (
                          <div className="text-center py-6 bg-white rounded-lg border border-purple-200">
                            <ShoppingBag className="mx-auto h-10 w-10 text-gray-400 mb-2" />
                            <p className="text-sm text-gray-600">No products with images found</p>
                            <p className="text-xs text-gray-500 mt-1">Add product images in your Shopify store</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Selected Image Preview (shown for both tabs) */}
                    {productImagePreview && (
                      <div className="mt-2 relative">
                        <img
                          src={productImagePreview}
                          alt="Product preview"
                          className="w-full h-48 object-cover rounded-lg border-2 border-purple-200"
                        />
                        <button
                          type="button"
                          onClick={handleRemoveImage}
                          className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600 transition-colors shadow-lg"
                          title="Remove image"
                        >
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        </button>
                        <div className="mt-2 text-xs text-green-700 bg-green-100 px-3 py-2 rounded-lg flex items-center gap-2">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          <span>Product image ready! AI will enhance it with professional effects.</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <button
                type="submit"
                disabled={generating}
                className="flex-1 flex items-center justify-center space-x-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white py-3 px-4 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {generating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    <span>Generate Content</span>
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="sm:w-auto px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Content List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {contents.map((content) => (
            <div
              key={content.id}
              className="bg-white rounded-xl sm:rounded-2xl shadow-sm p-5 sm:p-6 border border-gray-100 hover:shadow-lg transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex flex-wrap gap-2">
                  <span className="inline-block px-2.5 py-1 text-xs font-semibold bg-gradient-to-r from-primary-100 to-primary-200 text-primary-700 rounded-lg">
                    {content.platform || content.content_type}
                  </span>
                  <span
                    className={`inline-block px-2.5 py-1 text-xs font-semibold rounded-lg ${
                      content.status === 'approved'
                        ? 'bg-green-100 text-green-700'
                        : content.status === 'posted'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {content.status}
                  </span>
                </div>
              </div>

              {content.title && (
                <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-2">
                  {content.title}
                </h3>
              )}

              {content.caption && (
                <p className="text-sm sm:text-base text-gray-700 mb-3 whitespace-pre-wrap line-clamp-4 hover:line-clamp-none">
                  {content.caption}
                </p>
              )}

              {content.body && (
                <div
                  className="text-sm sm:text-base text-gray-700 mb-3 prose prose-sm max-w-none line-clamp-4 hover:line-clamp-none"
                  dangerouslySetInnerHTML={{ __html: content.body }}
                />
              )}

              {content.hashtags && (
                <p className="text-primary-600 text-xs sm:text-sm mb-3 break-words">
                  {content.hashtags}
                </p>
              )}

              {content.image_url && (
                <div className="mb-3 rounded-lg overflow-hidden border border-gray-200">
                  <img
                    src={`http://localhost:8000${content.image_url}`}
                    alt={content.title || 'Generated image'}
                    className="w-full h-auto"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      console.error('Failed to load image:', content.image_url);
                    }}
                  />
                </div>
              )}

              <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-100">
                <button
                  onClick={() =>
                    handleCopy(
                      `${content.title || ''}\n\n${content.caption || content.body || ''}\n\n${content.hashtags || ''}`
                    )
                  }
                  className="flex items-center space-x-1.5 px-3 py-2 text-xs sm:text-sm font-medium bg-black text-white hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <Copy size={14} />
                  <span>Copy</span>
                </button>

                {content.image_url && (
                  <button
                    onClick={() => handleDownloadImage(content.image_url, content.title)}
                    className="flex items-center space-x-1.5 px-3 py-2 text-xs sm:text-sm font-medium bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg transition-colors"
                  >
                    <Download size={14} />
                    <span>Download Image</span>
                  </button>
                )}

                {content.status === 'draft' && (
                  <>
                    <button
                      onClick={() => handleApprove(content.id)}
                      className="flex items-center space-x-1.5 px-3 py-2 text-xs sm:text-sm font-medium bg-green-100 text-green-700 hover:bg-green-200 rounded-lg transition-colors"
                    >
                      <ThumbsUp size={14} />
                      <span>Approve</span>
                    </button>
                    {content.content_type === 'social_post' && (
                      <button
                        onClick={() => handleSchedule(content)}
                        className="flex items-center space-x-1.5 px-3 py-2 text-xs sm:text-sm font-medium bg-purple-100 text-purple-700 hover:bg-purple-200 rounded-lg transition-colors"
                      >
                        <Calendar size={14} />
                        <span>Schedule</span>
                      </button>
                    )}
                    <button
                      onClick={() => handleImprove(content.id)}
                      className="flex items-center space-x-1.5 px-3 py-2 text-xs sm:text-sm font-medium bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg transition-colors"
                    >
                      <RefreshCw size={14} />
                      <span>Improve</span>
                    </button>
                  </>
                )}

                <button
                  onClick={() => handleDelete(content.id)}
                  className="flex items-center space-x-1.5 px-3 py-2 text-xs sm:text-sm font-medium bg-red-100 text-red-700 hover:bg-red-200 rounded-lg transition-colors ml-auto"
                >
                  <Trash2 size={14} />
                  <span>Delete</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && contents.length === 0 && (
        <div className="text-center py-12 sm:py-16 bg-gradient-to-br from-white to-gray-50 rounded-2xl border-2 border-dashed border-gray-300">
          <div className="max-w-md mx-auto px-4">
            <div className="inline-flex p-4 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl mb-4">
              <Sparkles className="h-10 w-10 sm:h-12 sm:w-12 text-primary-600" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-2">
              Start Creating Amazing Content
            </h3>
            <p className="text-sm sm:text-base text-gray-600 mb-6">
              Use AI to generate engaging social media posts, email templates, and ad copy in seconds
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:shadow-lg transition-all font-medium"
            >
              <Sparkles size={20} />
              <span>Generate Your First Content</span>
            </button>

            {/* Feature highlights */}
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-2xl mb-2">📱</div>
                <div className="text-xs sm:text-sm font-semibold text-gray-900">Social Posts</div>
                <div className="text-xs text-gray-600 mt-1">Facebook, Instagram, Twitter & LinkedIn</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-2xl mb-2">📧</div>
                <div className="text-xs sm:text-sm font-semibold text-gray-900">Email Templates</div>
                <div className="text-xs text-gray-600 mt-1">Professional marketing emails</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-2xl mb-2">📢</div>
                <div className="text-xs sm:text-sm font-semibold text-gray-900">Ad Copy</div>
                <div className="text-xs text-gray-600 mt-1">Compelling advertising content</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Schedule Modal */}
      {showScheduleModal && selectedContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
            <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-900">Schedule Post</h3>
              <button
                onClick={() => {
                  setShowScheduleModal(false)
                  setSelectedContent(null)
                  setScheduleTime('')
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <Trash2 size={20} />
              </button>
            </div>

            <form onSubmit={handleScheduleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Platform
                </label>
                <p className="text-gray-900 capitalize px-4 py-2 bg-gray-50 rounded-lg">
                  {selectedContent.platform}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content Preview
                </label>
                <div className="text-sm text-gray-700 p-3 bg-gray-50 rounded-lg max-h-32 overflow-y-auto">
                  {selectedContent.caption?.substring(0, 150)}
                  {selectedContent.caption?.length > 150 && '...'}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Schedule Time *
                </label>
                <input
                  type="datetime-local"
                  value={scheduleTime}
                  onChange={(e) => setScheduleTime(e.target.value)}
                  required
                  min={new Date().toISOString().slice(0, 16)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Post will be automatically published at this time
                </p>
              </div>

              <div className="flex items-center gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                >
                  Schedule Post
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowScheduleModal(false)
                    setSelectedContent(null)
                    setScheduleTime('')
                  }}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
