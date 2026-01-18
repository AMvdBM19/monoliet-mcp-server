@echo off
REM Quick start script for Monoliet MCP Server (Windows)

echo Starting Monoliet MCP Server for n8n...
echo.

REM Check if .env exists
if not exist .env (
    echo .env file not found!
    echo Creating from template...
    copy .env.example .env
    echo Created .env file
    echo.
    echo Please edit .env with your n8n configuration:
    echo    - N8N_URL=your-n8n-url
    echo    - N8N_API_KEY=your-api-key
    echo.
    pause
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo Dependencies installed

REM Run the server
echo.
echo Starting MCP server...
echo Logs will appear below. Press Ctrl+C to stop.
echo.
python -m src.server

pause
