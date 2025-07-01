// API service for admin functionality
import { API_BASE_URL } from '../config/api'
import { type CurrentQsoData } from './api'

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

  async workNextUser(): Promise<CurrentQsoData | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/queue/next`, {
        method: 'POST',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Failed to work next user')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to work next user:', error)
      throw error
    }
  }

  async completeCurrentQso(): Promise<{ message: string; cleared_qso: CurrentQsoData | null }> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/qso/complete`, {
        method: 'POST',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Failed to complete current QSO')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to complete current QSO:', error)
      throw error
    }
  }

  async setFrequency(frequency: string): Promise<{ message: string; frequency_data: any }> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/frequency`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ frequency })
      })

      if (!response.ok) {
        throw new Error('Failed to set frequency')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to set frequency:', error)
      throw error
    }
  }

  async setSplit(split: string): Promise<{ message: string; split_data: any }> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/split`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ split })
      })

      if (!response.ok) {
        throw new Error('Failed to set split')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to set split:', error)
      throw error
    }
  }

  async clearFrequency(): Promise<{ message: string; frequency_data: any }> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/frequency`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Failed to clear frequency')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to clear frequency:', error)
      throw error
    }
  }

  async clearSplit(): Promise<{ message: string; split_data: any }> {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/split`, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Failed to clear split')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to clear split:', error)
      throw error
    }
  }
}

export const adminApiService = new AdminApiService()