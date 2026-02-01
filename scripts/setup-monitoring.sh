#!/bin/bash
set -e

echo "📊 eidosSec - CI/CD Monitoring Setup"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Create monitoring directory
echo "📁 Creating monitoring directory..."
mkdir -p monitoring/data

# Start monitoring service
echo "🚀 Starting monitoring API..."
cd monitoring
docker-compose -f docker-compose.monitor.yml up -d --build

# Wait for service to be ready
echo "⏳ Waiting for service to start..."
sleep 5

# Check if service is running
if curl -f http://localhost:9000/health &> /dev/null; then
    echo "✅ Monitoring API is running!"
    echo ""
    echo "📊 Status API endpoints:"
    echo "  - Current status: http://localhost:9000/api/status"
    echo "  - Recent builds: http://localhost:9000/api/builds"
    echo "  - Health check: http://localhost:9000/health"
    echo ""
    echo "🤖 AI Agent Usage:"
    echo "  curl http://localhost:9000/api/status"
else
    echo "❌ Failed to start monitoring API"
    docker-compose -f docker-compose.monitor.yml logs
    exit 1
fi
