#!/usr/bin/env python3
"""Health check script for Monoliet MCP Server.

This script validates that the MCP server can connect to n8n
and all tools are working correctly.
"""

import asyncio
import sys
from typing import Dict, List

from src.config import get_config, reset_config
from src.n8n_client import N8NClient, N8NError


class HealthChecker:
    """Health check utility for MCP server."""

    def __init__(self) -> None:
        """Initialize health checker."""
        self.config = get_config()
        self.checks_passed = 0
        self.checks_failed = 0
        self.results: List[Dict[str, str]] = []

    def print_header(self) -> None:
        """Print health check header."""
        print("=" * 60)
        print("🏥 Monoliet MCP Server - Health Check")
        print("=" * 60)
        print()

    def print_result(self, name: str, status: str, message: str) -> None:
        """Print individual check result.

        Args:
            name: Check name
            status: Status (PASS/FAIL)
            message: Result message
        """
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {name}: {status}")
        if message:
            print(f"   {message}")
        print()

        self.results.append({
            "name": name,
            "status": status,
            "message": message
        })

        if status == "PASS":
            self.checks_passed += 1
        else:
            self.checks_failed += 1

    async def check_configuration(self) -> None:
        """Check configuration is valid."""
        try:
            # Check required config
            assert self.config.n8n_url, "N8N_URL is not set"
            assert self.config.n8n_api_key, "N8N_API_KEY is not set"

            self.print_result(
                "Configuration",
                "PASS",
                f"n8n URL: {self.config.n8n_url}"
            )
        except Exception as e:
            self.print_result(
                "Configuration",
                "FAIL",
                str(e)
            )

    async def check_n8n_connection(self) -> None:
        """Check connection to n8n instance."""
        try:
            async with N8NClient(self.config) as client:
                health = await client.health_check()
                self.print_result(
                    "n8n Connection",
                    "PASS",
                    health.get("message", "Connected successfully")
                )
        except Exception as e:
            self.print_result(
                "n8n Connection",
                "FAIL",
                f"Cannot connect to n8n: {str(e)}"
            )

    async def check_workflow_list(self) -> None:
        """Check workflow listing works."""
        try:
            async with N8NClient(self.config) as client:
                workflows = await client.list_workflows()
                count = len(workflows)
                self.print_result(
                    "Workflow Listing",
                    "PASS",
                    f"Found {count} workflow(s)"
                )
        except Exception as e:
            self.print_result(
                "Workflow Listing",
                "FAIL",
                str(e)
            )

    async def check_api_permissions(self) -> None:
        """Check API key has correct permissions."""
        try:
            async with N8NClient(self.config) as client:
                # Try to list workflows (read permission)
                await client.list_workflows()

                # Check if we can get executions (read permission)
                await client.get_executions(limit=1)

                self.print_result(
                    "API Permissions",
                    "PASS",
                    "API key has read permissions"
                )
        except N8NError as e:
            if "401" in str(e) or "403" in str(e):
                self.print_result(
                    "API Permissions",
                    "FAIL",
                    "API key invalid or insufficient permissions"
                )
            else:
                self.print_result(
                    "API Permissions",
                    "FAIL",
                    str(e)
                )
        except Exception as e:
            self.print_result(
                "API Permissions",
                "FAIL",
                str(e)
            )

    async def check_tools_import(self) -> None:
        """Check all tools can be imported."""
        try:
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

            tool_count = 11
            self.print_result(
                "MCP Tools Import",
                "PASS",
                f"All {tool_count} tools imported successfully"
            )
        except Exception as e:
            self.print_result(
                "MCP Tools Import",
                "FAIL",
                f"Failed to import tools: {str(e)}"
            )

    def print_summary(self) -> None:
        """Print health check summary."""
        print("=" * 60)
        print("📊 Health Check Summary")
        print("=" * 60)
        print()
        print(f"Total Checks: {self.checks_passed + self.checks_failed}")
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        print()

        if self.checks_failed == 0:
            print("🎉 All health checks passed! Server is ready.")
            print()
            print("Next steps:")
            print("1. Start the server: python -m src.server")
            print("2. Configure Claude Desktop (see README.md)")
            print("3. Test with Claude: 'List all my workflows'")
        else:
            print("⚠️  Some health checks failed. Please fix the issues above.")
            print()
            print("Common fixes:")
            print("- Verify n8n is running")
            print("- Check N8N_URL in .env")
            print("- Verify N8N_API_KEY is correct")
            print("- Ensure n8n API is enabled")

        print()

    async def run_all_checks(self) -> bool:
        """Run all health checks.

        Returns:
            True if all checks passed, False otherwise
        """
        self.print_header()

        # Run checks
        await self.check_configuration()
        await self.check_n8n_connection()
        await self.check_workflow_list()
        await self.check_api_permissions()
        await self.check_tools_import()

        # Print summary
        self.print_summary()

        return self.checks_failed == 0


async def main() -> None:
    """Main entry point."""
    try:
        checker = HealthChecker()
        success = await checker.run_all_checks()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Health check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
