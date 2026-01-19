"""
Main MCP server for n8n workflow management.

Runs two servers concurrently:
1. MCP server (stdio/HTTP) for Claude integration
2. Management REST API for Django portal integration
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
import uvicorn

from src.config import get_config
from src.n8n_client import N8NClient
from src.management_api import management_app
from src.tools import (
    ListWorkflowsTool,
    GetWorkflowDetailsTool,
    CreateWorkflowTool,
    UpdateWorkflowTool,
    ActivateWorkflowTool,
    DeactivateWorkflowTool,
    DeleteWorkflowTool,
    SearchWorkflowsTool,
    ExecuteWorkflowTool,
    GetExecutionsTool,
    GetWorkflowHealthTool,
)

logger = logging.getLogger(__name__)


def setup_logging(log_level: str, log_format: str) -> None:
    """Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ('json' or 'console')
    """
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # Set log level for httpx to WARNING to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.info(f"Logging configured: level={log_level}, format={log_format}")


class MonolietMCPServer:
    """MCP server for n8n workflow management.

    This server provides natural language tools for managing n8n workflows,
    executions, and monitoring through the Model Context Protocol.
    """

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.config = get_config()
        self.n8n_client: Optional[N8NClient] = None
        self.mcp_server = Server("monoliet-n8n-mcp")
        self.tools: List[Any] = []
        self._shutdown_event = asyncio.Event()

        logger.info("Monoliet MCP Server initialized")

    async def initialize(self) -> None:
        """Initialize server components."""
        logger.info("Initializing server components...")

        # Setup logging
        setup_logging(self.config.log_level, self.config.log_format)

        # Initialize n8n client
        self.n8n_client = N8NClient(self.config)

        # Validate n8n connection
        try:
            health = await self.n8n_client.health_check()
            logger.info(f"n8n connection validated: {health['message']}")
        except Exception as e:
            logger.error(f"Failed to connect to n8n: {e}")
            raise

        # Initialize and register tools
        await self._register_tools()

        logger.info("Server initialization complete")

    async def _register_tools(self) -> None:
        """Register all MCP tools."""
        if not self.n8n_client:
            raise RuntimeError("n8n client not initialized")

        # Instantiate all tools
        tool_classes = [
            ListWorkflowsTool,
            GetWorkflowDetailsTool,
            CreateWorkflowTool,
            UpdateWorkflowTool,
            ActivateWorkflowTool,
            DeactivateWorkflowTool,
            DeleteWorkflowTool,
            SearchWorkflowsTool,
            ExecuteWorkflowTool,
            GetExecutionsTool,
            GetWorkflowHealthTool,
        ]

        self.tools = [tool_class(self.n8n_client) for tool_class in tool_classes]

        # Register tools with MCP server
        @self.mcp_server.list_tools()
        async def list_tools() -> List[Dict[str, Any]]:
            """List all available tools."""
            return [tool.get_tool_metadata() for tool in self.tools]

        @self.mcp_server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
            """Call a tool by name with arguments."""
            # Find the tool
            tool = next((t for t in self.tools if t.name == name), None)

            if not tool:
                error_msg = f"Unknown tool: {name}"
                logger.error(error_msg)
                return [{
                    "type": "text",
                    "text": f"Error: {error_msg}"
                }]

            # Execute the tool
            try:
                result = await tool.run(arguments)

                # Format response for MCP
                if result.get("success"):
                    # Success response
                    return [{
                        "type": "text",
                        "text": self._format_success_response(result)
                    }]
                else:
                    # Error response
                    return [{
                        "type": "text",
                        "text": self._format_error_response(result)
                    }]

            except Exception as e:
                logger.exception(f"Error executing tool {name}: {e}")
                return [{
                    "type": "text",
                    "text": f"Error executing tool: {str(e)}"
                }]

        logger.info(f"Registered {len(self.tools)} tools")

    def _format_success_response(self, result: Dict[str, Any]) -> str:
        """Format successful tool response as text.

        Args:
            result: Tool execution result

        Returns:
            Formatted text response
        """
        import json
        data = result.get("data", {})
        return json.dumps(data, indent=2)

    def _format_error_response(self, result: Dict[str, Any]) -> str:
        """Format error tool response as text.

        Args:
            result: Tool execution result with error

        Returns:
            Formatted error message
        """
        error = result.get("error", {})
        error_type = error.get("type", "error")
        error_message = error.get("message", "Unknown error")
        return f"Error ({error_type}): {error_message}"

    async def run_stdio(self) -> None:
        """Run the MCP server in stdio mode (for Claude Desktop)."""
        logger.info("Running MCP server in STDIO mode...")

        async with stdio_server() as (read_stream, write_stream):
            await self.mcp_server.run(
                read_stream,
                write_stream,
                self.mcp_server.create_initialization_options()
            )

    async def run_http(self) -> None:
        """Run the MCP server in HTTP mode (for remote access)."""
        from aiohttp import web

        logger.info(f"Running MCP server in HTTP mode on {self.config.mcp_server_host}:{self.config.mcp_server_port}...")

        async def handle_sse(request: web.Request) -> web.StreamResponse:
            """Handle Server-Sent Events connection."""
            response = web.StreamResponse()
            response.headers['Content-Type'] = 'text/event-stream'
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Connection'] = 'keep-alive'
            response.headers['Access-Control-Allow-Origin'] = '*'
            await response.prepare(request)

            try:
                # Keep connection alive and handle MCP protocol
                while True:
                    await asyncio.sleep(1)
                    await response.write(b': keepalive\n\n')
            except Exception as e:
                logger.error(f"SSE error: {e}")
            finally:
                await response.write_eof()

            return response

        async def handle_post(request: web.Request) -> web.Response:
            """Handle MCP tool calls via POST."""
            try:
                data = await request.json()

                tool_name = data.get('tool')
                arguments = data.get('arguments', {})

                if not tool_name:
                    return web.json_response(
                        {'error': 'Missing tool name'},
                        status=400
                    )

                # Find and execute tool
                tool = next((t for t in self.tools if t.name == tool_name), None)

                if not tool:
                    return web.json_response(
                        {'error': f'Unknown tool: {tool_name}'},
                        status=404
                    )

                result = await tool.run(arguments)
                return web.json_response(result)

            except Exception as e:
                logger.exception(f"Error handling POST request: {e}")
                return web.json_response(
                    {'error': str(e)},
                    status=500
                )

        async def handle_list_tools(request: web.Request) -> web.Response:
            """Handle listing available tools."""
            try:
                tools_metadata = [tool.get_tool_metadata() for tool in self.tools]
                return web.json_response({
                    'tools': tools_metadata,
                    'count': len(tools_metadata)
                })
            except Exception as e:
                logger.exception(f"Error listing tools: {e}")
                return web.json_response(
                    {'error': str(e)},
                    status=500
                )

        async def handle_health(request: web.Request) -> web.Response:
            """Health check endpoint."""
            try:
                # Check n8n connection
                health = await self.n8n_client.health_check()
                return web.json_response({
                    'status': 'healthy',
                    'n8n': health,
                    'tools_count': len(self.tools)
                })
            except Exception as e:
                return web.json_response({
                    'status': 'unhealthy',
                    'error': str(e)
                }, status=503)

        # Create aiohttp application
        app = web.Application()
        app.router.add_get('/sse', handle_sse)
        app.router.add_post('/call', handle_post)
        app.router.add_get('/tools', handle_list_tools)
        app.router.add_get('/health', handle_health)

        # Run HTTP server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner,
            self.config.mcp_server_host,
            self.config.mcp_server_port
        )

        await site.start()
        logger.info(f"HTTP server started on http://{self.config.mcp_server_host}:{self.config.mcp_server_port}")
        logger.info("Endpoints:")
        logger.info(f"  - POST http://{self.config.mcp_server_host}:{self.config.mcp_server_port}/call - Execute tools")
        logger.info(f"  - GET  http://{self.config.mcp_server_host}:{self.config.mcp_server_port}/tools - List tools")
        logger.info(f"  - GET  http://{self.config.mcp_server_host}:{self.config.mcp_server_port}/health - Health check")
        logger.info(f"  - GET  http://{self.config.mcp_server_host}:{self.config.mcp_server_port}/sse - SSE connection")

        # Wait for shutdown signal
        await self._shutdown_event.wait()
        await runner.cleanup()

    async def run_management_api(self) -> None:
        """Run the management REST API server."""
        config = self.config
        logger.info(f"Starting Management API on port {config.management_api_port}...")

        uvicorn_config = uvicorn.Config(
            management_app,
            host="0.0.0.0",
            port=config.management_api_port,
            log_level=config.log_level.lower()
        )

        server = uvicorn.Server(uvicorn_config)
        await server.serve()

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting Monoliet MCP Server with Management API...")

        try:
            # Initialize server
            await self.initialize()

            # Setup signal handlers for graceful shutdown
            loop = asyncio.get_event_loop()

            def signal_handler(signum: int) -> None:
                logger.info(f"Received signal {signum}, initiating shutdown...")
                self._shutdown_event.set()

            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))

            # Determine server mode from environment or config
            server_mode = os.environ.get('MCP_SERVER_MODE', 'stdio').lower()

            logger.info(f"MCP server mode: {server_mode}")
            logger.info(f"Management API port: {self.config.management_api_port}")

            if server_mode == 'http':
                # Run both MCP HTTP server and Management API concurrently
                logger.info("Running in HTTP mode - both MCP and Management API servers")
                await asyncio.gather(
                    self.run_http(),
                    self.run_management_api()
                )
            else:
                # Run stdio mode for MCP, but still run Management API for Django portal
                logger.info("Running in STDIO mode for MCP, HTTP mode for Management API")
                logger.info("MCP server ready, waiting for stdio connections...")

                # Run Management API in background
                management_task = asyncio.create_task(self.run_management_api())

                # Run stdio in foreground
                try:
                    await self.run_stdio()
                except Exception as e:
                    logger.error(f"STDIO server error: {e}")
                    raise
                finally:
                    # Cancel management API when stdio exits
                    management_task.cancel()
                    try:
                        await management_task
                    except asyncio.CancelledError:
                        pass

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.exception(f"Server error: {e}")
            raise
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Gracefully shutdown the server."""
        logger.info("Shutting down server...")

        # Close n8n client
        if self.n8n_client:
            await self.n8n_client.close()

        logger.info("Server shutdown complete")


def main() -> None:
    """Main entry point for the MCP server."""
    # Create and run server
    server = MonolietMCPServer()

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
