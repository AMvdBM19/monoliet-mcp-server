# Setup Guide - Monoliet MCP Server

This guide provides detailed instructions for setting up and deploying the Monoliet MCP Server for n8n workflow management.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [VPS Deployment](#vps-deployment)
3. [Claude Desktop Integration](#claude-desktop-integration)
4. [Django Integration (Optional)](#django-integration-optional)
5. [Testing Your Setup](#testing-your-setup)
6. [Maintenance & Updates](#maintenance--updates)

---

## Local Development Setup

### Step 1: Prerequisites

Install required software:

```bash
# Python 3.11+
python --version  # Should be 3.11 or higher

# pip
pip --version

# git
git --version

# Docker (optional)
docker --version
docker-compose --version
```

### Step 2: Clone Repository

```bash
git clone https://github.com/monoliet/monoliet-mcp-server.git
cd monoliet-mcp-server
```

### Step 3: Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

Minimal `.env` configuration:

```env
N8N_URL=http://localhost:5678
N8N_API_KEY=your-api-key-here
MCP_SERVER_PORT=8001
LOG_LEVEL=INFO
```

### Step 6: Run the Server

```bash
# Run directly
python -m src.server

# Or with logging
python -m src.server 2>&1 | tee mcp-server.log
```

The server should start and connect to n8n. Check logs for any errors.

---

## VPS Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux VPS
- Root or sudo access
- n8n already deployed on the same VPS or network

### Step 1: Connect to Your VPS

```bash
ssh user@your-vps-ip
```

### Step 2: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Docker & Docker Compose
sudo apt install docker.io docker-compose -y

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

### Step 3: Clone and Setup Project

```bash
# Create directory
mkdir -p /opt/monoliet
cd /opt/monoliet

# Clone repository
git clone https://github.com/monoliet/monoliet-mcp-server.git
cd monoliet-mcp-server

# Copy environment file
cp .env.example .env
```

### Step 4: Configure for Production

Edit `.env`:

```bash
nano .env
```

Production configuration:

```env
# n8n Configuration
N8N_URL=http://n8n:5678  # Use container name if n8n is in Docker
N8N_API_KEY=your-production-api-key
N8N_TIMEOUT=30
N8N_MAX_RETRIES=3

# MCP Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
MCP_AUTH_TOKEN=your-secure-token-here

# Performance
ENABLE_CACHING=true
CACHE_TTL=60
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
```

### Step 5: Create Docker Network

```bash
# Create external network (if not exists)
docker network create web
```

### Step 6: Deploy with Docker Compose

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f monoliet-mcp
```

### Step 7: Setup Systemd Service (Alternative to Docker)

If you prefer running without Docker:

Create systemd service:

```bash
sudo nano /etc/systemd/system/monoliet-mcp.service
```

Add:

```ini
[Unit]
Description=Monoliet MCP Server for n8n
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/monoliet/monoliet-mcp-server
Environment="PATH=/opt/monoliet/monoliet-mcp-server/venv/bin"
EnvironmentFile=/opt/monoliet/monoliet-mcp-server/.env
ExecStart=/opt/monoliet/monoliet-mcp-server/venv/bin/python -m src.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable monoliet-mcp
sudo systemctl start monoliet-mcp

# Check status
sudo systemctl status monoliet-mcp

# View logs
sudo journalctl -u monoliet-mcp -f
```

### Step 8: Configure Firewall (Optional)

```bash
# Allow MCP port
sudo ufw allow 8001/tcp

# Reload firewall
sudo ufw reload
```

---

## Claude Desktop Integration

### macOS Setup

1. **Install Claude Desktop**

   Download from: https://claude.ai/download

2. **Locate Configuration File**

   ```bash
   cd ~/Library/Application\ Support/Claude/
   ```

3. **Edit Configuration**

   ```bash
   nano claude_desktop_config.json
   ```

4. **Add MCP Server Configuration**

   **For Local Development:**

   ```json
   {
     "mcpServers": {
       "monoliet-n8n": {
         "command": "python",
         "args": ["-m", "src.server"],
         "cwd": "/Users/yourname/path/to/monoliet-mcp-server",
         "env": {
           "N8N_URL": "http://localhost:5678",
           "N8N_API_KEY": "your-api-key"
         }
       }
     }
   }
   ```

   **For VPS/Remote Deployment:**

   If MCP server is running on VPS, you can use SSH tunneling or connect via HTTP:

   ```json
   {
     "mcpServers": {
       "monoliet-n8n": {
         "command": "ssh",
         "args": [
           "user@your-vps",
           "cd /opt/monoliet/monoliet-mcp-server && docker-compose exec -T monoliet-mcp python -m src.server"
         ]
       }
     }
   }
   ```

   **For Docker (Local):**

   ```json
   {
     "mcpServers": {
       "monoliet-n8n": {
         "command": "docker",
         "args": [
           "exec",
           "-i",
           "monoliet-mcp-server",
           "python",
           "-m",
           "src.server"
         ]
       }
     }
   }
   ```

5. **Restart Claude Desktop**

   Quit Claude Desktop completely and restart it.

### Windows Setup

1. **Install Claude Desktop**

   Download from: https://claude.ai/download

2. **Locate Configuration File**

   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

   Or navigate to:
   ```
   C:\Users\YourUsername\AppData\Roaming\Claude\
   ```

3. **Edit Configuration**

   Use Notepad or any text editor:

   ```json
   {
     "mcpServers": {
       "monoliet-n8n": {
         "command": "python",
         "args": ["-m", "src.server"],
         "cwd": "C:\\Users\\YourName\\path\\to\\monoliet-mcp-server",
         "env": {
           "N8N_URL": "http://localhost:5678",
           "N8N_API_KEY": "your-api-key"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

### Verify Integration

1. Open Claude Desktop
2. Start a new conversation
3. Type: "List all workflows"
4. Claude should use the `list_workflows` tool

---

## Django Integration (Optional)

If you're integrating with a Django portal for webhook notifications:

### Step 1: Configure Django Settings

In your `.env`:

```env
DJANGO_PORTAL_URL=https://your-django-app.com
DJANGO_WEBHOOK_TOKEN=your-webhook-secret-token
```

### Step 2: Django Webhook Endpoint

Create a webhook endpoint in Django to receive notifications from n8n via MCP:

```python
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def n8n_webhook(request):
    if request.method == 'POST':
        # Verify token
        token = request.headers.get('Authorization')
        if token != f"Bearer {settings.WEBHOOK_TOKEN}":
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        # Process webhook data
        data = json.loads(request.body)

        # Handle workflow events
        # ... your logic here

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
```

### Step 3: Add URL Pattern

```python
# urls.py
urlpatterns = [
    path('webhooks/n8n/', n8n_webhook, name='n8n_webhook'),
]
```

---

## Testing Your Setup

### 1. Test n8n Connection

```bash
# Using curl
curl -X GET \
  http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: your-api-key"
```

Expected: JSON response with workflows list

### 2. Test MCP Server

```bash
# Check if server is running
ps aux | grep "src.server"

# Or with Docker
docker-compose ps
```

### 3. Test with Claude Desktop

Open Claude Desktop and try these commands:

```
1. "List all my workflows"
2. "Show me details for workflow [workflow-id]"
3. "Search for workflows with 'email'"
4. "Check the health of workflow [workflow-id]"
```

### 4. Run Unit Tests

```bash
# From project directory
pytest

# With coverage
pytest --cov=src --cov-report=html
```

---

## Maintenance & Updates

### Update the Server

```bash
cd /opt/monoliet/monoliet-mcp-server

# Pull latest changes
git pull origin main

# Rebuild Docker container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or restart systemd service
sudo systemctl restart monoliet-mcp
```

### View Logs

**Docker:**
```bash
docker-compose logs -f monoliet-mcp
```

**Systemd:**
```bash
sudo journalctl -u monoliet-mcp -f
```

### Backup Configuration

```bash
# Backup .env file
cp .env .env.backup-$(date +%Y%m%d)

# Backup entire directory
tar -czf monoliet-mcp-backup-$(date +%Y%m%d).tar.gz /opt/monoliet/monoliet-mcp-server
```

### Monitor Performance

```bash
# Check resource usage
docker stats monoliet-mcp-server

# Check system resources
htop
```

### Troubleshooting Tips

1. **Server won't start:**
   - Check `.env` file for correct values
   - Verify n8n is accessible
   - Check logs for specific errors

2. **Claude Desktop can't connect:**
   - Restart Claude Desktop
   - Verify config file syntax (valid JSON)
   - Check server is running

3. **API errors:**
   - Regenerate n8n API key
   - Check n8n API is enabled
   - Verify network connectivity

---

## Advanced Configuration

### Enable HTTPS

If your n8n instance uses HTTPS:

```env
N8N_URL=https://your-n8n-domain.com
```

### Custom Logging

For more detailed logs:

```env
LOG_LEVEL=DEBUG
LOG_FORMAT=console  # For human-readable logs
```

### Rate Limiting Adjustments

For high-volume usage:

```env
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=500  # Increase limit
```

### Cache Configuration

Adjust caching for better performance:

```env
ENABLE_CACHING=true
CACHE_TTL=300  # 5 minutes
```

---

## Security Best Practices

1. **Never commit `.env` to version control**
2. **Use strong API keys** (generate with: `openssl rand -hex 32`)
3. **Regularly rotate credentials**
4. **Use HTTPS** for production n8n instances
5. **Limit network access** with firewall rules
6. **Monitor logs** for suspicious activity
7. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`

---

## Getting Help

If you encounter issues:

1. Check the [README.md](README.md) troubleshooting section
2. View server logs for error messages
3. Search [GitHub Issues](https://github.com/monoliet/monoliet-mcp-server/issues)
4. Create a new issue with:
   - Your setup (local/VPS/Docker)
   - Error messages from logs
   - Steps to reproduce
   - System information

---

**Happy Automating!** 🚀
