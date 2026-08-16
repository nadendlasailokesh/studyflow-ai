# ============================================================
# STUDENT PERFORMANCE ANALYZER
# StudyFlow AI
#
# Phase 10.1
# Advanced AI Study Coach
# ============================================================

from src.database.repository import (
    get_student_progress_summary,
    get_quiz_performance_analytics,
    get_learning_trends,
)


# ============================================================
# CONSTANTS
# ============================================================

LEARNING_STATE_NOT_STARTED = "NOT_STARTED"
LEARNING_STATE_STRUGGLING = "STRUGGLING"
LEARNING_STATE_DEVELOPING = "DEVELOPING"
LEARNING_STATE_STRONG = "STRONG"


TREND_IMPROVING = "IMPROVING"
TREND_DECLINING = "DECLINING"
TREND_STABLE = "STABLE"
TREND_INSUFFICIENT = "INSUFFICIENT_DATA"
TREND_NO_DATA = "NO_DATA"


# ============================================================
# SAFE NUMERIC HELPERS
# ============================================================

def _safe_float(
    value,
    default=0.0
):
    """
    Safely convert a value to float.
    """

    try:
        return float(
            value
        )
    except (
        TypeError,
        ValueError
    ):
        return float(
            default
        )


def _safe_int(
    value,
    default=0
):
    """
    Safely convert a value to int.
    """

    try:
        return int(
            value
        )
    except (
        TypeError,
        ValueError
    ):
        return int(
            default
        )


# ============================================================
# LEARNING STATE
# ============================================================

def determine_learning_state(
    mastery,
    quiz_accuracy,
    attempts
):
    """
    Determine the student's current overall learning state.

    This is intentionally deterministic.

    States:

        NOT_STARTED
        STRUGGLING
        DEVELOPING
        STRONG
    """

    mastery = _safe_float(
        mastery
    )

    quiz_accuracy = _safe_float(
        quiz_accuracy
    )

    attempts = _safe_int(
        attempts
    )

    # --------------------------------------------------------
    # No meaningful learning evidence
    # --------------------------------------------------------

    if (
        mastery <= 0
        and attempts == 0
    ):
        return LEARNING_STATE_NOT_STARTED

    # --------------------------------------------------------
    # Weak performance
    # --------------------------------------------------------

    if mastery < 50:

        return LEARNING_STATE_STRUGGLING

    # --------------------------------------------------------
    # Developing
    #
    # Either mastery or quiz accuracy is still moderate.
    # --------------------------------------------------------

    if mastery < 80:

        return LEARNING_STATE_DEVELOPING

    if (
        attempts > 0
        and quiz_accuracy < 70
    ):

        return LEARNING_STATE_DEVELOPING

    # --------------------------------------------------------
    # Strong
    # --------------------------------------------------------

    return LEARNING_STATE_STRONG


# ============================================================
# CONSISTENCY
# ============================================================

