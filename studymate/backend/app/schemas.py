from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserInDB(UserResponse):
    hashed_password: str


# Auth schemas
class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseSchema):
    username: Optional[str] = None


class LoginRequest(BaseSchema):
    username: str
    password: str


# Document schemas
class DocumentBase(BaseSchema):
    filename: str = Field(..., max_length=255)
    s3_key: str = Field(..., max_length=500)
    status: str = Field(..., max_length=50)


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseSchema):
    filename: Optional[str] = Field(None, max_length=255)
    s3_key: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, max_length=50)


class DocumentResponse(DocumentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


# Chunk schemas
class ChunkBase(BaseSchema):
    document_id: UUID
    chunk_index: int
    start_word: int
    end_word: int
    page_start: int
    page_end: int
    text: str
    embedding_vector: Optional[str] = None


class ChunkCreate(ChunkBase):
    pass


class ChunkUpdate(BaseSchema):
    chunk_index: Optional[int] = None
    start_word: Optional[int] = None
    end_word: Optional[int] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    text: Optional[str] = None
    embedding_vector: Optional[str] = None


class ChunkResponse(ChunkBase):
    id: UUID
    created_at: datetime


# Chat schemas
class ChatBase(BaseSchema):
    title: Optional[str] = Field(None, max_length=255)


class ChatCreate(ChatBase):
    pass


class ChatUpdate(BaseSchema):
    title: Optional[str] = Field(None, max_length=255)


class ChatResponse(ChatBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


# Message schemas
class MessageBase(BaseSchema):
    chat_id: UUID
    role: str = Field(..., max_length=20)
    text: str


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseSchema):
    role: Optional[str] = Field(None, max_length=20)
    text: Optional[str] = None


class MessageResponse(MessageBase):
    id: UUID
    created_at: datetime


# Citation schemas
class CitationBase(BaseSchema):
    message_id: UUID
    document_id: UUID
    chunk_id: UUID
    score: float


class CitationCreate(CitationBase):
    pass


class CitationUpdate(BaseSchema):
    score: Optional[float] = None


class CitationResponse(CitationBase):
    id: UUID
    created_at: datetime


# Pagination schemas
class PaginationParams(BaseSchema):
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class PaginatedResponse(BaseSchema):
    items: List[dict]
    total: int
    limit: int
    offset: int
    pages: int


# Search schemas
class SearchParams(BaseSchema):
    q: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    chat_id: Optional[UUID] = None
