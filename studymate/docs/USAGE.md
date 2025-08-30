# StudyMate API Usage Guide

This document provides comprehensive examples of how to use the StudyMate API endpoints for authentication, CRUD operations, and document management.

## Table of Contents

- [Authentication](#authentication)
- [CRUD Operations](#crud-operations)
- [Document Management](#document-management)
- [Chat Operations](#chat-operations)
- [Error Handling](#error-handling)
- [Frontend Integration](#frontend-integration)

## Authentication

### User Registration

**Endpoint:** `POST /auth/register`

**Request:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-08-29T17:30:00",
  "updated_at": "2025-08-29T17:30:00"
}
```

**JavaScript/Axios:**
```javascript
const response = await axios.post('http://localhost:8000/auth/register', {
  username: 'john_doe',
  email: 'john@example.com',
  password: 'securepassword123'
});
console.log(response.data);
```

### User Login

**Endpoint:** `POST /auth/login-json`

**Request:**
```bash
curl -X POST "http://localhost:8000/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**JavaScript/Axios:**
```javascript
const response = await axios.post('http://localhost:8000/auth/login-json', {
  username: 'john_doe',
  password: 'securepassword123'
});

// Store the token
localStorage.setItem('auth_token', response.data.access_token);
```

### Get Current User

**Endpoint:** `GET /auth/me`

**Request:**
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-08-29T17:30:00",
  "updated_at": "2025-08-29T17:30:00"
}
```

**JavaScript/Axios:**
```javascript
const token = localStorage.getItem('auth_token');
const response = await axios.get('http://localhost:8000/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
console.log(response.data);
```

## CRUD Operations

### Documents

#### List Documents

**Endpoint:** `GET /crud/documents`

**Query Parameters:**
- `limit`: Number of items per page (default: 100, max: 1000)
- `offset`: Number of items to skip (default: 0)
- `q`: Search query for filename
- `status`: Filter by document status

**Request:**
```bash
curl -X GET "http://localhost:8000/crud/documents?limit=10&offset=0&q=research&status=ready" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "filename": "research_paper.pdf",
      "s3_key": "uploads/research_paper.pdf",
      "status": "ready",
      "created_at": "2025-08-29T17:30:00",
      "updated_at": "2025-08-29T17:30:00"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0,
  "pages": 1
}
```

**JavaScript/Axios:**
```javascript
const response = await axios.get('http://localhost:8000/crud/documents', {
  params: {
    limit: 10,
    offset: 0,
    q: 'research',
    status: 'ready'
  },
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
console.log(response.data);
```

#### Create Document

**Endpoint:** `POST /crud/documents`

**Request:**
```bash
curl -X POST "http://localhost:8000/crud/documents" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "new_document.pdf",
    "s3_key": "uploads/new_document.pdf",
    "status": "processing"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "filename": "new_document.pdf",
  "s3_key": "uploads/new_document.pdf",
  "status": "processing",
  "created_at": "2025-08-29T17:30:00",
  "updated_at": "2025-08-29T17:30:00"
}
```

**JavaScript/Axios:**
```javascript
const response = await axios.post('http://localhost:8000/crud/documents', {
  filename: 'new_document.pdf',
  s3_key: 'uploads/new_document.pdf',
  status: 'processing'
}, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
console.log(response.data);
```

#### Get Document by ID

**Endpoint:** `GET /crud/documents/{document_id}`

**Request:**
```bash
curl -X GET "http://localhost:8000/crud/documents/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "filename": "research_paper.pdf",
  "s3_key": "uploads/research_paper.pdf",
  "status": "ready",
  "created_at": "2025-08-29T17:30:00",
  "updated_at": "2025-08-29T17:30:00"
}
```

#### Update Document

**Endpoint:** `PUT /crud/documents/{document_id}`

**Request:**
```bash
curl -X PUT "http://localhost:8000/crud/documents/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ready"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "filename": "research_paper.pdf",
  "s3_key": "uploads/research_paper.pdf",
  "status": "ready",
  "created_at": "2025-08-29T17:30:00",
  "updated_at": "2025-08-29T17:30:00"
}
```

#### Delete Document

**Endpoint:** `DELETE /crud/documents/{document_id}`

**Request:**
```bash
curl -X DELETE "http://localhost:8000/crud/documents/550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:** `204 No Content`

### Chats

#### List User Chats

**Endpoint:** `GET /crud/chats`

**Request:**
```bash
curl -X GET "http://localhost:8000/crud/chats?limit=10&offset=0" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "title": "Research Discussion",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-08-29T17:30:00",
      "updated_at": "2025-08-29T17:30:00"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0,
  "pages": 1
}
```

#### Create Chat

**Endpoint:** `POST /crud/chats`

**Request:**
```bash
curl -X POST "http://localhost:8000/crud/chats" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Discussion"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "title": "New Discussion",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-08-29T17:30:00",
  "updated_at": "2025-08-29T17:30:00"
}
```

### Messages

#### List Messages

**Endpoint:** `GET /crud/messages`

**Query Parameters:**
- `chat_id`: Filter messages by chat ID
- `limit`: Number of items per page
- `offset`: Number of items to skip
- `q`: Search query for message text

**Request:**
```bash
curl -X GET "http://localhost:8000/crud/messages?chat_id=550e8400-e29b-41d4-a716-446655440003&limit=50" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Create Message

**Endpoint:** `POST /crud/messages`

**Request:**
```bash
curl -X POST "http://localhost:8000/crud/messages" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "550e8400-e29b-41d4-a716-446655440003",
    "role": "user",
    "text": "What is this document about?"
  }'
```

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Example Error Responses

**Authentication Error:**
```json
{
  "detail": "Could not validate credentials"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Permission Error:**
```json
{
  "detail": "Not enough permissions"
}
```

## Frontend Integration

### Setting up Axios with Authentication

```javascript
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### React Hook for API Calls

```javascript
import { useState, useEffect } from 'react';
import api from './api';

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await api.get('/crud/documents');
      setDocuments(response.data.items);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createDocument = async (documentData) => {
    try {
      const response = await api.post('/crud/documents', documentData);
      setDocuments(prev => [...prev, response.data]);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return {
    documents,
    loading,
    error,
    fetchDocuments,
    createDocument,
  };
}
```

### Form Handling with React Hook Form

```javascript
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';

export function LoginForm() {
  const { login } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    try {
      await login(data.username, data.password);
      // Redirect to dashboard
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('username', { required: 'Username is required' })}
        placeholder="Username"
      />
      {errors.username && <span>{errors.username.message}</span>}
      
      <input
        type="password"
        {...register('password', { required: 'Password is required' })}
        placeholder="Password"
      />
      {errors.password && <span>{errors.password.message}</span>}
      
      <button type="submit">Login</button>
    </form>
  );
}
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-backend

# Run specific test file
docker compose exec api pytest tests/test_crud_api.py -v

# Run specific test class
docker compose exec api pytest tests/test_crud_api.py::TestAuthentication -v
```

### Test Examples

The test suite includes comprehensive tests for:
- User authentication (register, login, token validation)
- Document CRUD operations
- Chat management
- User permissions and access control
- Error handling and validation

## Security Considerations

1. **JWT Tokens**: Store tokens securely and implement proper expiration
2. **Password Hashing**: Passwords are hashed using bcrypt
3. **Input Validation**: All inputs are validated using Pydantic schemas
4. **CORS**: Configure CORS properly for production
5. **Rate Limiting**: Consider implementing rate limiting for production
6. **HTTPS**: Use HTTPS in production environments

## Production Deployment

1. **Environment Variables**: Set proper JWT secrets and database credentials
2. **Database**: Use production-grade PostgreSQL with proper backups
3. **Monitoring**: Implement logging and monitoring
4. **Security**: Regular security audits and updates
5. **Scaling**: Consider horizontal scaling for high-traffic applications
