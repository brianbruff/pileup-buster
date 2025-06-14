"""
Integration tests for callsign validation in the queue registration endpoint.
"""
import pytest
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
    """Create a test client with mocked database and QRZ service"""
    app = create_app()
    
    # Mock the system as active for tests
    mock_database.get_system_status.return_value = {'active': True}
    
    # Mock QRZ service response  
    mock_qrz_info = {
        'callsign': 'KC1ABC',
        'name': None,
        'address': None,
        'image': None,
        'error': 'QRZ.com credentials not configured. Please set QRZ_USERNAME and QRZ_PASSWORD environment variables.'
    }
    
    # Patch both the database and QRZ service
    with patch('app.routes.queue.queue_db', mock_database):
        with patch('app.routes.queue.qrz_service') as mock_qrz:
            mock_qrz.lookup_callsign.return_value = mock_qrz_info
            with TestClient(app) as client:
                yield client, mock_database


class TestCallsignValidationIntegration:
    """Integration tests for callsign validation in queue registration"""
    
    def test_valid_callsign_registration_succeeds(self, test_client):
        """Test that valid callsigns can be registered successfully"""
        client, mock_db = test_client
        
        # Mock successful registration
        mock_db.register_callsign.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00',
            'position': 1
        }
        
        response = client.post('/api/queue/register', json={'callsign': 'KC1ABC'})
        
        assert response.status_code == 200
        assert response.json()['message'] == 'Callsign registered successfully'
        assert response.json()['entry']['callsign'] == 'KC1ABC'
        
        # Verify register_callsign was called
        mock_db.register_callsign.assert_called_once()
    
    def test_invalid_callsign_registration_fails(self, test_client):
        """Test that invalid callsigns are rejected with proper error"""
        client, mock_db = test_client
        
        invalid_callsigns = [
            'ABC123',      # Too many prefix letters
            '123ABC',      # Starts with numbers
            'KC',          # Missing numbers and suffix
            'KC1',         # Missing suffix
            'KC123',       # Missing suffix letters
            'KC1ABCD',     # Too many suffix letters
            'KC@ABC',      # Invalid character
        ]
        
        for callsign in invalid_callsigns:
            response = client.post('/api/queue/register', json={'callsign': callsign})
            
            assert response.status_code == 400
            assert 'Invalid callsign format' in response.json()['detail']
            assert 'ITU standards' in response.json()['detail']
            
        # Database should not be called for invalid callsigns
        mock_db.register_callsign.assert_not_called()
    
    def test_case_insensitive_validation(self, test_client):
        """Test that callsigns are validated correctly regardless of case"""
        client, mock_db = test_client
        
        # Mock successful registration
        mock_db.register_callsign.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00',
            'position': 1
        }
        
        # Test lowercase input (should be converted to uppercase and validated)
        response = client.post('/api/queue/register', json={'callsign': 'kc1abc'})
        
        assert response.status_code == 200
        assert response.json()['message'] == 'Callsign registered successfully'
        
        # Verify the callsign was converted to uppercase
        args, kwargs = mock_db.register_callsign.call_args
        assert args[0] == 'KC1ABC'  # First argument should be uppercase
    
    def test_whitespace_handling_with_validation(self, test_client):
        """Test that whitespace is trimmed before validation"""
        client, mock_db = test_client
        
        # Mock successful registration
        mock_db.register_callsign.return_value = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00',
            'position': 1
        }
        
        # Test with surrounding whitespace
        response = client.post('/api/queue/register', json={'callsign': '  KC1ABC  '})
        
        assert response.status_code == 200
        assert response.json()['message'] == 'Callsign registered successfully'
        
        # Verify the callsign was trimmed
        args, kwargs = mock_db.register_callsign.call_args
        assert args[0] == 'KC1ABC'  # First argument should be trimmed
    
    def test_empty_callsign_still_rejected(self, test_client):
        """Test that empty callsigns are still rejected (existing behavior)"""
        client, mock_db = test_client
        
        response = client.post('/api/queue/register', json={'callsign': ''})
        
        assert response.status_code == 400
        assert response.json()['detail'] == 'Callsign is required'
        # Database should not be called for empty callsign
        mock_db.register_callsign.assert_not_called()
    
    def test_whitespace_only_callsign_still_rejected(self, test_client):
        """Test that whitespace-only callsigns are still rejected (existing behavior)"""
        client, mock_db = test_client
        
        response = client.post('/api/queue/register', json={'callsign': '   '})
        
        assert response.status_code == 400
        assert response.json()['detail'] == 'Callsign is required'
        # Database should not be called for whitespace-only callsign
        mock_db.register_callsign.assert_not_called()
    
    def test_validation_happens_before_database_check(self, test_client):
        """Test that validation occurs before any database operations"""
        client, mock_db = test_client
        
        # Try to register an invalid callsign
        response = client.post('/api/queue/register', json={'callsign': 'INVALID123'})
        
        assert response.status_code == 400
        assert 'Invalid callsign format' in response.json()['detail']
        
        # Verify that no database operations were attempted
        mock_db.get_system_status.assert_not_called()
        mock_db.register_callsign.assert_not_called()
    
    def test_various_valid_international_callsigns(self, test_client):
        """Test various valid international callsign formats"""
        client, mock_db = test_client
        
        valid_callsigns = [
            'W1AW',    # US
            'VK2DEF',  # Australia  
            'G0ABC',   # UK
            'JA1XYZ',  # Japan
            'DL9ABC',  # Germany
            'W10ABC',  # Two-digit region
        ]
        
        for callsign in valid_callsigns:
            # Mock successful registration for each callsign
            mock_db.register_callsign.return_value = {
                'callsign': callsign,
                'timestamp': '2024-01-01T12:00:00',
                'position': 1
            }
            
            response = client.post('/api/queue/register', json={'callsign': callsign})
            
            assert response.status_code == 200, f"Failed for callsign: {callsign}"
            assert response.json()['message'] == 'Callsign registered successfully'
            
            # Reset mock for next iteration
            mock_db.reset_mock()