import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './hooks/useAuth'

// Auth Components
import ProtectedRoute from './components/ProtectedRoute'

// Auth Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

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
import MetaABTestPage from './pages/MetaABTestPage'
import WebhooksPage from './pages/WebhooksPage'
import ShopifyPage from './pages/ShopifyPage'
import OutreachPage from './pages/OutreachPage'
import RetargetingPage from './pages/RetargetingPage'
import FormBuilderPage from './pages/FormBuilderPage'
import LeadAnalyticsPage from './pages/LeadAnalyticsPage'

// Layout
import Layout from './components/common/Layout'

function App() {
  return (
    <Router>
      <AuthProvider>
        <Toaster position="top-right" />
        <Routes>
          {/* Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<DashboardPage />} />
            <Route path="leads" element={<LeadsPage />} />
            <Route path="lead-sourcing" element={<LeadSourcingPage />} />
            <Route path="form-builder" element={<FormBuilderPage />} />
            <Route path="segments" element={<SegmentsPage />} />
            <Route path="campaigns" element={<CampaignsPage />} />
            <Route path="outreach" element={<OutreachPage />} />
            <Route path="retargeting" element={<RetargetingPage />} />
            <Route path="ab-tests" element={<ABTestPage />} />
            <Route path="meta-ab-tests" element={<MetaABTestPage />} />
            <Route path="content" element={<ContentPage />} />
            <Route path="templates" element={<TemplatesPage />} />
            <Route path="scheduling" element={<SchedulingPage />} />
            <Route path="webhooks" element={<WebhooksPage />} />
            <Route path="shopify" element={<ShopifyPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="lead-analytics" element={<LeadAnalyticsPage />} />
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
