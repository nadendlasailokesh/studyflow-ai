# ============================================================
# PERSONALIZED EXPLANATION ENGINE
# StudyFlow AI
# Phase 10.5
# ============================================================

from src.ai.intelligent_study_recommendation import (
    LEARN,
    RELEARN,
    REVISE,
    PRACTICE,
    CHALLENGE,
    MOVE_FORWARD,
)


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


def _normalize_text(value):
    return str(value or "").strip()


# ============================================================
# ACTION EXPLANATIONS
# ============================================================

def _get_action_explanation(
    action,
    topic,
    mastery,
    attempts,
):
    """
    Explain the selected study action.
    """

    if action == LEARN:
        return (
            f"{topic} has not been sufficiently studied yet. "
            "Starting with the learning material will build "
            "the foundation needed before more practice."
        )

    if action == RELEARN:
        return (
            f"Your current mastery of {topic} is "
            f"{mastery:.0f}%, so the topic needs stronger "
            "understanding before moving forward."
        )

    if action == REVISE:
        return (
            f"{topic} has been studied before, but the "
            "available performance signals suggest that "
            "revision will help strengthen retention."
        )

    if action == PRACTICE:
        return (
            f"Your mastery of {topic} is developing. "
            "Additional practice will help convert "
            "understanding into reliable performance."
        )

    if action == CHALLENGE:
        return (
            f"You have demonstrated strong understanding "
            f"of {topic}. A harder challenge can test whether "
            "that understanding remains reliable."
        )

    if action == MOVE_FORWARD:
        return (
            f"Your current performance on {topic} is strong "
            "enough to continue to another topic."
        )

    return (
        f"Continue working on {topic} based on your "
        "current learning progress."
    )


# ============================================================
# PERFORMANCE EXPLANATION
# ============================================================

def _get_performance_explanation(
    mastery,
    recent_average,
    attempts,
    trend,
    learning_state,
):
    """
    Explain the student's current performance state.
    """

    explanations = []

    mastery = _safe_float(mastery)
    recent_average = _safe_float(recent_average)
    attempts = _safe_int(attempts)

    state = _normalize_text(
        learning_state
    ).upper()

    trend = _normalize_text(
        trend
    ).upper()

    if mastery < 40:
        explanations.append(
            f"Current mastery is {mastery:.0f}%, "
            "which indicates that the topic needs "
            "additional strengthening."
        )

    elif mastery < 70:
        explanations.append(
            f"Current mastery is {mastery:.0f}%, "
            "showing developing understanding."
        )

    else:
        explanations.append(
            f"Current mastery is {mastery:.0f}%, "
            "showing a relatively strong understanding."
        )

    if attempts == 0:
        explanations.append(
            "There is not enough quiz history yet "
            "to judge performance reliably."
        )

    elif recent_average < 50:
        explanations.append(
            f"Recent quiz performance is around "
            f"{recent_average:.0f}%, indicating that "
            "additional practice may be useful."
        )

    elif recent_average >= 80:
        explanations.append(
            f"Recent quiz performance is strong at "
            f"{recent_average:.0f}%."
        )

    if trend == "IMPROVING":
        explanations.append(
            "Your recent performance is improving."
        )

    elif trend == "DECLINING":
        explanations.append(
            "Your recent performance is declining, "
            "so additional review is recommended."
        )

    elif trend == "STABLE":
        explanations.append(
            "Your recent performance is relatively stable."
        )

    if state == "STRUGGLING":
        explanations.append(
            "Overall learning signals indicate that "
            "you currently need additional support."
        )

    elif state == "MASTERING":
        explanations.append(
            "Overall learning signals indicate strong "
            "progress toward mastery."
        )

    return explanations


# ============================================================
# DIFFICULTY EXPLANATION
# ============================================================

def _get_difficulty_explanation(
    difficulty_data,
):
    if not difficulty_data:
        return (
            "There is not enough information to explain "
            "the recommended quiz difficulty."
        )

    difficulty = _normalize_text(
        difficulty_data.get(
            "difficulty",
            "MEDIUM"
        )
    ).upper()

    previous = _normalize_text(
        difficulty_data.get(
            "previous_difficulty",
            "MEDIUM"
        )
    ).upper()

    reason = _normalize_text(
        difficulty_data.get(
            "reason",
            ""
        )
    )

    if reason:
        return (
            f"The recommended quiz difficulty is "
            f"{difficulty}. {reason}"
        )

    if difficulty == "EASY":
        return (
            f"The difficulty was adjusted from "
            f"{previous} to EASY to strengthen "
            "your fundamentals."
        )

    if difficulty == "HARD":
        return (
            f"The difficulty was adjusted from "
            f"{previous} to HARD because your "
            "performance supports a greater challenge."
        )

    return (
        f"The recommended difficulty is {difficulty} "
        "based on your current performance."
    )


