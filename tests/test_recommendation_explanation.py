from src.ai.recommendation_explanation import (
    generate_recommendation_reasons,
    get_recommendation_summary
)

from src.ai.progress_schema import TopicProgress


def create_recommendation():

    progress = TopicProgress(
        topic="Morphology",
        attempts=0,
        correct_answers=0,
        total_questions=0,
        score_percentage=0,
        status="NOT_STARTED"
    )

    return {
        "topic": "Morphology",

        "topic_data": {
            "name": "Morphology",
            "priority": "HIGH"
        },

        "progress": progress,

        "adaptive_score": 8.0,

        "quiz_stats": {
            "attempts": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "accuracy": 0
        },

        "improvement": 0.0
    }


def test_generate_recommendation_reasons():

    recommendation = create_recommendation()

    reasons = generate_recommendation_reasons(
        recommendation
    )

    assert len(reasons) > 0

    combined = " ".join(
        reasons
    )

    assert "HIGH priority" in combined

    assert "mastery" in combined.lower()

    assert "quiz history" in combined.lower()


def test_recommendation_summary():

    recommendation = create_recommendation()

    summary = get_recommendation_summary(
        recommendation
    )

    assert "Morphology" in summary

    assert len(summary) > 20


def test_empty_recommendation():

    assert (
        generate_recommendation_reasons(None)
        == []
    )

    assert (
        get_recommendation_summary(None)
        == "No recommendation is currently available."
    )