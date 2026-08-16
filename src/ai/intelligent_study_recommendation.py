# ============================================================
# INTELLIGENT STUDY RECOMMENDATION ENGINE
# StudyFlow AI
# Phase 10.4
# ============================================================

from src.ai.adaptive_difficulty import (
    get_adaptive_difficulty_recommendation,
)


# ============================================================
# STUDY ACTIONS
# ============================================================

LEARN = "LEARN"
RELEARN = "RELEARN"
REVISE = "REVISE"
PRACTICE = "PRACTICE"
CHALLENGE = "CHALLENGE"
MOVE_FORWARD = "MOVE_FORWARD"


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


def _normalize_status(status, mastery):
    normalized = str(status or "").strip().upper()

    if normalized in {"NOT_STARTED", "NOT STARTED"}:
        return "NOT_STARTED"

    if normalized == "WEAK":
        return "WEAK"

    if normalized in {"AVERAGE", "MEDIUM"}:
        return "AVERAGE"

    if normalized == "STRONG":
        return "STRONG"

    if mastery >= 80:
        return "STRONG"

    if mastery >= 50:
        return "AVERAGE"

    if mastery > 0:
        return "WEAK"

    return "NOT_STARTED"


# ============================================================
# RECENT PERFORMANCE
# ============================================================

def _recent_average(recent_performance):
    scores = []

    for item in recent_performance or []:
        score = _safe_float(
            item.get("score", item.get("accuracy", 0))
        )
        scores.append(score)

    if not scores:
        return 0.0

    return round(
        sum(scores) / len(scores),
        2
    )


def _calculate_trend(recent_performance):
    if len(recent_performance or []) < 2:
        return "INSUFFICIENT_DATA"

    latest = _safe_float(
        recent_performance[0].get(
            "score",
            recent_performance[0].get("accuracy", 0)
        )
    )

    previous = _safe_float(
        recent_performance[1].get(
            "score",
            recent_performance[1].get("accuracy", 0)
        )
    )

    change = latest - previous

    if change >= 5:
        return "IMPROVING"

    if change <= -5:
        return "DECLINING"

    return "STABLE"


# ============================================================
# INTELLIGENT DECISION
# ============================================================

def determine_study_action(
    mastery,
    status,
    attempts,
    recent_average,
    trend,
    revision_due=False,
):
    """
    Determine the most appropriate next study action.
    """

    mastery = _safe_float(mastery)
    attempts = _safe_int(attempts)
    recent_average = _safe_float(recent_average)

    normalized_status = _normalize_status(
        status,
        mastery
    )

    # --------------------------------------------------------
    # No learning history
    # --------------------------------------------------------

    if (
        normalized_status == "NOT_STARTED"
        and attempts == 0
    ):
        return LEARN

    # --------------------------------------------------------
    # Revision due
    # --------------------------------------------------------

    if revision_due:
        return REVISE

    # --------------------------------------------------------
    # Very weak mastery
    # --------------------------------------------------------

    if mastery < 40:
        return RELEARN

    # --------------------------------------------------------
    # Weak recent quiz performance
    # --------------------------------------------------------

    if recent_average < 50 and attempts > 0:
        return RELEARN

    # --------------------------------------------------------
    # Declining performance
    # --------------------------------------------------------

    if trend == "DECLINING":
        return REVISE

    # --------------------------------------------------------
    # Moderate mastery
    # --------------------------------------------------------

    if 40 <= mastery < 70:
        return PRACTICE

    # --------------------------------------------------------
    # Strong mastery + strong performance
    # --------------------------------------------------------

    if (
        mastery >= 85
        and recent_average >= 80
        and trend != "DECLINING"
    ):
        return CHALLENGE

    # --------------------------------------------------------
    # Good mastery
    # --------------------------------------------------------

    if mastery >= 80:
        return MOVE_FORWARD

    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    return PRACTICE


# ============================================================
# ACTION PRIORITY
# ============================================================

