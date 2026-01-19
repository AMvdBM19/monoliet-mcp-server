# Monoliet MCP Server for n8n

> **Natural language workflow management for n8n through Claude**

A production-ready Model Context Protocol (MCP) server that enables Claude to manage n8n workflows through natural conversation. Create, manage, monitor, and debug your automation workflows using plain English.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **🗣️ Natural Language Interface**: Manage workflows using conversational commands
- **📊 Comprehensive Workflow Management**: Create, update, activate, deactivate, and delete workflows
- **🔍 Smart Search**: Find workflows by name or tags
- **⚡ Execution Control**: Trigger workflows manually and monitor their execution
- **📈 Health Monitoring**: Track workflow success rates and identify issues
- **🔒 Production-Ready**: Full error handling, logging, and type safety
- **🐳 Docker Support**: Easy deployment with Docker and docker-compose
- **✅ Well-Tested**: Comprehensive test suite with >80% coverage

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Integration with Claude Desktop](#integration-with-claude-desktop)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- n8n instance (running and accessible)
- n8n API key
- Docker (optional, for containerized deployment)

### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/monoliet/monoliet-mcp-server.git
cd monoliet-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Option 2: Docker Installation

```bash
# Clone the repository
git clone https://github.com/monoliet/monoliet-mcp-server.git
cd monoliet-mcp-server

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Build and run with docker-compose
docker-compose up -d
```

## ⚡ Quick Start

### 1. Configure Environment Variables

Edit your `.env` file:

```env
# n8n Configuration
N8N_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key-here

# MCP Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
LOG_LEVEL=INFO
```

### 2. Get Your n8n API Key

1. Open your n8n instance
2. Go to **Settings** → **API**
3. Click **Create API Key**
4. Copy the key to your `.env` file

### 3. Choose Server Mode

The server supports two modes:

**stdio mode** - For Claude Desktop integration (default)
**HTTP mode** - For remote access via HTTP API

```env
# For Claude Desktop (default)
MCP_SERVER_MODE=stdio

# For remote/HTTP access
MCP_SERVER_MODE=http
```

### 4. Run the Server

**stdio mode (Claude Desktop):**
```bash
python -m src.server
# or
./start.sh
```

**HTTP mode (Remote Access):**
```bash
MCP_SERVER_MODE=http python -m src.server
```

**Docker (HTTP mode by default):**
```bash
docker-compose up -d
```

### 5. Verify It's Working

**For HTTP mode:**
```bash
# Check health
curl http://localhost:8001/health

# List tools
curl http://localhost:8001/tools

# View logs (Docker)
docker-compose logs -f monoliet-mcp
```

**For stdio mode:**
```bash
# Check process is running
ps aux | grep "src.server"
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `N8N_URL` | n8n instance URL | - | ✅ Yes |
| `N8N_API_KEY` | n8n API key | - | ✅ Yes |
| `N8N_TIMEOUT` | API request timeout (seconds) | `30` | No |
| `N8N_MAX_RETRIES` | Max API request retries | `3` | No |
| `MCP_SERVER_HOST` | Server bind host | `0.0.0.0` | No |
| `MCP_SERVER_PORT` | Server bind port | `8001` | No |
| `MANAGEMENT_API_PORT` | Management API port | `8002` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `LOG_FORMAT` | Log format (json/console) | `json` | No |
| `MCP_AUTH_TOKEN` | Optional auth token | - | No |
| `ENABLE_CACHING` | Enable response caching | `true` | No |
| `CACHE_TTL` | Cache TTL in seconds | `60` | No |
| `ENABLE_RATE_LIMITING` | Enable rate limiting | `true` | No |
| `RATE_LIMIT_REQUESTS` | Max requests per minute | `100` | No |

### Advanced Configuration

For Django integration and webhook support, see [SETUP.md](SETUP.md).

## 🛠️ Available Tools

The MCP server provides 11 tools for managing n8n workflows:

### Workflow Management

#### 1. `list_workflows`
List all workflows with optional filtering.

**Parameters:**
- `status` (string, optional): Filter by status - "active", "inactive", or "all" (default: "all")

**Example:**
```
List all my active workflows
```

#### 2. `get_workflow_details`
Get detailed information about a specific workflow.

**Parameters:**
- `workflow_id` (string, required): Workflow ID

**Example:**
```
Show me details for workflow abc123
```

#### 3. `create_workflow`
Create a new workflow.

**Parameters:**
- `name` (string, required): Workflow name
- `nodes` (array, optional): Node definitions
- `connections` (object, optional): Node connections
- `settings` (object, optional): Workflow settings
- `tags` (array, optional): Workflow tags
- `active` (boolean, optional): Activate immediately (default: false)

**Example:**
```
Create a new workflow called "Daily Email Report"
```

#### 4. `update_workflow`
Update an existing workflow.

**Parameters:**
- `workflow_id` (string, required): Workflow ID
- `name` (string, optional): New name
- `nodes` (array, optional): Updated nodes
- `connections` (object, optional): Updated connections
- `settings` (object, optional): Updated settings
- `tags` (array, optional): Updated tags
- `active` (boolean, optional): Updated activation status

**Example:**
```
Update workflow abc123 to add the tag "production"
```

#### 5. `activate_workflow`
Activate a workflow to start processing.

**Parameters:**
- `workflow_id` (string, required): Workflow ID

**Example:**
```
Activate the "Daily Email Report" workflow
```

#### 6. `deactivate_workflow`
Deactivate a workflow to stop processing.

**Parameters:**
- `workflow_id` (string, required): Workflow ID

**Example:**
```
Deactivate workflow abc123
```

#### 7. `delete_workflow`
Permanently delete a workflow.

**Parameters:**
- `workflow_id` (string, required): Workflow ID
- `confirm` (boolean, required): Confirmation flag

**Example:**
```
Delete workflow abc123
```

#### 8. `search_workflows`
Search for workflows by name or tags.

**Parameters:**
- `query` (string, required): Search query
- `active_only` (boolean, optional): Only search active workflows (default: false)

**Example:**
```
Search for workflows with "email" in the name
```

### Execution Management

#### 9. `execute_workflow`
Manually trigger a workflow execution.

**Parameters:**
- `workflow_id` (string, required): Workflow ID
- `data` (object, optional): Input data for the workflow

**Example:**
```
Execute the "Daily Email Report" workflow
```

#### 10. `get_executions`
Get execution history with filtering.

**Parameters:**
- `workflow_id` (string, optional): Filter by workflow ID
- `status` (string, optional): Filter by status - "success", "error", "waiting", or "all"
- `limit` (integer, optional): Max results (1-250, default: 20)
- `include_data` (boolean, optional): Include full execution data (default: false)

**Example:**
```
Show me the last 10 failed executions
```

### Health & Monitoring

#### 11. `get_workflow_health`
Get health statistics for a workflow.

**Parameters:**
- `workflow_id` (string, required): Workflow ID
- `limit` (integer, optional): Executions to analyze (10-1000, default: 100)

**Example:**
```
Check the health of my "Daily Email Report" workflow
```

## 💬 Usage Examples

### Example 1: List and Activate Workflows

**User:** "Show me all my inactive workflows"

**Claude:** *Uses `list_workflows` with status="inactive"*

```json
{
  "total_count": 3,
  "workflows": [
    {"id": "1", "name": "Email Digest", "active": false},
    {"id": "2", "name": "Data Sync", "active": false},
    {"id": "3", "name": "Report Generator", "active": false}
  ]
}
```

**User:** "Activate the Email Digest workflow"

**Claude:** *Uses `activate_workflow` with workflow_id="1"*

### Example 2: Search and Monitor

**User:** "Find all workflows related to email and check their health"

**Claude:** *Uses `search_workflows` with query="email"*

Then for each workflow, *uses `get_workflow_health`*

### Example 3: Create and Execute

**User:** "Create a new workflow called 'Customer Onboarding' and execute it"

**Claude:**
1. *Uses `create_workflow` with name="Customer Onboarding"*
2. *Uses `execute_workflow` with the new workflow_id*

### Example 4: Troubleshooting

**User:** "Why is my 'Data Sync' workflow failing?"

**Claude:**
1. *Uses `search_workflows` to find the workflow*
2. *Uses `get_workflow_health` to check statistics*
3. *Uses `get_executions` with status="error" to see recent failures*
4. *Analyzes the error data and provides recommendations*

## 🔧 Management API

The MCP server includes a REST API for management operations, designed specifically for integration with the Django Monoliet Portal admin panel. This API runs concurrently with the MCP server and provides administrative capabilities.

### Ports

- **MCP Server:** Port 8001 (MCP protocol - stdio or HTTP)
- **Management API:** Port 8002 (REST API - always HTTP)

### Key Features

- **Health Monitoring:** Check server and n8n connectivity status
- **Workflow Statistics:** Get aggregated workflow metrics
- **Workflow Management:** Activate, deactivate, and execute workflows
- **Configuration Viewing:** Access current server configuration (sensitive data redacted)
- **Authentication:** Bearer token authentication for Django portal integration
- **CORS Support:** Configured for Django portal domains

### Quick Start

The Management API starts automatically when you run the MCP server:

```bash
# Local development
python -m src.server

# Docker
docker-compose up -d
```

The Management API will be available at `http://localhost:8002`

### Example Endpoints

```bash
# Health check (no auth required)
curl http://localhost:8002/health

# Get workflow statistics (requires auth)
curl -H "Authorization: Bearer your-django-token" \
     http://localhost:8002/workflows/stats

# List all workflows (requires auth)
curl -H "Authorization: Bearer your-django-token" \
     http://localhost:8002/workflows

# Activate a workflow (requires auth)
curl -X POST \
     -H "Authorization: Bearer your-django-token" \
     http://localhost:8002/workflows/abc123/activate
```

### Integration with Django Portal

The Management API is designed to be consumed by the **monoliet-portal** Django admin panel:

- All endpoints (except `/health`) require authentication via Django DRF tokens
- Responses are optimized for admin UI display
- CORS is configured for portal domains
- Real-time workflow statistics for dashboard

### Documentation

See [MANAGEMENT_API.md](MANAGEMENT_API.md) for complete API documentation including:
- All available endpoints
- Request/response formats
- Authentication requirements
- Error handling
- Integration examples

### Interactive Documentation

Access auto-generated API documentation:

- **Swagger UI:** `http://localhost:8002/docs`
- **ReDoc:** `http://localhost:8002/redoc`

## 🌐 HTTP API Mode

The MCP server can run in HTTP mode for remote access via REST API (separate from the Management API).

### Enable HTTP Mode

```bash
# Set environment variable
export MCP_SERVER_MODE=http

# Or in .env
MCP_SERVER_MODE=http
```

### API Endpoints

- `GET /health` - Health check
- `GET /tools` - List all available tools
- `POST /call` - Execute a tool
- `GET /sse` - Server-sent events stream

### Example Usage

```bash
# Check health
curl http://localhost:8001/health

# List workflows
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_workflows",
    "arguments": {"status": "all"}
  }'
```

**See [HTTP_API.md](HTTP_API.md) for complete API documentation.**

## 🖥️ Integration with Claude Desktop

### Install Claude Desktop

Download Claude Desktop from [https://claude.ai/download](https://claude.ai/download)

### Configure MCP Server

Edit your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the following:

```json
{
  "mcpServers": {
    "monoliet-n8n": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/monoliet-mcp-server",
      "env": {
        "N8N_URL": "http://your-n8n-instance:5678",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Using Docker with Claude Desktop

For Docker deployment, use the `docker run` command:

```json
{
  "mcpServers": {
    "monoliet-n8n": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network=web",
        "-e", "N8N_URL=http://n8n:5678",
        "-e", "N8N_API_KEY=your-api-key",
        "monoliet-mcp-server"
      ]
    }
  }
}
```

### Restart Claude Desktop

Close and reopen Claude Desktop. You should now see the Monoliet n8n MCP server available in your conversations!

## 🧪 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
monoliet-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── n8n_client.py      # n8n API client
│   ├── config.py          # Configuration management
│   └── tools/             # MCP tools
│       ├── __init__.py
│       ├── base.py        # Base tool class
│       ├── workflows.py   # Workflow tools
│       ├── executions.py  # Execution tools
│       └── health.py      # Health monitoring tools
├── tests/                 # Test suite
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
└── requirements.txt      # Python dependencies
```

