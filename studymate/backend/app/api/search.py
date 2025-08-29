from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.retrieval.embeddings import create_embeddings
from app.retrieval.index import FAISSIndex, VectorSearchService
from app.core.config import settings

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    k: Optional[int] = Field(default=None, ge=1, le=50, description="Number of results")


class SearchHit(BaseModel):
    """Search hit model."""
    chunk_id: str
    document_id: str
    filename: str
    page_start: int
    page_end: int
    text: str
    score: float
    chunk_index: int


class SearchResponse(BaseModel):
    """Search response model."""
    hits: List[SearchHit]
    total_hits: int
    query: str


# Global instances
embeddings = create_embeddings()
faiss_index = FAISSIndex(dimension=embeddings.get_dimension())
search_service = VectorSearchService(faiss_index)


@router.post("/", response_model=SearchResponse)
async def search_chunks(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
) -> SearchResponse:
    """Search for relevant chunks using vector similarity."""
    
    # Validate k parameter
    k = request.k or settings.default_top_k
    k = min(k, settings.max_top_k)
    
    try:
        # Embed the query
        query_embeddings = embeddings.embed_texts([request.query])
        if not query_embeddings:
            raise HTTPException(status_code=500, detail="Failed to embed query")
        
        query_vector = query_embeddings[0]
        
        # Search for similar chunks
        chunk_data = await search_service.search_chunks(query_vector, k, db)
        
        # Convert to response format
        hits = []
        for chunk in chunk_data:
            hit = SearchHit(
                chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                filename=chunk.get("filename", "Unknown"),
                page_start=chunk["page_start"],
                page_end=chunk["page_end"],
                text=chunk["text"],
                score=chunk["score"],
                chunk_index=chunk["chunk_index"]
            )
            hits.append(hit)
        
        return SearchResponse(
            hits=hits,
            total_hits=len(hits),
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/stats")
async def get_search_stats() -> dict:
    """Get search index statistics."""
    try:
        stats = faiss_index.get_stats()
        return {
            "index_stats": stats,
            "embedding_backend": settings.embeddings_backend,
            "embedding_model": settings.embeddings_model,
            "embedding_dimension": embeddings.get_dimension()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
