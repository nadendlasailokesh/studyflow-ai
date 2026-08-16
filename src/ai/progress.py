from src.ai.progress_schema import (
    TopicProgress,
    ProgressSummary
)

from src.database.repository import (
    save_quiz_attempt,
    update_topic_mastery,
    get_topic_quiz_mastery
)


# ============================================================
# SCORE UTILITIES
# ============================================================

def calculate_percentage(
    correct_answers,
    total_questions
):
    """
    Convert correct answers into a percentage.

    Example:
        4 / 5 -> 80.0
    """

    if total_questions <= 0:
        raise ValueError(
            "Total questions must be greater than zero."
        )

    percentage = (
        float(correct_answers)
        / float(total_questions)
    ) * 100.0

    return round(
        max(0.0, min(percentage, 100.0)),
        2
    )


# ============================================================
# STATUS
# ============================================================

def determine_status(score_percentage):

    score_percentage = float(score_percentage)

    if score_percentage >= 80:
        return "STRONG"

    elif score_percentage >= 50:
        return "AVERAGE"

    elif score_percentage > 0:
        return "WEAK"

    else:
        return "NOT_STARTED"


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
    """
    Save a quiz attempt and update cumulative topic mastery.

    IMPORTANT:
    quiz_attempts.score is stored as a percentage (0-100).
    """

    # --------------------------------------------------------
    # Normalize input
    # --------------------------------------------------------

    try:
        correct_answers = int(correct_answers)
        total_questions = int(total_questions)
    except (TypeError, ValueError) as error:

        raise ValueError(
            "Quiz answers must be numeric."
        ) from error


    # --------------------------------------------------------
    # Validate
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
    # Current quiz percentage
    # --------------------------------------------------------

    current_score = calculate_percentage(
        correct_answers,
        total_questions
    )


    # --------------------------------------------------------
    # Save quiz attempt
    # --------------------------------------------------------

    save_quiz_attempt(
        topic_id=topic_id,
        score=current_score,
        total_questions=total_questions,
        difficulty=difficulty
    )


    # --------------------------------------------------------
    # Calculate cumulative mastery
    # --------------------------------------------------------

    mastery_data = get_topic_quiz_mastery(
        topic_id
    )

    cumulative_mastery = float(
        mastery_data.get(
            "mastery",
            0.0
        )
    )

    attempts = int(
        mastery_data.get(
            "attempts",
            0
        )
    )


    # --------------------------------------------------------
    # Safety clamp
    # --------------------------------------------------------

    cumulative_mastery = round(
        max(
            0.0,
            min(
                cumulative_mastery,
                100.0
            )
        ),
        2
    )


    # --------------------------------------------------------
    # Determine status
    # --------------------------------------------------------

    status = determine_status(
        cumulative_mastery
    )


    # --------------------------------------------------------
    # Update topic
    # --------------------------------------------------------

    update_topic_mastery(
        topic_id=topic_id,
        mastery=cumulative_mastery,
        status=status
    )


    # --------------------------------------------------------
    # Return progress
    # --------------------------------------------------------

    return TopicProgress(

        topic=topic,

        attempts=attempts,

        correct_answers=correct_answers,

        total_questions=total_questions,

        score_percentage=cumulative_mastery,

        status=status
    )


# ============================================================
# CALCULATE TOPIC PROGRESS
# ============================================================

def calculate_topic_progress(
    topic,
    correct_answers,
    total_questions,
    attempts=1
):
    """
    Calculate progress for a single quiz result.
    """

    correct_answers = int(
        correct_answers
    )

    total_questions = int(
        total_questions
    )

    attempts = int(
        attempts
    )


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

    if attempts < 0:

        raise ValueError(
            "Attempts cannot be negative."
        )


    score_percentage = calculate_percentage(
        correct_answers,
        total_questions
    )


    status = determine_status(
        score_percentage
    )


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


    elif progress.status == "WEAK":

        return {

            "action": "RELEARN",

            "message": (
                "This topic needs more attention. "
                "Review the learning content and "
                "take another quiz."
            )
        }


    else:

        return {

            "action": "START",

            "message": (
                "Start learning this topic and "
                "complete the first practice quiz."
            )
        }