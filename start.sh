#!/bin/bash

# Quick Start Script for Agentic CX PoC
# This script sets up and runs the agent

echo "=================================="
echo "Agentic AI CX PoC - Quick Start"
echo "=================================="
echo ""

# Check Python
echo "1. Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi
python_version=$(python3 --version)
echo "✅ Found: $python_version"
echo ""

# Check pip
echo "2. Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi
echo "✅ pip3 is available"
echo ""

# Install dependencies
echo "3. Installing dependencies..."
pip3 install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Run the API server
echo "4. Starting API server..."
echo "   Server will run at: http://localhost:8000"
echo "   Documentation at:    http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo ""

python3 main.py