def get_action_priority(action):
    priorities = {
        LEARN: "HIGH",
        RELEARN: "HIGH",
        REVISE: "HIGH",
        PRACTICE: "MEDIUM",
        CHALLENGE: "LOW",
        MOVE_FORWARD: "LOW",
    }

    return priorities.get(
        action,
        "MEDIUM"
    )


# ============================================================
# ACTION MESSAGE
# ============================================================

def get_action_message(action, topic):
    topic = topic or "this topic"

    messages = {
        LEARN: (
            f"Start learning {topic} from the fundamentals "
            "and complete a practice quiz."
        ),

        RELEARN: (
            f"Relearn {topic}, focus on weak concepts, "
            "and then retake a practice quiz."
        ),

        REVISE: (
            f"Revise {topic} and review the concepts "
            "you previously studied."
        ),

        PRACTICE: (
            f"Practice {topic} with additional questions "
            "to strengthen your understanding."
        ),

        CHALLENGE: (
            f"You are ready for a harder challenge in "
            f"{topic}. Try a higher difficulty quiz."
        ),

        MOVE_FORWARD: (
            f"Your understanding of {topic} is strong. "
            "Continue to the next topic."
        ),
    }

    return messages.get(
        action,
        f"Continue studying {topic}."
    )


# ============================================================
# MAIN RECOMMENDATION
# ============================================================

def get_intelligent_study_recommendation(
    topic,
    mastery=None,
    status=None,
    attempts=0,
    recent_performance=None,
    revision_due=False,
    current_difficulty="MEDIUM",
):
    """
    Generate an intelligent study recommendation for one topic.

    This function combines:

        mastery
        quiz history
        recent performance
        performance trend
        revision state
        adaptive difficulty
    """

    topic = topic or "Unknown Topic"

    recent_performance = (
        recent_performance or []
    )

    mastery = _safe_float(
        mastery
    )

    attempts = _safe_int(
        attempts
    )

    recent_average = _recent_average(
        recent_performance
    )

    trend = _calculate_trend(
        recent_performance
    )

    normalized_status = _normalize_status(
        status,
        mastery
    )

    action = determine_study_action(
        mastery=mastery,
        status=normalized_status,
        attempts=attempts,
        recent_average=recent_average,
        trend=trend,
        revision_due=revision_due,
    )

    priority = get_action_priority(
        action
    )

    message = get_action_message(
        action,
        topic
    )

    # --------------------------------------------------------
    # Adaptive difficulty
    # --------------------------------------------------------

    difficulty = get_adaptive_difficulty_recommendation(
        mastery=mastery,
        recent_performance=recent_performance,
        attempts=attempts,
        current_difficulty=current_difficulty,
    )

    return {
        "topic": topic,

        "action": action,

        "priority": priority,

        "message": message,

        "mastery": round(
            mastery,
            2
        ),

        "status": normalized_status,

        "attempts": attempts,

        "recent_average": round(
            recent_average,
            2
        ),

        "trend": trend,

        "revision_due": bool(
            revision_due
        ),

        "difficulty": difficulty,
    }


# ============================================================
# STUDENT-LEVEL RECOMMENDATION
# ============================================================

def get_best_study_recommendation(
    recommendations
):
    """
    Select the most important study recommendation
    from multiple topic recommendations.
    """

    if not recommendations:
        return None

    priority_order = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    action_order = {
        RELEARN: 6,
        REVISE: 5,
        LEARN: 4,
        PRACTICE: 3,
        CHALLENGE: 2,
        MOVE_FORWARD: 1,
    }

    ranked = sorted(
        recommendations,
        key=lambda item: (
            priority_order.get(
                item.get("priority"),
                1
            ),

            action_order.get(
                item.get("action"),
                0
            ),

            100.0 - _safe_float(
                item.get("mastery")
            ),
        ),
        reverse=True,
    )

    return ranked[0]