from typing import Any, Dict, List


RAG_SYSTEM_PROMPT = """You are a helpful academic assistant. Your task is to answer questions based ONLY on the provided context from uploaded documents.

IMPORTANT RULES:
1. Answer ONLY using information from the provided context
2. If the answer cannot be found in the context, say "I don't have enough information to answer this question based on the provided documents."
3. Do not make up or infer information not present in the context
4. Always cite your sources using the format [filename p.x–y] where x and y are page numbers
5. Be concise but thorough in your answers
6. If you need to reference multiple sources, cite each one separately

Context will be provided as numbered evidence snippets with source information."""


def build_rag_prompt(
    chunks: List[Dict[str, Any]],
    question: str,
    system_prompt: str = None,
    max_total_tokens: int = 2048,
    safety_margin: int = 256,
) -> tuple[str, List[Dict[str, Any]]]:
    """Construct a token-aware RAG prompt using top-scored chunks.
    
    Args:
        chunks: List of chunk dictionaries with 'text', 'source_filename', 'page_start', 'page_end', 'score'
        question: User's question
        system_prompt: Custom system prompt (optional)
        max_total_tokens: Maximum total tokens for the prompt
        safety_margin: Safety margin to leave for response
        
    Returns:
        Tuple of (prompt_text, chunks_used)
    """
    if not chunks:
        system = system_prompt or RAG_SYSTEM_PROMPT
        prompt = f"{system}\n\nContext:\n(none)\n\nQuestion: {question}\nAnswer:"
        return prompt, []
    
    system = system_prompt or RAG_SYSTEM_PROMPT
    
    # Sort by score descending
    ranked = sorted(chunks, key=lambda c: c.get("score", 0.0), reverse=True)
    
    header = f"{system}\n\nContext:"
    used: List[Dict[str, Any]] = []
    lines: List[str] = [header]
    
    # Build incrementally while respecting token budget
    budget = max_total_tokens - safety_margin
    tokens_so_far = _estimate_tokens(system) + _estimate_tokens("Question: ") + _estimate_tokens(question) + 50
    
    for idx, chunk in enumerate(ranked, start=1):
        filename = chunk.get("source_filename", "Unknown")
        page_start = chunk.get("page_start", 1)
        page_end = chunk.get("page_end", page_start)
        score = chunk.get("score", 0.0)
        text = chunk.get("text", "")
        
        entry = f"- [{idx}] ({filename} p.{page_start}–{page_end}, score={score:.3f})\n{text}\n"
        need = _estimate_tokens(entry)
        
        if tokens_so_far + need > budget:
            break
            
        lines.append(entry)
        used.append(chunk)
        tokens_so_far += need
    
    lines.append(f"\nQuestion: {question}\nAnswer:")
    prompt_text = "\n".join(lines)
    
    return prompt_text, used


def _estimate_tokens(text: str) -> int:
    """Rough token estimator: ~0.75 words per token -> invert => tokens ≈ words / 0.75.
    
    We use a conservative estimate: tokens ≈ len(words).
    """
    return max(1, len(text.split()))


def build_citation_instruction() -> str:
    """Build instruction for proper citation format."""
    return """
When citing sources, use this exact format:
- [filename p.x–y] for page ranges
- [filename p.x] for single pages

Examples:
- [research_paper.pdf p.15–17]
- [lecture_notes.pdf p.3]
- [textbook.pdf p.42–45]

Always include the filename and page numbers for each piece of information you use."""


def build_followup_instruction() -> str:
    """Build instruction for follow-up questions."""
    return """
If the user asks a follow-up question, you can reference information from previous messages in this conversation, but still cite the original source documents when possible.

For follow-up questions, maintain the same citation standards and evidence-based approach."""
