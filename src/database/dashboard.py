from src.database.db import get_connection


def get_subject_topics(subject_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            unit,
            priority,
            mastery,
            status
        FROM topics
        WHERE subject_id = ?
        ORDER BY
            mastery ASC,
            priority DESC
        """,
        (subject_id,)
    )

    topics = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return topics


def get_topic_statistics(subject_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_topics,

            SUM(
                CASE
                    WHEN mastery >= 80
                    THEN 1
                    ELSE 0
                END
            ) AS strong_topics,

            SUM(
                CASE
                    WHEN mastery >= 50
                     AND mastery < 80
                    THEN 1
                    ELSE 0
                END
            ) AS review_topics,

            SUM(
                CASE
                    WHEN mastery < 50
                    THEN 1
                    ELSE 0
                END
            ) AS weak_topics,

            AVG(mastery) AS average_mastery

        FROM topics
        WHERE subject_id = ?
        """,
        (subject_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {
            "total_topics": 0,
            "strong_topics": 0,
            "review_topics": 0,
            "weak_topics": 0,
            "average_mastery": 0.0
        }

    return {
        "total_topics": row["total_topics"] or 0,
        "strong_topics": row["strong_topics"] or 0,
        "review_topics": row["review_topics"] or 0,
        "weak_topics": row["weak_topics"] or 0,
        "average_mastery": row["average_mastery"] or 0.0
    }


def get_latest_quiz_attempt(subject_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            qa.id,
            qa.score,
            qa.total_questions,
            qa.difficulty,
            qa.created_at,
            t.name AS topic

        FROM quiz_attempts qa

        JOIN topics t
            ON qa.topic_id = t.id

        WHERE t.subject_id = ?

        ORDER BY qa.created_at DESC

        LIMIT 1
        """,
        (subject_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)