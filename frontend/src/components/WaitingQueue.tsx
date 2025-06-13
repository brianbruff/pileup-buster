import QueueItem from './QueueItem'
import AddQueueItem from './AddQueueItem'
import type { QueueItemData } from './QueueItem'

export interface WaitingQueueProps {
  queueData: QueueItemData[]
  onAddCallsign: (callsign: string) => Promise<boolean>
  systemActive: boolean
}

export default function WaitingQueue({ queueData, onAddCallsign, systemActive }: WaitingQueueProps) {
  const handleAddCallsign = async (callsign: string): Promise<boolean> => {
    const success = await onAddCallsign(callsign);
    if (success) {
      console.log('Successfully added callsign:', callsign);
    } else {
      console.error('Failed to add callsign:', callsign);
    }
    return success;
  }

  const showAddButton = queueData.length < 4 && systemActive

  return (
    <section className="queue-section">
      <h2 className="queue-title">Waiting Queue</h2>
      <div className="queue-container">
        {queueData.map((item, index) => (
          <QueueItem key={item.callsign} item={item} index={index} />
        ))}
        {showAddButton && (
          <AddQueueItem onAddCallsign={handleAddCallsign} />
        )}
      </div>
    </section>
  )
}
