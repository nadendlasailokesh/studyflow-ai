from datetime import date

from src.database.db import (
    get_connection,
    initialize_database,
)

from src.database.revision import (
    create_revision_record,
    get_revision_record,
    update_revision_record,
    record_revision,
    get_due_revisions,
    get_upcoming_revisions,
    reset_revision_streak,
)


# ============================================================
# DATABASE TABLE
# ============================================================

def test_revision_table_exists():

    initialize_database()

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'topic_revision'
            """
        )

        row = cursor.fetchone()

        assert row is not None

        assert row["name"] == "topic_revision"

    finally:

        connection.close()


# ============================================================
# HELPERS
# ============================================================

def create_test_student():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO students (
                name,
                knowledge_level
            )
            VALUES (?, ?)
            """,
            (
                "Revision Test Student",
                "BEGINNER",
            )
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
                "Revision Test Subject",
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
                "Revision Test Topic",
                "Unit I",
                "HIGH",
                60.0,
                "AVERAGE",
            )
        )

        topic_id = cursor.lastrowid

        connection.commit()

        return topic_id

    finally:

        connection.close()


# ============================================================
# CREATE
# ============================================================

def test_create_revision_record():

    initialize_database()

    topic_id = create_test_student()

    result = create_revision_record(

        topic_id=topic_id,

        score_percentage=60,

        revision_streak=0,

        reviewed_date=date(
            2026,
            8,
            15
        ),
    )

    assert result is not None

    assert result["topic_id"] == topic_id

    assert result["revision_streak"] == 0

    assert result["review_interval_days"] == 2

    assert (
        result["next_review_date"]
        == "2026-08-17"
    )


# ============================================================
# GET
# ============================================================

def test_get_revision_record():

    initialize_database()

    topic_id = create_test_student()

    create_revision_record(

        topic_id=topic_id,

        score_percentage=85,

        reviewed_date=date(
            2026,
            8,
            15
        ),
    )

    result = get_revision_record(
        topic_id
    )

    assert result is not None

    assert result["topic_id"] == topic_id

    assert result["review_interval_days"] == 7


# ============================================================
# UPDATE
# ============================================================

def test_update_revision_record():

    initialize_database()

    topic_id = create_test_student()

    create_revision_record(

        topic_id=topic_id,

        score_percentage=60,

        reviewed_date=date(
            2026,
            8,
            15
        ),
    )

    result = update_revision_record(

        topic_id=topic_id,

        score_percentage=85,

        revision_streak=1,

        reviewed_date=date(
            2026,
            8,
            20
        ),
    )

    assert result["revision_streak"] == 1

    assert result["review_interval_days"] == 7

    assert (
        result["last_reviewed_at"]
        == "2026-08-20"
    )

    assert (
        result["next_review_date"]
        == "2026-08-27"
    )


# ============================================================
# SUCCESSFUL REVISION
# ============================================================

def test_record_successful_revision_increases_streak():

    initialize_database()

    topic_id = create_test_student()

    create_revision_record(

        topic_id=topic_id,

        score_percentage=85,

        revision_streak=1,

        reviewed_date=date(
            2026,
            8,
            15
        ),
    )

    result = record_revision(

        topic_id=topic_id,

        score_percentage=95,

        reviewed_date=date(
            2026,
            8,
            30
        ),
    )

    assert result["revision_streak"] == 2

    assert result["review_interval_days"] == 28


# ============================================================
# WEAK REVISION
# ============================================================

def test_weak_revision_resets_streak():

    initialize_database()

    topic_id = create_test_student()

    create_revision_record(

        topic_id=topic_id,

        score_percentage=95,

        revision_streak=3,

        reviewed_date=date(
            2026,
            8,
            15
        ),
    )

    result = record_revision(

        topic_id=topic_id,

        score_percentage=40,

        reviewed_date=date(
            2026,
            8,
            20
        ),
    )

    assert result["revision_streak"] == 0

    assert result["review_interval_days"] == 1

    assert (
        result["next_review_date"]
        == "2026-08-21"
    )


# ============================================================
# DUE REVISIONS
# ============================================================

def test_get_due_revisions():

    initialize_database()

    topic_id = create_test_student()

    create_revision_record(

        topic_id=topic_id,

        score_percentage=40,

        reviewed_date=date(
            2026,
            8,
            15
        ),
    )

    result = get_due_revisions(

        review_date=date(
            2026,
            8,
            16
        )
    )

    assert len(result) >= 1

    matching = [
        item
        for item in result
        if item["topic_id"] == topic_id
    ]

    assert len(matching) == 1


# ============================================================
# UPCOMING REVISIONS
# ============================================================

def test_get_upcoming_revisions():

    initialize_database()

    topic_id = create_test_student()

    create_revision_record(

        topic_id=topic_id,

        score_percentage=60,

        reviewed_date=date(
            2026,
            8,
            15
        ),
    )

    result = get_upcoming_revisions(

        days=7,

        start_date=date(
            2026,
            8,
            15
        ),
    )

    matching = [
        item
        for item in result
        if item["topic_id"] == topic_id
    ]

    assert len(matching) == 1


# ============================================================
# RESET
# ============================================================

def test_reset_revision_streak():

    initialize_database()

    topic_id = create_test_student()

    create_revision_record(

        topic_id=topic_id,

        score_percentage=95,

        revision_streak=3,

        reviewed_date=date(
            2026,
            8,
            15
        ),
    )

    result = reset_revision_streak(

        topic_id=topic_id,

        reviewed_date=date(
            2026,
            8,
            20
        ),
    )

    assert result["revision_streak"] == 0

    assert result["review_interval_days"] == 1