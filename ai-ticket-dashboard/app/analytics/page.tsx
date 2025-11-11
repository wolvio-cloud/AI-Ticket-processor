'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  TrendingUp, Brain, Menu, FileText, Shield, User, Calendar,
  BarChart3, PieChart, Activity, Clock, DollarSign, Target,
  ArrowUp, ArrowDown, Minus
} from 'lucide-react'
import { cn, formatNumber, formatCurrency, formatPercentage } from '@/lib/utils'
import { useDashboardData } from '@/lib/use-dashboard-data'

export default function AnalyticsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')

  const { data, loading, isLive, apiAvailable } = useDashboardData()

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
            <NavItem href="/analytics" icon={TrendingUp} label="Analytics" active sidebarOpen={sidebarOpen} />
            <NavItem href="/compliance" icon={Shield} label="Compliance" sidebarOpen={sidebarOpen} />
            <NavItem href="/settings" icon={User} label="Settings" sidebarOpen={sidebarOpen} />
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
              <h1 className="text-xl font-bold text-gray-900">Analytics</h1>
            </div>

            <div className="flex items-center gap-2">
              {['7d', '30d', '90d'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range as any)}
                  className={cn(
                    "px-4 py-2 text-sm font-medium rounded-lg transition-colors",
                    timeRange === range
                      ? "bg-blue-600 text-white"
                      : "text-gray-600 hover:bg-gray-100"
                  )}
                >
                  {range === '7d' && 'Last 7 Days'}
                  {range === '30d' && 'Last 30 Days'}
                  {range === '90d' && 'Last 90 Days'}
                </button>
              ))}
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Key Metrics Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Tickets"
              value={formatNumber(data.metrics?.ticketsProcessed || 0)}
              change={12.5}
              trend="up"
              icon={FileText}
              color="blue"
            />
            <MetricCard
              title="Avg Confidence"
              value={formatPercentage(data.metrics?.accuracyRate || 0)}
              change={2.3}
              trend="up"
              icon={Target}
              color="green"
            />
            <MetricCard
              title="Processing Time"
              value="7.3s"
              change={-5.1}
              trend="down"
              icon={Clock}
              color="purple"
            />
            <MetricCard
              title="Cost Savings"
              value={formatCurrency(data.metrics?.costSavings || 0)}
              change={18.2}
              trend="up"
              icon={DollarSign}
              color="emerald"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Volume Trend */}
            <ChartCard title="Ticket Volume Trend" subtitle={`Last ${timeRange}`}>
              <div className="h-64 flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <Activity className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                  <p>Time series chart</p>
                  <p className="text-sm">Showing ticket volume over time</p>
                </div>
              </div>
            </ChartCard>

            {/* Accuracy Trend */}
            <ChartCard title="Classification Accuracy" subtitle={`Last ${timeRange}`}>
              <div className="h-64 flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <Target className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                  <p>Accuracy trend chart</p>
                  <p className="text-sm">Classification confidence over time</p>
                </div>
              </div>
            </ChartCard>
          </div>

          {/* Category Performance */}
          <ChartCard title="Category Performance" subtitle="Processing metrics by category">
            <div className="space-y-4">
              {data.categories && data.categories.length > 0 ? (
                data.categories.slice(0, 8).map((category: any, idx: number) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-gray-700">{category.name}</span>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>{category.value} tickets</span>
                        <span>95% accuracy</span>
                        <span>6.2s avg</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${(category.value / (data.categories[0]?.value || 1)) * 100}%` }}
                        />
                      </div>
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: '95%' }} />
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No category data available
                </div>
              )}
            </div>
          </ChartCard>

          {/* Industry Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartCard title="Industry Distribution" subtitle="Tickets by industry type">
              <div className="space-y-3">
                {[
                  { industry: 'SaaS', count: 16, percentage: 80, color: 'bg-blue-500' },
                  { industry: 'E-commerce', count: 2, percentage: 10, color: 'bg-purple-500' },
                  { industry: 'General', count: 2, percentage: 10, color: 'bg-gray-500' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div className="w-32 text-sm font-medium text-gray-700">{item.industry}</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-6">
                      <div className={cn("h-6 rounded-full flex items-center justify-end px-2 text-white text-xs font-medium", item.color)}
                        style={{ width: `${item.percentage}%` }}>
                        {item.percentage}%
                      </div>
                    </div>
                    <div className="w-16 text-sm text-gray-600 text-right">{item.count} tickets</div>
                  </div>
                ))}
              </div>
            </ChartCard>

            <ChartCard title="Performance Metrics" subtitle="Key performance indicators">
              <div className="space-y-4">
                <PerformanceMetric
                  label="Classification Accuracy"
                  value={85}
                  target={90}
                  unit="%"
                  status="warning"
                />
                <PerformanceMetric
                  label="PII Detection Rate"
                  value={100}
                  target={100}
                  unit="%"
                  status="success"
                />
                <PerformanceMetric
                  label="Avg Processing Time"
                  value={7.3}
                  target={5.0}
                  unit="s"
                  status="warning"
                />
                <PerformanceMetric
                  label="Draft Generation Rate"
                  value={95}
                  target={90}
                  unit="%"
                  status="success"
                />
              </div>
            </ChartCard>
          </div>

          {/* Regional Analysis */}
          <ChartCard title="Regional Analysis" subtitle="Performance by geographic region">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data.regions && data.regions.length > 0 ? (
                data.regions.map((region: any, idx: number) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold text-gray-900">{region.region}</h4>
                      <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                        {region.compliance}
                      </span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Tickets</span>
                        <span className="font-medium">{region.tickets}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Accuracy</span>
                        <span className="font-medium">{region.accuracy}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Growth</span>
                        <span className="font-medium text-green-600">+{region.growth}%</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-8 text-gray-500">
                  No regional data available
                </div>
              )}
            </div>
          </ChartCard>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, change, trend, icon: Icon, color }: any) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    emerald: 'bg-emerald-50 text-emerald-600'
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-gray-600">{title}</span>
        <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", colorClasses[color as keyof typeof colorClasses])}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="space-y-2">
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="flex items-center gap-1">
          {trend === 'up' ? (
            <ArrowUp className="w-4 h-4 text-green-600" />
          ) : trend === 'down' ? (
            <ArrowDown className="w-4 h-4 text-red-600" />
          ) : (
            <Minus className="w-4 h-4 text-gray-400" />
          )}
          <span className={cn("text-sm font-medium",
            trend === 'up' ? "text-green-600" : trend === 'down' ? "text-red-600" : "text-gray-400"
          )}>
            {Math.abs(change)}%
          </span>
          <span className="text-sm text-gray-500">vs last period</span>
        </div>
      </div>
    </div>
  )
}

function ChartCard({ title, subtitle, children }: any) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900">{title}</h3>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}

function PerformanceMetric({ label, value, target, unit, status }: any) {
  const percentage = (value / target) * 100
  const statusColors = {
    success: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600'
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className={cn("text-sm font-semibold", statusColors[status as keyof typeof statusColors])}>
          {value}{unit}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-gray-200 rounded-full h-2">
          <div
            className={cn("h-2 rounded-full",
              status === 'success' ? 'bg-green-500' :
              status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
            )}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
        <span className="text-xs text-gray-500 w-12">Target: {target}{unit}</span>
      </div>
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
