from src.ai.progress_schema import (
    TopicProgress,
    ProgressSummary
)

from src.database.repository import (
    save_quiz_attempt,
    update_topic_mastery
)


# ============================================================
# SAVE QUIZ PROGRESS
# ============================================================

def save_progress_to_database(
    topic_id,
    correct_answers,
    total_questions,
    difficulty,
    topic=""
):

    progress = calculate_topic_progress(
        topic=topic,
        correct_answers=correct_answers,
        total_questions=total_questions
    )

    # --------------------------------------------------------
    # Save quiz attempt
    # --------------------------------------------------------

    save_quiz_attempt(
        topic_id=topic_id,
        score=progress.score_percentage,
        total_questions=total_questions,
        difficulty=difficulty
    )

    # --------------------------------------------------------
    # Update topic mastery
    # --------------------------------------------------------

    update_topic_mastery(
        topic_id=topic_id,
        mastery=progress.score_percentage,
        status=progress.status
    )

    return progress


# ============================================================
# CALCULATE TOPIC PROGRESS
# ============================================================

def calculate_topic_progress(
    topic,
    correct_answers,
    total_questions,
    attempts=1
):

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if total_questions <= 0:

        raise ValueError(
            "Total questions must be greater than zero."
        )

    if correct_answers < 0:

        raise ValueError(
            "Correct answers cannot be negative."
        )

    if correct_answers > total_questions:

        raise ValueError(
            "Correct answers cannot exceed total questions."
        )

    # --------------------------------------------------------
    # Calculate percentage
    # --------------------------------------------------------

    score_percentage = (
        correct_answers / total_questions
    ) * 100

    score_percentage = round(
        score_percentage,
        2
    )

    # --------------------------------------------------------
    # Determine status
    # --------------------------------------------------------

    if score_percentage >= 80:

        status = "STRONG"

    elif score_percentage >= 50:

        status = "AVERAGE"

    else:

        status = "WEAK"

    # --------------------------------------------------------
    # Return structured progress
    # --------------------------------------------------------

    return TopicProgress(

        topic=topic,

        attempts=attempts,

        correct_answers=correct_answers,

        total_questions=total_questions,

        score_percentage=score_percentage,

        status=status
    )


# ============================================================
# LEARNING RECOMMENDATION
# ============================================================

def get_learning_recommendation(
    progress: TopicProgress
):

    if progress.status == "STRONG":

        return {
            "action": "MOVE_FORWARD",

            "message": (
                "You understand this topic well. "
                "Move to the next important topic."
            )
        }

    elif progress.status == "AVERAGE":

        return {
            "action": "REVISE",

            "message": (
                "You have a reasonable understanding. "
                "Review the key concepts before moving on."
            )
        }

    else:

        return {
            "action": "RELEARN",

            "message": (
                "This topic needs more attention. "
                "Review the learning content and "
                "take another quiz."
            )
        }