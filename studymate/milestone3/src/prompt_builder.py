from __future__ import annotations

from typing import Any, Dict, List, Tuple

DEFAULT_SYSTEM = (
    "You are a helpful assistant. Answer strictly based on the context below. "
    "If the answer cannot be found in the provided context, reply only: 'I don't know'. Do not hallucinate."
)


def estimate_tokens(text: str) -> int:
    """Rough token estimator: ~0.75 words per token -> invert => tokens ≈ words / 0.75.

    We use a conservative estimate: tokens ≈ len(words).
    """
    return max(1, len(text.split()))


def build_prompt(
    chunks: List[Dict[str, Any]],
    question: str,
    system_template: str | None = None,
    max_total_tokens: int = 2048,
    safety_margin: int = 256,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Construct a token-aware prompt using top-scored chunks.

    Chunks: each dict must contain 'text', 'source_file', 'page', 'score'.
    Returns the prompt text and the list of chunks actually used.
    """
    if not chunks:
        system = system_template or DEFAULT_SYSTEM
        prompt = f"{system}\n\nContext:\n(none)\n\nQuestion: {question}\nAnswer:"
        return prompt, []

    system = system_template or DEFAULT_SYSTEM
    # Sort by score descending
    ranked = sorted(chunks, key=lambda c: c.get("score", 0.0), reverse=True)

    header = f"{system}\n\nContext:"
    used: List[Dict[str, Any]] = []
    lines: List[str] = [header]

    # Build incrementally while respecting token budget
    budget = max_total_tokens - safety_margin
    tokens_so_far = estimate_tokens(system) + estimate_tokens("Question: ") + estimate_tokens(question) + 50

    for idx, ch in enumerate(ranked, start=1):
        entry = f"- [{idx}] ({ch.get('source_file')} p.{ch.get('page')}, score={ch.get('score'):.3f})\n{ch.get('text')}\n"
        need = estimate_tokens(entry)
        if tokens_so_far + need > budget:
            break
        lines.append(entry)
        used.append(ch)
        tokens_so_far += need

    lines.append(f"\nQuestion: {question}\nAnswer:")
    prompt_text = "\n".join(lines)
    return prompt_text, used



