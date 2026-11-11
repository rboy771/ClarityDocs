from datetime import date, timedelta
from typing import Optional, Tuple
from claritydocs.schemas import UrgencyLevel
from dateutil import parser
from dateutil.parser import ParserError


def extract_letter_date(text: str) -> Optional[date]:
    """Safely extracts a date from raw text or returns None."""
    try:
        return parser.parse(text, fuzzy=True).date()
    except (ParserError, ValueError, OverflowError):
        return None


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
      - urgency: UrgencyLevel (CRITICAL, WARNING, INFO)
    """
    if today is None:
        today = date.today()

    due_date = letter_date + timedelta(days=window_days)
    days_remaining = (due_date - today).days
    if days_remaining <= 7:
        urgency = UrgencyLevel.CRITICAL
    elif days_remaining <= 28:
        urgency = UrgencyLevel.WARNING
    else:
        urgency = UrgencyLevel.INFO

    return due_date, days_remaining, urgency
