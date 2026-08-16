from src.ai.progress_schema import TopicProgress

from src.ai.adaptive_planner import (
    get_adaptive_action,
)

from src.ai.recommendation import (
    calculate_adaptive_score,
)


def test_action():

    progress = TopicProgress(

        topic="Test Topic",

        attempts=2,

        correct_answers=4,

        total_questions=10,

        score_percentage=40,

        status="WEAK",
    )

    result = get_adaptive_action(
        progress
    )

    print(
        "\nACTION TEST"
    )

    print(result)

    assert result["action"] == "RELEARN"


def test_score():

    progress = TopicProgress(

        topic="Test Topic",

        attempts=2,

        correct_answers=4,

        total_questions=10,

        score_percentage=40,

        status="WEAK",
    )

    topic = {

        "progress": progress,

        "base_score": 3.0,

        "quiz_stats": {

            "attempts": 2,

            "accuracy": 40.0,
        },

        "improvement": -10.0,
    }

    score = calculate_adaptive_score(
        topic
    )

    print(
        "\nADAPTIVE SCORE TEST"
    )

    print(
        "Score:",
        score
    )

    assert score > 3.0


if __name__ == "__main__":

    test_action()

    test_score()

    print(
        "\n✅ Adaptive engine tests passed."
    )