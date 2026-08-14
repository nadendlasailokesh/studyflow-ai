from src.database.db import (
    initialize_database,
    get_connection
)

from src.database.subjects import (
    create_student,
    create_subject
)

from src.database.dashboard import (
    get_subject_topics,
    get_topic_statistics,
    get_latest_quiz_attempt
)


def create_test_data():

    initialize_database()

    student_id = create_student(
        "Dashboard Test Student"
    )

    subject_id = create_subject(
        student_id=student_id,
        name="Data Mining",
        exam_date="2026-09-15",
        daily_hours=2,
        goal="Prepare for exam"
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO topics (
            subject_id,
            name,
            unit,
            priority,
            mastery,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            subject_id,
            "Decision Trees",
            "Unit 2",
            "HIGH",
            90,
            "STRONG"
        )
    )

    strong_topic_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO topics (
            subject_id,
            name,
            unit,
            priority,
            mastery,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            subject_id,
            "Entropy",
            "Unit 2",
            "HIGH",
            30,
            "WEAK"
        )
    )

    weak_topic_id = cursor.lastrowid

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
            weak_topic_id,
            3,
            10,
            "MEDIUM"
        )
    )

    connection.commit()
    connection.close()

    return subject_id


def test_dashboard_topics():

    subject_id = create_test_data()

    topics = get_subject_topics(
        subject_id
    )

    assert len(topics) >= 2


def test_dashboard_statistics():

    subject_id = create_test_data()

    stats = get_topic_statistics(
        subject_id
    )

    assert stats["total_topics"] >= 2

    assert stats["strong_topics"] >= 1

    assert stats["weak_topics"] >= 1

    assert stats["average_mastery"] >= 0


def test_latest_quiz():

    subject_id = create_test_data()

    latest = get_latest_quiz_attempt(
        subject_id
    )

    assert latest is not None

    assert latest["score"] == 3

    assert latest["total_questions"] == 10