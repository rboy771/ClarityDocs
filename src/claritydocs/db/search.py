import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

DB_PATH = Path(__file__).resolve().parent / "rules.db"

# Words that carry no signal. Two-letter tokens like "tb" and "b2" are kept on purpose,
# because they are real keywords in the rules table.
STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from", "you", "your", "have", "are", "not",
    "of", "in", "to", "is", "be", "by", "an", "as", "at", "it", "on", "or", "if", "do", "no",
    "we", "us", "our", "will", "must", "can", "may", "any", "all", "has", "was", "were", "been",
}

TOKEN_RE = re.compile(r"[A-Za-z0-9]{2,}")

# A rule is only returned when at least this many of its distinct keywords appear in the letter.
# Chosen from observed data: wrong rules on full letters share 1 keyword (e.g. "certificate"),
# correct rules share 2 on a short snippet and 6 or more on a full letter.
DEFAULT_MIN_KEYWORD_HITS = 2


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_RE.findall(text) if t.lower() not in STOP_WORDS]


def _normalise(token: str) -> str:
    """Cheap plural folding so 'statements' and 'statement' count as the same keyword."""
    return token[:-1] if len(token) > 3 and token.endswith("s") else token


class StatutorySearchService:
    """
    Retrieves statutory rules with SQLite FTS5 (BM25 ranking) and then keeps only the
    rules that share enough distinct keywords with the letter to be a real match.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def _build_fts_query(self, letter_tokens: Set[str]) -> str:
        if not letter_tokens:
            return ""
        # Quote every token so words like OR, AND, NOT, NEAR are never read as FTS5 operators.
        terms = " OR ".join(f'"{t}"' for t in sorted(letter_tokens))
        # Search the keywords column only, so common words in descriptions cannot create matches.
        return f"keywords : ({terms})"

    def search_rules(
        self,
        text: str,
        limit: int = 8,
        authority: Optional[str] = None,
        min_keyword_hits: int = DEFAULT_MIN_KEYWORD_HITS,
    ) -> List[Dict[str, Any]]:
        letter_tokens = set(tokenize(text))
        fts_query = self._build_fts_query(letter_tokens)
        if not fts_query:
            return []

        normalised_letter = {_normalise(t) for t in letter_tokens}

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            sql = """
                SELECT rule_id, authority, rule_name, category, citation, description,
                       keywords, pitfalls, bm25(statutory_rules) AS score
                FROM statutory_rules
                WHERE statutory_rules MATCH ?
                  AND (? IS NULL OR authority = ?)
                ORDER BY score ASC
                LIMIT ?
            """
            rows = conn.execute(sql, (fts_query, authority, authority, limit)).fetchall()
        finally:
            conn.close()

        results: List[Dict[str, Any]] = []
        for row in rows:
            rule_keywords = {_normalise(t) for t in tokenize(row["keywords"])}
            hits = rule_keywords & normalised_letter
            if len(hits) < min_keyword_hits:
                continue
            results.append({
                "rule_id": row["rule_id"],
                "authority": row["authority"],
                "rule_name": row["rule_name"],
                "category": row["category"],
                "citation": row["citation"],
                "description": row["description"],
                "pitfalls": json.loads(row["pitfalls"]),
                "relevance_score": row["score"],
                "keyword_hits": sorted(hits),
            })
        return results
