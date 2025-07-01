import { useState, useEffect } from 'react'
import { apiService } from '../services/api'
import { sseService } from '../services/sse'

export interface FrequencyDisplayProps {
  className?: string
}

export default function FrequencyDisplay({ className = '' }: FrequencyDisplayProps) {
  const [frequency, setFrequency] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Load initial frequency
    const loadFrequency = async () => {
      try {
        const data = await apiService.getCurrentFrequency()
        setFrequency(data.frequency)
        setLastUpdated(data.last_updated)
      } catch (error) {
        console.error('Failed to load frequency:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadFrequency()

    // Listen for frequency updates via SSE
    const handleFrequencyUpdate = (event: any) => {
      const frequencyData = event.data
      setFrequency(frequencyData.frequency)
      setLastUpdated(frequencyData.last_updated)
    }

    sseService.addEventListener('frequency_update', handleFrequencyUpdate)

    // Cleanup
    return () => {
      // Note: SSE service doesn't provide removeEventListener in current implementation
      // This would need to be added if we want proper cleanup
    }
  }, [])

  if (isLoading) {
    return (
      <div className={`frequency-display loading ${className}`}>
        <span className="frequency-label">Frequency:</span>
        <span className="frequency-value">Loading...</span>
      </div>
    )
  }

  return (
    <div className={`frequency-display ${className}`}>
      <span className="frequency-label">Frequency:</span>
      <span className="frequency-value">
        {frequency || 'Not set'}
      </span>
      {lastUpdated && (
        <span className="frequency-updated">
          Updated: {new Date(lastUpdated).toLocaleTimeString()}
        </span>
      )}
    </div>
  )
}