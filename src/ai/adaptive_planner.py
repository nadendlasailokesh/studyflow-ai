# ============================================================
# ADAPTIVE PLANNER
# StudyFlow AI
# ============================================================

from src.ai.progress_schema import TopicProgress


# ============================================================
# STATUS WEIGHTS
# ============================================================
#
# Kept for backward compatibility with older code.
#
# The authoritative recommendation score is calculated
# in recommendation.py.
# ============================================================

STATUS_WEIGHTS = {

    "NOT_STARTED": 1.0,

    "WEAK": 2.0,

    "AVERAGE": 1.25,

    "STRONG": 0.75,
}


# ============================================================
# CALCULATE ADAPTIVE WEIGHT
# ============================================================

def calculate_adaptive_weight(
    progress: TopicProgress
) -> float:

    status = (
        progress.status
        .strip()
        .upper()
    )

    return STATUS_WEIGHTS.get(
        status,
        1.0
    )


# ============================================================
# LEGACY ADAPTIVE SCORE
# ============================================================

def calculate_adaptive_score(
    progress: TopicProgress,
    base_score: float = 1.0
) -> float:
    """
    Backward-compatible status-based score.

    NOTE:
    The main recommendation engine does NOT use this
    as its authoritative score.

    The authoritative score is calculated by:

        src.ai.recommendation.calculate_adaptive_score()
    """

    weight = calculate_adaptive_weight(
        progress
    )

    return round(
        base_score * weight,
        2
    )


# ============================================================
# ADAPTIVE ACTION
# ============================================================

def get_adaptive_action(
    progress: TopicProgress
):
    """
    Determine the next learning action.

    Returns:

        action
        priority
        message
    """

    status = (
        progress.status
        .strip()
        .upper()
    )

    # --------------------------------------------------------
    # NOT STARTED
    # --------------------------------------------------------

    if status == "NOT_STARTED":

        return {

            "action": "CONTINUE",

            "priority": "HIGH",

            "message": (
                "Start learning this topic, "
                "understand the key concepts, "
                "and complete a practice quiz."
            )
        }

    # --------------------------------------------------------
    # WEAK
    # --------------------------------------------------------

    if status == "WEAK":

        return {

            "action": "RELEARN",

            "priority": "HIGH",

            "message": (
                "Relearn this topic carefully, "
                "review the learning material, "
                "practice examples, and retake the quiz."
            )
        }

    # --------------------------------------------------------
    # AVERAGE
    # --------------------------------------------------------

    if status == "AVERAGE":

        return {

            "action": "REVISE",

            "priority": "MEDIUM",

            "message": (
                "Review the important concepts "
                "and practice additional questions."
            )
        }

    # --------------------------------------------------------
    # STRONG
    # --------------------------------------------------------

    if status == "STRONG":

        return {

            "action": "MOVE_FORWARD",

            "priority": "LOW",

            "message": (
                "You have demonstrated strong "
                "understanding. Continue to the next topic."
            )
        }

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return {

        "action": "CONTINUE",

        "priority": "MEDIUM",

        "message": (
            "Review this topic and complete "
            "a practice quiz."
        )
    }


# ============================================================
# PRIORITIZE TOPICS
# ============================================================

def prioritize_topics(topics):
    """
    Backward-compatible topic prioritization.

    For the complete adaptive recommendation system,
    use:

        build_topic_recommendations()

    from src.ai.recommendation.

    This function remains available so existing parts
    of StudyFlow AI do not break.
    """

    result = []

    for item in topics:

        progress = item.get(
            "progress"
        )

        if progress is None:
            continue

        base_score = float(
            item.get(
                "base_score",
                1.0
            )
        )

        adaptive_score = (
            calculate_adaptive_score(
                progress=progress,
                base_score=base_score
            )
        )

        action_info = get_adaptive_action(
            progress
        )

        result.append(
            {

                "topic":
                    item.get("topic"),

                "topic_data":
                    item.get("topic_data"),

                "progress":
                    progress,

                "base_score":
                    base_score,

                "adaptive_score":
                    adaptive_score,

                "action":
                    action_info["action"],

                "action_priority":
                    action_info["priority"],

                "message":
                    action_info["message"],
            }
        )

    result.sort(

        key=lambda item: (

            item["adaptive_score"],

            item["base_score"]
        ),

        reverse=True
    )

    return result