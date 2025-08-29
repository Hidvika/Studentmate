import pytest
from app.llm.prompts import (
    build_rag_prompt,
    RAG_SYSTEM_PROMPT,
    build_citation_instruction,
    build_followup_instruction
)


def test_build_rag_prompt_empty_chunks():
    """Test building RAG prompt with no chunks."""
    question = "What is machine learning?"
    prompt, used_chunks = build_rag_prompt([], question)
    
    assert "Context:\n(none)" in prompt
    assert question in prompt
    assert used_chunks == []


def test_build_rag_prompt_with_chunks():
    """Test building RAG prompt with chunks."""
    chunks = [
        {
            "text": "Machine learning is a subset of artificial intelligence.",
            "source_filename": "paper1.pdf",
            "page_start": 1,
            "page_end": 1,
            "score": 0.9
        },
        {
            "text": "Deep learning uses neural networks with multiple layers.",
            "source_filename": "paper2.pdf",
            "page_start": 5,
            "page_end": 6,
            "score": 0.8
        }
    ]
    
    question = "What is machine learning?"
    prompt, used_chunks = build_rag_prompt(chunks, question)
    
    assert "Context:" in prompt
    assert question in prompt
    assert len(used_chunks) == 2
    
    # Check that chunks are sorted by score (descending)
    assert used_chunks[0]["score"] == 0.9
    assert used_chunks[1]["score"] == 0.8
    
    # Check that chunk information is included
    assert "paper1.pdf" in prompt
    assert "paper2.pdf" in prompt
    assert "p.1" in prompt
    assert "p.5–6" in prompt


def test_build_rag_prompt_token_limit():
    """Test that prompt respects token limits."""
    # Create many chunks to test token limiting
    chunks = []
    for i in range(10):
        chunks.append({
            "text": "This is a very long chunk of text that contains many words and should help us test the token limiting functionality of the prompt builder. " * 5,
            "source_filename": f"paper{i}.pdf",
            "page_start": i + 1,
            "page_end": i + 1,
            "score": 1.0 - (i * 0.1)
        })
    
    question = "What is machine learning?"
    prompt, used_chunks = build_rag_prompt(chunks, question, max_total_tokens=1000, safety_margin=200)
    
    # Should use fewer chunks due to token limit
    assert len(used_chunks) < len(chunks)
    assert len(used_chunks) > 0


def test_build_rag_prompt_custom_system():
    """Test building RAG prompt with custom system prompt."""
    custom_system = "You are a helpful assistant. Answer based on the context."
    chunks = [
        {
            "text": "Test content",
            "source_filename": "test.pdf",
            "page_start": 1,
            "page_end": 1,
            "score": 0.9
        }
    ]
    
    question = "What is this about?"
    prompt, used_chunks = build_rag_prompt(chunks, question, system_prompt=custom_system)
    
    assert custom_system in prompt
    assert RAG_SYSTEM_PROMPT not in prompt


def test_build_rag_prompt_chunk_formatting():
    """Test that chunks are formatted correctly in the prompt."""
    chunks = [
        {
            "text": "Simple test content",
            "source_filename": "test.pdf",
            "page_start": 1,
            "page_end": 2,
            "score": 0.95
        }
    ]
    
    question = "Test question?"
    prompt, used_chunks = build_rag_prompt(chunks, question)
    
    # Check for expected format: [1] (test.pdf p.1–2, score=0.950)
    assert "[1]" in prompt
    assert "(test.pdf p.1–2, score=0.950)" in prompt
    assert "Simple test content" in prompt


def test_build_citation_instruction():
    """Test citation instruction builder."""
    instruction = build_citation_instruction()
    
    assert "filename p.x–y" in instruction
    assert "filename p.x" in instruction
    assert "research_paper.pdf p.15–17" in instruction
    assert "lecture_notes.pdf p.3" in instruction


def test_build_followup_instruction():
    """Test follow-up instruction builder."""
    instruction = build_followup_instruction()
    
    assert "follow-up question" in instruction
    assert "citation standards" in instruction
    assert "evidence-based approach" in instruction


def test_rag_system_prompt_content():
    """Test that RAG system prompt contains expected content."""
    assert "academic assistant" in RAG_SYSTEM_PROMPT
    assert "ONLY on the provided context" in RAG_SYSTEM_PROMPT
    assert "don't have enough information" in RAG_SYSTEM_PROMPT
    assert "cite your sources" in RAG_SYSTEM_PROMPT
    assert "[filename p.x–y]" in RAG_SYSTEM_PROMPT


def test_prompt_structure():
    """Test that prompt has correct structure."""
    chunks = [
        {
            "text": "Test content",
            "source_filename": "test.pdf",
            "page_start": 1,
            "page_end": 1,
            "score": 0.9
        }
    ]
    
    question = "Test question?"
    prompt, _ = build_rag_prompt(chunks, question)
    
    # Check structure: system prompt -> context -> question -> answer
    lines = prompt.split('\n')
    
    # Should have system prompt at the beginning
    assert any("academic assistant" in line for line in lines[:5])
    
    # Should have context section
    assert any("Context:" in line for line in lines)
    
    # Should have question at the end
    assert "Question: Test question?" in prompt
    
    # Should end with "Answer:"
    assert prompt.endswith("Answer:")


def test_prompt_with_special_characters():
    """Test prompt building with special characters in text."""
    chunks = [
        {
            "text": "Content with special chars: éñtërnâtiönål & symbols!",
            "source_filename": "test.pdf",
            "page_start": 1,
            "page_end": 1,
            "score": 0.9
        }
    ]
    
    question = "What about special chars?"
    prompt, used_chunks = build_rag_prompt(chunks, question)
    
    assert "éñtërnâtiönål" in prompt
    assert "& symbols!" in prompt
    assert len(used_chunks) == 1
