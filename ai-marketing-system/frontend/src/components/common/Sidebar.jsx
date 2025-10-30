import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Mail,
  Sparkles,
  BarChart3,
  FileText,
  Calendar,
  Filter,
  FlaskConical,
  Webhook,
  Store,
  X,
  Download,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Leads', href: '/leads', icon: Users },
  { name: 'Lead Sourcing', href: '/lead-sourcing', icon: Download },
  { name: 'Segments', href: '/segments', icon: Filter },
  { name: 'Campaigns', href: '/campaigns', icon: Mail },
  { name: 'A/B Testing', href: '/ab-tests', icon: FlaskConical },
  { name: 'Content Generator', href: '/content', icon: Sparkles },
  { name: 'Email Templates', href: '/templates', icon: FileText },
  { name: 'Social Scheduling', href: '/scheduling', icon: Calendar },
  { name: 'Webhooks', href: '/webhooks', icon: Webhook },
  { name: 'Shopify', href: '/shopify', icon: Store },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
]

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden transition-opacity"
          onClick={onClose}
        ></div>
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out z-50
          md:sticky md:top-0 md:h-screen md:translate-x-0 md:z-20
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Mobile header */}
        <div className="md:hidden flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-sm">AI</span>
            </div>
            <span className="font-bold text-gray-900">Menu</span>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1 overflow-y-auto h-[calc(100vh-73px)] md:h-full">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              end={item.href === '/'}
              onClick={() => {
                // Close mobile menu when link is clicked
                if (window.innerWidth < 768) {
                  onClose()
                }
              }}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 text-sm font-medium rounded-xl transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-primary-50 to-primary-100 text-primary-700 shadow-sm'
                    : 'text-gray-700 hover:bg-gray-50 hover:translate-x-1'
                }`
              }
            >
              <item.icon size={20} />
              <span>{item.name}</span>
            </NavLink>
          ))}

          {/* Sidebar footer */}
          <div className="mt-8 pt-4 border-t border-gray-200">
            <div className="px-4 py-3 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl">
              <p className="text-xs font-semibold text-gray-900 mb-1">
                AI Powered
              </p>
              <p className="text-xs text-gray-600">
                Claude 3.5 Sonnet
              </p>
            </div>
          </div>
        </nav>
      </aside>
    </>
  )
}