def calculate_consistency(
    attempts,
    trend
):
    """
    Estimate how much evidence exists about the student's
    learning behavior.

    This is NOT a psychological measurement.

    It represents the reliability of available learning data.
    """

    attempts = _safe_int(
        attempts
    )

    if attempts <= 0:

        return {
            "level": "UNKNOWN",
            "score": 0.0,
        }

    if attempts == 1:

        return {
            "level": "LOW",
            "score": 0.25,
        }

    if attempts == 2:

        return {
            "level": "MODERATE",
            "score": 0.50,
        }

    if attempts <= 4:

        return {
            "level": "GOOD",
            "score": 0.75,
        }

    # --------------------------------------------------------
    # Five or more attempts provide stronger evidence.
    # --------------------------------------------------------

    return {
        "level": "HIGH",
        "score": 1.0,
    }


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_analysis_confidence(
    attempts,
    total_topics,
    trend
):
    """
    Calculate confidence in the performance analysis.

    Confidence represents how much reliable data StudyFlow
    currently has for making adaptive decisions.

    It does NOT represent the student's ability.
    """

    attempts = _safe_int(
        attempts
    )

    total_topics = _safe_int(
        total_topics
    )

    # --------------------------------------------------------
    # Quiz evidence
    # --------------------------------------------------------

    if attempts == 0:

        quiz_confidence = 0.0

    elif attempts == 1:

        quiz_confidence = 0.30

    elif attempts == 2:

        quiz_confidence = 0.50

    elif attempts <= 4:

        quiz_confidence = 0.75

    else:

        quiz_confidence = 1.0

    # --------------------------------------------------------
    # Topic evidence
    # --------------------------------------------------------

    if total_topics <= 0:

        topic_confidence = 0.0

    elif total_topics < 5:

        topic_confidence = 0.50

    else:

        topic_confidence = 1.0

    # --------------------------------------------------------
    # Trend evidence
    # --------------------------------------------------------

    if trend in {
        TREND_IMPROVING,
        TREND_DECLINING,
        TREND_STABLE,
    }:

        trend_confidence = 1.0

    elif trend == TREND_INSUFFICIENT:

        trend_confidence = 0.35

    else:

        trend_confidence = 0.0

    # --------------------------------------------------------
    # Weighted confidence
    # --------------------------------------------------------

    confidence = (
        quiz_confidence * 0.50
        +
        topic_confidence * 0.30
        +
        trend_confidence * 0.20
    )

    return round(
        max(
            0.0,
            min(
                confidence,
                1.0
            )
        ),
        2
    )


# ============================================================
# PERFORMANCE ANALYSIS
# ============================================================

