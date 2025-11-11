/**
 * Custom React Hook for Dashboard Data Management
 *
 * Handles:
 * - Initial data fetching from API
 * - WebSocket connection for real-time updates
 * - Automatic fallback to mock data if API unavailable
 * - Loading and error states
 */

'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  fetchAllDashboardData,
  checkHealth,
  getWebSocketInstance,
  type DashboardWebSocket,
} from './api-client'
import {
  dashboardMetrics as mockMetrics,
  regionData as mockRegionData,
  categoryData as mockCategoryData,
  trendData as mockTrendData,
  piiBreakdown as mockPiiBreakdown,
  complianceData as mockComplianceData,
  recentActivity as mockRecentActivity,
  testSuiteHealth as mockTestSuiteHealth,
} from './mock-data'

export interface DashboardData {
  metrics: any
  trends: any[]
  regions: any[]
  categories: any[]
  compliance: any[]
  activity: any[]
  pii: any
  tests: any[]
}

export interface DashboardState {
  data: DashboardData
  loading: boolean
  error: Error | null
  isLive: boolean
  lastUpdate: Date | null
  apiAvailable: boolean
}

export function useDashboardData(autoRefresh = true, refreshInterval = 30000) {
  const [state, setState] = useState<DashboardState>({
    data: {
      metrics: mockMetrics,
      trends: mockTrendData,
      regions: mockRegionData,
      categories: mockCategoryData,
      compliance: mockComplianceData,
      activity: mockRecentActivity,
      pii: mockPiiBreakdown,
      tests: mockTestSuiteHealth,
    },
    loading: true,
    error: null,
    isLive: false,
    lastUpdate: null,
    apiAvailable: false,
  })

  const wsRef = useRef<DashboardWebSocket | null>(null)
  const refreshTimerRef = useRef<NodeJS.Timeout | null>(null)

  /**
   * Fetch data from API
   */
  const fetchData = useCallback(async () => {
    try {
      // Check if API is available first
      const health = await checkHealth()

      if (!health.available) {
        console.warn('API server not available, using mock data')
        setState(prev => ({
          ...prev,
          loading: false,
          apiAvailable: false,
          isLive: false,
          lastUpdate: new Date(),
        }))
        return
      }

      // Fetch all data
      const data = await fetchAllDashboardData()

      setState(prev => ({
        ...prev,
        data: {
          metrics: data.metrics,
          trends: data.trends,
          regions: data.regions,
          categories: data.categories,
          compliance: data.compliance,
          activity: data.activity,
          pii: data.pii,
          tests: data.tests,
        },
        loading: false,
        error: null,
        apiAvailable: true,
        lastUpdate: new Date(),
      }))

      console.log('✅ Dashboard data loaded from API')
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setState(prev => ({
        ...prev,
        loading: false,
        error: error as Error,
        apiAvailable: false,
        isLive: false,
        lastUpdate: new Date(),
      }))
    }
  }, [])

  /**
   * Connect to WebSocket for real-time updates
   */
  const connectWebSocket = useCallback(async () => {
    if (wsRef.current?.isConnected()) {
      console.log('WebSocket already connected')
      return
    }

    try {
      const ws = getWebSocketInstance()
      wsRef.current = ws

      // Handle ticket processed event
      ws.on('ticket_processed', (data: any) => {
        console.log('📨 New ticket processed:', data)

        setState(prev => ({
          ...prev,
          isLive: true,
          lastUpdate: new Date(),
        }))

        // Refresh data after receiving update
        fetchData()
      })

      // Handle metrics updated event
      ws.on('metrics_updated', (data: any) => {
        console.log('📊 Metrics updated:', data)

        setState(prev => ({
          ...prev,
          data: {
            ...prev.data,
            metrics: data.data || prev.data.metrics,
          },
          isLive: true,
          lastUpdate: new Date(),
        }))
      })

      // Handle connection failures
      ws.on('max_reconnect_failed', () => {
        console.error('❌ WebSocket reconnection failed')
        setState(prev => ({
          ...prev,
          isLive: false,
        }))
      })

      // Attempt connection
      await ws.connect()
      console.log('✅ WebSocket connected successfully')

      setState(prev => ({
        ...prev,
        isLive: true,
      }))
    } catch (error) {
      console.error('WebSocket connection failed:', error)
      setState(prev => ({
        ...prev,
        isLive: false,
      }))
    }
  }, [fetchData])

  /**
   * Disconnect WebSocket
   */
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect()
      wsRef.current = null
      setState(prev => ({
        ...prev,
        isLive: false,
      }))
      console.log('WebSocket disconnected')
    }
  }, [])

  /**
   * Manual refresh
   */
  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true }))
    await fetchData()
  }, [fetchData])

  /**
   * Initial data load and WebSocket connection
   */
  useEffect(() => {
    // Load data immediately
    fetchData()

    // Connect WebSocket after a short delay
    const wsTimeout = setTimeout(() => {
      connectWebSocket()
    }, 1000)

    return () => {
      clearTimeout(wsTimeout)
    }
  }, [fetchData, connectWebSocket])

  /**
   * Auto-refresh interval (fallback if WebSocket not available)
   */
  useEffect(() => {
    if (!autoRefresh || state.isLive) {
      // Don't auto-refresh if WebSocket is live
      return
    }

    refreshTimerRef.current = setInterval(() => {
      console.log('Auto-refreshing dashboard data...')
      fetchData()
    }, refreshInterval)

    return () => {
      if (refreshTimerRef.current) {
        clearInterval(refreshTimerRef.current)
      }
    }
  }, [autoRefresh, refreshInterval, state.isLive, fetchData])

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      disconnectWebSocket()
      if (refreshTimerRef.current) {
        clearInterval(refreshTimerRef.current)
      }
    }
  }, [disconnectWebSocket])

  return {
    ...state,
    refresh,
    connectWebSocket,
    disconnectWebSocket,
  }
}

/**
 * Hook for connection status indicator
 */
export function useConnectionStatus() {
  const [status, setStatus] = useState<{
    api: boolean
    websocket: boolean
    lastChecked: Date | null
  }>({
    api: false,
    websocket: false,
    lastChecked: null,
  })

  useEffect(() => {
    const checkStatus = async () => {
      const health = await checkHealth()
      const ws = getWebSocketInstance()

      setStatus({
        api: health.available,
        websocket: ws.isConnected(),
        lastChecked: new Date(),
      })
    }

    checkStatus()

    // Check every 10 seconds
    const interval = setInterval(checkStatus, 10000)

    return () => clearInterval(interval)
  }, [])

  return status
}
