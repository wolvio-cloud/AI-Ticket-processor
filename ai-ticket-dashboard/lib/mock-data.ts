/**
 * ================================================================================
 * Mock Data - Realistic Sample Data for AI Ticket Processor Dashboard
 * ================================================================================
 *
 * Comprehensive mock data for demonstrating all dashboard features:
 * - Multi-region ticket data (US, EU, UK, CA, AUS, India)
 * - PII detection patterns
 * - Compliance statuses
 * - Analytics and trends
 * - Real-time metrics
 */

export type Region = 'US' | 'EU' | 'UK' | 'CA' | 'AUS' | 'INDIA'
export type ComplianceStatus = 'compliant' | 'pending' | 'at-risk'
export type Industry = 'SaaS' | 'E-commerce' | 'General'

export interface DashboardMetrics {
  ticketsProcessed: number
  accuracyRate: number
  agentTimeSaved: number
  costSavings: number
  confidenceScore: number
  piiDetections: number
  draftsGenerated: number
  fallbackRate: number
}

export interface RegionData {
  region: Region
  tickets: number
  accuracy: number
  compliance: ComplianceStatus
  growth: number
}

export interface CategoryData {
  name: string
  value: number
  color: string
  change: number
}

export interface TrendDataPoint {
  date: string
  tickets: number
  accuracy: number
  piiDetected: number
}

export interface PIIBreakdown {
  type: string
  count: number
  region: Region[]
  severity: 'high' | 'medium' | 'low'
}

// Global dashboard metrics
export const dashboardMetrics: DashboardMetrics = {
  ticketsProcessed: 12847,
  accuracyRate: 94.7,
  agentTimeSaved: 2847,
  costSavings: 42750,
  confidenceScore: 87.3,
  piiDetections: 1243,
  draftsGenerated: 11420,
  fallbackRate: 5.2,
}

// Region-specific data
export const regionData: RegionData[] = [
  { region: 'US', tickets: 4521, accuracy: 95.2, compliance: 'compliant', growth: 12.3 },
  { region: 'EU', tickets: 3102, accuracy: 94.8, compliance: 'compliant', growth: 8.7 },
  { region: 'UK', tickets: 2187, accuracy: 93.5, compliance: 'compliant', growth: 15.2 },
  { region: 'CA', tickets: 1432, accuracy: 96.1, compliance: 'compliant', growth: 10.5 },
  { region: 'AUS', tickets: 987, accuracy: 92.8, compliance: 'pending', growth: 7.3 },
  { region: 'INDIA', tickets: 618, accuracy: 91.2, compliance: 'compliant', growth: 22.1 },
]

// Category distribution (enhanced classification v2.4)
export const categoryData: CategoryData[] = [
  { name: 'Login/Auth', value: 2847, color: '#3b82f6', change: 5.2 },
  { name: 'Billing', value: 2103, color: '#8b5cf6', change: -2.1 },
  { name: 'API/Technical', value: 1876, color: '#ef4444', change: 8.7 },
  { name: 'Order Status', value: 1654, color: '#f59e0b', change: 12.3 },
  { name: 'Returns/Refunds', value: 1234, color: '#10b981', change: -4.5 },
  { name: 'Feature Requests', value: 987, color: '#6366f1', change: 15.6 },
  { name: 'Product Inquiry', value: 876, color: '#ec4899', change: 3.2 },
  { name: 'Payment Issues', value: 765, color: '#f97316', change: -1.8 },
  { name: 'Account Management', value: 543, color: '#14b8a6', change: 6.7 },
  { name: 'Other', value: 362, color: '#64748b', change: -18.3 },
]

// 30-day trend data
export const trendData: TrendDataPoint[] = Array.from({ length: 30 }, (_, i) => {
  const date = new Date()
  date.setDate(date.getDate() - (29 - i))
  return {
    date: date.toISOString().split('T')[0],
    tickets: Math.floor(Math.random() * 200 + 350),
    accuracy: Math.random() * 5 + 92,
    piiDetected: Math.floor(Math.random() * 30 + 20),
  }
})

