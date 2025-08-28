from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..prompt_builder import build_prompt
from ..watsonx_client import WatsonxClient, client_from_env


log = logging.getLogger("milestone3")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Milestone 3 API")


class QueryIn(BaseModel):
    question: str
    k: int = 8
    model_id: str | None = None


def mock_retrieve_topk(question: str, k: int) -> List[Dict[str, Any]]:
    # Placeholder retrieval for demo/testing
    return [
        {"text": "Machine learning uses data to build predictive models.", "source_file": "ml_intro.pdf", "page": 10, "score": 0.92},
        {"text": "Supervised learning involves labeled data and targets.", "source_file": "ml_intro.pdf", "page": 12, "score": 0.88},
        {"text": "Unsupervised learning finds structure without labels.", "source_file": "ml_intro.pdf", "page": 15, "score": 0.80},
    ][:k]


@app.post("/api/query")
def api_query(payload: QueryIn):
    chunks = mock_retrieve_topk(payload.question, payload.k)
    prompt, used = build_prompt(chunks, payload.question)

    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    model_id = payload.model_id or os.environ.get("MODEL_ID", "mistralai/mixtral-8x7b-instruct-v01")

    try:
        client: WatsonxClient = client_from_env()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"watsonx client init failed: {e}")

    log.info("Submitting prompt: len=%d, hash=%s, model_id=%s", len(prompt), prompt_hash, model_id)
    gen = client.generate_from_prompt(prompt_text=prompt, model_id=model_id)

    answer = gen.get("answer") or ""
    if not answer:
        # If model failed or empty, apply hallucination guard
        answer = "I don't know"

    # Minimal rule: enforce exact response when not grounded
    if not used:
        answer = "I don't know"

    return {
        "answer": answer,
        "chunks_used": used,
        "model": gen.get("meta", {}),
        "prompt_hash": prompt_hash,
        "warnings": [] if used else ["No chunks used; answer may be ungrounded."],
    }



