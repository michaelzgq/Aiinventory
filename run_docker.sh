#!/bin/bash

# Inventory AI - Docker Deployment Script

echo "🐳 Starting Inventory AI with Docker..."

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found!"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "✏️ Please edit .env file with your configuration"
    echo "🔑 Don't forget to change the API_KEY!"
fi

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up -d --build

# Wait for container to be ready
echo "⏳ Waiting for container to start..."
sleep 10

# Check container status
echo "📊 Container status:"
docker-compose ps

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=20 inventory-ai

# Health check
echo "🔍 Health check:"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "Health check failed"

echo ""
echo "🌟 Inventory AI is running!"
echo "📱 Web Interface: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f inventory-ai"
echo "  Stop: docker-compose down"
echo "  Restart: docker-compose restart inventory-ai"
echo "  Shell access: docker-compose exec inventory-ai bash"