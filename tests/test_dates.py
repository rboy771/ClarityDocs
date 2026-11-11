from datetime import date

from claritydocs.dates import (
    calculate_deadline,
    classify_due_date,
    extract_explicit_deadline,
    extract_letter_date,
)
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


def test_classify_due_date_tiers():
    today = date(2026, 11, 11)
    assert classify_due_date(date(2026, 11, 11), today) == (0, UrgencyLevel.CRITICAL)
    assert classify_due_date(date(2026, 11, 18), today) == (7, UrgencyLevel.CRITICAL)
    assert classify_due_date(date(2026, 11, 19), today) == (8, UrgencyLevel.WARNING)
    assert classify_due_date(date(2026, 12, 9), today) == (28, UrgencyLevel.WARNING)
    assert classify_due_date(date(2026, 12, 10), today) == (29, UrgencyLevel.INFO)
    assert classify_due_date(date(2026, 11, 10), today) == (-1, UrgencyLevel.EXPIRED)


def test_extract_letter_date_labelled_on_same_or_next_line():
    assert extract_letter_date("Date: 10 November 2026\nDear Sir") == date(2026, 11, 10)
    assert extract_letter_date("Date of letter\n10 November 2026\nOur reference") == date(2026, 11, 10)
    assert extract_letter_date("Date of decision 5 November 2026") == date(2026, 11, 5)


def test_extract_letter_date_ignores_unlabelled_dates():
    # The application date is not the letter date, so it must not be used.
    assert extract_letter_date("Your application made on 28 October 2026 is incomplete.") is None
    assert extract_letter_date("Hello no date here") is None


def test_extract_explicit_deadline():
    assert extract_explicit_deadline("You must reply by 24 November 2026.") == date(2026, 11, 24)
    assert extract_explicit_deadline("Contact us by 5 December 2026 to ask.") == date(2026, 12, 5)
    assert extract_explicit_deadline("You have 14 days to reply.") is None
