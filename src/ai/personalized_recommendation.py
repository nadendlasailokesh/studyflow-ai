# ============================================================
# PERSONALIZED RECOMMENDATION ENGINE
# StudyFlow AI
#
# Phase 10.2
# Advanced AI Study Coach
# ============================================================

from src.ai.student_performance import (
    analyze_student_performance,
)

from src.ai.recommendation import (
    build_topic_recommendations,
)


# ============================================================
# PRIORITY WEIGHTS
# ============================================================

PRIORITY_WEIGHTS = {
    "HIGH": 1.20,
    "MEDIUM": 1.00,
    "LOW": 0.85,
}


# ============================================================
# PERSONALIZATION WEIGHTS
# ============================================================

MASTERY_WEIGHT = 0.35
QUIZ_WEIGHT = 0.30
TREND_WEIGHT = 0.15
BASE_ADAPTIVE_WEIGHT = 0.20


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_float(
    value,
    default=0.0,
):
    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return float(default)


def _safe_int(
    value,
    default=0,
):
    try:
        return int(value)
    except (
        TypeError,
        ValueError,
    ):
        return int(default)


# ============================================================
# TREND SCORE
# ============================================================

def calculate_trend_factor(
    trend_status,
    trend_change,
):
    """
    Convert learning trend into a recommendation factor.

    A declining student receives a higher priority.
    An improving student receives a slightly lower priority.
    Stable performance remains neutral.
    """

    trend_status = str(
        trend_status or ""
    ).strip().upper()

    trend_change = _safe_float(
        trend_change
    )

    if trend_status == "DECLINING":

        return min(
            1.0
            + (
                abs(trend_change)
                / 100.0
            ),
            1.5,
        )

    if trend_status == "IMPROVING":

        return max(
            0.75,
            1.0
            - (
                abs(trend_change)
                / 200.0
            ),
        )

    if trend_status == "STABLE":

        return 1.0

    # --------------------------------------------------------
    # Not enough evidence.
    #
    # Do not punish the student for insufficient history.
    # --------------------------------------------------------

    return 1.0


# ============================================================
# TOPIC PERSONALIZATION SCORE
# ============================================================

def calculate_personalization_score(
    topic_recommendation,
    performance,
):
    """
    Calculate a personalized score for one topic.

    Combines:

        1. Topic mastery weakness
        2. Topic quiz weakness
        3. Student-wide performance trend
        4. Existing adaptive recommendation score

    Higher score = higher study priority.
    """

    progress = topic_recommendation.get(
        "progress"
    )

    if progress is None:
        return 0.0

    # --------------------------------------------------------
    # Topic mastery
    # --------------------------------------------------------

    mastery = _safe_float(
        progress.score_percentage
    )

    mastery_factor = (
        max(
            0.0,
            min(
                1.0,
                (100.0 - mastery)
                / 100.0,
            ),
        )
    )

    # --------------------------------------------------------
    # Topic quiz performance
    # --------------------------------------------------------

    quiz_stats = (
        topic_recommendation.get(
            "quiz_stats",
            {},
        )
        or {}
    )

    attempts = _safe_int(
        quiz_stats.get(
            "attempts",
            0,
        )
    )

    accuracy = _safe_float(
        quiz_stats.get(
            "accuracy",
            0.0,
        )
    )

    if attempts > 0:

        quiz_factor = (
            max(
                0.0,
                min(
                    1.0,
                    (100.0 - accuracy)
                    / 100.0,
                ),
            )
        )

    else:

        # Unattempted topics should receive meaningful
        # priority because there is no evidence yet.
        quiz_factor = 1.0

    # --------------------------------------------------------
    # Student-wide trend
    # --------------------------------------------------------

    trend_data = (
        performance.get(
            "trend",
            {},
        )
        or {}
    )

    trend_factor = calculate_trend_factor(
        trend_status=trend_data.get(
            "status"
        ),
        trend_change=trend_data.get(
            "change",
            0.0,
        ),
    )

    # --------------------------------------------------------
    # Existing adaptive score
    # --------------------------------------------------------

    adaptive_score = _safe_float(
        topic_recommendation.get(
            "adaptive_score",
            0.0,
        )
    )

    # Normalize adaptive score approximately.
    adaptive_factor = min(
        adaptive_score / 10.0,
        1.0,
    )

    # --------------------------------------------------------
    # Priority
    # --------------------------------------------------------

    topic_data = (
        topic_recommendation.get(
            "topic_data",
            {},
        )
        or {}
    )

    priority = str(
        topic_data.get(
            "priority",
            "MEDIUM",
        )
        or "MEDIUM"
    ).strip().upper()

    priority_factor = PRIORITY_WEIGHTS.get(
        priority,
        1.0,
    )

    # --------------------------------------------------------
    # Combined score
    # --------------------------------------------------------

    base_score = (
        mastery_factor
        * MASTERY_WEIGHT
        +
        quiz_factor
        * QUIZ_WEIGHT
        +
        adaptive_factor
        * BASE_ADAPTIVE_WEIGHT
    )

    personalized_score = (
        base_score
        * TREND_WEIGHT
        + (
            base_score
            * (
                1.0
                - TREND_WEIGHT
            )
        )
    )

    personalized_score *= trend_factor
    personalized_score *= priority_factor

    return round(
        personalized_score,
        4,
    )


# ============================================================
# BUILD PERSONALIZED RECOMMENDATIONS
# ============================================================

def build_personalized_recommendations(
    student_id,
    topics,
):
    """
    Build personalized topic recommendations.

    Returns recommendations sorted by personalized priority.
    """

    if not topics:
        return []

    performance = (
        analyze_student_performance(
            student_id
        )
    )

    base_recommendations = (
        build_topic_recommendations(
            topics
        )
    )

    personalized = []

    for recommendation in base_recommendations:

        score = calculate_personalization_score(
            topic_recommendation=recommendation,
            performance=performance,
        )

        item = dict(
            recommendation
        )

        item["personalized_score"] = score

        personalized.append(
            item
        )

    # --------------------------------------------------------
    # Sort by personalized priority.
    #
    # Existing adaptive score is used as a deterministic
    # tie-breaker.
    # --------------------------------------------------------

    personalized.sort(
        key=lambda item: (
            item.get(
                "personalized_score",
                0.0,
            ),
            item.get(
                "adaptive_score",
                0.0,
            ),
        ),
        reverse=True,
    )

    return personalized


# ============================================================
# TOP PERSONALIZED RECOMMENDATION
# ============================================================

def get_personalized_recommendation(
    student_id,
    topics,
):
    """
    Return the highest-priority personalized recommendation.
    """

    recommendations = (
        build_personalized_recommendations(
            student_id=student_id,
            topics=topics,
        )
    )

    if not recommendations:
        return None

    recommendation = dict(
        recommendations[0]
    )

    recommendation["performance"] = (
        analyze_student_performance(
            student_id
        )
    )

    return recommendation