from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Optional, TypedDict

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from dotenv import load_dotenv


class GenerationResult(TypedDict, total=False):
    answer: str
    raw: Any
    meta: dict[str, Any]


def load_env(path: Optional[str] = None) -> None:
    """Load environment variables from a .env file if present."""
    load_dotenv(dotenv_path=path, override=False)


@dataclass
class WatsonxClient:
    """Thin client for IBM watsonx.ai text generation.

    Attributes are minimal and safe to log, except api_key which should never be logged.
    """

    url: str
    api_key: str
    project_id: str
    space_id: Optional[str] = None
    timeout_s: float = 30.0
    max_retries: int = 3

    def _build_api(self) -> tuple[APIClient, dict[str, Any]]:
        creds = Credentials(url=self.url, api_key=self.api_key)
        client = APIClient(credentials=creds, space_id=self.space_id) if self.space_id else APIClient(credentials=creds)
        meta: dict[str, Any] = {"url": self.url, "project_id": self.project_id}
        if self.space_id:
            meta["space_id"] = self.space_id
        return client, meta

    def generate_from_prompt(
        self,
        prompt_text: str,
        model_id: str,
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

        model = ModelInference(model_id=model_id, api_client=client, project_id=self.project_id)

        last_err: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                # The SDK returns either a string or a dict depending on version/config
                raw = model.generate_text(prompt=prompt_text, params=params, request_timeout=self.timeout_s)
                answer = raw if isinstance(raw, str) else raw.get("generated_text") or raw
                return GenerationResult(answer=str(answer), raw=raw, meta={"model_id": model_id, **meta, "params": {"max_new_tokens": max_new_tokens, "temperature": temperature, "decoding_method": decoding_method}})
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                if attempt == self.max_retries:
                    break
                time.sleep(min(2 ** (attempt - 1), 5))

        return GenerationResult(answer="", raw={"error": str(last_err)}, meta={"model_id": model_id, **meta, "error": True})


def client_from_env() -> WatsonxClient:
    """Construct a WatsonxClient from environment variables.

    Required env vars: IBM_URL, IBM_API_KEY, IBM_PROJECT_ID. Optional: SPACE_ID.
    """
    load_env()
    url = os.environ.get("IBM_URL", "").strip()
    api_key = os.environ.get("IBM_API_KEY", "").strip()
    project_id = os.environ.get("IBM_PROJECT_ID", "").strip()
    space_id = os.environ.get("SPACE_ID", "").strip() or None
    if not (url and api_key and project_id):
        raise RuntimeError("Missing IBM_URL, IBM_API_KEY, or IBM_PROJECT_ID in environment")
    return WatsonxClient(url=url, api_key=api_key, project_id=project_id, space_id=space_id)