// PII detection breakdown
export const piiBreakdown: PIIBreakdown[] = [
  { type: 'Credit Card', count: 342, region: ['US', 'EU', 'UK', 'CA'], severity: 'high' },
  { type: 'SSN', count: 187, region: ['US'], severity: 'high' },
  { type: 'IBAN', count: 156, region: ['EU', 'UK'], severity: 'high' },
  { type: 'Aadhaar', count: 98, region: ['INDIA'], severity: 'high' },
  { type: 'Phone Numbers', count: 234, region: ['US', 'EU', 'UK', 'CA', 'AUS', 'INDIA'], severity: 'medium' },
  { type: 'Email Addresses', count: 156, region: ['US', 'EU', 'UK', 'CA', 'AUS', 'INDIA'], severity: 'low' },
  { type: 'Account Numbers', count: 70, region: ['US', 'EU', 'UK', 'CA'], severity: 'medium' },
]

// Compliance data by region
export const complianceData = {
  US: { status: 'compliant', framework: 'CCPA', lastAudit: '2025-01-15', coverage: 100 },
  EU: { status: 'compliant', framework: 'GDPR', lastAudit: '2025-01-20', coverage: 100 },
  UK: { status: 'compliant', framework: 'UK GDPR', lastAudit: '2025-01-18', coverage: 100 },
  CA: { status: 'compliant', framework: 'PIPEDA', lastAudit: '2025-01-22', coverage: 100 },
  AUS: { status: 'pending', framework: 'Privacy Act', lastAudit: '2024-12-10', coverage: 95 },
  INDIA: { status: 'compliant', framework: 'DPDPA', lastAudit: '2025-01-25', coverage: 100 },
}

// Quick stats for today
export const todayStats = {
  ticketsToday: 487,
  draftsGenerated: 421,
  avgProcessingTime: 2.3, // seconds
  piiProtected: 38,
  apiHealth: 99.8,
  activeRegions: 6,
}

// Industry distribution
export const industryDistribution = [
  { name: 'SaaS', value: 6847, percentage: 53.3 },
  { name: 'E-commerce', value: 4523, percentage: 35.2 },
  { name: 'General', value: 1477, percentage: 11.5 },
]

// Sentiment analysis
export const sentimentData = [
  { sentiment: 'Positive', count: 3847, percentage: 29.9, color: '#10b981' },
  { sentiment: 'Neutral', count: 7234, percentage: 56.3, color: '#6b7280' },
  { sentiment: 'Negative', count: 1766, percentage: 13.8, color: '#ef4444' },
]

// Recent activity feed
export const recentActivity = [
  { id: 1, type: 'batch_complete', message: '500 tickets processed successfully', time: '2 minutes ago', region: 'US' },
  { id: 2, type: 'compliance_alert', message: 'GDPR audit passed with 100% coverage', time: '15 minutes ago', region: 'EU' },
  { id: 3, type: 'milestone', message: '10,000 tickets processed this month! 🎉', time: '1 hour ago', region: 'Global' },
  { id: 4, type: 'pii_detection', message: '38 PII patterns detected and redacted', time: '2 hours ago', region: 'US' },
  { id: 5, type: 'system_update', message: 'Enhanced classification v2.4 deployed', time: '3 hours ago', region: 'Global' },
]

// ROI metrics
export const roiMetrics = {
  costPerTicket: 3.33,
  timeSavedPerTicket: 13.3, // minutes
  annualSavings: 513000,
  accuracyImprovement: 47, // percentage points
  agentProductivity: 312, // percentage increase
}

// Test suite health
export const testSuiteHealth = {
  syntaxCheck: { status: 'pass', time: '0.2s' },
  classificationAccuracy: { status: 'pass', accuracy: '80%', time: '1.3s' },
  piiRedaction: { status: 'pass', patterns: 18, time: '0.5s' },
  enhancedClassification: { status: 'pass', tests: '4/4', time: '0.8s' },
  integration: { status: 'pass', tests: '5/5', time: '2.1s' },
  overallHealth: 100,
}
