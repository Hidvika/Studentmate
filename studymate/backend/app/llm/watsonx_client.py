from __future__ import annotations

import os
import time
from typing import Any, AsyncGenerator, Optional, TypedDict

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods

from app.core.config import settings


class GenerationResult(TypedDict, total=False):
    answer: str
    raw: Any
    meta: dict[str, Any]


class WatsonxClient:
    """Thin client for IBM watsonx.ai text generation with streaming support."""

    def __init__(self, url: str = None, api_key: str = None, project_id: str = None, 
                 model_id: str = None, space_id: Optional[str] = None, 
                 timeout_s: float = 30.0, max_retries: int = 3) -> None:
        """Initialize WatsonX client."""
        self.url = url or settings.watsonx_url
        self.api_key = api_key or settings.watsonx_api_key
        self.project_id = project_id or settings.watsonx_project_id
        self.model_id = model_id or settings.watsonx_model_id
        self.space_id = space_id
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        
        if not self.api_key or not self.project_id:
            raise ValueError("WatsonX API key and project ID are required")

    def _build_api(self) -> tuple[APIClient, dict[str, Any]]:
        """Build API client and metadata."""
        creds = Credentials(url=self.url, api_key=self.api_key)
        client = APIClient(credentials=creds, space_id=self.space_id) if self.space_id else APIClient(credentials=creds)
        meta: dict[str, Any] = {"url": self.url, "project_id": self.project_id}
        if self.space_id:
            meta["space_id"] = self.space_id
        return client, meta

    def generate_from_prompt(
        self,
        prompt_text: str,
        max_new_tokens: int = 300,
        temperature: float = 0.5,
        decoding_method: str = "greedy",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> GenerationResult:
        """Generate text from a prompt using watsonx foundation models.

        Returns a dict with the final answer, raw SDK response, and model metadata.
        Retries on transient errors with exponential backoff.
        """

        client, meta = self._build_api()
        params: dict[str, Any] = {
            GenParams.MAX_NEW_TOKENS: max_new_tokens,
            GenParams.TEMPERATURE: temperature,
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY if decoding_method.lower() == "greedy" else decoding_method,
        }
        if extra_params:
            params.update(extra_params)

        model = ModelInference(model_id=self.model_id, api_client=client, project_id=self.project_id)

        last_err: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                # The SDK returns either a string or a dict depending on version/config
                raw = model.generate_text(prompt=prompt_text, params=params, request_timeout=self.timeout_s)
                answer = raw if isinstance(raw, str) else raw.get("generated_text") or raw
                return GenerationResult(
                    answer=str(answer), 
                    raw=raw, 
                    meta={
                        "model_id": self.model_id, 
                        **meta, 
                        "params": {
                            "max_new_tokens": max_new_tokens, 
                            "temperature": temperature, 
                            "decoding_method": decoding_method
                        }
                    }
                )
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                if attempt == self.max_retries:
                    break
                time.sleep(min(2 ** (attempt - 1), 5))

        return GenerationResult(
            answer="", 
            raw={"error": str(last_err)}, 
            meta={"model_id": self.model_id, **meta, "error": True}
        )

    async def generate_stream(
        self,
        prompt_text: str,
        max_new_tokens: int = 300,
        temperature: float = 0.5,
        decoding_method: str = "greedy",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate text stream from a prompt using watsonx foundation models.
        
        Yields tokens as they are generated.
        """
        client, meta = self._build_api()
        params: dict[str, Any] = {
            GenParams.MAX_NEW_TOKENS: max_new_tokens,
            GenParams.TEMPERATURE: temperature,
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY if decoding_method.lower() == "greedy" else decoding_method,
        }
        if extra_params:
            params.update(extra_params)

        model = ModelInference(model_id=self.model_id, api_client=client, project_id=self.project_id)

        try:
            # Use streaming generation
            response = model.generate_text_stream(
                prompt=prompt_text, 
                params=params, 
                request_timeout=self.timeout_s
            )
            
            for chunk in response:
                if hasattr(chunk, 'generated_text'):
                    yield chunk.generated_text
                elif isinstance(chunk, str):
                    yield chunk
                elif isinstance(chunk, dict) and 'generated_text' in chunk:
                    yield chunk['generated_text']
                    
        except Exception as e:
            yield f"Error: {str(e)}"


def client_from_env() -> WatsonxClient:
    """Construct a WatsonxClient from environment variables."""
    return WatsonxClient()


# Global instance
# Initialize WatsonX client lazily to avoid connection issues during import
watsonx_client = None

def get_watsonx_client():
    """Get or create WatsonX client instance."""
    global watsonx_client
    if watsonx_client is None:
        watsonx_client = client_from_env()
    return watsonx_client
