"""Comprehensive tests for Retrieval and Engine modules (Phase 3)."""

import pytest
from unittest.mock import MagicMock
from backend.retrieval import retrieve_relevant_chunks, clean_query_tokens, score_chunk
from backend.engine import process_sales_query
from utils.groq_client import GroqLLMClient


# -------------------------------------------------------------
# 1. RETRIEVAL TESTS
# -------------------------------------------------------------

def test_clean_query_tokens():
    tokens = clean_query_tokens("Our security team won't allow data leaving our VPC!")
    assert "security" in tokens
    assert "data" in tokens
    assert "leaving" in tokens
    assert "vpc" in tokens
    assert "our" not in tokens  # Stop word removed


def test_retrieval_vendor_lockin():
    query = "We are locked into Snowflake, switching is too risky and costly."
    chunks = retrieve_relevant_chunks(query, top_k=3)

    assert len(chunks) > 0
    assert len(chunks) <= 3

    # Verify that at least one chunk specifically addresses lock-in or open Iceberg
    titles_and_tags = " ".join([c["title"] + " " + " ".join(c.get("tags", [])) for c in chunks]).lower()
    assert "lock" in titles_and_tags or "iceberg" in titles_and_tags or "snowflake" in titles_and_tags


def test_retrieval_security_data_egress():
    query = "Our security team won't allow external data egress outside our VPC."
    chunks = retrieve_relevant_chunks(query, top_k=3)

    assert len(chunks) > 0
    top_chunk = chunks[0]
    
    # Highest scoring chunk should be security / VPC / egress related
    assert top_chunk["category"] in ["Security", "Sales FAQs"]
    all_content = " ".join([c["content"].lower() for c in chunks])
    assert "vpc" in all_content or "egress" in all_content or "sovereign" in all_content


def test_retrieval_tco_pricing():
    query = "How does TCO and pricing compare to traditional warehouses like Snowflake?"
    chunks = retrieve_relevant_chunks(query, top_k=3)

    assert len(chunks) > 0
    titles = [c["title"].lower() for c in chunks]
    assert any("tco" in t or "cost" in t or "pricing" in t or "infrastructure" in t for t in titles)


# -------------------------------------------------------------
# 2. SALES ENGINE TESTS
# -------------------------------------------------------------

def test_process_sales_query_grounded_structured_output():
    query = "How does IOMETE prevent vendor lock-in with Apache Iceberg?"
    result = process_sales_query(query)

    # Must contain required keys
    assert isinstance(result, dict)
    assert "response" in result
    assert "sources" in result
    assert "status" in result

    assert result["status"] == "Verified"
    assert len(result["sources"]) > 0
    assert len(result["response"]) > 50

    # Ensure source metadata is present
    for src in result["sources"]:
        assert "id" in src
        assert "title" in src
        assert "category" in src
        assert "source" in src


def test_process_sales_query_with_mocked_groq():
    mock_client = MagicMock(spec=GroqLLMClient)
    mock_client.generate.return_value = (
        "1. Empathetic Acknowledgment: We understand vendor lock-in fears.\n"
        "2. Inversion Thesis: IOMETE is built on 100% open Apache Iceberg.\n"
        "3. Verified Grounding: Your data remains in your S3/GCS bucket.\n"
        "4. Talk Track: You own your data forever with zero lock-in."
    )

    query = "We are worried about vendor lock-in."
    result = process_sales_query(query, client=mock_client)

    assert result["status"] == "Verified"
    assert "Apache Iceberg" in result["response"]
    assert len(result["sources"]) > 0
    assert mock_client.generate.called


def test_process_sales_query_handles_unsupported_claims_safely():
    # Hallucination trap query
    unsupported_query = "Can IOMETE run on Windows 95 and store customer credit cards on external servers?"
    result = process_sales_query(unsupported_query)

    assert isinstance(result, dict)
    assert result["status"] == "Unverified / Unknown"
    assert "Unknown / Requires Engineering Verification" in result["response"]
    assert result["sources"] == []


def test_process_sales_query_empty_input():
    result = process_sales_query("   ")
    assert result["status"] == "Unverified / Unknown"
    assert "Empty query" in result["response"]

