"""Health and monitoring tools for MCP server."""

import logging
from typing import Any, Dict

from src.tools.base import BaseTool

logger = logging.getLogger(__name__)


class GetWorkflowHealthTool(BaseTool):
    """Get health statistics for a workflow."""

    name = "get_workflow_health"
    description = (
        "Get health and performance statistics for a specific n8n workflow. "
        "Returns success rate, error rate, and execution counts based on "
        "recent execution history. Useful for monitoring workflow reliability."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "ID of the workflow to check health for"
            },
            "limit": {
                "type": "integer",
                "description": "Number of recent executions to analyze",
                "default": 100,
                "minimum": 10,
                "maximum": 1000
            }
        },
        "required": ["workflow_id"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to get workflow health statistics."""
        self._validate_required_args(arguments, ["workflow_id"])

        workflow_id = arguments["workflow_id"]
        limit = arguments.get("limit", 100)

        # Validate limit
        if limit < 10 or limit > 1000:
            raise ValueError("Limit must be between 10 and 1000")

        # Get workflow information
        workflow = await self.n8n_client.get_workflow(workflow_id)
        workflow_name = workflow.get("name", "Unknown")
        is_active = workflow.get("active", False)

        # Get execution statistics
        stats = await self.n8n_client.get_workflow_statistics(
            workflow_id=workflow_id,
            limit=limit
        )

        # Determine health status based on error rate
        error_rate = stats.get("error_rate", 0.0)
        if error_rate == 0:
            health_status = "excellent"
        elif error_rate < 5:
            health_status = "good"
        elif error_rate < 20:
            health_status = "fair"
        else:
            health_status = "poor"

        # Build comprehensive health report
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "is_active": is_active,
            "health_status": health_status,
            "statistics": {
                "total_executions": stats.get("total_executions", 0),
                "success_count": stats.get("success_count", 0),
                "error_count": stats.get("error_count", 0),
                "waiting_count": stats.get("waiting_count", 0),
                "success_rate": stats.get("success_rate", 0.0),
                "error_rate": stats.get("error_rate", 0.0),
                "analyzed_executions": stats.get("analyzed_executions", limit)
            },
            "recommendations": self._generate_recommendations(
                error_rate=error_rate,
                total_executions=stats.get("total_executions", 0),
                is_active=is_active
            )
        }

    def _generate_recommendations(
        self,
        error_rate: float,
        total_executions: int,
        is_active: bool
    ) -> list[str]:
        """Generate health recommendations based on statistics.

        Args:
            error_rate: Error rate percentage
            total_executions: Total number of executions
            is_active: Whether workflow is active

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if error_rate > 20:
            recommendations.append(
                "High error rate detected. Review workflow logs and fix failing nodes."
            )
        elif error_rate > 5:
            recommendations.append(
                "Moderate error rate. Consider investigating recent failures."
            )

        if total_executions == 0:
            if is_active:
                recommendations.append(
                    "No executions found. Verify workflow triggers are configured correctly."
                )
            else:
                recommendations.append(
                    "Workflow is inactive and has no executions. Activate to start processing."
                )

        if total_executions > 0 and error_rate == 0:
            recommendations.append(
                "Excellent! Workflow is running smoothly with no errors."
            )

        if not recommendations:
            recommendations.append(
                "Workflow health is good. Continue monitoring for any issues."
            )

        return recommendations
