"""Base class for MCP tools."""

import logging
from typing import Any, Dict
from abc import ABC, abstractmethod

from src.n8n_client import N8NClient, N8NError

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all MCP tools.

    Provides common functionality for error handling, logging,
    and response formatting.

    Attributes:
        name: Tool name used in MCP protocol
        description: Tool description for LLM
        input_schema: JSON schema for tool parameters
        n8n_client: n8n API client instance
    """

    name: str = "base_tool"
    description: str = "Base tool class"
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def __init__(self, n8n_client: N8NClient) -> None:
        """Initialize the tool.

        Args:
            n8n_client: n8n API client instance
        """
        self.n8n_client = n8n_client
        logger.debug(f"Initialized tool: {self.name}")

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool logic.

        This method must be implemented by all tool subclasses.

        Args:
            arguments: Tool arguments from MCP request

        Returns:
            Tool execution result

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Tool must implement execute() method")

    async def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Run the tool with error handling and logging.

        This is the main entry point that wraps execute() with
        common error handling and response formatting.

        Args:
            arguments: Tool arguments from MCP request

        Returns:
            Formatted tool response with success/error information
        """
        try:
            logger.info(
                f"Executing tool: {self.name}",
                extra={"tool": self.name, "arguments": arguments}
            )

            result = await self.execute(arguments)

            logger.info(
                f"Tool execution successful: {self.name}",
                extra={"tool": self.name}
            )

            return self._format_success(result)

        except N8NError as e:
            logger.error(
                f"n8n error in tool {self.name}: {e}",
                extra={"tool": self.name, "error": str(e)}
            )
            return self._format_error(str(e), error_type="n8n_error")

        except ValueError as e:
            logger.warning(
                f"Validation error in tool {self.name}: {e}",
                extra={"tool": self.name, "error": str(e)}
            )
            return self._format_error(str(e), error_type="validation_error")

        except Exception as e:
            logger.exception(
                f"Unexpected error in tool {self.name}: {e}",
                extra={"tool": self.name, "error": str(e)}
            )
            return self._format_error(
                f"Unexpected error: {str(e)}",
                error_type="internal_error"
            )

    def _format_success(self, data: Any) -> Dict[str, Any]:
        """Format successful response.

        Args:
            data: Tool execution result

        Returns:
            Formatted success response
        """
        return {
            "success": True,
            "data": data,
            "error": None
        }

    def _format_error(
        self,
        message: str,
        error_type: str = "error"
    ) -> Dict[str, Any]:
        """Format error response.

        Args:
            message: Error message
            error_type: Type of error (for categorization)

        Returns:
            Formatted error response
        """
        return {
            "success": False,
            "data": None,
            "error": {
                "type": error_type,
                "message": message
            }
        }

    def _validate_required_args(
        self,
        arguments: Dict[str, Any],
        required: list[str]
    ) -> None:
        """Validate that required arguments are present.

        Args:
            arguments: Tool arguments
            required: List of required argument names

        Raises:
            ValueError: If required arguments are missing
        """
        missing = [arg for arg in required if arg not in arguments]
        if missing:
            raise ValueError(f"Missing required arguments: {', '.join(missing)}")

    def get_tool_metadata(self) -> Dict[str, Any]:
        """Get tool metadata for MCP registration.

        Returns:
            Tool metadata including name, description, and schema
        """
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }
