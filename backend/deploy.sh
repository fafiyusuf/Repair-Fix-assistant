#!/bin/bash

# IFix-AI Backend - Quick Deployment Script
# This script provides a simple way to deploy the backend with Docker

set -e

echo "🚀 IFix-AI Backend Deployment Script"
echo "===================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your environment variables."
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your configuration."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed!"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Warning: docker-compose not found. Will use docker compose instead."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Menu
echo "Select deployment option:"
echo "1) Build and run with Docker Compose (Recommended)"
echo "2) Build and run with Docker CLI"
echo "3) Development mode with hot reload"
echo "4) Stop and remove containers"
echo "5) View logs"
echo "6) Check health status"
echo "0) Exit"
echo ""
read -p "Enter your choice [0-6]: " choice

case $choice in
    1)
        echo ""
        echo "📦 Building and starting with Docker Compose..."
        $DOCKER_COMPOSE up -d --build
        echo ""
        echo "✅ Backend is running!"
        echo "🔗 API: http://localhost:8000"
        echo "📖 API Docs: http://localhost:8000/docs"
        echo "❤️  Health: http://localhost:8000/health"
        echo ""
        echo "View logs with: $DOCKER_COMPOSE logs -f backend"
        ;;
    2)
        echo ""
        echo "📦 Building Docker image..."
        docker build -t ifix-ai-backend:latest .
        echo ""
        echo "🚀 Starting container..."
        docker run -d \
            --name ifix-ai-backend \
            -p 8000:8000 \
            --env-file .env \
            --restart unless-stopped \
            ifix-ai-backend:latest
        echo ""
        echo "✅ Backend is running!"
        echo "🔗 API: http://localhost:8000"
        echo "📖 API Docs: http://localhost:8000/docs"
        echo "❤️  Health: http://localhost:8000/health"
        echo ""
        echo "View logs with: docker logs -f ifix-ai-backend"
        ;;
    3)
        echo ""
        echo "🔧 Starting in development mode..."
        $DOCKER_COMPOSE up backend-dev
        ;;
    4)
        echo ""
        echo "🛑 Stopping and removing containers..."
        $DOCKER_COMPOSE down
        docker stop ifix-ai-backend 2>/dev/null || true
        docker rm ifix-ai-backend 2>/dev/null || true
        echo "✅ Containers stopped and removed"
        ;;
    5)
        echo ""
        echo "📋 Viewing logs (Ctrl+C to exit)..."
        if docker ps | grep -q ifix-ai-backend; then
            docker logs -f ifix-ai-backend
        else
            $DOCKER_COMPOSE logs -f backend
        fi
        ;;
    6)
        echo ""
        echo "🏥 Checking health status..."
        if curl -f http://localhost:8000/health 2>/dev/null; then
            echo ""
            echo "✅ Backend is healthy!"
        else
            echo ""
            echo "❌ Backend is not responding or unhealthy"
            echo "Check logs for more information"
        fi
        ;;
    0)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
