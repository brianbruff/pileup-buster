"""
Test cases for chat functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.app import create_app
from app.services.events import event_broadcaster


@pytest.fixture
def test_app():
    """Create a test FastAPI application"""
    return create_app()


@pytest.fixture  
def client(test_app):
    """Create a test client"""
    return TestClient(test_app)


class TestChatEndpoints:
    """Test chat API endpoints"""
    
    def test_get_chat_rooms_endpoint_exists(self, client):
        """Test that chat rooms endpoint exists"""
        # Test without MongoDB connection - should return 500 but endpoint exists
        response = client.get("/api/chat/rooms")
        # Endpoint exists even if database is not available
        assert response.status_code in [200, 500]
    
    def test_send_message_endpoint_exists(self, client):
        """Test that send message endpoint exists"""
        message_data = {
            "callsign": "W1AW",
            "message": "Test message",
            "room_name": "general"
        }
        response = client.post("/api/chat/messages", json=message_data)
        # Endpoint exists even if database is not available
        assert response.status_code in [200, 400, 500]
    
    def test_invalid_callsign_format(self, client):
        """Test that invalid callsign formats are rejected"""
        message_data = {
            "callsign": "INVALID123TOOLONG",
            "message": "Test message", 
            "room_name": "general"
        }
        response = client.post("/api/chat/messages", json=message_data)
        assert response.status_code == 422  # Validation error
    
    def test_empty_message_rejected(self, client):
        """Test that empty messages are rejected"""
        message_data = {
            "callsign": "W1AW",
            "message": "",
            "room_name": "general"
        }
        response = client.post("/api/chat/messages", json=message_data)
        assert response.status_code == 422  # Validation error
    
    def test_message_too_long_rejected(self, client):
        """Test that messages over 500 characters are rejected"""
        message_data = {
            "callsign": "W1AW",
            "message": "x" * 501,  # Too long
            "room_name": "general"
        }
        response = client.post("/api/chat/messages", json=message_data)
        assert response.status_code == 422  # Validation error

    def test_create_room_requires_auth(self, client):
        """Test that creating rooms requires admin authentication"""
        room_data = {
            "name": "test-room",
            "description": "Test room"
        }
        response = client.post("/api/chat/rooms", json=room_data)
        assert response.status_code == 401  # Unauthorized


class TestChatValidation:
    """Test chat input validation"""
    
    def test_callsign_validation(self):
        """Test callsign validation logic"""
        from app.routes.chat import ChatMessage
        from pydantic import ValidationError
        
        # Valid callsigns should work
        valid_message = ChatMessage(callsign="W1AW", message="Test", room_name="general")
        assert valid_message.callsign == "W1AW"
        
        # Invalid callsigns should raise validation error
        with pytest.raises(ValidationError):
            ChatMessage(callsign="INVALID", message="Test", room_name="general")
    
    def test_room_name_validation(self):
        """Test room name validation"""
        from app.routes.chat import ChatMessage
        from pydantic import ValidationError
        
        # Valid room names
        valid_message = ChatMessage(callsign="W1AW", message="Test", room_name="general")
        assert valid_message.room_name == "general"
        
        valid_message = ChatMessage(callsign="W1AW", message="Test", room_name="test-room_123")
        assert valid_message.room_name == "test-room_123"
        
        # Invalid room names should raise validation error
        with pytest.raises(ValidationError):
            ChatMessage(callsign="W1AW", message="Test", room_name="room with spaces")


@pytest.mark.asyncio
class TestChatEvents:
    """Test chat event broadcasting"""
    
    async def test_chat_event_types_exist(self):
        """Test that chat event types are defined"""
        from app.services.events import EventType
        
        assert EventType.CHAT_MESSAGE == "chat_message"
        assert EventType.CHAT_ROOM_UPDATE == "chat_room_update"
    
    async def test_chat_message_broadcast(self):
        """Test chat message event broadcasting"""
        # Mock the broadcaster connections
        mock_queue = AsyncMock()
        event_broadcaster._connections = {mock_queue}
        
        test_message = {
            "room_name": "general",
            "callsign": "W1AW", 
            "message": "Test message",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        await event_broadcaster.broadcast_chat_message(test_message)
        
        # Verify message was queued
        mock_queue.put.assert_called_once()
        call_args = mock_queue.put.call_args[0][0]
        assert "chat_message" in call_args
        assert "W1AW" in call_args


class TestChatIntegration:
    """Test chat integration with existing system"""
    
    def test_chat_routes_included_in_app(self, test_app):
        """Test that chat routes are included in the main app"""
        # Check that chat routes are registered
        route_paths = [route.path for route in test_app.routes]
        
        # Should have chat endpoints
        assert any("/api/chat" in path for path in route_paths)
    
    def test_sse_supports_chat_events(self):
        """Test that SSE service supports chat events"""
        from app.services.events import EventType
        
        # Chat events should be defined
        assert hasattr(EventType, 'CHAT_MESSAGE')
        assert hasattr(EventType, 'CHAT_ROOM_UPDATE')