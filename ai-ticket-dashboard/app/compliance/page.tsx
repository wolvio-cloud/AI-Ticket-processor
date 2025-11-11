'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  Shield, Brain, Menu, FileText, TrendingUp, User, CheckCircle2,
  AlertCircle, Clock, Lock, Eye, FileCheck, Download, Calendar,
  Globe, AlertTriangle, BarChart3
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDashboardData } from '@/lib/use-dashboard-data'

export default function CompliancePage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [selectedRegion, setSelectedRegion] = useState<string>('all')

  const { data, loading, isLive, apiAvailable } = useDashboardData()

  const complianceRegions = [
    {
      region: 'US',
      framework: 'CCPA',
      status: 'compliant',
      lastAudit: '2025-01-15',
      coverage: 100,
      requirements: ['Data encryption', 'User consent', 'Right to deletion', 'Data portability'],
      piiDetected: 145,
      piiRedacted: 145,
      violations: 0
    },
    {
      region: 'EU',
      framework: 'GDPR',
      status: 'compliant',
      lastAudit: '2025-01-20',
      coverage: 100,
      requirements: ['Data minimization', 'Purpose limitation', 'Storage limitation', 'Consent management'],
      piiDetected: 89,
      piiRedacted: 89,
      violations: 0
    },
    {
      region: 'UK',
      framework: 'UK GDPR',
      status: 'compliant',
      lastAudit: '2025-01-18',
      coverage: 100,
      requirements: ['Lawful processing', 'Data protection by design', 'Breach notification', 'DPO appointment'],
      piiDetected: 56,
      piiRedacted: 56,
      violations: 0
    },
    {
      region: 'CA',
      framework: 'PIPEDA',
      status: 'compliant',
      lastAudit: '2025-01-22',
      coverage: 100,
      requirements: ['Consent for collection', 'Accuracy', 'Safeguards', 'Openness'],
      piiDetected: 34,
      piiRedacted: 34,
      violations: 0
    },
    {
      region: 'AUS',
      framework: 'Privacy Act',
      status: 'pending',
      lastAudit: '2024-12-10',
      coverage: 95,
      requirements: ['APP compliance', 'Cross-border disclosure', 'Data security', 'Breach notification'],
      piiDetected: 28,
      piiRedacted: 27,
      violations: 1
    },
    {
      region: 'INDIA',
      framework: 'DPDPA',
      status: 'compliant',
      lastAudit: '2025-01-25',
      coverage: 100,
      requirements: ['Purpose limitation', 'Data minimization', 'Storage limitation', 'Security safeguards'],
      piiDetected: 42,
      piiRedacted: 42,
      violations: 0
    }
  ]

  const piiTypes = [
    { type: 'Credit Card Numbers', detected: 45, redacted: 45, pattern: /\d{4}-\d{4}-\d{4}-\d{4}/, severity: 'high' },
    { type: 'Social Security Numbers', detected: 32, redacted: 32, pattern: /\d{3}-\d{2}-\d{4}/, severity: 'high' },
    { type: 'Email Addresses', detected: 234, redacted: 0, pattern: /[a-z0-9]+@[a-z]+\.[a-z]+/, severity: 'low' },
    { type: 'Phone Numbers', detected: 89, redacted: 89, pattern: /\(\d{3}\) \d{3}-\d{4}/, severity: 'medium' },
    { type: 'IP Addresses', detected: 156, redacted: 156, pattern: /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/, severity: 'medium' },
    { type: 'Passport Numbers', detected: 12, redacted: 12, pattern: /[A-Z]\d{7}/, severity: 'high' },
    { type: 'Driver License', detected: 18, redacted: 18, pattern: /DL-\d{8}/, severity: 'high' },
    { type: 'Addresses', detected: 67, redacted: 67, pattern: /\d+\s+\w+\s+\w+/, severity: 'medium' }
  ]

  const filteredRegions = selectedRegion === 'all'
    ? complianceRegions
    : complianceRegions.filter(r => r.region === selectedRegion)

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
            <NavItem href="/compliance" icon={Shield} label="Compliance" active sidebarOpen={sidebarOpen} />
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
              <h1 className="text-xl font-bold text-gray-900">Compliance & Privacy</h1>
            </div>

            <div className="flex items-center gap-3">
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Regions</option>
                {complianceRegions.map(r => (
                  <option key={r.region} value={r.region}>{r.region} - {r.framework}</option>
                ))}
              </select>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export Report
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <ComplianceMetric
              title="Compliant Regions"
              value="5/6"
              subtitle="83% coverage"
              icon={CheckCircle2}
              color="green"
            />
            <ComplianceMetric
              title="PII Protected"
              value="394/395"
              subtitle="99.7% redacted"
              icon={Shield}
              color="blue"
            />
            <ComplianceMetric
              title="Violations"
              value="1"
              subtitle="Low severity"
              icon={AlertTriangle}
              color="yellow"
            />
            <ComplianceMetric
              title="Last Audit"
              value="2 days ago"
              subtitle="Next: 30 days"
              icon={Calendar}
              color="purple"
            />
          </div>

          {/* Regional Compliance */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-6">Regional Compliance Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredRegions.map((region, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{region.region}</h3>
                      <p className="text-sm text-gray-600">{region.framework}</p>
                    </div>
                    {region.status === 'compliant' ? (
                      <div className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                        <CheckCircle2 className="w-3 h-3" />
                        Compliant
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">
                        <Clock className="w-3 h-3" />
                        Pending
                      </div>
                    )}
                  </div>

                  <div className="space-y-3 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Coverage</span>
                      <span className="font-semibold text-gray-900">{region.coverage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={cn("h-2 rounded-full",
                          region.coverage === 100 ? "bg-green-500" : "bg-yellow-500"
                        )}
                        style={{ width: `${region.coverage}%` }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="text-center p-2 bg-blue-50 rounded-lg">
                      <div className="text-lg font-bold text-blue-600">{region.piiDetected}</div>
                      <div className="text-xs text-gray-600">PII Detected</div>
                    </div>
                    <div className="text-center p-2 bg-green-50 rounded-lg">
                      <div className="text-lg font-bold text-green-600">{region.piiRedacted}</div>
                      <div className="text-xs text-gray-600">PII Redacted</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-xs font-semibold text-gray-700 uppercase">Key Requirements</div>
                    {region.requirements.slice(0, 3).map((req, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm text-gray-600">
                        <CheckCircle2 className="w-3 h-3 text-green-500 flex-shrink-0" />
                        <span className="truncate">{req}</span>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between text-xs text-gray-500">
                    <span>Last audit: {new Date(region.lastAudit).toLocaleDateString()}</span>
                    {region.violations > 0 && (
                      <span className="text-yellow-600 font-medium">{region.violations} violation(s)</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* PII Detection Breakdown */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-6">PII Detection & Redaction</h2>
            <div className="space-y-4">
              {piiTypes.map((pii, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center",
                        pii.severity === 'high' ? 'bg-red-50' :
                        pii.severity === 'medium' ? 'bg-yellow-50' : 'bg-blue-50'
                      )}>
                        <Shield className={cn("w-5 h-5",
                          pii.severity === 'high' ? 'text-red-600' :
                          pii.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                        )} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{pii.type}</h4>
                        <p className="text-xs text-gray-500">Pattern: {pii.pattern.toString()}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">{pii.detected}</div>
                        <div className="text-xs text-gray-500">Detected</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-green-600">{pii.redacted}</div>
                        <div className="text-xs text-gray-500">Redacted</div>
                      </div>
                      <div className={cn("px-3 py-1 rounded-full text-xs font-medium",
                        pii.severity === 'high' ? 'bg-red-100 text-red-700' :
                        pii.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700'
                      )}>
                        {pii.severity.toUpperCase()}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={cn("h-2 rounded-full",
                          (pii.redacted / pii.detected) === 1 ? 'bg-green-500' : 'bg-yellow-500'
                        )}
                        style={{ width: `${(pii.redacted / pii.detected) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600 w-12">
                      {((pii.redacted / pii.detected) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Compliance Timeline */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-6">Audit Timeline</h2>
            <div className="space-y-4">
              {[
                { date: '2025-01-25', event: 'INDIA DPDPA Audit Completed', status: 'success', details: 'Full compliance verified' },
                { date: '2025-01-22', event: 'CA PIPEDA Audit Completed', status: 'success', details: 'All requirements met' },
                { date: '2025-01-20', event: 'EU GDPR Audit Completed', status: 'success', details: 'No violations found' },
                { date: '2025-01-18', event: 'UK GDPR Audit Completed', status: 'success', details: 'Compliant with all provisions' },
                { date: '2025-01-15', event: 'US CCPA Audit Completed', status: 'success', details: 'Privacy controls validated' },
                { date: '2024-12-10', event: 'AUS Privacy Act Audit', status: 'warning', details: '1 minor violation identified' }
              ].map((item, idx) => (
                <div key={idx} className="flex items-start gap-4 pb-4 border-b border-gray-100 last:border-0">
                  <div className={cn("w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                    item.status === 'success' ? 'bg-green-100' : 'bg-yellow-100'
                  )}>
                    {item.status === 'success' ? (
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-yellow-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-gray-900">{item.event}</h4>
                      <span className="text-sm text-gray-500">{new Date(item.date).toLocaleDateString()}</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{item.details}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ComplianceMetric({ title, value, subtitle, icon: Icon, color }: any) {
  const colorClasses = {
    green: 'bg-green-50 text-green-600',
    blue: 'bg-blue-50 text-blue-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600'
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-gray-600">{title}</span>
        <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", colorClasses[color as keyof typeof colorClasses])}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-sm text-gray-500">{subtitle}</div>
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
