import { useState, useEffect } from 'react';
import { Store, RefreshCw, Users, ShoppingCart, Package, CheckCircle, XCircle, AlertCircle, Download } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function ShopifyPage() {
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchStores();
  }, []);

  const fetchStores = async () => {
    try {
      const response = await api.get('/api/shopify/stores');
      setStores(response.data);

      // Auto-select first configured store
      const firstConfigured = response.data.find(s => s.configured);
      if (firstConfigured) {
        setSelectedStore(firstConfigured);
        await auditStore(firstConfigured.id);
      }
    } catch (error) {
      console.error('Error fetching stores:', error);
      toast.error('Failed to load Shopify stores');
    }
  };

  const auditStore = async (storeId) => {
    setLoading(true);
    try {
      const response = await api.get(`/api/shopify/stores/${storeId}/audit`);
      setAuditData(response.data);

      if (response.data.configured && !response.data.error) {
        toast.success('Store audit completed successfully');
      }
    } catch (error) {
      console.error('Error auditing store:', error);
      toast.error('Failed to audit store');
      setAuditData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleStoreSelect = async (store) => {
    setSelectedStore(store);
    setAuditData(null);
    if (store.configured) {
      await auditStore(store.id);
    }
  };

  const handleRefreshAudit = async () => {
    if (selectedStore && selectedStore.configured) {
      await auditStore(selectedStore.id);
    }
  };

  const handleSyncCustomers = async () => {
    if (!selectedStore) return;

    setSyncing(true);
    try {
      const response = await api.post(`/api/shopify/stores/${selectedStore.id}/sync-customers`);
      const { synced, skipped, errors, total_processed } = response.data;

      toast.success(
        `Sync completed! ${synced} imported, ${skipped} skipped, ${errors} errors`,
        { duration: 5000 }
      );

      // Refresh audit after sync
      await auditStore(selectedStore.id);
    } catch (error) {
      console.error('Error syncing customers:', error);
      toast.error('Failed to sync customers');
    } finally {
      setSyncing(false);
    }
  };

  const getStatusIcon = (status) => {
    if (status === 'healthy') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status === 'error') return <XCircle className="w-5 h-5 text-red-500" />;
    return <AlertCircle className="w-5 h-5 text-yellow-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Shopify Integration</h1>
          <p className="mt-2 text-gray-600">
            Audit your Shopify stores and sync customers to your marketing database
          </p>
        </div>
        {selectedStore && selectedStore.configured && (
          <button
            onClick={handleRefreshAudit}
            disabled={loading}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Audit</span>
          </button>
        )}
      </div>

      {/* Store Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Store</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stores.map((store) => (
            <button
              key={store.id}
              onClick={() => handleStoreSelect(store)}
              className={`p-4 border-2 rounded-lg text-left transition-all ${
                selectedStore?.id === store.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              } ${!store.configured ? 'opacity-60' : ''}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <Store className="w-5 h-5 text-gray-600 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900">{store.name}</h3>
                    <p className="text-sm text-gray-500">{store.store_url}</p>
                    <div className="mt-2">
                      {store.configured ? (
                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Configured
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          Not Configured
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Not Configured Message */}
      {selectedStore && !selectedStore.configured && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-6 h-6 text-yellow-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-yellow-900 mb-2">Store Not Configured</h3>
              <p className="text-yellow-800 mb-3">
                This store requires API credentials to connect. Please add the following to your backend <code className="bg-yellow-100 px-2 py-1 rounded text-sm">.env</code> file:
              </p>
              <div className="bg-yellow-100 p-3 rounded font-mono text-sm text-yellow-900">
                SHOPIFY_STORE_URL_{selectedStore.id}={selectedStore.store_url}<br/>
                SHOPIFY_API_KEY_{selectedStore.id}=your-api-key<br/>
                SHOPIFY_ACCESS_TOKEN_{selectedStore.id}=your-access-token
              </div>
              <p className="text-yellow-800 mt-3 text-sm">
                Get your API credentials from: <a href="https://admin.shopify.com/settings/apps" target="_blank" rel="noopener noreferrer" className="underline">Shopify Admin → Apps → Develop apps</a>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Auditing store...</p>
        </div>
      )}

      {/* Audit Results */}
      {auditData && auditData.configured && !loading && (
        <>
          {/* Store Health Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Store Status</h2>
              {auditData.status && getStatusIcon(auditData.status)}
            </div>

            {auditData.shop_info && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Shop Name</p>
                  <p className="font-semibold text-gray-900">{auditData.shop_info.name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Domain</p>
                  <p className="font-semibold text-gray-900">{auditData.shop_info.domain || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Currency</p>
                  <p className="font-semibold text-gray-900">{auditData.shop_info.currency || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Plan</p>
                  <p className="font-semibold text-gray-900">{auditData.shop_info.plan_name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Country</p>
                  <p className="font-semibold text-gray-900">{auditData.shop_info.country || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Timezone</p>
                  <p className="font-semibold text-gray-900">{auditData.shop_info.timezone || 'N/A'}</p>
                </div>
              </div>
            )}

            {auditData.audit_timestamp && (
              <p className="text-xs text-gray-500 mt-4">
                Last audited: {new Date(auditData.audit_timestamp).toLocaleString()}
              </p>
            )}
          </div>

          {/* Metrics */}
          {auditData.metrics && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Total Customers</p>
                    <p className="text-3xl font-bold text-gray-900">{auditData.metrics.total_customers.toLocaleString()}</p>
                  </div>
                  <Users className="w-12 h-12 text-blue-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Total Orders</p>
                    <p className="text-3xl font-bold text-gray-900">{auditData.metrics.total_orders.toLocaleString()}</p>
                  </div>
                  <ShoppingCart className="w-12 h-12 text-green-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Total Products</p>
                    <p className="text-3xl font-bold text-gray-900">{auditData.metrics.total_products.toLocaleString()}</p>
                  </div>
                  <Package className="w-12 h-12 text-purple-500" />
                </div>
              </div>
            </div>
          )}

          {/* Sync Customers */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Customer Sync</h2>
            <p className="text-gray-600 mb-4">
              Import Shopify customers as marketing leads. Only customers who have opted in to marketing will have email consent enabled.
            </p>
            <button
              onClick={handleSyncCustomers}
              disabled={syncing}
              className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className={`w-5 h-5 ${syncing ? 'animate-bounce' : ''}`} />
              <span>{syncing ? 'Syncing...' : 'Sync Customers to Leads'}</span>
            </button>
          </div>

          {/* Error Display */}
          {auditData.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-start space-x-3">
                <XCircle className="w-6 h-6 text-red-600 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-2">Error</h3>
                  <p className="text-red-800">{auditData.error}</p>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* No Store Selected */}
      {!selectedStore && !loading && (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <Store className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Store Selected</h3>
          <p className="text-gray-600">Select a store above to view audit results</p>
        </div>
      )}
    </div>
  );
}
