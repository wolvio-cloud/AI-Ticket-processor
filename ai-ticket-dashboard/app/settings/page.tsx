'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  Settings as SettingsIcon, Brain, Menu, FileText, TrendingUp, Shield, User,
  Bell, Globe, Lock, Database, Zap, Save, RefreshCw, Eye, EyeOff,
  CheckCircle2, AlertCircle, BarChart3
} from 'lucide-react'
import { cn } from '@/lib/utils'

export default function SettingsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [apiUrl, setApiUrl] = useState('http://localhost:8000')
  const [wsUrl, setWsUrl] = useState('ws://localhost:8000')
  const [refreshInterval, setRefreshInterval] = useState('30000')
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [enableWebSocket, setEnableWebSocket] = useState(true)
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKey, setApiKey] = useState('sk-xxxxxxxxxxxxxxxxxxxxxxxx')
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle')

  const handleSave = () => {
    setSaveStatus('saving')
    setTimeout(() => {
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)
    }, 1000)
  }

  return (
    <div className="min-h-screen bg-[#F1F5F9]">
      {/* Sidebar */}
      <aside className={cn(
        "fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 z-40",
        sidebarOpen ? "w-64" : "w-20"
      )}>
        <div className="flex flex-col h-full">
          <div className="h-16 flex items-center justify-between px-6 border-b border-gray-200">
            {sidebarOpen && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="font-bold text-lg gradient-text">AI Ticket</span>
              </div>
            )}
          </div>

          <nav className="flex-1 px-3 py-6 space-y-1">
            <NavItem href="/" icon={BarChart3} label="Dashboard" sidebarOpen={sidebarOpen} />
            <NavItem href="/tickets" icon={FileText} label="Tickets" sidebarOpen={sidebarOpen} />
            <NavItem href="/analytics" icon={TrendingUp} label="Analytics" sidebarOpen={sidebarOpen} />
            <NavItem href="/compliance" icon={Shield} label="Compliance" sidebarOpen={sidebarOpen} />
            <NavItem href="/settings" icon={SettingsIcon} label="Settings" active sidebarOpen={sidebarOpen} />
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className={cn("transition-all duration-300", sidebarOpen ? "ml-64" : "ml-20")}>
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 sticky top-0 z-30">
          <div className="h-full px-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-gray-100 rounded-lg">
                <Menu className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-bold text-gray-900">Settings</h1>
            </div>

            <button
              onClick={handleSave}
              disabled={saveStatus === 'saving'}
              className={cn(
                "px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors",
                saveStatus === 'saved'
                  ? "bg-green-600 text-white"
                  : "bg-blue-600 text-white hover:bg-blue-700"
              )}
            >
              {saveStatus === 'saving' && <RefreshCw className="w-4 h-4 animate-spin" />}
              {saveStatus === 'saved' && <CheckCircle2 className="w-4 h-4" />}
              {saveStatus === 'idle' && <Save className="w-4 h-4" />}
              {saveStatus === 'saving' && 'Saving...'}
              {saveStatus === 'saved' && 'Saved!'}
              {saveStatus === 'idle' && 'Save Changes'}
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="p-6 max-w-4xl space-y-6">
          {/* API Configuration */}
          <SettingsSection
            title="API Configuration"
            subtitle="Configure connection to the FastAPI backend server"
            icon={Database}
          >
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Server URL
                </label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="http://localhost:8000"
                />
                <p className="mt-1 text-sm text-gray-500">
                  The base URL of your FastAPI backend server
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  WebSocket URL
                </label>
                <input
                  type="text"
                  value={wsUrl}
                  onChange={(e) => setWsUrl(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ws://localhost:8000"
                />
                <p className="mt-1 text-sm text-gray-500">
                  WebSocket URL for real-time updates
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key (Optional)
                </label>
                <div className="relative">
                  <input
                    type={showApiKey ? "text" : "password"}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="w-full px-4 py-2 pr-12 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
                  />
                  <button
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <p className="mt-1 text-sm text-gray-500">
                  Leave empty if authentication is not required
                </p>
              </div>
            </div>
          </SettingsSection>

          {/* Dashboard Preferences */}
          <SettingsSection
            title="Dashboard Preferences"
            subtitle="Customize how the dashboard behaves"
            icon={Zap}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Auto Refresh
                  </label>
                  <p className="text-sm text-gray-500">
                    Automatically refresh data at intervals
                  </p>
                </div>
                <button
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className={cn(
                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                    autoRefresh ? "bg-blue-600" : "bg-gray-200"
                  )}
                >
                  <span
                    className={cn(
                      "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                      autoRefresh ? "translate-x-6" : "translate-x-1"
                    )}
                  />
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Refresh Interval (ms)
                </label>
                <select
                  value={refreshInterval}
                  onChange={(e) => setRefreshInterval(e.target.value)}
                  disabled={!autoRefresh}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <option value="10000">10 seconds</option>
                  <option value="30000">30 seconds</option>
                  <option value="60000">1 minute</option>
                  <option value="300000">5 minutes</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    Enable WebSocket
                  </label>
                  <p className="text-sm text-gray-500">
                    Use WebSocket for real-time updates
                  </p>
                </div>
                <button
                  onClick={() => setEnableWebSocket(!enableWebSocket)}
                  className={cn(
                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                    enableWebSocket ? "bg-blue-600" : "bg-gray-200"
                  )}
                >
                  <span
                    className={cn(
                      "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                      enableWebSocket ? "translate-x-6" : "translate-x-1"
                    )}
                  />
                </button>
              </div>
            </div>
          </SettingsSection>

          {/* Regional Settings */}
          <SettingsSection
            title="Regional Settings"
            subtitle="Configure regional and compliance preferences"
            icon={Globe}
          >
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default Region
                </label>
                <select className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="ALL">All Regions</option>
                  <option value="US">United States</option>
                  <option value="EU">European Union</option>
                  <option value="UK">United Kingdom</option>
                  <option value="CA">Canada</option>
                  <option value="AUS">Australia</option>
                  <option value="INDIA">India</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Compliance Framework
                </label>
                <select className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option value="auto">Auto-detect</option>
                  <option value="GDPR">GDPR (EU)</option>
                  <option value="CCPA">CCPA (California)</option>
                  <option value="PIPEDA">PIPEDA (Canada)</option>
                  <option value="DPDPA">DPDPA (India)</option>
                </select>
              </div>
            </div>
          </SettingsSection>

          {/* Notifications */}
          <SettingsSection
            title="Notifications"
            subtitle="Manage alerts and notifications"
            icon={Bell}
          >
            <div className="space-y-4">
              <NotificationToggle
                title="Compliance Alerts"
                description="Get notified about compliance issues"
                enabled={true}
              />
              <NotificationToggle
                title="PII Detection"
                description="Alert when sensitive data is detected"
                enabled={true}
              />
              <NotificationToggle
                title="Processing Errors"
                description="Notify on ticket processing failures"
                enabled={true}
              />
              <NotificationToggle
                title="Daily Reports"
                description="Receive daily processing summaries"
                enabled={false}
              />
            </div>
          </SettingsSection>

          {/* Security */}
          <SettingsSection
            title="Security"
            subtitle="Security and privacy settings"
            icon={Lock}
          >
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900">Data Encryption</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      All data is encrypted in transit using TLS 1.3 and at rest using AES-256
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-green-900">PII Protection</h4>
                    <p className="text-sm text-green-700 mt-1">
                      16+ PII patterns detected and redacted before processing
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <Lock className="w-5 h-5 text-purple-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-purple-900">Access Control</h4>
                    <p className="text-sm text-purple-700 mt-1">
                      Role-based access control (RBAC) enabled for all endpoints
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </SettingsSection>

          {/* About */}
          <SettingsSection
            title="About"
            subtitle="Application information and version"
            icon={Brain}
          >
            <div className="space-y-3">
              <div className="flex justify-between py-2">
                <span className="text-sm text-gray-600">Version</span>
                <span className="text-sm font-medium text-gray-900">2.4.0</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-sm text-gray-600">API Version</span>
                <span className="text-sm font-medium text-gray-900">1.0.0</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-sm text-gray-600">Dashboard</span>
                <span className="text-sm font-medium text-gray-900">Next.js 14.2.33</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-sm text-gray-600">Last Updated</span>
                <span className="text-sm font-medium text-gray-900">2025-11-11</span>
              </div>
            </div>
          </SettingsSection>
        </div>
      </div>
    </div>
  )
}

