import './App.css'
import CurrentActiveCallsign, { type CurrentActiveUser } from './components/CurrentActiveCallsign'
import WaitingQueue from './components/WaitingQueue'
import { type QueueItemData } from './components/QueueItem'
import { usePileupBuster } from './hooks/usePileupBuster'

function App() {
  const {
    queue,
    currentQSO,
    systemStatus,
    isConnected,
    isLoading,
    error,
    registerCallsign,
  } = usePileupBuster();

  // Convert queue entries to QueueItemData format
  const queueData: QueueItemData[] = queue.map(entry => ({
    callsign: entry.callsign,
    location: `Position ${entry.position}`, // We'll enhance this with QRZ data later
  }));

  // Convert currentQSO to CurrentActiveUser format
  const currentActiveUser: CurrentActiveUser | null = currentQSO ? {
    callsign: currentQSO.callsign,
    name: currentQSO.qrz?.name || 'Unknown',
    location: currentQSO.qrz?.location || 'Unknown location',
  } : null;

  if (isLoading) {
    return (
      <div className="pileup-buster-app">
        <header className="header">
          <div className="hamburger-menu">
            <div className="hamburger-line"></div>
            <div className="hamburger-line"></div>
            <div className="hamburger-line"></div>
          </div>
          <h1 className="title">PILEUP BUSTER</h1>
        </header>
        <main className="main-content">
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            Loading...
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="pileup-buster-app">
      {/* Header */}
      <header className="header">
        <div className="hamburger-menu">
          <div className="hamburger-line"></div>
          <div className="hamburger-line"></div>
          <div className="hamburger-line"></div>
        </div>
        <h1 className="title">PILEUP BUSTER</h1>
        <div style={{ 
          position: 'absolute', 
          right: '1rem', 
          top: '50%', 
          transform: 'translateY(-50%)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.875rem'
        }}>
          <div style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            backgroundColor: isConnected ? '#10b981' : '#ef4444' 
          }}></div>
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      <main className="main-content">
        {error && (
          <div style={{ 
            backgroundColor: '#fee2e2', 
            color: '#dc2626', 
            padding: '1rem', 
            borderRadius: '0.5rem', 
            margin: '1rem 0',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}

        {!systemStatus.active && (
          <div style={{ 
            backgroundColor: '#fef3c7', 
            color: '#d97706', 
            padding: '1rem', 
            borderRadius: '0.5rem', 
            margin: '1rem 0',
            textAlign: 'center'
          }}>
            System is currently inactive. Queue registration is not available.
          </div>
        )}

        {/* Current Active Callsign (Green Border) */}
        {currentActiveUser ? (
          <CurrentActiveCallsign activeUser={currentActiveUser} />
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '2rem',
            color: '#6b7280' 
          }}>
            No active QSO
          </div>
        )}

        {/* Waiting Queue Container (Red Border) */}
        <WaitingQueue 
          queueData={queueData} 
          onAddCallsign={registerCallsign}
          systemActive={systemStatus.active}
        />
      </main>
    </div>
  )
}

export default App
