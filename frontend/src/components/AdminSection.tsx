import { useState } from 'react'

export interface AdminSectionProps {
  isLoggedIn: boolean
  onToggleSystemStatus: (active: boolean) => Promise<boolean>
  onWorkNextUser: () => Promise<void>
  onCompleteCurrentQso: () => Promise<void>
  onSetFrequency: (frequency: string) => Promise<void>
  systemStatus: boolean | null
}

export default function AdminSection({ 
  isLoggedIn, 
  onToggleSystemStatus, 
  onWorkNextUser,
  onCompleteCurrentQso,
  onSetFrequency,
  systemStatus 
}: AdminSectionProps) {
  const [isTogglingStatus, setIsTogglingStatus] = useState(false)
  const [isWorkingNext, setIsWorkingNext] = useState(false)
  const [isCompletingQso, setIsCompletingQso] = useState(false)
  const [frequency, setFrequency] = useState('')
  const [isSettingFrequency, setIsSettingFrequency] = useState(false)

  if (!isLoggedIn) {
    return null
  }

  const handleToggleStatus = async () => {
    if (systemStatus === null) return
    
    setIsTogglingStatus(true)
    try {
      await onToggleSystemStatus(!systemStatus)
    } catch (error) {
      console.error('Failed to toggle system status:', error)
    } finally {
      setIsTogglingStatus(false)
    }
  }

  const handleWorkNext = async () => {
    setIsWorkingNext(true)
    try {
      await onWorkNextUser()
    } catch (error) {
      console.error('Failed to work next user:', error)
    } finally {
      setIsWorkingNext(false)
    }
  }

  const handleCompleteQso = async () => {
    setIsCompletingQso(true)
    try {
      await onCompleteCurrentQso()
    } catch (error) {
      console.error('Failed to complete current QSO:', error)
    } finally {
      setIsCompletingQso(false)
    }
  }

  const handleSetFrequency = async () => {
    if (!frequency.trim()) return
    
    setIsSettingFrequency(true)
    try {
      await onSetFrequency(frequency.trim())
      setFrequency('') // Clear input after successful set
    } catch (error) {
      console.error('Failed to set frequency:', error)
    } finally {
      setIsSettingFrequency(false)
    }
  }

  return (
    <section className="admin-section">
      <h2 className="admin-title">Admin Controls</h2>
      <div className="admin-controls">
        <div className="button-group">
          <div className="queue-control">
            <button
              className="work-next-button"
              onClick={handleWorkNext}
              disabled={isWorkingNext || !systemStatus}
              type="button"
            >
              {isWorkingNext ? 'Working...' : 'Work Next User in Queue'}
            </button>
          </div>

          <div className="queue-control complete-control">
            <button
              className="complete-qso-button"
              onClick={handleCompleteQso}
              disabled={isCompletingQso || !systemStatus}
              type="button"
            >
              {isCompletingQso ? 'Completing...' : 'Complete Current QSO'}
            </button>
          </div>
        </div>


        <div className="system-status-control">
          <label className="status-toggle-label">
            <span className="status-label">System Status:</span>
            <div className="toggle-container">
              <button
                className={`toggle-button ${systemStatus ? 'active' : 'inactive'}`}
                onClick={handleToggleStatus}
                disabled={isTogglingStatus || systemStatus === null}
                type="button"
              >
                <div className="toggle-slider">
                  <div className="toggle-knob"></div>
                </div>
                <span className="toggle-text">
                  {systemStatus === null ? 'Loading...' : systemStatus ? 'ACTIVE' : 'INACTIVE'}
                </span>
              </button>
            </div>
          </label>
        </div>

        <div className="frequency-control">
          <label className="frequency-label">
            <span className="frequency-label-text">Set Frequency:</span>
            <div className="frequency-input-group">
              <input
                type="text"
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
                placeholder="e.g., 146.520 MHz"
                className="frequency-input"
                disabled={isSettingFrequency}
              />
              <button
                className="frequency-button"
                onClick={handleSetFrequency}
                disabled={isSettingFrequency || !frequency.trim()}
                type="button"
              >
                {isSettingFrequency ? 'Setting...' : 'Set'}
              </button>
            </div>
          </label>
        </div>

        
      </div>
    </section>
  )
}