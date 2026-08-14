from src.ai.adaptive_planner import (
    calculate_adaptive_weight,
    get_adaptive_action,
    prioritize_topics
)

from src.ai.progress_schema import (
    TopicProgress
)


def test_weak_topic_gets_high_weight():

    progress = TopicProgress(
        topic="Entropy",
        attempts=1,
        correct_answers=3,
        total_questions=10,
        score_percentage=30,
        status="WEAK"
    )

    weight = calculate_adaptive_weight(
        progress
    )

    assert weight == 2.0


def test_strong_topic_gets_lower_weight():

    progress = TopicProgress(
        topic="Decision Trees",
        attempts=1,
        correct_answers=9,
        total_questions=10,
        score_percentage=90,
        status="STRONG"
    )

    weight = calculate_adaptive_weight(
        progress
    )

    assert weight == 0.75


def test_adaptive_action():

    progress = TopicProgress(
        topic="Entropy",
        attempts=1,
        correct_answers=3,
        total_questions=10,
        score_percentage=30,
        status="WEAK"
    )

    action = get_adaptive_action(
        progress
    )

    assert action["action"] == "RELEARN"

    assert action["priority"] == "HIGH"


def test_topic_prioritization():

    weak_progress = TopicProgress(
        topic="Entropy",
        attempts=1,
        correct_answers=3,
        total_questions=10,
        score_percentage=30,
        status="WEAK"
    )

    strong_progress = TopicProgress(
        topic="Decision Trees",
        attempts=1,
        correct_answers=9,
        total_questions=10,
        score_percentage=90,
        status="STRONG"
    )

    topics = [

        {
            "topic": "Entropy",
            "progress": weak_progress,
            "base_score": 1.5
        },

        {
            "topic": "Decision Trees",
            "progress": strong_progress,
            "base_score": 1.5
        }
    ]

    ranked = prioritize_topics(
        topics
    )

    assert ranked[0]["topic"] == "Entropy"