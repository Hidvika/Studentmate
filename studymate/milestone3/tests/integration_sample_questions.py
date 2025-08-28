from __future__ import annotations

from studymate.milestone3.src.prompt_builder import build_prompt


def test_integration_prompt_contains_selected_chunks():
    chunks = [
        {"text": "This book introduces machine learning basics.", "source_file": "intro_ml.pdf", "page": 5, "score": 0.95},
        {"text": "Classification is a supervised task.", "source_file": "intro_ml.pdf", "page": 12, "score": 0.85},
    ]
    prompt, used = build_prompt(chunks, question="What is classification?")
    assert any("Classification" in u["text"] for u in used)



