import { API_BASE_URL } from '../config/api'

export interface QueueEntry {
  callsign: string
  timestamp: string
  position: number
  qrz?: {
    callsign?: string
    name?: string
    address?: string
    dxcc_name?: string
    image?: string
    error?: string
  }
}

export interface CurrentQsoData {
  callsign: string
  timestamp: string
  qrz?: {
    name?: string
    address?: string
    dxcc_name?: string
    image?: string
    url?: string
  }
}

export interface QueueListResponse {
  queue: QueueEntry[]
  total: number
  max_size: number
  system_active: boolean
}

export interface RegisterResponse {
  message: string
  entry: QueueEntry
}

export class ApiError extends Error {
  status: number
  detail?: string

  constructor(
    message: string,
    status: number,
    detail?: string
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError(
      `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData.detail || response.statusText
    )
  }
  return response.json()
}

export const apiService = {
  // Register a new callsign in the queue
  async registerCallsign(callsign: string): Promise<RegisterResponse> {
    const response = await fetch(`${API_BASE_URL}/queue/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ callsign }),
    })
    return handleResponse<RegisterResponse>(response)
  },

  // Get current active callsign
  async getCurrentQso(): Promise<CurrentQsoData | null> {
    const response = await fetch(`${API_BASE_URL}/queue/current`)
    if (response.status === 404) {
      return null
    }
    return handleResponse<CurrentQsoData | null>(response)
  },

  // Get the waiting queue list
  async getQueueList(): Promise<QueueListResponse> {
    const response = await fetch(`${API_BASE_URL}/queue/list`)
    return handleResponse<QueueListResponse>(response)
  },
}