from src.ai.progress_schema import TopicProgress


# ============================================================
# ADAPTIVE WEIGHTS
# ============================================================

STATUS_WEIGHTS = {
    "WEAK": 2.0,
    "AVERAGE": 1.25,
    "STRONG": 0.75,
}


def calculate_adaptive_weight(
    progress: TopicProgress
) -> float:

    status = progress.status.upper()

    return STATUS_WEIGHTS.get(
        status,
        1.0
    )


# ============================================================
# ADAPTIVE SCORE
# ============================================================

def calculate_adaptive_score(
    progress: TopicProgress,
    base_score: float = 1.0
) -> float:

    weight = calculate_adaptive_weight(
        progress
    )

    return round(
        base_score * weight,
        2
    )


# ============================================================
# PRIORITIZE TOPICS
# ============================================================

def prioritize_topics(topics):

    result = []

    for item in topics:

        progress = item.get(
            "progress"
        )

        if progress is None:
            continue

        base_score = item.get(
            "base_score",
            1.0
        )

        adaptive_score = calculate_adaptive_score(
            progress=progress,
            base_score=base_score
        )

        result.append(
            {
                "topic": item.get(
                    "topic"
                ),

                "topic_data": item.get(
                    "topic_data"
                ),

                "progress": progress,

                "base_score": base_score,

                "adaptive_score": adaptive_score,

                "action": get_adaptive_action(
                    progress
                )
            }
        )

    result.sort(
        key=lambda item: item[
            "adaptive_score"
        ],
        reverse=True
    )

    return result


# ============================================================
# ADAPTIVE ACTION
# ============================================================

def get_adaptive_action(
    progress: TopicProgress
):

    status = progress.status.upper()

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

    if status == "AVERAGE":

        return {
            "action": "REVISE",

            "priority": "MEDIUM",

            "message": (
                "Review the important concepts "
                "and practice additional questions."
            )
        }

    if status == "STRONG":

        return {
            "action": "MOVE_FORWARD",

            "priority": "LOW",

            "message": (
                "You have demonstrated strong "
                "understanding. Continue to the next topic."
            )
        }

    return {
        "action": "REVIEW",

        "priority": "MEDIUM",

        "message": (
            "Review this topic and complete "
            "a practice quiz."
        )
    }