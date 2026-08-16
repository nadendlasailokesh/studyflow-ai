# ============================================================
# ADAPTIVE RECOMMENDATION ENGINE
# StudyFlow AI
# ============================================================

from src.ai.adaptive_planner import (
    get_adaptive_action,
)

from src.ai.progress_schema import (
    TopicProgress,
)

from src.database.progress import (
    get_quiz_statistics,
    get_recent_quiz_performance,
)


# ============================================================
# STATUS NORMALIZATION
# ============================================================

def normalize_status(
    status,
    mastery
):

    normalized = str(
        status or ""
    ).strip().upper()

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

    # --------------------------------------------------------
    # Fallback based on mastery
    # --------------------------------------------------------

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
    # Weak performance
    # --------------------------------------------------------

    weakness_score = (
        (100.0 - accuracy)
        / 100.0
    )

    # --------------------------------------------------------
    # Performance trend
    # --------------------------------------------------------

    trend_score = 0.0

    if improvement < 0:

        trend_score = min(
            abs(improvement) / 100.0,
            1.0
        )

    elif improvement > 0:

        trend_score = -min(
            improvement / 100.0,
            0.5
        )

    # --------------------------------------------------------
    # Final history score
    # --------------------------------------------------------

    history_score = (
        weakness_score
        + trend_score
    )

    return max(
        history_score,
        0.0
    )


# ============================================================
# ADAPTIVE SCORE
# ============================================================

def calculate_adaptive_score(topic):

    base_score = float(
        topic.get(
            "base_score",
            1.0
        )
    )

    progress = topic.get(
        "progress"
    )

    if progress is None:
        return 0.0

    mastery = float(
        progress.score_percentage
    )

    # --------------------------------------------------------
    # Mastery weakness
    # --------------------------------------------------------

    mastery_score = (
        (100.0 - mastery)
        / 100.0
    )

    # --------------------------------------------------------
    # Quiz history
    # --------------------------------------------------------

    history_score = (
        calculate_history_score(
            topic
        )
    )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    adaptive_score = (
        base_score
        + (
            mastery_score
            * 3.0
        )
        + (
            history_score
            * 2.0
        )
    )

    return round(
        max(
            adaptive_score,
            0.0
        ),
        3
    )


# ============================================================
# BUILD TOPIC RECOMMENDATIONS
# ============================================================

def build_topic_recommendations(
    topics
):

    adaptive_topics = []

    for topic in topics:

        # ----------------------------------------------------
        # Mastery
        # ----------------------------------------------------

        mastery = float(
            topic.get(
                "mastery"
            )
            or 0.0
        )

        topic_id = topic.get(
            "id"
        )

        # ----------------------------------------------------
        # Default quiz statistics
        # ----------------------------------------------------

        quiz_stats = {

            "attempts": 0,

            "total_questions": 0,

            "correct_answers": 0.0,

            "accuracy": 0.0,
        }

        recent_performance = []

        improvement = 0.0

        # ----------------------------------------------------
        # Load quiz history
        # ----------------------------------------------------

        if topic_id is not None:

            quiz_stats = (
                get_quiz_statistics(
                    topic_id
                )
                or quiz_stats
            )

            recent_performance = (
                get_recent_quiz_performance(
                    topic_id
                )
                or []
            )

            # ------------------------------------------------
            # Recent performance trend
            # ------------------------------------------------

            if len(
                recent_performance
            ) >= 2:

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
            topic.get(
                "status"
            ),
            mastery
        )

        # ----------------------------------------------------
        # Build progress model
        # ----------------------------------------------------

        progress = TopicProgress(

            topic=topic.get(
                "name",
                "Unknown Topic"
            ),

            attempts=int(
                quiz_stats.get(
                    "attempts",
                    0
                )
            ),

            correct_answers=int(
                round(
                    float(
                        quiz_stats.get(
                            "correct_answers",
                            0.0
                        )
                    )
                )
            ),

            total_questions=int(
                quiz_stats.get(
                    "total_questions",
                    0
                )
            ),

            score_percentage=mastery,

            status=status,
        )

        # ----------------------------------------------------
        # Syllabus priority
        # ----------------------------------------------------

        priority = (
            topic.get(
                "priority"
            )
            or "MEDIUM"
        )

        priority = (
            str(priority)
            .strip()
            .upper()
        )

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

                "topic":
                    topic.get(
                        "name",
                        "Unknown Topic"
                    ),

                "topic_data":
                    topic,

                "progress":
                    progress,

                "base_score":
                    base_score,

                "quiz_stats":
                    quiz_stats,

                "recent_performance":
                    recent_performance,

                "improvement":
                    improvement,
            }
        )

    # ========================================================
    # CALCULATE SCORES + ACTIONS
    # ========================================================

    for topic in adaptive_topics:

        topic["adaptive_score"] = (
            calculate_adaptive_score(
                topic
            )
        )

        action_info = (
            get_adaptive_action(
                topic["progress"]
            )
        )

        topic["action"] = action_info

        topic["action_priority"] = (
            action_info["priority"]
        )

        topic["action_message"] = (
            action_info["message"]
        )

    # ========================================================
    # SORT
    # ========================================================

    adaptive_topics.sort(

        key=lambda item: (

            item["adaptive_score"],

            item["base_score"],

            item["progress"].score_percentage * -1,

        ),

        reverse=True
    )

    return adaptive_topics


# ============================================================
# TOP RECOMMENDATION
# ============================================================

def get_top_recommendation(
    topics
):

    recommendations = (
        build_topic_recommendations(
            topics
        )
    )

    if not recommendations:
        return None

    top = recommendations[0]

    return {

        "topic":
            top["topic"],

        "topic_data":
            top["topic_data"],

        "progress":
            top["progress"],

        "adaptive_score":
            top["adaptive_score"],

        "action":
            top["action"],

        "action_priority":
            top["action_priority"],

        "action_message":
            top["action_message"],

        "quiz_stats":
            top["quiz_stats"],

        "recent_performance":
            top["recent_performance"],

        "improvement":
            top["improvement"],
    }