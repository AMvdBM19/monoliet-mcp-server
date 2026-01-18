# MCP Server Verification Checklist

Use this checklist to verify your Monoliet MCP Server installation is complete and working correctly.

## 📋 Pre-Deployment Checklist

### Files & Structure

- [ ] All source files present in `src/`
  - [ ] `src/__init__.py`
  - [ ] `src/server.py`
  - [ ] `src/n8n_client.py`
  - [ ] `src/config.py`
  - [ ] `src/tools/__init__.py`
  - [ ] `src/tools/base.py`
  - [ ] `src/tools/workflows.py`
  - [ ] `src/tools/executions.py`
  - [ ] `src/tools/health.py`

- [ ] All test files present in `tests/`
  - [ ] `tests/__init__.py`
  - [ ] `tests/test_n8n_client.py`
  - [ ] `tests/test_tools.py`

- [ ] Configuration files present
  - [ ] `requirements.txt`
  - [ ] `pyproject.toml`
  - [ ] `Dockerfile`
  - [ ] `docker-compose.yml`
  - [ ] `.env.example`
  - [ ] `.gitignore`
  - [ ] `pytest.ini`

- [ ] Documentation files present
  - [ ] `README.md`
  - [ ] `SETUP.md`
  - [ ] `QUICKSTART.md`
  - [ ] `CONTRIBUTING.md`
  - [ ] `CHANGELOG.md`
  - [ ] `LICENSE`
  - [ ] `PROJECT_SUMMARY.md`

- [ ] Utility scripts present
  - [ ] `health_check.py`
  - [ ] `start.sh`
  - [ ] `start.bat`

- [ ] CI/CD files present
  - [ ] `.github/workflows/ci.yml`

## 🔧 Setup Verification

### Environment Configuration

- [ ] `.env` file created (copy from `.env.example`)
- [ ] `N8N_URL` configured
- [ ] `N8N_API_KEY` configured
- [ ] Other optional settings reviewed

### Dependencies

```bash
# Verify Python version
python --version  # Should be 3.11+

# Install dependencies
pip install -r requirements.txt

# Verify key packages installed
python -c "import mcp; print('MCP SDK:', mcp.__version__)"
python -c "import httpx; print('httpx:', httpx.__version__)"
python -c "import pydantic; print('Pydantic:', pydantic.__version__)"
```

- [ ] Python 3.11+ installed
- [ ] All dependencies installed successfully
- [ ] No import errors

## 🧪 Testing Verification

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Expected: All tests pass, coverage >80%
```

- [ ] All tests pass
- [ ] Test coverage >80%
- [ ] No import errors in tests

### Test Individual Components

```bash
# Test n8n client
pytest tests/test_n8n_client.py -v

# Test tools
pytest tests/test_tools.py -v
```

- [ ] n8n client tests pass
- [ ] Tool tests pass

## 🏥 Health Check

### Run Health Check Script

```bash
python health_check.py
```

Expected output:
```
✅ Configuration: PASS
✅ n8n Connection: PASS
✅ Workflow Listing: PASS
✅ API Permissions: PASS
✅ MCP Tools Import: PASS

🎉 All health checks passed!
```

- [ ] Configuration check passes
- [ ] n8n connection check passes
- [ ] Workflow listing check passes
- [ ] API permissions check passes
- [ ] MCP tools import check passes

## 🐳 Docker Verification (if using Docker)

### Build & Run

```bash
# Create network
docker network create web

