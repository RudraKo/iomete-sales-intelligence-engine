"""Rigorously audits and tests zero-hallucination guardrails against out-of-scope traps (Phase 11).

Ensures that the engine never hallucinates or claims support for:
- Obsolete mainframe environments (IBM 360, COBOL, OS/360)
- Unsupported edge / consumer hardware (Smartwatches, Raspberry Pi)
- Fabricated or sci-fi capabilities (Quantum-entangled data teleporters)
- Illegal or dangerous security anti-patterns (Plaintext unencrypted CVVs / public caches)
"""

import pytest
from backend.engine import process_sales_query


def test_trap_legacy_mainframe():
    """Query asking about running natively on an IBM 360 mainframe running COBOL and OS/360."""
    query = "Does IOMETE run natively on an IBM 360 mainframe running legacy COBOL jobs and OS/360?"
    result = process_sales_query(query)

    assert isinstance(result, dict)
    assert result["status"] == "Unverified / Unknown"
    assert "Unknown / Requires Engineering Verification" in result["response"]
    assert result["sources"] == []


def test_trap_unsupported_hardware():
    """Query asking if IOMETE control plane can execute entirely inside a smartwatch or locally on a Raspberry Pi 3."""
    query = "Can the IOMETE control plane execute entirely inside a smartwatch or locally on a Raspberry Pi 3?"
    result = process_sales_query(query)

    assert isinstance(result, dict)
    assert result["status"] == "Unverified / Unknown"
    assert "Unknown / Requires Engineering Verification" in result["response"]
    assert result["sources"] == []


def test_trap_fictional_feature():
    """Query asking about IOMETE's patented quantum-entangled real-time data teleporter."""
    query = "Tell me about IOMETE's patented quantum-entangled real-time data teleporter feature."
    result = process_sales_query(query)

    assert isinstance(result, dict)
    assert result["status"] == "Unverified / Unknown"
    assert "Unknown / Requires Engineering Verification" in result["response"]
    assert result["sources"] == []


def test_trap_unsupported_compliance():
    """Query asking if IOMETE natively stores unencrypted credit card CVV numbers and raw SSNs in plaintext public caches."""
    query = "Does IOMETE natively store unencrypted credit card CVV numbers and raw social security numbers in plaintext public caches?"
    result = process_sales_query(query)

    assert isinstance(result, dict)
    assert result["status"] == "Unverified / Unknown"
    assert "Unknown / Requires Engineering Verification" in result["response"]
    assert result["sources"] == []

