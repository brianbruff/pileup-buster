import { useState } from 'react'

export interface AddQueueItemProps {
  onAddCallsign: (callsign: string) => Promise<boolean>
}

export default function AddQueueItem({ onAddCallsign }: AddQueueItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [callsign, setCallsign] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleClick = () => {
    setIsEditing(true)
  }

  const handleSubmit = async () => {
    if (!callsign.trim() || isSubmitting) return
    
    setIsSubmitting(true)
    try {
      const success = await onAddCallsign(callsign.trim().toUpperCase())
      if (success) {
        setCallsign('')
        setIsEditing(false)
      }
      // If unsuccessful, keep the input open so user can try again
    } catch (error) {
      console.error('Error adding callsign:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSubmit()
    } else if (e.key === 'Escape') {
      setCallsign('')
      setIsEditing(false)
    }
  }

  const handleBlur = () => {
    // Don't close if we're submitting
    if (!isSubmitting) {
      setCallsign('')
      setIsEditing(false)
    }
  }

  return (
    <div className="callsign-card add-queue-item" onClick={handleClick}>
      {isEditing ? (
        <input
          type="text"
          value={callsign}
          onChange={(e) => setCallsign(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder={isSubmitting ? "Adding..." : "CALLSIGN"}
          className="callsign-input"
          autoFocus
          maxLength={10}
          disabled={isSubmitting}
        />
      ) : (
        <div className="add-icon">➕</div>
      )}
    </div>
  )
}
