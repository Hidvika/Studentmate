from __future__ import annotations

from studymate.milestone3.src.prompt_builder import build_prompt


def test_build_prompt_respects_token_limit():
    chunks = [
        {"text": "a " * 300, "source_file": "a.pdf", "page": 1, "score": 0.9},
        {"text": "b " * 300, "source_file": "b.pdf", "page": 2, "score": 0.8},
        {"text": "c " * 300, "source_file": "c.pdf", "page": 3, "score": 0.7},
    ]
    prompt, used = build_prompt(chunks, question="What?", max_total_tokens=600, safety_margin=100)
    assert len(used) >= 1
    assert len(used) <= 2
    assert all("text" in u and "source_file" in u and "page" in u for u in used)


def test_build_prompt_prioritizes_score():
    chunks = [
        {"text": "low", "source_file": "x.pdf", "page": 1, "score": 0.1},
        {"text": "high", "source_file": "y.pdf", "page": 2, "score": 0.9},
    ]
    prompt, used = build_prompt(chunks, question="Q", max_total_tokens=200)
    assert used[0]["text"] == "high"



