"""Execution management tools for MCP server."""

import logging
from typing import Any, Dict, Optional

from src.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ExecuteWorkflowTool(BaseTool):
    """Manually execute an n8n workflow."""

    name = "execute_workflow"
    description = (
        "Manually trigger execution of an n8n workflow. You can optionally "
        "provide input data to be passed to the workflow execution."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "ID of the workflow to execute"
            },
            "data": {
                "type": "object",
                "description": "Optional input data to pass to the workflow",
                "default": {}
            }
        },
        "required": ["workflow_id"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to trigger workflow execution."""
        self._validate_required_args(arguments, ["workflow_id"])

        workflow_id = arguments["workflow_id"]
        input_data = arguments.get("data")

        # Execute workflow
        execution = await self.n8n_client.execute_workflow(
            workflow_id=workflow_id,
            data=input_data
        )

        # Extract execution information
        execution_id = execution.get("id")
        finished = execution.get("finished", False)
        mode = execution.get("mode", "manual")
        started_at = execution.get("startedAt")
        stopped_at = execution.get("stoppedAt")

        # Determine execution status
        if stopped_at:
            status = "error"
        elif finished:
            status = "success"
        else:
            status = "running"

        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": status,
            "mode": mode,
            "started_at": started_at,
            "stopped_at": stopped_at,
            "finished": finished,
            "data": execution.get("data"),
            "message": f"Workflow execution {status}: {execution_id}"
        }


class GetExecutionsTool(BaseTool):
    """Get execution history for workflows."""

    name = "get_executions"
    description = (
        "Get execution history for n8n workflows. You can filter by workflow ID, "
        "status, and limit the number of results. Useful for monitoring workflow "
        "performance and debugging issues."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "Filter executions by workflow ID (optional)"
            },
            "status": {
                "type": "string",
                "enum": ["success", "error", "waiting", "all"],
                "description": "Filter executions by status",
                "default": "all"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of executions to return",
                "default": 20,
                "minimum": 1,
                "maximum": 250
            },
            "include_data": {
                "type": "boolean",
                "description": "Include full execution data in response",
                "default": False
            }
        }
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to get execution history."""
        workflow_id = arguments.get("workflow_id")
        status_filter = arguments.get("status", "all")
        limit = arguments.get("limit", 20)
        include_data = arguments.get("include_data", False)

        # Validate limit
        if limit < 1 or limit > 250:
            raise ValueError("Limit must be between 1 and 250")

        # Determine status filter for API
        status_param: Optional[str] = None
        if status_filter != "all":
            status_param = status_filter

        # Get executions from n8n
        executions = await self.n8n_client.get_executions(
            workflow_id=workflow_id,
            limit=limit,
            status=status_param
        )

        # Format executions
        formatted_executions = []
        for execution in executions:
            exec_data = {
                "id": execution.get("id"),
                "workflow_id": execution.get("workflowId"),
                "workflow_name": execution.get("workflowData", {}).get("name"),
                "mode": execution.get("mode"),
                "started_at": execution.get("startedAt"),
                "stopped_at": execution.get("stoppedAt"),
                "finished": execution.get("finished", False),
                "status": self._determine_status(execution)
            }

            # Include full data if requested
            if include_data:
                exec_data["data"] = execution.get("data")
                exec_data["execution_data"] = execution.get("executionData")

            formatted_executions.append(exec_data)

        # Calculate summary statistics
        total = len(formatted_executions)
        success_count = sum(1 for e in formatted_executions if e["status"] == "success")
        error_count = sum(1 for e in formatted_executions if e["status"] == "error")
        running_count = sum(1 for e in formatted_executions if e["status"] == "running")

        return {
            "total_count": total,
            "success_count": success_count,
            "error_count": error_count,
            "running_count": running_count,
            "filters": {
                "workflow_id": workflow_id,
                "status": status_filter,
                "limit": limit
            },
            "executions": formatted_executions
        }

    def _determine_status(self, execution: Dict[str, Any]) -> str:
        """Determine execution status from execution data.

        Args:
            execution: Execution object from n8n API

        Returns:
            Status string: 'success', 'error', or 'running'
        """
        stopped_at = execution.get("stoppedAt")
        finished = execution.get("finished", False)

        if stopped_at:
            return "error"
        elif finished:
            return "success"
        else:
            return "running"
