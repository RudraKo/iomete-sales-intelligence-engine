"""FastAPI Application for The Living Sales Intelligence Engine (IOMETE).

Serves:
- REST API for Sales Briefs, Objection Inversion, Follow-up Memos
- Living Ledger Ingestion and Search
- Zero-Hallucination Audit Endpoint
- Interactive Executive Dashboard
"""

import os
import sqlite3
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.core.models import (
    CallPrepRequest, CallPrepResponse,
    ObjectionInversionRequest, ObjectionInversionResponse,
    ProposalMemoRequest, ProposalMemoResponse,
    SnippetCreateRequest, KnowledgeSnippet,
    VerificationResult
)
from app.core.ledger import LivingLedger
from app.core.verifier import ZeroHallucinationVerifier
from app.core.synthesis import SalesIntelligenceEngine

app = FastAPI(
    title="The Living Sales Intelligence Engine",
    description="Sovereign Data Lakehouse Sales Intelligence for IOMETE",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
DB_PATH = os.getenv("DATABASE_PATH", "data/living_ledger.db")
ledger = LivingLedger(db_path=DB_PATH)
verifier = ZeroHallucinationVerifier()
sales_engine = SalesIntelligenceEngine(ledger=ledger, verifier=verifier)

# Mount Static Files & Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "templates")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Renders the executive sales intelligence dashboard."""
    stats = ledger.get_stats()
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "stats": stats}
    )


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "system": "The Living Sales Intelligence Engine (IOMETE)",
        "version": "1.0.0",
        "zero_hallucination_guard": "ACTIVE"
    }


@app.get("/api/stats")
async def get_stats():
    return ledger.get_stats()


@app.get("/api/snippets", response_model=List[KnowledgeSnippet])
async def list_snippets(
    category: Optional[str] = None, 
    query: Optional[str] = None, 
    limit: int = Query(50, ge=1, le=200)
):
    if query:
        return ledger.search(query=query, category=category, limit=limit)
    return ledger.list_all(category=category, limit=limit)


@app.post("/api/snippets", response_model=KnowledgeSnippet)
async def create_snippet(req: SnippetCreateRequest):
    """Ingests a new technical snippet or winning call resolution into the Living Ledger."""
    return ledger.create_from_request(req)


@app.get("/api/snippets/{snippet_id}", response_model=KnowledgeSnippet)
async def get_snippet(snippet_id: str):
    snippet = ledger.get_by_id(snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found in living ledger")
    return snippet


@app.delete("/api/snippets/{snippet_id}")
async def delete_snippet(snippet_id: str):
    with ledger._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        try:
            cursor.execute("DELETE FROM snippets_fts WHERE id = ?", (snippet_id,))
        except sqlite3.OperationalError:
            pass
        conn.commit()
    return {"status": "deleted", "id": snippet_id}


@app.post("/api/sales/call-prep", response_model=CallPrepResponse)
async def generate_call_prep(req: CallPrepRequest):
    """Generates a verified 15-minute call prep brief for an enterprise sales conversation."""
    return sales_engine.generate_call_prep(req)


@app.post("/api/sales/objection-inversion", response_model=ObjectionInversionResponse)
async def generate_objection_inversion(req: ObjectionInversionRequest):
    """Inverts an enterprise sales objection into an IOMETE architectural advantage."""
    return sales_engine.generate_objection_inversion(req)


@app.post("/api/sales/proposal-memo", response_model=ProposalMemoResponse)
async def generate_proposal_memo(req: ProposalMemoRequest):
    """Synthesizes a structured proposal memo and executive co-existence plan."""
    return sales_engine.generate_proposal_memo(req)


@app.post("/api/verifier/audit", response_model=VerificationResult)
async def audit_claim(text: str = Query(..., description="Sales claim or question to audit")):
    """Audits any statement for zero-hallucination compliance against IOMETE ground truth."""
    retrieved = ledger.search(text, limit=4)
    return verifier.audit_generated_text(text, retrieved)

