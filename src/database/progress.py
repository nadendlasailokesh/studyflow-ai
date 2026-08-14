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