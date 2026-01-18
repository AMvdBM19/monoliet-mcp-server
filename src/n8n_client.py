"""Async client for n8n API interactions."""

import logging
from typing import Any, Dict, List, Optional
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from src.config import Config

logger = logging.getLogger(__name__)


class N8NError(Exception):
    """Base exception for n8n client errors."""
    pass


class N8NConnectionError(N8NError):
    """Raised when connection to n8n fails."""
    pass


class N8NAuthError(N8NError):
    """Raised when authentication fails."""
    pass


class N8NNotFoundError(N8NError):
    """Raised when a resource is not found."""
    pass


class N8NValidationError(N8NError):
    """Raised when request validation fails."""
    pass


class N8NClient:
    """Async client for interacting with n8n API.

    This client provides methods for managing workflows and executions
    in n8n with proper error handling, retries, and logging.

    Attributes:
        config: Configuration instance
        client: Async HTTP client
    """

    def __init__(self, config: Config) -> None:
        """Initialize n8n client.

        Args:
            config: Application configuration
        """
        self.config = config
        self.base_url = config.get_n8n_api_base_url()
        self.headers = config.get_n8n_headers()
        self.timeout = config.n8n_timeout

        # Create async HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=True
        )

        logger.info(
            "N8N client initialized",
            extra={"base_url": self.base_url}
        )

    async def __aenter__(self) -> "N8NClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.debug("N8N client closed")

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response

        Raises:
            N8NAuthError: On 401/403 errors
            N8NNotFoundError: On 404 errors
            N8NValidationError: On 400 errors
            N8NError: On other errors
        """
        try:
            response.raise_for_status()

            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {}

            return response.json()

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code

            # Try to get error message from response
            try:
                error_data = e.response.json()
                error_msg = error_data.get("message", str(e))
            except Exception:
                error_msg = str(e)

            # Raise specific exceptions based on status code
            if status_code in (401, 403):
                logger.error(f"Authentication error: {error_msg}")
                raise N8NAuthError(f"Authentication failed: {error_msg}")
            elif status_code == 404:
                logger.warning(f"Resource not found: {error_msg}")
                raise N8NNotFoundError(f"Resource not found: {error_msg}")
            elif status_code == 400:
                logger.warning(f"Validation error: {error_msg}")
                raise N8NValidationError(f"Validation error: {error_msg}")
            else:
                logger.error(f"n8n API error: {error_msg}")
                raise N8NError(f"n8n API error: {error_msg}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> Any:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for httpx request

        Returns:
            Parsed JSON response

        Raises:
            N8NConnectionError: On connection errors
            Various N8NError subclasses: On API errors
        """
        try:
            logger.debug(
                f"n8n API request: {method} {endpoint}",
                extra={"method": method, "endpoint": endpoint}
            )

            response = await self.client.request(method, endpoint, **kwargs)
            return self._handle_response(response)

        except (httpx.NetworkError, httpx.TimeoutException) as e:
            logger.error(f"Connection error to n8n: {e}")
            raise N8NConnectionError(f"Failed to connect to n8n: {e}")

    # ==================== Health & Status ====================

    async def health_check(self) -> Dict[str, Any]:
        """Check if n8n instance is healthy and accessible.

        Returns:
            Health status information

        Raises:
            N8NConnectionError: If health check fails
        """
        try:
            # Try to list workflows as health check
            await self._request("GET", "/workflows", params={"limit": 1})
            return {
                "status": "healthy",
                "url": self.base_url,
                "message": "Successfully connected to n8n"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise N8NConnectionError(f"Health check failed: {e}")

    # ==================== Workflow Management ====================

    async def list_workflows(
        self,
        active: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List all workflows.

        Args:
            active: Filter by active status (True/False/None for all)
            tags: Filter by tags

        Returns:
            List of workflow objects

        Raises:
            N8NError: On API errors
        """
        params: Dict[str, Any] = {}

        if active is not None:
            params["active"] = str(active).lower()

        if tags:
            params["tags"] = ",".join(tags)

        response = await self._request("GET", "/workflows", params=params)

        # n8n returns data in different formats, handle both
        if isinstance(response, dict) and "data" in response:
            workflows = response["data"]
        elif isinstance(response, list):
            workflows = response
        else:
            workflows = []

        logger.info(f"Listed {len(workflows)} workflows")
        return workflows

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific workflow.

        Args:
            workflow_id: Workflow ID or name

        Returns:
            Workflow object with full details

        Raises:
            N8NNotFoundError: If workflow doesn't exist
            N8NError: On other API errors
        """
        workflow = await self._request("GET", f"/workflows/{workflow_id}")
        logger.info(f"Retrieved workflow: {workflow_id}")
        return workflow

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow.

        Args:
            workflow_data: Workflow definition including name, nodes, connections

        Returns:
            Created workflow object

        Raises:
            N8NValidationError: If workflow data is invalid
            N8NError: On other API errors
        """
        workflow = await self._request("POST", "/workflows", json=workflow_data)
        logger.info(f"Created workflow: {workflow.get('id')}")
        return workflow

    async def update_workflow(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing workflow.

        Args:
            workflow_id: Workflow ID to update
            workflow_data: Updated workflow definition

        Returns:
            Updated workflow object

        Raises:
            N8NNotFoundError: If workflow doesn't exist
            N8NValidationError: If workflow data is invalid
            N8NError: On other API errors
        """
        workflow = await self._request(
            "PUT",
            f"/workflows/{workflow_id}",
            json=workflow_data
        )
        logger.info(f"Updated workflow: {workflow_id}")
        return workflow

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow.

        Args:
            workflow_id: Workflow ID to delete

        Returns:
            True if deletion was successful

        Raises:
            N8NNotFoundError: If workflow doesn't exist
            N8NError: On other API errors
        """
        await self._request("DELETE", f"/workflows/{workflow_id}")
        logger.info(f"Deleted workflow: {workflow_id}")
        return True

    async def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Activate a workflow.

        Args:
            workflow_id: Workflow ID to activate

        Returns:
            Updated workflow object

        Raises:
            N8NNotFoundError: If workflow doesn't exist
            N8NError: On other API errors
        """
        # Get current workflow
        workflow = await self.get_workflow(workflow_id)

        # Update active status
        workflow["active"] = True
        updated = await self.update_workflow(workflow_id, workflow)

        logger.info(f"Activated workflow: {workflow_id}")
        return updated

    async def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Deactivate a workflow.

        Args:
            workflow_id: Workflow ID to deactivate

        Returns:
            Updated workflow object

        Raises:
            N8NNotFoundError: If workflow doesn't exist
            N8NError: On other API errors
        """
        # Get current workflow
        workflow = await self.get_workflow(workflow_id)

        # Update active status
        workflow["active"] = False
        updated = await self.update_workflow(workflow_id, workflow)

        logger.info(f"Deactivated workflow: {workflow_id}")
        return updated

    # ==================== Execution Management ====================

    async def execute_workflow(
        self,
        workflow_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Manually execute a workflow.

        Args:
            workflow_id: Workflow ID to execute
            data: Optional input data for the workflow

        Returns:
            Execution result

        Raises:
            N8NNotFoundError: If workflow doesn't exist
            N8NError: On execution errors
        """
        payload: Dict[str, Any] = {}
        if data:
            payload["data"] = data

        execution = await self._request(
            "POST",
            f"/workflows/{workflow_id}/execute",
            json=payload
        )

        logger.info(
            f"Executed workflow: {workflow_id}",
            extra={"execution_id": execution.get("id")}
        )
        return execution

    async def get_executions(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get execution history.

        Args:
            workflow_id: Optional workflow ID to filter by
            limit: Maximum number of executions to return
            status: Filter by status (success, error, waiting)

        Returns:
            List of execution objects

        Raises:
            N8NError: On API errors
        """
        params: Dict[str, Any] = {"limit": limit}

        if workflow_id:
            params["workflowId"] = workflow_id

        if status:
            params["status"] = status

        response = await self._request("GET", "/executions", params=params)

        # Handle different response formats
        if isinstance(response, dict) and "data" in response:
            executions = response["data"]
        elif isinstance(response, list):
            executions = response
        else:
            executions = []

        logger.info(f"Retrieved {len(executions)} executions")
        return executions

    async def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution object with full details

        Raises:
            N8NNotFoundError: If execution doesn't exist
            N8NError: On other API errors
        """
        execution = await self._request("GET", f"/executions/{execution_id}")
        logger.info(f"Retrieved execution: {execution_id}")
        return execution

    async def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution.

        Args:
            execution_id: Execution ID to delete

        Returns:
            True if deletion was successful

        Raises:
            N8NNotFoundError: If execution doesn't exist
            N8NError: On other API errors
        """
        await self._request("DELETE", f"/executions/{execution_id}")
        logger.info(f"Deleted execution: {execution_id}")
        return True

    # ==================== Search & Analytics ====================

    async def search_workflows(
        self,
        query: str,
        active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Search workflows by name or tags.

        Args:
            query: Search query string
            active: Filter by active status

        Returns:
            List of matching workflows

        Raises:
            N8NError: On API errors
        """
        # Get all workflows (n8n API doesn't have built-in search)
        all_workflows = await self.list_workflows(active=active)

        # Filter by query
        query_lower = query.lower()
        matching_workflows = [
            w for w in all_workflows
            if query_lower in w.get("name", "").lower()
            or any(query_lower in tag.lower() for tag in w.get("tags", []))
        ]

        logger.info(
            f"Search found {len(matching_workflows)} workflows",
            extra={"query": query}
        )
        return matching_workflows

    async def get_workflow_statistics(
        self,
        workflow_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get execution statistics for a workflow.

        Args:
            workflow_id: Workflow ID
            limit: Number of recent executions to analyze

        Returns:
            Statistics including success rate, error count, etc.

        Raises:
            N8NError: On API errors
        """
        executions = await self.get_executions(workflow_id=workflow_id, limit=limit)

        total = len(executions)
        if total == 0:
            return {
                "workflow_id": workflow_id,
                "total_executions": 0,
                "success_count": 0,
                "error_count": 0,
                "waiting_count": 0,
                "success_rate": 0.0,
                "error_rate": 0.0
            }

        success_count = sum(1 for e in executions if e.get("finished") and not e.get("stoppedAt"))
        error_count = sum(1 for e in executions if e.get("stoppedAt"))
        waiting_count = sum(1 for e in executions if not e.get("finished"))

        return {
            "workflow_id": workflow_id,
            "total_executions": total,
            "success_count": success_count,
            "error_count": error_count,
            "waiting_count": waiting_count,
            "success_rate": round((success_count / total) * 100, 2) if total > 0 else 0.0,
            "error_rate": round((error_count / total) * 100, 2) if total > 0 else 0.0,
            "analyzed_executions": limit
        }
