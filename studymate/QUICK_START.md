# StudyMate Quick Start Guide

## Option 1: Install Docker (Recommended)

1. **Install Docker Desktop for Windows:**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and restart your computer
   - Start Docker Desktop

2. **Run the project:**
   ```bash
   .\start.bat
   ```

## Option 2: Manual Setup (Current Status)

### What's Already Working ✅
- ✅ Python backend code is complete and imports successfully
- ✅ Frontend dependencies are installed
- ✅ All core functionality is implemented

### What You Need to Install

#### 1. PostgreSQL Database
- Download from: https://www.postgresql.org/download/windows/
- Install with password: `studymate`
- Default port: `5432`
- Create database: `studymate`

#### 2. Redis (Optional - for caching)
- Download from: https://github.com/microsoftarchive/redis/releases
- Install with default settings

#### 3. MinIO (for file storage)
- Download from: https://min.io/download
- Extract to `C:\minio`
- Run: `C:\minio\minio.exe server C:\minio\data --console-address ":9001"`

### Quick Test (Backend Only)

You can test the backend API right now:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Then visit: http://localhost:8000/docs

### Quick Test (Frontend Only)

```bash
cd frontend
npm run dev
```

Then visit: http://localhost:3000

## Current Status

The StudyMate project is **fully implemented** with:

✅ **Complete Backend** (FastAPI with RAG functionality)
✅ **Complete Frontend** (Next.js 14 with modern UI)
✅ **Database Models** (PostgreSQL with Alembic migrations)
✅ **Vector Search** (FAISS with sentence-transformers)
✅ **File Processing** (PDF extraction, chunking, embeddings)
✅ **Chat Interface** (Streaming responses with citations)
✅ **Docker Configuration** (Multi-service setup)

## Next Steps

1. **Install Docker Desktop** (easiest option)
2. **Or install PostgreSQL, Redis, and MinIO** manually
3. **Run the application** using the provided scripts

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
