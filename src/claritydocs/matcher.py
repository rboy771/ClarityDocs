import re
from typing import List
from claritydocs.schemas import (
    BreakdownReport,
    DeadlineItem,
    EvidenceRequirement,
    UrgencyLevel,
    RequirementType,
)
from claritydocs.dates import extract_letter_date, calculate_deadline
from claritydocs.db.search import StatutorySearchService


class StatutoryRuleMatcher:
    """Matches text against statutory immigration and benefit rules using SQLite FTS5."""

    def __init__(self, search_service: StatutorySearchService | None = None):
        self.search_service = search_service or StatutorySearchService()

    def analyze_and_match(self, sanitized_text: str, redaction_count: int) -> BreakdownReport:
        lower_text = sanitized_text.lower()

        # 1. Detect Issuing Body
        issuing_body = "UK Statutory Authority"
        if "home office" in lower_text or "ukvi" in lower_text or "visas and immigration" in lower_text:
            issuing_body = "UK Visas and Immigration (Home Office)"
        elif "dwp" in lower_text or "department for work and pensions" in lower_text or "jobcentre" in lower_text:
            issuing_body = "Department for Work and Pensions (DWP)"
        elif "hmcts" in lower_text or "tribunal" in lower_text:
            issuing_body = "HM Courts & Tribunals Service"
        elif "council" in lower_text:
            issuing_body = "Local Authority Council"

        # 2. Extract Letter Date and Calculate Deadlines
        detected_date = extract_letter_date(sanitized_text)
        deadlines: List[DeadlineItem] = []

        # Check for 14-day window
        if re.search(r"\b14\s+days?\b", lower_text):
            if detected_date:
                due_date, days_left, urgency = calculate_deadline(detected_date, 14)
                due_date_str = due_date.isoformat()
            else:
                due_date_str = None
                days_left = 14
                urgency = UrgencyLevel.CRITICAL

            deadlines.append(
                DeadlineItem(
                    title="14-Day Response / Appeal Window",
                    due_date=due_date_str,
                    days_remaining=days_left,
                    urgency=urgency,
                    statutory_consequence="Failure to submit evidence within 14 days will result in the application being decided on existing papers or rejected."
                )
            )

        # Check for 28-day window
        if re.search(r"\b28\s+days?\b", lower_text):
            if detected_date:
                due_date, days_left, urgency = calculate_deadline(detected_date, 28)
                due_date_str = due_date.isoformat()
            else:
                due_date_str = None
                days_left = 28
                urgency = UrgencyLevel.WARNING

            deadlines.append(
                DeadlineItem(
                    title="28-Day Evidence Submission Window",
                    due_date=due_date_str,
                    days_remaining=days_left,
                    urgency=urgency,
                    statutory_consequence="Application may be treated as withdrawn or refused without refund."
                )
            )

        # Check for 1 calendar month
        if re.search(r"\b(?:one|1)\s+(?:calendar\s+)?month\b", lower_text):
            if detected_date:
                due_date, days_left, urgency = calculate_deadline(detected_date, 30)
                due_date_str = due_date.isoformat()
            else:
                due_date_str = None
                days_left = 30
                urgency = UrgencyLevel.WARNING

            deadlines.append(
                DeadlineItem(
                    title="1 Calendar Month Mandatory Reconsideration",
                    due_date=due_date_str,
                    days_remaining=days_left,
                    urgency=urgency,
                    statutory_consequence="Right to dispute the decision lapses; late reconsideration requires formal proof of special circumstances."
                )
            )

        if not deadlines:
            deadlines.append(
                DeadlineItem(
                    title="Standard Processing Notice",
                    due_date=None,
                    days_remaining=None,
                    urgency=UrgencyLevel.INFO,
                    statutory_consequence="No urgent time-limited sanction detected in parsed paragraphs."
                )
            )

        # 3. Match Statutory Evidence Requirements via SQLite FTS5
        matched_evidence: List[EvidenceRequirement] = []
        db_results = self.search_service.search_rules(sanitized_text, limit=4)
        
        for rule in db_results:
            req_type = RequirementType.MANDATORY_DOCUMENT
            if rule["category"] == "financial_evidence":
                req_type = RequirementType.FINANCIAL_EVIDENCE
            elif rule["category"] == "form_submission":
                req_type = RequirementType.FORM_SUBMISSION
            elif rule["category"] == "biometric_or_interview":
                req_type = RequirementType.BIOMETRIC_OR_INTERVIEW

            matched_evidence.append(
                EvidenceRequirement(
                    item_name=rule["rule_name"],
                    requirement_type=req_type,
                    description=rule["description"],
                    statutory_rule_citation=rule["citation"],
                    common_pitfalls=rule["pitfalls"]
                )
            )

        summary = f"Parsed {issuing_body} communication. Identified {len(deadlines)} timeline constraints and {len(matched_evidence)} statutory documentation requirements."

        return BreakdownReport(
            document_title="Official Statutory Notice Review",
            issuing_body=issuing_body,
            summary=summary,
            deadlines=deadlines,
            evidence_checklist=matched_evidence,
            redacted_items_count=redaction_count,
            raw_sanitized_length=len(sanitized_text)
        )
