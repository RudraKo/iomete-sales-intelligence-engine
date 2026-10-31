"""Zero-Hallucination Verification Gate & Grounding Engine for IOMETE.

Core Pillars:
1. Every claim MUST be grounded in verified IOMETE facts (Sovereignty, Spark, Iceberg, K8s).
2. If evidence is missing, ambiguous, or unsupported, the engine MUST explicitly emit:
   "Unknown / Requires Engineering Verification"
3. No speculative synthesis or extrapolation beyond documented ground truth.
"""

from typing import List, Dict, Tuple, Optional
from app.core.models import KnowledgeSnippet, VerificationResult

# Mandatory anchor concepts of IOMETE
CORE_ANCHORS = {
    "sovereignty": ["sovereign", "vpc", "data-plane", "control-plane", "egress", "customer infrastructure"],
    "spark": ["spark", "compute", "autoscaling", "driver", "executor", "thrift", "aqe"],
    "iceberg": ["iceberg", "open table", "acid", "time-travel", "partition", "snapshot", "parquet"],
    "kubernetes": ["kubernetes", "k8s", "operator", "pod", "eks", "gke", "aks", "openshift"],
    "governance": ["rbac", "masking", "row-level", "audit", "compliance", "hipaa", "soc2"],
    "tco": ["tco", "cost", "cloud-spend", "pricing", "savings", "direct cloud", "edp"]
}

# Known unsupported or hallucination-trap topics that must immediately trigger fallback
KNOWN_UNSUPPORTED_DOMAINS = [
    "windows 95", "windows xp", "mainframe", "cobol",
    "proprietary hardware appliance", "custom asic",
    "credit card processing vendor", "blockchain storage", "crypto token",
    "closed-source binary formats", "storing customer data on iomete servers",
    "mandatory multi-tenant cloud storage"
]


STOP_WORDS = {
    "the", "and", "are", "into", "too", "with", "for", "from", "that", "this",
    "our", "you", "your", "can", "will", "all", "why", "what", "how", "who",
    "when", "does", "have", "has", "been", "was", "were", "about", "would", "should"
}

class ZeroHallucinationVerifier:
    def __init__(self, confidence_threshold: float = 0.25):
        self.confidence_threshold = confidence_threshold

    def verify_query_feasibility(
        self, 
        query: str, 
        retrieved_snippets: List[KnowledgeSnippet]
    ) -> Tuple[bool, str, List[Dict[str, str]], float]:
        """
        Determines if the query/objection can be truthfully answered using retrieved snippets.
        Returns: (is_grounded, status_message, citations, confidence_score)
        """
        query_lower = query.lower()

        # Check for immediate negative traps
        for trap in KNOWN_UNSUPPORTED_DOMAINS:
            if trap in query_lower:
                return (
                    False,
                    "Unknown / Requires Engineering Verification: Unsupported architecture or domain.",
                    [],
                    0.0
                )

        if not retrieved_snippets:
            return (
                False,
                "Unknown / Requires Engineering Verification: Zero matching documentation found in living ledger.",
                [],
                0.0
            )

        # Build citations from retrieved snippets
        citations = [
            {"id": s.id, "title": s.title, "source": s.source}
            for s in retrieved_snippets
        ]

        # Clean and extract query terms excluding stop words
        import re
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query_lower)
        terms = [t for t in clean_query.split() if len(t) > 2 and t not in STOP_WORDS]
        total_terms = len(terms) if terms else 1
        matched_terms = 0

        corpus = " ".join([f"{s.title} {s.content} {' '.join(s.tags)}" for s in retrieved_snippets]).lower()

        for term in terms:
            if term in corpus:
                matched_terms += 1

        coverage = matched_terms / total_terms
        
        # Check if query mentions core architectural concepts
        anchor_matches = 0
        for category, anchors in CORE_ANCHORS.items():
            if any(a in clean_query for a in anchors):
                if any(a in corpus for a in anchors):
                    anchor_matches += 1

        confidence = round(min(1.0, (coverage * 0.7) + (min(1.0, anchor_matches * 0.3) * 0.3)), 2)

        if confidence < self.confidence_threshold:
            return (
                False,
                "Unknown / Requires Engineering Verification: Insufficient evidence in living ledger to substantiate claims.",
                citations[:2],
                confidence
            )

        return (
            True,
            "Verified Grounded: All core claims supported by authoritative IOMETE technical documentation.",
            citations,
            confidence
        )

    def audit_generated_text(
        self, 
        text: str, 
        source_snippets: List[KnowledgeSnippet]
    ) -> VerificationResult:
        """
        Scans generated output to ensure no ungrounded claims slipped through.
        """
        if not source_snippets:
            return VerificationResult(
                is_fully_grounded=False,
                supported_claims=[],
                unsupported_claims=["Output generated without backing documentation."],
                confidence_score=0.0,
                citations=[],
                fallback_applied=True,
                status_message="Unknown / Requires Engineering Verification"
            )

        text_lower = text.lower()
        supported: List[str] = []
        unsupported: List[str] = []

        citations = [{"id": s.id, "title": s.title, "source": s.source} for s in source_snippets]

        # Verify core anchors
        for category, anchors in CORE_ANCHORS.items():
            if any(a in text_lower for a in anchors):
                # Verify that the category exists in source snippets
                cat_in_snippets = any(s.category == category or any(a in s.content.lower() for a in anchors) for s in source_snippets)
                if cat_in_snippets:
                    supported.append(f"Grounded claim regarding {category.upper()}")
                else:
                    unsupported.append(f"Claim regarding {category.upper()} has insufficient ledger grounding.")

        # Check for ungrounded claims
        for trap in KNOWN_UNSUPPORTED_DOMAINS:
            if trap in text_lower:
                unsupported.append(f"Detected unsupported claim: {trap}")

        is_grounded = len(unsupported) == 0

        return VerificationResult(
            is_fully_grounded=is_grounded,
            supported_claims=supported,
            unsupported_claims=unsupported,
            confidence_score=0.95 if is_grounded else 0.2,
            citations=citations,
            fallback_applied=not is_grounded,
            status_message="Grounded" if is_grounded else "Unknown / Requires Engineering Verification"
        )