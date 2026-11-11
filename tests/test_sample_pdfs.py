import importlib.util
from datetime import date
from pathlib import Path

import pytest

from claritydocs.extractor import DocumentIngestionService
from claritydocs.matcher import StatutoryRuleMatcher
from claritydocs.sanitizer import LocalPrivacySanitizer

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
TODAY = date(2026, 11, 11)


def _build_pdf(script_name: str, out_path: Path) -> bytes:
    spec = importlib.util.spec_from_file_location(script_name, SCRIPTS_DIR / f"{script_name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.build(out_path)
    return out_path.read_bytes()


def _analyse(pdf_bytes: bytes):
    raw = DocumentIngestionService.extract_from_pdf_bytes(pdf_bytes)
    clean, redactions = LocalPrivacySanitizer().sanitize(raw)
    report = StatutoryRuleMatcher().analyze_and_match(clean, len(redactions), today=TODAY)
    return clean, redactions, report


@pytest.fixture(scope="module")
def ukvi(tmp_path_factory):
    out = tmp_path_factory.mktemp("pdf") / "ukvi.pdf"
    return _analyse(_build_pdf("generate_sample_pdf_v2", out))


@pytest.fixture(scope="module")
def dwp(tmp_path_factory):
    out = tmp_path_factory.mktemp("pdf") / "dwp.pdf"
    return _analyse(_build_pdf("generate_sample_pdf_dwp", out))


def test_ukvi_pdf_authority_and_evidence(ukvi):
    _, _, report = ukvi
    assert report.issuing_body == "UK Visas and Immigration (Home Office)"
    names = {item.item_name for item in report.evidence_checklist}
    assert names == {
        "Bank Statements & Maintenance Funds",
        "Tuberculosis (TB) Medical Clearance",
        "English Language Proficiency (SELT)",
    }


def test_ukvi_pdf_uses_stated_deadline(ukvi):
    _, _, report = ukvi
    deadline = next(d for d in report.deadlines if d.title.startswith("14-Day"))
    assert deadline.due_date == "2026-11-24"
    assert deadline.days_remaining == 13


def test_ukvi_pdf_redacts_every_identifier(ukvi):
    clean, redactions, _ = ukvi
    assert len(redactions) == 5
    for leaked in ["GWF012345678", "1212-0001", "QQ 12 34 56 C", "07700 900123", "M1 1AA"]:
        assert leaked not in clean


def test_dwp_pdf_authority_and_evidence(dwp):
    _, _, report = dwp
    assert report.issuing_body == "Department for Work and Pensions (DWP)"
    names = {item.item_name for item in report.evidence_checklist}
    assert names == {"DWP Mandatory Reconsideration"}


def test_dwp_pdf_uses_stated_deadline(dwp):
    _, _, report = dwp
    deadline = next(d for d in report.deadlines if "Mandatory Reconsideration" in d.title)
    assert deadline.due_date == "2026-12-05"
    assert deadline.days_remaining == 24
    assert deadline.urgency == "warning"


def test_dwp_pdf_redacts_claim_reference(dwp):
    clean, redactions, _ = dwp
    assert "PIP-2026-0048213" not in clean
    assert "QQ 98 76 54 A" not in clean
    assert len(redactions) == 3
