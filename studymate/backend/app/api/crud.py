from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_active_user, get_current_superuser
from app.crud.base import CRUDBase
from app.db.models import Chat, Citation, Chunk, Document, Message, User
from app.db.session import get_db
from app.schemas import (
    ChatCreate, ChatResponse, ChatUpdate,
    CitationCreate, CitationResponse, CitationUpdate,
    ChunkCreate, ChunkResponse, ChunkUpdate,
    DocumentCreate, DocumentResponse, DocumentUpdate,
    MessageCreate, MessageResponse, MessageUpdate,
    PaginatedResponse, PaginationParams, SearchParams,
    UserCreate, UserResponse, UserUpdate
)

router = APIRouter(prefix="/crud", tags=["crud"])

# CRUD instances
user_crud = CRUDBase[User, UserCreate, UserUpdate](User)
document_crud = CRUDBase[Document, DocumentCreate, DocumentUpdate](Document)
chunk_crud = CRUDBase[Chunk, ChunkCreate, ChunkUpdate](Chunk)
chat_crud = CRUDBase[Chat, ChatCreate, ChatUpdate](Chat)
message_crud = CRUDBase[Message, MessageCreate, MessageUpdate](Message)
citation_crud = CRUDBase[Citation, CitationCreate, CitationUpdate](Citation)


# User endpoints
@router.get("/users", response_model=PaginatedResponse)
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    pagination: PaginationParams = Depends(),
    search: SearchParams = Depends(),
) -> Any:
    """Retrieve users with pagination and search."""
    filters = {}
    if search.user_id:
        filters["id"] = search.user_id
    
    total = await user_crud.count(db, filters=filters, search=search.q, search_fields=["username", "email"])
    users = await user_crud.get_multi(
        db, 
        skip=pagination.offset, 
        limit=pagination.limit,
        filters=filters,
        search=search.q,
        search_fields=["username", "email"]
    )
    
    return PaginatedResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    user_in: UserCreate,
) -> Any:
    """Create new user."""
    user = await user_crud.create(db, obj_in=user_in)
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    user_id: str,
) -> Any:
    """Get user by ID."""
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    user_id: str,
    user_in: UserUpdate,
) -> Any:
    """Update user."""
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = await user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    user_id: str,
) -> None:
    """Delete user."""
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_crud.remove(db, id=user_id)
    return None


# Document endpoints
@router.get("/documents", response_model=PaginatedResponse)
async def read_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    search: SearchParams = Depends(),
) -> Any:
    """Retrieve documents with pagination and search."""
    filters = {}
    if search.status:
        filters["status"] = search.status
    
    total = await document_crud.count(db, filters=filters, search=search.q, search_fields=["filename"])
    documents = await document_crud.get_multi(
        db, 
        skip=pagination.offset, 
        limit=pagination.limit,
        filters=filters,
        search=search.q,
        search_fields=["filename"]
    )
    
    return PaginatedResponse(
        items=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    document_in: DocumentCreate,
) -> Any:
    """Create new document."""
    document = await document_crud.create(db, obj_in=document_in)
    return document


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def read_document(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    document_id: str,
) -> Any:
    """Get document by ID."""
    document = await document_crud.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    document_id: str,
    document_in: DocumentUpdate,
) -> Any:
    """Update document."""
    document = await document_crud.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document = await document_crud.update(db, db_obj=document, obj_in=document_in)
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    document_id: str,
) -> None:
    """Delete document."""
    document = await document_crud.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await document_crud.remove(db, id=document_id)
    return None


# Chat endpoints
@router.get("/chats", response_model=PaginatedResponse)
async def read_chats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    search: SearchParams = Depends(),
) -> Any:
    """Retrieve chats for current user with pagination and search."""
    filters = {"user_id": current_user.id}
    
    total = await chat_crud.count(db, filters=filters, search=search.q, search_fields=["title"])
    chats = await chat_crud.get_multi(
        db, 
        skip=pagination.offset, 
        limit=pagination.limit,
        filters=filters,
        search=search.q,
        search_fields=["title"]
    )
    
    return PaginatedResponse(
        items=[ChatResponse.model_validate(chat) for chat in chats],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.post("/chats", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    chat_in: ChatCreate,
) -> Any:
    """Create new chat for current user."""
    chat_data = chat_in.model_dump()
    chat_data["user_id"] = current_user.id
    chat = await chat_crud.create(db, obj_in=ChatCreate(**chat_data))
    return chat


@router.get("/chats/{chat_id}", response_model=ChatResponse)
async def read_chat(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    chat_id: str,
) -> Any:
    """Get chat by ID (must belong to current user)."""
    chat = await chat_crud.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return chat


@router.put("/chats/{chat_id}", response_model=ChatResponse)
async def update_chat(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    chat_id: str,
    chat_in: ChatUpdate,
) -> Any:
    """Update chat (must belong to current user)."""
    chat = await chat_crud.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    chat = await chat_crud.update(db, db_obj=chat, obj_in=chat_in)
    return chat


@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    chat_id: str,
) -> None:
    """Delete chat (must belong to current user)."""
    chat = await chat_crud.get(db, id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await chat_crud.remove(db, id=chat_id)
    return None


# Message endpoints
@router.get("/messages", response_model=PaginatedResponse)
async def read_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    pagination: PaginationParams = Depends(),
    search: SearchParams = Depends(),
) -> Any:
    """Retrieve messages with pagination and search."""
    filters = {}
    if search.chat_id:
        filters["chat_id"] = search.chat_id
    
    total = await message_crud.count(db, filters=filters, search=search.q, search_fields=["text"])
    messages = await message_crud.get_multi(
        db, 
        skip=pagination.offset, 
        limit=pagination.limit,
        filters=filters,
        search=search.q,
        search_fields=["text"]
    )
    
    return PaginatedResponse(
        items=[MessageResponse.model_validate(msg) for msg in messages],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
        pages=(total + pagination.limit - 1) // pagination.limit
    )


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    message_in: MessageCreate,
) -> Any:
    """Create new message."""
    # Verify chat belongs to current user
    chat = await chat_crud.get(db, id=message_in.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    message = await message_crud.create(db, obj_in=message_in)
    return message


@router.get("/messages/{message_id}", response_model=MessageResponse)
async def read_message(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    message_id: str,
) -> Any:
    """Get message by ID."""
    message = await message_crud.get(db, id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify chat belongs to current user
    chat = await chat_crud.get(db, id=message.chat_id)
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return message


@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    message_id: str,
    message_in: MessageUpdate,
) -> Any:
    """Update message."""
    message = await message_crud.get(db, id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify chat belongs to current user
    chat = await chat_crud.get(db, id=message.chat_id)
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    message = await message_crud.update(db, db_obj=message, obj_in=message_in)
    return message


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    message_id: str,
) -> None:
    """Delete message."""
    message = await message_crud.get(db, id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Verify chat belongs to current user
    chat = await chat_crud.get(db, id=message.chat_id)
    if chat.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await message_crud.remove(db, id=message_id)
    return None
