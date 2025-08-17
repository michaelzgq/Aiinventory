#!/bin/bash

# Inventory AI - Local Development Startup Script

echo "🚀 Starting Inventory AI..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "✏️ Please edit .env file with your configuration"
fi

# Create storage directories
echo "📁 Creating storage directories..."
mkdir -p storage/{photos,reports,temp}

# Check if sample data should be loaded
read -p "📊 Load sample data? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📋 Sample data will be available at http://localhost:8000/api/dev/sample-data"
fi

echo "🌟 Starting development server..."
echo "📱 Web Interface: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000