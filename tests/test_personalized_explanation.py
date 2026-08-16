from src.ai.personalized_explanation import (
    generate_personalized_explanation,
    get_personalized_summary,
)


def test_relearn_explanation():

    recommendation = {
        "topic": "Morphology",
        "action": "RELEARN",
        "mastery": 25,
        "attempts": 1,
        "recent_average": 20,
        "trend": "INSUFFICIENT_DATA",
        "difficulty": {
            "difficulty": "EASY",
            "previous_difficulty": "MEDIUM",
            "reason": "Low mastery requires easier practice.",
        },
    }

    performance = {
        "learning_state": "STRUGGLING"
    }

    result = generate_personalized_explanation(
        recommendation,
        performance,
    )

    assert result["topic"] == "Morphology"
    assert result["action"] == "RELEARN"
    assert result["why"]
    assert result["performance"]
    assert result["difficulty"]
    assert result["next_steps"]


def test_challenge_explanation():

    recommendation = {
        "topic": "Syntax",
        "action": "CHALLENGE",
        "mastery": 90,
        "attempts": 2,
        "recent_average": 92.5,
        "trend": "IMPROVING",
        "difficulty": {
            "difficulty": "HARD",
            "previous_difficulty": "MEDIUM",
            "reason": "Strong performance supports a harder challenge.",
        },
    }

    performance = {
        "learning_state": "MASTERING"
    }

    result = generate_personalized_explanation(
        recommendation,
        performance,
    )

    assert result["action"] == "CHALLENGE"

    assert any(
        "strong" in text.lower()
        for text in result["performance"]
    )


def test_revision_explanation():

    recommendation = {
        "topic": "Automata",
        "action": "REVISE",
        "mastery": 65,
        "attempts": 3,
        "recent_average": 55,
        "trend": "DECLINING",
        "difficulty": {
            "difficulty": "MEDIUM",
            "previous_difficulty": "MEDIUM",
            "reason": "Current performance requires continued practice.",
        },
    }

    result = generate_personalized_explanation(
        recommendation
    )

    assert result["action"] == "REVISE"

    assert any(
        "declining" in text.lower()
        for text in result["performance"]
    )


def test_learning_explanation():

    recommendation = {
        "topic": "Phonetics",
        "action": "LEARN",
        "mastery": 0,
        "attempts": 0,
        "recent_average": 0,
        "trend": "INSUFFICIENT_DATA",
        "difficulty": {
            "difficulty": "EASY",
            "previous_difficulty": "MEDIUM",
        },
    }

    result = generate_personalized_explanation(
        recommendation
    )

    assert result["action"] == "LEARN"

    assert len(
        result["next_steps"]
    ) >= 2


def test_practice_explanation():

    recommendation = {
        "topic": "Semantics",
        "action": "PRACTICE",
        "mastery": 60,
        "attempts": 2,
        "recent_average": 65,
        "trend": "STABLE",
        "difficulty": {
            "difficulty": "MEDIUM",
            "previous_difficulty": "MEDIUM",
        },
    }

    result = generate_personalized_explanation(
        recommendation
    )

    assert result["action"] == "PRACTICE"


def test_move_forward_explanation():

    recommendation = {
        "topic": "Syntax",
        "action": "MOVE_FORWARD",
        "mastery": 82,
        "attempts": 3,
        "recent_average": 80,
        "trend": "STABLE",
        "difficulty": {
            "difficulty": "MEDIUM",
            "previous_difficulty": "MEDIUM",
        },
    }

    result = generate_personalized_explanation(
        recommendation
    )

    assert result["action"] == "MOVE_FORWARD"


def test_empty_recommendation():

    result = generate_personalized_explanation(
        None
    )

    assert result["topic"] == ""
    assert result["why"] == []
    assert result["next_steps"] == []


def test_personalized_summary():

    recommendation = {
        "topic": "Morphology",
        "action": "RELEARN",
        "mastery": 25,
        "attempts": 1,
        "recent_average": 20,
        "trend": "INSUFFICIENT_DATA",
    }

    result = generate_personalized_explanation(
        recommendation
    )

    summary = get_personalized_summary(
        result
    )

    assert summary
    assert "Morphology" in summary