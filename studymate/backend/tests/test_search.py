import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.search import SearchRequest, SearchHit, SearchResponse


@pytest.fixture
def client():
    return TestClient(app)


def test_search_request_validation():
    """Test search request validation."""
    # Valid request
    request = SearchRequest(query="What is machine learning?", k=5)
    assert request.query == "What is machine learning?"
    assert request.k == 5
    
    # Test with default k
    request = SearchRequest(query="Test query")
    assert request.k is None
    
    # Test with invalid k
    with pytest.raises(ValueError):
        SearchRequest(query="Test", k=0)
    
    with pytest.raises(ValueError):
        SearchRequest(query="Test", k=51)


def test_search_hit_model():
    """Test search hit model."""
    hit = SearchHit(
        chunk_id="uuid1",
        document_id="uuid2",
        filename="test.pdf",
        page_start=1,
        page_end=2,
        text="Test content",
        score=0.85,
        chunk_index=0
    )
    
    assert hit.chunk_id == "uuid1"
    assert hit.document_id == "uuid2"
    assert hit.filename == "test.pdf"
    assert hit.page_start == 1
    assert hit.page_end == 2
    assert hit.text == "Test content"
    assert hit.score == 0.85
    assert hit.chunk_index == 0


def test_search_response_model():
    """Test search response model."""
    hits = [
        SearchHit(
            chunk_id="uuid1",
            document_id="uuid2",
            filename="test.pdf",
            page_start=1,
            page_end=2,
            text="Test content",
            score=0.85,
            chunk_index=0
        )
    ]
    
    response = SearchResponse(
        hits=hits,
        total_hits=1,
        query="Test query"
    )
    
    assert len(response.hits) == 1
    assert response.total_hits == 1
    assert response.query == "Test query"


@patch('app.api.search.embeddings')
@patch('app.api.search.search_service')
@patch('app.api.search.settings')
@pytest.mark.asyncio
async def test_search_chunks_success(mock_settings, mock_search_service, mock_embeddings):
    """Test successful search operation."""
    # Mock settings
    mock_settings.default_top_k = 5
    mock_settings.max_top_k = 20
    
    # Mock embeddings
    mock_embeddings.embed_texts.return_value = [[0.1, 0.2, 0.3]]
    
    # Mock search service
    mock_search_service.search_chunks = AsyncMock(return_value=[
            {
                "chunk_id": "uuid1",
                "document_id": "uuid2",
                "filename": "test.pdf",
                "page_start": 1,
                "page_end": 2,
                "text": "Test content",
                "score": 0.85,
                "chunk_index": 0
            }
        ])
    
    # Mock database session
    mock_db = AsyncMock()
    
    # Test the search function
    from app.api.search import search_chunks
    request = SearchRequest(query="Test query", k=5)
    
    response = await search_chunks(request, mock_db)
    
    assert response.total_hits == 1
    assert response.query == "Test query"
    assert len(response.hits) == 1
    assert response.hits[0].chunk_id == "uuid1"
    assert response.hits[0].score == 0.85


@patch('app.api.search.embeddings')
@patch('app.api.search.settings')
@pytest.mark.asyncio
async def test_search_chunks_embedding_failure(mock_settings, mock_embeddings):
    """Test search with embedding failure."""
    # Mock settings
    mock_settings.default_top_k = 5
    mock_settings.max_top_k = 20
    
    # Mock embeddings failure
    mock_embeddings.embed_texts.return_value = []
    
    # Mock database session
    mock_db = AsyncMock()
    
    # Test the search function
    from app.api.search import search_chunks
    request = SearchRequest(query="Test query")
    
    with pytest.raises(Exception, match="Failed to embed query"):
        await search_chunks(request, mock_db)


@patch('app.api.search.faiss_index')
@pytest.mark.asyncio
async def test_get_search_stats(mock_faiss_index):
    """Test getting search statistics."""
    # Mock FAISS index stats
    mock_faiss_index.get_stats.return_value = {
        "total_vectors": 1000,
        "dimension": 384,
        "index_type": "HNSW",
        "document_count": 10
    }
    
    # Mock settings
    with patch('app.api.search.settings') as mock_settings:
        mock_settings.embeddings_backend = "sentence-transformers"
        mock_settings.embeddings_model = "test-model"
        
        # Mock embeddings
        with patch('app.api.search.embeddings') as mock_embeddings:
            mock_embeddings.get_dimension.return_value = 384
            
            # Test the stats function
            from app.api.search import get_search_stats
            
            response = await get_search_stats()
            
            assert response["index_stats"]["total_vectors"] == 1000
            assert response["index_stats"]["dimension"] == 384
            assert response["embedding_backend"] == "sentence-transformers"
            assert response["embedding_model"] == "test-model"
            assert response["embedding_dimension"] == 384


def test_search_request_optional_fields():
    """Test search request with optional fields."""
    # Test with only required field
    request = SearchRequest(query="Test query")
    assert request.query == "Test query"
    assert request.k is None
    
    # Test with all fields
    request = SearchRequest(query="Test query", k=10)
    assert request.query == "Test query"
    assert request.k == 10


def test_search_hit_validation():
    """Test search hit validation."""
    # Valid hit
    hit = SearchHit(
        chunk_id="uuid1",
        document_id="uuid2",
        filename="test.pdf",
        page_start=1,
        page_end=2,
        text="Test content",
        score=0.85,
        chunk_index=0
    )
    
    # Test score validation (should be float)
    assert isinstance(hit.score, float)
    
    # Test page validation
    assert hit.page_start <= hit.page_end


def test_search_response_validation():
    """Test search response validation."""
    hits = [
        SearchHit(
            chunk_id="uuid1",
            document_id="uuid2",
            filename="test.pdf",
            page_start=1,
            page_end=2,
            text="Test content",
            score=0.85,
            chunk_index=0
        )
    ]
    
    response = SearchResponse(
        hits=hits,
        total_hits=1,
        query="Test query"
    )
    
    # Test that total_hits matches actual hits
    assert response.total_hits == len(response.hits)
    
    # Test query validation
    assert len(response.query) > 0
