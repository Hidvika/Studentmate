@echo off
echo Setting up StudyMate for local development...

echo.
echo Step 1: Install PostgreSQL
echo - Download from: https://www.postgresql.org/download/windows/
echo - Install with password: studymate
echo - Default port: 5432

echo.
echo Step 2: Install Redis
echo - Download from: https://github.com/microsoftarchive/redis/releases
echo - Install with default settings

echo.
echo Step 3: Install MinIO
echo - Download from: https://min.io/download
echo - Extract to C:\minio
echo - Run: C:\minio\minio.exe server C:\minio\data --console-address ":9001"

echo.
echo Step 4: Create database
echo - Open pgAdmin or psql
echo - Create database: studymate
echo - Create user: studymate with password: studymate

echo.
echo Step 5: Install Python dependencies
cd backend
pip install -e .

echo.
echo Step 6: Install Node.js dependencies
cd ..\frontend
npm install

echo.
echo Step 7: Start services
echo - Start PostgreSQL service
echo - Start Redis service
echo - Start MinIO: C:\minio\minio.exe server C:\minio\data --console-address ":9001"

echo.
echo Step 8: Run migrations
cd ..\backend
alembic upgrade head

echo.
echo Step 9: Start the application
echo - Backend: cd backend && uvicorn app.main:app --reload --port 8000
echo - Frontend: cd frontend && npm run dev

echo.
echo StudyMate will be available at:
echo - Frontend: http://localhost:3000
echo - Backend: http://localhost:8000
echo - MinIO Console: http://localhost:9001

pause
