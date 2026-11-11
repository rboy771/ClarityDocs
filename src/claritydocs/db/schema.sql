-- SQLite Full-Text Search 5 (FTS5) table for statutory immigration and benefit rules.
-- The porter tokenizer lets "statements" match "statement", "certificates" match "certificate", and so on.
-- `authority` records which body the rule belongs to (ukvi, dwp, council) so a DWP letter
-- is never matched against Home Office visa rules.
CREATE VIRTUAL TABLE IF NOT EXISTS statutory_rules USING fts5(
    rule_id UNINDEXED,
    authority UNINDEXED,
    rule_name,
    category,
    citation,
    description,
    keywords,
    pitfalls,
    tokenize = 'porter unicode61'
);
