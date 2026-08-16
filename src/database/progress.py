# ============================================================
# PROGRESS DATABASE FUNCTIONS
# StudyFlow AI
# ============================================================
from src.ai.progress_schema import TopicProgress
from src.database.db import get_connection


# ============================================================
# SAVE QUIZ ATTEMPT
# ============================================================

def save_quiz_attempt(
    topic_id,
    score,
    total_questions,
    difficulty
):
    """
    Save a quiz attempt.

    IMPORTANT:
    score is stored as percentage (0-100).

    Example:
        8/10 = 80.0
    """

    if total_questions <= 0:
        raise ValueError(
            "Total questions must be greater than zero."
        )

    score = float(score)

    score = max(
        0.0,
        min(score, 100.0)
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO quiz_attempts (
                topic_id,
                score,
                total_questions,
                difficulty
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                topic_id,
                score,
                total_questions,
                difficulty
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


# ============================================================
# UPDATE TOPIC MASTERY
# ============================================================

def update_topic_mastery(
    topic_id,
    mastery,
    status
):

    mastery = float(mastery)

    mastery = max(
        0.0,
        min(mastery, 100.0)
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE topics
            SET
                mastery = ?,
                status = ?
            WHERE id = ?
            """,
            (
                mastery,
                status,
                topic_id
            )
        )

        connection.commit()

        return cursor.rowcount

    finally:

        connection.close()


# ============================================================
# GET TOPIC PROGRESS
# ============================================================

def get_topic_progress(topic_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                mastery,
                status
            FROM topics
            WHERE id = ?
            """,
            (topic_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:

        connection.close()


# ============================================================
# GET QUIZ HISTORY
# ============================================================

def get_quiz_history(topic_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                score,
                total_questions,
                difficulty,
                created_at
            FROM quiz_attempts
            WHERE topic_id = ?
            ORDER BY created_at DESC
            """,
            (topic_id,)
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# GET QUIZ STATISTICS
# ============================================================

def get_quiz_statistics(topic_id):
    """
    Calculate quiz statistics for one topic.

    score is stored as percentage.

    Example:

        Quiz 1 = 80%
        Quiz 2 = 60%

    Accuracy = average percentage
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS attempts,

                COALESCE(
                    SUM(total_questions),
                    0
                ) AS total_questions,

                COALESCE(
                    AVG(score),
                    0
                ) AS average_score

            FROM quiz_attempts

            WHERE topic_id = ?
            """,
            (topic_id,)
        )

        row = cursor.fetchone()

        if row is None:

            return {
                "attempts": 0,
                "total_questions": 0,
                "correct_answers": 0.0,
                "accuracy": 0.0
            }

        attempts = int(
            row["attempts"] or 0
        )

        total_questions = int(
            row["total_questions"] or 0
        )

        accuracy = float(
            row["average_score"] or 0.0
        )

        # ----------------------------------------------------
        # Convert average percentage into equivalent
        # number of correct answers for reporting.
        # ----------------------------------------------------

        correct_answers = (
            accuracy
            / 100.0
            * total_questions
        )

        return {
            "attempts": attempts,

            "total_questions":
                total_questions,

            "correct_answers":
                round(
                    correct_answers,
                    2
                ),

            "accuracy":
                round(
                    accuracy,
                    2
                )
        }

    finally:

        connection.close()


# ============================================================
# GET RECENT QUIZ PERFORMANCE
# ============================================================

def get_recent_quiz_performance(
    topic_id,
    limit=3
):
    """
    Return recent quiz performance.

    Newest attempt appears first.

    score is already stored as percentage,
    therefore it must NOT be divided by total_questions.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                score,
                total_questions,
                difficulty,
                created_at

            FROM quiz_attempts

            WHERE topic_id = ?

            ORDER BY
                created_at DESC

            LIMIT ?
            """,
            (
                topic_id,
                limit
            )
        )

        rows = cursor.fetchall()

        performance = []

        for row in rows:

            score = float(
                row["score"] or 0.0
            )

            total_questions = int(
                row["total_questions"] or 0
            )

            performance.append(
                {
                    "score": score,

                    "total_questions":
                        total_questions,

                    "difficulty":
                        row["difficulty"],

                    "created_at":
                        row["created_at"],

                    "accuracy":
                        round(
                            score,
                            2
                        )
                }
            )

        return performance

    finally:

        connection.close()
# ============================================================
# SAVE QUIZ RESULT + UPDATE ADAPTIVE PROGRESS
# ============================================================

def save_progress_to_database(
    topic_id,
    correct_answers,
    total_questions,
    difficulty,
    topic
):
    """
    Save a completed quiz attempt and update topic mastery.

    Flow:

        Quiz Result
            ↓
        Save Quiz Attempt
            ↓
        Recalculate Mastery
            ↓
        Determine Status
            ↓
        Update Topic
            ↓
        Return Updated Progress
    """

    if total_questions <= 0:
        raise ValueError(
            "Total questions must be greater than zero."
        )

    correct_answers = int(correct_answers)
    total_questions = int(total_questions)

    correct_answers = max(
        0,
        min(
            correct_answers,
            total_questions
        )
    )

    # --------------------------------------------------------
    # Calculate current quiz score
    # --------------------------------------------------------

    score_percentage = (
        correct_answers
        / total_questions
    ) * 100.0

    score_percentage = round(
        score_percentage,
        2
    )

    # --------------------------------------------------------
    # Save quiz attempt
    # --------------------------------------------------------

    save_quiz_attempt(
        topic_id=topic_id,
        score=score_percentage,
        total_questions=total_questions,
        difficulty=difficulty
    )

    # --------------------------------------------------------
    # Get previous topic progress
    # --------------------------------------------------------

    previous_progress = get_topic_progress(
        topic_id
    )

    previous_mastery = 0.0

    if previous_progress:

        previous_mastery = float(
            previous_progress.get(
                "mastery",
                0.0
            )
            or 0.0
        )

    # --------------------------------------------------------
    # Calculate new mastery
    # --------------------------------------------------------
    #
    # We use a weighted update:
    #
    # 70% previous mastery
    # 30% latest quiz score
    #
    # This prevents one quiz from completely changing
    # the student's long-term mastery.
    # --------------------------------------------------------

    if previous_mastery <= 0:

        new_mastery = score_percentage

    else:

        new_mastery = (
            (previous_mastery * 0.70)
            +
            (score_percentage * 0.30)
        )

    new_mastery = round(
        max(
            0.0,
            min(
                new_mastery,
                100.0
            )
        ),
        2
    )

    # --------------------------------------------------------
    # Determine topic status
    # --------------------------------------------------------

    if new_mastery >= 80:

        status = "STRONG"

    elif new_mastery >= 50:

        status = "AVERAGE"

    elif new_mastery > 0:

        status = "WEAK"

    else:

        status = "NOT_STARTED"

    # --------------------------------------------------------
    # Update topic
    # --------------------------------------------------------

    update_topic_mastery(
        topic_id=topic_id,
        mastery=new_mastery,
        status=status
    )

    # --------------------------------------------------------
    # Return updated progress
    # --------------------------------------------------------

    return TopicProgress(

    topic=topic,

    attempts=get_quiz_statistics(
        topic_id
    )["attempts"],

    correct_answers=correct_answers,

    total_questions=total_questions,

    score_percentage=new_mastery,

    status=status,
)