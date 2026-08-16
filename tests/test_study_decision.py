from src.ai.study_decision import (
    STUDY,
    REVIEW,
    PRACTICE_ACTION,
    CHALLENGE_ACTION,
    ADVANCE,
    make_study_decision,
    calculate_decision_confidence,
    select_best_study_decision,
)


def test_not_started_student_should_study():

    result = make_study_decision(
        topic="Morphology",
        mastery=0,
        status="NOT_STARTED",
        attempts=0,
        recent_performance=[],
    )

    assert result["decision"] == STUDY
    assert result["action"] == "LEARN"
    assert result["priority"] == "HIGH"


def test_weak_student_should_relearn():

    result = make_study_decision(
        topic="Morphology",
        mastery=25,
        status="WEAK",
        attempts=1,
        recent_performance=[
            {"score": 20}
        ],
    )

    assert result["decision"] == STUDY
    assert result["action"] == "RELEARN"


def test_revision_due_should_review():

    result = make_study_decision(
        topic="Automata",
        mastery=70,
        status="AVERAGE",
        attempts=2,
        recent_performance=[
            {"score": 70},
            {"score": 75},
        ],
        revision_due=True,
    )

    assert result["decision"] == REVIEW
    assert result["action"] == "REVISE"


def test_medium_mastery_should_practice():

    result = make_study_decision(
        topic="Syntax",
        mastery=60,
        status="AVERAGE",
        attempts=2,
        recent_performance=[
            {"score": 65},
            {"score": 60},
        ],
    )

    assert result["decision"] == PRACTICE_ACTION
    assert result["action"] == "PRACTICE"


def test_strong_student_should_challenge():

    result = make_study_decision(
        topic="Semantics",
        mastery=90,
        status="STRONG",
        attempts=3,
        recent_performance=[
            {"score": 95},
            {"score": 90},
        ],
    )

    assert result["decision"] == CHALLENGE_ACTION
    assert result["action"] == "CHALLENGE"


def test_move_forward_decision():

    result = make_study_decision(
        topic="Syntax",
        mastery=82,
        status="STRONG",
        attempts=3,
        recent_performance=[
            {"score": 80},
            {"score": 78},
        ],
    )

    assert result["decision"] == ADVANCE
    assert result["action"] == "MOVE_FORWARD"


def test_decision_contains_explanation():

    result = make_study_decision(
        topic="Morphology",
        mastery=25,
        status="WEAK",
        attempts=1,
        recent_performance=[
            {"score": 20}
        ],
    )

    assert result["reason"]
    assert result["next_step"]
    assert result["explanation"]


def test_decision_confidence_is_bounded():

    result = make_study_decision(
        topic="Syntax",
        mastery=90,
        status="STRONG",
        attempts=5,
        recent_performance=[
            {"score": 95},
            {"score": 90},
            {"score": 92},
        ],
        performance={
            "learning_state": "MASTERING"
        },
    )

    assert 0 <= result["confidence"] <= 1


def test_more_history_increases_confidence():

    low = calculate_decision_confidence(
        {
            "mastery": 60,
            "attempts": 0,
            "trend": "INSUFFICIENT_DATA",
        }
    )

    high = calculate_decision_confidence(
        {
            "mastery": 60,
            "attempts": 3,
            "trend": "STABLE",
        }
    )

    assert high > low


def test_select_best_decision():

    decisions = [

        {
            "topic": "Strong Topic",
            "action": "CHALLENGE",
            "priority": "LOW",
            "confidence": 0.9,
            "mastery": 90,
        },

        {
            "topic": "Weak Topic",
            "action": "RELEARN",
            "priority": "HIGH",
            "confidence": 0.7,
            "mastery": 25,
        },
    ]

    result = select_best_study_decision(
        decisions
    )

    assert result["topic"] == "Weak Topic"


def test_empty_decisions():

    assert (
        select_best_study_decision([])
        is None
    )