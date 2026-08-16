from datetime import date, datetime

import pytest

from src.ai.revision_scheduler import (
    calculate_review_interval,
    calculate_next_review_date,
    get_revision_recommendation,
)


# ============================================================
# REVIEW INTERVAL TESTS
# ============================================================

def test_weak_score_requires_immediate_revision():

    assert (
        calculate_review_interval(40)
        == 1
    )


def test_average_score_gets_short_interval():

    assert (
        calculate_review_interval(60)
        == 2
    )


def test_developing_score_gets_four_day_interval():

    assert (
        calculate_review_interval(75)
        == 4
    )


def test_strong_score_gets_seven_day_interval():

    assert (
        calculate_review_interval(85)
        == 7
    )


def test_excellent_score_gets_fourteen_day_interval():

    assert (
        calculate_review_interval(95)
        == 14
    )


# ============================================================
# STREAK TESTS
# ============================================================

def test_strong_revision_streak_extends_interval():

    assert (
        calculate_review_interval(
            95,
            revision_streak=2
        )
        == 28
    )


def test_revision_interval_has_thirty_day_limit():

    assert (
        calculate_review_interval(
            100,
            revision_streak=10
        )
        == 30
    )


def test_weak_topic_does_not_get_streak_extension():

    assert (
        calculate_review_interval(
            40,
            revision_streak=10
        )
        == 1
    )


# ============================================================
# DATE TESTS
# ============================================================

def test_next_review_date():

    start = date(
        2026,
        8,
        15
    )

    result = calculate_next_review_date(
        interval_days=7,
        start_date=start,
    )

    assert result == date(
        2026,
        8,
        22
    )


def test_next_review_date_accepts_datetime():

    start = datetime(
        2026,
        8,
        15,
        10,
        30
    )

    result = calculate_next_review_date(
        interval_days=2,
        start_date=start,
    )

    assert result == date(
        2026,
        8,
        17
    )


def test_zero_interval_returns_same_date():

    start = date(
        2026,
        8,
        15
    )

    result = calculate_next_review_date(
        interval_days=0,
        start_date=start,
    )

    assert result == start


def test_invalid_date_type():

    with pytest.raises(TypeError):

        calculate_next_review_date(
            interval_days=7,
            start_date="2026-08-15",
        )


# ============================================================
# RECOMMENDATION TESTS
# ============================================================

def test_weak_revision_recommendation():

    result = get_revision_recommendation(
        score_percentage=40
    )

    assert result["interval_days"] == 1

    assert result["urgency"] == "HIGH"


def test_average_revision_recommendation():

    result = get_revision_recommendation(
        score_percentage=60
    )

    assert result["interval_days"] == 2

    assert result["urgency"] == "HIGH"


def test_strong_revision_recommendation():

    result = get_revision_recommendation(
        score_percentage=85
    )

    assert result["interval_days"] == 7

    assert result["urgency"] == "LOW"


def test_excellent_revision_recommendation():

    result = get_revision_recommendation(
        score_percentage=95
    )

    assert result["interval_days"] == 14

    assert result["urgency"] == "LOW"