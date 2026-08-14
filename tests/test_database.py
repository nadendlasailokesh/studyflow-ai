from src.database.db import initialize_database
from src.database.db import get_connection


def test_database_initialization():

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """
    )

    tables = {
        row["name"]
        for row in cursor.fetchall()
    }

    expected_tables = {
        "students",
        "subjects",
        "topics",
        "study_tasks",
        "quiz_attempts",
        "learning_sessions"
    }

    assert expected_tables.issubset(tables)

    connection.close()
def test_topic_progress_persistence():

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    # Create test student
    cursor.execute(
        """
        INSERT INTO students (
            name,
            knowledge_level
        )
        VALUES (?, ?)
        """,
        (
            "Test Student",
            "Beginner"
        )
    )

    student_id = cursor.lastrowid

    # Create test subject
    cursor.execute(
        """
        INSERT INTO subjects (
            student_id,
            name
        )
        VALUES (?, ?)
        """,
        (
            student_id,
            "Data Mining"
        )
    )

    subject_id = cursor.lastrowid

    # Create test topic
    cursor.execute(
        """
        INSERT INTO topics (
            subject_id,
            name
        )
        VALUES (?, ?)
        """,
        (
            subject_id,
            "Decision Trees"
        )
    )

    topic_id = cursor.lastrowid

    connection.commit()

    connection.close()


    from src.database.progress import (
        save_quiz_attempt,
        update_topic_mastery,
        get_topic_progress,
        get_quiz_history
    )


    attempt_id = save_quiz_attempt(

        topic_id=topic_id,

        score=8,

        total_questions=10,

        difficulty="MEDIUM"
    )

    assert attempt_id is not None


    updated = update_topic_mastery(

        topic_id=topic_id,

        mastery=80,

        status="STRONG"
    )

    assert updated == 1


    progress = get_topic_progress(
        topic_id
    )

    assert progress is not None

    assert progress["mastery"] == 80

    assert progress["status"] == "STRONG"


    history = get_quiz_history(
        topic_id
    )

    assert len(history) >= 1

    assert history[0]["score"] == 8