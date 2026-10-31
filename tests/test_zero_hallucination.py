"""Tests verifying Core Pillar #1: ZERO HALLUCINATION ACCURACY.

Verifies:
- Documented facts regarding IOMETE pass grounding checks.
- Hallucination traps and unsupported assertions explicitly return "Unknown / Requires Engineering Verification".
"""

import pytest
import os
import tempfile
from app.core.ledger import LivingLedger
from app.core.verifier import ZeroHallucinationVerifier
from app.core.synthesis import SalesIntelligenceEngine
from app.core.models import ObjectionInversionRequest


@pytest.fixture
def test_engine():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db = f.name
    ledger = LivingLedger(db_path=temp_db)
    verifier = ZeroHallucinationVerifier()
    engine = SalesIntelligenceEngine(ledger=ledger, verifier=verifier)
    yield engine, ledger, verifier
    if os.path.exists(temp_db):
        os.remove(temp_db)


def test_grounded_objection_passes(test_engine):
    engine, _, _ = test_engine
    req = ObjectionInversionRequest(
        objection_text="How can we guarantee our data never leaves our private cloud VPC?",
        competitor="General"
    )
    resp = engine.generate_objection_inversion(req)

    assert resp.is_verified is True
    assert "Verified Grounded" in resp.grounding_status
    assert "data plane" in resp.verified_technical_grounding.lower()
    assert len(resp.citations) > 0


def test_unsupported_trap_triggers_unknown(test_engine):
    engine, _, _ = test_engine
    # Query asking about Windows 95 and storing credit cards on IOMETE servers
    req = ObjectionInversionRequest(
        objection_text="Can IOMETE run on Windows 95 and store customer credit cards on your own servers?",
        competitor="None"
    )
    resp = engine.generate_objection_inversion(req)

    # Core non-negotiable constraint: MUST return "Unknown / Requires Engineering Verification"
    assert resp.is_verified is False
    assert "Unknown / Requires Engineering Verification" in resp.grounding_status
    assert "Unknown / Requires Engineering Verification" in resp.inversion_thesis
    assert resp.unverified_note is not None
    assert "Unknown / Requires Engineering Verification" in resp.unverified_note


def test_unsupported_domain_audit(test_engine):
    _, _, verifier = test_engine
    # Auditing an unsupported claim
    claim = "IOMETE runs a proprietary blockchain storage network on custom ASIC hardware."
    result = verifier.audit_generated_text(claim, [])

    assert result.is_fully_grounded is False
    assert result.status_message == "Unknown / Requires Engineering Verification"
    assert result.fallback_applied is True

