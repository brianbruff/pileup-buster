import { formatDistanceToNow } from 'date-fns'
import type { ChatMessage as ChatMessageType } from '../services/chatApi'

interface ChatMessageProps {
  message: ChatMessageType
  isAdmin?: boolean
  onDelete?: (message: ChatMessageType) => void
}

export default function ChatMessage({ message, isAdmin, onDelete }: ChatMessageProps) {
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return formatDistanceToNow(date, { addSuffix: true })
    } catch {
      return 'unknown time'
    }
  }

  const getMessageClass = () => {
    switch (message.message_type) {
      case 'join':
        return 'chat-message system-message join-message'
      case 'leave':
        return 'chat-message system-message leave-message'
      case 'system':
        return 'chat-message system-message'
      case 'deleted':
        return 'chat-message deleted-message'
      default:
        return 'chat-message user-message'
    }
  }

  const handleDelete = () => {
    if (onDelete && window.confirm('Are you sure you want to delete this message?')) {
      onDelete(message)
    }
  }

  if (message.deleted) {
    return (
      <div className="chat-message deleted-message">
        <span className="message-deleted">Message deleted by {message.deleted_by}</span>
      </div>
    )
  }

  if (message.message_type === 'deleted') {
    return null // Don't show deletion notifications as messages
  }

  return (
    <div className={getMessageClass()}>
      <div className="message-header">
        <span className="message-callsign">{message.callsign}</span>
        <span className="message-timestamp">{formatTimestamp(message.timestamp)}</span>
        {isAdmin && message.message_type === 'message' && (
          <button 
            className="delete-message-button"
            onClick={handleDelete}
            title="Delete message"
          >
            ×
          </button>
        )}
      </div>
      <div className="message-content">
        {message.message}
      </div>
    </div>
  )
}