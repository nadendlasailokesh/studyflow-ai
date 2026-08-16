# ============================================================
# PHASE 10.3 TESTS
# Adaptive Difficulty
# ============================================================

from src.ai.adaptive_difficulty import (
    EASY,
    MEDIUM,
    HARD,
    calculate_performance_trend,
    determine_adaptive_difficulty,
    get_adaptive_difficulty_recommendation,
)


# ============================================================
# NO HISTORY
# ============================================================

def test_no_history_returns_medium():

    difficulty = determine_adaptive_difficulty(
        mastery=0,
        recent_performance=[],
        attempts=0,
    )

    assert difficulty == MEDIUM


# ============================================================
# LOW MASTERY
# ============================================================

def test_low_mastery_returns_easy():

    difficulty = determine_adaptive_difficulty(
        mastery=25,
        recent_performance=[
            {"score": 30}
        ],
        attempts=1,
    )

    assert difficulty == EASY


# ============================================================
# MODERATE PERFORMANCE
# ============================================================

def test_moderate_mastery_returns_medium():

    difficulty = determine_adaptive_difficulty(
        mastery=55,
        recent_performance=[
            {"score": 60},
            {"score": 55},
        ],
        attempts=2,
    )

    assert difficulty == MEDIUM


# ============================================================
# STRONG PERFORMANCE
# ============================================================

def test_strong_repeated_performance_returns_hard():

    difficulty = determine_adaptive_difficulty(
        mastery=90,
        recent_performance=[
            {"score": 95},
            {"score": 90},
            {"score": 85},
        ],
        attempts=3,
        current_difficulty=MEDIUM,
    )

    assert difficulty == HARD


# ============================================================
# DECLINING PERFORMANCE
# ============================================================

def test_declining_performance_reduces_hard_to_medium():

    difficulty = determine_adaptive_difficulty(
        mastery=70,
        recent_performance=[
            {"score": 55},
            {"score": 80},
        ],
        attempts=2,
        current_difficulty=HARD,
    )

    assert difficulty == MEDIUM


# ============================================================
# IMPROVING PERFORMANCE
# ============================================================

def test_improving_performance_can_increase_difficulty():

    difficulty = determine_adaptive_difficulty(
        mastery=75,
        recent_performance=[
            {"score": 85},
            {"score": 70},
        ],
        attempts=2,
        current_difficulty=MEDIUM,
    )

    assert difficulty == HARD


# ============================================================
# TREND
# ============================================================

def test_improving_trend():

    trend = calculate_performance_trend(
        [
            {"score": 90},
            {"score": 70},
        ]
    )

    assert trend == "IMPROVING"


def test_declining_trend():

    trend = calculate_performance_trend(
        [
            {"score": 50},
            {"score": 75},
        ]
    )

    assert trend == "DECLINING"


def test_stable_trend():

    trend = calculate_performance_trend(
        [
            {"score": 70},
            {"score": 68},
        ]
    )

    assert trend == "STABLE"


def test_insufficient_trend():

    trend = calculate_performance_trend(
        [
            {"score": 70}
        ]
    )

    assert trend == "INSUFFICIENT_DATA"


# ============================================================
# STRUCTURED RECOMMENDATION
# ============================================================

def test_adaptive_recommendation_contains_expected_fields():

    recommendation = (
        get_adaptive_difficulty_recommendation(
            mastery=85,
            recent_performance=[
                {"score": 90},
                {"score": 85},
            ],
            attempts=2,
            current_difficulty=MEDIUM,
        )
    )

    assert recommendation["difficulty"] == HARD
    assert recommendation["mastery"] == 85.0
    assert recommendation["attempts"] == 2
    assert "reason" in recommendation
    assert "trend" in recommendation