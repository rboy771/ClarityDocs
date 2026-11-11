from datetime import date
from claritydocs.dates import calculate_deadline
from claritydocs.schemas import UrgencyLevel


def test_deadline_future():
    # Letter issued 1 Nov 2026, 14-day window -> due 15 Nov 2026
    # Today is 11 Nov 2026 -> 4 days remaining -> CRITICAL
    letter_date = date(2026, 11, 1)
    today = date(2026, 11, 11)
    
    due_date, days_left, urgency = calculate_deadline(letter_date, 14, today)
    
    assert due_date == date(2026, 11, 15)
    assert days_left == 4
    assert urgency == UrgencyLevel.CRITICAL


def test_deadline_overdue():
    # Letter issued 1 Oct 2026, 14-day window -> due 15 Oct 2026
    # Today is 11 Nov 2026 -> -27 days remaining -> EXPIRED
    letter_date = date(2026, 10, 1)
    today = date(2026, 11, 11)
    
    due_date, days_left, urgency = calculate_deadline(letter_date, 14, today)
    
    assert due_date == date(2026, 10, 15)
    assert days_left == -27
    assert urgency == UrgencyLevel.EXPIRED
