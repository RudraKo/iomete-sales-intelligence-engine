"""Pydantic models and data structures for The Living Sales Intelligence Engine."""

from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class KnowledgeSnippet(BaseModel):
    id: str
    title: str
    category: str = Field(..., description="Category: architecture, security, compute_storage, competitor_comparison, winning_call, tco_pricing")
    content: str
    tags: List[str] = Field(default_factory=list)
    source: str = Field(..., description="Source doc name, PR, or internal battlecard link")
    verified: bool = True
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SnippetCreateRequest(BaseModel):
    title: str
    category: str
    content: str
    tags: List[str] = Field(default_factory=list)
    source: str


class SnippetSearchQuery(BaseModel):
    query: str
    category: Optional[str] = None
    limit: int = 5


class CallPrepRequest(BaseModel):
    prospect_name: str
    industry: str
    current_stack: str
    key_pain_points: List[str]
    target_personas: List[str] = Field(default_factory=list)


class CallPrepResponse(BaseModel):
    prospect_name: str
    industry: str
    current_stack: str
    architecture_fit: str
    verified_value_drivers: List[str]
    role_discovery_questions: Dict[str, List[str]]
    strict_landmines: List[str]
    citations: List[Dict[str, str]]
    confidence_score: float
    unverified_flags: List[str]
    grounding_status: str


class ObjectionInversionRequest(BaseModel):
    objection_text: str
    competitor: Optional[str] = None
    prospect_context: Optional[str] = None


class ObjectionInversionResponse(BaseModel):
    original_objection: str
    is_verified: bool
    grounding_status: str
    acknowledgment: str
    inversion_thesis: str
    verified_technical_grounding: str
    battle_tested_talk_track: str
    citations: List[Dict[str, str]]
    unverified_note: Optional[str] = None


class ProposalMemoRequest(BaseModel):
    prospect_name: str
    sponsor_name: str
    sponsor_title: str
    current_stack: str
    primary_initiatives: List[str]
    discovery_notes: str


class ProposalMemoResponse(BaseModel):
    prospect_name: str
    sponsor_name: str
    sponsor_title: str
    executive_summary: str
    problem_statement: str
    proposed_solution_architecture: str
    migration_and_interoperability: str
    tco_analysis_matrix: Dict[str, Any]
    next_steps_poc_plan: List[str]
    citations: List[Dict[str, str]]
    unverified_flags: List[str]
    grounding_status: str


class VerificationResult(BaseModel):
    is_fully_grounded: bool
    supported_claims: List[str]
    unsupported_claims: List[str]
    confidence_score: float
    citations: List[Dict[str, str]]
    fallback_applied: bool
    status_message: str

