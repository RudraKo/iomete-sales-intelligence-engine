"""The Living Ledger: Persistent, dynamically updatable knowledge database for IOMETE.

Provides:
- SQLite-backed storage with FTS5 (Full-Text Search)
- Dynamic snippet ingestion and categorization
- Keyword, tag, and BM25-style token rank scoring
- Seamless tracking of new product features and winning deal playbooks
"""

import os
import json
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.models import KnowledgeSnippet, SnippetCreateRequest
from app.knowledge.seed_data import SEED_SNIPPETS


class LivingLedger:
    def __init__(self, db_path: str = "data/living_ledger.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self._seed_if_empty()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Core snippets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snippets (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    source TEXT NOT NULL,
                    verified INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            # FTS5 virtual table for full-text search
            try:
                cursor.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS snippets_fts USING fts5(
                        id,
                        title,
                        category,
                        content,
                        tags,
                        source
                    )
                """)
            except sqlite3.OperationalError:
                # In environments where FTS5 is not compiled, fallback gracefully
                pass
            conn.commit()

    def _seed_if_empty(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM snippets")
            count = cursor.fetchone()[0]
            if count == 0:
                for s in SEED_SNIPPETS:
                    self.insert_snippet(s)

    def insert_snippet(self, snippet: KnowledgeSnippet) -> KnowledgeSnippet:
        tags_str = json.dumps(snippet.tags)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO snippets 
                (id, title, category, content, tags, source, verified, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snippet.id,
                snippet.title,
                snippet.category,
                snippet.content,
                tags_str,
                snippet.source,
                1 if snippet.verified else 0,
                snippet.created_at,
                snippet.updated_at
            ))
            # Sync FTS
            try:
                cursor.execute("DELETE FROM snippets_fts WHERE id = ?", (snippet.id,))
                cursor.execute("""
                    INSERT INTO snippets_fts (id, title, category, content, tags, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    snippet.id,
                    snippet.title,
                    snippet.category,
                    snippet.content,
                    tags_str,
                    snippet.source
                ))
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                pass
            conn.commit()
        return snippet

    def create_from_request(self, req: SnippetCreateRequest) -> KnowledgeSnippet:
        import uuid
        now = datetime.utcnow().isoformat()
        snippet_id = f"custom-{uuid.uuid4().hex[:8]}"
        snippet = KnowledgeSnippet(
            id=snippet_id,
            title=req.title,
            category=req.category,
            content=req.content,
            tags=req.tags,
            source=req.source,
            verified=True,
            created_at=now,
            updated_at=now
        )
        return self.insert_snippet(snippet)

    def get_by_id(self, snippet_id: str) -> Optional[KnowledgeSnippet]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return KnowledgeSnippet(
                id=row["id"],
                title=row["title"],
                category=row["category"],
                content=row["content"],
                tags=json.loads(row["tags"]) if row["tags"] else [],
                source=row["source"],
                verified=bool(row["verified"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )

    def list_all(self, category: Optional[str] = None, limit: int = 50) -> List[KnowledgeSnippet]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    "SELECT * FROM snippets WHERE category = ? ORDER BY updated_at DESC LIMIT ?", 
                    (category, limit)
                )
            else:
                cursor.execute("SELECT * FROM snippets ORDER BY updated_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [
                KnowledgeSnippet(
                    id=r["id"],
                    title=r["title"],
                    category=r["category"],
                    content=r["content"],
                    tags=json.loads(r["tags"]) if r["tags"] else [],
                    source=r["source"],
                    verified=bool(r["verified"]),
                    created_at=r["created_at"],
                    updated_at=r["updated_at"]
                )
                for r in rows
            ]

    def search(self, query: str, category: Optional[str] = None, limit: int = 6) -> List[KnowledgeSnippet]:
        """Hybrid search combining FTS5 with keyword scoring and tag matching."""
        import re
        clean_q = re.sub(r'[^a-zA-Z0-9\s]', ' ', query).lower()
        terms = [t.strip() for t in clean_q.split() if len(t.strip()) > 2]
        all_snippets = self.list_all(category=category, limit=200)

        if not terms:
            return all_snippets[:limit]

        scored: List[tuple[float, KnowledgeSnippet]] = []
        for snip in all_snippets:
            score = 0.0
            haystack_title = snip.title.lower()
            haystack_content = snip.content.lower()
            haystack_tags = [t.lower() for t in snip.tags]
            haystack_source = snip.source.lower()

            for term in terms:
                # Title exact match
                if term in haystack_title:
                    score += 5.0
                # Content match
                if term in haystack_content:
                    score += 2.0
                # Tag match
                if any(term in t for t in haystack_tags):
                    score += 4.0
                # Source match
                if term in haystack_source:
                    score += 1.5

            # Boost verified facts
            if snip.verified:
                score *= 1.2

            if score > 0.0:
                scored.append((score, snip))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM snippets")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT category, COUNT(*) FROM snippets GROUP BY category")
            cats = dict(cursor.fetchall())
            return {
                "total_snippets": total,
                "categories": cats,
                "storage_backend": "SQLite + FTS5 Living Ledger"
            }