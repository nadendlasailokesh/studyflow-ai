# ============================================================
# PHASE 10.2 TESTS
# Personalized Recommendations
# ============================================================

from src.ai.personalized_recommendation import (
    calculate_trend_factor,
    calculate_personalization_score,
)


# ============================================================
# TREND FACTOR
# ============================================================

def test_declining_trend_increases_priority():

    factor = calculate_trend_factor(
        trend_status="DECLINING",
        trend_change=-20,
    )

    assert factor > 1.0


def test_improving_trend_reduces_priority():

    factor = calculate_trend_factor(
        trend_status="IMPROVING",
        trend_change=20,
    )

    assert factor < 1.0


def test_stable_trend_is_neutral():

    factor = calculate_trend_factor(
        trend_status="STABLE",
        trend_change=0,
    )

    assert factor == 1.0


def test_insufficient_trend_is_neutral():

    factor = calculate_trend_factor(
        trend_status="INSUFFICIENT_DATA",
        trend_change=0,
    )

    assert factor == 1.0


# ============================================================
# PERSONALIZATION SCORE
# ============================================================

def test_weak_topic_gets_personalized_score():

    topic = {

        "adaptive_score": 5.0,

        "progress": type(
            "Progress",
            (),
            {
                "score_percentage": 20.0,
            },
        )(),

        "quiz_stats": {

            "attempts": 1,

            "accuracy": 20.0,
        },

        "topic_data": {

            "priority": "HIGH",
        },
    }

    performance = {

        "trend": {

            "status":
                "INSUFFICIENT_DATA",

            "change":
                0.0,
        },
    }

    score = calculate_personalization_score(
        topic_recommendation=topic,
        performance=performance,
    )

    assert score > 0


def test_high_priority_topic_scores_higher():

    base_topic = {

        "adaptive_score": 3.0,

        "progress": type(
            "Progress",
            (),
            {
                "score_percentage": 40.0,
            },
        )(),

        "quiz_stats": {

            "attempts": 1,

            "accuracy": 40.0,
        },

        "topic_data": {

            "priority": "MEDIUM",
        },
    }

    high_topic = dict(
        base_topic
    )

    high_topic["topic_data"] = {
        "priority": "HIGH"
    }

    performance = {

        "trend": {

            "status":
                "INSUFFICIENT_DATA",

            "change":
                0.0,
        },
    }

    normal_score = calculate_personalization_score(
        topic_recommendation=base_topic,
        performance=performance,
    )

    high_score = calculate_personalization_score(
        topic_recommendation=high_topic,
        performance=performance,
    )

    assert high_score > normal_score