# Management API Documentation

## Overview

The Monoliet MCP Server provides a REST API for management operations, designed specifically for integration with the Django Monoliet Portal admin panel.

This API runs concurrently with the MCP protocol server and provides administrative endpoints for monitoring, workflow management, and configuration.

## Base URL

- **Local Development:** `http://localhost:8002`
- **Docker:** `http://monoliet-mcp-server:8002`
- **Production:** `https://mcp-api.monoliet.cloud` (configure in reverse proxy)

## Authentication

All endpoints (except `/health`) require Bearer token authentication:

```http
Authorization: Bearer <django-portal-token>
```

The token is provided by the Django portal's DRF authentication system. The Management API accepts any valid bearer token (Django portal handles its own authentication and authorization).

## Endpoints

### Health & Monitoring

#### `GET /health`

Health check endpoint (no authentication required).

**Response:**
```json
{
  "healthy": true,
  "n8n_reachable": true,
  "database_connected": true,
  "errors": []
}
```

**Status Codes:**
- `200 OK`: Health check completed (check response for actual health status)

---

#### `GET /status`

Comprehensive server status (requires authentication).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "operational",
  "uptime_seconds": 3600.0,
  "n8n_connected": true,
  "n8n_url": "https://n8n.monoliet.cloud",
  "mcp_port": 8001,
  "management_port": 8002,
  "version": "0.1.0",
  "timestamp": "2026-01-19T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved status
- `401 Unauthorized`: Missing or invalid authentication token

---

### Workflows

#### `GET /workflows/stats`

Get aggregated workflow statistics (requires authentication).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_workflows": 42,
  "active_workflows": 38,
  "paused_workflows": 4,
  "error_workflows": 0,
  "total_executions_today": 0,
  "success_rate": 0.0
}
```

**Note:** `error_workflows`, `total_executions_today`, and `success_rate` are placeholder values (currently 0) and will be implemented in future versions.

**Status Codes:**
- `200 OK`: Successfully retrieved statistics
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Failed to fetch workflow statistics

---

#### `GET /workflows`

List all workflows with optional filtering (requires authentication).

**Headers:**
```http
Authorization: Bearer <token>
```

**Query Parameters:**
- `active_only` (boolean, optional): Only return active workflows
- `search` (string, optional): Search by workflow name (case-insensitive)

**Example Request:**
```http
GET /workflows?active_only=true&search=customer
```

**Response:**
```json
{
  "workflows": [
    {
      "id": "abc123",
      "name": "Customer Onboarding",
      "active": true,
      "tags": ["crm", "automation"],
      "createdAt": "2026-01-15T10:00:00Z",
      "updatedAt": "2026-01-19T08:30:00Z"
    }
  ],
  "count": 1
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved workflows
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Failed to list workflows

---

#### `GET /workflows/{workflow_id}`

Get detailed information about a specific workflow (requires authentication).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "workflow": {
    "id": "abc123",
    "name": "Customer Onboarding",
    "active": true,
    "tags": ["crm", "automation"],
    "nodes": [...],
    "connections": {...},
    "settings": {...},
    "createdAt": "2026-01-15T10:00:00Z",
    "updatedAt": "2026-01-19T08:30:00Z"
  }
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved workflow
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Workflow not found
- `500 Internal Server Error`: Failed to get workflow

---

#### `POST /workflows/{workflow_id}/activate`

Activate a workflow (requires authentication).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "abc123",
  "data": {
    "id": "abc123",
    "name": "Customer Onboarding",
    "active": true,
    ...
  }
}
```

**Status Codes:**
- `200 OK`: Successfully activated workflow
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Failed to activate workflow

---

#### `POST /workflows/{workflow_id}/deactivate`

Deactivate a workflow (requires authentication).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "abc123",
  "data": {
    "id": "abc123",
    "name": "Customer Onboarding",
    "active": false,
    ...
  }
}
```

**Status Codes:**
- `200 OK`: Successfully deactivated workflow
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Failed to deactivate workflow

---

#### `POST /workflows/{workflow_id}/execute`

Manually trigger workflow execution (requires authentication).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "abc123",
  "execution_id": "exec_xyz789"
}
```

**Status Codes:**
- `200 OK`: Successfully triggered execution
- `401 Unauthorized`: Missing or invalid authentication token
- `500 Internal Server Error`: Failed to execute workflow

---

### Configuration

#### `GET /config`

Get current configuration with sensitive data redacted (requires authentication).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response:**
```json
{
  "n8n_url": "https://n8n.monoliet.cloud",
  "n8n_api_key_set": true,
  "mcp_server_port": 8001,
  "management_api_port": 8002,
  "log_level": "INFO"
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved configuration
- `401 Unauthorized`: Missing or invalid authentication token

---

#### `PUT /config`

Update configuration (requires authentication).

**Note:** This endpoint is not implemented. Configuration changes require updating the `.env` file and restarting the server.

**Headers:**
```http
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "n8n_url": "https://new-n8n.monoliet.cloud",
  "log_level": "DEBUG"
}
```

**Response:**
```json
{
  "detail": "Configuration updates require server restart. Update .env file and restart container."
}
```

**Status Codes:**
- `501 Not Implemented`: Configuration updates not supported

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `501 Not Implemented`: Feature not implemented

---

## Integration with Django Portal

The Django portal (`monoliet-portal` repository) integrates with this API by:

1. Storing the MCP server URL in the `PortalSettings` model
2. Using Django REST Framework tokens for authentication
3. Calling these endpoints from admin panel views
4. Displaying results in a Palantir-inspired UI

### Example Django Integration

```python
import requests

# Django portal settings
MCP_API_URL = "http://monoliet-mcp-server:8002"
AUTH_TOKEN = request.user.auth_token.key

# Get workflow statistics
response = requests.get(
    f"{MCP_API_URL}/workflows/stats",
    headers={"Authorization": f"Bearer {AUTH_TOKEN}"}
)

if response.status_code == 200:
    stats = response.json()
    # Display stats in admin UI
```

---

## Development

### Running Management API Standalone

For development and testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export N8N_URL=https://n8n.monoliet.cloud
export N8N_API_KEY=your-api-key
export MANAGEMENT_API_PORT=8002

# Run with uvicorn
uvicorn src.management_api:management_app --reload --port 8002
```

### Access Interactive Documentation

The Management API provides auto-generated interactive documentation:

- **Swagger UI:** `http://localhost:8002/docs`
- **ReDoc:** `http://localhost:8002/redoc`

---

## CORS Configuration

The Management API is configured to accept requests from:

- `http://localhost:8000` (Django local development)
- `http://127.0.0.1:8000` (Django local development)
- Django portal URL from `DJANGO_PORTAL_URL` environment variable

If you need to add additional origins, update the `setup_cors()` function in `src/management_api.py`.

---

## Security Considerations

### Authentication

- All endpoints (except `/health`) require Bearer token authentication
- Tokens are validated but not verified against Django portal (Django handles auth)
- Minimum token length: 10 characters

### Data Protection

- n8n API keys are never exposed in responses
- Configuration endpoint redacts sensitive information
- All requests are logged for audit purposes

### Rate Limiting

Currently not implemented. Consider implementing rate limiting at the reverse proxy level (Nginx, etc.).

---

## Future Enhancements

- Implement execution statistics (`total_executions_today`, `success_rate`)
- Add error workflow detection
- Support for runtime configuration updates
- WebSocket support for real-time workflow status updates
- Rate limiting middleware
- Enhanced authentication (verify tokens against Django portal)

---

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review the Django portal integration guide
- Check server logs: `docker logs monoliet-mcp-server`
