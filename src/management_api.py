"""
Management REST API for MCP Server.

This module provides HTTP endpoints for the Django portal to manage
and monitor the MCP server without interfering with MCP protocol operations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import time

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import get_config
from src.n8n_client import N8NClient, N8NError

logger = logging.getLogger(__name__)

# Global startup time for uptime tracking
_startup_time = time.time()

# Initialize FastAPI app
management_app = FastAPI(
    title="Monoliet MCP Management API",
    description="REST API for managing the MCP server from Django portal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Pydantic Models
class ServerStatus(BaseModel):
    """MCP Server status information."""
    status: str = Field(..., description="Server operational status")
    uptime_seconds: float = Field(..., description="Server uptime in seconds")
    n8n_connected: bool = Field(..., description="n8n API connection status")
    n8n_url: str = Field(..., description="Configured n8n URL")
    mcp_port: int = Field(..., description="MCP server port")
    management_port: int = Field(..., description="Management API port")
    version: str = Field(..., description="MCP server version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WorkflowStats(BaseModel):
    """Aggregated workflow statistics."""
    total_workflows: int
    active_workflows: int
    paused_workflows: int
    error_workflows: int = 0
    total_executions_today: int = 0
    success_rate: float = 0.0


class ConfigUpdate(BaseModel):
    """Configuration update request."""
    n8n_url: Optional[str] = None
    log_level: Optional[str] = None


class HealthCheck(BaseModel):
    """Health check response."""
    healthy: bool
    n8n_reachable: bool
    database_connected: bool = True  # MCP server is stateless
    errors: List[str] = []


class WorkflowListResponse(BaseModel):
    """Response for workflow list endpoint."""
    workflows: List[Dict[str, Any]]
    count: int


class WorkflowActionResponse(BaseModel):
    """Response for workflow action endpoints."""
    success: bool
    workflow_id: str
    data: Optional[Dict[str, Any]] = None


class ExecutionResponse(BaseModel):
    """Response for workflow execution endpoint."""
    success: bool
    workflow_id: str
    execution_id: Optional[str] = None


class ConfigResponse(BaseModel):
    """Configuration response (sensitive data redacted)."""
    n8n_url: str
    n8n_api_key_set: bool
    mcp_server_port: int
    management_api_port: int
    log_level: str


# Authentication
async def verify_portal_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify Django portal authentication token.

    Expected format: "Bearer <django-token>"
    Django portal will send its DRF token here.

    Args:
        authorization: Authorization header value

    Returns:
        The verified token

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    try:
        scheme, token = authorization.split(maxsplit=1)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer <token>'"
            )

        # In production, verify token against Django portal's API
        # For now, we accept any non-empty token (Django portal handles its own auth)
        if not token or len(token) < 10:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'"
        )


def get_n8n_client() -> N8NClient:
    """Get initialized n8n client."""
    config = get_config()
    return N8NClient(config)


# CORS Configuration
def setup_cors():
    """Configure CORS middleware for Django portal."""
    config = get_config()

    # Default allowed origins
    allowed_origins = [
        "http://localhost:8000",  # Django local development
        "http://127.0.0.1:8000",  # Django local development (alternative)
    ]

    # Add production portal URL if configured
    if config.django_portal_url:
        allowed_origins.append(config.django_portal_url)

    management_app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Call CORS setup
setup_cors()


# Endpoints
@management_app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "service": "Monoliet MCP Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "/status"
    }


@management_app.get("/health", response_model=HealthCheck, tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint (no auth required).
    Used by Docker healthcheck and monitoring systems.
    """
    config = get_config()
    errors = []
    n8n_reachable = False

    try:
        client = N8NClient(config)
        try:
            # Test n8n connection
            await client.health_check()
            n8n_reachable = True
        finally:
            await client.close()
    except Exception as e:
        errors.append(f"n8n unreachable: {str(e)}")
        logger.warning(f"Health check: n8n unreachable - {e}")

    healthy = n8n_reachable and len(errors) == 0

    return HealthCheck(
        healthy=healthy,
        n8n_reachable=n8n_reachable,
        errors=errors
    )


@management_app.get("/status", response_model=ServerStatus, tags=["Monitoring"])
async def get_status(token: str = Depends(verify_portal_token)):
    """
    Get comprehensive server status.
    Requires authentication.
    """
    config = get_config()
    n8n_connected = False

    try:
        client = N8NClient(config)
        try:
            await client.health_check()
            n8n_connected = True
        finally:
            await client.close()
    except Exception as e:
        logger.warning(f"Status check: n8n connection failed - {e}")

    # Calculate uptime
    uptime = time.time() - _startup_time

    return ServerStatus(
        status="operational" if n8n_connected else "degraded",
        uptime_seconds=uptime,
        n8n_connected=n8n_connected,
        n8n_url=config.n8n_url,
        mcp_port=config.mcp_server_port,
        management_port=config.management_api_port,
        version="0.1.0"
    )


