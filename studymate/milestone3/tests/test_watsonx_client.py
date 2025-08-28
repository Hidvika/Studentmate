from __future__ import annotations

from unittest.mock import MagicMock, patch

from studymate.milestone3.src.watsonx_client import WatsonxClient


@patch("studymate.milestone3.src.watsonx_client.ModelInference")
@patch("studymate.milestone3.src.watsonx_client.APIClient")
@patch("studymate.milestone3.src.watsonx_client.Credentials")
def test_generate_params_passed(mock_creds, mock_api, mock_model):
    client = WatsonxClient(url="u", api_key="k", project_id="p")
    model_instance = MagicMock()
    model_instance.generate_text.return_value = {"generated_text": "ok"}
    mock_model.return_value = model_instance

    res = client.generate_from_prompt("hello", model_id="m", max_new_tokens=123, temperature=0.7, decoding_method="greedy")
    assert res["answer"] == "ok"
    # Check generate_text called with params containing our values
    kwargs = model_instance.generate_text.call_args.kwargs
    params = kwargs["params"]
    assert params["max_new_tokens"] == 123
    assert params["temperature"] == 0.7


@patch("studymate.milestone3.src.watsonx_client.ModelInference")
@patch("studymate.milestone3.src.watsonx_client.APIClient")
@patch("studymate.milestone3.src.watsonx_client.Credentials")
def test_errors_return_empty_answer(mock_creds, mock_api, mock_model):
    client = WatsonxClient(url="u", api_key="k", project_id="p", max_retries=1)
    model_instance = MagicMock()
    model_instance.generate_text.side_effect = RuntimeError("boom")
    mock_model.return_value = model_instance

    res = client.generate_from_prompt("hello", model_id="m")
    assert res["answer"] == ""
    assert "error" in res["raw"]



