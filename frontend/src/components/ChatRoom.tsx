import { useState, useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'
import type { ChatMessage as ChatMessageType, ChatRoom as ChatRoomType } from '../services/chatApi'
import { chatApiService } from '../services/chatApi'
import { sseService, type StateChangeEvent } from '../services/sse'

interface ChatRoomProps {
  room: ChatRoomType
  callsign: string
  isAdmin?: boolean
  adminCredentials?: string
}

export default function ChatRoom({ room, callsign, isAdmin, adminCredentials }: ChatRoomProps) {
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Load messages when room changes
  useEffect(() => {
    const loadMessages = async () => {
      try {
        setLoading(true)
        setError(null)
        const roomMessages = await chatApiService.getChatMessages(room.name)
        setMessages(roomMessages)
      } catch (err) {
        console.error('Failed to load messages:', err)
        setError('Failed to load messages')
      } finally {
        setLoading(false)
      }
    }

    loadMessages()
  }, [room.name])

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Handle real-time chat messages via SSE
  useEffect(() => {
    const handleChatMessage = (event: StateChangeEvent) => {
      const messageData = event.data as ChatMessageType
      
      // Only add messages for the current room
      if (messageData.room_name === room.name) {
        if (messageData.message_type === 'deleted') {
          // Handle message deletion
          setMessages(prev => prev.filter(msg => msg.timestamp !== messageData.timestamp))
        } else {
          // Add new message
          setMessages(prev => {
            // Avoid duplicates
            const exists = prev.some(msg => 
              msg.timestamp === messageData.timestamp && 
              msg.callsign === messageData.callsign
            )
            if (exists) return prev
            return [...prev, messageData]
          })
        }
      }
    }

    const handleChatRoomUpdate = (event: StateChangeEvent) => {
      const updateData = event.data
      if (updateData.action === 'cleared' && updateData.room_name === room.name) {
        setMessages([])
      }
    }

    // Register SSE event listeners
    sseService.addEventListener('chat_message', handleChatMessage)
    sseService.addEventListener('chat_room_update', handleChatRoomUpdate)

    // Cleanup
    return () => {
      sseService.removeEventListener('chat_message', handleChatMessage)
      sseService.removeEventListener('chat_room_update', handleChatRoomUpdate)
    }
  }, [room.name])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!newMessage.trim() || sending) return

    try {
      setSending(true)
      setError(null)
      
      await chatApiService.sendMessage({
        callsign: callsign,
        message: newMessage.trim(),
        room_name: room.name
      })
      
      setNewMessage('')
    } catch (err) {
      console.error('Failed to send message:', err)
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setSending(false)
    }
  }

  const handleDeleteMessage = async (message: ChatMessageType) => {
    if (!isAdmin || !adminCredentials) return

    try {
      await chatApiService.deleteMessage({
        room_name: message.room_name,
        message_timestamp: message.timestamp
      }, adminCredentials)
    } catch (err) {
      console.error('Failed to delete message:', err)
      setError(err instanceof Error ? err.message : 'Failed to delete message')
    }
  }

  const handleClearRoom = async () => {
    if (!isAdmin || !adminCredentials) return
    
    if (!window.confirm(`Are you sure you want to clear all messages in ${room.name}?`)) {
      return
    }

    try {
      await chatApiService.clearChatRoom(room.name, adminCredentials)
    } catch (err) {
      console.error('Failed to clear room:', err)
      setError(err instanceof Error ? err.message : 'Failed to clear room')
    }
  }

  return (
    <div className="chat-room">
      <div className="chat-room-header">
        <h3>{room.name}</h3>
        {room.description && <p className="room-description">{room.description}</p>}
        {isAdmin && (
          <button 
            className="clear-room-button"
            onClick={handleClearRoom}
            title="Clear all messages (admin)"
          >
            Clear Room
          </button>
        )}
      </div>

      <div className="chat-messages">
        {loading && <div className="loading">Loading messages...</div>}
        
        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {!loading && messages.length === 0 && (
          <div className="no-messages">
            No messages yet. Be the first to say something!
          </div>
        )}

        {messages.map((message, index) => (
          <ChatMessage
            key={`${message.timestamp}-${index}`}
            message={message}
            isAdmin={isAdmin}
            onDelete={handleDeleteMessage}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder={`Message ${room.name}...`}
          disabled={sending}
          maxLength={500}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={!newMessage.trim() || sending}
          className="send-button"
        >
          {sending ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}