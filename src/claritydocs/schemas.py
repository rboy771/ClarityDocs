from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class UrgencyLevel(str, Enum):
    CRITICAL = "critical"  # <= 7 days or strict legal cut-off
    WARNING = "warning"    # <= 28 days
    INFO = "info"          # Standard action or informational


class RequirementType(str, Enum):
    MANDATORY_DOCUMENT = "mandatory_document"
    FINANCIAL_EVIDENCE = "financial_evidence"
    BIOMETRIC_OR_INTERVIEW = "biometric_or_interview"
    FORM_SUBMISSION = "form_submission"
    FEES_PAYMENT = "fees_payment"


class DeadlineItem(BaseModel):
    title: str = Field(..., description="Short summary of the deadline")
    due_date: Optional[str] = Field(None, description="ISO formatted date YYYY-MM-DD or relative string")
    days_remaining: Optional[int] = Field(None, description="Estimated days remaining from receipt date")
    urgency: UrgencyLevel
    statutory_consequence: str = Field(..., description="Legal outcome if missed (e.g. invalid application, right to appeal lapsed)")


class EvidenceRequirement(BaseModel):
    item_name: str = Field(..., description="The name of the requested document or proof")
    requirement_type: RequirementType
    description: str = Field(..., description="Specific conditions like 28 consecutive days, official letterhead, translation")
    statutory_rule_citation: Optional[str] = Field(None, description="Official UKVI or DWP appendix clause")
    common_pitfalls: List[str] = Field(default_factory=list, description="Common reasons this document gets rejected")


class RedactedField(BaseModel):
    field_type: str  # NI_NUMBER, PASSPORT, ADDRESS, NAME, CASE_REF
    original_length: int
    placeholder: str


class BreakdownReport(BaseModel):
    document_title: str
    issuing_body: str  # e.g. "UK Visas and Immigration", "HM Courts & Tribunals Service", "DWP"
    summary: str
    deadlines: List[DeadlineItem]
    evidence_checklist: List[EvidenceRequirement]
    redacted_items_count: int
    raw_sanitized_length: int
