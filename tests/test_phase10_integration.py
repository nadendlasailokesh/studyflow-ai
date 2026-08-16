# ============================================================
# PHASE 10.8
# ADVANCED AI STUDY COACH - INTEGRATION TESTS
# StudyFlow AI
# ============================================================

import pytest

from src.ai.student_performance import (
    analyze_student_performance,
)

from src.ai.personalized_recommendation import (
    get_personalized_recommendation,
)

from src.ai.adaptive_difficulty import (
    get_adaptive_difficulty_recommendation,
)

from src.ai.intelligent_study_recommendation import (
    get_intelligent_study_recommendation,
)

from src.ai.personalized_explanation import (
    generate_personalized_explanation,
)

from src.ai.study_decision import (
    make_study_decision,
)


# ============================================================
# HELPERS
# ============================================================

def weak_topic():
    return {
        "id": 1,
        "name": "Morphology",
        "unit": "Unit 1",
        "priority": "HIGH",
        "mastery": 25,
        "status": "WEAK",
    }


def strong_topic():
    return {
        "id": 2,
        "name": "Syntax",
        "unit": "Unit 2",
        "priority": "HIGH",
        "mastery": 90,
        "status": "STRONG",
    }


# ============================================================
# 10.8.1
# PERFORMANCE -> RECOMMENDATION
# ============================================================

def test_performance_to_personalized_recommendation(
    monkeypatch
):
    """
    Verify that student performance analysis can feed
    the personalized recommendation engine.
    """

    performance = {
        "student_id": 1,
        "learning_state": "STRUGGLING",

        "mastery": {
            "average": 25.0,
            "strong_topics": 0,
            "average_topics": 0,
            "weak_topics": 1,
            "not_started_topics": 0,
            "completed_topics": 0,
            "total_topics": 1,
            "coverage": 100.0,
        },

        "quiz": {
            "attempts": 1,
            "total_questions": 5,
            "correct_answers": 1,
            "average_score": 20.0,
            "best_score": 20.0,
            "lowest_score": 20.0,
            "topics_attempted": 1,
            "coverage": 100.0,
        },

        "trend": {
            "status": "INSUFFICIENT_DATA",
            "change": 0.0,
            "first_score": 20.0,
            "latest_score": 20.0,
            "highest_score": 20.0,
            "lowest_score": 20.0,
        },

        "consistency": {
            "level": "LOW",
            "score": 0.25,
        },

        "confidence": 0.52,
    }

    monkeypatch.setattr(
        "src.ai.personalized_recommendation.analyze_student_performance",
        lambda student_id: performance,
    )

    recommendation = get_personalized_recommendation(
        student_id=1,
        topics=[weak_topic()],
    )

    assert recommendation is not None

    assert (
        recommendation["topic"]
        == "Morphology"
    )

    assert recommendation["performance"] is not None


# ============================================================
# 10.8.2
# PERFORMANCE -> ADAPTIVE DIFFICULTY
# ============================================================

def test_performance_to_adaptive_difficulty():

    result = get_adaptive_difficulty_recommendation(
        mastery=25,
        recent_performance=[
            {
                "score": 20
            }
        ],
        attempts=1,
        current_difficulty="MEDIUM",
    )

    assert result["difficulty"] == "EASY"

    assert (
        result["previous_difficulty"]
        == "MEDIUM"
    )

    assert (
        result["mastery"]
        == 25.0
    )

    assert (
        result["attempts"]
        == 1
    )


# ============================================================
# 10.8.3
# STRONG PERFORMANCE -> HARD DIFFICULTY
# ============================================================

def test_strong_performance_to_hard_difficulty():

    result = get_adaptive_difficulty_recommendation(
        mastery=90,
        recent_performance=[
            {
                "score": 95
            },
            {
                "score": 90
            },
        ],
        attempts=2,
        current_difficulty="MEDIUM",
    )

    assert result["difficulty"] == "HARD"

    assert (
        result["previous_difficulty"]
        == "MEDIUM"
    )

    assert (
        result["recent_average"]
        == 92.5
    )


