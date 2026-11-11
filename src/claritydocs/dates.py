import re
from datetime import date, timedelta
from typing import Optional, Tuple
from dateutil import parser
from dateutil.parser import ParserError
from claritydocs.schemas import UrgencyLevel

MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December"
)

# "10 November 2026", "1st October 2026", or "10/11/2026" (day first, as in UK letters)
DATE_PATTERN = (
    r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:" + MONTHS + r")\s+\d{4}|\d{1,2}[/.]\d{1,2}[/.]\d{4})"
)

# Only trust a date that follows a label such as "Date of letter" or "Date:".
# A label and its value may be on separate lines after PDF extraction, so allow whitespace.
LABELLED_DATE_RE = re.compile(
    r"(?:date\s+of\s+(?:the\s+)?(?:letter|notice|decision)|date\s+issued|issued\s+on|date\s*:)"
    r"\s*[:\-]?\s*" + DATE_PATTERN,
    re.IGNORECASE,
)

# A stated cut-off such as "reply by 24 November 2026" or "contact us by 5 December 2026".
EXPLICIT_DEADLINE_RE = re.compile(
    r"\b(?:by|before|no\s+later\s+than)\s+" + DATE_PATTERN,
    re.IGNORECASE,
)


def _parse_date_fragment(fragment: str) -> Optional[date]:
    """Parses one matched date fragment. dayfirst=True because UK letters write 10/11/2026 as 10 November."""
    try:
        return parser.parse(fragment, dayfirst=True).date()
    except (ParserError, ValueError, OverflowError):
        return None


def extract_letter_date(text: str) -> Optional[date]:
    """
    Finds the date the letter was issued by looking for a labelled date
    ("Date of letter", "Date of decision", "Date:"). Returns None if there is no
    labelled date, because guessing from an unrelated date would give a wrong deadline.
    """
    match = LABELLED_DATE_RE.search(text)
    if not match:
        return None
    return _parse_date_fragment(match.group(1))


def extract_explicit_deadline(text: str) -> Optional[date]:
    """Finds a stated cut-off date such as 'reply by 24 November 2026'. Returns None if absent."""
    match = EXPLICIT_DEADLINE_RE.search(text)
    if not match:
        return None
    return _parse_date_fragment(match.group(1))


def classify_due_date(due_date: date, today: Optional[date] = None) -> Tuple[int, UrgencyLevel]:
    """Returns (days_remaining, urgency) for a known due date."""
    if today is None:
        today = date.today()

    days_remaining = (due_date - today).days

    if days_remaining < 0:
        urgency = UrgencyLevel.EXPIRED
    elif days_remaining <= 7:
        urgency = UrgencyLevel.CRITICAL
    elif days_remaining <= 28:
        urgency = UrgencyLevel.WARNING
    else:
        urgency = UrgencyLevel.INFO

    return days_remaining, urgency


def calculate_deadline(
    letter_date: date,
    window_days: int,
    today: Optional[date] = None
) -> Tuple[date, int, UrgencyLevel]:
    """
    Given:
      - letter_date: date the notice was issued
      - window_days: days granted (e.g. 14, 28)
      - today: current date (defaults to date.today())

    Returns:
      - due_date: exact expiration date
      - days_remaining: integer days left from today
      - urgency: UrgencyLevel (EXPIRED, CRITICAL, WARNING, INFO)
    """
    due_date = letter_date + timedelta(days=window_days)
    days_remaining, urgency = classify_due_date(due_date, today)
    return due_date, days_remaining, urgency
