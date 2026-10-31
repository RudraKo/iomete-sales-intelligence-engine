"""Unit tests for utils/groq_client.py (Phase 1)."""

import pytest
from unittest.mock import MagicMock, patch
from utils.groq_client import (
    GroqLLMClient,
    STRICT_IOMETE_SYSTEM_PROMPT,
    DEFAULT_MODEL,
    generate_grounded_response
)


def test_groq_client_requires_api_key():
    client = GroqLLMClient(api_key=None)
    with patch.dict("os.environ", {}, clear=True):
        client.api_key = None
        with pytest.raises(ValueError, match="GROQ_API_KEY is not set"):
            client._get_client()


def test_strict_system_prompt_contains_pillars():
    assert "SOVEREIGN DEPLOYMENT" in STRICT_IOMETE_SYSTEM_PROMPT
    assert "APACHE SPARK COMPUTE" in STRICT_IOMETE_SYSTEM_PROMPT
    assert "APACHE ICEBERG STORAGE" in STRICT_IOMETE_SYSTEM_PROMPT
    assert "KUBERNETES-NATIVE" in STRICT_IOMETE_SYSTEM_PROMPT
    assert "Unknown / Requires Engineering Verification" in STRICT_IOMETE_SYSTEM_PROMPT


def test_groq_client_generation_mock():
    mock_groq_instance = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "IOMETE is a sovereign lakehouse built on Apache Spark and Iceberg."
    mock_completion.choices = [mock_choice]
    mock_groq_instance.chat.completions.create.return_value = mock_completion

    client = GroqLLMClient(api_key="mock_groq_test_key", model="llama-3.3-70b-versatile")
    client._client = mock_groq_instance

    result = client.generate(
        prompt="Explain IOMETE architecture",
        context="Data plane runs in customer VPC."
    )

    assert result == "IOMETE is a sovereign lakehouse built on Apache Spark and Iceberg."
    assert mock_groq_instance.chat.completions.create.called
    call_args = mock_groq_instance.chat.completions.create.call_args[1]
    assert call_args["model"] == "llama-3.3-70b-versatile"
    assert len(call_args["messages"]) == 2
    assert call_args["messages"][0]["role"] == "system"
    assert "Data plane runs in customer VPC." in call_args["messages"][1]["content"]

