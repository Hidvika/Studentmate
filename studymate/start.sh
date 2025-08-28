#!/bin/bash

# StudyMate Startup Script
# This script helps you get StudyMate up and running quickly

set -e

echo "🚀 Starting StudyMate..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Navigate to deploy directory
cd deploy

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# StudyMate Environment Configuration

# App
APP_ENV=dev
DEBUG=true

# Database
POSTGRES_URL=postgresql+asyncpg://studymate:studymate@db:5432/studymate

# Redis
REDIS_URL=redis://redis:6379/0

# S3/MinIO
S3_ENDPOINT=http://minio:9000
S3_BUCKET=studymate
S3_ACCESS_KEY=studymate
S3_SECRET_KEY=studymate
S3_REGION=us-east-1

# Embeddings
EMBEDDINGS_BACKEND=sentence-transformers
EMBEDDINGS_MODEL=BAAI/bge-small-en-v1.5

# WatsonX (optional - set if using WatsonX embeddings/LLM)
WATSONX_API_KEY=SET_ME
WATSONX_PROJECT_ID=SET_ME
WATSONX_MODEL_ID=granite-13b-instruct-v2
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Search
DEFAULT_TOP_K=5
MAX_TOP_K=20

# File upload
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=[".pdf"]

# Frontend
NEXT_PUBLIC_API_BASE=http://localhost:8000
EOF
    echo "✅ Created .env file"
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec -T api alembic upgrade head

echo ""
echo "🎉 StudyMate is now running!"
echo ""
echo "📱 Access the application:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • MinIO Console: http://localhost:9001"
echo ""
echo "📋 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Upload some PDF documents"
echo "   3. Start chatting with your documents!"
echo ""
echo "🔧 To stop the application:"
echo "   cd deploy && docker-compose down"
echo ""
echo "📊 To view logs:"
echo "   cd deploy && docker-compose logs -f [service]"
echo ""
