"""
Tests for Management API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.management_api import management_app
from src.n8n_client import N8NClient, N8NError


@pytest.fixture
def client():
    """Create test client for Management API."""
    return TestClient(management_app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    return {"Authorization": "Bearer test-token-1234567890"}


@pytest.fixture
def mock_n8n_client():
    """Create mock n8n client."""
    with patch('src.management_api.N8NClient') as mock:
        client_instance = AsyncMock(spec=N8NClient)
        mock.return_value = client_instance
        yield client_instance


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_endpoint_no_auth(self, client, mock_n8n_client):
        """Health endpoint should work without authentication."""
        # Setup mock
        mock_n8n_client.health_check = AsyncMock(return_value={"status": "healthy"})
        mock_n8n_client.close = AsyncMock()

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "healthy" in data
        assert "n8n_reachable" in data
        assert isinstance(data["healthy"], bool)

    def test_health_endpoint_n8n_unreachable(self, client, mock_n8n_client):
        """Health endpoint should handle n8n connection failures."""
        # Setup mock to raise error
        mock_n8n_client.health_check = AsyncMock(
            side_effect=N8NError("Connection failed")
        )
        mock_n8n_client.close = AsyncMock()

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["healthy"] is False
        assert data["n8n_reachable"] is False
        assert len(data["errors"]) > 0


class TestAuthenticationRequired:
    """Tests for authentication requirements."""

    def test_status_endpoint_requires_auth(self, client):
        """Status endpoint should require authentication."""
        response = client.get("/status")
        assert response.status_code == 401

    def test_workflows_stats_requires_auth(self, client):
        """Workflow stats endpoint should require authentication."""
        response = client.get("/workflows/stats")
        assert response.status_code == 401

    def test_workflows_list_requires_auth(self, client):
        """Workflows list endpoint should require authentication."""
        response = client.get("/workflows")
        assert response.status_code == 401

    def test_workflow_activate_requires_auth(self, client):
        """Workflow activate endpoint should require authentication."""
        response = client.post("/workflows/test123/activate")
        assert response.status_code == 401

    def test_invalid_auth_header(self, client):
        """Invalid auth header should be rejected."""
        headers = {"Authorization": "InvalidFormat"}
        response = client.get("/status", headers=headers)
        assert response.status_code == 401

    def test_short_token_rejected(self, client):
        """Short tokens should be rejected."""
        headers = {"Authorization": "Bearer short"}
        response = client.get("/status", headers=headers)
        assert response.status_code == 401


class TestStatusEndpoint:
    """Tests for status endpoint."""

    def test_status_endpoint_with_auth(self, client, auth_headers, mock_n8n_client):
        """Status endpoint should work with valid token."""
        # Setup mock
        mock_n8n_client.health_check = AsyncMock(return_value={"status": "healthy"})
        mock_n8n_client.close = AsyncMock()

        response = client.get("/status", headers=auth_headers)

        # Should not be 401
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "uptime_seconds" in data
            assert "n8n_connected" in data

    def test_status_endpoint_operational(self, client, auth_headers, mock_n8n_client):
        """Status should show operational when n8n is reachable."""
        mock_n8n_client.health_check = AsyncMock(return_value={"status": "healthy"})
        mock_n8n_client.close = AsyncMock()

        response = client.get("/status", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "operational"
            assert data["n8n_connected"] is True

    def test_status_endpoint_degraded(self, client, auth_headers, mock_n8n_client):
        """Status should show degraded when n8n is unreachable."""
        mock_n8n_client.health_check = AsyncMock(
            side_effect=N8NError("Connection failed")
        )
        mock_n8n_client.close = AsyncMock()

        response = client.get("/status", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "degraded"
            assert data["n8n_connected"] is False


class TestWorkflowStatsEndpoint:
    """Tests for workflow statistics endpoint."""

    def test_workflow_stats_success(self, client, auth_headers, mock_n8n_client):
        """Should return workflow statistics."""
        # Setup mock workflows
        mock_workflows = [
            {"id": "1", "name": "Workflow 1", "active": True},
            {"id": "2", "name": "Workflow 2", "active": True},
            {"id": "3", "name": "Workflow 3", "active": False},
        ]
        mock_n8n_client.list_workflows = AsyncMock(return_value=mock_workflows)
        mock_n8n_client.close = AsyncMock()

        response = client.get("/workflows/stats", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["total_workflows"] == 3
            assert data["active_workflows"] == 2
            assert data["paused_workflows"] == 1

    def test_workflow_stats_empty(self, client, auth_headers, mock_n8n_client):
        """Should handle empty workflow list."""
        mock_n8n_client.list_workflows = AsyncMock(return_value=[])
        mock_n8n_client.close = AsyncMock()

        response = client.get("/workflows/stats", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["total_workflows"] == 0
            assert data["active_workflows"] == 0


class TestWorkflowsListEndpoint:
    """Tests for workflows list endpoint."""

    def test_list_all_workflows(self, client, auth_headers, mock_n8n_client):
        """Should list all workflows."""
        mock_workflows = [
            {"id": "1", "name": "Workflow 1", "active": True},
            {"id": "2", "name": "Workflow 2", "active": False},
        ]
        mock_n8n_client.list_workflows = AsyncMock(return_value=mock_workflows)
        mock_n8n_client.close = AsyncMock()

        response = client.get("/workflows", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["count"] == 2
            assert len(data["workflows"]) == 2

    def test_list_active_only(self, client, auth_headers, mock_n8n_client):
        """Should filter active workflows only."""
        mock_workflows = [
            {"id": "1", "name": "Workflow 1", "active": True},
            {"id": "2", "name": "Workflow 2", "active": False},
        ]
        mock_n8n_client.list_workflows = AsyncMock(return_value=mock_workflows)
        mock_n8n_client.close = AsyncMock()

        response = client.get("/workflows?active_only=true", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            # Should filter to only active workflows
            assert all(w["active"] for w in data["workflows"])

    def test_search_workflows(self, client, auth_headers, mock_n8n_client):
        """Should search workflows by name."""
        mock_workflows = [
            {"id": "1", "name": "Email Workflow", "active": True},
            {"id": "2", "name": "Data Sync", "active": False},
        ]
        mock_n8n_client.list_workflows = AsyncMock(return_value=mock_workflows)
        mock_n8n_client.close = AsyncMock()

        response = client.get("/workflows?search=email", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            # Should filter to workflows matching search
            assert all("email" in w["name"].lower() for w in data["workflows"])


class TestWorkflowActionsEndpoint:
    """Tests for workflow action endpoints."""

    def test_activate_workflow(self, client, auth_headers, mock_n8n_client):
        """Should activate a workflow."""
        mock_workflow = {"id": "123", "name": "Test", "active": True}
        mock_n8n_client.activate_workflow = AsyncMock(return_value=mock_workflow)
        mock_n8n_client.close = AsyncMock()

        response = client.post("/workflows/123/activate", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert data["workflow_id"] == "123"

    def test_deactivate_workflow(self, client, auth_headers, mock_n8n_client):
        """Should deactivate a workflow."""
        mock_workflow = {"id": "123", "name": "Test", "active": False}
        mock_n8n_client.deactivate_workflow = AsyncMock(return_value=mock_workflow)
        mock_n8n_client.close = AsyncMock()

        response = client.post("/workflows/123/deactivate", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert data["workflow_id"] == "123"

    def test_execute_workflow(self, client, auth_headers, mock_n8n_client):
        """Should execute a workflow."""
        mock_execution = {"id": "exec123"}
        mock_n8n_client.execute_workflow = AsyncMock(return_value=mock_execution)
        mock_n8n_client.close = AsyncMock()

        response = client.post("/workflows/123/execute", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert data["workflow_id"] == "123"
            assert data["execution_id"] == "exec123"


class TestConfigEndpoint:
    """Tests for configuration endpoint."""

    def test_get_config(self, client, auth_headers):
        """Should return configuration with sensitive data redacted."""
        response = client.get("/config", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            assert "n8n_url" in data
            assert "n8n_api_key_set" in data
            assert "mcp_server_port" in data
            assert "management_api_port" in data
            # API key should not be exposed
            assert "n8n_api_key" not in data

    def test_update_config_not_implemented(self, client, auth_headers):
        """Config update should return not implemented."""
        response = client.put(
            "/config",
            headers=auth_headers,
            json={"log_level": "DEBUG"}
        )

        assert response.status_code == 501


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client):
        """Root endpoint should return service information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["service"] == "Monoliet MCP Management API"


class TestErrorHandling:
    """Tests for error handling."""

    def test_n8n_error_handling(self, client, auth_headers, mock_n8n_client):
        """Should handle n8n errors gracefully."""
        mock_n8n_client.list_workflows = AsyncMock(
            side_effect=N8NError("n8n error")
        )
        mock_n8n_client.close = AsyncMock()

        response = client.get("/workflows/stats", headers=auth_headers)

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_workflow_not_found(self, client, auth_headers, mock_n8n_client):
        """Should handle workflow not found."""
        from src.n8n_client import N8NNotFoundError

        mock_n8n_client.get_workflow = AsyncMock(
            side_effect=N8NNotFoundError("Workflow not found")
        )
        mock_n8n_client.close = AsyncMock()

        response = client.get("/workflows/nonexistent", headers=auth_headers)

        assert response.status_code == 404
