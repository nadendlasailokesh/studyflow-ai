# ============================================================
# REVISION INTEGRATION TESTS
# StudyFlow AI
# Phase 8.4
# ============================================================

from datetime import date

from src.ai.revision_integration import (
    update_revision_after_quiz,
)

from src.database.db import (
    get_connection,
    initialize_database,
)

from src.database.revision import (
    get_revision_record,
)


def create_student_subject_topic():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO students (
                name
            )
            VALUES (?)
            """,
            ("Revision Integration Test",)
        )

        student_id = cursor.lastrowid

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
                "Test Subject",
            )
        )

        subject_id = cursor.lastrowid

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
                "Test Topic",
                "Unit I",
                "HIGH",
                0.0,
                "Not Started",
            )
        )

        topic_id = cursor.lastrowid

        connection.commit()

        return topic_id

    finally:

        connection.close()


def test_weak_quiz_creates_revision():

    initialize_database()

    topic_id = create_student_subject_topic()

    revision = update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=40,
    )

    assert revision is not None

    assert revision["topic_id"] == topic_id

    assert revision["revision_streak"] == 0

    assert revision["review_interval_days"] == 1

    assert revision["next_review_date"] is not None


def test_average_quiz_creates_short_revision():

    initialize_database()

    topic_id = create_student_subject_topic()

    revision = update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=60,
    )

    assert revision["review_interval_days"] == 2


def test_strong_quiz_creates_revision():

    initialize_database()

    topic_id = create_student_subject_topic()

    revision = update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=85,
    )

    assert revision["revision_streak"] == 1

    assert revision["review_interval_days"] == 7


def test_excellent_quiz_creates_longer_revision():

    initialize_database()

    topic_id = create_student_subject_topic()

    revision = update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=95,
    )

    assert revision["revision_streak"] == 1

    assert revision["review_interval_days"] == 14


def test_successful_quiz_increases_existing_streak():

    initialize_database()

    topic_id = create_student_subject_topic()

    first = update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=90,
    )

    assert first["revision_streak"] == 1

    second = update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=90,
    )

    assert second["revision_streak"] == 2

    assert second["review_interval_days"] == 28


def test_weak_quiz_resets_existing_streak():

    initialize_database()

    topic_id = create_student_subject_topic()

    update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=90,
    )

    update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=90,
    )

    revision = update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=40,
    )

    assert revision["revision_streak"] == 0

    assert revision["review_interval_days"] == 1


def test_revision_record_is_persisted():

    initialize_database()

    topic_id = create_student_subject_topic()

    update_revision_after_quiz(

        topic_id=topic_id,

        score_percentage=75,
    )

    revision = get_revision_record(
        topic_id
    )

    assert revision is not None

    assert revision["topic_id"] == topic_id

    assert revision["review_interval_days"] == 4


def test_invalid_topic_id_is_rejected():

    initialize_database()

    try:

        update_revision_after_quiz(

            topic_id=None,

            score_percentage=80,
        )

    except ValueError as error:

        assert "topic_id" in str(error)

    else:

        raise AssertionError(
            "Expected ValueError"
        )