'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import {
  FileText, Search, Filter, Download, ChevronLeft, ChevronRight,
  ArrowUpDown, CheckCircle2, AlertCircle, Clock, Tag, TrendingUp,
  Calendar, User, Building, Globe, Shield, Brain, Menu, X
} from 'lucide-react'
import { cn, formatNumber } from '@/lib/utils'
import { useDashboardData } from '@/lib/use-dashboard-data'

interface Ticket {
  id: number
  description: string
  category: string
  industry: string
  confidence: number
  status: string
  region: string
  pii_protected: boolean
  processing_time: number
  processed_at: string
}

export default function TicketsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterCategory, setFilterCategory] = useState('all')
  const [filterIndustry, setFilterIndustry] = useState('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [sortBy, setSortBy] = useState<'date' | 'confidence' | 'id'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const { data, loading, error, isLive, apiAvailable, refresh } = useDashboardData()
  const [tickets, setTickets] = useState<Ticket[]>([])

  const itemsPerPage = 20

  // Fetch tickets from API or use mock data
  useEffect(() => {
    const fetchTickets = async () => {
      if (apiAvailable) {
        try {
          const response = await fetch('http://localhost:8000/api/tickets/recent?limit=100')
          const data = await response.json()
          setTickets(data)
        } catch (err) {
          console.error('Failed to fetch tickets:', err)
          // Use mock data
          setTickets(generateMockTickets())
        }
      } else {
        setTickets(generateMockTickets())
      }
    }

    fetchTickets()
  }, [apiAvailable])

  // Generate mock tickets for demo
  const generateMockTickets = (): Ticket[] => {
    const categories = ['API Integration Error', 'Login/Authentication', 'Feature Request', 'Billing', 'Payment', 'Account', 'Data Sync', 'Other']
    const industries = ['SaaS', 'E-commerce', 'General']
    const regions = ['US', 'EU', 'UK', 'CA', 'AUS']

    return Array.from({ length: 50 }, (_, i) => ({
      id: 12345 + i,
      description: `Customer ticket regarding ${categories[i % categories.length]}`,
      category: categories[i % categories.length],
      industry: industries[i % industries.length],
      confidence: 75 + Math.random() * 25,
      status: Math.random() > 0.1 ? 'processed' : 'pending',
      region: regions[i % regions.length],
      pii_protected: Math.random() > 0.7,
      processing_time: 5 + Math.random() * 10,
      processed_at: new Date(Date.now() - i * 3600000).toISOString()
    }))
  }

  // Filter and sort tickets
  const filteredTickets = tickets
    .filter(ticket => {
      const matchesSearch = searchQuery === '' ||
        ticket.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ticket.id.toString().includes(searchQuery)
      const matchesCategory = filterCategory === 'all' || ticket.category === filterCategory
      const matchesIndustry = filterIndustry === 'all' || ticket.industry === filterIndustry
      return matchesSearch && matchesCategory && matchesIndustry
    })
    .sort((a, b) => {
      let comparison = 0
      if (sortBy === 'date') {
        comparison = new Date(a.processed_at).getTime() - new Date(b.processed_at).getTime()
      } else if (sortBy === 'confidence') {
        comparison = a.confidence - b.confidence
      } else {
        comparison = a.id - b.id
      }
      return sortOrder === 'asc' ? comparison : -comparison
    })

  const totalPages = Math.ceil(filteredTickets.length / itemsPerPage)
  const paginatedTickets = filteredTickets.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const categories = Array.from(new Set(tickets.map(t => t.category)))
  const industries = Array.from(new Set(tickets.map(t => t.industry)))

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
            {!sidebarOpen && (
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center mx-auto">
                <Brain className="w-5 h-5 text-white" />
              </div>
            )}
          </div>

          <nav className="flex-1 px-3 py-6 space-y-1">
            <NavItem href="/" icon={TrendingUp} label="Dashboard" sidebarOpen={sidebarOpen} />
            <NavItem href="/tickets" icon={FileText} label="Tickets" active sidebarOpen={sidebarOpen} />
            <NavItem href="/analytics" icon={TrendingUp} label="Analytics" sidebarOpen={sidebarOpen} />
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
              <h1 className="text-xl font-bold text-gray-900">Tickets</h1>
              <span className="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-sm font-medium">
                {filteredTickets.length} tickets
              </span>
            </div>

            <div className="flex items-center gap-3">
              <button onClick={refresh} className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg">
                Refresh
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </header>

        {/* Filters */}
        <div className="p-6 space-y-4">
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by ticket ID or description..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Category Filter */}
              <div>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Categories</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              {/* Industry Filter */}
              <div>
                <select
                  value={filterIndustry}
                  onChange={(e) => setFilterIndustry(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Industries</option>
                  {industries.map(ind => (
                    <option key={ind} value={ind}>{ind}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Table */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <button onClick={() => {
                        setSortBy('id')
                        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
                      }} className="flex items-center gap-1 hover:text-gray-700">
                        Ticket ID <ArrowUpDown className="w-3 h-3" />
                      </button>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Industry
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <button onClick={() => {
                        setSortBy('confidence')
                        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
                      }} className="flex items-center gap-1 hover:text-gray-700">
                        Confidence <ArrowUpDown className="w-3 h-3" />
                      </button>
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Region
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <button onClick={() => {
                        setSortBy('date')
                        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
                      }} className="flex items-center gap-1 hover:text-gray-700">
                        Date <ArrowUpDown className="w-3 h-3" />
                      </button>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {paginatedTickets.map((ticket) => (
                    <tr key={ticket.id} className="hover:bg-gray-50 cursor-pointer transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-blue-600">#{ticket.id}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-900 max-w-md truncate">{ticket.description}</span>
                          {ticket.pii_protected && (
                            <Shield className="w-4 h-4 text-orange-500" title="PII Protected" />
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {ticket.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">{ticket.industry}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className={cn("h-2 rounded-full",
                                ticket.confidence >= 90 ? "bg-green-500" :
                                ticket.confidence >= 75 ? "bg-blue-500" : "bg-yellow-500"
                              )}
                              style={{ width: `${ticket.confidence}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-600">{ticket.confidence.toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {ticket.status === 'processed' ? (
                          <span className="inline-flex items-center gap-1 text-green-600">
                            <CheckCircle2 className="w-4 h-4" />
                            <span className="text-sm">Processed</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-yellow-600">
                            <Clock className="w-4 h-4" />
                            <span className="text-sm">Pending</span>
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">{ticket.region}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(ticket.processed_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, filteredTickets.length)} of {filteredTickets.length} tickets
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-sm text-gray-600">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

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