@management_app.get("/workflows/stats", response_model=WorkflowStats, tags=["Workflows"])
async def get_workflow_stats(token: str = Depends(verify_portal_token)):
    """
    Get aggregated workflow statistics.
    Requires authentication.
    """
    config = get_config()
    client = N8NClient(config)

    try:
        workflows = await client.list_workflows()

        total = len(workflows)
        active = sum(1 for w in workflows if w.get("active", False))
        paused = total - active

        # TODO: Implement error detection based on recent execution failures
        error = 0

        # TODO: Get today's execution count (requires execution history API)
        executions_today = 0
        success_rate = 0.0

        return WorkflowStats(
            total_workflows=total,
            active_workflows=active,
            paused_workflows=paused,
            error_workflows=error,
            total_executions_today=executions_today,
            success_rate=success_rate
        )
    except N8NError as e:
        logger.error(f"Failed to fetch workflow stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workflow stats: {str(e)}"
        )
    finally:
        await client.close()


@management_app.get("/workflows", response_model=WorkflowListResponse, tags=["Workflows"])
async def list_workflows(
    token: str = Depends(verify_portal_token),
    active_only: bool = False,
    search: Optional[str] = None
):
    """
    List all workflows with optional filtering.
    Requires authentication.

    Args:
        token: Authentication token
        active_only: Only return active workflows
        search: Search by workflow name
    """
    config = get_config()
    client = N8NClient(config)

    try:
        workflows = await client.list_workflows()

        # Filter active only
        if active_only:
            workflows = [w for w in workflows if w.get("active", False)]

        # Search by name
        if search:
            search_lower = search.lower()
            workflows = [
                w for w in workflows
                if search_lower in w.get("name", "").lower()
            ]

        return WorkflowListResponse(workflows=workflows, count=len(workflows))
    except N8NError as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )
    finally:
        await client.close()


@management_app.get("/workflows/{workflow_id}", tags=["Workflows"])
async def get_workflow(
    workflow_id: str,
    token: str = Depends(verify_portal_token)
):
    """
    Get detailed information about a specific workflow.
    Requires authentication.
    """
    config = get_config()
    client = N8NClient(config)

    try:
        workflow = await client.get_workflow(workflow_id)
        return {"success": True, "workflow": workflow}
    except N8NError as e:
        logger.error(f"Failed to get workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        await client.close()


@management_app.post(
    "/workflows/{workflow_id}/activate",
    response_model=WorkflowActionResponse,
    tags=["Workflows"]
)
async def activate_workflow(
    workflow_id: str,
    token: str = Depends(verify_portal_token)
):
    """
    Activate a workflow.
    Requires authentication.
    """
    config = get_config()
    client = N8NClient(config)

    try:
        result = await client.activate_workflow(workflow_id)
        return WorkflowActionResponse(
            success=True,
            workflow_id=workflow_id,
            data=result
        )
    except N8NError as e:
        logger.error(f"Failed to activate workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate workflow: {str(e)}"
        )
    finally:
        await client.close()


@management_app.post(
    "/workflows/{workflow_id}/deactivate",
    response_model=WorkflowActionResponse,
    tags=["Workflows"]
)
async def deactivate_workflow(
    workflow_id: str,
    token: str = Depends(verify_portal_token)
):
    """
    Deactivate a workflow.
    Requires authentication.
    """
    config = get_config()
    client = N8NClient(config)

    try:
        result = await client.deactivate_workflow(workflow_id)
        return WorkflowActionResponse(
            success=True,
            workflow_id=workflow_id,
            data=result
        )
    except N8NError as e:
        logger.error(f"Failed to deactivate workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate workflow: {str(e)}"
        )
    finally:
        await client.close()


@management_app.post(
    "/workflows/{workflow_id}/execute",
    response_model=ExecutionResponse,
    tags=["Workflows"]
)
async def execute_workflow(
    workflow_id: str,
    token: str = Depends(verify_portal_token)
):
    """
    Manually trigger workflow execution.
    Requires authentication.
    """
    config = get_config()
    client = N8NClient(config)

    try:
        result = await client.execute_workflow(workflow_id)
        return ExecutionResponse(
            success=True,
            workflow_id=workflow_id,
            execution_id=result.get("id")
        )
    except N8NError as e:
        logger.error(f"Failed to execute workflow {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )
    finally:
        await client.close()


@management_app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_config_info(token: str = Depends(verify_portal_token)):
    """
    Get current configuration (sensitive data redacted).
    Requires authentication.
    """
    config = get_config()

    return ConfigResponse(
        n8n_url=config.n8n_url,
        n8n_api_key_set=bool(config.n8n_api_key),
        mcp_server_port=config.mcp_server_port,
        management_api_port=config.management_api_port,
        log_level=config.log_level,
    )


@management_app.put("/config", tags=["Configuration"])
async def update_config(
    updates: ConfigUpdate,
    token: str = Depends(verify_portal_token)
):
    """
    Update configuration (runtime only, not persistent).
    Requires authentication.

    Note: Changes are NOT persisted to .env file.
    Restart server to revert to .env configuration.
    """
    # This is a stub - actual implementation would need to update runtime config
    # For now, return error indicating this needs server restart
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Configuration updates require server restart. Update .env file and restart container."
    )
