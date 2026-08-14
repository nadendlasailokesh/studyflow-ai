from src.ai.adaptive_planner import get_adaptive_action
from src.ai.progress_schema import TopicProgress

from src.database.progress import (
    get_quiz_statistics,
    get_recent_quiz_performance,
)


# ============================================================
# STATUS NORMALIZATION
# ============================================================

def normalize_status(status, mastery):
    """
    Convert database status values into the standardized
    progress status used by the AI recommendation system.
    """

    if not status:
        status = ""

    normalized = str(status).strip().upper()

    if normalized in {
        "NOT_STARTED",
        "NOT STARTED",
    }:
        return "NOT_STARTED"

    if normalized == "WEAK":
        return "WEAK"

    if normalized in {
        "AVERAGE",
        "MEDIUM",
    }:
        return "AVERAGE"

    if normalized == "STRONG":
        return "STRONG"

    # Fallback based on mastery
    if mastery >= 80:
        return "STRONG"

    if mastery >= 50:
        return "AVERAGE"

    if mastery > 0:
        return "WEAK"

    return "NOT_STARTED"


# ============================================================
# HISTORY SCORE
# ============================================================

def calculate_history_score(topic):
    """
    Calculate how urgently a topic needs attention based
    on previous quiz performance.

    Higher score = higher learning need.
    """

    quiz_stats = topic.get(
        "quiz_stats",
        {}
    )

    attempts = int(
        quiz_stats.get(
            "attempts",
            0
        )
    )

    accuracy = float(
        quiz_stats.get(
            "accuracy",
            0.0
        )
    )

    improvement = float(
        topic.get(
            "improvement",
            0.0
        )
    )

    # --------------------------------------------------------
    # No quiz history
    # --------------------------------------------------------

    if attempts == 0:
        return 1.0

    # --------------------------------------------------------
    # Lower accuracy = higher learning need
    # --------------------------------------------------------

    weakness_score = (
        (100 - accuracy) / 100
    )

    # --------------------------------------------------------
    # Negative improvement = increased urgency
    # --------------------------------------------------------

    decline_score = 0.0

    if improvement < 0:

        decline_score = min(
            abs(improvement) / 100,
            1.0
        )

    # --------------------------------------------------------
    # Positive improvement = reduced urgency
    # --------------------------------------------------------

    improvement_bonus = 0.0

    if improvement > 0:

        improvement_bonus = min(
            improvement / 100,
            0.5
        )

    history_score = (
        weakness_score
        + decline_score
        - improvement_bonus
    )

    return max(
        history_score,
        0.0
    )


# ============================================================
# ADAPTIVE SCORE
# ============================================================

def calculate_adaptive_score(topic):
    """
    Calculate the final adaptive priority score.

    Factors:
        1. Topic priority
        2. Current mastery
        3. Historical quiz performance

    Higher score = topic should be studied sooner.
    """

    base_score = float(
        topic.get(
            "base_score",
            1.0
        )
    )

    progress = topic["progress"]

    mastery = float(
        progress.score_percentage
    )

    # --------------------------------------------------------
    # Lower mastery = higher need
    # --------------------------------------------------------

    mastery_score = (
        (100 - mastery) / 100
    )

    # --------------------------------------------------------
    # Historical performance
    # --------------------------------------------------------

    history_score = calculate_history_score(
        topic
    )

    # --------------------------------------------------------
    # Final adaptive score
    # --------------------------------------------------------

    adaptive_score = (
        base_score
        + (mastery_score * 3.0)
        + (history_score * 2.0)
    )

    return round(
        adaptive_score,
        3
    )


# ============================================================
# BUILD TOPIC RECOMMENDATIONS
# ============================================================

