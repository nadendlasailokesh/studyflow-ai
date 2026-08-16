from src.ai.intelligent_study_recommendation import (
    LEARN,
    RELEARN,
    REVISE,
    PRACTICE,
    CHALLENGE,
    MOVE_FORWARD,
    determine_study_action,
    get_intelligent_study_recommendation,
    get_best_study_recommendation,
)


def test_not_started_topic_should_be_learn():

    action = determine_study_action(
        mastery=0,
        status="NOT_STARTED",
        attempts=0,
        recent_average=0,
        trend="INSUFFICIENT_DATA",
    )

    assert action == LEARN


def test_low_mastery_should_relearn():

    action = determine_study_action(
        mastery=25,
        status="WEAK",
        attempts=1,
        recent_average=20,
        trend="INSUFFICIENT_DATA",
    )

    assert action == RELEARN


def test_revision_due_should_revise():

    action = determine_study_action(
        mastery=75,
        status="AVERAGE",
        attempts=2,
        recent_average=70,
        trend="STABLE",
        revision_due=True,
    )

    assert action == REVISE


def test_declining_performance_should_revise():

    action = determine_study_action(
        mastery=65,
        status="AVERAGE",
        attempts=3,
        recent_average=55,
        trend="DECLINING",
    )

    assert action == REVISE


def test_medium_mastery_should_practice():

    action = determine_study_action(
        mastery=60,
        status="AVERAGE",
        attempts=2,
        recent_average=65,
        trend="STABLE",
    )

    assert action == PRACTICE


def test_high_mastery_should_challenge():

    action = determine_study_action(
        mastery=90,
        status="STRONG",
        attempts=3,
        recent_average=92,
        trend="IMPROVING",
    )

    assert action == CHALLENGE


def test_strong_topic_can_move_forward():

    action = determine_study_action(
        mastery=82,
        status="STRONG",
        attempts=3,
        recent_average=75,
        trend="STABLE",
    )

    assert action == MOVE_FORWARD


def test_recommendation_contains_required_fields():

    recommendation = (
        get_intelligent_study_recommendation(
            topic="Morphology",
            mastery=25,
            status="WEAK",
            attempts=1,
            recent_performance=[
                {"score": 20}
            ],
        )
    )

    assert recommendation["topic"] == "Morphology"
    assert recommendation["action"] == RELEARN
    assert recommendation["priority"] == "HIGH"
    assert recommendation["mastery"] == 25.0
    assert recommendation["attempts"] == 1
    assert "difficulty" in recommendation


def test_recent_average_is_calculated():

    recommendation = (
        get_intelligent_study_recommendation(
            topic="Syntax",
            mastery=60,
            status="AVERAGE",
            attempts=2,
            recent_performance=[
                {"score": 80},
                {"score": 60},
            ],
        )
    )

    assert recommendation["recent_average"] == 70.0


def test_best_recommendation_prioritizes_relearn():

    recommendations = [

        {
            "topic": "Strong Topic",
            "action": MOVE_FORWARD,
            "priority": "LOW",
            "mastery": 90,
        },

        {
            "topic": "Weak Topic",
            "action": RELEARN,
            "priority": "HIGH",
            "mastery": 25,
        },
    ]

    result = get_best_study_recommendation(
        recommendations
    )

    assert result["topic"] == "Weak Topic"


def test_empty_recommendations():

    result = get_best_study_recommendation([])

    assert result is None