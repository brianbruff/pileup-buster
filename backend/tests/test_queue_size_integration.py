"""
Integration test to demonstrate queue size display functionality
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


class TestQueueSizeIntegration:
    """Integration test for queue size display functionality"""
    
    def test_complete_queue_size_workflow(self, test_client):
        """Test the complete workflow from empty queue to full queue with proper size display"""
        client, mock_db = test_client
        
        # Mock active system status
        mock_db.get_system_status.return_value = {
            'active': True,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin'
        }
        
        # Test with custom queue size limit
        with patch.dict(os.environ, {'MAX_QUEUE_SIZE': '3'}):
            # Test empty queue
            mock_db.get_queue_list.return_value = []
            response = client.get('/api/queue/list')
            
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 0
            assert data['max_size'] == 3
            assert data['system_active'] is True
            print(f"✓ Empty queue: {data['total']}/{data['max_size']}")
            
            # Test partially filled queue (2/3)
            mock_queue = [
                {'callsign': 'W1ABC', 'timestamp': '2024-01-01T12:00:00Z', 'position': 1},
                {'callsign': 'K2DEF', 'timestamp': '2024-01-01T12:01:00Z', 'position': 2}
            ]
            mock_db.get_queue_list.return_value = mock_queue
            response = client.get('/api/queue/list')
            
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 2
            assert data['max_size'] == 3
            assert len(data['queue']) == 2
            print(f"✓ Partially filled queue: {data['total']}/{data['max_size']}")
            
            # Test full queue (3/3)
            mock_queue_full = [
                {'callsign': 'W1ABC', 'timestamp': '2024-01-01T12:00:00Z', 'position': 1},
                {'callsign': 'K2DEF', 'timestamp': '2024-01-01T12:01:00Z', 'position': 2},
                {'callsign': 'N3GHI', 'timestamp': '2024-01-01T12:02:00Z', 'position': 3}
            ]
            mock_db.get_queue_list.return_value = mock_queue_full
            response = client.get('/api/queue/list')
            
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 3
            assert data['max_size'] == 3
            assert len(data['queue']) == 3
            print(f"✓ Full queue: {data['total']}/{data['max_size']}")
            
            print("✓ All queue size display tests passed!")
    
    def test_queue_size_with_different_limits(self, test_client):
        """Test queue size display with different MAX_QUEUE_SIZE values"""
        client, mock_db = test_client
        
        # Mock active system status
        mock_db.get_system_status.return_value = {
            'active': True,
            'last_updated': '2024-01-01T12:00:00Z',
            'updated_by': 'admin'
        }
        
        mock_queue = [
            {'callsign': 'W1ABC', 'timestamp': '2024-01-01T12:00:00Z', 'position': 1}
        ]
        mock_db.get_queue_list.return_value = mock_queue
        
        # Test with different queue size limits
        for queue_size in ['2', '4', '6', '10']:
            with patch.dict(os.environ, {'MAX_QUEUE_SIZE': queue_size}):
                response = client.get('/api/queue/list')
                assert response.status_code == 200
                data = response.json()
                assert data['max_size'] == int(queue_size)
                print(f"✓ Queue size {queue_size}: {data['total']}/{data['max_size']}")
        
        print("✓ All queue size limit tests passed!")