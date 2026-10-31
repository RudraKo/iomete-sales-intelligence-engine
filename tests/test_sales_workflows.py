"""Tests verifying Core Pillar #2: PRACTICAL B2B IMPACT.

Verifies:
- 15-Minute Call Prep Brief Generation
- Objection Inversion Logic (Lock-in, DIY Spark, TCO)
- Proposal Memo & TCO Matrix Generation
"""

import pytest
import os
import tempfile
from app.core.ledger import LivingLedger
from app.core.verifier import ZeroHallucinationVerifier
from app.core.synthesis import SalesIntelligenceEngine
from app.core.models import CallPrepRequest, ObjectionInversionRequest, ProposalMemoRequest


@pytest.fixture
def test_engine():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db = f.name
    ledger = LivingLedger(db_path=temp_db)
    verifier = ZeroHallucinationVerifier()
    engine = SalesIntelligenceEngine(ledger=ledger, verifier=verifier)
    yield engine
    if os.path.exists(temp_db):
        os.remove(temp_db)


def test_15_minute_call_prep_snowflake(test_engine):
    req = CallPrepRequest(
        prospect_name="Apex Payments",
        industry="FinTech",
        current_stack="Snowflake on AWS",
        key_pain_points=["High compute bills", "Data sovereignty compliance", "Vendor lock-in"],
        target_personas=["Chief Security Officer", "VP Data Engineering", "Chief Financial Officer"]
    )
    resp = test_engine.generate_call_prep(req)

    assert resp.prospect_name == "Apex Payments"
    assert "Iceberg" in resp.architecture_fit
    assert "Snowflake" in resp.architecture_fit
    assert len(resp.verified_value_drivers) >= 3
    assert "Chief Security Officer" in resp.role_discovery_questions
    assert "VP Data Engineering" in resp.role_discovery_questions
    assert len(resp.strict_landmines) >= 3
    assert len(resp.citations) > 0


def test_objection_inversion_diy_spark(test_engine):
    req = ObjectionInversionRequest(
        objection_text="Why shouldn't we just deploy open source Apache Spark and Iceberg ourselves on K8s?",
        competitor="DIY Open Source"
    )
    resp = test_engine.generate_objection_inversion(req)

    assert resp.is_verified is True
    assert "compaction" in resp.verified_technical_grounding.lower() or "operational" in resp.inversion_thesis.lower()
    assert len(resp.battle_tested_talk_track) > 50


def test_proposal_memo_generation(test_engine):
    req = ProposalMemoRequest(
        prospect_name="Acme Health",
        sponsor_name="Dr. Aris Vance",
        sponsor_title="Chief Technology Officer",
        current_stack="Snowflake Enterprise",
        primary_initiatives=["Eliminate egress fees", "HIPAA sovereign compliance"],
        discovery_notes="200TB warehouse. Need zero data leaves customer boundary."
    )
    resp = test_engine.generate_proposal_memo(req)

    assert resp.prospect_name == "Acme Health"
    assert resp.sponsor_name == "Dr. Aris Vance"
    assert "tco_analysis_matrix" in resp.model_dump()
    assert len(resp.next_steps_poc_plan) == 4
    assert "Week 1" in resp.next_steps_poc_plan[0]