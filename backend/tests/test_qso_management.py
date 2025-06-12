"""
Test for QSO status management in the pileup-buster queue system.
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
        # Patch the database instance
        with patch('app.routes.admin.queue_db', mock_database):
            with TestClient(app) as client:
                yield client, mock_database


class TestQSOManagement:
    """Test cases for QSO status management"""
    
    def test_next_with_queue_and_no_current_qso(self, test_client):
        """Test calling Next with queue but no current QSO - should move first to QSO"""
        client, mock_db = test_client
        
        # Mock no current QSO and queue has entries
        mock_db.clear_current_qso.return_value = None
        mock_db.get_next_callsign.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00',
            'position': 1
        }
        mock_db.set_current_qso.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:01:00',
            'started_by': 'admin'
        }
        mock_db.get_queue_count.return_value = 1
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert 'Next callsign: KC1ABC is now in QSO' in data['message']
        assert data['processed']['callsign'] == 'KC1ABC'
        assert data['current_qso']['callsign'] == 'KC1ABC'
        assert data['remaining'] == 1
        
        # Verify the correct calls were made
        mock_db.clear_current_qso.assert_called_once()
        mock_db.get_next_callsign.assert_called_once()
        mock_db.set_current_qso.assert_called_once_with('KC1ABC', 'admin')
    
    def test_next_with_queue_and_current_qso(self, test_client):
        """Test calling Next with queue and current QSO - should clear QSO and move first to QSO"""
        client, mock_db = test_client
        
        # Mock current QSO exists and queue has entries
        mock_db.clear_current_qso.return_value = {
            'callsign': 'W1ABC',
            'timestamp': '2024-01-01T11:00:00',
            'started_by': 'admin'
        }
        mock_db.get_next_callsign.return_value = {
            'callsign': 'KC1XYZ',
            'timestamp': '2024-01-01T12:00:00',
            'position': 1
        }
        mock_db.set_current_qso.return_value = {
            'callsign': 'KC1XYZ',
            'timestamp': '2024-01-01T12:01:00',
            'started_by': 'admin'
        }
        mock_db.get_queue_count.return_value = 0
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert 'QSO with W1ABC cleared. Next callsign: KC1XYZ is now in QSO' in data['message']
        assert data['processed']['callsign'] == 'KC1XYZ'
        assert data['current_qso']['callsign'] == 'KC1XYZ'
        assert data['cleared_qso']['callsign'] == 'W1ABC'
        assert data['remaining'] == 0
    
    def test_next_with_empty_queue_and_current_qso(self, test_client):
        """Test calling Next with empty queue but current QSO - should clear QSO only"""
        client, mock_db = test_client
        
        # Mock current QSO exists but queue is empty
        mock_db.clear_current_qso.return_value = {
            'callsign': 'W1ABC',
            'timestamp': '2024-01-01T11:00:00',
            'started_by': 'admin'
        }
        mock_db.get_next_callsign.return_value = None
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 200
        data = response.json()
        assert 'QSO with W1ABC cleared. Queue is empty.' in data['message']
        assert data['cleared_qso']['callsign'] == 'W1ABC'
        assert data['current_qso'] is None
        assert data['remaining'] == 0
        
        # Verify set_current_qso was not called
        mock_db.set_current_qso.assert_not_called()
    
    def test_next_with_empty_queue_and_no_current_qso(self, test_client):
        """Test calling Next with empty queue and no current QSO - should do nothing"""
        client, mock_db = test_client
        
        # Mock no current QSO and empty queue
        mock_db.clear_current_qso.return_value = None
        mock_db.get_next_callsign.return_value = None
        
        response = client.post('/api/admin/queue/next', auth=('admin', 'admin'))
        
        assert response.status_code == 400
        assert 'Queue is empty and no active QSO' in response.json()['detail']
        
        # Verify set_current_qso was not called
        mock_db.set_current_qso.assert_not_called()
    
    def test_next_requires_admin_auth(self, test_client):
        """Test that Next endpoint requires admin authentication"""
        client, mock_db = test_client
        
        response = client.post('/api/admin/queue/next')
        assert response.status_code == 401
        
        response = client.post('/api/admin/queue/next', auth=('wrong', 'wrong'))
        assert response.status_code == 401


class TestDatabaseQSOManagement:
    """Test the database layer QSO management functionality"""
    
    def test_get_current_qso_when_exists(self):
        """Test getting current QSO when one exists"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.qso_collection = mock_qso_collection
        
        # Mock existing QSO document
        mock_qso_collection.find_one.return_value = {
            '_id': 'current_qso',
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z',
            'started_by': 'admin'
        }
        
        result = db.get_current_qso()
        
        assert result['callsign'] == 'KC1ABC'
        assert result['timestamp'] == '2024-01-01T12:00:00Z'
        assert result['started_by'] == 'admin'
        assert '_id' not in result  # MongoDB ObjectId should be removed
    
    def test_get_current_qso_when_none_exists(self):
        """Test getting current QSO when none exists"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.qso_collection = mock_qso_collection
        
        # Mock no existing QSO document
        mock_qso_collection.find_one.return_value = None
        
        result = db.get_current_qso()
        
        assert result is None
    
    def test_set_current_qso(self):
        """Test setting a callsign as current QSO"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.qso_collection = mock_qso_collection
        
        result = db.set_current_qso('KC1ABC', 'admin')
        
        assert result['callsign'] == 'KC1ABC'
        assert result['started_by'] == 'admin'
        assert 'timestamp' in result
        
        # Verify the replace_one was called
        mock_qso_collection.replace_one.assert_called_once()
        call_args = mock_qso_collection.replace_one.call_args
        assert call_args[0][0] == {"_id": "current_qso"}  # filter
        assert call_args[0][1]['callsign'] == 'KC1ABC'   # replacement doc
        assert call_args[1]['upsert'] is True
    
    def test_clear_current_qso_when_exists(self):
        """Test clearing current QSO when one exists"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.qso_collection = mock_qso_collection
        
        # Mock existing QSO document to be deleted
        mock_qso_collection.find_one_and_delete.return_value = {
            '_id': 'current_qso',
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z',
            'started_by': 'admin'
        }
        
        result = db.clear_current_qso()
        
        assert result['callsign'] == 'KC1ABC'
        assert result['timestamp'] == '2024-01-01T12:00:00Z'
        assert result['started_by'] == 'admin'
        assert '_id' not in result  # MongoDB ObjectId should be removed
        
        # Verify the find_one_and_delete was called
        mock_qso_collection.find_one_and_delete.assert_called_once_with({"_id": "current_qso"})
    
    def test_clear_current_qso_when_none_exists(self):
        """Test clearing current QSO when none exists"""
        mock_qso_collection = Mock()
        
        db = QueueDatabase()
        db.qso_collection = mock_qso_collection
        
        # Mock no existing QSO document
        mock_qso_collection.find_one_and_delete.return_value = None
        
        result = db.clear_current_qso()
        
        assert result is None