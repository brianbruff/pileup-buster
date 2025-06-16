import QueueItem from './QueueItem'
import AddQueueItem from './AddQueueItem'
import type { QueueItemData } from './QueueItem'

export interface WaitingQueueProps {
  queueData: QueueItemData[]
  queueTotal: number
  queueMaxSize: number
  onAddCallsign: (callsign: string) => Promise<void>
  systemActive?: boolean
  isAdmin?: boolean
  onDeleteCallsign?: (callsign: string) => Promise<void>
}

export default function WaitingQueue({ 
  queueData, 
  queueTotal, 
  queueMaxSize, 
  onAddCallsign, 
  systemActive = true,
  isAdmin = false,
  onDeleteCallsign
}: WaitingQueueProps) {
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

  const isQueueFull = queueTotal >= queueMaxSize
  const showAddButton = !isQueueFull && systemActive

  return (
    <section className="queue-section">
      <h2 className="queue-title">
        Waiting Queue ({queueTotal}/{queueMaxSize})
      </h2>
      
      {/* Queue status messaging */}
      {isQueueFull && systemActive && (
        <div style={{
          backgroundColor: '#fff3cd',
          border: '1px solid #ffeaa7',
          borderRadius: '4px',
          padding: '10px',
          margin: '10px 0',
          color: '#856404',
          textAlign: 'center'
        }}>
          ⚠️ Queue is currently full ({queueTotal}/{queueMaxSize}). Please wait for a spot to open up and try again.
        </div>
      )}
      
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
