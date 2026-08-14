from src.database.db import get_connection


def save_quiz_attempt(
    topic_id,
    score,
    total_questions,
    difficulty
):

    if total_questions <= 0:
        raise ValueError(
            "Total questions must be greater than zero."
        )

    connection = get_connection()

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

    attempt_id = cursor.lastrowid

    connection.close()

    return attempt_id


def update_topic_mastery(
    topic_id,
    mastery,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE topics
        SET mastery = ?,
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

    updated_rows = cursor.rowcount

    connection.close()

    return updated_rows

def get_topic_progress(topic_id):

    connection = get_connection()

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

    connection.close()

    if row is None:
        return None

    return dict(row)

def get_quiz_history(topic_id):

    connection = get_connection()

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

    connection.close()

    return [
        dict(row)
        for row in rows
    ]
def get_quiz_statistics(topic_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS attempts,
            COALESCE(SUM(total_questions), 0)
                AS total_questions,
            COALESCE(SUM(score), 0)
                AS correct_answers
        FROM quiz_attempts
        WHERE topic_id = ?
        """,
        (topic_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {
            "attempts": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "accuracy": 0.0
        }

    attempts = int(
        row["attempts"] or 0
    )

    total_questions = int(
        row["total_questions"] or 0
    )

    correct_answers = float(
        row["correct_answers"] or 0
    )

    if total_questions > 0:

        accuracy = (
            correct_answers
            / total_questions
        ) * 100

    else:

        accuracy = 0.0

    return {
        "attempts": attempts,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "accuracy": round(
            accuracy,
            2
        )
    }
def get_recent_quiz_performance(
    topic_id,
    limit=3
):

    connection = get_connection()

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
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (
            topic_id,
            limit
        )
    )

    rows = cursor.fetchall()

    connection.close()

    performance = []

    for row in rows:

        total_questions = int(
            row["total_questions"] or 0
        )

        score = float(
            row["score"] or 0
        )

        if total_questions > 0:

            accuracy = (
                score
                / total_questions
            ) * 100

        else:

            accuracy = 0.0

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
                        accuracy,
                        2
                    )
            }
        )

    return performance