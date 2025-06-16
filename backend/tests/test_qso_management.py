"""Test cases for QSO management functionality"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
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


class TestQSODatabaseMethods:
    """Test the database layer QSO management functionality"""
    
    def test_get_current_qso_existing(self):
        """Test getting existing current QSO"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.currentqso_collection = mock_qso_collection
        
        # Mock existing QSO document
        mock_qso_collection.find_one.return_value = {
            '_id': 'current_qso',
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        result = db.get_current_qso()
        
        assert result['callsign'] == 'KC1ABC'
        assert result['timestamp'] == '2024-01-01T12:00:00Z'
        assert '_id' not in result  # MongoDB ObjectId should be removed
    
    def test_get_current_qso_none(self):
        """Test getting current QSO when none exists"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.currentqso_collection = mock_qso_collection
        
        # Mock no existing QSO document
        mock_qso_collection.find_one.return_value = None
        
        result = db.get_current_qso()
        
        assert result is None
    
    def test_set_current_qso(self):
        """Test setting current QSO"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.currentqso_collection = mock_qso_collection
        
        mock_qso_collection.replace_one.return_value = Mock()
        
        result = db.set_current_qso('KC1ABC')
        
        assert result['callsign'] == 'KC1ABC'
        assert 'timestamp' in result
        
        # Verify the replace_one was called with correct parameters
        mock_qso_collection.replace_one.assert_called_once()
        replace_call = mock_qso_collection.replace_one.call_args
        assert replace_call[0][0] == {'_id': 'current_qso'}  # filter
        assert replace_call[0][1]['callsign'] == 'KC1ABC'  # update document
        assert replace_call[1]['upsert'] is True
    
    def test_clear_current_qso_existing(self):
        """Test clearing existing current QSO"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.currentqso_collection = mock_qso_collection
        
        # Mock existing QSO document
        mock_qso_collection.find_one_and_delete.return_value = {
            '_id': 'current_qso',
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        result = db.clear_current_qso()
        
        assert result['callsign'] == 'KC1ABC'
        assert result['timestamp'] == '2024-01-01T12:00:00Z'
        assert '_id' not in result
    
    def test_clear_current_qso_none(self):
        """Test clearing current QSO when none exists"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.currentqso_collection = mock_qso_collection
        
        # Mock no existing QSO document
        mock_qso_collection.find_one_and_delete.return_value = None
        
        result = db.clear_current_qso()
        
        assert result is None


class TestNextCallsignQSOManagement:
    """Test the Next endpoint QSO management functionality"""
    
    def test_next_with_queue_and_no_current_qso(self, test_client):
        """Test calling Next with non-empty queue and no current QSO"""
        client, mock_db = test_client
        
        # Mock no current QSO to clear
        mock_db.clear_current_qso.return_value = None
        
        # Mock queue has a callsign
        mock_db.get_next_callsign.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z',
            'position': 1
        }
        
        # Mock setting new QSO
        mock_db.set_current_qso.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:05:00Z'
        }
        
        # Mock remaining count
        mock_db.get_queue_count.return_value = 2
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert 'Next callsign: KC1ABC is now in QSO' in data['message']
        assert data['processed']['callsign'] == 'KC1ABC'
        assert data['current_qso']['callsign'] == 'KC1ABC'
        assert data['remaining'] == 2
        assert 'cleared_qso' not in data  # No previous QSO to clear
    
    def test_next_with_queue_and_existing_qso(self, test_client):
        """Test calling Next with non-empty queue and existing current QSO"""
        client, mock_db = test_client
        
        # Mock existing QSO to clear
        mock_db.clear_current_qso.return_value = {
            'callsign': 'KC1XYZ',
            'timestamp': '2024-01-01T11:00:00Z'
        }
        
        # Mock queue has a callsign
        mock_db.get_next_callsign.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z',
            'position': 1
        }
        
        # Mock setting new QSO
        mock_db.set_current_qso.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:05:00Z'
        }
        
        # Mock remaining count
        mock_db.get_queue_count.return_value = 1
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert 'Next callsign: KC1ABC is now in QSO' in data['message']
        assert data['processed']['callsign'] == 'KC1ABC'
        assert data['current_qso']['callsign'] == 'KC1ABC'
        assert data['cleared_qso']['callsign'] == 'KC1XYZ'
        assert data['remaining'] == 1
    
    def test_next_with_empty_queue_and_existing_qso(self, test_client):
        """Test calling Next with empty queue but existing current QSO"""
        client, mock_db = test_client
        
        # Mock existing QSO to clear
        mock_db.clear_current_qso.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        # Mock empty queue
        mock_db.get_next_callsign.return_value = None
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Queue is empty. Cleared current QSO.'
        assert data['cleared_qso']['callsign'] == 'KC1ABC'
        assert data['remaining'] == 0
        assert 'processed' not in data
        assert 'current_qso' not in data
    
    def test_next_with_empty_queue_and_no_qso(self, test_client):
        """Test calling Next with empty queue and no current QSO"""
        client, mock_db = test_client
        
        # Mock no current QSO to clear
        mock_db.clear_current_qso.return_value = None
        
        # Mock empty queue
        mock_db.get_next_callsign.return_value = None
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Queue is empty. No action taken.'
        assert data['remaining'] == 0
        assert 'processed' not in data
        assert 'current_qso' not in data
        assert 'cleared_qso' not in data
    
    def test_next_requires_admin_auth(self, test_client):
        """Test that Next endpoint requires admin authentication"""
        client, mock_db = test_client
        
        # Test without auth
        response = client.post('/api/admin/queue/next')
        assert response.status_code == 401
        
        # Test with wrong auth
        response = client.post('/api/admin/queue/next', auth=('wrong', 'creds'))
        assert response.status_code == 401
    
    def test_next_database_error_handling(self, test_client):
        """Test proper error handling when database operations fail"""
        client, mock_db = test_client
        
        # Mock database error
        mock_db.clear_current_qso.side_effect = Exception("Database connection failed")
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 500
        assert 'Database error' in response.json()['detail']


