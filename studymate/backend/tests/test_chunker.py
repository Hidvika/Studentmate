import pytest
from app.ingestion.chunker import Chunker


def test_chunker_initialization():
    """Test chunker initialization with default parameters."""
    chunker = Chunker()
    assert chunker.chunk_size == 500
    assert chunker.chunk_overlap == 100
    assert chunker.stride == 400  # 500 - 100


def test_chunker_custom_parameters():
    """Test chunker with custom parameters."""
    chunker = Chunker(chunk_size=300, chunk_overlap=50)
    assert chunker.chunk_size == 300
    assert chunker.chunk_overlap == 50
    assert chunker.stride == 250  # 300 - 50


def test_chunker_short_text():
    """Test chunking of short text (less than chunk_size)."""
    chunker = Chunker()
    text = "This is a short text with only a few words."
    chunks = chunker.chunk_text(text, "test.pdf")
    
    assert len(chunks) == 1
    assert chunks[0]["text"] == text.strip()
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["start_word"] == 0
    assert chunks[0]["end_word"] == 10  # 10 words


def test_chunker_exact_chunk_size():
    """Test chunking of text with exactly chunk_size words."""
    chunker = Chunker(chunk_size=5, chunk_overlap=1)
    
    # Create text with exactly 5 words
    words = ["word"] * 5
    text = " ".join(words)
    
    chunks = chunker.chunk_text(text, "test.pdf")
    
    assert len(chunks) == 1
    assert chunks[0]["text"] == text
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["start_word"] == 0
    assert chunks[0]["end_word"] == 5


def test_chunker_multiple_chunks():
    """Test chunking with multiple chunks and overlap."""
    chunker = Chunker(chunk_size=5, chunk_overlap=2)
    
    # Create text with 12 words
    words = [f"word{i}" for i in range(12)]
    text = " ".join(words)
    
    chunks = chunker.chunk_text(text, "test.pdf")
    
    # Expected: ceil((12-5)/3)+1 = ceil(7/3)+1 = 3+1 = 4 chunks
    assert len(chunks) == 4
    
    # Check first chunk
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["start_word"] == 0
    assert chunks[0]["end_word"] == 5
    assert chunks[0]["text"] == "word0 word1 word2 word3 word4"
    
    # Check second chunk
    assert chunks[1]["chunk_index"] == 1
    assert chunks[1]["start_word"] == 3  # stride = 3
    assert chunks[1]["end_word"] == 8
    assert chunks[1]["text"] == "word3 word4 word5 word6 word7"
    
    # Check third chunk
    assert chunks[2]["chunk_index"] == 2
    assert chunks[2]["start_word"] == 6
    assert chunks[2]["end_word"] == 11
    assert chunks[2]["text"] == "word6 word7 word8 word9 word10"
    
    # Check fourth chunk
    assert chunks[3]["chunk_index"] == 3
    assert chunks[3]["start_word"] == 9
    assert chunks[3]["end_word"] == 12
    assert chunks[3]["text"] == "word9 word10 word11"


def test_chunker_overlap_validation():
    """Test that chunks have correct overlap."""
    chunker = Chunker(chunk_size=5, chunk_overlap=2)
    
    # Create text with 10 words
    words = [f"word{i}" for i in range(10)]
    text = " ".join(words)
    
    chunks = chunker.chunk_text(text, "test.pdf")
    
    # Validate overlap
    assert chunker.validate_overlap(chunks) == True
    
    # Check overlap between chunks
    if len(chunks) >= 2:
        chunk1_words = chunks[0]["text"].split()
        chunk2_words = chunks[1]["text"].split()
        
        # Last 2 words of chunk1 should equal first 2 words of chunk2
        assert chunk1_words[-2:] == chunk2_words[:2]


def test_chunker_calculate_num_chunks():
    """Test the chunk calculation formula."""
    chunker = Chunker(chunk_size=500, chunk_overlap=100)
    
    # Test with N=500 words (exactly one chunk)
    assert chunker._calculate_num_chunks(500) == 1
    
    # Test with N=1000 words
    # Formula: ceil((1000-500)/400)+1 = ceil(500/400)+1 = 2+1 = 3
    assert chunker._calculate_num_chunks(1000) == 3
    
    # Test with N=1500 words
    # Formula: ceil((1500-500)/400)+1 = ceil(1000/400)+1 = 3+1 = 4
    assert chunker._calculate_num_chunks(1500) == 4


def test_chunker_page_range_estimation():
    """Test page range estimation."""
    chunker = Chunker()
    
    # Test with page texts
    page_texts = [
        "Page 1 content with some words",
        "Page 2 content with more words",
        "Page 3 content with even more words"
    ]
    
    # Test chunk that spans pages 1-2
    start_word, end_word = chunker._estimate_page_range(0, 5, 10, page_texts)
    assert start_word == 1
    assert end_word == 1  # This is a simplified test


def test_chunker_empty_text():
    """Test chunking empty text."""
    chunker = Chunker()
    chunks = chunker.chunk_text("", "test.pdf")
    assert len(chunks) == 0
    
    chunks = chunker.chunk_text("   ", "test.pdf")
    assert len(chunks) == 0


def test_chunker_metadata():
    """Test that chunks have correct metadata."""
    chunker = Chunker(chunk_size=5, chunk_overlap=2)
    
    text = "word0 word1 word2 word3 word4 word5 word6 word7 word8 word9"
    chunks = chunker.chunk_text(text, "test_document.pdf", ["Page 1", "Page 2"])
    
    for chunk in chunks:
        assert "chunk_index" in chunk
        assert "start_word" in chunk
        assert "end_word" in chunk
        assert "page_start" in chunk
        assert "page_end" in chunk
        assert "text" in chunk
        assert "source_filename" in chunk
        assert "word_count" in chunk
        
        assert chunk["source_filename"] == "test_document.pdf"
        assert chunk["word_count"] == len(chunk["text"].split())
