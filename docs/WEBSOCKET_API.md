# WebSocket API Documentation

## Overview

The Pileup Buster application includes a real-time WebSocket notification system that provides instant updates to the frontend when database changes occur. This eliminates the need for polling and provides a better user experience with immediate feedback.

## WebSocket Endpoint

**URL:** `ws://localhost:5000/api/ws` (development) or `wss://yourhost.com/api/ws` (production)

## Connection

To connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:5000/api/ws');

ws.onopen = () => {
  console.log('Connected to Pileup Buster WebSocket');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

## Message Format

All WebSocket messages follow this JSON structure:

```json
{
  "type": "message_type",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "data": {
    // Message-specific data
  }
}
```

## Message Types

### Connection Messages

#### Connection Confirmation
Sent when a client successfully connects.

```json
{
  "type": "connection",
  "status": "connected",
  "message": "Connected to Pileup Buster notifications"
}
```

#### Heartbeat Response
Sent in response to client heartbeat messages.

```json
{
  "type": "heartbeat",
  "status": "ok"
}
```

### Queue Update Messages

#### Queue Add Event
Sent when a new callsign is added to the queue.

```json
{
  "type": "queue_update",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "data": {
    "action": "add",
    "callsign": "N0CALL",
    "timestamp": "2025-01-01T12:00:00.000Z",
    "position": 3
  }
}
```

#### Queue Remove Event
Sent when a callsign is removed from the queue.

```json
{
  "type": "queue_update",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "data": {
    "action": "remove",
    "callsign": "N0CALL",
    "timestamp": "2025-01-01T12:00:00.000Z",
    "position": 2
  }
}
```

#### Queue Clear Event
Sent when the entire queue is cleared.

```json
{
  "type": "queue_update",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "data": {
    "action": "clear",
    "cleared_count": 4
  }
}
```

#### Queue Next Event
Sent when the next callsign is processed (moved from queue to QSO).

```json
{
  "type": "queue_update",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "data": {
    "action": "next",
    "callsign": "N0CALL",
    "timestamp": "2025-01-01T12:00:00.000Z",
    "position": 1
  }
}
```

### QSO Update Messages

#### QSO Start Event
Sent when a new QSO begins.

```json
{
  "type": "qso_update",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "data": {
    "action": "start",
    "callsign": "N0CALL",
    "timestamp": "2025-01-01T12:00:00.000Z"
  }
}
```

#### QSO End Event
Sent when a QSO ends.

```json
{
  "type": "qso_update",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "data": {
    "action": "end",
    "callsign": "N0CALL",
    "timestamp": "2025-01-01T12:00:00.000Z"
  }
}
```

### System Status Update Messages

#### System Status Change Event
Sent when the system is activated or deactivated.

```json
{
  "type": "system_status_update",
  "timestamp": "2025-01-01T12:00:00.000Z",
  "data": {
    "active": true,
    "updated_by": "admin",
    "queue_cleared": true,
    "cleared_count": 2
  }
}
```

## Client Implementation

### React Hook Example

The application includes a custom React hook for easy WebSocket integration:

```typescript
import { usePileupBuster } from './hooks/usePileupBuster';

function MyComponent() {
  const {
    queue,
    currentQSO,
    systemStatus,
    isConnected,
    error,
    registerCallsign,
  } = usePileupBuster();

  // Use the real-time data in your component
  return (
    <div>
      <div>Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
      <div>Queue size: {queue.length}</div>
      <div>Current QSO: {currentQSO?.callsign || 'None'}</div>
    </div>
  );
}
```

### Manual WebSocket Implementation

```javascript
class PileupBusterClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.reconnectInterval = 3000;
    this.maxReconnectAttempts = 10;
    this.reconnectAttempts = 0;
  }

  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      console.log('Connected to Pileup Buster');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.ws.onclose = () => {
      console.log('Disconnected from Pileup Buster');
      this.stopHeartbeat();
      this.reconnect();
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  handleMessage(message) {
    switch (message.type) {
      case 'queue_update':
        this.onQueueUpdate(message.data);
        break;
      case 'qso_update':
        this.onQSOUpdate(message.data);
        break;
      case 'system_status_update':
        this.onSystemStatusUpdate(message.data);
        break;
    }
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, this.reconnectInterval);
    }
  }

  // Override these methods to handle events
  onQueueUpdate(data) {}
  onQSOUpdate(data) {}
  onSystemStatusUpdate(data) {}
}
```

## Security Considerations

- WebSocket connections are not authenticated in the current implementation
- Consider adding authentication tokens for production deployments
- Use WSS (WebSocket Secure) for production HTTPS sites
- Implement rate limiting to prevent abuse

## Error Handling

- The client should implement automatic reconnection logic
- Handle connection failures gracefully
- Provide user feedback when disconnected
- Fall back to polling if WebSocket connection fails repeatedly

## Testing

### Manual Testing with Browser Console

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:5000/api/ws');

// Log all messages
ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};

// Send heartbeat
ws.send(JSON.stringify({ type: 'heartbeat' }));
```

### Testing with curl (for WebSocket handshake)

```bash
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" \
  -H "Sec-WebSocket-Version: 13" \
  http://localhost:5000/api/ws
```

## Performance Notes

- WebSocket connections are lightweight for real-time updates
- Each connection uses minimal server resources
- Messages are sent only when database changes occur
- Heartbeat messages help detect dead connections
- Automatic reconnection prevents permanent disconnections