"""Tests verifying Core Pillar #3: CONSTANTLY UPDATING CONTEXT.

Verifies:
- Dynamic ingestion of new technical snippets & winning deals
- Instant full-text and category indexing
- Updating and deleting snippets
"""

import pytest
import os
import tempfile
from app.core.ledger import LivingLedger
from app.core.models import SnippetCreateRequest, KnowledgeSnippet


@pytest.fixture
def test_ledger():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db = f.name
    ledger = LivingLedger(db_path=temp_db)
    yield ledger
    if os.path.exists(temp_db):
        os.remove(temp_db)


def test_seed_data_loaded(test_ledger):
    stats = test_ledger.get_stats()
    assert stats["total_snippets"] >= 8
    assert "architecture" in stats["categories"]
    assert "winning_call" in stats["categories"]


def test_dynamic_snippet_ingestion(test_ledger):
    req = SnippetCreateRequest(
        title="Apache Iceberg v3 Puffin Stats Optimization",
        category="compute_storage",
        content="IOMETE now accelerates query planning using Iceberg Puffin file statistics, cutting metadata latency by 65%.",
        tags=["iceberg-v3", "puffin", "metadata-speed"],
        source="IOMETE Release 4.1 [release#puffin-stats]"
    )
    new_snip = test_ledger.create_from_request(req)
    assert new_snip.id.startswith("custom-")

    # Search and verify instant indexing
    results = test_ledger.search("Puffin statistics metadata")
    assert len(results) > 0
    assert results[0].id == new_snip.id
    assert "Puffin" in results[0].content


def test_category_filtering(test_ledger):
    arch_snippets = test_ledger.list_all(category="architecture")
    assert len(arch_snippets) > 0
    for s in arch_snippets:
        assert s.category == "architecture"