def analyze_student_performance(
    student_id
):
    """
    Build a complete performance profile for a student.

    This function combines existing database analytics:

        - progress summary
        - quiz performance
        - learning trends

    It does not modify the database.

    Returns:
        dict
    """

    # ========================================================
    # LOAD EXISTING ANALYTICS
    # ========================================================

    progress_summary = (
        get_student_progress_summary(
            student_id
        )
        or {}
    )

    quiz_analytics = (
        get_quiz_performance_analytics(
            student_id
        )
        or {}
    )

    learning_trends = (
        get_learning_trends(
            student_id
        )
        or {}
    )

    # ========================================================
    # PROGRESS
    # ========================================================

    total_topics = _safe_int(
        progress_summary.get(
            "total_topics",
            0
        )
    )

    strong_topics = _safe_int(
        progress_summary.get(
            "strong_topics",
            0
        )
    )

    average_topics = _safe_int(
        progress_summary.get(
            "average_topics",
            0
        )
    )

    weak_topics = _safe_int(
        progress_summary.get(
            "weak_topics",
            0
        )
    )

    not_started_topics = _safe_int(
        progress_summary.get(
            "not_started_topics",
            0
        )
    )

    completed_topics = _safe_int(
        progress_summary.get(
            "completed_topics",
            0
        )
    )

    average_mastery = _safe_float(
        progress_summary.get(
            "average_mastery",
            0.0
        )
    )

    # ========================================================
    # QUIZ PERFORMANCE
    # ========================================================

    quiz_overall = (
        quiz_analytics.get(
            "overall",
            {}
        )
        or {}
    )

    attempts = _safe_int(
        quiz_overall.get(
            "attempts",
            0
        )
    )

    total_questions = _safe_int(
        quiz_overall.get(
            "total_questions",
            0
        )
    )

    correct_answers = _safe_float(
        quiz_overall.get(
            "correct_answers",
            0.0
        )
    )

    average_score = _safe_float(
        quiz_overall.get(
            "average_score",
            0.0
        )
    )

    best_score = _safe_float(
        quiz_overall.get(
            "best_score",
            0.0
        )
    )

    lowest_score = _safe_float(
        quiz_overall.get(
            "lowest_score",
            0.0
        )
    )

    # ========================================================
    # TREND
    # ========================================================

    trend_summary = (
        learning_trends.get(
            "summary",
            {}
        )
        or {}
    )

    trend = str(
        trend_summary.get(
            "trend",
            TREND_NO_DATA
        )
        or TREND_NO_DATA
    ).upper()

    trend_change = _safe_float(
        trend_summary.get(
            "change",
            0.0
        )
    )

    first_score = _safe_float(
        trend_summary.get(
            "first_score",
            0.0
        )
    )

    latest_score = _safe_float(
        trend_summary.get(
            "latest_score",
            0.0
        )
    )

    highest_score = _safe_float(
        trend_summary.get(
            "highest_score",
            0.0
        )
    )

    lowest_trend_score = _safe_float(
        trend_summary.get(
            "lowest_score",
            0.0
        )
    )

    # ========================================================
    # LEARNING STATE
    # ========================================================

    learning_state = determine_learning_state(
        mastery=average_mastery,
        quiz_accuracy=average_score,
        attempts=attempts
    )

    # ========================================================
    # CONSISTENCY
    # ========================================================

    consistency = calculate_consistency(
        attempts=attempts,
        trend=trend
    )

    # ========================================================
    # ANALYSIS CONFIDENCE
    # ========================================================

    confidence = calculate_analysis_confidence(
        attempts=attempts,
        total_topics=total_topics,
        trend=trend
    )

    # ========================================================
    # TOPIC DISTRIBUTION
    # ========================================================

    if total_topics > 0:

        mastery_coverage = (
            (
                strong_topics
                + average_topics
                + weak_topics
            )
            / total_topics
        ) * 100.0

    else:

        mastery_coverage = 0.0

    # ========================================================
    # QUIZ COVERAGE
    # ========================================================

    if total_topics > 0:

        # Number of topics with quiz attempts.
        topic_quiz_results = (
            quiz_analytics.get(
                "by_topic",
                []
            )
            or []
        )

        quiz_topics = len(
            topic_quiz_results
        )

        quiz_coverage = (
            quiz_topics
            / total_topics
        ) * 100.0

    else:

        quiz_topics = 0
        quiz_coverage = 0.0

    # ========================================================
    # RETURN PERFORMANCE PROFILE
    # ========================================================

    return {

        "student_id":
            student_id,

        # ----------------------------------------------------
        # Overall learning state
        # ----------------------------------------------------

        "learning_state":
            learning_state,

        # ----------------------------------------------------
        # Mastery
        # ----------------------------------------------------

        "mastery": {
            "average":
                round(
                    average_mastery,
                    2
                ),

            "strong_topics":
                strong_topics,

            "average_topics":
                average_topics,

            "weak_topics":
                weak_topics,

            "not_started_topics":
                not_started_topics,

            "completed_topics":
                completed_topics,

            "total_topics":
                total_topics,

            "coverage":
                round(
                    mastery_coverage,
                    2
                ),
        },

        # ----------------------------------------------------
        # Quiz performance
        # ----------------------------------------------------

        "quiz": {

            "attempts":
                attempts,

            "total_questions":
                total_questions,

            "correct_answers":
                round(
                    correct_answers,
                    2
                ),

            "average_score":
                round(
                    average_score,
                    2
                ),

            "best_score":
                round(
                    best_score,
                    2
                ),

            "lowest_score":
                round(
                    lowest_score,
                    2
                ),

            "topics_attempted":
                quiz_topics,

            "coverage":
                round(
                    quiz_coverage,
                    2
                ),
        },

        # ----------------------------------------------------
        # Trend
        # ----------------------------------------------------

        "trend": {

            "status":
                trend,

            "change":
                round(
                    trend_change,
                    2
                ),

            "first_score":
                round(
                    first_score,
                    2
                ),

            "latest_score":
                round(
                    latest_score,
                    2
                ),

            "highest_score":
                round(
                    highest_score,
                    2
                ),

            "lowest_score":
                round(
                    lowest_trend_score,
                    2
                ),
        },

        # ----------------------------------------------------
        # Learning consistency
        # ----------------------------------------------------

        "consistency":
            consistency,

        # ----------------------------------------------------
        # Analysis confidence
        # ----------------------------------------------------

        "confidence":
            confidence,
    }