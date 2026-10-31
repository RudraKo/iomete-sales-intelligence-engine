"""Core Retrieval Module for IOMETE Sales Intelligence Engine.

Reads processed knowledge chunks from /data/processed_knowledge.json and provides
semantic & keyword ranking for incoming sales queries, objections, and technical prompts.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed_knowledge.json")

# Standard query stop words to avoid noise in keyword matching
STOP_WORDS = {
    "the", "and", "are", "into", "too", "with", "for", "from", "that", "this",
    "our", "you", "your", "can", "will", "all", "why", "what", "how", "who",
    "when", "does", "have", "has", "been", "was", "were", "about", "would",
    "should", "their", "them", "then", "there", "they", "we", "us", "is", "it"
}


def load_knowledge_chunks(data_path: str = DATA_PATH) -> List[Dict[str, Any]]:
    """Loads processed knowledge chunks from JSON, triggering ingestion if not found."""
    if not os.path.exists(data_path):
        logger.warning(f"{data_path} not found. Triggering automated ingestion.")
        from backend.ingest import ingest
        return ingest(output_file=data_path)

    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_query_tokens(query: str) -> List[str]:
    """Cleans and extracts meaningful terms from a query string."""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', query.lower())
    return [t.strip() for t in cleaned.split() if len(t.strip()) > 2 and t.strip() not in STOP_WORDS]


def score_chunk(query_tokens: List[str], chunk: Dict[str, Any], query_raw: str) -> float:
    """Calculates relevance score for a chunk against query tokens and intent."""
    if not query_tokens:
        return 0.0

    score = 0.0
    title_lower = chunk.get("title", "").lower()
    content_lower = chunk.get("content", "").lower()
    tags = [t.lower() for t in chunk.get("tags", [])]
    category_lower = chunk.get("category", "").lower()

    # Category intent bonus
    query_raw_lower = query_raw.lower()
    if any(k in query_raw_lower for k in ["secure", "security", "egress", "vpc", "air-gap", "compliance", "hipaa", "soc2"]):
        if category_lower == "security":
            score += 4.0
    if any(k in query_raw_lower for k in ["lock-in", "locked", "switch", "alternative", "objection", "cost", "tco", "pricing", "bill"]):
        if category_lower == "sales faqs":
            score += 4.0
    if any(k in query_raw_lower for k in ["spark", "iceberg", "compute", "storage", "table", "kubernetes", "k8s"]):
        if category_lower == "core stack":
            score += 4.0

    for token in query_tokens:
        # Tag matches (highest value indicator)
        if any(token == tag or token in tag for tag in tags):
            score += 5.0

        # Title match
        if token in title_lower:
            score += 4.0

        # Content match
        if token in content_lower:
            # Add up to 3 occurrences
            count = content_lower.count(token)
            score += min(count, 3) * 1.5

    return score


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 3,
    data_path: str = DATA_PATH,
    category_filter: Optional[str] = None,
    min_score_threshold: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Retrieves the top_k most relevant knowledge chunks for a query.

    Args:
        query: Sales objection, question, or technical topic.
        top_k: Number of chunks to return (default 3).
        data_path: Path to processed_knowledge.json.
        category_filter: Optional filter by category (Architecture, Core Stack, Security, Sales FAQs).
        min_score_threshold: Minimum score required for a chunk to be considered relevant.

    Returns:
        List of top matching chunk dictionaries including relevance score.
    """
    chunks = load_knowledge_chunks(data_path)
    if not chunks or not query.strip():
        return []

    tokens = clean_query_tokens(query)
    scored_chunks = []

    for chunk in chunks:
        if category_filter and chunk.get("category", "").lower() != category_filter.lower():
            continue

        score = score_chunk(tokens, chunk, query)
        if score >= min_score_threshold:
            scored_chunk = dict(chunk)
            scored_chunk["relevance_score"] = round(score, 2)
            scored_chunks.append(scored_chunk)

    # Sort descending by relevance score
    scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored_chunks[:top_k]

