import json
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from ibm_watsonx_ai import APIClient, Credentials

from app.core.config import settings


class EmbeddingsInterface(ABC):
    """Abstract interface for text embeddings."""
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts into vectors.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        pass


class SentenceTransformersEmbeddings(EmbeddingsInterface):
    """Sentence-transformers implementation using BAAI/bge-small-en-v1.5."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        """Initialize the sentence-transformers model."""
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using sentence-transformers."""
        if not texts:
            return []
        
        # Convert to numpy arrays and normalize
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # L2 normalize (required for cosine similarity)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Convert to list of lists
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


class WatsonxEmbeddings(EmbeddingsInterface):
    """IBM WatsonX embeddings implementation."""
    
    def __init__(self, api_key: str, project_id: str, url: str = None) -> None:
        """Initialize WatsonX embeddings client."""
        if not api_key or not project_id:
            raise ValueError("WatsonX API key and project ID are required")
        
        self.api_key = api_key
        self.project_id = project_id
        self.url = url or settings.watsonx_url
        
        # Initialize client
        credentials = Credentials(url=self.url, api_key=self.api_key)
        self.client = APIClient(credentials=credentials)
        
        # Cache dimension
        self._dimension = None
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using WatsonX embeddings."""
        if not texts:
            return []
        
        try:
            # WatsonX embeddings API - using the client directly
            # Note: This is a simplified implementation. In practice, you'd use the proper WatsonX embeddings API
            # For now, we'll raise an error to indicate this needs proper implementation
            raise NotImplementedError("WatsonX embeddings implementation needs to be completed with proper API calls")
            
            # Placeholder for actual implementation:
            # response = self.client.embeddings.embed_text(
            #     texts=texts,
            #     model_id="sentence-transformers__all-minilm-l6-v2"
            # )
            # embeddings.append(normalized.tolist())
            
            # For now, return empty embeddings since implementation is not complete
            return []
            
            return embeddings
            
        except Exception as e:
            raise RuntimeError(f"WatsonX embeddings failed: {e}")
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            # Get dimension by embedding a single text
            test_embedding = self.embed_texts(["test"])
            self._dimension = len(test_embedding[0]) if test_embedding else 384
        return self._dimension


class BatchedEmbeddings:
    """Wrapper for batching and rate limiting embeddings."""
    
    def __init__(self, embeddings: EmbeddingsInterface, batch_size: int = 32, 
                 rate_limit_delay: float = 0.1) -> None:
        """Initialize batched embeddings wrapper.
        
        Args:
            embeddings: Underlying embeddings implementation
            batch_size: Number of texts to process in each batch
            rate_limit_delay: Delay between batches in seconds
        """
        self.embeddings = embeddings
        self.batch_size = batch_size
        self.rate_limit_delay = rate_limit_delay
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts in batches with rate limiting."""
        if not texts:
            return []
        
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # Embed batch
            batch_embeddings = self.embeddings.embed_texts(batch)
            all_embeddings.extend(batch_embeddings)
            
            # Rate limiting
            if i + self.batch_size < len(texts):
                time.sleep(self.rate_limit_delay)
        
        return all_embeddings
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embeddings.get_dimension()


def create_embeddings() -> EmbeddingsInterface:
    """Factory function to create embeddings based on configuration."""
    backend = settings.embeddings_backend.lower()
    
    if backend == "sentence-transformers":
        model_name = settings.embeddings_model
        embeddings = SentenceTransformersEmbeddings(model_name)
        return BatchedEmbeddings(embeddings)
    
    elif backend == "watsonx":
        if not settings.watsonx_api_key or not settings.watsonx_project_id:
            raise RuntimeError(
                "WatsonX embeddings require WATSONX_API_KEY and WATSONX_PROJECT_ID "
                "environment variables to be set"
            )
        
        embeddings = WatsonxEmbeddings(
            api_key=settings.watsonx_api_key,
            project_id=settings.watsonx_project_id,
            url=settings.watsonx_url
        )
        return BatchedEmbeddings(embeddings)
    
    else:
        raise ValueError(f"Unsupported embeddings backend: {backend}")


def serialize_embedding(embedding: List[float]) -> str:
    """Serialize embedding vector to JSON string."""
    return json.dumps(embedding)


def deserialize_embedding(embedding_str: str) -> List[float]:
    """Deserialize embedding vector from JSON string."""
    return json.loads(embedding_str)
