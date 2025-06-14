"""
Tests for the status page endpoint with screenshot functionality
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
        
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            mock_screenshot.return_value = 'mock_base64_image_data'
            mock_get_status.return_value = mock_status
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            assert response.headers['content-type'] == 'text/html; charset=utf-8'
            
            content = response.text
            assert 'Pileup Buster Status' in content
            assert 'mock_base64_image_data' in content
            assert 'Go to Pileup Buster Frontend' in content
            assert 'ACTIVE' in content
    
    def test_get_status_page_with_custom_frontend_url(self, test_client):
        """Test status page with custom frontend URL from environment"""
        custom_url = 'https://example.com:8080'
        mock_status = {
            'active': False, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            with patch.dict(os.environ, {'FRONTEND_URL': custom_url}):
                mock_screenshot.return_value = 'mock_base64_image_data'
                mock_get_status.return_value = mock_status
                
                response = test_client.get('/status')
                
                assert response.status_code == 200
                content = response.text
                assert custom_url in content
                assert 'INACTIVE' in content
                
                # Verify screenshot was called with custom URL
                mock_screenshot.assert_called_once_with(custom_url)
    
    def test_get_status_page_screenshot_failure(self, test_client):
        """Test status page when screenshot capture fails"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            mock_screenshot.return_value = None  # Simulate failure
            mock_get_status.return_value = mock_status
            
            response = test_client.get('/status')
            
            # Status page should still work without screenshot
            assert response.status_code == 200
            content = response.text
            assert 'Screenshot not available' in content
            assert 'ACTIVE' in content
    
    def test_get_status_page_exception_handling(self, test_client):
        """Test status page exception handling"""
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            mock_screenshot.side_effect = Exception("Screenshot service error")
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
        
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            with patch.dict(os.environ, {}, clear=True):  # Clear environment
                mock_screenshot.return_value = 'mock_base64_image_data'
                mock_get_status.return_value = mock_status
                
                response = test_client.get('/status')
                
                assert response.status_code == 200
                
                # Verify screenshot was called with default URL
                mock_screenshot.assert_called_once_with('https://briankeating.net/pileup-buster')
    
    def test_get_status_page_no_authentication_required(self, test_client):
        """Test that status page endpoint does not require authentication"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            mock_screenshot.return_value = 'mock_base64_image_data'
            mock_get_status.return_value = mock_status
            
            # Make request without any authentication
            response = test_client.get('/status')
            
            assert response.status_code == 200
    
    def test_get_status_page_contains_required_elements(self, test_client):
        """Test that status page contains all required elements"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            mock_screenshot.return_value = 'mock_base64_image_data'
            mock_get_status.return_value = mock_status
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Check for required HTML elements
            assert '<html' in content
            assert '<head>' in content
            assert '<title>Pileup Buster Status</title>' in content
            assert '<img' in content
            assert 'data:image/png;base64,mock_base64_image_data' in content
            assert '<a href=' in content
            assert 'Go to Pileup Buster Frontend' in content
            assert 'System Status: ACTIVE' in content
            assert 'Last updated:' in content
    
    def test_get_status_page_inactive_system(self, test_client):
        """Test status page displays inactive system status correctly"""
        mock_status = {
            'active': False, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            mock_screenshot.return_value = None  # No screenshot
            mock_get_status.return_value = mock_status
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Verify inactive status is displayed
            assert 'System Status: INACTIVE' in content
            assert 'Go to Pileup Buster Frontend (INACTIVE)' in content
            assert '#dc3545' in content  # Red color for inactive
            assert 'Screenshot not available' in content

    def test_get_status_page_active_system_with_screenshot(self, test_client):
        """Test status page displays active system status with screenshot"""
        mock_status = {
            'active': True, 
            'last_updated': '2024-01-01T12:00:00'
        }
        
        with patch('app.services.screenshot.capture_screenshot') as mock_screenshot, \
             patch('app.database.queue_db.get_system_status') as mock_get_status:
            mock_screenshot.return_value = 'screenshot_data'
            mock_get_status.return_value = mock_status
            
            response = test_client.get('/status')
            
            assert response.status_code == 200
            content = response.text
            
            # Verify active status is displayed
            assert 'System Status: ACTIVE' in content
            assert 'Go to Pileup Buster Frontend (ACTIVE)' in content
            assert '#28a745' in content  # Green color for active
            assert 'data:image/png;base64,screenshot_data' in content