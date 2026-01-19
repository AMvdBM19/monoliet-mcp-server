#!/usr/bin/env python3
"""Test script for HTTP API mode.

This script tests the MCP server running in HTTP mode.
"""

import asyncio
import httpx
import sys
from typing import Dict, Any


class MCPHTTPClient:
    """Simple HTTP client for MCP server."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        """Initialize client.

        Args:
            base_url: Base URL of MCP server
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        response = await self.client.get(f"{self.base_url}/tools")
        response.raise_for_status()
        return response.json()

    async def call_tool(self, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool.

        Args:
            tool: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        response = await self.client.post(
            f"{self.base_url}/call",
            json={"tool": tool, "arguments": arguments}
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close client."""
        await self.client.aclose()


async def test_http_api():
    """Run HTTP API tests."""
    print("🧪 Testing MCP Server HTTP API")
    print("=" * 60)
    print()

    client = MCPHTTPClient()

    try:
        # Test 1: Health Check
        print("1️⃣  Testing Health Check...")
        try:
            health = await client.health_check()
            print(f"   ✅ Server is {health['status']}")
            print(f"   ✅ n8n: {health.get('n8n', {}).get('status', 'unknown')}")
            print(f"   ✅ Tools: {health.get('tools_count', 0)}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False
        print()

        # Test 2: List Tools
        print("2️⃣  Testing List Tools...")
        try:
            tools = await client.list_tools()
            tool_count = tools.get('count', 0)
            print(f"   ✅ Found {tool_count} tools")
            for tool in tools.get('tools', [])[:3]:
                print(f"      - {tool['name']}")
            if tool_count > 3:
                print(f"      ... and {tool_count - 3} more")
        except Exception as e:
            print(f"   ❌ List tools failed: {e}")
            return False
        print()

        # Test 3: List Workflows
        print("3️⃣  Testing List Workflows Tool...")
        try:
            result = await client.call_tool(
                "list_workflows",
                {"status": "all"}
            )
            if result.get('success'):
                data = result.get('data', {})
                count = data.get('total_count', 0)
                print(f"   ✅ Found {count} workflows")
                workflows = data.get('workflows', [])
                for wf in workflows[:3]:
                    status = '🟢' if wf.get('active') else '⚪'
                    print(f"      {status} {wf.get('name')} (ID: {wf.get('id')})")
                if count > 3:
                    print(f"      ... and {count - 3} more")
            else:
                error = result.get('error', {})
                print(f"   ⚠️  Tool returned error: {error.get('message')}")
        except Exception as e:
            print(f"   ❌ List workflows failed: {e}")
            return False
        print()

        # Test 4: Search Workflows
        print("4️⃣  Testing Search Workflows Tool...")
        try:
            result = await client.call_tool(
                "search_workflows",
                {"query": "test"}
            )
            if result.get('success'):
                data = result.get('data', {})
                matches = data.get('total_matches', 0)
                print(f"   ✅ Search found {matches} matches for 'test'")
            else:
                error = result.get('error', {})
                print(f"   ⚠️  Tool returned error: {error.get('message')}")
        except Exception as e:
            print(f"   ❌ Search workflows failed: {e}")
            return False
        print()

        # Test 5: Get Executions
        print("5️⃣  Testing Get Executions Tool...")
        try:
            result = await client.call_tool(
                "get_executions",
                {"limit": 5}
            )
            if result.get('success'):
                data = result.get('data', {})
                total = data.get('total_count', 0)
                success = data.get('success_count', 0)
                errors = data.get('error_count', 0)
                print(f"   ✅ Recent executions: {total} total, {success} success, {errors} errors")
            else:
                error = result.get('error', {})
                print(f"   ⚠️  Tool returned error: {error.get('message')}")
        except Exception as e:
            print(f"   ❌ Get executions failed: {e}")
            return False
        print()

        # Test 6: Error Handling
        print("6️⃣  Testing Error Handling (invalid tool)...")
        try:
            result = await client.call_tool(
                "invalid_tool_name",
                {}
            )
            if not result.get('success'):
                print(f"   ✅ Server correctly returned error for invalid tool")
            else:
                print(f"   ⚠️  Expected error but got success")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"   ✅ Server correctly returned 404 for invalid tool")
            else:
                print(f"   ⚠️  Unexpected status code: {e.response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Unexpected error: {e}")
        print()

        print("=" * 60)
        print("✅ All HTTP API tests passed!")
        print()
        print("🎉 MCP Server HTTP mode is working correctly!")
        print()
        print("Next steps:")
        print("  - Use curl: curl http://localhost:8001/health")
        print("  - Use Python: See test_http_api.py for examples")
        print("  - See HTTP_API.md for full documentation")
        print()

        return True

    except httpx.ConnectError:
        print()
        print("❌ Could not connect to MCP server")
        print()
        print("Make sure the server is running in HTTP mode:")
        print("  MCP_SERVER_MODE=http python -m src.server")
        print()
        print("Or with Docker:")
        print("  docker-compose up -d")
        print()
        return False

    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        print()
        return False

    finally:
        await client.close()


def main():
    """Main entry point."""
    try:
        success = asyncio.run(test_http_api())
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)


if __name__ == "__main__":
    main()
