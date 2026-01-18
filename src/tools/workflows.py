"""Workflow management tools for MCP server."""

import logging
from typing import Any, Dict, List, Optional

from src.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ListWorkflowsTool(BaseTool):
    """List all n8n workflows with optional filtering."""

    name = "list_workflows"
    description = (
        "List all n8n workflows. You can filter by active status to see "
        "only active or inactive workflows, or view all workflows."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["active", "inactive", "all"],
                "description": "Filter workflows by activation status",
                "default": "all"
            }
        }
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to list workflows."""
        status_filter = arguments.get("status", "all")

        # Determine active filter
        active: Optional[bool] = None
        if status_filter == "active":
            active = True
        elif status_filter == "inactive":
            active = False

        # Get workflows from n8n
        workflows = await self.n8n_client.list_workflows(active=active)

        # Format response with summary
        return {
            "total_count": len(workflows),
            "filter": status_filter,
            "workflows": [
                {
                    "id": w.get("id"),
                    "name": w.get("name"),
                    "active": w.get("active", False),
                    "tags": w.get("tags", []),
                    "created_at": w.get("createdAt"),
                    "updated_at": w.get("updatedAt")
                }
                for w in workflows
            ]
        }


class GetWorkflowDetailsTool(BaseTool):
    """Get detailed information about a specific workflow."""

    name = "get_workflow_details"
    description = (
        "Get detailed information about a specific n8n workflow including "
        "its nodes, connections, settings, and metadata."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "The ID of the workflow to retrieve"
            }
        },
        "required": ["workflow_id"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to get workflow details."""
        self._validate_required_args(arguments, ["workflow_id"])

        workflow_id = arguments["workflow_id"]
        workflow = await self.n8n_client.get_workflow(workflow_id)

        # Format comprehensive workflow information
        return {
            "id": workflow.get("id"),
            "name": workflow.get("name"),
            "active": workflow.get("active", False),
            "tags": workflow.get("tags", []),
            "nodes": workflow.get("nodes", []),
            "connections": workflow.get("connections", {}),
            "settings": workflow.get("settings", {}),
            "static_data": workflow.get("staticData"),
            "created_at": workflow.get("createdAt"),
            "updated_at": workflow.get("updatedAt"),
            "node_count": len(workflow.get("nodes", [])),
            "version_id": workflow.get("versionId")
        }


