"""Knowledge Ingestion Pipeline for IOMETE Sales Intelligence Engine.

Parses structured markdown (/data/iomte_knowledge_base.md), semantically chunks
the documentation across Architecture, Core Stack, Security, and Sales FAQs,
and produces /data/processed_knowledge.json with rich metadata tags.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Default file paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "iomte_knowledge_base.md")
DEFAULT_OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "processed_knowledge.json")


def categorize_title(title: str, parent_heading: str = "") -> str:
    """Classifies a title/heading into one of the core semantic categories."""
    combined = f"{parent_heading} {title}".lower()

    if any(k in combined for k in ["faq", "objection", "friction", "buying", "sales", "cost", "tco", "pricing"]):
        return "Sales FAQs"
    elif any(k in combined for k in ["security", "sovereign", "governance", "compliance", "egress", "vpc", "masking", "rbac", "isolation", "data plane", "control plane"]):
        return "Security"
    elif any(k in combined for k in ["stack", "spark", "iceberg", "kubernetes", "k8s", "engine", "format"]):
        return "Core Stack"
    elif any(k in combined for k in ["architecture", "overview", "what is", "lakehouse"]):
        return "Architecture"
    
    return "Architecture"


def extract_tags(title: str, content: str) -> List[str]:
    """Generates relevant tags based on content analysis."""
    text = f"{title} {content}".lower()
    tag_candidates = [
        ("sovereign", "sovereignty"),
        ("spark", "spark"),
        ("iceberg", "iceberg"),
        ("kubernetes", "kubernetes"),
        ("k8s", "kubernetes"),
        ("vpc", "vpc"),
        ("security", "security"),
        ("rbac", "rbac"),
        ("tco", "tco"),
        ("pricing", "pricing"),
        ("cost", "cost-savings"),
        ("snowflake", "snowflake"),
        ("databricks", "databricks"),
        ("aws", "aws"),
        ("azure", "azure"),
        ("gcp", "gcp"),
        ("acid", "acid"),
        ("lock-in", "vendor-lockin"),
        ("egress", "data-egress"),
        ("air-gapped", "air-gap"),
        ("aqe", "aqe"),
    ]
    tags = set()
    for keyword, tag in tag_candidates:
        if keyword in text:
            tags.add(tag)
    return sorted(list(tags))


def parse_markdown_to_chunks(markdown_text: str, source_doc: str = "iomte_knowledge_base.md") -> List[Dict[str, Any]]:
    """
    Parses structured markdown into semantic blocks by H2 and H3 headings.
    Ensures subsections (like individual objections or stack components) are cleanly extracted.
    """
    lines = markdown_text.splitlines()
    chunks: List[Dict[str, Any]] = []

    current_h2 = ""
    current_title = ""
    current_content_lines: List[str] = []
    chunk_counter = 1

    def commit_chunk():
        nonlocal chunk_counter, current_title, current_content_lines, current_h2
        content = "\n".join(current_content_lines).strip()
        if content and current_title:
            category = categorize_title(current_title, current_h2)
            tags = extract_tags(current_title, content)
            
            chunk_id = f"iomete-chunk-{chunk_counter:03d}"
            chunks.append({
                "id": chunk_id,
                "category": category,
                "title": current_title,
                "parent_section": current_h2 or current_title,
                "content": content,
                "tags": tags,
                "source": source_doc
            })
            chunk_counter += 1
        current_content_lines = []

    for line in lines:
        stripped = line.strip()

        # Handle H1 (Document Header)
        if stripped.startswith("# ") and not stripped.startswith("## "):
            continue

        # Handle H2 (Major Sections)
        if stripped.startswith("## "):
            commit_chunk()
            heading_text = stripped.lstrip("#").strip()
            # Remove leading number prefixes e.g. "1. Overview: "
            cleaned_heading = re.sub(r'^\d+\.\s*', '', heading_text)
            current_h2 = cleaned_heading
            current_title = cleaned_heading
            continue

        # Handle H3 (Subsections e.g. Apache Spark, Objection 1)
        if stripped.startswith("### "):
            commit_chunk()
            subheading_text = stripped.lstrip("#").strip()
            current_title = subheading_text
            continue

        # Skip horizontal dividers
        if stripped == "---":
            continue

        current_content_lines.append(line)

    # Commit any trailing block
    commit_chunk()

    return chunks


def ingest(input_file: str = DEFAULT_INPUT_FILE, output_file: str = DEFAULT_OUTPUT_FILE) -> List[Dict[str, Any]]:
    """
    Executes the ingestion pipeline:
    1. Reads the markdown source file.
    2. Chunks by semantic sections.
    3. Writes structured JSON to output_file.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input knowledge base file not found at: {input_file}")

    logger.info(f"Reading knowledge base from: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    chunks = parse_markdown_to_chunks(markdown_text, source_doc=os.path.basename(input_file))
    logger.info(f"Successfully parsed {len(chunks)} semantic chunks.")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved processed knowledge chunks to: {output_file}")
    return chunks


if __name__ == "__main__":
    ingest()
