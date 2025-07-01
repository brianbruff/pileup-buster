"""
Tests for the optimized status page endpoint without screenshots
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.app import create_app
import os


@pytest.fixture
def test_client():
    """Create a test client"""
    app = create_app()
    with TestClient(app) as client:
        yield client


class TestStatusPageEndpoint:
    """Test cases for status page endpoint functionality"""
    
    def test_get_status_page_success(self, test_client):
        """Test successful status page generation"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_current_qso = {
            'callsign': 'W1ABC',
            'qrz': {
                'name': 'John Doe',
                'dxcc_name': 'United States'
            }
        }
        mock_queue = [
            {
                'callsign': 'W2DEF',
                'position': 1,
                'qrz': {'name': 'Jane Smith'}
            },
            {
                'callsign': 'W3GHI',
                'position': 2,
                'qrz': {'name': 'Bob Johnson'}
            }
        ]
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = mock_current_qso
            mock_get_queue.return_value = mock_queue
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            assert response.headers['content-type'] == 'text/html; charset=utf-8'
            
            content = response.text
            assert 'Pileup Buster Status' in content
            assert 'Visit Pileup Buster' in content
            assert 'ACTIVE' in content
            assert 'W1ABC' in content  # Current QSO
            assert 'John Doe' in content  # Current QSO name
            assert 'W2DEF' in content  # Queue user
            assert 'Jane Smith' in content  # Queue user name
    
    def test_get_status_page_with_custom_frontend_url(self, test_client):
        """Test status page with custom frontend URL from environment"""
        custom_url = 'https://example.com:8080'
        mock_status = {
            'active': False, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            with patch.dict(os.environ, {'FRONTEND_URL': custom_url}):
                mock_get_status.return_value = mock_status
                mock_get_qso.return_value = None
                mock_get_queue.return_value = []
                
                response = test_client.get('/status')
                
                assert response.status_code == 200
                content = response.text
                assert custom_url in content
                assert 'INACTIVE' in content
    
    def test_get_status_page_no_current_qso(self, test_client):
        """Test status page when no current QSO is active"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = []
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            assert 'No active QSO' in content
            assert 'ACTIVE' in content
    
    def test_get_status_page_exception_handling(self, test_client):
        """Test status page exception handling"""
        with patch('app.database.queue_db.get_system_status') as mock_get_status:
            mock_get_status.side_effect = Exception("Database error")
            
            response = test_client.get('/status')
            
            assert response.status_code == 500
            content = response.text
            assert 'Status Page Unavailable' in content
            assert 'Database error' in content
    
    def test_get_status_page_default_frontend_url(self, test_client):
        """Test status page uses default frontend URL when not configured"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            with patch.dict(os.environ, {}, clear=True):  # Clear environment
                mock_get_status.return_value = mock_status
                mock_get_qso.return_value = None
                mock_get_queue.return_value = []
                
                response = test_client.get('/status')
                
                assert response.status_code == 200
                content = response.text
                assert 'https://briankeating.net/pileup-buster' in content
    
    def test_get_status_page_no_authentication_required(self, test_client):
        """Test that status page endpoint does not require authentication"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = []
            
            # Make request without any authentication
            response = test_client.get('/status')
            
            assert response.status_code == 200
    
    def test_get_status_page_contains_required_elements(self, test_client):
        """Test that status page contains all required elements"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_current_qso = {
            'callsign': 'W1ABC',
            'qrz': {'name': 'John Doe', 'dxcc_name': 'United States'}
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = mock_current_qso
            mock_get_queue.return_value = []
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Check for required HTML elements
            assert '<html' in content
            assert '<head>' in content
            assert '<title>Pileup Buster Status</title>' in content
            assert '<a href=' in content
            assert 'Visit Pileup Buster' in content
            assert 'System Status: ACTIVE' in content
            assert 'Last updated:' in content
            assert 'Currently Working' in content
            assert 'Queue' in content
    
    def test_get_status_page_inactive_system(self, test_client):
        """Test status page displays inactive system status correctly"""
        mock_status = {
            'active': False, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = []
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Verify inactive status is displayed
            assert 'System Status: INACTIVE' in content
            assert 'Visit Pileup Buster (INACTIVE)' in content
            assert '#dc3545' in content  # Red color for inactive

    def test_get_status_page_active_system_with_queue(self, test_client):
        """Test status page displays active system status with queue"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_queue = [
            {'callsign': 'W1ABC', 'position': 1, 'qrz': {'name': 'Alice'}},
            {'callsign': 'W2DEF', 'position': 2, 'qrz': {'name': 'Bob'}},
            {'callsign': 'W3GHI', 'position': 3, 'qrz': {'name': 'Charlie'}}
        ]
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = mock_queue
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Verify active status and queue are displayed
            assert 'System Status: ACTIVE' in content
            assert 'Visit Pileup Buster (ACTIVE)' in content
            assert '#28a745' in content  # Green color for active
            assert 'Queue (3 users)' in content
            assert 'W1ABC' in content
            assert 'Alice' in content
            assert '#1' in content  # Position indicator

    def test_get_status_page_large_queue_truncation(self, test_client):
        """Test status page truncates large queues properly"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        # Create a queue with 15 users
        mock_queue = []
        for i in range(15):
            mock_queue.append({
                'callsign': f'W{i}ABC',
                'position': i + 1,
                'qrz': {'name': f'User {i}'}
            })
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = mock_queue
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Should show queue count and truncation message
            assert 'Queue (15 users)' in content
            assert '+5 more' in content  # Shows remaining users after 10
            assert 'users in queue' in content

    def test_get_status_page_with_frequency_only(self, test_client):
        """Test status page displays frequency when set"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_frequency_data = {
            'frequency': '146.520 MHz',
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue, \
             patch('app.database.queue_db.get_frequency') as mock_get_frequency, \
             patch('app.database.queue_db.get_split') as mock_get_split:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = []
            mock_get_frequency.return_value = mock_frequency_data
            mock_get_split.return_value = None
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Should display frequency in status banner
            assert 'System Status: ACTIVE' in content
            assert 'Frequency: 146.520 MHz' in content
            # Should not display split since it's not set
            assert 'Split:' not in content

    def test_get_status_page_with_split_only(self, test_client):
        """Test status page displays split when set"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_split_data = {
            'split': '+5',
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue, \
             patch('app.database.queue_db.get_frequency') as mock_get_frequency, \
             patch('app.database.queue_db.get_split') as mock_get_split:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = []
            mock_get_frequency.return_value = None
            mock_get_split.return_value = mock_split_data
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Should display split in status banner
            assert 'System Status: ACTIVE' in content
            assert 'Split: +5' in content
            # Should not display frequency since it's not set
            assert 'Frequency:' not in content

    def test_get_status_page_with_frequency_and_split(self, test_client):
        """Test status page displays both frequency and split when both are set"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_frequency_data = {
            'frequency': '14.205 MHz',
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_split_data = {
            'split': '+10',
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue, \
             patch('app.database.queue_db.get_frequency') as mock_get_frequency, \
             patch('app.database.queue_db.get_split') as mock_get_split:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = []
            mock_get_frequency.return_value = mock_frequency_data
            mock_get_split.return_value = mock_split_data
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Should display both frequency and split in status banner
            assert 'System Status: ACTIVE' in content
            assert 'Frequency: 14.205 MHz' in content
            assert 'Split: +10' in content

    def test_get_status_page_with_empty_frequency_and_split(self, test_client):
        """Test status page handles empty frequency and split values gracefully"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_frequency_data = {
            'frequency': '',  # Empty frequency
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_split_data = {
            'split': '',  # Empty split
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue, \
             patch('app.database.queue_db.get_frequency') as mock_get_frequency, \
             patch('app.database.queue_db.get_split') as mock_get_split:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = []
            mock_get_frequency.return_value = mock_frequency_data
            mock_get_split.return_value = mock_split_data
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Should not display frequency or split when they are empty
            assert 'System Status: ACTIVE' in content
            assert 'Frequency:' not in content
            assert 'Split:' not in content

    def test_get_status_page_inactive_system_with_frequency_and_split(self, test_client):
        """Test status page does not display frequency and split when system is inactive"""
        mock_status = {
            'active': False,  # System is INACTIVE
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_frequency_data = {
            'frequency': '146.520 MHz',
            'last_updated': '2024-01-01T12:00:00'
        }
        mock_split_data = {
            'split': '+5',
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.database.queue_db.get_system_status') as mock_get_status, \
             patch('app.database.queue_db.get_current_qso') as mock_get_qso, \
             patch('app.database.queue_db.get_queue_list') as mock_get_queue, \
             patch('app.database.queue_db.get_frequency') as mock_get_frequency, \
             patch('app.database.queue_db.get_split') as mock_get_split:
            mock_get_status.return_value = mock_status
            mock_get_qso.return_value = None
            mock_get_queue.return_value = []
            mock_get_frequency.return_value = mock_frequency_data
            mock_get_split.return_value = mock_split_data
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Should display inactive status
            assert 'System Status: INACTIVE' in content
            # Should NOT display frequency or split when system is inactive
            assert 'Frequency:' not in content
            assert 'Split:' not in content
            assert '146.520 MHz' not in content
            assert '+5' not in content