import { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import { sseService } from '../services/sse'

export interface FrequencySignalPaneProps {
  className?: string
}

interface SignalMeterProps {
  level: number
}

function SignalMeter({ level }: SignalMeterProps) {
  // Scale: 1,2,3,4,5,6,7,8,9,+10,+20,+30,+100
  const scaleLabels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '+10', '+20', '+30', '+100']
  
  // Convert level to scale position (0-12)
  const getScalePosition = (signalLevel: number): number => {
    if (signalLevel <= 9) return signalLevel - 1
    if (signalLevel <= 10) return 9
    if (signalLevel <= 20) return 10
    if (signalLevel <= 30) return 11
    return 12
  }
  
  // Get color based on signal level
  const getSignalColor = (signalLevel: number): string => {
    if (signalLevel <= 7) return '#00ff40' // bright green
    if (signalLevel <= 9) return '#ffff00' // yellow near +8
    return '#ff0000' // red for +10 and above
  }
  
  // Format signal level for display
  const formatSignalLevel = (signalLevel: number): string => {
    if (signalLevel <= 9) return `S${signalLevel}`
    return `S9 +${signalLevel - 9}`
  }
  
  const position = getScalePosition(level)
  const fillPercentage = ((position + 1) / scaleLabels.length) * 100
  
  return (
    <div className="signal-meter">
      <div className="signal-scale">
        {scaleLabels.map((label) => (
          <div key={label} className="scale-tick">
            <div className="tick-mark"></div>
            <div className="tick-label">{label}</div>
          </div>
        ))}
      </div>
      <div className="signal-bar-container">
        <div 
          className="signal-bar" 
          style={{ 
            width: `${fillPercentage}%`,
            backgroundColor: getSignalColor(level)
          }}
        ></div>
      </div>
      <div className="signal-level-display">
        <span className="level-label">LEVEL</span>
        <span className="level-value">{formatSignalLevel(level)}</span>
      </div>
    </div>
  )
}

export default function FrequencySignalPane({ className = '' }: FrequencySignalPaneProps) {
  const [frequency, setFrequency] = useState<string | null>(null)
  const [split, setSplit] = useState('')
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [signalLevel, setSignalLevel] = useState(7)
  const [systemStatus, setSystemStatus] = useState<boolean | null>(null)

  // Animation for signal level fluctuation between 7 and 20
  useEffect(() => {
    let interval: number | undefined
    
    // Only animate if system is online
    if (systemStatus === true) {
      interval = setInterval(() => {
        // Random fluctuation between 7 and 20
        const newLevel = Math.floor(Math.random() * 14) + 7 // 7-20
        setSignalLevel(newLevel)
      }, 1000) // Update every second
    } else {
      // When offline, set signal to 0
      setSignalLevel(0)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [systemStatus])  // Depend on systemStatus

  useEffect(() => {
    // Load initial frequency and split
    const loadFrequencyData = async () => {
      try {
        const [frequencyData, splitData, statusData] = await Promise.all([
          apiService.getCurrentFrequency(),
          apiService.getCurrentSplit(),
          fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/public/status`).then(r => r.json())
        ])
        
        setFrequency(frequencyData.frequency)
        setLastUpdated(frequencyData.last_updated)
        setSplit(splitData.split || '')
        setSystemStatus(statusData.active)
      } catch (error) {
        console.error('Failed to load frequency/split/status:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadFrequencyData()

    // Listen for frequency updates via SSE
    const handleFrequencyUpdate = (event: { data: any }) => {
      const frequencyData = event.data
      setFrequency(frequencyData.frequency)
      setLastUpdated(frequencyData.last_updated)
    }

    // Listen for split updates via SSE
    const handleSplitUpdate = (event: { data: any }) => {
      const splitData = event.data
      setSplit(splitData.split || '')
    }

    // Listen for system status updates via SSE
    const handleSystemStatusUpdate = (event: { data: any }) => {
      const statusData = event.data
      setSystemStatus(statusData.active)
      
      // When system goes offline, clear split to 0
      if (!statusData.active) {
        setSplit('')
      }
    }

    sseService.addEventListener('frequency_update', handleFrequencyUpdate)
    sseService.addEventListener('split_update', handleSplitUpdate)
    sseService.addEventListener('system_status', handleSystemStatusUpdate)

    // Cleanup
    return () => {
      // Note: SSE service doesn't provide removeEventListener in current implementation
      // This would need to be added if we want proper cleanup
    }
  }, [])

  // Parse frequency string to display as KHz with thousand separators
  const formatFrequency = (freq: string | null): string => {
    if (!freq) return '0,000.00'
    
    // Try to parse frequency and format as KHz
    try {
      // Remove "MHz" or "KHz" suffix if present and extract numeric value
      const numericValue = freq.replace(/\s*(MHz|KHz)\s*$/i, '').trim()
      let parsed = parseFloat(numericValue)
      
      if (isNaN(parsed)) return freq // Return original if can't parse
      
      // If the input was in MHz, convert to KHz
      if (freq.toLowerCase().includes('mhz') || parsed < 1000) {
        parsed = parsed * 1000 // Convert MHz to KHz
      }
      
      // Format as XX,XXX.XX (like 14,315.00)
      return parsed.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    } catch {
      return freq // Return original on error
    }
  }

  if (isLoading) {
    return (
      <div className={`frequency-signal-pane loading ${className}`}>
        <div className="frequency-display-large">Loading...</div>
      </div>
    )
  }

  return (
    <div className={`frequency-signal-pane ${className} ${systemStatus === false ? 'offline' : ''}`}>
      <div className="frequency-display-large">
        {formatFrequency(frequency)} KHz
        {systemStatus === false && <span className="offline-indicator">OFFLINE</span>}
      </div>
      
      {/* Split Display only - no input controls */}
      <div className="split-section">
        {split ? (
          <div className="split-display">
            SPLIT {split}
          </div>
        ) : (
          <div className="split-display no-split">
            SPLIT 0
          </div>
        )}
      </div>

      {/* Signal Meter */}
      <SignalMeter level={signalLevel} />
      
      {lastUpdated && (
        <div className="frequency-updated">
          Updated: {new Date(lastUpdated).toLocaleTimeString()}
        </div>
      )}
    </div>
  )
}