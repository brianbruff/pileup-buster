"""Tests for DXCC name extraction from QRZ lookups"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.app import create_app


@pytest.fixture
def test_app():
    """Create a test app instance"""
    return create_app()


@pytest.fixture
def test_client(test_app):
    """Create a test client"""
    return TestClient(test_app)


class TestDXCCNameExtraction:
    """Test DXCC name extraction functionality"""

    @patch('app.routes.queue.queue_db')
    @patch('app.routes.queue.qrz_service')
    def test_qrz_service_includes_dxcc_name_on_success(self, mock_qrz_service, mock_db, test_client):
        """Test that QRZ service includes DXCC name when lookup succeeds"""
        # Mock active system status
        mock_db.get_system_status.return_value = {'active': True}
        
        # Mock QRZ service success with DXCC name
        mock_qrz_info = {
            'callsign': 'KC1ABC',
            'name': 'John Doe',
            'address': '123 Main St, City, State, Country',
            'dxcc_name': 'United States',
            'image': 'http://example.com/image.jpg',
            'error': None
        }
        mock_qrz_service.lookup_callsign.return_value = mock_qrz_info
        
        # Mock database registration response
        mock_entry = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z',
            'position': 1,
            'qrz': mock_qrz_info
        }
        mock_db.register_callsign.return_value = mock_entry
        
        # Make registration request
        response = test_client.post('/api/queue/register', json={'callsign': 'KC1ABC'})
        
        # Verify response includes DXCC name
        assert response.status_code == 200
        data = response.json()
        assert data['entry']['qrz']['dxcc_name'] == 'United States'
        
        # Verify QRZ service was called and database was updated with DXCC name
        mock_qrz_service.lookup_callsign.assert_called_once_with('KC1ABC')
        mock_db.register_callsign.assert_called_once_with('KC1ABC', mock_qrz_info)

    @patch('app.routes.queue.queue_db')
    @patch('app.routes.queue.qrz_service')
    def test_qrz_service_includes_dxcc_name_none_on_failure(self, mock_qrz_service, mock_db, test_client):
        """Test that QRZ service includes dxcc_name: None when lookup fails"""
        # Mock active system status
        mock_db.get_system_status.return_value = {'active': True}
        
        # Mock QRZ service failure
        mock_qrz_info = {
            'callsign': 'KC1ABC',
            'name': None,
            'address': None,
            'dxcc_name': None,
            'image': None,
            'error': 'QRZ.com credentials not configured. Please set QRZ_USERNAME and QRZ_PASSWORD environment variables.'
        }
        mock_qrz_service.lookup_callsign.return_value = mock_qrz_info
        
        # Mock database registration response
        mock_entry = {
            'callsign': 'KC1ABC',
            'timestamp': '2024-01-01T12:00:00Z',
            'position': 1,
            'qrz': mock_qrz_info
        }
        mock_db.register_callsign.return_value = mock_entry
        
        # Make registration request
        response = test_client.post('/api/queue/register', json={'callsign': 'KC1ABC'})
        
        # Verify response includes dxcc_name: None
        assert response.status_code == 200
        data = response.json()
        assert data['entry']['qrz']['dxcc_name'] is None
        
        # Verify QRZ service was called and database was updated with dxcc_name: None
        mock_qrz_service.lookup_callsign.assert_called_once_with('KC1ABC')
        mock_db.register_callsign.assert_called_once_with('KC1ABC', mock_qrz_info)