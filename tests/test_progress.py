from src.ai.progress import (
    calculate_topic_progress,
    get_learning_recommendation
)


def test_strong_topic():

    progress = calculate_topic_progress(

        topic="Decision Trees",

        correct_answers=9,

        total_questions=10
    )

    assert progress.score_percentage == 90

    assert progress.status == "STRONG"

    recommendation = (
        get_learning_recommendation(
            progress
        )
    )

    assert (
        recommendation["action"]
        == "MOVE_FORWARD"
    )


def test_average_topic():

    progress = calculate_topic_progress(

        topic="Clustering",

        correct_answers=6,

        total_questions=10
    )

    assert progress.status == "AVERAGE"


def test_weak_topic():

    progress = calculate_topic_progress(

        topic="Entropy",

        correct_answers=3,

        total_questions=10
    )

    assert progress.score_percentage == 30

    assert progress.status == "WEAK"

    recommendation = (
        get_learning_recommendation(
            progress
        )
    )

    assert (
        recommendation["action"]
        == "RELEARN"
    )