# ============================================================
# MAIN EXPLANATION
# ============================================================

def generate_personalized_explanation(
    recommendation,
    performance=None,
):
    """
    Generate a personalized explanation for a study
    recommendation.

    The function is deterministic and does not require
    an external AI provider.
    """

    if not recommendation:
        return {
            "topic": "",
            "summary": (
                "No personalized recommendation is "
                "currently available."
            ),
            "why": [],
            "performance": [],
            "difficulty": "",
            "next_steps": [],
        }

    performance = (
        performance or {}
    )

    topic = _normalize_text(
        recommendation.get(
            "topic",
            "this topic"
        )
    )

    raw_action = recommendation.get(
        "action",
        ""
    )

    if isinstance(raw_action, dict):

        action = _normalize_text(
            raw_action.get(
                "action",
                ""
            )
        ).upper()

    else:

        action = _normalize_text(
            raw_action
        ).upper()   

    mastery = _safe_float(
        recommendation.get(
            "mastery",
            0
        )
    )

    attempts = _safe_int(
        recommendation.get(
            "attempts",
            0
        )
    )

    recent_average = _safe_float(
        recommendation.get(
            "recent_average",
            0
        )
    )

    trend = recommendation.get(
        "trend",
        "INSUFFICIENT_DATA"
    )

    learning_state = performance.get(
        "learning_state",
        ""
    )

    difficulty_data = recommendation.get(
        "difficulty",
        {}
    )

    action_explanation = _get_action_explanation(
        action=action,
        topic=topic,
        mastery=mastery,
        attempts=attempts,
    )

    performance_explanations = (
        _get_performance_explanation(
            mastery=mastery,
            recent_average=recent_average,
            attempts=attempts,
            trend=trend,
            learning_state=learning_state,
        )
    )

    difficulty_explanation = (
        _get_difficulty_explanation(
            difficulty_data
        )
    )

    next_steps = []

    if action == LEARN:
        next_steps = [
            f"Study the learning material for {topic}.",
            "Review the key concepts and examples.",
            "Complete a practice quiz.",
        ]

    elif action == RELEARN:
        next_steps = [
            f"Relearn the important concepts in {topic}.",
            "Review mistakes from previous practice.",
            "Take another practice quiz.",
        ]

    elif action == REVISE:
        next_steps = [
            f"Review the key concepts in {topic}.",
            "Practice questions you previously found difficult.",
            "Complete another quiz to check retention.",
        ]

    elif action == PRACTICE:
        next_steps = [
            f"Practice additional questions on {topic}.",
            "Focus on concepts where mistakes occur.",
            "Retake a quiz to measure improvement.",
        ]

    elif action == CHALLENGE:
        next_steps = [
            f"Attempt a harder quiz on {topic}.",
            "Focus on applying concepts rather than memorizing them.",
            "Use mistakes to identify deeper gaps.",
        ]

    elif action == MOVE_FORWARD:
        next_steps = [
            "Continue to the next topic.",
            "Keep the current topic in your revision cycle.",
        ]

    else:
        next_steps = [
            f"Continue studying {topic}.",
            "Complete a practice quiz when ready.",
        ]

    summary = (
        f"StudyFlow recommends that you {action.lower()} "
        f"{topic} because your current mastery is "
        f"{mastery:.0f}% and your recent learning signals "
        "indicate this is the most useful next step."
    )

    return {
        "topic": topic,
        "action": action,
        "summary": summary,
        "why": [
            action_explanation
        ],
        "performance": performance_explanations,
        "difficulty": difficulty_explanation,
        "next_steps": next_steps,
    }


# ============================================================
# SHORT SUMMARY
# ============================================================

def get_personalized_summary(
    explanation
):
    """
    Return a concise personalized explanation.
    """

    if not explanation:
        return (
            "No personalized explanation is available."
        )

    return explanation.get(
        "summary",
        "No personalized explanation is available."
    )