function SettingsSection({ title, subtitle, icon: Icon, children }: any) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <div className="flex items-start gap-4 mb-6">
        <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
          <Icon className="w-5 h-5 text-blue-600" />
        </div>
        <div className="flex-1">
          <h2 className="text-lg font-bold text-gray-900">{title}</h2>
          <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
        </div>
      </div>
      {children}
    </div>
  )
}

function NotificationToggle({ title, description, enabled }: any) {
  const [isEnabled, setIsEnabled] = useState(enabled)

  return (
    <div className="flex items-center justify-between py-3">
      <div>
        <h4 className="text-sm font-medium text-gray-900">{title}</h4>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
      <button
        onClick={() => setIsEnabled(!isEnabled)}
        className={cn(
          "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
          isEnabled ? "bg-blue-600" : "bg-gray-200"
        )}
      >
        <span
          className={cn(
            "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
            isEnabled ? "translate-x-6" : "translate-x-1"
          )}
        />
      </button>
    </div>
  )
}

function NavItem({ href, icon: Icon, label, active, sidebarOpen }: any) {
  return (
    <Link href={href} className={cn(
      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200",
      active ? "bg-blue-50 text-blue-600 font-medium" : "text-gray-700 hover:bg-gray-50"
    )}>
      <Icon className="w-5 h-5 flex-shrink-0" />
      {sidebarOpen && <span className="truncate">{label}</span>}
    </Link>
  )
}
