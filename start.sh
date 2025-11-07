#!/bin/bash

echo "🚀 Starting AI Ticket Processor Backend..."
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env - Please update with your API keys"
    echo ""
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🌐 API Documentation:"
echo "   • Swagger UI: http://localhost:8000/docs"
echo "   • ReDoc: http://localhost:8000/redoc"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
echo "✨ Happy coding!"
