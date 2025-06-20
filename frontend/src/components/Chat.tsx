import { useState, useEffect } from 'react'
import ChatRoom from './ChatRoom'
import type { ChatRoom as ChatRoomType } from '../services/chatApi'
import { chatApiService } from '../services/chatApi'
import { sseService, type StateChangeEvent, type ChatRoomUpdateEventData } from '../services/sse'

interface ChatProps {
  callsign: string
  isAdmin?: boolean
  adminCredentials?: string
}

export default function Chat({ callsign, isAdmin, adminCredentials }: ChatProps) {
  const [rooms, setRooms] = useState<ChatRoomType[]>([])
  const [selectedRoom, setSelectedRoom] = useState<ChatRoomType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateRoom, setShowCreateRoom] = useState(false)
  const [newRoomName, setNewRoomName] = useState('')
  const [newRoomDescription, setNewRoomDescription] = useState('')
  const [creating, setCreating] = useState(false)

  // Load chat rooms
  useEffect(() => {
    const loadRooms = async () => {
      try {
        setLoading(true)
        setError(null)
        const availableRooms = await chatApiService.getChatRooms()
        setRooms(availableRooms)
        
        // Auto-select 'general' room if available, otherwise first room
        if (availableRooms.length > 0) {
          const generalRoom = availableRooms.find(room => room.name === 'general')
          setSelectedRoom(generalRoom || availableRooms[0])
        }
      } catch (err) {
        console.error('Failed to load chat rooms:', err)
        setError('Failed to load chat rooms')
      } finally {
        setLoading(false)
      }
    }

    loadRooms()
  }, [])

  // Handle room updates via SSE
  useEffect(() => {
    const handleChatRoomUpdate = (event: StateChangeEvent) => {
      const updateData = event.data as ChatRoomUpdateEventData
      
      if (updateData.action === 'created' && updateData.room) {
        // Add new room to list
        setRooms(prev => {
          const exists = prev.some(room => room.name === (updateData.room as any).name)
          if (exists) return prev
          return [...prev, updateData.room as any]
        })
      }
    }

    sseService.addEventListener('chat_room_update', handleChatRoomUpdate)
    
    return () => {
      sseService.removeEventListener('chat_room_update', handleChatRoomUpdate)
    }
  }, [])

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!newRoomName.trim() || creating || !isAdmin || !adminCredentials) return

    try {
      setCreating(true)
      setError(null)
      
      const newRoom = await chatApiService.createChatRoom({
        name: newRoomName.trim(),
        description: newRoomDescription.trim()
      }, adminCredentials)
      
      // Room will be added via SSE event, but add it immediately for better UX
      setRooms(prev => {
        const exists = prev.some(room => room.name === newRoom.name)
        if (exists) return prev
        return [...prev, newRoom]
      })
      
      setSelectedRoom(newRoom)
      setNewRoomName('')
      setNewRoomDescription('')
      setShowCreateRoom(false)
    } catch (err) {
      console.error('Failed to create room:', err)
      setError(err instanceof Error ? err.message : 'Failed to create room')
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="chat-container">
        <div className="loading">Loading chat...</div>
      </div>
    )
  }

  if (error && rooms.length === 0) {
    return (
      <div className="chat-container">
        <div className="error-message">
          {error}
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-container">
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <h3>Chat Rooms</h3>
          {isAdmin && (
            <button 
              className="create-room-button"
              onClick={() => setShowCreateRoom(!showCreateRoom)}
              title="Create new room (admin)"
            >
              +
            </button>
          )}
        </div>

        {showCreateRoom && isAdmin && (
          <form className="create-room-form" onSubmit={handleCreateRoom}>
            <input
              type="text"
              placeholder="Room name"
              value={newRoomName}
              onChange={(e) => setNewRoomName(e.target.value)}
              disabled={creating}
              maxLength={50}
              required
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={newRoomDescription}
              onChange={(e) => setNewRoomDescription(e.target.value)}
              disabled={creating}
              maxLength={200}
            />
            <div className="form-buttons">
              <button type="submit" disabled={!newRoomName.trim() || creating}>
                {creating ? 'Creating...' : 'Create'}
              </button>
              <button type="button" onClick={() => setShowCreateRoom(false)}>
                Cancel
              </button>
            </div>
          </form>
        )}

        <div className="room-list">
          {rooms.map(room => (
            <button
              key={room.name}
              className={`room-button ${selectedRoom?.name === room.name ? 'active' : ''}`}
              onClick={() => setSelectedRoom(room)}
            >
              <div className="room-name">#{room.name}</div>
              {room.description && (
                <div className="room-description">{room.description}</div>
              )}
              <div className="message-count">{room.message_count} messages</div>
            </button>
          ))}
        </div>
      </div>

      <div className="chat-main">
        {selectedRoom ? (
          <ChatRoom
            room={selectedRoom}
            callsign={callsign}
            isAdmin={isAdmin}
            adminCredentials={adminCredentials}
          />
        ) : (
          <div className="no-room-selected">
            Select a chat room to start messaging
          </div>
        )}
      </div>

      {error && (
        <div className="error-toast">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
    </div>
  )
}