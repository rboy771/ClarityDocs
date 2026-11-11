import sqlite3
import json
import re
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).resolve().parent / "rules.db"


class StatutorySearchService:
    """Provides full-text search and BM25 ranking over statutory rules using SQLite FTS5."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def _sanitize_query(self, query: str) -> str:
        """Cleans and extracts meaningful words for FTS5 boolean OR search."""
        words = re.findall(r"\b[A-Za-z0-9]{3,}\b", query)
        # Filter out common stop words
        stop_words = {"the", "and", "for", "with", "that", "this", "from", "you", "your", "have", "are", "not"}
        filtered = [w for w in words if w.lower() not in stop_words]
        if not filtered:
            return ""
        # Create an OR query for FTS5: e.g. "bank OR statement OR maintenance"
        return " OR ".join(filtered[:20])

    def search_rules(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a BM25 ranked full-text search against the statutory_rules FTS5 table.
        Returns matching rules sorted by relevance score.
        """
        fts_query = self._sanitize_query(text)
        if not fts_query:
            return []

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # bm25(statutory_rules) gives lower scores for better matches in SQLite FTS5
            sql = """
                SELECT rule_id, rule_name, category, citation, description, pitfalls, bm25(statutory_rules) as score
                FROM statutory_rules
                WHERE statutory_rules MATCH ?
                ORDER BY score ASC
                LIMIT ?
            """
            cursor.execute(sql, (fts_query, limit))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    "rule_id": row["rule_id"],
                    "rule_name": row["rule_name"],
                    "category": row["category"],
                    "citation": row["citation"],
                    "description": row["description"],
                    "pitfalls": json.loads(row["pitfalls"]),
                    "relevance_score": row["score"]
                })
            return results
        finally:
            conn.close()
