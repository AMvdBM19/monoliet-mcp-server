# Quick Start Guide

Get up and running with Monoliet MCP Server in 5 minutes!

## Prerequisites

- Python 3.11+
- Running n8n instance
- n8n API key

## Installation

### Option 1: Automated Setup (Recommended)

**macOS/Linux:**
```bash
git clone https://github.com/monoliet/monoliet-mcp-server.git
cd monoliet-mcp-server
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
git clone https://github.com/monoliet/monoliet-mcp-server.git
cd monoliet-mcp-server
start.bat
```

### Option 2: Manual Setup

```bash
# 1. Clone
git clone https://github.com/monoliet/monoliet-mcp-server.git
cd monoliet-mcp-server

# 2. Setup environment
cp .env.example .env
# Edit .env with your n8n details

# 3. Install
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Run
python -m src.server
```

### Option 3: Docker

```bash
# 1. Clone and configure
git clone https://github.com/monoliet/monoliet-mcp-server.git
cd monoliet-mcp-server
cp .env.example .env
# Edit .env

# 2. Create network
docker network create web

# 3. Start
docker-compose up -d

# 4. View logs
docker-compose logs -f monoliet-mcp
```

## Configuration

Edit `.env`:

```env
N8N_URL=http://localhost:5678
N8N_API_KEY=your-api-key-here
```

### Get n8n API Key

1. Open n8n → **Settings** → **API**
2. Click **Create API Key**
3. Copy key to `.env`

## Claude Desktop Integration

### 1. Install Claude Desktop

Download: https://claude.ai/download

### 2. Configure

**macOS:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

Add:

```json
{
  "mcpServers": {
    "monoliet-n8n": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/full/path/to/monoliet-mcp-server",
      "env": {
        "N8N_URL": "http://localhost:5678",
        "N8N_API_KEY": "your-api-key"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Completely quit and restart Claude Desktop.

## Verify Setup

In Claude Desktop, type:

```
List all my workflows
```

Claude should respond with your n8n workflows!

## Common Commands

Try these in Claude:

- "Show me all active workflows"
- "Create a new workflow called 'Test Workflow'"
- "Search for workflows with 'email' in the name"
- "Check the health of workflow [id]"
- "Execute workflow [id]"
- "Show me the last 10 executions"

## Troubleshooting

### Can't connect to n8n

```bash
# Test n8n connection
curl http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: your-api-key"
```

### Server won't start

```bash
# Check logs
tail -f mcp-server.log

# Or with Docker
docker-compose logs monoliet-mcp
```

### Claude can't find server

1. Restart Claude Desktop completely
2. Check config file syntax (valid JSON)
3. Verify server is running: `ps aux | grep "src.server"`

## Next Steps

- Read full [README.md](README.md) for all features
- Check [SETUP.md](SETUP.md) for VPS deployment
- Explore all 11 MCP tools
- Join discussions on GitHub

## Support

- GitHub Issues: https://github.com/monoliet/monoliet-mcp-server/issues
- Email: support@monoliet.com

---

**Happy automating with Claude!** 🎉
