import { useState, useEffect, useCallback, useRef } from 'react'
import './App.css'
import pileupBusterLogo from './assets/logo.png'
import CurrentActiveCallsign, { type CurrentActiveUser } from './components/CurrentActiveCallsign'
import WaitingQueue from './components/WaitingQueue'
import AdminLogin from './components/AdminLogin'
import AdminSection from './components/AdminSection'
import { type QueueItemData } from './components/QueueItem'
import { apiService, type CurrentQsoData, type QueueEntry, ApiError } from './services/api'
import { adminApiService } from './services/adminApi'
import { sseService, type StateChangeEvent } from './services/sse'

function App() {
  // Real data state
  const [currentQso, setCurrentQso] = useState<CurrentQsoData | null>(null)
  const [queueData, setQueueData] = useState<QueueItemData[]>([])
  const [queueTotal, setQueueTotal] = useState(0)
  const [queueMaxSize, setQueueMaxSize] = useState(4)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Admin state
  const [isAdminLoggedIn, setIsAdminLoggedIn] = useState(false)
  const [systemStatus, setSystemStatus] = useState<boolean | null>(null)

  // Ref to track previous callsign for clipboard functionality
  const previousCallsignRef = useRef<string | null>(null)

  // Utility function to copy text to clipboard
  const copyToClipboard = async (text: string): Promise<void> => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        // Use modern Clipboard API if available
        await navigator.clipboard.writeText(text)
        console.log(`Copied callsign to clipboard: ${text}`)
      } else {
        // Fallback for older browsers or insecure contexts
        const textArea = document.createElement('textarea')
        textArea.value = text
        textArea.style.position = 'fixed'
        textArea.style.left = '-999999px'
        textArea.style.top = '-999999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()
        
        try {
          document.execCommand('copy')
          console.log(`Copied callsign to clipboard (fallback): ${text}`)
        } catch (err) {
          console.warn('Failed to copy callsign to clipboard:', err)
        } finally {
          document.body.removeChild(textArea)
        }
      }
    } catch (err) {
      console.warn('Failed to copy callsign to clipboard:', err)
    }
  }

  // Convert QueueEntry to QueueItemData format
  const convertQueueEntryToItemData = (entry: QueueEntry): QueueItemData => {
    return {
      callsign: entry.callsign,
      location: entry.qrz?.dxcc_name || entry.qrz?.address || 'Location not available',
      qrz: entry.qrz
    }
  }

  // Convert CurrentQsoData to CurrentActiveUser format
  const convertCurrentQsoToActiveUser = (qso: CurrentQsoData): CurrentActiveUser => {
    return {
      callsign: qso.callsign,
      name: qso.qrz?.name || 'Name not available',
      location: qso.qrz?.dxcc_name || qso.qrz?.address || 'Location not available'
    }
  }

  // Fetch current QSO data
  const fetchCurrentQso = useCallback(async () => {
    try {
      const data = await apiService.getCurrentQso()
      setCurrentQso(data)
      // Update ref for initial load (don't copy to clipboard on initial load)
      previousCallsignRef.current = data?.callsign || null
    } catch (err) {
      if (err instanceof ApiError) {
        console.error('Failed to fetch current QSO:', err.detail || err.message)
        setError(err.detail || err.message)
      } else {
        console.error('Failed to fetch current QSO:', err)
        setError('Failed to load current QSO')
      }
    }
  }, [])

  // Fetch queue list
  const fetchQueueList = useCallback(async () => {
    try {
      const response = await apiService.getQueueList()
      const queueItems = response.queue.map(convertQueueEntryToItemData)
      setQueueData(queueItems)
      setQueueTotal(response.total)
      setQueueMaxSize(response.max_size)
    } catch (err) {
      if (err instanceof ApiError) {
        console.error('Failed to fetch queue list:', err.detail || err.message)
        setError(err.detail || err.message)
      } else {
        console.error('Failed to fetch queue list:', err)
        setError('Failed to load queue')
      }
    }
  }, [])

  // Load admin system status
  const loadSystemStatus = async () => {
    try {
      const status = await adminApiService.getSystemStatus()
      setSystemStatus(status)
    } catch (error) {
      console.error('Failed to load system status:', error)
      // Set default status if can't load
      setSystemStatus(false)
    }
  }

  // Initial data load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError(null)
      
      await Promise.all([
        fetchCurrentQso(),
        fetchQueueList()
      ])
      
      setLoading(false)
    }

    loadData()
  }, [fetchCurrentQso, fetchQueueList])

  // Admin initialization
  useEffect(() => {
    // Check if admin is already logged in
    setIsAdminLoggedIn(adminApiService.isLoggedIn())
    
    // Load initial system status
    loadSystemStatus()
  }, [])

  // Real-time updates via Server-Sent Events (SSE)
  useEffect(() => {
    // Event handlers for different types of state changes
    const handleCurrentQsoEvent = (event: StateChangeEvent) => {
      console.log('Received current_qso event:', event)
      const newQso = event.data
      const previousCallsign = previousCallsignRef.current
      const newCallsign = newQso?.callsign
      
      // Copy callsign to clipboard when a new callsign becomes active
      if (newCallsign && newCallsign !== previousCallsign) {
        copyToClipboard(newCallsign)
      }
      
      // Update the ref with the new callsign
      previousCallsignRef.current = newCallsign || null
      
      setCurrentQso(newQso)
    }

    const handleQueueUpdateEvent = (event: StateChangeEvent) => {
      console.log('Received queue_update event:', event)
      if (event.data?.queue) {
        const queueItems = event.data.queue.map(convertQueueEntryToItemData)
        setQueueData(queueItems)
        if (event.data.total !== undefined) {
          setQueueTotal(event.data.total)
        }
        if (event.data.max_size !== undefined) {
          setQueueMaxSize(event.data.max_size)
        }
      }
    }

    const handleSystemStatusEvent = (event: StateChangeEvent) => {
      console.log('Received system_status event:', event)
      if (event.data?.active !== undefined) {
        setSystemStatus(event.data.active)
        
        // Clear error state when system is activated
        if (event.data.active) {
          setError(null)
        }
      }
    }

    const handleConnectedEvent = (event: StateChangeEvent) => {
      console.log('SSE connected:', event)
      // When SSE connects, fetch initial data
      Promise.all([
        fetchCurrentQso(),
        fetchQueueList()
      ]).catch(err => {
        console.error('Failed to fetch initial data after SSE connection:', err)
      })
    }

    // Register event listeners
    sseService.addEventListener('current_qso', handleCurrentQsoEvent)
    sseService.addEventListener('queue_update', handleQueueUpdateEvent)
    sseService.addEventListener('system_status', handleSystemStatusEvent)
    sseService.addEventListener('connected', handleConnectedEvent)

    // Start SSE connection
    sseService.connect()

    // Fallback polling in case SSE fails (every 30 seconds)
    const fallbackInterval = setInterval(() => {
      if (!sseService.isConnected()) {
        console.log('SSE not connected, using fallback polling')
        fetchCurrentQso()
        fetchQueueList()
      }
    }, 30000) // Fallback poll every 30 seconds

    // Cleanup on component unmount
    return () => {
      sseService.removeEventListener('current_qso', handleCurrentQsoEvent)
      sseService.removeEventListener('queue_update', handleQueueUpdateEvent)
      sseService.removeEventListener('system_status', handleSystemStatusEvent)
      sseService.removeEventListener('connected', handleConnectedEvent)
      sseService.disconnect()
      clearInterval(fallbackInterval)
    }
  }, [fetchCurrentQso, fetchQueueList])

  // Handle callsign registration
  const handleCallsignRegistration = async (callsign: string) => {
    try {
      await apiService.registerCallsign(callsign)
      // No need to manually refresh - SSE will broadcast the queue update
    } catch (err) {
      if (err instanceof ApiError) {
        console.error('Failed to register callsign:', err.detail || err.message)
        // You might want to show a user-visible error here
        throw new Error(err.detail || err.message)
      } else {
        console.error('Failed to register callsign:', err)
        throw new Error('Failed to register callsign')
      }
    }
  }

  // Admin handlers
  const handleAdminLogin = async (username: string, password: string): Promise<boolean> => {
    const success = await adminApiService.login(username, password)
    if (success) {
      setIsAdminLoggedIn(true)
      // Reload system status after login
      await loadSystemStatus()
    }
    return success
  }

  const handleAdminLogout = () => {
    adminApiService.logout()
    setIsAdminLoggedIn(false)
  }

  const handleToggleSystemStatus = async (active: boolean): Promise<boolean> => {
    try {
      await adminApiService.setSystemStatus(active)
      // SSE will handle the system status update
      // No need to manually refresh data - SSE events will handle this
      
      return true
    } catch (error) {
      console.error('Failed to toggle system status:', error)
      return false
    }
  }

  const handleWorkNextUser = async (): Promise<void> => {
    await adminApiService.workNextUser()
    // No need to manually refresh - SSE will broadcast the updates
  }

  const handleCompleteCurrentQso = async (): Promise<void> => {
    await adminApiService.completeCurrentQso()
    // No need to manually refresh - SSE will broadcast the updates
  }

  return (
    <div className="pileup-buster-app">
      {/* Header */}
      <header className="header">
        <img 
          src={pileupBusterLogo} 
          alt="Pileup Buster Logo" 
          className="logo"
        />
        <AdminLogin 
          onLogin={handleAdminLogin}
          isLoggedIn={isAdminLoggedIn}
          onLogout={handleAdminLogout}
        />
      </header>

      <main className="main-content">
        {loading && <div>Loading...</div>}
        
        {/* Show system status info instead of red error when system is inactive */}
        {systemStatus === false && (
          <div style={{ 
            color: '#ff6600', 
            backgroundColor: '#fff3cd', 
            border: '1px solid #ffeaa7',
            padding: '10px',
            borderRadius: '4px',
            margin: '10px 0'
          }}>
            ⚠️ System is currently inactive. Registration and queue access are disabled.
          </div>
        )}
        
        {/* Show errors only if they're not system inactive related */}
        {error && systemStatus !== false && (
          <div style={{ color: 'red' }}>Error: {error}</div>
        )}
        
        {/* Current Active Callsign (Green Border) */}
        <CurrentActiveCallsign 
          activeUser={currentQso ? convertCurrentQsoToActiveUser(currentQso) : null}
          qrzData={currentQso?.qrz}
        />

        {/* Waiting Queue Container (Red Border) */}
        <WaitingQueue 
          queueData={queueData} 
          queueTotal={queueTotal}
          queueMaxSize={queueMaxSize}
          onAddCallsign={handleCallsignRegistration}
          systemActive={systemStatus === true}
        />

        {/* Admin Section - Only visible when logged in */}
        <AdminSection 
          isLoggedIn={isAdminLoggedIn}
          onToggleSystemStatus={handleToggleSystemStatus}
          onWorkNextUser={handleWorkNextUser}
          onCompleteCurrentQso={handleCompleteCurrentQso}
          systemStatus={systemStatus}
        />
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <a 
            href="https://github.com/brianbruff/pileup-buster" 
            target="_blank" 
            rel="noopener noreferrer"
            className="github-link"
          >
            View on GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}

export default App
