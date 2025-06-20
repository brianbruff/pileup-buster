/**
 * Chat API service for frontend communication
 */
import { API_BASE_URL } from '../config/api'

export interface ChatMessage {
  callsign: string
  message: string
  room_name: string
  timestamp: string
  message_type: string
  deleted?: boolean
  deleted_by?: string
  deleted_at?: string
}

export interface ChatRoom {
  name: string
  description: string
  created_by: string
  created_at: string
  active: boolean
  message_count: number
}

export interface SendMessageRequest {
  callsign: string
  message: string
  room_name: string
}

export interface CreateRoomRequest {
  name: string
  description: string
}

export interface DeleteMessageRequest {
  room_name: string
  message_timestamp: string
}

class ChatApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${API_BASE_URL}/chat`
  }

  /**
   * Get list of available chat rooms
   */
  async getChatRooms(): Promise<ChatRoom[]> {
    const response = await fetch(`${this.baseUrl}/rooms`)
    if (!response.ok) {
      throw new Error(`Failed to get chat rooms: ${response.statusText}`)
    }
    const data = await response.json()
    return data.rooms
  }

  /**
   * Create a new chat room (admin only)
   */
  async createChatRoom(request: CreateRoomRequest, credentials?: string): Promise<ChatRoom> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (credentials) {
      headers['Authorization'] = `Basic ${credentials}`
    }

    const response = await fetch(`${this.baseUrl}/rooms`, {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || 'Failed to create chat room')
    }

    return response.json()
  }

  /**
   * Get messages from a chat room
   */
  async getChatMessages(roomName: string, limit: number = 50, skip: number = 0): Promise<ChatMessage[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      skip: skip.toString(),
    })

    const response = await fetch(`${this.baseUrl}/rooms/${encodeURIComponent(roomName)}/messages?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to get chat messages: ${response.statusText}`)
    }
    
    const data = await response.json()
    return data.messages
  }

  /**
   * Send a message to a chat room
   */
  async sendMessage(request: SendMessageRequest): Promise<ChatMessage> {
    const response = await fetch(`${this.baseUrl}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || 'Failed to send message')
    }

    return response.json()
  }

  /**
   * Delete a chat message (admin only)
   */
  async deleteMessage(request: DeleteMessageRequest, credentials?: string): Promise<void> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (credentials) {
      headers['Authorization'] = `Basic ${credentials}`
    }

    const response = await fetch(`${this.baseUrl}/messages`, {
      method: 'DELETE',
      headers,
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || 'Failed to delete message')
    }
  }

  /**
   * Clear all messages in a chat room (admin only)
   */
  async clearChatRoom(roomName: string, credentials?: string): Promise<void> {
    const headers: Record<string, string> = {}

    if (credentials) {
      headers['Authorization'] = `Basic ${credentials}`
    }

    const response = await fetch(`${this.baseUrl}/rooms/${encodeURIComponent(roomName)}/clear`, {
      method: 'DELETE',
      headers,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || 'Failed to clear chat room')
    }
  }
}

// Global chat API service instance
export const chatApiService = new ChatApiService()