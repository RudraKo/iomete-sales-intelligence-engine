"""Unit and component verification tests for /frontend/app.py (Phase 4)."""

import sys
from unittest.mock import MagicMock

# Ensure streamlit can be imported/mocked if still downloading in background
if "streamlit" not in sys.modules:
    try:
        import streamlit
    except ImportError:
        sys.modules["streamlit"] = MagicMock()

import pytest
from unittest.mock import patch
from frontend.app import PRESET_OBJECTIONS, get_system_health, render_response_cards


def test_preset_objections_completeness():
    """Verifies all required demo pill presets are defined and non-empty."""
    required_keys = [
        "Vendor Lock-in",
        "Security & Data Egress",
        "TCO & Pricing vs Snowflake",
        "Open Source vs Managed Platform",
        "Zero-Hallucination Trap Test"
    ]
    for key in required_keys:
        assert key in PRESET_OBJECTIONS
        assert len(PRESET_OBJECTIONS[key]) > 20


def test_get_system_health():
    """Verifies that knowledge base telemetry and chunk counts load accurately."""
    health = get_system_health()
    assert isinstance(health, dict)
    assert health["status"] == "Active"
    assert health["total_chunks"] >= 8
    assert "Architecture" in health["categories"]
    assert "Sales FAQs" in health["categories"]
    assert health["error"] is None


@patch("streamlit.markdown")
@patch("streamlit.code")
@patch("streamlit.expander")
def test_render_response_cards_verified(mock_expander, mock_code, mock_markdown):
    """Verifies UI card rendering for a verified objection inversion."""
    sample_result = {
        "status": "Verified",
        "response": (
            "1. Empathetic Acknowledgment: We understand your concern.\n"
            "2. Inversion Thesis: Iceberg eliminates lock-in.\n"
            "3. Verified Technical Reality: Data stays in your S3 bucket.\n"
            "4. Battle-Tested Talk Track: You own your data 100%."
        ),
        "sources": [
            {
                "id": "iomete-chunk-008",
                "title": "Objection 1: Vendor Lock-in",
                "category": "Sales FAQs",
                "source": "iomte_knowledge_base.md"
            }
        ]
    }

    render_response_cards(sample_result)

    assert mock_markdown.called
    assert mock_code.called
    assert mock_expander.called


@patch("streamlit.markdown")
@patch("streamlit.code")
@patch("streamlit.expander")
@patch("streamlit.warning")
def test_render_response_cards_unverified(mock_warning, mock_expander, mock_code, mock_markdown):
    """Verifies UI card rendering for an unverified/unknown objection."""
    sample_unverified = {
        "status": "Unverified / Unknown",
        "response": "Unknown / Requires Engineering Verification: No documentation supports this.",
        "sources": []
    }

    render_response_cards(sample_unverified)

    assert mock_markdown.called
    assert mock_code.called
    assert mock_expander.called
    assert mock_warning.called
