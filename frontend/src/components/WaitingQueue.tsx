import QueueItem from './QueueItem'
import AddQueueItem from './AddQueueItem'
import type { QueueItemData } from './QueueItem'

export interface WaitingQueueProps {
  queueData: QueueItemData[]
  onAddCallsign: (callsign: string) => Promise<void>
  systemActive?: boolean
  isAdmin?: boolean
  onDeleteCallsign?: (callsign: string) => Promise<void>
}

export default function WaitingQueue({ queueData, onAddCallsign, systemActive = true, isAdmin = false, onDeleteCallsign }: WaitingQueueProps) {
  const handleAddCallsign = async (callsign: string) => {
    try {
      await onAddCallsign(callsign)
    } catch (error) {
      // Error handling could be improved with user notifications
      console.error('Failed to add callsign:', error)
      alert(`Failed to add callsign: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const handleDeleteCallsign = async (callsign: string) => {
    if (!onDeleteCallsign) return;
    
    try {
      await onDeleteCallsign(callsign)
    } catch (error) {
      console.error('Failed to delete callsign:', error)
      alert(`Failed to delete callsign: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const showAddButton = queueData.length < 4 && systemActive

  return (
    <section className="queue-section">
      <h2 className="queue-title">Waiting Queue</h2>
      <div className="queue-container">
        {queueData.map((item, index) => (
          <QueueItem 
            key={`${item.callsign}-${index}`} 
            item={item} 
            index={index}
            isAdmin={isAdmin}
            onDelete={isAdmin ? handleDeleteCallsign : undefined}
          />
        ))}
        {showAddButton && (
          <AddQueueItem onAddCallsign={handleAddCallsign} />
        )}
      </div>
    </section>
  )
}
