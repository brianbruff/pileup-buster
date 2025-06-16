// API service for admin functionality
import { API_BASE_URL } from '../config/api'

export interface AdminCredentials {
  username: string
  password: string
}

class AdminApiService {
  private credentials: AdminCredentials | null = null

  constructor() {
    // Load stored credentials on initialization
    this.loadStoredCredentials()
  }

  private getAuthHeaders(): HeadersInit {
    if (!this.credentials) {
      throw new Error('No admin credentials available')
    }
    
    const encoded = btoa(`${this.credentials.username}:${this.credentials.password}`)
    return {
      'Authorization': `Basic ${encoded}`,
      'Content-Type': 'application/json'
    }
  }

  private loadStoredCredentials(): void {
    try {
      const stored = localStorage.getItem('admin_credentials')
      if (stored) {
        this.credentials = JSON.parse(stored)
      }
    } catch (error) {
      console.error('Failed to load stored credentials:', error)
      localStorage.removeItem('admin_credentials')
    }
  }

  private storeCredentials(credentials: AdminCredentials): void {
    try {
      localStorage.setItem('admin_credentials', JSON.stringify(credentials))
      this.credentials = credentials
    } catch (error) {
      console.error('Failed to store credentials:', error)
    }
  }

  clearCredentials(): void {
    this.credentials = null
    localStorage.removeItem('admin_credentials')
  }

  isLoggedIn(): boolean {
    return this.credentials !== null
  }

  async login(username: string, password: string): Promise<boolean> {
    const credentials = { username, password }
    
    try {
      // Test credentials by making a request to an admin endpoint
      const encoded = btoa(`${username}:${password}`)
      const response = await fetch(`${API_BASE_URL}/admin/queue`, {
        method: 'GET',
        headers: {
          'Authorization': `Basic ${encoded}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        this.storeCredentials(credentials)
        return true
      } else {
        return false
      }
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  logout(): void {
    this.clearCredentials()
  }

  async getSystemStatus(): Promise<boolean> {
    try {
      // Use queue endpoint for status (no auth required)
      const response = await fetch(`${API_BASE_URL}/queue/status`)
      if (response.ok) {
        const data = await response.json()
        return data.active
      }
      throw new Error('Failed to get system status')
    } catch (error) {
      console.error('Failed to get system status:', error)
      throw error
    }
  }

  async setSystemStatus(active: boolean): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/status`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ active })
      })

      if (response.ok) {
        return active
      }
      throw new Error('Failed to set system status')
    } catch (error) {
      console.error('Failed to set system status:', error)
      throw error
    }
  }

  async workNextUser(): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/queue/next`, {
        method: 'POST',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Failed to work next user')
      }
    } catch (error) {
      console.error('Failed to work next user:', error)
      throw error
    }
  }

  async deleteCallsign(callsign: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/queue/${encodeURIComponent(callsign)}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to delete callsign')
      }
    } catch (error) {
      console.error('Failed to delete callsign:', error)
      throw error
    }
  }
}

export const adminApiService = new AdminApiService()