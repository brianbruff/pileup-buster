"""
Test queue size display functionality
"""
import pytest
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.app import create_app
from app.database import QueueDatabase


@pytest.fixture
def mock_database():
    """Create a mock database for testing"""
    mock_db = Mock(spec=QueueDatabase)
    return mock_db


@pytest.fixture
def test_client(mock_database):
    """Create a test client with mocked database"""
    app = create_app()
    
    # Patch the database instance in queue routes
    with patch('app.routes.queue.queue_db', mock_database):
        with TestClient(app) as client:
            yield client, mock_database


class TestQueueSizeDisplay:
    """Test cases for queue size display functionality"""
    
    def test_queue_list_includes_max_size_active_system(self, test_client):
        """Test that queue list includes max_size when system is active"""
        client, mock_db = test_client
        
        # Mock active system status
        mock_db.get_system_status.return_value = {
            'active': True,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin'
        }
        
        # Mock queue with 2 users
        mock_queue = [
            {'callsign': 'W1ABC', 'timestamp': '2024-01-01T12:00:00Z', 'position': 1},
            {'callsign': 'K2DEF', 'timestamp': '2024-01-01T12:01:00Z', 'position': 2}
        ]
        mock_db.get_queue_list.return_value = mock_queue
        
        # Test with default MAX_QUEUE_SIZE
        with patch.dict(os.environ, {'MAX_QUEUE_SIZE': '4'}):
            response = client.get('/api/queue/list')
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure includes new max_size field
        assert 'queue' in data
        assert 'total' in data
        assert 'max_size' in data  # New field
        assert 'system_active' in data
        
        # Verify correct values
        assert len(data['queue']) == 2
        assert data['total'] == 2
        assert data['max_size'] == 4  # Should match MAX_QUEUE_SIZE env var
        assert data['system_active'] is True
    
    def test_queue_list_includes_max_size_inactive_system(self, test_client):
        """Test that queue list includes max_size when system is inactive"""
        client, mock_db = test_client
        
        # Mock inactive system status
        mock_db.get_system_status.return_value = {
            'active': False,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin'
        }
        
        # Test with custom MAX_QUEUE_SIZE
        with patch.dict(os.environ, {'MAX_QUEUE_SIZE': '6'}):
            response = client.get('/api/queue/list')
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure includes new max_size field
        assert 'queue' in data
        assert 'total' in data
        assert 'max_size' in data  # New field
        assert 'system_active' in data
        
        # Verify correct values for inactive system
        assert data['queue'] == []
        assert data['total'] == 0
        assert data['max_size'] == 6  # Should match custom MAX_QUEUE_SIZE env var
        assert data['system_active'] is False
    
    def test_queue_list_uses_default_max_size_when_env_not_set(self, test_client):
        """Test that queue list uses default max_size when env var is not set"""
        client, mock_db = test_client
        
        # Mock active system status
        mock_db.get_system_status.return_value = {
            'active': True,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin'
        }
        
        mock_db.get_queue_list.return_value = []
        
        # Test without MAX_QUEUE_SIZE env var (should default to 4)
        with patch.dict(os.environ, {}, clear=True):
            response = client.get('/api/queue/list')
        
        assert response.status_code == 200
        data = response.json()
        assert data['max_size'] == 4  # Should use default value