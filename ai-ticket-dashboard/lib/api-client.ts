/**
 * API Client for AI Ticket Processor Dashboard
 *
 * Provides functions to fetch data from the FastAPI backend
 * and establish WebSocket connections for real-time updates.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

/**
 * Fetch dashboard metrics
 */
export async function fetchMetrics() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/metrics`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching metrics:', error);
    throw error;
  }
}

/**
 * Fetch 30-day trend data
 */
export async function fetchTrends() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/trends`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching trends:', error);
    throw error;
  }
}

/**
 * Fetch regional performance data
 */
export async function fetchRegions() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/regions`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching regions:', error);
    throw error;
  }
}

/**
 * Fetch category distribution
 */
export async function fetchCategories() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/categories`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
}

/**
 * Fetch compliance status for all regions
 */
export async function fetchCompliance() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/compliance`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching compliance:', error);
    throw error;
  }
}

/**
 * Fetch recent activity feed
 */
export async function fetchActivity() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/activity`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching activity:', error);
    throw error;
  }
}

/**
 * Fetch PII detection breakdown
 */
export async function fetchPII() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/pii`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching PII data:', error);
    throw error;
  }
}

/**
 * Fetch test suite health status
 */
export async function fetchTests() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/tests`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching tests:', error);
    throw error;
  }
}

/**
 * Fetch recent processed tickets
 */
export async function fetchRecentTickets(limit: number = 50) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tickets/recent?limit=${limit}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching recent tickets:', error);
    throw error;
  }
}

/**
 * Check API server health
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) return { status: 'unhealthy', available: false };
    const data = await response.json();
    return { ...data, available: true };
  } catch (error) {
    console.error('API server not available:', error);
    return { status: 'unavailable', available: false };
  }
}

/**
 * WebSocket connection manager for real-time updates
 */
export class DashboardWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private listeners: Map<string, Function[]> = new Map();

  constructor(private url: string = `${WS_BASE_URL}/ws/dashboard`) {}

  /**
   * Connect to WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.emit(data.type || 'message', data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.attemptReconnect();
        };
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      setTimeout(() => {
        this.connect().catch((error) => {
          console.error('Reconnection failed:', error);
        });
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('max_reconnect_failed', {});
    }
  }

  /**
   * Register event listener
   */
  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  /**
   * Unregister event listener
   */
  off(event: string, callback: Function) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  /**
   * Emit event to all registered listeners
   */
  private emit(event: string, data: any) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => callback(data));
    }
  }

  /**
   * Send message to server
   */
  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

/**
 * Create a singleton WebSocket instance
 */
let wsInstance: DashboardWebSocket | null = null;

export function getWebSocketInstance(): DashboardWebSocket {
  if (!wsInstance) {
    wsInstance = new DashboardWebSocket();
  }
  return wsInstance;
}

/**
 * Helper function to fetch all dashboard data at once
 */
export async function fetchAllDashboardData() {
  try {
    const [
      metrics,
      trends,
      regions,
      categories,
      compliance,
      activity,
      pii,
      tests,
    ] = await Promise.all([
      fetchMetrics(),
      fetchTrends(),
      fetchRegions(),
      fetchCategories(),
      fetchCompliance(),
      fetchActivity(),
      fetchPII(),
      fetchTests(),
    ]);

    return {
      metrics,
      trends,
      regions,
      categories,
      compliance,
      activity,
      pii,
      tests,
    };
  } catch (error) {
    console.error('Error fetching all dashboard data:', error);
    throw error;
  }
}