## ✅ Testing

### Run All Tests

```bash
# Run test suite
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_n8n_client.py

# Run with verbose output
pytest -v
```

### Test Coverage

Current test coverage: **>80%**

View coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## 🐛 Troubleshooting

### Connection Issues

**Problem:** Can't connect to n8n

**Solutions:**
1. Verify n8n is running: `curl http://localhost:5678`
2. Check API key is valid in n8n settings
3. Ensure `N8N_URL` in `.env` is correct
4. Check network connectivity (Docker network if using containers)

### Authentication Errors

**Problem:** Getting 401/403 errors

**Solutions:**
1. Regenerate your n8n API key
2. Update `.env` with the new key
3. Restart the MCP server

### Tool Not Found

**Problem:** Claude says "tool not found"

**Solutions:**
1. Restart Claude Desktop
2. Check MCP server is running: `docker-compose ps`
3. Verify Claude Desktop config has correct path
4. Check server logs: `docker-compose logs monoliet-mcp`

### Execution Timeouts

**Problem:** Workflow executions timing out

**Solutions:**
1. Increase `N8N_TIMEOUT` in `.env`
2. Check workflow complexity (simplify if needed)
3. Monitor n8n server resources

### Docker Issues

**Problem:** Container won't start

**Solutions:**
```bash
# Check logs
docker-compose logs

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check network exists
docker network ls | grep web
docker network create web  # If missing
```

## 📊 Performance & Limits

- **Rate Limiting:** 100 requests/minute (configurable)
- **Execution Timeout:** 30 seconds (configurable)
- **Max Executions Query:** 250 executions
- **Cache TTL:** 60 seconds (configurable)

## 🔒 Security

- API keys stored in environment variables (never committed)
- Non-root Docker user
- Input validation on all tools
- HTTPS support for n8n connections
- Optional authentication token for MCP server

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/monoliet/monoliet-mcp-server/issues)
- **Discussions:** [GitHub Discussions](https://github.com/monoliet/monoliet-mcp-server/discussions)
- **Email:** support@monoliet.com

## 🙏 Acknowledgments

- Built with [Anthropic MCP SDK](https://github.com/anthropics/python-sdk)
- Powered by [n8n](https://n8n.io/)
- Inspired by the Claude Code community

---

**Made with ❤️ by Monoliet**
