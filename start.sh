#!/bin/bash
# Quick start script for Monoliet MCP Server

set -e

echo "🚀 Starting Monoliet MCP Server for n8n..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  Please edit .env with your n8n configuration:"
    echo "   - N8N_URL=your-n8n-url"
    echo "   - N8N_API_KEY=your-api-key"
    echo ""
    read -p "Press Enter after configuring .env..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Run the server
echo ""
echo "✨ Starting MCP server..."
echo "📊 Logs will appear below. Press Ctrl+C to stop."
echo ""
python -m src.server
