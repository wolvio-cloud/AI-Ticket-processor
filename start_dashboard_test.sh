#!/bin/bash
# ============================================================================
# Dashboard Quick Start Script - Linux/Mac
# ============================================================================
#
# This script helps you test the dashboard integration quickly.
#
# Usage: chmod +x start_dashboard_test.sh && ./start_dashboard_test.sh
# ============================================================================

echo ""
echo "================================================================================"
echo "  AI TICKET PROCESSOR - DASHBOARD TESTING"
echo "================================================================================"
echo ""
echo "This script will help you test the dashboard integration."
echo ""
echo "STEP 1: Starting API Server..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python 3.8+ and try again"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

echo "Python found:"
$PYTHON_CMD --version
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
$PYTHON_CMD -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: FastAPI not found. Installing dependencies..."
    echo ""
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "Dependencies OK"
echo ""
echo "================================================================================"
echo "  STARTING API SERVER"
echo "================================================================================"
echo ""
echo "API Server will start on: http://localhost:8000"
echo "API Documentation: http://localhost:8000/api/docs"
echo ""
echo "Leave this terminal open. The API server must keep running."
echo ""
echo "To test the dashboard, open a NEW terminal and run:"
echo "  cd ai-ticket-dashboard"
echo "  npm install  # first time only"
echo "  npm run dev"
echo "  Open browser: http://localhost:3000"
echo ""
echo "================================================================================"
echo ""

# Start API server
$PYTHON_CMD api_server.py

# If the server exits
echo ""
echo "API Server stopped."
