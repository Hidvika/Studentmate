import pytest
from unittest.mock import Mock, patch
import numpy as np

from app.retrieval.embeddings import (
    SentenceTransformersEmbeddings,
    WatsonxEmbeddings,
    create_embeddings,
    serialize_embedding,
    deserialize_embedding
)


def test_sentence_transformers_embeddings():
    """Test sentence-transformers embeddings."""
    with patch('app.retrieval.embeddings.SentenceTransformer') as mock_model:
        # Mock the model
        mock_instance = Mock()
        mock_instance.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_instance.get_sentence_embedding_dimension.return_value = 3
        mock_model.return_value = mock_instance
        
        embeddings = SentenceTransformersEmbeddings("test-model")
        
        # Test embedding generation
        texts = ["Hello world", "Test text"]
        result = embeddings.embed_texts(texts)
        
        assert len(result) == 2
        assert len(result[0]) == 3
        assert len(result[1]) == 3
        
        # Test dimension
        assert embeddings.get_dimension() == 3


def test_watsonx_embeddings():
    """Test WatsonX embeddings."""
    with patch('app.retrieval.embeddings.APIClient') as mock_client, \
         patch('app.retrieval.embeddings.Credentials') as mock_creds:
        
        # Mock the client and credentials
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_creds_instance = Mock()
        mock_creds.return_value = mock_creds_instance
        
        embeddings = WatsonxEmbeddings("test-key", "test-project")
        
        # Test embedding generation (should raise RuntimeError for now)
        texts = ["Hello world", "Test text"]
        with pytest.raises(RuntimeError, match="WatsonX embeddings implementation needs to be completed"):
            result = embeddings.embed_texts(texts)


def test_batched_embeddings():
    """Test batched embeddings wrapper."""
    with patch('app.retrieval.embeddings.SentenceTransformer') as mock_model:
        # Mock the model
        mock_instance = Mock()
        mock_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_instance.get_sentence_embedding_dimension.return_value = 3
        mock_model.return_value = mock_instance
        
        base_embeddings = SentenceTransformersEmbeddings("test-model")
        
        # Test with small batch size
        from app.retrieval.embeddings import BatchedEmbeddings
        batched = BatchedEmbeddings(base_embeddings, batch_size=1)
        
        texts = ["Hello", "World", "Test"]
        result = batched.embed_texts(texts)
        
        assert len(result) == 3
        assert all(len(embedding) == 3 for embedding in result)


def test_serialize_deserialize_embedding():
    """Test embedding serialization and deserialization."""
    embedding = [0.1, 0.2, 0.3, 0.4]
    
    # Serialize
    serialized = serialize_embedding(embedding)
    assert isinstance(serialized, str)
    
    # Deserialize
    deserialized = deserialize_embedding(serialized)
    assert deserialized == embedding


def test_create_embeddings_sentence_transformers():
    """Test create_embeddings with sentence-transformers backend."""
    with patch('app.retrieval.embeddings.settings') as mock_settings, \
         patch('app.retrieval.embeddings.SentenceTransformersEmbeddings') as mock_st:
        
        mock_settings.embeddings_backend = "sentence-transformers"
        mock_settings.embeddings_model = "test-model"
        
        mock_instance = Mock()
        mock_st.return_value = mock_instance
        
        result = create_embeddings()
        
        # Should return a BatchedEmbeddings wrapper
        from app.retrieval.embeddings import BatchedEmbeddings
        assert isinstance(result, BatchedEmbeddings)


def test_create_embeddings_watsonx():
    """Test create_embeddings with WatsonX backend."""
    with patch('app.retrieval.embeddings.settings') as mock_settings, \
         patch('app.retrieval.embeddings.WatsonxEmbeddings') as mock_watsonx:
        
        mock_settings.embeddings_backend = "watsonx"
        mock_settings.watsonx_api_key = "test-key"
        mock_settings.watsonx_project_id = "test-project"
        mock_settings.watsonx_url = "test-url"
        
        mock_instance = Mock()
        mock_watsonx.return_value = mock_instance
        
        result = create_embeddings()
        
        # Should return a BatchedEmbeddings wrapper
        from app.retrieval.embeddings import BatchedEmbeddings
        assert isinstance(result, BatchedEmbeddings)


def test_create_embeddings_invalid_backend():
    """Test create_embeddings with invalid backend."""
    with patch('app.retrieval.embeddings.settings') as mock_settings:
        mock_settings.embeddings_backend = "invalid-backend"
        
        with pytest.raises(ValueError, match="Unsupported embeddings backend"):
            create_embeddings()


def test_watsonx_embeddings_missing_credentials():
    """Test WatsonX embeddings with missing credentials."""
    with pytest.raises(ValueError, match="WatsonX API key and project ID are required"):
        WatsonxEmbeddings("", "")


def test_embeddings_empty_texts():
    """Test embeddings with empty text list."""
    with patch('app.retrieval.embeddings.SentenceTransformer') as mock_model:
        mock_instance = Mock()
        mock_instance.encode.return_value = np.array([])
        mock_instance.get_sentence_embedding_dimension.return_value = 3
        mock_model.return_value = mock_instance
        
        embeddings = SentenceTransformersEmbeddings("test-model")
        result = embeddings.embed_texts([])
        
        assert result == []
