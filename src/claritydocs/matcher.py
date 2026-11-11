import re
from datetime import date
from typing import List, Optional

from claritydocs.dates import (
    calculate_deadline,
    classify_due_date,
    extract_explicit_deadline,
    extract_letter_date,
)
from claritydocs.db.search import StatutorySearchService
from claritydocs.schemas import (
    BreakdownReport,
    DeadlineItem,
    EvidenceRequirement,
    RequirementType,
    UrgencyLevel,
)

AUTHORITY_KEY = {
    "UK Visas and Immigration (Home Office)": "ukvi",
    "Department for Work and Pensions (DWP)": "dwp",
    "Local Authority Council": "council",
}

# (regex, title, window in days, consequence, urgency used only when no date can be found)
DEADLINE_WINDOWS = [
    (
        re.compile(r"\b14\s+days?\b", re.IGNORECASE),
        "14-Day Response / Appeal Window",
        14,
        "Failure to submit evidence within 14 days will result in the application being decided on existing papers or rejected.",
        UrgencyLevel.CRITICAL,
    ),
    (
        re.compile(r"\b28\s+days?\b", re.IGNORECASE),
        "28-Day Evidence Submission Window",
        28,
        "Application may be treated as withdrawn or refused without refund.",
        UrgencyLevel.WARNING,
    ),
    (
        re.compile(r"\b(?:one|1)\s+(?:calendar\s+)?month\b", re.IGNORECASE),
        "1 Calendar Month Mandatory Reconsideration",
        30,
        "Right to dispute the decision lapses; late reconsideration requires formal proof of special circumstances.",
        UrgencyLevel.WARNING,
    ),
]

CATEGORY_TO_REQUIREMENT = {
    "financial_evidence": RequirementType.FINANCIAL_EVIDENCE,
    "form_submission": RequirementType.FORM_SUBMISSION,
    "biometric_or_interview": RequirementType.BIOMETRIC_OR_INTERVIEW,
}


def detect_issuing_body(lower_text: str) -> Optional[str]:
    if "home office" in lower_text or "ukvi" in lower_text or "visas and immigration" in lower_text:
        return "UK Visas and Immigration (Home Office)"
    if "dwp" in lower_text or "department for work and pensions" in lower_text or "jobcentre" in lower_text:
        return "Department for Work and Pensions (DWP)"
    if "hmcts" in lower_text or "tribunal" in lower_text:
        return "HM Courts & Tribunals Service"
    if "council" in lower_text:
        return "Local Authority Council"
    return None


class StatutoryRuleMatcher:
    """Matches letter text against statutory rules (SQLite FTS5) and works out real deadlines."""

    def __init__(self, search_service: Optional[StatutorySearchService] = None):
        self.search_service = search_service or StatutorySearchService()

    def analyze_and_match(
        self,
        sanitized_text: str,
        redaction_count: int,
        today: Optional[date] = None,
    ) -> BreakdownReport:
        lower_text = sanitized_text.lower()
        issuing_body = detect_issuing_body(lower_text)

        # Gate: If the document is not an official statutory letter, reject gracefully
        if not issuing_body:
            return BreakdownReport(
                document_title="Unrecognized Document",
                issuing_body="Unknown / Non-Statutory Document",
                summary="No official UKVI, Home Office, DWP, HMCTS, or Local Council notice detected in this document. Please ensure you upload an official decision, request, or correspondence letter.",
                deadlines=[],
                evidence_checklist=[],
                redacted_items_count=redaction_count,
                raw_sanitized_length=len(sanitized_text),
            )

        # Deadlines. A stated cut-off ("reply by 24 November 2026") wins; otherwise
        # letter date + window; otherwise only the generic window is known.
        letter_date = extract_letter_date(sanitized_text)
        explicit_due = extract_explicit_deadline(sanitized_text)

        deadlines: List[DeadlineItem] = []
        for pattern, title, window_days, consequence, fallback_urgency in DEADLINE_WINDOWS:
            if not pattern.search(lower_text):
                continue

            if explicit_due is not None:
                days_left, urgency = classify_due_date(explicit_due, today)
                due_date_str = explicit_due.isoformat()
            elif letter_date is not None:
                due, days_left, urgency = calculate_deadline(letter_date, window_days, today)
                due_date_str = due.isoformat()
            else:
                due_date_str = None
                days_left = window_days
                urgency = fallback_urgency

            deadlines.append(
                DeadlineItem(
                    title=title,
                    due_date=due_date_str,
                    days_remaining=days_left,
                    urgency=urgency,
                    statutory_consequence=consequence,
                )
            )

        if not deadlines:
            deadlines.append(
                DeadlineItem(
                    title="Standard Processing Notice",
                    due_date=None,
                    days_remaining=None,
                    urgency=UrgencyLevel.INFO,
                    statutory_consequence="No urgent time-limited sanction detected in parsed paragraphs.",
                )
            )

        # Evidence and rules, restricted to the detected authority.
        authority = AUTHORITY_KEY.get(issuing_body)
        db_results = self.search_service.search_rules(sanitized_text, authority=authority)

        matched_evidence: List[EvidenceRequirement] = []
        for rule in db_results:
            matched_evidence.append(
                EvidenceRequirement(
                    item_name=rule["rule_name"],
                    requirement_type=CATEGORY_TO_REQUIREMENT.get(rule["category"], RequirementType.MANDATORY_DOCUMENT),
                    description=rule["description"],
                    statutory_rule_citation=rule["citation"],
                    common_pitfalls=rule["pitfalls"],
                )
            )

        summary = (
            f"Parsed {issuing_body} communication. Identified {len(deadlines)} timeline constraints "
            f"and {len(matched_evidence)} statutory documentation requirements."
        )

        return BreakdownReport(
            document_title="Official Statutory Notice Review",
            issuing_body=issuing_body,
            summary=summary,
            deadlines=deadlines,
            evidence_checklist=matched_evidence,
            redacted_items_count=redaction_count,
            raw_sanitized_length=len(sanitized_text),
        )