def build_topic_recommendations(topics):
    """
    Convert database topics into adaptive planner input
    and rank them according to learning needs.
    """

    adaptive_topics = []

    for topic in topics:

        # ----------------------------------------------------
        # Basic topic information
        # ----------------------------------------------------

        mastery = float(
            topic.get("mastery") or 0.0
        )

        topic_id = topic.get("id")

        # ----------------------------------------------------
        # Default quiz statistics
        # ----------------------------------------------------

        quiz_stats = {
            "attempts": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "accuracy": 0.0,
        }

        recent_performance = []

        # IMPORTANT:
        # Always initialize improvement.
        # Otherwise it can be undefined when topic_id is None.
        improvement = 0.0

        # ----------------------------------------------------
        # Load quiz history
        # ----------------------------------------------------

        if topic_id is not None:

            quiz_stats = get_quiz_statistics(
                topic_id
            )

            if quiz_stats is None:

                quiz_stats = {
                    "attempts": 0,
                    "total_questions": 0,
                    "correct_answers": 0,
                    "accuracy": 0.0,
                }

            recent_performance = (
                get_recent_quiz_performance(
                    topic_id
                )
                or []
            )

            # ------------------------------------------------
            # Calculate improvement
            # ------------------------------------------------

            if len(recent_performance) >= 2:

                latest_accuracy = float(
                    recent_performance[0].get(
                        "accuracy",
                        0.0
                    )
                )

                previous_accuracy = float(
                    recent_performance[1].get(
                        "accuracy",
                        0.0
                    )
                )

                improvement = (
                    latest_accuracy
                    - previous_accuracy
                )

        # ----------------------------------------------------
        # Normalize status
        # ----------------------------------------------------

        status = normalize_status(
            topic.get("status"),
            mastery
        )

        # ----------------------------------------------------
        # Create progress object
        # ----------------------------------------------------

        progress = TopicProgress(

            topic=topic["name"],

            attempts=int(
                quiz_stats.get(
                    "attempts",
                    0
                )
            ),

            correct_answers=int(
                quiz_stats.get(
                    "correct_answers",
                    0
                )
            ),

            total_questions=int(
                quiz_stats.get(
                    "total_questions",
                    0
                )
            ),

            score_percentage=mastery,

            status=status
        )

        # ----------------------------------------------------
        # Topic priority
        # ----------------------------------------------------

        priority = (
            topic.get("priority")
            or "MEDIUM"
        )

        priority = str(
            priority
        ).strip().upper()

        base_score = {
            "HIGH": 3.0,
            "MEDIUM": 2.0,
            "LOW": 1.0,
        }.get(
            priority,
            1.0
        )

        # ----------------------------------------------------
        # Build adaptive topic
        # ----------------------------------------------------

        adaptive_topics.append(
            {
                "topic": topic["name"],

                "topic_data": topic,

                "progress": progress,

                "base_score": base_score,

                "quiz_stats": quiz_stats,

                "recent_performance":
                    recent_performance,

                "improvement":
                    improvement,
            }
        )

    # ========================================================
    # CALCULATE ADAPTIVE SCORES
    # ========================================================

    for topic in adaptive_topics:

        topic["adaptive_score"] = (
            calculate_adaptive_score(
                topic
            )
        )

    # ========================================================
    # SORT BY LEARNING NEED
    # ========================================================

    adaptive_topics.sort(
        key=lambda item: item[
            "adaptive_score"
        ],
        reverse=True
    )

    return adaptive_topics


# ============================================================
# TOP RECOMMENDATION
# ============================================================

def get_top_recommendation(topics):
    """
    Return the single topic that currently needs
    the most attention.
    """

    recommendations = (
        build_topic_recommendations(
            topics
        )
    )

    if not recommendations:
        return None

    top = recommendations[0]

    progress = top["progress"]

    action = get_adaptive_action(
        progress
    )

    return {
        "topic": top["topic"],

        "topic_data":
            top["topic_data"],

        "progress":
            progress,

        "adaptive_score":
            top["adaptive_score"],

        "action":
            action,

        "quiz_stats":
            top["quiz_stats"],

        "recent_performance":
            top["recent_performance"],

        "improvement":
            top["improvement"],
    }