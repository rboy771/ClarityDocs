-- SQLite Full-Text Search 5 (FTS5) Table for Statutory Immigration & Benefit Rules
CREATE VIRTUAL TABLE IF NOT EXISTS statutory_rules USING fts5(
    rule_id UNINDEXED,
    rule_name,
    category,
    citation,
    description,
    keywords,
    pitfalls
);