class TestCompleteQSOEndpoint:
    """Test the Complete QSO endpoint functionality"""
    
    def test_complete_qso_with_existing_qso(self, test_client):
        """Test completing an existing QSO"""
        client, mock_db = test_client
        
        # Mock existing QSO to clear
        mock_db.clear_current_qso.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z',
            'qrz': {
                'callsign': 'KC1ABC',
                'name': 'Test User',
                'address': 'Test Address',
                'dxcc_name': 'United States',
                'image': None,
                'error': None
            }
        }
        
        response = client.post('/api/admin/qso/complete', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'QSO with KC1ABC completed successfully'
        assert data['cleared_qso']['callsign'] == 'KC1ABC'
        assert data['cleared_qso']['timestamp'] == '2024-01-01T12:00:00Z'
        
        # Verify clear_current_qso was called
        mock_db.clear_current_qso.assert_called_once()
    
    def test_complete_qso_with_no_existing_qso(self, test_client):
        """Test completing QSO when no current QSO exists"""
        client, mock_db = test_client
        
        # Mock no current QSO to clear
        mock_db.clear_current_qso.return_value = None
        
        response = client.post('/api/admin/qso/complete', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'No active QSO to complete'
        assert data['cleared_qso'] is None
        
        # Verify clear_current_qso was called
        mock_db.clear_current_qso.assert_called_once()
    
    def test_complete_qso_requires_admin_auth(self, test_client):
        """Test that Complete QSO endpoint requires admin authentication"""
        client, mock_db = test_client
        
        # Test without auth
        response = client.post('/api/admin/qso/complete')
        assert response.status_code == 401
        
        # Test with wrong auth
        response = client.post('/api/admin/qso/complete', auth=('wrong', 'creds'))
        assert response.status_code == 401
    
    def test_complete_qso_database_error_handling(self, test_client):
        """Test proper error handling when database operations fail"""
        client, mock_db = test_client
        
        # Mock database error
        mock_db.clear_current_qso.side_effect = Exception("Database connection failed")
        
        response = client.post('/api/admin/qso/complete', auth=('admin', 'admin'))
        
        assert response.status_code == 500
        assert 'Database error' in response.json()['detail']


class TestQSOManagementEdgeCases:
    """Test edge cases for QSO management"""
    
    def test_database_connection_not_available(self):
        """Test QSO methods when database connection is not available"""
        db = QueueDatabase()
        db.currentqso_collection = None
        
        with pytest.raises(Exception, match="Database connection not available"):
            db.get_current_qso()
        
        with pytest.raises(Exception, match="Database connection not available"):
            db.set_current_qso("KC1ABC")
        
        with pytest.raises(Exception, match="Database connection not available"):
            db.clear_current_qso()