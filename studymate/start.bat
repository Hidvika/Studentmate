@echo off
REM StudyMate Startup Script for Windows
REM This script helps you get StudyMate up and running quickly

echo 🚀 Starting StudyMate...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose is not installed. Please install it and try again.
    pause
    exit /b 1
)

REM Navigate to deploy directory
cd deploy

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # StudyMate Environment Configuration
        echo.
        echo # App
        echo APP_ENV=dev
        echo DEBUG=true
        echo.
        echo # Database
        echo POSTGRES_URL=postgresql+asyncpg://studymate:studymate@db:5432/studymate
        echo.
        echo # Redis
        echo REDIS_URL=redis://redis:6379/0
        echo.
        echo # S3/MinIO
        echo S3_ENDPOINT=http://minio:9000
        echo S3_BUCKET=studymate
        echo S3_ACCESS_KEY=studymate
        echo S3_SECRET_KEY=studymate
        echo S3_REGION=us-east-1
        echo.
        echo # Embeddings
        echo EMBEDDINGS_BACKEND=sentence-transformers
        echo EMBEDDINGS_MODEL=BAAI/bge-small-en-v1.5
        echo.
        echo # WatsonX (optional - set if using WatsonX embeddings/LLM)
        echo WATSONX_API_KEY=SET_ME
        echo WATSONX_PROJECT_ID=SET_ME
        echo WATSONX_MODEL_ID=granite-13b-instruct-v2
        echo WATSONX_URL=https://us-south.ml.cloud.ibm.com
        echo.
        echo # Chunking
        echo CHUNK_SIZE=500
        echo CHUNK_OVERLAP=100
        echo.
        echo # Search
        echo DEFAULT_TOP_K=5
        echo MAX_TOP_K=20
        echo.
        echo # File upload
        echo MAX_FILE_SIZE_MB=50
        echo ALLOWED_EXTENSIONS=[".pdf"]
        echo.
        echo # Frontend
        echo NEXT_PUBLIC_API_BASE=http://localhost:8000
    ) > .env
    echo ✅ Created .env file
)

REM Stop any existing containers
echo 🛑 Stopping any existing containers...
docker-compose down

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up -d --build

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM Run database migrations
echo 🗄️ Running database migrations...
docker-compose exec -T api alembic upgrade head

echo.
echo 🎉 StudyMate is now running!
echo.
echo 📱 Access the application:
echo    • Frontend: http://localhost:3000
echo    • Backend API: http://localhost:8000
echo    • API Documentation: http://localhost:8000/docs
echo    • MinIO Console: http://localhost:9001
echo.
echo 📋 Next steps:
echo    1. Open http://localhost:3000 in your browser
echo    2. Upload some PDF documents
echo    3. Start chatting with your documents!
echo.
echo 🔧 To stop the application:
echo    cd deploy ^&^& docker-compose down
echo.
echo 📊 To view logs:
echo    cd deploy ^&^& docker-compose logs -f [service]
echo.
pause
