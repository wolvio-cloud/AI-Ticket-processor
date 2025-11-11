/**
 * ================================================================================
 * AI Ticket Processor - Main Dashboard Page
 * ================================================================================
 *
 * World-class SaaS dashboard showcasing:
 * - Real-time KPIs with trend indicators
 * - Interactive analytics charts
 * - Multi-region compliance tracking
 * - PII protection monitoring
 * - Live activity feed
 * - Customizable quick stats
 *
 * Design inspired by: Notion, Linear, Webflow, Zoho, Holded
 */

'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  BarChart3, TrendingUp, Clock, DollarSign, Shield, Zap,
  Globe, Activity, CheckCircle2, AlertCircle, Users,
  FileText, Brain, Target, Sparkles, Bell, Settings,
  ChevronDown, Search, Menu, X, Loader2, Wifi, WifiOff, RefreshCw
} from 'lucide-react'
import {
  todayStats, roiMetrics, industryDistribution, sentimentData,
  type Region
} from '@/lib/mock-data'
import { cn, formatNumber, formatCurrency, formatPercentage } from '@/lib/utils'
import { useDashboardData, useConnectionStatus } from '@/lib/use-dashboard-data'

export default function DashboardPage() {
  const [selectedRegion, setSelectedRegion] = useState<Region | 'ALL'>('ALL')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showOnboarding, setShowOnboarding] = useState(true)

  // Fetch real-time data from API
  const { data, loading, error, isLive, lastUpdate, apiAvailable, refresh } = useDashboardData()
  const connectionStatus = useConnectionStatus()

  // Extract data for easier access
  const dashboardMetrics = data.metrics
  const regionData = data.regions
  const categoryData = data.categories
  const trendData = data.trends
  const piiBreakdown = data.pii
  const complianceData = data.compliance
  const recentActivity = data.activity
  const testSuiteHealth = data.tests

  return (
    <div className="min-h-screen bg-[#F1F5F9]">
      {/* Sidebar */}
      <aside className={cn(
        "fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 z-40",
        sidebarOpen ? "w-64" : "w-20"
      )}>
        <div className="flex flex-col h-full">
          {/* Logo & Brand */}
          <div className="h-16 flex items-center justify-between px-6 border-b border-gray-200">
            {sidebarOpen && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="font-bold text-lg gradient-text">AI Ticket</span>
              </div>
            )}
            {!sidebarOpen && (
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center mx-auto">
                <Brain className="w-5 h-5 text-white" />
              </div>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-6 space-y-1">
            <NavItem href="/" icon={BarChart3} label="Dashboard" active sidebarOpen={sidebarOpen} />
            <NavItem href="/tickets" icon={FileText} label="Tickets" sidebarOpen={sidebarOpen} />
            <NavItem href="/analytics" icon={TrendingUp} label="Analytics" sidebarOpen={sidebarOpen} />
            <NavItem href="/compliance" icon={Shield} label="Compliance" sidebarOpen={sidebarOpen} />
            <NavItem href="/settings" icon={Settings} label="Settings" sidebarOpen={sidebarOpen} />
          </nav>

          {/* User Profile */}
          <div className="p-4 border-t border-gray-200">
            {sidebarOpen ? (
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                  SM
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold truncate">Support Manager</p>
                  <p className="text-xs text-gray-500 truncate">manager@company.com</p>
                </div>
              </div>
            ) : (
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold mx-auto">
                SM
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className={cn(
        "transition-all duration-300",
        sidebarOpen ? "ml-64" : "ml-20"
      )}>
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-gray-200 sticky top-0 z-30">
          <div className="h-full px-6 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>

              {/* Search */}
              <div className="relative hidden md:block">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search tickets, categories..."
                  className="pl-10 pr-4 py-2 w-80 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Connection Status & Refresh */}
              <div className="flex items-center gap-2 mr-2">
                <button
                  onClick={refresh}
                  disabled={loading}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Refresh data"
                >
                  <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
                </button>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg text-xs">
                  {isLive ? (
                    <>
                      <Wifi className="w-3.5 h-3.5 text-green-600" />
                      <span className="text-green-600 font-medium">Live</span>
                    </>
                  ) : apiAvailable ? (
                    <>
                      <Wifi className="w-3.5 h-3.5 text-blue-600" />
                      <span className="text-blue-600 font-medium">API</span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="w-3.5 h-3.5 text-gray-400" />
                      <span className="text-gray-500 font-medium">Mock</span>
                    </>
                  )}
                </div>
              </div>

              {/* Region Selector */}
              <RegionSelector selected={selectedRegion} onSelect={setSelectedRegion} />

              {/* Notifications */}
              <button className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>

              {/* Avatar */}
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-sm font-semibold">
                SM
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="p-6 space-y-6">
          {/* Loading Overlay */}
          {loading && !data.metrics && (
            <div className="bg-white rounded-2xl p-12 text-center animate-pulse">
              <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
              <p className="text-gray-600 font-medium">Loading dashboard data...</p>
              <p className="text-sm text-gray-400 mt-2">Connecting to API server</p>
            </div>
          )}

          {/* Error Banner */}
          {error && !loading && (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-6 flex items-start gap-4">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-red-900 mb-1">Connection Error</h3>
                <p className="text-sm text-red-700">
                  Unable to fetch data from API server. Using mock data instead.
                  Make sure the API server is running on <code className="px-2 py-0.5 bg-red-100 rounded">http://localhost:8000</code>
                </p>
              </div>
              <button
                onClick={refresh}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
              >
                Retry
              </button>
            </div>
          )}

          {/* API Status Banner */}
          {!loading && !apiAvailable && !error && (
            <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm text-amber-800">
                  <strong>Offline Mode:</strong> Displaying mock data. Start the API server to see real-time results.
                </p>
              </div>
            </div>
          )}

          {/* Onboarding Card */}
          {showOnboarding && (
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white relative overflow-hidden animate-slide-in">
              <button
                onClick={() => setShowOnboarding(false)}
                className="absolute top-4 right-4 p-1 hover:bg-white/20 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-2">Welcome to AI Ticket Processor! 🎉</h3>
                  <p className="text-blue-100 mb-4">
                    Your intelligent support automation platform is saving teams <strong>{formatNumber(dashboardMetrics.agentTimeSaved)}</strong> hours and
                    <strong> {formatCurrency(dashboardMetrics.costSavings)}</strong> monthly. Let's get you started!
                  </p>
                  <div className="flex gap-3">
                    <button className="px-4 py-2 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
                      Take Tour
                    </button>
                    <button className="px-4 py-2 bg-white/20 rounded-lg font-semibold hover:bg-white/30 transition-colors">
                      View Documentation
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* KPI Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <KPICard
              title="Tickets Processed"
              value={formatNumber(dashboardMetrics.ticketsProcessed)}
              change={12.3}
              icon={FileText}
              color="blue"
              trend="up"
            />
            <KPICard
              title="Accuracy Rate"
              value={formatPercentage(dashboardMetrics.accuracyRate)}
              change={2.4}
              icon={Target}
              color="green"
              trend="up"
            />
            <KPICard
              title="Agent Time Saved"
              value={`${formatNumber(dashboardMetrics.agentTimeSaved)}h`}
              change={15.7}
              icon={Clock}
              color="purple"
              trend="up"
            />
            <KPICard
              title="Cost Savings"
              value={formatCurrency(dashboardMetrics.costSavings)}
              change={8.2}
              icon={DollarSign}
              color="orange"
              trend="up"
            />
          </div>

          {/* Charts & Analytics Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Trend Chart - Takes 2 columns */}
            <div className="lg:col-span-2">
              <ChartCard title="30-Day Trend Analysis" subtitle="Tickets, Accuracy & PII Detection">
                <div className="h-80 flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Interactive Chart Component</p>
                    <p className="text-xs">(Install Recharts and implement)</p>
                  </div>
                </div>
              </ChartCard>
            </div>

            {/* Quick Stats */}
            <div className="space-y-6">
              <StatCard
                label="Today's Tickets"
                value={todayStats.ticketsToday}
                icon={Activity}
                color="blue"
              />
              <StatCard
                label="Drafts Generated"
                value={todayStats.draftsGenerated}
                icon={FileText}
                color="purple"
              />
              <StatCard
                label="PII Protected"
                value={todayStats.piiProtected}
                icon={Shield}
                color="green"
              />
              <StatCard
                label="API Health"
                value={`${todayStats.apiHealth}%`}
                icon={Zap}
                color="orange"
              />
            </div>
          </div>

          {/* Category Distribution & Regional Performance */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Category Distribution */}
            <ChartCard title="Category Distribution" subtitle="Top 10 Classifications (v2.4)">
              <div className="space-y-3">
                {categoryData && categoryData.length > 0 ? (
                  categoryData.slice(0, 10).map((category, index) => (
                    <CategoryBar
                      key={category.name}
                      category={category}
                      index={index}
                      allCategories={categoryData}
                    />
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No category data available
                  </div>
                )}
              </div>
            </ChartCard>

            {/* Regional Performance */}
            <ChartCard title="Regional Performance" subtitle="Tickets & Accuracy by Region">
              <div className="space-y-3">
                {regionData && regionData.length > 0 ? (
                  regionData.map((region) => (
                    <RegionBar key={region.region} data={region} />
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No regional data available
                  </div>
                )}
              </div>
            </ChartCard>
          </div>

          {/* Compliance & Activity Feed */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Compliance Status - 2 columns */}
            <div className="lg:col-span-2">
              <ChartCard title="Compliance Status" subtitle="Global Data Protection Frameworks">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {complianceData && Object.keys(complianceData).length > 0 ? (
                    Object.entries(complianceData).map(([region, data]) => (
                      <ComplianceCard key={region} region={region as Region} data={data} />
                    ))
                  ) : (
                    <div className="col-span-full text-center py-8 text-gray-500">
                      No compliance data available
                    </div>
                  )}
                </div>
              </ChartCard>
            </div>

            {/* Activity Feed */}
            <ChartCard title="Recent Activity" subtitle="Live Updates">
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {recentActivity && recentActivity.length > 0 ? (
                  recentActivity.map((activity) => (
                    <ActivityItem key={activity.id} activity={activity} />
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No recent activity
                  </div>
                )}
              </div>
            </ChartCard>
          </div>

          {/* Test Suite Health */}
          <ChartCard title="System Health & Test Suite" subtitle="Real-time Quality Metrics">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <TestResult name="Syntax" status={testSuiteHealth.syntaxCheck.status} time={testSuiteHealth.syntaxCheck.time} />
              <TestResult name="Classification" status={testSuiteHealth.classificationAccuracy.status} detail={testSuiteHealth.classificationAccuracy.accuracy} />
              <TestResult name="PII Redaction" status={testSuiteHealth.piiRedaction.status} detail={`${testSuiteHealth.piiRedaction.patterns} patterns`} />
              <TestResult name="Enhanced v2.4" status={testSuiteHealth.enhancedClassification.status} detail={testSuiteHealth.enhancedClassification.tests} />
              <TestResult name="Integration" status={testSuiteHealth.integration.status} detail={testSuiteHealth.integration.tests} />
            </div>
          </ChartCard>
        </main>
      </div>
    </div>
  )
}

// ============================================================================
// Component Library
// ============================================================================

interface NavItemProps {
  href: string
  icon: any
  label: string
  active?: boolean
  sidebarOpen: boolean
}

function NavItem({ href, icon: Icon, label, active, sidebarOpen }: NavItemProps) {
  return (
    <Link href={href} className={cn(
      "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200",
      active
        ? "bg-blue-50 text-blue-600 font-medium"
        : "text-gray-700 hover:bg-gray-50"
    )}>
      <Icon className="w-5 h-5 flex-shrink-0" />
      {sidebarOpen && <span className="truncate">{label}</span>}
    </Link>
  )
}

interface RegionSelectorProps {
  selected: Region | 'ALL'
  onSelect: (region: Region | 'ALL') => void
}

function RegionSelector({ selected, onSelect }: RegionSelectorProps) {
  return (
    <div className="relative">
      <button className="flex items-center gap-2 px-3 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
        <Globe className="w-4 h-4" />
        <span className="text-sm font-medium">{selected}</span>
        <ChevronDown className="w-4 h-4" />
      </button>
    </div>
  )
}

interface KPICardProps {
  title: string
  value: string
  change: number
  icon: any
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red'
  trend: 'up' | 'down'
}

function KPICard({ title, value, change, icon: Icon, color, trend }: KPICardProps) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
    red: 'from-red-500 to-red-600',
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200 card-hover">
      <div className="flex items-start justify-between mb-4">
        <div className={cn(
          "w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center",
          colorClasses[color]
        )}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div className={cn(
          "flex items-center gap-1 text-sm font-semibold px-2 py-1 rounded-full",
          trend === 'up' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
        )}>
          <TrendingUp className={cn("w-4 h-4", trend === 'down' && 'rotate-180')} />
          {change}%
        </div>
      </div>
      <div>
        <p className="text-gray-600 text-sm mb-1">{title}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  )
}

interface StatCardProps {
  label: string
  value: number | string
  icon: any
  color: 'blue' | 'green' | 'purple' | 'orange'
}

function StatCard({ label, value, icon: Icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  }

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm mb-1">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", colorClasses[color])}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  )
}

interface ChartCardProps {
  title: string
  subtitle?: string
  children: React.ReactNode
}

function ChartCard({ title, subtitle, children }: ChartCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900">{title}</h3>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}

interface CategoryBarProps {
  category: any
  index: number
  allCategories: any[]
}

function CategoryBar({ category, index, allCategories }: CategoryBarProps) {
  const maxValue = allCategories && allCategories.length > 0
    ? Math.max(...allCategories.map(c => c.value))
    : category.value
  const percentage = maxValue > 0 ? (category.value / maxValue) * 100 : 0

  return (
    <div className="group cursor-pointer">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: category.color }} />
          <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
            {category.name}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-900">{formatNumber(category.value)}</span>
          <span className={cn(
            "text-xs font-medium",
            category.change > 0 ? "text-green-600" : "text-red-600"
          )}>
            {category.change > 0 ? '+'  : ''}{category.change}%
          </span>
        </div>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 group-hover:opacity-80"
          style={{
            width: `${percentage}%`,
            backgroundColor: category.color
          }}
        />
      </div>
    </div>
  )
}

interface RegionBarProps {
  data: typeof regionData[0]
}

function RegionBar({ data }: RegionBarProps) {
  const statusColors = {
    compliant: 'bg-green-500',
    pending: 'bg-yellow-500',
    'at-risk': 'bg-red-500'
  }

  return (
    <div className="group cursor-pointer">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
            {data.region}
          </span>
          <div className={cn("w-2 h-2 rounded-full", statusColors[data.compliance])} />
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">{formatNumber(data.tickets)} tickets</span>
          <span className="text-sm font-semibold text-gray-900">{formatPercentage(data.accuracy)}</span>
        </div>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500"
          style={{ width: `${data.accuracy}%` }}
        />
      </div>
    </div>
  )
}

interface ComplianceCardProps {
  region: Region
  data: typeof complianceData.US
}

function ComplianceCard({ region, data }: ComplianceCardProps) {
  const statusConfig = {
    compliant: { color: 'bg-green-500', icon: CheckCircle2, text: 'Compliant' },
    pending: { color: 'bg-yellow-500', icon: AlertCircle, text: 'Pending' },
    'at-risk': { color: 'bg-red-500', icon: AlertCircle, text: 'At Risk' }
  }

  const config = statusConfig[data.status as keyof typeof statusConfig]
  const Icon = config.icon

  return (
    <div className="bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors cursor-pointer">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-bold text-gray-900">{region}</span>
        <div className={cn("w-2 h-2 rounded-full", config.color)} />
      </div>
      <div className="space-y-2">
        <div>
          <p className="text-xs text-gray-500">Framework</p>
          <p className="text-sm font-semibold text-gray-900">{data.framework}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Coverage</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div className={cn("h-full rounded-full", config.color)} style={{ width: `${data.coverage}%` }} />
            </div>
            <span className="text-xs font-semibold">{data.coverage}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}

interface ActivityItemProps {
  activity: typeof recentActivity[0]
}

function ActivityItem({ activity }: ActivityItemProps) {
  const typeConfig = {
    ticket_processed: { icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-50' },
    batch_complete: { icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-50' },
    compliance_alert: { icon: Shield, color: 'text-blue-600', bg: 'bg-blue-50' },
    milestone: { icon: Sparkles, color: 'text-purple-600', bg: 'bg-purple-50' },
    pii_detection: { icon: Shield, color: 'text-orange-600', bg: 'bg-orange-50' },
    system_update: { icon: Zap, color: 'text-gray-600', bg: 'bg-gray-50' }
  }

  // Get config with fallback for unknown types
  const config = typeConfig[activity.type as keyof typeof typeConfig] || {
    icon: Activity,
    color: 'text-gray-600',
    bg: 'bg-gray-50'
  }
  const Icon = config.icon

  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
      <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0", config.bg)}>
        <Icon className={cn("w-4 h-4", config.color)} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900 font-medium">{activity.message}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-gray-500">{activity.time}</span>
          <span className="text-xs text-gray-400">•</span>
          <span className="text-xs text-gray-500">{activity.region}</span>
        </div>
      </div>
    </div>
  )
}

interface TestResultProps {
  name: string
  status: string
  time?: string
  detail?: string
}

function TestResult({ name, status, time, detail }: TestResultProps) {
  return (
    <div className="bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <CheckCircle2 className="w-5 h-5 text-green-600" />
        <span className="text-xs font-semibold text-green-600 uppercase">{status}</span>
      </div>
      <p className="text-sm font-semibold text-gray-900 mb-1">{name}</p>
      {detail && <p className="text-xs text-gray-600">{detail}</p>}
      {time && <p className="text-xs text-gray-500 mt-1">{time}</p>}
    </div>
  )
}
