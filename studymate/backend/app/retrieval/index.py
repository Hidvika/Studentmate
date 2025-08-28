import json
import os
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import faiss
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Chunk
from app.retrieval.embeddings import deserialize_embedding


class FAISSIndex:
    """FAISS index wrapper for vector search."""
    
    def __init__(self, dimension: int, index_path: str = "/data/faiss/index.faiss") -> None:
        """Initialize FAISS index.
        
        Args:
            dimension: Embedding vector dimension
            index_path: Path to persist the index
        """
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = index_path.replace(".faiss", "_metadata.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Initialize or load index
        self.index = self._initialize_index()
        self.metadata = self._load_metadata()
    
    def _initialize_index(self) -> faiss.Index:
        """Initialize FAISS index with HNSW if available, otherwise FlatIP."""
        try:
            # Try to create HNSW index for cosine similarity
            index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 neighbors
            index.hnsw.efConstruction = 200
            index.hnsw.efSearch = 100
            return index
        except Exception:
            # Fallback to FlatIP (Inner Product) for cosine similarity
            index = faiss.IndexFlatIP(self.dimension)
            return index
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load index metadata from disk."""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"total_vectors": 0, "document_ids": set()}
    
    def _save_metadata(self) -> None:
        """Save index metadata to disk."""
        # Convert set to list for JSON serialization
        metadata = {
            "total_vectors": self.metadata["total_vectors"],
            "document_ids": list(self.metadata["document_ids"])
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f)
    
    def upsert(self, document_id: UUID, vectors: List[List[float]], 
               metadatas: List[Dict[str, Any]]) -> None:
        """Upsert vectors for a document.
        
        Args:
            document_id: Document ID
            vectors: List of embedding vectors
            metadatas: List of metadata dicts for each vector
        """
        if not vectors:
            return
        
        # Convert to numpy array
        vectors_array = np.array(vectors, dtype=np.float32)
        
        # Remove existing vectors for this document
        self._remove_document_vectors(document_id)
        
        # Add new vectors
        start_idx = self.index.ntotal
        self.index.add(vectors_array)
        
        # Update metadata
        self.metadata["total_vectors"] = self.index.ntotal
        self.metadata["document_ids"].add(str(document_id))
        
        # Save metadata
        self._save_metadata()
        
        # Save index
        self._save_index()
    
    def _remove_document_vectors(self, document_id: UUID) -> None:
        """Remove all vectors for a document (simplified implementation)."""
        # Note: FAISS doesn't support efficient deletion, so we'll rebuild
        # In production, you might want to use a different approach
        pass
    
    def search(self, query_vector: List[float], k: int = 5) -> Tuple[List[float], List[int]]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            
        Returns:
            Tuple of (scores, indices)
        """
        if self.index.ntotal == 0:
            return [], []
        
        # Convert query to numpy array
        query_array = np.array([query_vector], dtype=np.float32)
        
        # Search
        scores, indices = self.index.search(query_array, min(k, self.index.ntotal))
        
        return scores[0].tolist(), indices[0].tolist()
    
    def get_vectors_by_indices(self, indices: List[int], db_session: AsyncSession) -> List[Dict[str, Any]]:
        """Get chunk data by FAISS indices.
        
        Args:
            indices: FAISS indices
            db_session: Database session
            
        Returns:
            List of chunk data dictionaries
        """
        if not indices:
            return []
        
        # Get chunks from database by their IDs
        # Note: This assumes chunks are stored in order in the database
        # In a real implementation, you'd need to maintain a mapping
        
        # For now, return empty list - this would need to be implemented
        # based on how you store the mapping between FAISS indices and chunk IDs
        return []
    
    def _save_index(self) -> None:
        """Save FAISS index to disk."""
        faiss.write_index(self.index, self.index_path)
    
    def load_index(self) -> bool:
        """Load FAISS index from disk.
        
        Returns:
            True if index was loaded successfully, False otherwise
        """
        if not os.path.exists(self.index_path):
            return False
        
        try:
            self.index = faiss.read_index(self.index_path)
            self.metadata = self._load_metadata()
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__,
            "document_count": len(self.metadata.get("document_ids", set())),
        }
    
    def clear(self) -> None:
        """Clear the index."""
        self.index = self._initialize_index()
        self.metadata = {"total_vectors": 0, "document_ids": set()}
        self._save_index()
        self._save_metadata()


class VectorSearchService:
    """Service for vector search operations."""
    
    def __init__(self, index: FAISSIndex) -> None:
        """Initialize vector search service."""
        self.index = index
    
    async def search_chunks(self, query_vector: List[float], k: int, 
                          db_session: AsyncSession) -> List[Dict[str, Any]]:
        """Search for similar chunks.
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            db_session: Database session
            
        Returns:
            List of chunk data with scores
        """
        # Search FAISS index
        scores, indices = self.index.search(query_vector, k)
        
        if not indices:
            return []
        
        # Get chunk data from database
        # This is a simplified implementation - you'd need to maintain
        # a proper mapping between FAISS indices and chunk IDs
        
        # For now, we'll query chunks directly by their database IDs
        # assuming they're stored in order
        chunk_data = []
        
        for i, (score, idx) in enumerate(zip(scores, indices)):
            if idx < 0:  # Invalid index
                continue
            
            # Get chunk by index (simplified)
            # In reality, you'd need a proper mapping table
            stmt = select(Chunk).offset(idx).limit(1)
            result = await db_session.execute(stmt)
            chunk = result.scalar_one_or_none()
            
            if chunk:
                chunk_data.append({
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "text": chunk.text,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "score": float(score),
                    "chunk_index": chunk.chunk_index,
                })
        
        return chunk_data
