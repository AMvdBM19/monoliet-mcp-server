# Changelog

All notable changes to the Monoliet MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Authentication middleware (Bearer tokens)
- WebSocket support for real-time updates
- Workflow template library
- Bulk workflow operations
- Advanced filtering and sorting
- Workflow export/import
- Webhook management tools
- Workflow versioning support
- Rate limiting per client
- Metrics endpoint (Prometheus)

## [0.2.0] - 2026-01-19

### Added - HTTP Mode Support 🌐
- **Dual mode support**: Server can now run in either stdio or HTTP mode
- **HTTP REST API** with 4 endpoints:
  - `GET /health` - Server health check with n8n connectivity status
  - `GET /tools` - List all available MCP tools
  - `POST /call` - Execute any MCP tool via REST API
  - `GET /sse` - Server-Sent Events endpoint for real-time updates
- **Mode selection** via `MCP_SERVER_MODE` environment variable
- **Complete HTTP API documentation** (HTTP_API.md)
- **HTTP test suite** (test_http_api.py) with automated endpoint testing
- **aiohttp integration** for async HTTP server
- **CORS support** for development
- **Docker pre-configured** for HTTP mode with health checks
- **curl support** in Docker for HTTP health checks

### Changed
- Default Docker mode is now **HTTP** instead of stdio
- Health check in Docker uses HTTP endpoint instead of Python check
- README updated with dual-mode documentation
- Configuration examples updated for both modes

### Documentation
- New HTTP_API.md with complete REST API documentation
- Updated README.md with mode selection guide
- New HTTP_MODE_UPDATE.md summarizing the changes
- Integration examples for Python, JavaScript, and Go
- Troubleshooting guide for HTTP mode

### Infrastructure
- Added aiohttp>=3.9.0 dependency
- Updated Docker health check to use curl
- Added MCP_SERVER_MODE to docker-compose.yml

## [0.1.0] - 2024-01-18

### Added
- Initial release of Monoliet MCP Server
- Core n8n API client with full async support
- 11 MCP tools for workflow management:
  - `list_workflows` - List all workflows with filtering
  - `get_workflow_details` - Get detailed workflow information
  - `create_workflow` - Create new workflows
  - `update_workflow` - Update existing workflows
  - `activate_workflow` - Activate workflows
  - `deactivate_workflow` - Deactivate workflows
  - `delete_workflow` - Delete workflows
  - `search_workflows` - Search workflows by name/tags
  - `execute_workflow` - Manually trigger workflow execution
  - `get_executions` - Get execution history
  - `get_workflow_health` - Monitor workflow health and statistics
- Production-ready error handling and logging
- Retry logic for API requests with exponential backoff
- Docker and docker-compose support
- Comprehensive test suite with >80% coverage
- Configuration management via environment variables
- Health check script for deployment validation
- Quick start scripts for macOS, Linux, and Windows
- Complete documentation:
  - README.md with features and usage examples
  - SETUP.md with deployment guides
  - QUICKSTART.md for 5-minute setup
  - CONTRIBUTING.md for developers
- CI/CD with GitHub Actions
- Type hints throughout codebase
- Structured logging support

### Infrastructure
- Python 3.11+ support
- Async/await throughout
- httpx for HTTP client
- Pydantic for configuration validation
- pytest for testing framework
- Docker multi-stage build
- Non-root Docker user for security

### Documentation
- Comprehensive API documentation
- Integration guide for Claude Desktop
- VPS deployment guide
- Docker deployment guide
- Troubleshooting section
- Usage examples

### Security
- Environment-based configuration
- API key validation
- Input sanitization
- Non-root Docker execution
- Optional authentication token support

## [0.0.1] - 2024-01-15

### Added
- Initial project structure
- Basic n8n client prototype
- Repository setup with .gitignore and LICENSE

---

## Version History Links

[Unreleased]: https://github.com/monoliet/monoliet-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/monoliet/monoliet-mcp-server/releases/tag/v0.1.0
[0.0.1]: https://github.com/monoliet/monoliet-mcp-server/releases/tag/v0.0.1
