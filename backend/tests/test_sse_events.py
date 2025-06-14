"""
Tests for Server-Sent Events (SSE) functionality
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, patch
from app.services.events import EventBroadcaster, EventType


class TestEventBroadcaster:
    """Test the event broadcasting service"""
    
    @pytest.fixture
    def broadcaster(self):
        return EventBroadcaster()
    
    @pytest.mark.asyncio
    async def test_add_remove_connection(self, broadcaster):
        """Test adding and removing connections"""
        queue = asyncio.Queue()
        
        # Add connection
        await broadcaster.add_connection(queue)
        assert queue in broadcaster._connections
        assert len(broadcaster._connections) == 1
        
        # Remove connection
        await broadcaster.remove_connection(queue)
        assert queue not in broadcaster._connections
        assert len(broadcaster._connections) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_to_no_connections(self, broadcaster):
        """Test broadcasting when no connections exist"""
        # Should not raise an error
        await broadcaster.broadcast_event(EventType.CURRENT_QSO, {"test": "data"})
    
    @pytest.mark.asyncio
    async def test_broadcast_current_qso(self, broadcaster):
        """Test broadcasting current QSO events"""
        queue = asyncio.Queue()
        await broadcaster.add_connection(queue)
        
        test_qso = {
            "callsign": "TEST123",
            "timestamp": "2024-01-01T12:00:00",
            "qrz": {"name": "Test User"}
        }
        
        await broadcaster.broadcast_current_qso(test_qso)
        
        # Check that event was sent
        assert not queue.empty()
        message = await queue.get()
        
        # Verify SSE format
        assert "event: current_qso\n" in message
        assert "data: " in message
        
        # Parse the data
        data_line = [line for line in message.split('\n') if line.startswith('data: ')][0]
        event_data = json.loads(data_line[6:])  # Remove "data: " prefix
        
        assert event_data["type"] == "current_qso"
        assert event_data["data"] == test_qso
        assert "timestamp" in event_data
    
    @pytest.mark.asyncio
    async def test_broadcast_queue_update(self, broadcaster):
        """Test broadcasting queue update events"""
        queue = asyncio.Queue()
        await broadcaster.add_connection(queue)
        
        test_queue_data = {
            "queue": [{"callsign": "TEST123", "position": 1}],
            "total": 1,
            "system_active": True
        }
        
        await broadcaster.broadcast_queue_update(test_queue_data)
        
        # Check that event was sent
        assert not queue.empty()
        message = await queue.get()
        
        # Verify SSE format
        assert "event: queue_update\n" in message
        assert "data: " in message
    
    @pytest.mark.asyncio
    async def test_broadcast_system_status(self, broadcaster):
        """Test broadcasting system status events"""
        queue = asyncio.Queue()
        await broadcaster.add_connection(queue)
        
        test_status = {"active": True}
        
        await broadcaster.broadcast_system_status(test_status)
        
        # Check that event was sent
        assert not queue.empty()
        message = await queue.get()
        
        # Verify SSE format
        assert "event: system_status\n" in message
        assert "data: " in message
    
    @pytest.mark.asyncio
    async def test_multiple_connections(self, broadcaster):
        """Test broadcasting to multiple connections"""
        queue1 = asyncio.Queue()
        queue2 = asyncio.Queue()
        
        await broadcaster.add_connection(queue1)
        await broadcaster.add_connection(queue2)
        
        test_data = {"test": "message"}
        await broadcaster.broadcast_event(EventType.CURRENT_QSO, test_data)
        
        # Both queues should receive the message
        assert not queue1.empty()
        assert not queue2.empty()
        
        message1 = await queue1.get()
        message2 = await queue2.get()
        
        # Messages should be identical
        assert message1 == message2
    
    @pytest.mark.asyncio 
    async def test_connection_cleanup_on_error(self, broadcaster):
        """Test that failed connections are cleaned up"""
        # Create a mock queue that raises an exception
        mock_queue = Mock()
        mock_queue.put = Mock(side_effect=Exception("Connection failed"))
        
        await broadcaster.add_connection(mock_queue)
        assert len(broadcaster._connections) == 1
        
        # Broadcast should clean up the failed connection
        await broadcaster.broadcast_event(EventType.CURRENT_QSO, {"test": "data"})
        
        assert len(broadcaster._connections) == 0