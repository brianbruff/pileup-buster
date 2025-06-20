"""Integration tests for frequency management API endpoints"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.app import app
from app.database import queue_db
from app.services.events import event_broadcaster


class TestFrequencyEndpoints:
    """Test frequency management API endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
        
    @patch('app.routes.public.queue_db')
    def test_get_frequency_public_endpoint_none_exists(self, mock_db):
        """Test public frequency endpoint when no frequency is set"""
        mock_db.get_frequency.return_value = None
        
        response = self.client.get("/api/public/frequency")
        
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] is None
        assert data["last_updated"] is None
        
    @patch('app.routes.public.queue_db')
    def test_get_frequency_public_endpoint_exists(self, mock_db):
        """Test public frequency endpoint when frequency exists"""
        mock_frequency_data = {
            "frequency": "146.520 MHz",
            "last_updated": "2024-01-01T12:00:00",
            "updated_by": "admin"
        }
        mock_db.get_frequency.return_value = mock_frequency_data
        
        response = self.client.get("/api/public/frequency")
        
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "146.520 MHz"
        assert data["last_updated"] == "2024-01-01T12:00:00"
        # Should NOT include updated_by for public consumption
        assert "updated_by" not in data
        
    @patch('app.routes.public.queue_db')
    def test_get_frequency_public_endpoint_database_error(self, mock_db):
        """Test public frequency endpoint with database error"""
        mock_db.get_frequency.side_effect = Exception("Database error")
        
        response = self.client.get("/api/public/frequency")
        
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]
        
    @patch('app.routes.admin.queue_db')
    @patch('app.routes.admin.event_broadcaster')
    @patch('app.auth.verify_admin_credentials')
    def test_set_frequency_admin_endpoint_success(self, mock_auth, mock_broadcaster, mock_db):
        """Test admin frequency setting endpoint - success"""
        # Mock authentication
        mock_auth.return_value = "test-admin"
        
        # Mock database response
        mock_frequency_data = {
            "frequency": "146.520 MHz",
            "last_updated": "2024-01-01T12:00:00",
            "updated_by": "test-admin"
        }
        mock_db.set_frequency.return_value = mock_frequency_data
        
        # Mock broadcaster
        mock_broadcaster.broadcast_frequency_update = AsyncMock()
        
        response = self.client.post(
            "/api/admin/frequency",
            json={"frequency": "146.520 MHz"},
            auth=("admin", "password")
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Frequency set to 146.520 MHz"
        assert data["frequency_data"] == mock_frequency_data
        
        # Verify database was called
        mock_db.set_frequency.assert_called_once_with("146.520 MHz", "test-admin")
        
    @patch('app.routes.admin.queue_db')
    @patch('app.auth.verify_admin_credentials')
    def test_set_frequency_admin_endpoint_auth_required(self, mock_auth, mock_db):
        """Test admin frequency setting endpoint requires authentication"""
        # Don't mock auth to test auth failure
        response = self.client.post(
            "/api/admin/frequency",
            json={"frequency": "146.520 MHz"}
        )
        
        # Should return 401 or 403 for missing auth
        assert response.status_code in [401, 403, 422]  # Depending on FastAPI auth setup
        
    @patch('app.routes.admin.queue_db')
    @patch('app.auth.verify_admin_credentials')
    def test_set_frequency_admin_endpoint_invalid_request(self, mock_auth, mock_db):
        """Test admin frequency setting endpoint with invalid request"""
        mock_auth.return_value = "test-admin"
        
        response = self.client.post(
            "/api/admin/frequency",
            json={},  # Missing frequency field
            auth=("admin", "password")
        )
        
        assert response.status_code == 422  # Validation error
        
    @patch('app.routes.admin.queue_db')
    @patch('app.auth.verify_admin_credentials')
    def test_set_frequency_admin_endpoint_database_error(self, mock_auth, mock_db):
        """Test admin frequency setting endpoint with database error"""
        mock_auth.return_value = "test-admin"
        mock_db.set_frequency.side_effect = Exception("Database error")
        
        response = self.client.post(
            "/api/admin/frequency",
            json={"frequency": "146.520 MHz"},
            auth=("admin", "password")
        )
        
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]
        
    @patch('app.routes.admin.queue_db')
    @patch('app.auth.verify_admin_credentials')
    def test_set_frequency_empty_string(self, mock_auth, mock_db):
        """Test setting frequency to empty string"""
        mock_auth.return_value = "test-admin"
        mock_db.set_frequency.return_value = {
            "frequency": "",
            "last_updated": "2024-01-01T12:00:00",
            "updated_by": "test-admin"
        }
        
        response = self.client.post(
            "/api/admin/frequency",
            json={"frequency": ""},
            auth=("admin", "password")
        )
        
        assert response.status_code == 200
        mock_db.set_frequency.assert_called_once_with("", "test-admin")
        
    @patch('app.routes.admin.queue_db')
    @patch('app.auth.verify_admin_credentials')
    def test_set_frequency_whitespace_handling(self, mock_auth, mock_db):
        """Test setting frequency with whitespace"""
        mock_auth.return_value = "test-admin"
        mock_db.set_frequency.return_value = {
            "frequency": "  146.520 MHz  ",
            "last_updated": "2024-01-01T12:00:00",
            "updated_by": "test-admin"
        }
        
        response = self.client.post(
            "/api/admin/frequency",
            json={"frequency": "  146.520 MHz  "},
            auth=("admin", "password")
        )
        
        assert response.status_code == 200
        # Should preserve the whitespace as submitted
        mock_db.set_frequency.assert_called_once_with("  146.520 MHz  ", "test-admin")


class TestFrequencyEndpointIntegration:
    """Test frequency endpoints with real app integration"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
        
    def test_public_frequency_endpoint_exists(self):
        """Test that public frequency endpoint exists and is accessible"""
        # This test will fail if database is not available, but that's expected
        # We're testing that the endpoint exists and handles the error gracefully
        response = self.client.get("/api/public/frequency")
        
        # Should either return 200 with data or 500 with database error
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "frequency" in data
            assert "last_updated" in data
        else:
            # Database error case
            assert "detail" in response.json()
    
    def test_admin_frequency_endpoint_exists(self):
        """Test that admin frequency endpoint exists"""
        # This should fail with 401/403/422 since we're not providing auth
        response = self.client.post(
            "/api/admin/frequency",
            json={"frequency": "146.520 MHz"}
        )
        
        # Should not be 404 (endpoint exists) but should be auth-related error
        assert response.status_code in [401, 403, 422]
        assert response.status_code != 404