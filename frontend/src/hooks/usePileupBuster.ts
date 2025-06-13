import { useState, useEffect, useCallback } from 'react';
import { useWebSocket, type WebSocketMessage } from './useWebSocket';
import { apiService, type QueueEntry, type CurrentQSO, type SystemStatus } from '../services/api';

export interface UsePileupBusterReturn {
  // Queue state
  queue: QueueEntry[];
  currentQSO: CurrentQSO | null;
  systemStatus: SystemStatus;
  
  // Connection state
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  registerCallsign: (callsign: string) => Promise<boolean>;
  refreshData: () => Promise<void>;
}

export function usePileupBuster(): UsePileupBusterReturn {
  const [queue, setQueue] = useState<QueueEntry[]>([]);
  const [currentQSO, setCurrentQSO] = useState<CurrentQSO | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({ active: false });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // WebSocket URL - determine if we're on localhost or production
  const getWebSocketUrl = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname === 'localhost' ? 'localhost:5000' : window.location.host;
    return `${protocol}//${host}/api/ws`;
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    console.log('Received WebSocket message:', message);

    switch (message.type) {
      case 'queue_update':
        handleQueueUpdate(message.data);
        break;
      case 'qso_update':
        handleQSOUpdate(message.data);
        break;
      case 'system_status_update':
        handleSystemStatusUpdate(message.data);
        break;
      case 'connection':
      case 'heartbeat':
        // Connection/heartbeat messages don't need special handling
        break;
      default:
        console.log('Unknown WebSocket message type:', message.type);
    }
  }, []);

  const handleQueueUpdate = (data: any) => {
    switch (data.action) {
      case 'add':
        // Add new callsign to queue
        setQueue(prev => [...prev, {
          callsign: data.callsign,
          timestamp: data.timestamp,
          position: data.position || prev.length + 1
        }]);
        break;
      case 'remove':
        // Remove callsign from queue
        setQueue(prev => prev.filter(entry => entry.callsign !== data.callsign));
        break;
      case 'clear':
        // Clear the entire queue
        setQueue([]);
        break;
      case 'next':
        // Remove the next callsign (it moved to QSO)
        setQueue(prev => prev.filter(entry => entry.callsign !== data.callsign));
        break;
      default:
        // For unknown actions, refresh the data
        refreshData();
    }
  };

  const handleQSOUpdate = (data: any) => {
    switch (data.action) {
      case 'start':
        setCurrentQSO({
          callsign: data.callsign,
          timestamp: data.timestamp,
          qrz: data.qrz
        });
        break;
      case 'end':
        setCurrentQSO(null);
        break;
      default:
        // For unknown actions, refresh the current QSO data
        refreshCurrentQSO();
    }
  };

  const handleSystemStatusUpdate = (data: any) => {
    setSystemStatus({ active: data.active });
    if (data.queue_cleared) {
      setQueue([]);
    }
  };

  // WebSocket connection
  const { isConnected } = useWebSocket({
    url: getWebSocketUrl(),
    onMessage: handleWebSocketMessage,
    onConnect: () => {
      console.log('Connected to Pileup Buster WebSocket');
      setError(null);
    },
    onDisconnect: () => {
      console.log('Disconnected from Pileup Buster WebSocket');
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket connection error');
    },
  });

  // API calls
  const refreshData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [queueResult, qsoResult, statusResult] = await Promise.all([
        apiService.getQueue(),
        apiService.getCurrentQSO(),
        apiService.getSystemStatus(),
      ]);

      if (queueResult.error) {
        throw new Error(queueResult.error);
      }
      if (qsoResult.error) {
        throw new Error(qsoResult.error);
      }
      if (statusResult.error) {
        throw new Error(statusResult.error);
      }

      if (queueResult.data) {
        setQueue(queueResult.data.queue);
        setSystemStatus({ active: queueResult.data.system_active });
      }
      if (qsoResult.data !== undefined) {
        setCurrentQSO(qsoResult.data);
      }
      if (statusResult.data) {
        setSystemStatus(statusResult.data);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load data';
      setError(errorMessage);
      console.error('Error refreshing data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshCurrentQSO = useCallback(async () => {
    const result = await apiService.getCurrentQSO();
    if (result.data !== undefined) {
      setCurrentQSO(result.data);
    }
  }, []);

  const registerCallsign = useCallback(async (callsign: string): Promise<boolean> => {
    const result = await apiService.registerCallsign(callsign.trim().toUpperCase());
    
    if (result.error) {
      setError(result.error);
      return false;
    }

    if (result.data) {
      // The WebSocket will handle updating the queue, but we can add it optimistically
      setQueue(prev => [...prev, result.data!]);
      setError(null);
      return true;
    }

    return false;
  }, []);

  // Initial data load
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  return {
    queue,
    currentQSO,
    systemStatus,
    isConnected,
    isLoading,
    error,
    registerCallsign,
    refreshData,
  };
}