/**
 * Server-Sent Events (SSE) service for real-time notifications
 */
import { API_BASE_URL } from '../config/api'

export interface StateChangeEvent {
  type: 'current_qso' | 'queue_update' | 'system_status' | 'frequency_update' | 'connected' | 'keepalive'
  data: any
  timestamp: string
}

export type EventCallback = (event: StateChangeEvent) => void

export class SSEService {
  private eventSource: EventSource | null = null
  private eventCallbacks: Map<string, EventCallback[]> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // Start with 1 second
  private isConnecting = false

  /**
   * Start the SSE connection
   */
  connect(): void {
    if (this.eventSource && this.eventSource.readyState !== EventSource.CLOSED) {
      console.log('SSE already connected or connecting')
      return
    }

    if (this.isConnecting) {
      console.log('SSE connection attempt already in progress')
      return
    }

    this.isConnecting = true
    const url = `${API_BASE_URL}/events/stream`
    
    try {
      this.eventSource = new EventSource(url)
      
      this.eventSource.onopen = () => {
        console.log('SSE connection opened')
        this.reconnectAttempts = 0
        this.reconnectDelay = 1000
        this.isConnecting = false
      }

      this.eventSource.onerror = (error) => {
        console.error('SSE connection error:', error)
        this.isConnecting = false
        this.handleReconnection()
      }

      // Handle different event types
      this.eventSource.addEventListener('current_qso', (event) => {
        this.handleEvent('current_qso', event)
      })

      this.eventSource.addEventListener('queue_update', (event) => {
        this.handleEvent('queue_update', event)
      })

      this.eventSource.addEventListener('system_status', (event) => {
        this.handleEvent('system_status', event)
      })

      this.eventSource.addEventListener('frequency_update', (event) => {
        this.handleEvent('frequency_update', event)
      })

      this.eventSource.addEventListener('connected', (event) => {
        this.handleEvent('connected', event)
      })

      this.eventSource.addEventListener('keepalive', () => {
        // Keepalive events don't need to be handled by the UI
        console.debug('SSE keepalive received')
      })

    } catch (error) {
      console.error('Failed to create SSE connection:', error)
      this.isConnecting = false
      this.handleReconnection()
    }
  }

  /**
   * Disconnect the SSE connection
   */
  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
    this.isConnecting = false
    this.reconnectAttempts = 0
  }

  /**
   * Register a callback for specific event types
   */
  addEventListener(eventType: string, callback: EventCallback): void {
    if (!this.eventCallbacks.has(eventType)) {
      this.eventCallbacks.set(eventType, [])
    }
    this.eventCallbacks.get(eventType)!.push(callback)
  }

  /**
   * Remove a callback for specific event types
   */
  removeEventListener(eventType: string, callback: EventCallback): void {
    const callbacks = this.eventCallbacks.get(eventType)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * Check if SSE is connected
   */
  isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN
  }

  private handleEvent(eventType: string, event: MessageEvent): void {
    try {
      const eventData: StateChangeEvent = JSON.parse(event.data)
      
      // Call registered callbacks
      const callbacks = this.eventCallbacks.get(eventType)
      if (callbacks) {
        callbacks.forEach(callback => {
          try {
            callback(eventData)
          } catch (error) {
            console.error(`Error in SSE callback for ${eventType}:`, error)
          }
        })
      }
    } catch (error) {
      console.error(`Failed to parse SSE event data for ${eventType}:`, error)
    }
  }

  private handleReconnection(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max SSE reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(`SSE reconnection attempt ${this.reconnectAttempts} in ${this.reconnectDelay}ms`)

    setTimeout(() => {
      this.connect()
    }, this.reconnectDelay)

    // Exponential backoff with jitter
    this.reconnectDelay = Math.min(
      this.reconnectDelay * 2 + Math.random() * 1000,
      30000 // Max 30 seconds
    )
  }
}

// Global SSE service instance
export const sseService = new SSEService()