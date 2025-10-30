import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

// Pages
import DashboardPage from './pages/DashboardPage'
import LeadsPage from './pages/LeadsPage'
import LeadSourcingPage from './pages/LeadSourcingPage'
import CampaignsPage from './pages/CampaignsPage'
import ContentPage from './pages/ContentPage'
import AnalyticsPage from './pages/AnalyticsPage'
import TemplatesPage from './pages/TemplatesPage'
import SchedulingPage from './pages/SchedulingPage'
import SegmentsPage from './pages/SegmentsPage'
import ABTestPage from './pages/ABTestPage'
import WebhooksPage from './pages/WebhooksPage'
import ShopifyPage from './pages/ShopifyPage'

// Layout
import Layout from './components/common/Layout'

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        {/* All Routes - No Auth Required */}
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="leads" element={<LeadsPage />} />
          <Route path="lead-sourcing" element={<LeadSourcingPage />} />
          <Route path="segments" element={<SegmentsPage />} />
          <Route path="campaigns" element={<CampaignsPage />} />
          <Route path="ab-tests" element={<ABTestPage />} />
          <Route path="content" element={<ContentPage />} />
          <Route path="templates" element={<TemplatesPage />} />
          <Route path="scheduling" element={<SchedulingPage />} />
          <Route path="webhooks" element={<WebhooksPage />} />
          <Route path="shopify" element={<ShopifyPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
