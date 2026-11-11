import pytest
from pathlib import Path
from claritydocs.db.seed import init_db
from claritydocs.db.search import StatutorySearchService

TEST_DB_PATH = Path(__file__).resolve().parent / "test_rules.db"


@pytest.fixture(scope="module")
def search_service():
    # Initialize fresh test db
    init_db(db_path=TEST_DB_PATH)
    service = StatutorySearchService(db_path=TEST_DB_PATH)
    yield service
    # Cleanup test db after tests
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def test_search_bank_statements(search_service):
    # Notice mentioning maintenance funds and cash savings
    results = search_service.search_rules("Please provide maintenance funds and cash balance statements", limit=3)
    assert len(results) > 0
    top_match = results[0]
    assert top_match["rule_id"] == "ukvi_finance_28day"
    assert "FIN 2.1" in top_match["citation"]
    assert len(top_match["pitfalls"]) >= 3


def test_search_dwp_mandatory_reconsideration(search_service):
    # DWP letter about PIP decision and disagreement
    results = search_service.search_rules("If you disagree with this PIP decision ask for a mandatory reconsideration", limit=3)
    assert len(results) > 0
    top_match = results[0]
    assert top_match["rule_id"] == "dwp_mandatory_reconsideration"
    assert "Social Security Act 1998" in top_match["citation"]


def test_search_english_selt(search_service):
    # Letter asking for SELT or CEFR B1
    results = search_service.search_rules("Proof of English language proficiency at level B1 via IELTS", limit=3)
    assert len(results) > 0
    top_match = results[0]
    assert top_match["rule_id"] == "ukvi_english_selt"
    assert "Appendix English Language" in top_match["citation"]