# Build and start
docker-compose build
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs monoliet-mcp
```

- [ ] Docker network created
- [ ] Docker image builds successfully
- [ ] Container starts without errors
- [ ] Logs show successful n8n connection

## 🖥️ Claude Desktop Integration

### Configuration

- [ ] Claude Desktop installed
- [ ] Config file created/edited
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- [ ] MCP server added to config
- [ ] Paths are absolute (not relative)
- [ ] Environment variables set correctly

### Example Config

```json
{
  "mcpServers": {
    "monoliet-n8n": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/monoliet-mcp-server",
      "env": {
        "N8N_URL": "http://localhost:5678",
        "N8N_API_KEY": "your-api-key"
      }
    }
  }
}
```

- [ ] Config syntax is valid JSON
- [ ] Paths use forward slashes (even on Windows in JSON)
- [ ] Environment variables match `.env`

## 🔍 Claude Desktop Testing

### Restart Claude

- [ ] Claude Desktop completely quit
- [ ] Claude Desktop restarted
- [ ] Wait 10 seconds for initialization

### Test Commands

Try these in Claude Desktop:

1. **List workflows**
   ```
   List all my workflows
   ```
   - [ ] Tool `list_workflows` is called
   - [ ] Workflows are returned
   - [ ] No errors

2. **Search workflows**
   ```
   Search for workflows with "test" in the name
   ```
   - [ ] Tool `search_workflows` is called
   - [ ] Results returned
   - [ ] No errors

3. **Get workflow details**
   ```
   Show me details for workflow [id]
   ```
   - [ ] Tool `get_workflow_details` is called
   - [ ] Details returned
   - [ ] No errors

4. **Check workflow health**
   ```
   Check the health of workflow [id]
   ```
   - [ ] Tool `get_workflow_health` is called
   - [ ] Statistics returned
   - [ ] Recommendations provided

5. **Get executions**
   ```
   Show me the last 5 executions
   ```
   - [ ] Tool `get_executions` is called
   - [ ] Execution history returned
   - [ ] No errors

## 🚨 Troubleshooting Checks

### If tests fail

- [ ] Check Python version (must be 3.11+)
- [ ] Verify all dependencies installed
- [ ] Check for import errors
- [ ] Review test output for specific failures

### If health check fails

- [ ] Verify n8n is running
- [ ] Test n8n API manually:
  ```bash
  curl http://localhost:5678/api/v1/workflows \
    -H "X-N8N-API-KEY: your-api-key"
  ```
- [ ] Check `.env` configuration
- [ ] Verify API key is valid
- [ ] Check network connectivity

### If Claude can't connect

- [ ] Restart Claude Desktop completely
- [ ] Check server is running:
  ```bash
  ps aux | grep "src.server"
  # or
  docker-compose ps
  ```
- [ ] Verify config file syntax (valid JSON)
- [ ] Check paths are absolute
- [ ] Review Claude Desktop logs (if available)
- [ ] Try running server manually:
  ```bash
  python -m src.server
  ```

### If Docker fails

- [ ] Check Docker is running
- [ ] Verify `web` network exists:
  ```bash
  docker network ls | grep web
  ```
- [ ] Review container logs:
  ```bash
  docker-compose logs monoliet-mcp
  ```
- [ ] Rebuild container:
  ```bash
  docker-compose down
  docker-compose build --no-cache
  docker-compose up -d
  ```

## ✅ Final Verification

All checks should be complete:

- [ ] ✅ Files and structure verified
- [ ] ✅ Setup completed
- [ ] ✅ Tests passing
- [ ] ✅ Health check passing
- [ ] ✅ Docker running (if applicable)
- [ ] ✅ Claude Desktop configured
- [ ] ✅ Tools working in Claude

## 📊 Success Metrics

When everything is working:

✅ **Health Check**: All 5 checks pass
✅ **Test Coverage**: >80%
✅ **Claude Integration**: All tools callable
✅ **No Errors**: Clean logs and outputs
✅ **Response Time**: Tools respond <2 seconds

## 🎉 You're Ready!

If all checks pass, your Monoliet MCP Server is ready for production use!

### What to do next:

1. Start managing workflows with Claude
2. Explore all 11 tools
3. Set up monitoring (optional)
4. Consider contributing improvements
5. Share feedback and suggestions

## 📝 Notes

Use this space for your own notes:

```
Installation date: _______________
n8n version: _______________
Python version: _______________
Deployment type: [ ] Local [ ] Docker [ ] VPS
Issues encountered:



Resolutions:



```

---

**Need help?** Check SETUP.md troubleshooting section or open a GitHub issue.
