from fastapi.testclient import TestClient
from claritydocs.main import app
from claritydocs.sanitizer import LocalPrivacySanitizer

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_privacy_sanitizer():
    sanitizer = LocalPrivacySanitizer()
    sample_text = (
        "Dear Applicant, your National Insurance number is QQ123456C and your case ref is GWF012345678. "
        "Please send documents to 10 Downing St, SW1A 2AA, or call 07123 456789."
    )
    clean, redactions = sanitizer.sanitize(sample_text)

    assert "QQ123456C" not in clean
    assert "GWF012345678" not in clean
    assert "SW1A 2AA" not in clean
    assert "07123 456789" not in clean
    assert "[REDACTED_NI_NUMBER]" in clean
    assert "[REDACTED_CASE_REF]" in clean
    assert "[REDACTED_POSTCODE]" in clean
    assert "[REDACTED_PHONE]" in clean
    assert len(redactions) == 4


def test_analyze_ukvi_further_evidence_letter():
    ukvi_letter = """
    UK Visas and Immigration
    Home Office
    Ref: 1212-0001-9999-8888
    
    We are currently considering your application for permission to stay.
    To make a decision, we require further evidence.
    
    You must provide:
    1. Official bank statements covering a consecutive 28-day period proving maintenance funds.
    2. A valid Tuberculosis (TB) medical certificate from an approved clinic.
    
    You must send this evidence to us within 14 days of the date of this letter.
    If you do not reply within 14 days, your application may be refused.
    """

    response = client.post("/api/v1/analyze-text", json={"text": ukvi_letter})
    assert response.status_code == 200
    data = response.json()

    assert data["issuing_body"] == "UK Visas and Immigration (Home Office)"
    assert data["redacted_items_count"] >= 1
    
    # Verify 14-day deadline was detected as CRITICAL
    deadlines = data["deadlines"]
    assert any(d["days_remaining"] == 14 and d["urgency"] == "critical" for d in deadlines)

    # Verify matched statutory rules
    checklist = data["evidence_checklist"]
    item_names = [item["item_name"] for item in checklist]
    assert "Bank Statements & Financial Proof" in item_names
    assert "Tuberculosis (TB) Certificate" in item_names
