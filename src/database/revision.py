# ============================================================
# REVISION DATABASE SERVICE
# StudyFlow AI
# Phase 8.3
# ============================================================

from datetime import date, datetime

from src.database.db import get_connection

from src.ai.revision_scheduler import (
    calculate_review_interval,
    calculate_next_review_date,
)


# ============================================================
# DATE HELPERS
# ============================================================

def _today():

    return date.today()


def _date_to_string(value):

    if isinstance(value, datetime):

        return value.date().isoformat()

    if isinstance(value, date):

        return value.isoformat()

    if value is None:

        return None

    return str(value)


# ============================================================
# GET REVISION RECORD
# ============================================================

def get_revision_record(topic_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                topic_id,
                revision_streak,
                review_interval_days,
                last_reviewed_at,
                next_review_date,
                created_at,
                updated_at
            FROM topic_revision
            WHERE topic_id = ?
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
# CREATE REVISION RECORD
# ============================================================

def create_revision_record(
    topic_id,
    score_percentage=0.0,
    revision_streak=0,
    reviewed_date=None,
):
    """
    Create the initial revision schedule for a topic.

    If a record already exists, the existing record is returned.
    """

    existing = get_revision_record(
        topic_id
    )

    if existing is not None:

        return existing

    if reviewed_date is None:

        reviewed_date = _today()

    interval = calculate_review_interval(

        score_percentage=score_percentage,

        revision_streak=revision_streak,
    )

    next_review = calculate_next_review_date(

        interval_days=interval,

        start_date=reviewed_date,
    )

    last_reviewed = _date_to_string(
        reviewed_date
    )

    next_review_string = _date_to_string(
        next_review
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO topic_revision (
                topic_id,
                revision_streak,
                review_interval_days,
                last_reviewed_at,
                next_review_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                int(revision_streak),
                interval,
                last_reviewed,
                next_review_string,
            )
        )

        connection.commit()

        revision_id = cursor.lastrowid

    finally:

        connection.close()

    return get_revision_record(
        topic_id
    )


# ============================================================
# UPDATE REVISION RECORD
# ============================================================

def update_revision_record(
    topic_id,
    score_percentage,
    revision_streak=None,
    reviewed_date=None,
):
    """
    Update the revision schedule after a review.

    If revision_streak is omitted, the existing streak is used.
    """

    existing = get_revision_record(
        topic_id
    )

    if existing is None:

        return create_revision_record(

            topic_id=topic_id,

            score_percentage=score_percentage,

            revision_streak=(
                revision_streak
                if revision_streak is not None
                else 0
            ),

            reviewed_date=reviewed_date,
        )

    current_streak = int(
        existing.get(
            "revision_streak",
            0
        )
        or 0
    )

    if revision_streak is None:

        revision_streak = current_streak

    revision_streak = max(
        0,
        int(revision_streak)
    )

    if reviewed_date is None:

        reviewed_date = _today()

    interval = calculate_review_interval(

        score_percentage=score_percentage,

        revision_streak=revision_streak,
    )

    next_review = calculate_next_review_date(

        interval_days=interval,

        start_date=reviewed_date,
    )

    last_reviewed = _date_to_string(
        reviewed_date
    )

    next_review_string = _date_to_string(
        next_review
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE topic_revision

            SET
                revision_streak = ?,
                review_interval_days = ?,
                last_reviewed_at = ?,
                next_review_date = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE topic_id = ?
            """,
            (
                revision_streak,
                interval,
                last_reviewed,
                next_review_string,
                topic_id,
            )
        )

        connection.commit()

    finally:

        connection.close()

    return get_revision_record(
        topic_id
    )


# ============================================================
# RECORD SUCCESSFUL REVISION
# ============================================================

def record_revision(
    topic_id,
    score_percentage,
    reviewed_date=None,
):
    """
    Record a completed revision.

    Strong performance increases the revision streak.

    Weak performance resets the streak.
    """

    existing = get_revision_record(
        topic_id
    )

    if existing is None:

        current_streak = 0

    else:

        current_streak = int(
            existing.get(
                "revision_streak",
                0
            )
            or 0
        )

    score = float(
        score_percentage
    )

    if score >= 80:

        new_streak = (
            current_streak + 1
        )

    else:

        new_streak = 0

    return update_revision_record(

        topic_id=topic_id,

        score_percentage=score,

        revision_streak=new_streak,

        reviewed_date=reviewed_date,
    )


# ============================================================
# GET DUE REVISIONS
# ============================================================

def get_due_revisions(
    review_date=None
):
    """
    Return topics whose next review date is today
    or earlier.

    Results are ordered by oldest review date first.
    """

    if review_date is None:

        review_date = _today()

    review_date = _date_to_string(
        review_date
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                tr.id,
                tr.topic_id,
                tr.revision_streak,
                tr.review_interval_days,
                tr.last_reviewed_at,
                tr.next_review_date,
                t.name AS topic_name,
                t.unit,
                t.mastery,
                t.status,
                t.priority,
                t.subject_id

            FROM topic_revision tr

            INNER JOIN topics t
                ON t.id = tr.topic_id

            WHERE
                tr.next_review_date IS NOT NULL
                AND tr.next_review_date <= ?

            ORDER BY
                tr.next_review_date ASC
            """,
            (review_date,)
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# GET UPCOMING REVISIONS
# ============================================================

def get_upcoming_revisions(
    days=7,
    start_date=None,
):
    """
    Return revisions scheduled between start_date
    and start_date + days.
    """

    if start_date is None:

        start_date = _today()

    if not isinstance(
        start_date,
        date
    ):

        raise TypeError(
            "start_date must be a date."
        )

    days = max(
        0,
        int(days)
    )

    end_date = (
        start_date
        + __import__(
            "datetime"
        ).timedelta(
            days=days
        )
    )

    start_string = _date_to_string(
        start_date
    )

    end_string = _date_to_string(
        end_date
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                tr.id,
                tr.topic_id,
                tr.revision_streak,
                tr.review_interval_days,
                tr.last_reviewed_at,
                tr.next_review_date,
                t.name AS topic_name,
                t.unit,
                t.mastery,
                t.status,
                t.priority,
                t.subject_id

            FROM topic_revision tr

            INNER JOIN topics t
                ON t.id = tr.topic_id

            WHERE
                tr.next_review_date IS NOT NULL
                AND tr.next_review_date >= ?
                AND tr.next_review_date <= ?

            ORDER BY
                tr.next_review_date ASC
            """,
            (
                start_string,
                end_string,
            )
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# RESET REVISION STREAK
# ============================================================

def reset_revision_streak(
    topic_id,
    reviewed_date=None,
):
    """
    Reset a topic's revision streak.

    Useful when a learner's performance drops significantly.
    """

    existing = get_revision_record(
        topic_id
    )

    if existing is None:

        return create_revision_record(

            topic_id=topic_id,

            score_percentage=0.0,

            revision_streak=0,

            reviewed_date=reviewed_date,
        )

    return update_revision_record(

        topic_id=topic_id,

        score_percentage=0.0,

        revision_streak=0,

        reviewed_date=reviewed_date,
    )