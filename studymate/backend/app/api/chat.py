import json
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sse_starlette.sse import EventSourceResponse

from app.db.session import get_db
from app.db.models import Chat, Message, Citation, Document, Chunk
from app.retrieval.embeddings import create_embeddings
from app.retrieval.index import FAISSIndex, VectorSearchService
from app.llm.watsonx_client import get_watsonx_client
from app.llm.prompts import build_rag_prompt
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., min_length=1, max_length=2000, description="User's question")
    chat_id: Optional[str] = Field(None, description="Existing chat ID (optional)")
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="Number of chunks to retrieve")


class CitationResponse(BaseModel):
    """Citation response model."""
    document_id: str
    chunk_id: str
    filename: str
    page_start: int
    page_end: int
    score: float


class ChatResponse(BaseModel):
    """Chat response model."""
    chat_id: str
    message_id: str
    answer: str
    citations: List[CitationResponse]


# Global instances
embeddings = create_embeddings()
faiss_index = FAISSIndex(dimension=embeddings.get_dimension())
search_service = VectorSearchService(faiss_index)


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """Chat endpoint with RAG-based responses."""
    
    # Validate top_k
    top_k = request.top_k or settings.default_top_k
    top_k = min(top_k, settings.max_top_k)
    
    try:
        # Get or create chat
        chat_id = request.chat_id
        if chat_id:
            stmt = select(Chat).where(Chat.id == UUID(chat_id))
            result = await db.execute(stmt)
            chat = result.scalar_one_or_none()
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
        else:
            chat = Chat(title=request.query[:50] + "..." if len(request.query) > 50 else request.query)
            db.add(chat)
            await db.flush()
        
        # Store user message
        user_message = Message(
            chat_id=chat.id,
            role="user",
            text=request.query
        )
        db.add(user_message)
        await db.flush()
        
        # Embed query and search for relevant chunks
        query_embeddings = embeddings.embed_texts([request.query])
        if not query_embeddings:
            raise HTTPException(status_code=500, detail="Failed to embed query")
        
        query_vector = query_embeddings[0]
        chunk_data = await search_service.search_chunks(query_vector, top_k, db)
        
        # Build RAG prompt
        prompt, used_chunks = build_rag_prompt(chunk_data, request.query)
        
        # Generate response
        watsonx_client = get_watsonx_client()
        result = watsonx_client.generate_from_prompt(
            prompt_text=prompt,
            max_new_tokens=500,
            temperature=0.3
        )
        
        answer = result.get("answer", "I'm sorry, I couldn't generate a response.")
        
        # Store assistant message
        assistant_message = Message(
            chat_id=chat.id,
            role="assistant",
            text=answer
        )
        db.add(assistant_message)
        await db.flush()
        
        # Store citations
        citations = []
        for chunk in used_chunks:
            citation = Citation(
                message_id=assistant_message.id,
                document_id=UUID(chunk["document_id"]),
                chunk_id=UUID(chunk["chunk_id"]),
                score=chunk["score"]
            )
            db.add(citation)
            citations.append(citation)
        
        await db.commit()
        
        # Build response
        citation_responses = []
        for citation in citations:
            # Get document filename
            stmt = select(Document).where(Document.id == citation.document_id)
            result = await db.execute(stmt)
            document = result.scalar_one_or_none()
            
            # Get chunk page info
            stmt = select(Chunk).where(Chunk.id == citation.chunk_id)
            result = await db.execute(stmt)
            chunk = result.scalar_one_or_none()
            
            citation_responses.append(CitationResponse(
                document_id=str(citation.document_id),
                chunk_id=str(citation.chunk_id),
                filename=document.filename if document else "Unknown",
                page_start=chunk.page_start if chunk else 1,
                page_end=chunk.page_end if chunk else 1,
                score=citation.score
            ))
        
        return ChatResponse(
            chat_id=str(chat.id),
            message_id=str(assistant_message.id),
            answer=answer,
            citations=citation_responses
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Streaming chat endpoint with SSE."""
    
    # Validate top_k
    top_k = request.top_k or settings.default_top_k
    top_k = min(top_k, settings.max_top_k)
    
    async def generate_stream():
        try:
            # Get or create chat
            chat_id = request.chat_id
            if chat_id:
                stmt = select(Chat).where(Chat.id == UUID(chat_id))
                result = await db.execute(stmt)
                chat = result.scalar_one_or_none()
                if not chat:
                    yield {"event": "error", "data": json.dumps({"error": "Chat not found"})}
                    return
            else:
                chat = Chat(title=request.query[:50] + "..." if len(request.query) > 50 else request.query)
                db.add(chat)
                await db.flush()
            
            # Store user message
            user_message = Message(
                chat_id=chat.id,
                role="user",
                text=request.query
            )
            db.add(user_message)
            await db.flush()
            
            # Embed query and search for relevant chunks
            query_embeddings = embeddings.embed_texts([request.query])
            if not query_embeddings:
                yield {"event": "error", "data": json.dumps({"error": "Failed to embed query"})}
                return
            
            query_vector = query_embeddings[0]
            chunk_data = await search_service.search_chunks(query_vector, top_k, db)
            
            # Build RAG prompt
            prompt, used_chunks = build_rag_prompt(chunk_data, request.query)
            
            # Stream response
            full_answer = ""
            watsonx_client = get_watsonx_client()
            async for token in watsonx_client.generate_stream(
                prompt_text=prompt,
                max_new_tokens=500,
                temperature=0.3
            ):
                full_answer += token
                yield {
                    "event": "token",
                    "data": json.dumps({"delta": token, "done": False})
                }
            
            # Store assistant message
            assistant_message = Message(
                chat_id=chat.id,
                role="assistant",
                text=full_answer
            )
            db.add(assistant_message)
            await db.flush()
            
            # Store citations
            citations = []
            for chunk in used_chunks:
                citation = Citation(
                    message_id=assistant_message.id,
                    document_id=UUID(chunk["document_id"]),
                    chunk_id=UUID(chunk["chunk_id"]),
                    score=chunk["score"]
                )
                db.add(citation)
                citations.append(citation)
            
            await db.commit()
            
            # Send final response with citations
            citation_data = []
            for citation in citations:
                # Get document filename
                stmt = select(Document).where(Document.id == citation.document_id)
                result = await db.execute(stmt)
                document = result.scalar_one_or_none()
                
                # Get chunk page info
                stmt = select(Chunk).where(Chunk.id == citation.chunk_id)
                result = await db.execute(stmt)
                chunk = result.scalar_one_or_none()
                
                citation_data.append({
                    "document_id": str(citation.document_id),
                    "chunk_id": str(citation.chunk_id),
                    "filename": document.filename if document else "Unknown",
                    "page_start": chunk.page_start if chunk else 1,
                    "page_end": chunk.page_end if chunk else 1,
                    "score": citation.score
                })
            
            yield {
                "event": "done",
                "data": json.dumps({
                    "done": True,
                    "chat_id": str(chat.id),
                    "message_id": str(assistant_message.id),
                    "citations": citation_data
                })
            }
            
        except Exception as e:
            await db.rollback()
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
    
    return EventSourceResponse(generate_stream())


@router.get("/{chat_id}")
async def get_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history."""
    try:
        stmt = select(Chat).where(Chat.id == UUID(chat_id))
        result = await db.execute(stmt)
        chat = result.scalar_one_or_none()
        
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Get messages
        stmt = select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at)
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        return {
            "chat_id": str(chat.id),
            "title": chat.title,
            "created_at": chat.created_at.isoformat(),
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "text": msg.text,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat: {str(e)}")
