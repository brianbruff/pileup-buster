"""
Test for system activation/deactivation functionality in the pileup-buster queue system.
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
    """Create a test client with mocked database and admin credentials"""
    app = create_app()
    
    # Set admin credentials for testing
    with patch.dict(os.environ, {'ADMIN_USERNAME': 'admin', 'ADMIN_PASSWORD': 'admin'}):
        # Patch the database instance in both admin and queue routes
        with patch('app.routes.admin.queue_db', mock_database):
            with patch('app.routes.queue.queue_db', mock_database):
                with TestClient(app) as client:
                    yield client, mock_database


class TestSystemActivation:
    """Test cases for system activation/deactivation functionality"""
    
    def test_get_system_status_active(self, test_client):
        """Test getting system status when active"""
        client, mock_db = test_client
        
        # Mock active system status
        mock_db.get_system_status.return_value = {
            'active': True,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin'
        }
        
        response = client.get(
            '/api/admin/status',
            auth=('admin', 'admin')  # HTTP Basic Auth
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['active'] is True
        assert data['last_updated'] == '2024-01-01T12:00:00Z'
        assert data['updated_by'] == 'admin'
        mock_db.get_system_status.assert_called_once()
    
    def test_get_system_status_inactive(self, test_client):
        """Test getting system status when inactive"""
        client, mock_db = test_client
        
        # Mock inactive system status
        mock_db.get_system_status.return_value = {
            'active': False,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin'
        }
        
        response = client.get(
            '/api/admin/status',
            auth=('admin', 'admin')
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['active'] is False
        mock_db.get_system_status.assert_called_once()
    
    def test_get_system_status_requires_auth(self, test_client):
        """Test that getting system status requires admin authentication"""
        client, mock_db = test_client
        
        response = client.get('/api/admin/status')
        
        assert response.status_code == 401
        mock_db.get_system_status.assert_not_called()
    
    def test_activate_system(self, test_client):
        """Test activating the system"""
        client, mock_db = test_client
        
        # Mock successful activation with queue clearing
        mock_db.set_system_status.return_value = {
            'active': True,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin',
            'queue_cleared': True,
            'cleared_count': 2
        }
        
        response = client.post(
            '/api/admin/status',
            json={'active': True},
            auth=('admin', 'admin')
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'System activated successfully' in data['message']
        assert 'Queue cleared (2 entries removed)' in data['message']
        assert data['status']['active'] is True
        assert data['status']['queue_cleared'] is True
        assert data['status']['cleared_count'] == 2
        mock_db.set_system_status.assert_called_once_with(True, 'admin')
    
    def test_deactivate_system_with_queue_clearing(self, test_client):
        """Test deactivating the system and clearing queue"""
        client, mock_db = test_client
        
        # Mock successful deactivation with queue clearing
        mock_db.set_system_status.return_value = {
            'active': False,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin',
            'queue_cleared': True,
            'cleared_count': 3
        }
        
        response = client.post(
            '/api/admin/status',
            json={'active': False},
            auth=('admin', 'admin')
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'System deactivated successfully' in data['message']
        assert 'Queue cleared (3 entries removed)' in data['message']
        assert data['status']['active'] is False
        assert data['status']['queue_cleared'] is True
        assert data['status']['cleared_count'] == 3
        mock_db.set_system_status.assert_called_once_with(False, 'admin')
    
    def test_set_system_status_requires_auth(self, test_client):
        """Test that setting system status requires admin authentication"""
        client, mock_db = test_client
        
        response = client.post(
            '/api/admin/status',
            json={'active': True}
        )
        
        assert response.status_code == 401
        mock_db.set_system_status.assert_not_called()
    
    def test_set_system_status_invalid_request(self, test_client):
        """Test setting system status with invalid request data"""
        client, mock_db = test_client
        
        response = client.post(
            '/api/admin/status',
            json={'invalid': 'data'},
            auth=('admin', 'admin')
        )
        
        assert response.status_code == 422  # Pydantic validation error
        mock_db.set_system_status.assert_not_called()


class TestSystemActivationQueueIntegration:
    """Test cases for system activation integration with queue operations"""
    
    def test_register_callsign_when_system_active(self, test_client):
        """Test that callsign registration works when system is active"""
        client, mock_db = test_client
        
        # Mock successful registration (system is active)
        mock_db.register_callsign.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00',
            'position': 1
        }
        
        response = client.post('/api/queue/register', json={'callsign': 'KC1ABC'})
        
        assert response.status_code == 200
        assert response.json()['message'] == 'Callsign registered successfully'
        
        # Verify register_callsign was called with callsign and QRZ info
        args, kwargs = mock_db.register_callsign.call_args
        assert args[0] == 'KC1ABC'  # First argument is callsign
    
    def test_register_callsign_when_system_inactive(self, test_client):
        """Test that callsign registration fails when system is inactive"""
        client, mock_db = test_client
        
        # Mock system inactive error
        mock_db.register_callsign.side_effect = ValueError(
            "System is currently inactive. Registration is not available."
        )
        
        response = client.post('/api/queue/register', json={'callsign': 'KC1ABC'})
        
        assert response.status_code == 400
        assert 'System is currently inactive' in response.json()['detail']
        
        # Verify register_callsign was called with callsign and QRZ info
        args, kwargs = mock_db.register_callsign.call_args
        assert args[0] == 'KC1ABC'  # First argument is callsign


class TestDatabaseSystemStatus:
    """Test the database layer system status functionality"""
    
    def test_get_system_status_default_inactive(self):
        """Test that system defaults to inactive when no status exists"""
        # Create a database instance with a mocked status collection
        mock_status_collection = Mock()
        
        db = QueueDatabase()
        db.status_collection = mock_status_collection
        
        # Mock no existing status document
        mock_status_collection.find_one.return_value = None
        mock_status_collection.insert_one.return_value = Mock()
        
        result = db.get_system_status()
        
        assert result['active'] is False
        assert result['updated_by'] == 'system'
        assert 'last_updated' in result
        
        # Verify default status was created
        mock_status_collection.insert_one.assert_called_once()
        insert_call = mock_status_collection.insert_one.call_args[0][0]
        assert insert_call['_id'] == 'system_status'
        assert insert_call['active'] is False
        assert insert_call['updated_by'] == 'system'
    
    def test_get_system_status_existing(self):
        """Test getting existing system status"""
        mock_status_collection = Mock()
        
        db = QueueDatabase()
        db.status_collection = mock_status_collection
        
        # Mock existing status document
        mock_status_collection.find_one.return_value = {
            '_id': 'system_status',
            'active': True,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin'
        }
        
        result = db.get_system_status()
        
        assert result['active'] is True
        assert result['last_updated'] == '2024-01-01T12:00:00Z'
        assert result['updated_by'] == 'admin'
        assert '_id' not in result  # MongoDB ObjectId should be removed
    
    def test_set_system_status_activate(self):
        """Test activating the system clears the queue"""
        mock_status_collection = Mock()
        mock_collection = Mock()
        
        db = QueueDatabase()
        db.status_collection = mock_status_collection
        db.collection = mock_collection
        
        # Mock queue clearing
        mock_collection.count_documents.return_value = 1
        mock_collection.delete_many.return_value = Mock()
        mock_status_collection.replace_one.return_value = Mock()
        
        result = db.set_system_status(True, 'admin')
        
        assert result['active'] is True
        assert result['updated_by'] == 'admin'
        assert result['queue_cleared'] is True
        assert result['cleared_count'] == 1
        assert 'last_updated' in result
        
        # Verify queue was cleared
        mock_collection.delete_many.assert_called_once_with({})
        
        # Verify the status was updated
        mock_status_collection.replace_one.assert_called_once()
        replace_call = mock_status_collection.replace_one.call_args
        assert replace_call[0][0] == {'_id': 'system_status'}  # filter
        assert replace_call[0][1]['active'] is True  # update document
        assert replace_call[1]['upsert'] is True
    
    def test_set_system_status_deactivate_with_queue_clear(self):
        """Test deactivating the system clears the queue"""
        mock_status_collection = Mock()
        mock_collection = Mock()
        
        db = QueueDatabase()
        db.status_collection = mock_status_collection
        db.collection = mock_collection
        
        # Mock queue clearing
        mock_collection.count_documents.return_value = 2
        mock_collection.delete_many.return_value = Mock()
        mock_status_collection.replace_one.return_value = Mock()
        
        result = db.set_system_status(False, 'admin')
        
        assert result['active'] is False
        assert result['updated_by'] == 'admin'
        assert result['queue_cleared'] is True
        assert result['cleared_count'] == 2
        
        # Verify queue was cleared
        mock_collection.delete_many.assert_called_once_with({})
        
        # Verify status was updated
        mock_status_collection.replace_one.assert_called_once()
    
    def test_is_system_active_when_active(self):
        """Test is_system_active returns True when system is active"""
        mock_status_collection = Mock()
        
        db = QueueDatabase()
        db.status_collection = mock_status_collection
        
        # Mock active status
        mock_status_collection.find_one.return_value = {
            'active': True
        }
        
        result = db.is_system_active()
        
        assert result is True
    
    def test_is_system_active_when_inactive(self):
        """Test is_system_active returns False when system is inactive"""
        mock_status_collection = Mock()
        
        db = QueueDatabase()
        db.status_collection = mock_status_collection
        
        # Mock inactive status
        mock_status_collection.find_one.return_value = None
        
        result = db.is_system_active()
        
        assert result is False
    
    def test_is_system_active_on_error(self):
        """Test is_system_active returns False on database error (fail-safe)"""
        db = QueueDatabase()
        db.status_collection = None  # Simulate database connection failure
        
        result = db.is_system_active()
        
        assert result is False  # Should default to inactive for safety