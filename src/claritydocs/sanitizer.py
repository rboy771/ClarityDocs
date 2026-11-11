import re
from typing import Tuple, List
from claritydocs.schemas import RedactedField


# UK National Insurance Number regex
# Format: 2 prefix letters, 6 digits, 1 suffix letter (A-D)
# Prefix letters cannot include D, F, I, Q, U, V, and the second letter cannot be D, F, I, O, Q, U, V.
NI_REGEX = re.compile(r"\b[A-Z]{2}\s?[0-9]{2}\s?[0-9]{2}\s?[0-9]{2}\s?[A-D]{1}\b", re.IGNORECASE)

# Standard UK/International 9-digit passport numbers
PASSPORT_REGEX = re.compile(r"\b[0-9]{9}\b")

# UK Postcode regex
POSTCODE_REGEX = re.compile(r"\b[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}\b", re.IGNORECASE)

# Home Office / UKVI Case reference patterns (e.g. 1212-0001-1234-5678, HO/1234567, GWF012345678)
HO_REF_REGEX = re.compile(r"\b(GWF\d{9}|HO/\d{6,8}|\d{4}-\d{4}-\d{4}-\d{4})\b", re.IGNORECASE)

# UK Phone numbers
PHONE_REGEX = re.compile(r"\b(?:\+44\s?|0)(?:7\d{3}|\d{4})\s?\d{6}\b")


class LocalPrivacySanitizer:
    """
    Strips personal identifying information (PII) before documents
    are parsed or sent to any language model.
    """

    def sanitize(self, raw_text: str) -> Tuple[str, List[RedactedField]]:
        redactions: List[RedactedField] = []
        cleaned = raw_text

        # 1. National Insurance Number
        for match in NI_REGEX.finditer(cleaned):
            val = match.group(0)
            redactions.append(RedactedField(field_type="NI_NUMBER", original_length=len(val), placeholder="[REDACTED_NI_NUMBER]"))
        cleaned = NI_REGEX.sub("[REDACTED_NI_NUMBER]", cleaned)

        # 2. Case References
        for match in HO_REF_REGEX.finditer(cleaned):
            val = match.group(0)
            redactions.append(RedactedField(field_type="CASE_REF", original_length=len(val), placeholder="[REDACTED_CASE_REF]"))
        cleaned = HO_REF_REGEX.sub("[REDACTED_CASE_REF]", cleaned)

        # 3. UK Postcodes
        for match in POSTCODE_REGEX.finditer(cleaned):
            val = match.group(0)
            redactions.append(RedactedField(field_type="POSTCODE", original_length=len(val), placeholder="[REDACTED_POSTCODE]"))
        cleaned = POSTCODE_REGEX.sub("[REDACTED_POSTCODE]", cleaned)

        # 4. Phone Numbers
        for match in PHONE_REGEX.finditer(cleaned):
            val = match.group(0)
            redactions.append(RedactedField(field_type="PHONE", original_length=len(val), placeholder="[REDACTED_PHONE]"))
        cleaned = PHONE_REGEX.sub("[REDACTED_PHONE]", cleaned)

        return cleaned, redactions
