"""Tests for frequency management functionality"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from app.database import QueueDatabase
from app.routes.admin import FrequencyRequest
from app.services.events import EventType, event_broadcaster


class TestFrequencyDatabase:
    """Test frequency storage in database"""
    
    def test_get_frequency_none_exists(self):
        """Test getting frequency when none exists"""
        db = QueueDatabase()
        db.status_collection = MagicMock()
        db.status_collection.find_one.return_value = None
        
        result = db.get_frequency()
        assert result is None
        db.status_collection.find_one.assert_called_once_with({"_id": "frequency"})
    
    def test_get_frequency_exists(self):
        """Test getting frequency when it exists"""
        db = QueueDatabase()
        db.status_collection = MagicMock()
        
        mock_doc = {
            "_id": "frequency",
            "frequency": "146.520 MHz",
            "last_updated": "2024-01-01T12:00:00",
            "updated_by": "admin"
        }
        db.status_collection.find_one.return_value = mock_doc
        
        result = db.get_frequency()
        assert result == {
            "frequency": "146.520 MHz",
            "last_updated": "2024-01-01T12:00:00",
            "updated_by": "admin"
        }
        db.status_collection.find_one.assert_called_once_with({"_id": "frequency"})
    
    def test_set_frequency(self):
        """Test setting frequency"""
        db = QueueDatabase()
        db.status_collection = MagicMock()
        
        result = db.set_frequency("146.520 MHz", "test-admin")
        
        assert result["frequency"] == "146.520 MHz"
        assert result["updated_by"] == "test-admin"
        assert "last_updated" in result
        
        # Verify database call
        db.status_collection.replace_one.assert_called_once()
        call_args = db.status_collection.replace_one.call_args
        assert call_args[0][0] == {"_id": "frequency"}
        assert call_args[0][1]["frequency"] == "146.520 MHz"
        assert call_args[0][1]["updated_by"] == "test-admin"
        assert call_args[1]["upsert"] is True
    
    def test_set_frequency_default_user(self):
        """Test setting frequency with default user"""
        db = QueueDatabase()
        db.status_collection = MagicMock()
        
        result = db.set_frequency("146.520 MHz")
        
        assert result["frequency"] == "146.520 MHz"
        assert result["updated_by"] == "admin"
    
    def test_database_connection_not_available(self):
        """Test frequency operations when database is not available"""
        db = QueueDatabase()
        db.status_collection = None
        
        with pytest.raises(Exception, match="Database connection not available"):
            db.get_frequency()
        
        with pytest.raises(Exception, match="Database connection not available"):
            db.set_frequency("146.520 MHz")


class TestFrequencyEvents:
    """Test frequency event broadcasting"""
    
    @pytest.mark.asyncio
    async def test_broadcast_frequency_update(self):
        """Test broadcasting frequency update events"""
        # Mock the event broadcaster's broadcast_event method
        event_broadcaster.broadcast_event = AsyncMock()
        
        test_frequency_data = {
            "frequency": "146.520 MHz",
            "last_updated": "2024-01-01T12:00:00",
            "updated_by": "admin"
        }
        
        await event_broadcaster.broadcast_frequency_update(test_frequency_data)
        
        event_broadcaster.broadcast_event.assert_called_once_with(
            EventType.FREQUENCY_UPDATE, 
            test_frequency_data
        )
    
    def test_frequency_event_type_exists(self):
        """Test that FREQUENCY_UPDATE event type exists"""
        assert hasattr(EventType, 'FREQUENCY_UPDATE')
        assert EventType.FREQUENCY_UPDATE == "frequency_update"


class TestFrequencyRequest:
    """Test frequency request model"""
    
    def test_frequency_request_valid(self):
        """Test valid frequency request"""
        request = FrequencyRequest(frequency="146.520 MHz")
        assert request.frequency == "146.520 MHz"
    
    def test_frequency_request_empty_string(self):
        """Test frequency request with empty string"""
        request = FrequencyRequest(frequency="")
        assert request.frequency == ""
    
    def test_frequency_request_whitespace(self):
        """Test frequency request with whitespace"""
        request = FrequencyRequest(frequency="  146.520 MHz  ")
        assert request.frequency == "  146.520 MHz  "