# ============================================================
# 10.8.4
# PERSONALIZED RECOMMENDATION ->
# INTELLIGENT STUDY RECOMMENDATION
# ============================================================

def test_personalized_recommendation_to_intelligent_recommendation():

    topic = weak_topic()

    result = get_intelligent_study_recommendation(

        topic=topic["name"],

        mastery=topic["mastery"],

        status=topic["status"],

        attempts=1,

        recent_performance=[
            {
                "score": 20
            }
        ],

        current_difficulty="MEDIUM",
    )

    assert result is not None

    assert (
        result["topic"]
        == "Morphology"
    )

    assert (
        result["action"]
        == "RELEARN"
    )

    assert (
        result["priority"]
        == "HIGH"
    )

    assert (
        result["difficulty"]["difficulty"]
        == "EASY"
    )


# ============================================================
# 10.8.5
# INTELLIGENT RECOMMENDATION ->
# PERSONALIZED EXPLANATION
# ============================================================

def test_recommendation_to_personalized_explanation():

    recommendation = (
        get_intelligent_study_recommendation(

            topic="Morphology",

            mastery=25,

            status="WEAK",

            attempts=1,

            recent_performance=[
                {
                    "score": 20
                }
            ],

            current_difficulty="MEDIUM",
        )
    )

    performance = {
        "learning_state": "STRUGGLING",

        "mastery": {
            "average": 25.0,
            "strong_topics": 0,
            "average_topics": 0,
            "weak_topics": 1,
            "not_started_topics": 0,
            "completed_topics": 0,
            "total_topics": 1,
            "coverage": 100.0,
        },

        "quiz": {
            "attempts": 1,
            "total_questions": 5,
            "correct_answers": 1,
            "average_score": 20.0,
            "best_score": 20.0,
            "lowest_score": 20.0,
            "topics_attempted": 1,
            "coverage": 100.0,
        },

        "trend": {
            "status": "INSUFFICIENT_DATA",
            "change": 0.0,
            "first_score": 20.0,
            "latest_score": 20.0,
            "highest_score": 20.0,
            "lowest_score": 20.0,
        },

        "consistency": {
            "level": "LOW",
            "score": 0.25,
        },

        "confidence": 0.52,
    }

    explanation = (
        generate_personalized_explanation(
            recommendation,
            performance,
        )
    )

    assert explanation is not None

    assert (
        explanation["topic"]
        == "Morphology"
    )

    assert explanation["action"] == "RELEARN"

    assert explanation["summary"]

    assert explanation["why"]

    assert explanation["performance"]

    assert explanation["next_steps"]


# ============================================================
# 10.8.6
# PERSONALIZED EXPLANATION ->
# STUDY DECISION
# ============================================================

def test_personalized_decision_for_weak_topic():

    performance = {
        "learning_state": "STRUGGLING",
        "confidence": 0.52,
    }

    decision = make_study_decision(

        topic="Morphology",

        mastery=25,

        status="WEAK",

        attempts=1,

        recent_performance=[
            {
                "score": 20
            }
        ],

        performance=performance,
    )

    assert decision is not None

    assert (
        decision["decision"]
        == "STUDY"
    )

    assert (
        decision["action"]
        == "RELEARN"
    )

    assert (
        decision["priority"]
        == "HIGH"
    )

    assert (
        decision["difficulty"]["difficulty"]
        == "EASY"
    )

    assert decision["reason"]

    assert decision["next_step"]

    assert decision["explanation"]


# ============================================================
# 10.8.7
# STRONG STUDENT -> CHALLENGE DECISION
# ============================================================

def test_strong_student_gets_challenge_decision():

    performance = {
        "learning_state": "MASTERING",
        "confidence": 0.90,
    }

    decision = make_study_decision(

        topic="Syntax",

        mastery=90,

        status="STRONG",

        attempts=3,

        recent_performance=[
            {
                "score": 95
            },
            {
                "score": 90
            },
        ],

        performance=performance,
    )

    assert decision is not None

    assert (
        decision["decision"]
        == "CHALLENGE"
    )

    assert (
        decision["action"]
        == "CHALLENGE"
    )

    assert (
        decision["priority"]
        == "LOW"
    )

    assert (
        decision["difficulty"]["difficulty"]
        == "HARD"
    )

    assert decision["reason"]

    assert decision["next_step"]


