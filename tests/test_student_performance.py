# ============================================================
# PHASE 10.1 TESTS
# Student Performance Analysis
# ============================================================

from src.ai.student_performance import (
    determine_learning_state,
    calculate_consistency,
    calculate_analysis_confidence,
)


# ============================================================
# LEARNING STATE
# ============================================================

def test_not_started_learning_state():

    result = determine_learning_state(
        mastery=0,
        quiz_accuracy=0,
        attempts=0,
    )

    assert result == "NOT_STARTED"


def test_struggling_learning_state():

    result = determine_learning_state(
        mastery=20,
        quiz_accuracy=20,
        attempts=1,
    )

    assert result == "STRUGGLING"


def test_developing_learning_state():

    result = determine_learning_state(
        mastery=60,
        quiz_accuracy=65,
        attempts=3,
    )

    assert result == "DEVELOPING"


def test_strong_learning_state():

    result = determine_learning_state(
        mastery=90,
        quiz_accuracy=90,
        attempts=5,
    )

    assert result == "STRONG"


# ============================================================
# CONSISTENCY
# ============================================================

def test_consistency_no_attempts():

    result = calculate_consistency(
        attempts=0,
        trend="NO_DATA",
    )

    assert result["level"] == "UNKNOWN"
    assert result["score"] == 0.0


def test_consistency_one_attempt():

    result = calculate_consistency(
        attempts=1,
        trend="INSUFFICIENT_DATA",
    )

    assert result["level"] == "LOW"


def test_consistency_multiple_attempts():

    result = calculate_consistency(
        attempts=5,
        trend="STABLE",
    )

    assert result["level"] == "HIGH"
    assert result["score"] == 1.0


# ============================================================
# CONFIDENCE
# ============================================================

def test_confidence_without_quiz_history():

    result = calculate_analysis_confidence(
        attempts=0,
        total_topics=29,
        trend="NO_DATA",
    )

    assert result >= 0
    assert result <= 1


def test_confidence_increases_with_history():

    low = calculate_analysis_confidence(
        attempts=1,
        total_topics=29,
        trend="INSUFFICIENT_DATA",
    )

    high = calculate_analysis_confidence(
        attempts=5,
        total_topics=29,
        trend="STABLE",
    )

    assert high > low