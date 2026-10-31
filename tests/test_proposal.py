"""Unit tests for Proposal Generator and Deal Risk Assessor (Phase 5 & 6)."""

import pytest
from backend.engine import assess_deal_risks, generate_executive_proposal


def test_assess_deal_risks_banking_fintech():
    """Verifies that high-risk compliance and data residency threats are identified for banking/fintech."""
    company = "HDFC Bank"
    industry = "Fintech / Banking"
    objections = [
        "Security & Strict Data Egress / Air-Gapped VPC",
        "Vendor Lock-in (Snowflake / AWS proprietary formats)"
    ]

    risks = assess_deal_risks(company, industry, objections)

    assert len(risks) >= 3
    categories = [r["risk_category"] for r in risks]

    assert "Data Sovereignty & Regulatory Compliance" in categories
    assert "Vendor Lock-in & Storage Portability" in categories
    assert "Pipeline Migration & Dashboard Downtime" in categories

    # Verify severity and mitigation
    sovereignty_risk = next(r for r in risks if r["risk_category"] == "Data Sovereignty & Regulatory Compliance")
    assert sovereignty_risk["severity"] == "HIGH"
    assert "VPC" in sovereignty_risk["iomete_mitigation"]
    assert "KMS" in sovereignty_risk["iomete_mitigation"]


def test_assess_deal_risks_diy_and_cost():
    """Verifies operational drag and spend volatility risks are detected."""
    risks = assess_deal_risks(
        company_name="Acme Corp",
        industry="Retail",
        selected_objections=["Open Source DIY Overhead vs Managed Platform", "TCO & Exploding Compute Bills"]
    )

    categories = [r["risk_category"] for r in risks]
    assert "Day-90 Platform Engineering Overhead" in categories
    assert "Unpredictable Warehouse Spend" in categories


def test_generate_executive_proposal_structure():
    """Verifies the complete structure and markdown sections of the generated executive proposal."""
    company = "HDFC Bank"
    industry = "Fintech / Banking"
    objections = [
        "Vendor Lock-in (Snowflake / AWS proprietary formats)",
        "Security & Strict Data Egress / Air-Gapped VPC"
    ]

    result = generate_executive_proposal(company, industry, objections)

    # Check required dictionary keys
    assert isinstance(result, dict)
    assert "company_name" in result
    assert "industry" in result
    assert "proposal_markdown" in result
    assert "risk_assessment" in result
    assert "sources" in result
    assert "status" in result

    assert result["company_name"] == "HDFC Bank"
    assert result["industry"] == "Fintech / Banking"
    assert result["status"] == "Verified"
    assert len(result["sources"]) > 0
    assert len(result["risk_assessment"]) > 0

    # Check key sections in proposal markdown
    md = result["proposal_markdown"]
    assert "# Executive Briefing & Architecture Recommendation" in md
    assert "Target Enterprise**: HDFC Bank" in md
    assert "## 1. Executive Summary" in md
    assert "## 2. Proposed Solution Architecture: Sovereign Lakehouse" in md
    assert "## 3. Addressed Buying Concerns & Technical Inversions" in md
    assert "## 4. Deal Risk Assessment & Architectural Mitigations" in md
    assert "## 5. Verified TCO Impact Analysis" in md
    assert "## 6. Recommended 4-Week Proof of Concept (POC) Plan" in md
    assert "## 7. Authoritative Knowledge Provenance" in md
    assert "70% to 80%" in md
    assert "Apache Iceberg" in md
    assert "Apache Spark" in md


def test_generate_executive_proposal_empty_objections():
    """Verifies that an empty objection list falls back gracefully with default Lakehouse pillars."""
    result = generate_executive_proposal("OmniTrack", "SaaS Analytics", [])

    assert result["status"] == "Verified"
    assert result["company_name"] == "OmniTrack"
    assert len(result["sources"]) > 0
    assert "Sovereign Lakehouse" in result["proposal_markdown"]

