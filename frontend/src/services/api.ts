// API service for backend communication

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export interface QueueEntry {
  callsign: string;
  timestamp: string;
  position: number;
}

export interface CurrentQSO {
  callsign: string;
  timestamp: string;
  qrz?: {
    name?: string;
    location?: string;
    image?: string;
  };
}

export interface SystemStatus {
  active: boolean;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        return { error: `HTTP ${response.status}: ${errorText}` };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return { error: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}` };
    }
  }

  // Queue operations
  async getQueue(): Promise<ApiResponse<{ queue: QueueEntry[]; total: number; system_active: boolean }>> {
    return this.request('/queue/list');
  }

  async registerCallsign(callsign: string): Promise<ApiResponse<QueueEntry>> {
    return this.request('/queue/register', {
      method: 'POST',
      body: JSON.stringify({ callsign }),
    });
  }

  async getCallsignStatus(callsign: string): Promise<ApiResponse<QueueEntry>> {
    return this.request(`/queue/status/${callsign}`);
  }

  // Current QSO operations
  async getCurrentQSO(): Promise<ApiResponse<CurrentQSO | null>> {
    return this.request('/queue/current');
  }

  // System status
  async getSystemStatus(): Promise<ApiResponse<SystemStatus>> {
    return this.request('/queue/status');
  }
}

export const apiService = new ApiService();