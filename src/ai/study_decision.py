# ============================================================
# AI-DRIVEN STUDY DECISION ENGINE
# StudyFlow AI
# Phase 10.6
# ============================================================

from src.ai.intelligent_study_recommendation import (
    LEARN,
    RELEARN,
    REVISE,
    PRACTICE,
    CHALLENGE,
    MOVE_FORWARD,
    get_intelligent_study_recommendation,
)

from src.ai.personalized_explanation import (
    generate_personalized_explanation,
)


# ============================================================
# DECISION TYPES
# ============================================================

STUDY = "STUDY"
REVIEW = "REVIEW"
PRACTICE_ACTION = "PRACTICE"
CHALLENGE_ACTION = "CHALLENGE"
ADVANCE = "ADVANCE"


# ============================================================
# ACTION → DECISION
# ============================================================

ACTION_TO_DECISION = {
    LEARN: STUDY,
    RELEARN: STUDY,
    REVISE: REVIEW,
    PRACTICE: PRACTICE_ACTION,
    CHALLENGE: CHALLENGE_ACTION,
    MOVE_FORWARD: ADVANCE,
}


# ============================================================
# HELPERS
# ============================================================

def _safe_float(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


# ============================================================
# NEXT STEP
# ============================================================

def _get_next_step(action):

    steps = {

        LEARN:
            "Study the topic and then complete a practice quiz.",

        RELEARN:
            "Review the topic carefully and retake a practice quiz.",

        REVISE:
            "Revise the topic and complete questions to reinforce retention.",

        PRACTICE:
            "Complete additional practice questions and check your mistakes.",

        CHALLENGE:
            "Attempt a harder quiz and apply the concepts to new questions.",

        MOVE_FORWARD:
            "Continue to the next topic while keeping this topic in revision.",
    }

    return steps.get(
        action,
        "Continue studying and complete a practice quiz."
    )


# ============================================================
# DECISION CONFIDENCE
# ============================================================

def calculate_decision_confidence(
    recommendation,
    performance=None,
):

    performance = performance or {}

    confidence = 0.50

    attempts = _safe_int(
        recommendation.get(
            "attempts",
            0
        )
    )

    mastery = _safe_float(
        recommendation.get(
            "mastery",
            0
        )
    )

    trend = str(
        recommendation.get(
            "trend",
            ""
        )
    ).upper()

    learning_state = str(
        performance.get(
            "learning_state",
            ""
        )
    ).upper()

    # More quiz history gives more confidence.
    if attempts >= 3:
        confidence += 0.15

    elif attempts >= 2:
        confidence += 0.10

    elif attempts == 1:
        confidence += 0.05

    # Strong mastery boundaries provide clearer decisions.
    if mastery >= 80 or mastery < 30:
        confidence += 0.10

    elif mastery >= 50:
        confidence += 0.05

    # Clear trend increases confidence.
    if trend in {
        "IMPROVING",
        "DECLINING",
        "STABLE",
    }:
        confidence += 0.10

    # Performance analysis provides another signal.
    if learning_state in {
        "STRUGGLING",
        "DEVELOPING",
        "MASTERING",
    }:
        confidence += 0.05

    return round(
        min(
            confidence,
            1.0
        ),
        2
    )


# ============================================================
# DECISION REASON
# ============================================================

def _build_decision_reason(
    action,
    recommendation,
):

    topic = recommendation.get(
        "topic",
        "this topic"
    )

    mastery = _safe_float(
        recommendation.get(
            "mastery",
            0
        )
    )

    trend = str(
        recommendation.get(
            "trend",
            "INSUFFICIENT_DATA"
        )
    ).upper()

    recent_average = _safe_float(
        recommendation.get(
            "recent_average",
            0
        )
    )

    revision_due = bool(
        recommendation.get(
            "revision_due",
            False
        )
    )

    if revision_due:

        return (
            f"{topic} is due for revision, so reviewing it "
            "is currently the most useful action."
        )

    if action == LEARN:

        return (
            f"{topic} has not been sufficiently studied yet. "
            "Learning the fundamentals is the best next step."
        )

    if action == RELEARN:

        return (
            f"{topic} currently has {mastery:.0f}% mastery"
            + (
                f" and recent performance is around "
                f"{recent_average:.0f}%."
                if recent_average > 0
                else "."
            )
            + " Strengthening the topic is recommended "
              "before progressing."
        )

    if action == REVISE:

        if trend == "DECLINING":

            return (
                f"Performance on {topic} is declining, "
                "so revision should reinforce the concepts "
                "before further progression."
            )

        return (
            f"{topic} has already been studied, but "
            "revision will help strengthen retention."
        )

    if action == PRACTICE:

        return (
            f"{topic} has developing mastery at "
            f"{mastery:.0f}%. Additional practice will "
            "help strengthen understanding."
        )

    if action == CHALLENGE:

        return (
            f"{topic} has strong mastery at "
            f"{mastery:.0f}% and recent performance is "
            "strong enough for a harder challenge."
        )

    if action == MOVE_FORWARD:

        return (
            f"{topic} has strong mastery at "
            f"{mastery:.0f}%, so continuing to the next "
            "topic is appropriate."
        )

    return (
        f"Continue working on {topic} according to "
        "your current learning progress."
    )


# ============================================================
# MAIN DECISION ENGINE
# ============================================================

def make_study_decision(
    topic,
    mastery=0,
    status=None,
    attempts=0,
    recent_performance=None,
    revision_due=False,
    current_difficulty="MEDIUM",
    performance=None,
):
    """
    Produce the final AI-driven study decision.

    This is the orchestration layer for Phase 10.6.

    It does not modify the database.
    """

    recommendation = (
        get_intelligent_study_recommendation(

            topic=topic,

            mastery=mastery,

            status=status,

            attempts=attempts,

            recent_performance=(
                recent_performance or []
            ),

            revision_due=revision_due,

            current_difficulty=current_difficulty,
        )
    )

    action = recommendation[
        "action"
    ]

    decision = ACTION_TO_DECISION.get(
        action,
        PRACTICE_ACTION
    )

    confidence = calculate_decision_confidence(
        recommendation,
        performance,
    )

    reason = _build_decision_reason(
        action,
        recommendation,
    )

    next_step = _get_next_step(
        action
    )

    explanation = (
        generate_personalized_explanation(
            recommendation,
            performance,
        )
    )

    return {

        "topic":
            topic,

        "decision":
            decision,

        "action":
            action,

        "priority":
            recommendation[
                "priority"
            ],

        "confidence":
            confidence,

        "reason":
            reason,

        "next_step":
            next_step,

        "mastery":
            recommendation[
                "mastery"
            ],

        "status":
            recommendation[
                "status"
            ],

        "trend":
            recommendation[
                "trend"
            ],

        "recent_average":
            recommendation[
                "recent_average"
            ],

        "attempts":
            recommendation[
                "attempts"
            ],

        "difficulty":
            recommendation[
                "difficulty"
            ],

        "explanation":
            explanation,
    }


# ============================================================
# MULTI-TOPIC DECISION
# ============================================================

def select_best_study_decision(
    decisions
):
    """
    Select the highest-priority decision from multiple topics.
    """

    if not decisions:
        return None

    priority_weight = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    decision_weight = {
        RELEARN: 6,
        REVISE: 5,
        LEARN: 4,
        PRACTICE: 3,
        CHALLENGE: 2,
        MOVE_FORWARD: 1,
    }

    ranked = sorted(
        decisions,
        key=lambda item: (

            priority_weight.get(
                item.get(
                    "priority"
                ),
                1
            ),

            decision_weight.get(
                item.get(
                    "action"
                ),
                0
            ),

            item.get(
                "confidence",
                0
            ),

            -item.get(
                "mastery",
                0
            ),
        ),

        reverse=True,
    )

    return ranked[0]