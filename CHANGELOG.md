# Changelog

All notable changes to the Monoliet MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Workflow template library
- Bulk workflow operations
- Advanced filtering and sorting
- Workflow export/import
- Real-time execution monitoring
- Webhook management tools
- Workflow versioning support

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
