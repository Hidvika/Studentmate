# StudyMate - AI-Powered Document Analysis & Chat

StudyMate is a production-ready RAG (Retrieval-Augmented Generation) web application that allows users to upload PDF documents and chat with an AI assistant that can answer questions based on the uploaded content.

## 🚀 Features

- **Document Upload**: Drag-and-drop PDF upload with real-time processing status
- **RAG Chat**: AI-powered chat interface with streaming responses
- **Citation Support**: Every AI response includes source citations with page references
- **Vector Search**: Fast semantic search using FAISS vector database
- **Multiple Embedding Backends**: Support for Sentence-Transformers and WatsonX embeddings
- **Modern UI**: Beautiful, responsive interface built with Next.js 14 and Tailwind CSS

## 🏗️ Architecture

StudyMate is built as a 3-service system:

1. **Backend API** (FastAPI + Python 3.11)
   - Document ingestion pipeline (PDF → text → chunks → embeddings)
   - Vector search with FAISS
   - RAG chat with WatsonX LLM
   - PostgreSQL for metadata storage
   - MinIO/S3 for file storage

2. **Frontend UI** (Next.js 14 + TypeScript)
   - Modern, responsive interface
   - Real-time file upload with progress tracking
   - Streaming chat interface
   - Source citation display

3. **Infrastructure** (Docker + docker-compose)
   - PostgreSQL database
   - Redis for caching
   - MinIO for object storage
   - All services containerized

## 🛠️ Tech Stack

### Backend
- **Python 3.11** with FastAPI
- **SQLAlchemy** with async PostgreSQL
- **FAISS** for vector similarity search
- **Sentence-Transformers** for local embeddings
- **IBM WatsonX.ai** for LLM and cloud embeddings
- **PyMuPDF** for PDF text extraction
- **MinIO** for S3-compatible storage

### Frontend
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Radix UI** for accessible components
- **React Dropzone** for file uploads
- **Server-Sent Events** for streaming

### Infrastructure
- **Docker** and **docker-compose**
- **PostgreSQL 16** for metadata
- **Redis 7** for caching
- **MinIO** for object storage

## 🚀 Quick Start

### Prerequisites
- Docker and docker-compose
- Node.js 18+ (for local development)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd studymate
```

### 2. Start the Application
```bash
# Start all services
cd deploy
docker-compose up -d

# The application will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - MinIO Console: http://localhost:9001
```

### 3. Initialize the Database
```bash
# Run database migrations
docker-compose exec api alembic upgrade head
```

### 4. Upload Documents and Chat
1. Open http://localhost:3000
2. Upload PDF documents using the drag-and-drop interface
3. Wait for processing to complete
4. Switch to the Chat tab and start asking questions!

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `deploy` directory:

```env
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

# Embeddings
EMBEDDINGS_BACKEND=sentence-transformers
EMBEDDINGS_MODEL=BAAI/bge-small-en-v1.5

# WatsonX (optional)
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_MODEL_ID=granite-13b-instruct-v2

# Frontend
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### Embedding Backends

StudyMate supports two embedding backends:

1. **Sentence-Transformers** (default, local)
   - Uses BAAI/bge-small-en-v1.5 model
   - Runs locally, no API keys required
   - Good for development and testing

2. **WatsonX** (cloud)
   - Requires IBM WatsonX.ai account
   - Set `EMBEDDINGS_BACKEND=watsonx` and provide API credentials
   - Better performance for production

## 📁 Project Structure

```
studymate/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── db/             # Database models
│   │   ├── ingestion/      # PDF processing
│   │   ├── retrieval/      # Vector search
│   │   ├── llm/            # WatsonX client
│   │   └── s3/             # File storage
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   ├── lib/               # Utilities and API client
│   └── Dockerfile
├── deploy/                # Docker deployment
│   └── docker-compose.yml
└── README.md
```

## 🔌 API Endpoints

### Document Management
- `POST /ingest` - Upload PDF documents
- `GET /ingest/{document_id}/status` - Get processing status
- `DELETE /ingest/{document_id}` - Delete document

### Search
- `POST /search` - Vector search for relevant chunks
- `GET /search/stats` - Get search statistics

### Chat
- `POST /chat` - Synchronous chat with RAG
- `POST /chat/stream` - Streaming chat with SSE
- `GET /chat/{chat_id}` - Get chat history

## 🧪 Development

### Backend Development
```bash
cd backend

# Install dependencies
pip install -e .

# Run tests
pytest tests/ -v

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests (when implemented)
cd frontend
npm test
```

## 🐳 Docker Development

### Build and Run
```bash
# Build all services
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Database Management
```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Reset database
docker-compose down -v
docker-compose up -d db
docker-compose exec api alembic upgrade head
```

## 📊 Performance

- **Search Speed**: <300ms for 50k chunks on development hardware
- **Upload Processing**: Real-time status updates with background processing
- **Chat Response**: Streaming responses with citations
- **Scalability**: Designed for horizontal scaling with proper indexing

## 🔒 Security

- Input validation and sanitization
- File type and size restrictions
- SQL injection protection via SQLAlchemy
- CORS configuration
- Environment-based configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure PostgreSQL is running: `docker-compose ps db`
   - Check database logs: `docker-compose logs db`

2. **File Upload Failures**
   - Verify MinIO is running: `docker-compose ps minio`
   - Check MinIO console at http://localhost:9001

3. **Embedding Model Loading**
   - First run may take time to download models
   - Check API logs: `docker-compose logs api`

4. **Frontend Not Loading**
   - Ensure backend API is running: `docker-compose ps api`
   - Check frontend logs: `docker-compose logs ui`

### Getting Help

- Check the logs: `docker-compose logs -f [service]`
- Verify environment variables are set correctly
- Ensure all services are running: `docker-compose ps`
- Check the API documentation at http://localhost:8000/docs

## 🎯 Roadmap

- [ ] User authentication and authorization
- [ ] Document versioning and history
- [ ] Advanced search filters
- [ ] Export chat conversations
- [ ] Mobile-responsive improvements
- [ ] Performance optimizations
- [ ] Additional file format support
- [ ] Multi-language support
