# HTTP API Documentation

The Monoliet MCP Server can run in **HTTP mode** for remote access, in addition to stdio mode for Claude Desktop integration.

## 🚀 Quick Start

### Enable HTTP Mode

Set the environment variable:

```bash
export MCP_SERVER_MODE=http
```

Or in your `.env` file:

```env
MCP_SERVER_MODE=http
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
```

### Start Server

**Local:**
```bash
MCP_SERVER_MODE=http python -m src.server
```

**Docker:**
```bash
# Already configured to use HTTP mode by default
docker-compose up -d
```

## 📡 API Endpoints

### Health Check

Check server and n8n connection health.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "n8n": {
    "status": "healthy",
    "url": "http://localhost:5678",
    "message": "Successfully connected to n8n"
  },
  "tools_count": 11
}
```

**Example:**
```bash
curl http://localhost:8001/health
```

---

### List Tools

Get all available MCP tools.

**Endpoint:** `GET /tools`

**Response:**
```json
{
  "tools": [
    {
      "name": "list_workflows",
      "description": "List all n8n workflows...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "status": {
            "type": "string",
            "enum": ["active", "inactive", "all"]
          }
        }
      }
    }
  ],
  "count": 11
}
```

**Example:**
```bash
curl http://localhost:8001/tools
```

---

### Call Tool

Execute an MCP tool.

**Endpoint:** `POST /call`

**Request Body:**
```json
{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    // Tool-specific response data
  },
  "error": null
}
```

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "type": "error_type",
    "message": "Error message"
  }
}
```

---

### Server-Sent Events (SSE)

Real-time connection endpoint (for future MCP protocol support).

**Endpoint:** `GET /sse`

**Response:** Event stream with keepalive messages.

**Example:**
```bash
curl -N http://localhost:8001/sse
```

## 🛠️ Tool Examples

### List Workflows

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_workflows",
    "arguments": {
      "status": "active"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_count": 5,
    "filter": "active",
    "workflows": [
      {
        "id": "1",
        "name": "Daily Email Report",
        "active": true,
        "tags": ["email", "automation"],
        "created_at": "2024-01-15T10:00:00Z"
      }
    ]
  },
  "error": null
}
```

---

### Get Workflow Details

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_workflow_details",
    "arguments": {
      "workflow_id": "1"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "1",
    "name": "Daily Email Report",
    "active": true,
    "nodes": [...],
    "connections": {...},
    "node_count": 5
  },
  "error": null
}
```

---

### Search Workflows

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_workflows",
    "arguments": {
      "query": "email",
      "active_only": true
    }
  }'
```

---

### Execute Workflow

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "execute_workflow",
    "arguments": {
      "workflow_id": "1",
      "data": {
        "email": "test@example.com"
      }
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec-123",
    "workflow_id": "1",
    "status": "success",
    "started_at": "2024-01-18T10:00:00Z"
  },
  "error": null
}
```

---

### Get Executions

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_executions",
    "arguments": {
      "workflow_id": "1",
      "limit": 10,
      "status": "error"
    }
  }'
```

---

### Get Workflow Health

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_workflow_health",
    "arguments": {
      "workflow_id": "1",
      "limit": 100
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "workflow_id": "1",
    "workflow_name": "Daily Email Report",
    "is_active": true,
    "health_status": "excellent",
    "statistics": {
      "total_executions": 100,
      "success_count": 98,
      "error_count": 2,
      "success_rate": 98.0,
      "error_rate": 2.0
    },
    "recommendations": [
      "Excellent! Workflow is running smoothly with no errors."
    ]
  },
  "error": null
}
```

---

### Create Workflow

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "create_workflow",
    "arguments": {
      "name": "New Workflow",
      "nodes": [],
      "connections": {},
      "active": false
    }
  }'
```

---

### Activate Workflow

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "activate_workflow",
    "arguments": {
      "workflow_id": "1"
    }
  }'
```

---

### Delete Workflow

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "delete_workflow",
    "arguments": {
      "workflow_id": "1",
      "confirm": true
    }
  }'
```

## 🔒 Security

### Authentication (Coming Soon)

Future versions will support authentication via the `MCP_AUTH_TOKEN`:

```bash
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{...}'
```

### HTTPS

For production, use a reverse proxy (nginx, Caddy) with SSL:

```nginx
server {
    listen 443 ssl;
    server_name mcp.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 🐳 Docker Deployment

The Docker setup is pre-configured for HTTP mode:

```bash
# Start in HTTP mode (default)
docker-compose up -d

# Test endpoints
curl http://localhost:8001/health
curl http://localhost:8001/tools
```

## 🌐 Remote Access

### Via SSH Tunnel

```bash
# On your local machine
ssh -L 8001:localhost:8001 user@your-vps

# Access locally
curl http://localhost:8001/health
```

### Via Nginx Reverse Proxy

```bash
# Install nginx on VPS
sudo apt install nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/mcp

# Add configuration (see HTTPS section above)

# Enable and restart
sudo ln -s /etc/nginx/sites-available/mcp /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 📊 Python Client Example

```python
import httpx
import asyncio

class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def call_tool(self, tool: str, arguments: dict):
        response = await self.client.post(
            f"{self.base_url}/call",
            json={"tool": tool, "arguments": arguments}
        )
        return response.json()

    async def list_tools(self):
        response = await self.client.get(f"{self.base_url}/tools")
        return response.json()

    async def health_check(self):
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()

async def main():
    client = MCPClient()

    # Health check
    health = await client.health_check()
    print(f"Health: {health}")

    # List workflows
    result = await client.call_tool("list_workflows", {"status": "all"})
    print(f"Workflows: {result}")

asyncio.run(main())
```

## 🧪 Testing

```bash
# Health check
curl http://localhost:8001/health

# List all tools
curl http://localhost:8001/tools | jq

# Execute a tool
curl -X POST http://localhost:8001/call \
  -H "Content-Type: application/json" \
  -d '{"tool": "list_workflows", "arguments": {"status": "all"}}' \
  | jq
```

## 🔄 Switching Modes

### stdio → HTTP

```bash
# Stop stdio server
# Set environment
export MCP_SERVER_MODE=http

# Restart
python -m src.server
```

### HTTP → stdio

```bash
# Stop HTTP server
# Set environment
export MCP_SERVER_MODE=stdio

# Restart
python -m src.server
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8001
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill process or change port
export MCP_SERVER_PORT=8002
```

### Connection Refused

```bash
# Check server is running
docker-compose ps

# Check logs
docker-compose logs monoliet-mcp

# Verify port mapping
docker-compose port monoliet-mcp 8001
```

### CORS Issues

The server includes CORS headers for development. For production, configure your reverse proxy.

## 📚 Integration Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function listWorkflows() {
  const response = await axios.post('http://localhost:8001/call', {
    tool: 'list_workflows',
    arguments: { status: 'all' }
  });
  return response.data;
}
```

### Go

```go
import (
    "bytes"
    "encoding/json"
    "net/http"
)

func callTool(tool string, args map[string]interface{}) (map[string]interface{}, error) {
    payload := map[string]interface{}{
        "tool": tool,
        "arguments": args,
    }

    jsonData, _ := json.Marshal(payload)
    resp, err := http.Post(
        "http://localhost:8001/call",
        "application/json",
        bytes.NewBuffer(jsonData),
    )

    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    return result, err
}
```

---

**Need help?** See [README.md](README.md) for more information.