# ============================================================
# 10.8.8
# COMPLETE AI DECISION PIPELINE
# ============================================================

def test_complete_phase10_ai_pipeline():

    topic = weak_topic()

    # --------------------------------------------------------
    # Step 1: Adaptive difficulty
    # --------------------------------------------------------

    difficulty = (
        get_adaptive_difficulty_recommendation(

            mastery=topic["mastery"],

            recent_performance=[
                {
                    "score": 20
                }
            ],

            attempts=1,

            current_difficulty="MEDIUM",
        )
    )

    assert difficulty["difficulty"] == "EASY"

    # --------------------------------------------------------
    # Step 2: Intelligent recommendation
    # --------------------------------------------------------

    recommendation = (
        get_intelligent_study_recommendation(

            topic=topic["name"],

            mastery=topic["mastery"],

            status=topic["status"],

            attempts=1,

            recent_performance=[
                {
                    "score": 20
                }
            ],

            current_difficulty="MEDIUM",
        )
    )

    assert recommendation["action"] == "RELEARN"

    # --------------------------------------------------------
    # Step 3: Study decision
    # --------------------------------------------------------

    decision = make_study_decision(

        topic=topic["name"],

        mastery=topic["mastery"],

        status=topic["status"],

        attempts=1,

        recent_performance=[
            {
                "score": 20
            }
        ],

        performance={
            "learning_state": "STRUGGLING",
            "confidence": 0.52,
        },
    )

    assert decision["decision"] == "STUDY"

    assert decision["action"] == "RELEARN"

    # --------------------------------------------------------
    # Step 4: Verify difficulty propagated
    # --------------------------------------------------------

    assert (
        decision["difficulty"]["difficulty"]
        == "EASY"
    )

    # --------------------------------------------------------
    # Step 5: Verify explanation exists
    # --------------------------------------------------------

    assert decision["explanation"] is not None

    assert decision["explanation"]["topic"] == (
        "Morphology"
    )


# ============================================================
# 10.8.9
# EMPTY / LOW-DATA SAFETY
# ============================================================

def test_phase10_handles_no_quiz_history():

    result = get_intelligent_study_recommendation(

        topic="Semantics",

        mastery=0,

        status="NOT_STARTED",

        attempts=0,

        recent_performance=[],

        current_difficulty="MEDIUM",
    )

    assert result is not None

    # A topic that has never been studied should
    # start with the LEARN action.
    assert result["action"] == "LEARN"

    assert result["priority"] == "HIGH"

    assert (
        result["difficulty"]["difficulty"]
        == "MEDIUM"
    )

    assert (
        result["difficulty"]["attempts"]
        == 0
    )

    assert (
        result["difficulty"]["trend"]
        == "INSUFFICIENT_DATA"
    )


# ============================================================
# 10.8.10
# PHASE 10 OUTPUT CONTRACT
# ============================================================

def test_phase10_decision_output_contract():

    result = make_study_decision(

        topic="Morphology",

        mastery=25,

        status="WEAK",

        attempts=1,

        recent_performance=[
            {
                "score": 20
            }
        ],

        performance={
            "learning_state": "STRUGGLING",
            "confidence": 0.52,
        },
    )

    required_fields = {
        "topic",
        "decision",
        "action",
        "priority",
        "confidence",
        "reason",
        "next_step",
        "mastery",
        "status",
        "trend",
        "recent_average",
        "attempts",
        "difficulty",
        "explanation",
    }

    assert required_fields.issubset(
        result.keys()
    )

    assert isinstance(
        result["confidence"],
        float,
    )

    assert 0.0 <= result["confidence"] <= 1.0

    assert isinstance(
        result["difficulty"],
        dict,
    )

    assert isinstance(
        result["explanation"],
        dict,
    )