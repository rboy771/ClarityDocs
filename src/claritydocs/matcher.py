import re
from typing import List
from claritydocs.schemas import (
    BreakdownReport,
    DeadlineItem,
    EvidenceRequirement,
    UrgencyLevel,
    RequirementType,
)


STATUTORY_RULES_DB = [
    {
        "keywords": ["bank statement", "funds", "maintenance", "savings", "financial requirement"],
        "name": "Bank Statements & Financial Proof",
        "type": RequirementType.FINANCIAL_EVIDENCE,
        "citation": "UKVI Appendix Finance, Paragraph FIN 2.1 to FIN 8.1",
        "description": "Must show consecutive funds held for at least 28 days ending no more than 31 days before application date.",
        "pitfalls": [
            "Funds dropped below required threshold even for a single day during the 28-day window.",
            "Statements do not display account holder name, account number, or bank logo.",
            "Using mini-statements or ad-hoc ATM receipts instead of official formal statements.",
            "Closing statement date is more than 31 days older than the application submission date."
        ]
    },
    {
        "keywords": ["tb", "tuberculosis", "medical certificate", "chest x-ray"],
        "name": "Tuberculosis (TB) Certificate",
        "type": RequirementType.MANDATORY_DOCUMENT,
        "citation": "UKVI Appendix T: Tuberculosis screening",
        "description": "Certificate from an approved Home Office diagnostic clinic confirming clearance.",
        "pitfalls": [
            "Test was taken at an unaccredited clinic not listed on the official UKVI designated clinics panel.",
            "Certificate has passed its 6-month validity period."
        ]
    },
    {
        "keywords": ["english language", "ielts", "b1", "b2", "selt", "degree taught in english"],
        "name": "Proof of English Language Proficiency",
        "type": RequirementType.MANDATORY_DOCUMENT,
        "citation": "UKVI Appendix English Language (EL 1.1)",
        "description": "Passed an approved Secure English Language Test (SELT) at CEFR level or Ecctis confirmation.",
        "pitfalls": [
            "Certificate is from an unapproved provider (must be IELTS SELT Consortium, LanguageCert, Pearson, or PSI).",
            "Missing the unique reference number (URN) needed by the case worker to verify online."
        ]
    },
    {
        "keywords": ["tenancy", "accommodation", "landlord", "property inspection", "living arrangement"],
        "name": "Adequate Accommodation Evidence",
        "type": RequirementType.MANDATORY_DOCUMENT,
        "citation": "UKVI Immigration Rules: Part 8 & Appendix FM",
        "description": "Proof that housing is not overcrowded and complies with UK Public Health Acts.",
        "pitfalls": [
            "Missing landlord letter permitting the applicant to reside at the premises.",
            "Failure to include a property inspection report for shared accommodations."
        ]
    },
    {
        "keywords": ["pip", "personal independence payment", "dwp", "mandatory reconsideration", "appeal"],
        "name": "Mandatory Reconsideration Request (DWP)",
        "type": RequirementType.FORM_SUBMISSION,
        "citation": "Social Security Act 1998, Section 12 & DWP Decision Making Guidance",
        "description": "Formal written request disputing a benefit decision within 1 calendar month of decision letter.",
        "pitfalls": [
            "Submitting beyond the 1-calendar-month deadline without an official 'good cause' explanation.",
            "Not providing new medical evidence directly matching the specific PIP descriptors scored 0."
        ]
    }
]


class StatutoryRuleMatcher:
    """Matches text against statutory immigration and benefit rules."""

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

        # 2. Extract Deadlines
        deadlines: List[DeadlineItem] = []
        
        # Check for 14-day appeal / response notice
        if re.search(r"\b14\s+days?\b", lower_text):
            deadlines.append(
                DeadlineItem(
                    title="14-Day Response / Appeal Window",
                    due_date=None,
                    days_remaining=14,
                    urgency=UrgencyLevel.CRITICAL,
                    statutory_consequence="Failure to submit evidence within 14 days will result in the application being decided on existing papers or rejected."
                )
            )

        # Check for 28-day statutory notice
        if re.search(r"\b28\s+days?\b", lower_text):
            deadlines.append(
                DeadlineItem(
                    title="28-Day Evidence Submission Window",
                    due_date=None,
                    days_remaining=28,
                    urgency=UrgencyLevel.WARNING,
                    statutory_consequence="Application may be treated as withdrawn or refused without refund."
                )
            )

        # Check for 1 calendar month (DWP / Council mandatory reconsideration)
        if re.search(r"\b(?:one|1)\s+(?:calendar\s+)?month\b", lower_text):
            deadlines.append(
                DeadlineItem(
                    title="1 Calendar Month Mandatory Reconsideration",
                    due_date=None,
                    days_remaining=30,
                    urgency=UrgencyLevel.WARNING,
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

        # 3. Match Statutory Evidence Requirements
        matched_evidence: List[EvidenceRequirement] = []
        for rule in STATUTORY_RULES_DB:
            if any(kw in lower_text for kw in rule["keywords"]):
                matched_evidence.append(
                    EvidenceRequirement(
                        item_name=rule["name"],
                        requirement_type=rule["type"],
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
