"""Tests for n8n client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.n8n_client import (
    N8NClient,
    N8NError,
    N8NConnectionError,
    N8NAuthError,
    N8NNotFoundError,
    N8NValidationError,
)
from src.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock(spec=Config)
    config.n8n_url = "http://localhost:5678"
    config.n8n_api_key = "test-api-key"
    config.n8n_timeout = 30
    config.n8n_max_retries = 3
    config.get_n8n_api_base_url.return_value = "http://localhost:5678/api/v1"
    config.get_n8n_headers.return_value = {
        "X-N8N-API-KEY": "test-api-key",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return config


@pytest.fixture
async def n8n_client(mock_config):
    """Create an n8n client instance."""
    client = N8NClient(mock_config)
    yield client
    await client.close()


class TestN8NClient:
    """Test suite for N8NClient."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_config):
        """Test client initialization."""
        client = N8NClient(mock_config)
        assert client.config == mock_config
        assert client.base_url == "http://localhost:5678/api/v1"
        await client.close()

    @pytest.mark.asyncio
    async def test_health_check_success(self, n8n_client):
        """Test successful health check."""
        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"data": []}

            health = await n8n_client.health_check()

            assert health["status"] == "healthy"
            assert "Successfully connected" in health["message"]
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, n8n_client):
        """Test failed health check."""
        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = N8NConnectionError("Connection failed")

            with pytest.raises(N8NConnectionError):
                await n8n_client.health_check()

    @pytest.mark.asyncio
    async def test_list_workflows(self, n8n_client):
        """Test listing workflows."""
        mock_workflows = [
            {"id": "1", "name": "Workflow 1", "active": True},
            {"id": "2", "name": "Workflow 2", "active": False}
        ]

        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"data": mock_workflows}

            workflows = await n8n_client.list_workflows()

            assert len(workflows) == 2
            assert workflows[0]["name"] == "Workflow 1"
            mock_request.assert_called_once_with("GET", "/workflows", params={})

    @pytest.mark.asyncio
    async def test_list_workflows_with_filter(self, n8n_client):
        """Test listing workflows with active filter."""
        mock_workflows = [{"id": "1", "name": "Workflow 1", "active": True}]

        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"data": mock_workflows}

            workflows = await n8n_client.list_workflows(active=True)

            assert len(workflows) == 1
            mock_request.assert_called_once_with(
                "GET", "/workflows", params={"active": "true"}
            )

    @pytest.mark.asyncio
    async def test_get_workflow(self, n8n_client):
        """Test getting a specific workflow."""
        mock_workflow = {
            "id": "1",
            "name": "Test Workflow",
            "active": True,
            "nodes": []
        }

        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_workflow

            workflow = await n8n_client.get_workflow("1")

            assert workflow["name"] == "Test Workflow"
            mock_request.assert_called_once_with("GET", "/workflows/1")

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, n8n_client):
        """Test getting non-existent workflow."""
        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = N8NNotFoundError("Workflow not found")

            with pytest.raises(N8NNotFoundError):
                await n8n_client.get_workflow("999")

    @pytest.mark.asyncio
    async def test_create_workflow(self, n8n_client):
        """Test creating a workflow."""
        workflow_data = {
            "name": "New Workflow",
            "nodes": [],
            "connections": {},
            "active": False
        }

        mock_created = {**workflow_data, "id": "123"}

        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_created

            workflow = await n8n_client.create_workflow(workflow_data)

            assert workflow["id"] == "123"
            assert workflow["name"] == "New Workflow"
            mock_request.assert_called_once_with(
                "POST", "/workflows", json=workflow_data
            )

    @pytest.mark.asyncio
    async def test_update_workflow(self, n8n_client):
        """Test updating a workflow."""
        workflow_data = {"name": "Updated Workflow"}

        mock_updated = {
            "id": "1",
            "name": "Updated Workflow",
            "active": True
        }

        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_updated

            workflow = await n8n_client.update_workflow("1", workflow_data)

            assert workflow["name"] == "Updated Workflow"
            mock_request.assert_called_once_with(
                "PUT", "/workflows/1", json=workflow_data
            )

    @pytest.mark.asyncio
    async def test_delete_workflow(self, n8n_client):
        """Test deleting a workflow."""
        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}

            result = await n8n_client.delete_workflow("1")

            assert result is True
            mock_request.assert_called_once_with("DELETE", "/workflows/1")

    @pytest.mark.asyncio
    async def test_activate_workflow(self, n8n_client):
        """Test activating a workflow."""
        mock_workflow = {"id": "1", "name": "Test", "active": False}
        mock_updated = {**mock_workflow, "active": True}

        with patch.object(n8n_client, 'get_workflow', new_callable=AsyncMock) as mock_get:
            with patch.object(n8n_client, 'update_workflow', new_callable=AsyncMock) as mock_update:
                mock_get.return_value = mock_workflow
                mock_update.return_value = mock_updated

                workflow = await n8n_client.activate_workflow("1")

                assert workflow["active"] is True
                mock_get.assert_called_once_with("1")
                mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_workflow(self, n8n_client):
        """Test deactivating a workflow."""
        mock_workflow = {"id": "1", "name": "Test", "active": True}
        mock_updated = {**mock_workflow, "active": False}

        with patch.object(n8n_client, 'get_workflow', new_callable=AsyncMock) as mock_get:
            with patch.object(n8n_client, 'update_workflow', new_callable=AsyncMock) as mock_update:
                mock_get.return_value = mock_workflow
                mock_update.return_value = mock_updated

                workflow = await n8n_client.deactivate_workflow("1")

                assert workflow["active"] is False
                mock_get.assert_called_once_with("1")
                mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_workflow(self, n8n_client):
        """Test executing a workflow."""
        mock_execution = {
            "id": "exec-1",
            "workflowId": "1",
            "finished": True,
            "mode": "manual"
        }

        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_execution

            execution = await n8n_client.execute_workflow("1", {"input": "test"})

            assert execution["id"] == "exec-1"
            mock_request.assert_called_once_with(
                "POST",
                "/workflows/1/execute",
                json={"data": {"input": "test"}}
            )

    @pytest.mark.asyncio
    async def test_get_executions(self, n8n_client):
        """Test getting executions."""
        mock_executions = [
            {"id": "exec-1", "finished": True},
            {"id": "exec-2", "finished": False}
        ]

        with patch.object(n8n_client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"data": mock_executions}

            executions = await n8n_client.get_executions(limit=10)

            assert len(executions) == 2
            mock_request.assert_called_once_with(
                "GET", "/executions", params={"limit": 10}
            )

    @pytest.mark.asyncio
    async def test_search_workflows(self, n8n_client):
        """Test searching workflows."""
        mock_workflows = [
            {"id": "1", "name": "Email Workflow", "tags": ["email"]},
            {"id": "2", "name": "Data Sync", "tags": ["email", "sync"]},
            {"id": "3", "name": "Notification", "tags": ["notify"]}
        ]

        with patch.object(n8n_client, 'list_workflows', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = mock_workflows

            results = await n8n_client.search_workflows("email")

            assert len(results) == 2
            assert results[0]["name"] == "Email Workflow"
            assert results[1]["name"] == "Data Sync"

    @pytest.mark.asyncio
    async def test_get_workflow_statistics(self, n8n_client):
        """Test getting workflow statistics."""
        mock_executions = [
            {"id": "1", "finished": True, "stoppedAt": None},
            {"id": "2", "finished": True, "stoppedAt": None},
            {"id": "3", "finished": False, "stoppedAt": "2024-01-01"},
        ]

        with patch.object(n8n_client, 'get_executions', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_executions

            stats = await n8n_client.get_workflow_statistics("1", limit=100)

            assert stats["total_executions"] == 3
            assert stats["success_count"] == 2
            assert stats["error_count"] == 1
            assert stats["success_rate"] == 66.67

    @pytest.mark.asyncio
    async def test_auth_error_handling(self, n8n_client):
        """Test authentication error handling."""
        with patch.object(n8n_client.client, 'request', new_callable=AsyncMock) as mock_request:
            response = MagicMock()
            response.status_code = 401
            response.json.return_value = {"message": "Unauthorized"}
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=response
            )
            mock_request.return_value = response

            with pytest.raises(N8NAuthError):
                await n8n_client._request("GET", "/workflows")