class CreateWorkflowTool(BaseTool):
    """Create a new n8n workflow."""

    name = "create_workflow"
    description = (
        "Create a new n8n workflow. You need to provide at minimum a workflow name. "
        "Optionally include nodes, connections, and other workflow configuration."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the workflow"
            },
            "nodes": {
                "type": "array",
                "description": "Array of node definitions",
                "default": []
            },
            "connections": {
                "type": "object",
                "description": "Node connections definition",
                "default": {}
            },
            "settings": {
                "type": "object",
                "description": "Workflow settings",
                "default": {}
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags for organizing workflows",
                "default": []
            },
            "active": {
                "type": "boolean",
                "description": "Whether to activate the workflow immediately",
                "default": False
            }
        },
        "required": ["name"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to create a workflow."""
        self._validate_required_args(arguments, ["name"])

        # Build workflow data
        workflow_data = {
            "name": arguments["name"],
            "nodes": arguments.get("nodes", []),
            "connections": arguments.get("connections", {}),
            "settings": arguments.get("settings", {}),
            "tags": arguments.get("tags", []),
            "active": arguments.get("active", False)
        }

        # Create workflow
        workflow = await self.n8n_client.create_workflow(workflow_data)

        return {
            "id": workflow.get("id"),
            "name": workflow.get("name"),
            "active": workflow.get("active"),
            "created_at": workflow.get("createdAt"),
            "message": f"Successfully created workflow '{workflow.get('name')}'"
        }


class UpdateWorkflowTool(BaseTool):
    """Update an existing n8n workflow."""

    name = "update_workflow"
    description = (
        "Update an existing n8n workflow. You can update the name, nodes, "
        "connections, settings, tags, and activation status."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "ID of the workflow to update"
            },
            "name": {
                "type": "string",
                "description": "New name for the workflow"
            },
            "nodes": {
                "type": "array",
                "description": "Updated array of node definitions"
            },
            "connections": {
                "type": "object",
                "description": "Updated node connections"
            },
            "settings": {
                "type": "object",
                "description": "Updated workflow settings"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Updated tags"
            },
            "active": {
                "type": "boolean",
                "description": "Updated activation status"
            }
        },
        "required": ["workflow_id"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to update a workflow."""
        self._validate_required_args(arguments, ["workflow_id"])

        workflow_id = arguments["workflow_id"]

        # Get current workflow
        current_workflow = await self.n8n_client.get_workflow(workflow_id)

        # Build update data (merge with current)
        workflow_data = {
            "name": arguments.get("name", current_workflow.get("name")),
            "nodes": arguments.get("nodes", current_workflow.get("nodes", [])),
            "connections": arguments.get("connections", current_workflow.get("connections", {})),
            "settings": arguments.get("settings", current_workflow.get("settings", {})),
            "tags": arguments.get("tags", current_workflow.get("tags", [])),
            "active": arguments.get("active", current_workflow.get("active", False))
        }

        # Update workflow
        workflow = await self.n8n_client.update_workflow(workflow_id, workflow_data)

        return {
            "id": workflow.get("id"),
            "name": workflow.get("name"),
            "active": workflow.get("active"),
            "updated_at": workflow.get("updatedAt"),
            "message": f"Successfully updated workflow '{workflow.get('name')}'"
        }


class ActivateWorkflowTool(BaseTool):
    """Activate a workflow."""

    name = "activate_workflow"
    description = (
        "Activate an n8n workflow to start processing triggers and webhooks. "
        "The workflow must be properly configured before activation."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "ID of the workflow to activate"
            }
        },
        "required": ["workflow_id"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to activate a workflow."""
        self._validate_required_args(arguments, ["workflow_id"])

        workflow_id = arguments["workflow_id"]
        workflow = await self.n8n_client.activate_workflow(workflow_id)

        return {
            "id": workflow.get("id"),
            "name": workflow.get("name"),
            "active": workflow.get("active"),
            "message": f"Successfully activated workflow '{workflow.get('name')}'"
        }


class DeactivateWorkflowTool(BaseTool):
    """Deactivate a workflow."""

    name = "deactivate_workflow"
    description = (
        "Deactivate an n8n workflow to stop processing triggers and webhooks. "
        "The workflow will no longer execute automatically."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "ID of the workflow to deactivate"
            }
        },
        "required": ["workflow_id"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to deactivate a workflow."""
        self._validate_required_args(arguments, ["workflow_id"])

        workflow_id = arguments["workflow_id"]
        workflow = await self.n8n_client.deactivate_workflow(workflow_id)

        return {
            "id": workflow.get("id"),
            "name": workflow.get("name"),
            "active": workflow.get("active"),
            "message": f"Successfully deactivated workflow '{workflow.get('name')}'"
        }


class DeleteWorkflowTool(BaseTool):
    """Delete a workflow."""

    name = "delete_workflow"
    description = (
        "Permanently delete an n8n workflow. This action cannot be undone. "
        "Make sure to deactivate the workflow first if it's active."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "workflow_id": {
                "type": "string",
                "description": "ID of the workflow to delete"
            },
            "confirm": {
                "type": "boolean",
                "description": "Confirmation flag to prevent accidental deletion",
                "default": False
            }
        },
        "required": ["workflow_id", "confirm"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to delete a workflow."""
        self._validate_required_args(arguments, ["workflow_id", "confirm"])

        if not arguments.get("confirm", False):
            raise ValueError(
                "Deletion requires explicit confirmation. Set 'confirm' to true."
            )

        workflow_id = arguments["workflow_id"]

        # Get workflow name before deletion
        workflow = await self.n8n_client.get_workflow(workflow_id)
        workflow_name = workflow.get("name", "Unknown")

        # Delete workflow
        await self.n8n_client.delete_workflow(workflow_id)

        return {
            "id": workflow_id,
            "name": workflow_name,
            "deleted": True,
            "message": f"Successfully deleted workflow '{workflow_name}'"
        }


class SearchWorkflowsTool(BaseTool):
    """Search workflows by name or tags."""

    name = "search_workflows"
    description = (
        "Search for n8n workflows by name or tags. Returns workflows that "
        "match the search query in their name or tag list."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query to match against workflow names and tags"
            },
            "active_only": {
                "type": "boolean",
                "description": "Only return active workflows",
                "default": False
            }
        },
        "required": ["query"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool to search workflows."""
        self._validate_required_args(arguments, ["query"])

        query = arguments["query"]
        active_only = arguments.get("active_only", False)

        # Search workflows
        active_filter = True if active_only else None
        workflows = await self.n8n_client.search_workflows(query, active=active_filter)

        return {
            "query": query,
            "total_matches": len(workflows),
            "active_filter": active_only,
            "workflows": [
                {
                    "id": w.get("id"),
                    "name": w.get("name"),
                    "active": w.get("active", False),
                    "tags": w.get("tags", []),
                    "created_at": w.get("createdAt"),
                    "updated_at": w.get("updatedAt")
                }
                for w in workflows
            ]
        }
