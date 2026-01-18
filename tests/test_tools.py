"""Tests for MCP tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.n8n_client import N8NClient, N8NNotFoundError
from src.tools.workflows import (
    ListWorkflowsTool,
    GetWorkflowDetailsTool,
    SearchWorkflowsTool,
    ActivateWorkflowTool,
)
from src.tools.executions import ExecuteWorkflowTool, GetExecutionsTool
from src.tools.health import GetWorkflowHealthTool


@pytest.fixture
def mock_n8n_client():
    """Create a mock n8n client."""
    return MagicMock(spec=N8NClient)


class TestListWorkflowsTool:
    """Test suite for ListWorkflowsTool."""

    @pytest.mark.asyncio
    async def test_list_all_workflows(self, mock_n8n_client):
        """Test listing all workflows."""
        mock_workflows = [
            {"id": "1", "name": "Workflow 1", "active": True, "tags": []},
            {"id": "2", "name": "Workflow 2", "active": False, "tags": ["test"]}
        ]
        mock_n8n_client.list_workflows = AsyncMock(return_value=mock_workflows)

        tool = ListWorkflowsTool(mock_n8n_client)
        result = await tool.run({"status": "all"})

        assert result["success"] is True
        assert result["data"]["total_count"] == 2
        assert len(result["data"]["workflows"]) == 2

    @pytest.mark.asyncio
    async def test_list_active_workflows(self, mock_n8n_client):
        """Test listing only active workflows."""
        mock_workflows = [
            {"id": "1", "name": "Workflow 1", "active": True, "tags": []}
        ]
        mock_n8n_client.list_workflows = AsyncMock(return_value=mock_workflows)

        tool = ListWorkflowsTool(mock_n8n_client)
        result = await tool.run({"status": "active"})

        assert result["success"] is True
        assert result["data"]["filter"] == "active"
        mock_n8n_client.list_workflows.assert_called_once_with(active=True)

    @pytest.mark.asyncio
    async def test_list_workflows_error(self, mock_n8n_client):
        """Test error handling in list workflows."""
        mock_n8n_client.list_workflows = AsyncMock(
            side_effect=Exception("Connection error")
        )

        tool = ListWorkflowsTool(mock_n8n_client)
        result = await tool.run({"status": "all"})

        assert result["success"] is False
        assert "error" in result
        assert "Connection error" in result["error"]["message"]


class TestGetWorkflowDetailsTool:
    """Test suite for GetWorkflowDetailsTool."""

    @pytest.mark.asyncio
    async def test_get_workflow_details(self, mock_n8n_client):
        """Test getting workflow details."""
        mock_workflow = {
            "id": "1",
            "name": "Test Workflow",
            "active": True,
            "nodes": [{"id": "node1"}],
            "connections": {},
            "tags": ["test"]
        }
        mock_n8n_client.get_workflow = AsyncMock(return_value=mock_workflow)

        tool = GetWorkflowDetailsTool(mock_n8n_client)
        result = await tool.run({"workflow_id": "1"})

        assert result["success"] is True
        assert result["data"]["name"] == "Test Workflow"
        assert result["data"]["node_count"] == 1

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, mock_n8n_client):
        """Test getting non-existent workflow."""
        mock_n8n_client.get_workflow = AsyncMock(
            side_effect=N8NNotFoundError("Workflow not found")
        )

        tool = GetWorkflowDetailsTool(mock_n8n_client)
        result = await tool.run({"workflow_id": "999"})

        assert result["success"] is False
        assert result["error"]["type"] == "n8n_error"

    @pytest.mark.asyncio
    async def test_missing_workflow_id(self, mock_n8n_client):
        """Test error when workflow_id is missing."""
        tool = GetWorkflowDetailsTool(mock_n8n_client)
        result = await tool.run({})

        assert result["success"] is False
        assert result["error"]["type"] == "validation_error"


class TestSearchWorkflowsTool:
    """Test suite for SearchWorkflowsTool."""

    @pytest.mark.asyncio
    async def test_search_workflows(self, mock_n8n_client):
        """Test searching workflows."""
        mock_workflows = [
            {"id": "1", "name": "Email Workflow", "active": True, "tags": []},
            {"id": "2", "name": "Email Sync", "active": False, "tags": ["email"]}
        ]
        mock_n8n_client.search_workflows = AsyncMock(return_value=mock_workflows)

        tool = SearchWorkflowsTool(mock_n8n_client)
        result = await tool.run({"query": "email"})

        assert result["success"] is True
        assert result["data"]["total_matches"] == 2
        assert result["data"]["query"] == "email"

    @pytest.mark.asyncio
    async def test_search_active_only(self, mock_n8n_client):
        """Test searching only active workflows."""
        mock_workflows = [
            {"id": "1", "name": "Email Workflow", "active": True, "tags": []}
        ]
        mock_n8n_client.search_workflows = AsyncMock(return_value=mock_workflows)

        tool = SearchWorkflowsTool(mock_n8n_client)
        result = await tool.run({"query": "email", "active_only": True})

        assert result["success"] is True
        mock_n8n_client.search_workflows.assert_called_once_with("email", active=True)


class TestActivateWorkflowTool:
    """Test suite for ActivateWorkflowTool."""

    @pytest.mark.asyncio
    async def test_activate_workflow(self, mock_n8n_client):
        """Test activating a workflow."""
        mock_workflow = {
            "id": "1",
            "name": "Test Workflow",
            "active": True
        }
        mock_n8n_client.activate_workflow = AsyncMock(return_value=mock_workflow)

        tool = ActivateWorkflowTool(mock_n8n_client)
        result = await tool.run({"workflow_id": "1"})

        assert result["success"] is True
        assert result["data"]["active"] is True
        assert "Successfully activated" in result["data"]["message"]


class TestExecuteWorkflowTool:
    """Test suite for ExecuteWorkflowTool."""

    @pytest.mark.asyncio
    async def test_execute_workflow(self, mock_n8n_client):
        """Test executing a workflow."""
        mock_execution = {
            "id": "exec-1",
            "workflowId": "1",
            "finished": True,
            "mode": "manual",
            "startedAt": "2024-01-01T00:00:00Z"
        }
        mock_n8n_client.execute_workflow = AsyncMock(return_value=mock_execution)

        tool = ExecuteWorkflowTool(mock_n8n_client)
        result = await tool.run({"workflow_id": "1"})

        assert result["success"] is True
        assert result["data"]["execution_id"] == "exec-1"
        assert result["data"]["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_workflow_with_data(self, mock_n8n_client):
        """Test executing a workflow with input data."""
        mock_execution = {
            "id": "exec-1",
            "workflowId": "1",
            "finished": True,
            "mode": "manual",
            "startedAt": "2024-01-01T00:00:00Z"
        }
        mock_n8n_client.execute_workflow = AsyncMock(return_value=mock_execution)

        tool = ExecuteWorkflowTool(mock_n8n_client)
        input_data = {"test": "data"}
        result = await tool.run({"workflow_id": "1", "data": input_data})

        assert result["success"] is True
        mock_n8n_client.execute_workflow.assert_called_once_with(
            workflow_id="1",
            data=input_data
        )


class TestGetExecutionsTool:
    """Test suite for GetExecutionsTool."""

    @pytest.mark.asyncio
    async def test_get_executions(self, mock_n8n_client):
        """Test getting executions."""
        mock_executions = [
            {
                "id": "exec-1",
                "workflowId": "1",
                "finished": True,
                "mode": "manual",
                "startedAt": "2024-01-01T00:00:00Z"
            },
            {
                "id": "exec-2",
                "workflowId": "1",
                "finished": False,
                "mode": "trigger",
                "startedAt": "2024-01-01T01:00:00Z"
            }
        ]
        mock_n8n_client.get_executions = AsyncMock(return_value=mock_executions)

        tool = GetExecutionsTool(mock_n8n_client)
        result = await tool.run({"limit": 20})

        assert result["success"] is True
        assert result["data"]["total_count"] == 2
        assert result["data"]["success_count"] == 1
        assert result["data"]["running_count"] == 1

    @pytest.mark.asyncio
    async def test_get_executions_with_workflow_filter(self, mock_n8n_client):
        """Test getting executions filtered by workflow."""
        mock_executions = [
            {
                "id": "exec-1",
                "workflowId": "1",
                "finished": True,
                "mode": "manual",
                "startedAt": "2024-01-01T00:00:00Z"
            }
        ]
        mock_n8n_client.get_executions = AsyncMock(return_value=mock_executions)

        tool = GetExecutionsTool(mock_n8n_client)
        result = await tool.run({"workflow_id": "1", "limit": 20})

        assert result["success"] is True
        mock_n8n_client.get_executions.assert_called_once_with(
            workflow_id="1",
            limit=20,
            status=None
        )

    @pytest.mark.asyncio
    async def test_get_executions_invalid_limit(self, mock_n8n_client):
        """Test error with invalid limit."""
        tool = GetExecutionsTool(mock_n8n_client)
        result = await tool.run({"limit": 999})

        assert result["success"] is False
        assert result["error"]["type"] == "validation_error"


class TestGetWorkflowHealthTool:
    """Test suite for GetWorkflowHealthTool."""

    @pytest.mark.asyncio
    async def test_get_workflow_health(self, mock_n8n_client):
        """Test getting workflow health."""
        mock_workflow = {
            "id": "1",
            "name": "Test Workflow",
            "active": True
        }
        mock_stats = {
            "workflow_id": "1",
            "total_executions": 100,
            "success_count": 95,
            "error_count": 5,
            "waiting_count": 0,
            "success_rate": 95.0,
            "error_rate": 5.0,
            "analyzed_executions": 100
        }

        mock_n8n_client.get_workflow = AsyncMock(return_value=mock_workflow)
        mock_n8n_client.get_workflow_statistics = AsyncMock(return_value=mock_stats)

        tool = GetWorkflowHealthTool(mock_n8n_client)
        result = await tool.run({"workflow_id": "1", "limit": 100})

        assert result["success"] is True
        assert result["data"]["health_status"] == "good"
        assert result["data"]["statistics"]["success_rate"] == 95.0
        assert len(result["data"]["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_get_workflow_health_excellent(self, mock_n8n_client):
        """Test workflow with excellent health."""
        mock_workflow = {
            "id": "1",
            "name": "Test Workflow",
            "active": True
        }
        mock_stats = {
            "workflow_id": "1",
            "total_executions": 100,
            "success_count": 100,
            "error_count": 0,
            "waiting_count": 0,
            "success_rate": 100.0,
            "error_rate": 0.0,
            "analyzed_executions": 100
        }

        mock_n8n_client.get_workflow = AsyncMock(return_value=mock_workflow)
        mock_n8n_client.get_workflow_statistics = AsyncMock(return_value=mock_stats)

        tool = GetWorkflowHealthTool(mock_n8n_client)
        result = await tool.run({"workflow_id": "1"})

        assert result["success"] is True
        assert result["data"]["health_status"] == "excellent"

    @pytest.mark.asyncio
    async def test_get_workflow_health_poor(self, mock_n8n_client):
        """Test workflow with poor health."""
        mock_workflow = {
            "id": "1",
            "name": "Test Workflow",
            "active": True
        }
        mock_stats = {
            "workflow_id": "1",
            "total_executions": 100,
            "success_count": 60,
            "error_count": 40,
            "waiting_count": 0,
            "success_rate": 60.0,
            "error_rate": 40.0,
            "analyzed_executions": 100
        }

        mock_n8n_client.get_workflow = AsyncMock(return_value=mock_workflow)
        mock_n8n_client.get_workflow_statistics = AsyncMock(return_value=mock_stats)

        tool = GetWorkflowHealthTool(mock_n8n_client)
        result = await tool.run({"workflow_id": "1"})

        assert result["success"] is True
        assert result["data"]["health_status"] == "poor"
        # Should have recommendation about high error rate
        assert any("High error rate" in rec for rec in result["data"]["recommendations"])
