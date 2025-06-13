"""Test WebSocket functionality"""
import pytest
import asyncio
from app.websocket_manager import WebSocketManager
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_websocket_manager_basic_functionality():
    """Test basic WebSocket manager functionality"""
    manager = WebSocketManager()
    
    # Mock WebSocket connection
    mock_websocket = AsyncMock()
    
    # Test connection
    await manager.connect(mock_websocket)
    assert len(manager.active_connections) == 1
    assert mock_websocket in manager.active_connections
    
    # Test broadcasting
    test_message = {"type": "test", "data": {"message": "hello"}}
    await manager.broadcast(test_message)
    
    # Verify websocket.send_text was called
    mock_websocket.send_text.assert_called_once()
    
    # Test disconnection
    manager.disconnect(mock_websocket)
    assert len(manager.active_connections) == 0


def test_websocket_manager_event_message_creation():
    """Test event message creation"""
    manager = WebSocketManager()
    
    message = manager.create_event_message("test_event", {"key": "value"})
    
    assert message["type"] == "test_event"
    assert message["data"]["key"] == "value"
    assert "timestamp" in message


def test_websocket_manager_queue_events():
    """Test queue event broadcasting"""
    manager = WebSocketManager()
    manager.broadcast_sync = MagicMock()  # Mock the sync broadcast method
    
    # Test queue add event
    manager.broadcast_queue_update("add", "N0CALL", {"position": 1})
    manager.broadcast_sync.assert_called_once()
    
    call_args = manager.broadcast_sync.call_args[0][0]
    assert call_args["type"] == "queue_update"
    assert call_args["data"]["action"] == "add"
    assert call_args["data"]["callsign"] == "N0CALL"


def test_websocket_manager_qso_events():
    """Test QSO event broadcasting"""
    manager = WebSocketManager()
    manager.broadcast_sync = MagicMock()  # Mock the sync broadcast method
    
    # Test QSO start event
    manager.broadcast_qso_update("start", "N0CALL", {"timestamp": "2025-01-01T00:00:00"})
    manager.broadcast_sync.assert_called_once()
    
    call_args = manager.broadcast_sync.call_args[0][0]
    assert call_args["type"] == "qso_update"
    assert call_args["data"]["action"] == "start"
    assert call_args["data"]["callsign"] == "N0CALL"


def test_websocket_manager_system_status_events():
    """Test system status event broadcasting"""
    manager = WebSocketManager()
    manager.broadcast_sync = MagicMock()  # Mock the sync broadcast method
    
    # Test system status change event
    manager.broadcast_system_status_update(True, "admin", {"queue_cleared": True})
    manager.broadcast_sync.assert_called_once()
    
    call_args = manager.broadcast_sync.call_args[0][0]
    assert call_args["type"] == "system_status_update"
    assert call_args["data"]["active"] is True
    assert call_args["data"]["updated_by"] == "admin"
    assert call_args["data"]["queue_cleared"] is True