"""Unit tests for the Knowledge Ingestion Pipeline (/backend/ingest.py)."""

import os
import json
import tempfile
import pytest
from backend.ingest import ingest, parse_markdown_to_chunks, categorize_title, extract_tags


@pytest.fixture
def sample_markdown():
    return """# Test IOMETE Document

## 1. Overview: What is IOMETE?
IOMETE is a sovereign data lakehouse combining Spark and Iceberg.

## 2. Core Stack & Infrastructure

### Apache Spark (Distributed Compute Engine)
Apache Spark provides auto-scaling compute and AQE.

### Apache Iceberg (Open Table Format)
Apache Iceberg provides ACID transactions and zero vendor lock-in.

## 3. Sovereign Deployment Model & Security
Runs 100% inside customer VPC on Kubernetes.

## 4. Enterprise Buying Frictions & Sales FAQs

### Objection 1: "We are locked into AWS/Snowflake."
Open Iceberg tables prevent vendor lock-in.
"""


def test_categorize_title():
    assert categorize_title("Overview: What is IOMETE?") == "Architecture"
    assert categorize_title("Apache Spark (Distributed Compute)") == "Core Stack"
    assert categorize_title("Control Plane vs. Data Plane Isolation") == "Security"
    assert categorize_title('Objection 1: "We are locked into AWS/Snowflake."') == "Sales FAQs"
    assert categorize_title("Total Cost of Ownership (TCO) & Economics") == "Sales FAQs"


def test_extract_tags():
    tags = extract_tags("Apache Spark Engine", "Runs in customer VPC with Iceberg on AWS EKS")
    assert "spark" in tags
    assert "iceberg" in tags
    assert "vpc" in tags
    assert "aws" in tags


def test_parse_markdown_to_chunks(sample_markdown):
    chunks = parse_markdown_to_chunks(sample_markdown, source_doc="test.md")
    assert len(chunks) == 5

    titles = [c["title"] for c in chunks]
    assert "Overview: What is IOMETE?" in titles
    assert "Apache Spark (Distributed Compute Engine)" in titles
    assert "Apache Iceberg (Open Table Format)" in titles
    assert "Sovereign Deployment Model & Security" in titles
    assert 'Objection 1: "We are locked into AWS/Snowflake."' in titles

    for chunk in chunks:
        assert "id" in chunk
        assert "category" in chunk
        assert "title" in chunk
        assert "content" in chunk
        assert "tags" in chunk
        assert chunk["source"] == "test.md"


def test_ingest_live_knowledge_base():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        temp_output = f.name

    try:
        chunks = ingest(output_file=temp_output)
        assert len(chunks) >= 8

        # Verify output JSON exists and is valid
        assert os.path.exists(temp_output)
        with open(temp_output, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == len(chunks)

        categories = {c["category"] for c in data}
        assert "Architecture" in categories
        assert "Core Stack" in categories
        assert "Security" in categories
        assert "Sales FAQs" in categories

        # Verify specific objection handlers
        objection_titles = [c["title"] for c in data if "Objection" in c["title"]]
        assert any("locked into" in t for t in objection_titles)
        assert any("data egress" in t for t in objection_titles)
        assert any("TCO compare" in t for t in objection_titles)

    finally:
        if os.path.exists(temp_output):
            os.remove(temp_output)

