# ============================================================
# DATABASE REPOSITORY
# StudyFlow AI
# ============================================================

import json

from src.database.db import get_connection


# ============================================================
# STUDENT
# ============================================================

# ============================================================
# STUDENT
# ============================================================

def create_student(
    name,
    knowledge_level="Beginner"
):

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
                name,
                knowledge_level
            )
        )

        student_id = cursor.lastrowid

        connection.commit()

        return student_id

    finally:

        connection.close()


def get_student(student_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE id = ?
            """,
            (student_id,)
        )

        return cursor.fetchone()

    finally:

        connection.close()


def get_student_by_name(name):
    """
    Find an existing student by name.

    Matching is:
    - case-insensitive
    - ignores leading/trailing spaces

    If multiple students have the same name,
    the most recently created student is returned.
    """

    if not name:
        return None

    name = str(name).strip()

    if not name:
        return None

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
            ORDER BY id DESC
            LIMIT 1
            """,
            (name,)
        )

        return cursor.fetchone()

    finally:

        connection.close()
# ============================================================
# UPDATE STUDENT PROFILE

# ============================================================

def update_student(
    student_id,
    name=None,
    knowledge_level=None
):
    """
    Update a student's profile.

    Only supplied fields are changed.
    Existing values are preserved when a field is None.

    Returns:
        Updated student row, or None if the student does not exist.
    """

    if student_id is None:
        raise ValueError(
            "student_id is required."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Verify student exists
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE id = ?
            """,
            (student_id,)
        )

        existing = cursor.fetchone()

        if existing is None:
            return None

        # ----------------------------------------------------
        # Preserve existing values
        # ----------------------------------------------------

        updated_name = (
            existing["name"]
            if name is None
            else str(name).strip()
        )

        updated_knowledge_level = (
            existing["knowledge_level"]
            if knowledge_level is None
            else str(knowledge_level).strip()
        )

        # ----------------------------------------------------
        # Validate name
        # ----------------------------------------------------

        if not updated_name:
            raise ValueError(
                "Student name cannot be empty."
            )

        # ----------------------------------------------------
        # Validate knowledge level
        # ----------------------------------------------------

        allowed_levels = {
            "Beginner",
            "Intermediate",
            "Advanced",
        }

        if (
            updated_knowledge_level
            and updated_knowledge_level
            not in allowed_levels
        ):
            raise ValueError(
                "Knowledge level must be "
                "Beginner, Intermediate, or Advanced."
            )

        # ----------------------------------------------------
        # Update
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE students
            SET
                name = ?,
                knowledge_level = ?
            WHERE id = ?
            """,
            (
                updated_name,
                updated_knowledge_level,
                student_id
            )
        )

        connection.commit()

        # ----------------------------------------------------
        # Return updated student
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE id = ?
            """,
            (student_id,)
        )

        return cursor.fetchone()

    finally:

        connection.close()


# ============================================================
# SUBJECT
# ============================================================

def create_subject(
    student_id,
    name,
    exam_date=None,
    daily_hours=None,
    goal=None
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO subjects (
                student_id,
                name,
                exam_date,
                daily_hours,
                goal
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student_id,
                name,
                exam_date,
                daily_hours,
                goal
            )
        )

        subject_id = cursor.lastrowid

        connection.commit()

        return subject_id

    finally:

        connection.close()


def get_subjects(student_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM subjects
            WHERE student_id = ?
            ORDER BY created_at DESC
            """,
            (student_id,)
        )

        return cursor.fetchall()

    finally:

        connection.close()


def get_all_subjects(student_id):

    return get_subjects(student_id)


def update_subject(
    subject_id,
    name,
    exam_date,
    daily_hours,
    goal
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE subjects
            SET
                name = ?,
                exam_date = ?,
                daily_hours = ?,
                goal = ?
            WHERE id = ?
            """,
            (
                name,
                exam_date,
                daily_hours,
                goal,
                subject_id
            )
        )

        connection.commit()

        return cursor.rowcount

    finally:

        connection.close()


def delete_subject(subject_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM subjects
            WHERE id = ?
            """,
            (subject_id,)
        )

        connection.commit()

        return cursor.rowcount

    finally:

        connection.close()


# ============================================================
# TOPICS
# ============================================================

def create_topic(
    subject_id,
    name,
    unit=None,
    priority="MEDIUM",
    estimated_minutes=60,
    reason=None,
    prerequisites=None
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        name = str(name).strip()

        unit = (
            str(unit).strip()
            if unit
            else None
        )

        priority = (
            str(priority).upper().strip()
            if priority
            else "MEDIUM"
        )

        if priority not in {
            "HIGH",
            "MEDIUM",
            "LOW"
        }:

            priority = "MEDIUM"

        try:

            estimated_minutes = int(
                estimated_minutes
            )

        except (
            TypeError,
            ValueError
        ):

            estimated_minutes = 60

        estimated_minutes = max(
            15,
            min(
                estimated_minutes,
                600
            )
        )

        if prerequisites is None:

            prerequisites = []

        elif not isinstance(
            prerequisites,
            list
        ):

            prerequisites = [
                str(prerequisites)
            ]

        prerequisites_json = json.dumps(
            prerequisites,
            ensure_ascii=False
        )

        cursor.execute(
            """
            INSERT INTO topics (
                subject_id,
                name,
                unit,
                priority,
                estimated_minutes,
                reason,
                prerequisites
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subject_id,
                name,
                unit,
                priority,
                estimated_minutes,
                reason,
                prerequisites_json
            )
        )

        topic_id = cursor.lastrowid

        connection.commit()

        return topic_id

    finally:

        connection.close()


# ============================================================
# GET TOPICS
# ============================================================

def get_topics(subject_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM topics
            WHERE subject_id = ?
            ORDER BY id
            """,
            (subject_id,)
        )

        rows = cursor.fetchall()

        topics = []

        for row in rows:

            topic = dict(row)

            prerequisites = (
                topic.get("prerequisites")
                or "[]"
            )

            try:

                topic["prerequisites"] = json.loads(
                    prerequisites
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):

                topic["prerequisites"] = []

            topics.append(topic)

        return topics

    finally:

        connection.close()


# ============================================================
# SAVE AI-ANALYZED SYLLABUS TOPICS
# ============================================================

def save_syllabus_topics(
    subject_id,
    topics
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM topics
            WHERE subject_id = ?
            """,
            (subject_id,)
        )

        saved_topic_ids = []

        for topic in topics:

            topic_name = (
                topic.topic.strip()
            )

            if not topic_name:

                continue

            unit = (
                topic.unit.strip()
                if topic.unit
                else None
            )

            priority = (
                topic.priority.upper()
                if topic.priority
                else "MEDIUM"
            )

            if priority not in {
                "HIGH",
                "MEDIUM",
                "LOW"
            }:

                priority = "MEDIUM"

            try:

                estimated_minutes = int(
                    topic.estimated_minutes
                )

            except (
                TypeError,
                ValueError
            ):

                estimated_minutes = 60

            estimated_minutes = max(
                15,
                min(
                    estimated_minutes,
                    600
                )
            )

            reason = (
                topic.reason.strip()
                if topic.reason
                else None
            )

            prerequisites = (
                topic.prerequisites
                if topic.prerequisites
                else []
            )

            prerequisites_json = json.dumps(
                prerequisites,
                ensure_ascii=False
            )

            cursor.execute(
                """
                INSERT INTO topics (
                    subject_id,
                    name,
                    unit,
                    priority,
                    estimated_minutes,
                    reason,
                    prerequisites
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    subject_id,
                    topic_name,
                    unit,
                    priority,
                    estimated_minutes,
                    reason,
                    prerequisites_json
                )
            )

            saved_topic_ids.append(
                cursor.lastrowid
            )

        connection.commit()

        return saved_topic_ids

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# ============================================================
# DELETE TOPICS
# ============================================================

def delete_topics_for_subject(
    subject_id
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM topics
            WHERE subject_id = ?
            """,
            (subject_id,)
        )

        connection.commit()

        return cursor.rowcount

    finally:

        connection.close()


# ============================================================
# STUDY TASKS
# ============================================================

def create_task(
    topic_id,
    task_name,
    task_date,
    duration_minutes
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO study_tasks (
                topic_id,
                task_name,
                task_date,
                duration_minutes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                topic_id,
                task_name,
                task_date,
                duration_minutes
            )
        )

        task_id = cursor.lastrowid

        connection.commit()

        return task_id

    finally:

        connection.close()


def mark_task_completed(
    task_id,
    completed=True
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE study_tasks
            SET completed = ?
            WHERE id = ?
            """,
            (
                1 if completed else 0,
                task_id
            )
        )

        connection.commit()

        return cursor.rowcount

    finally:

        connection.close()


# ============================================================
# QUIZ
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
    `score` must be a percentage from 0 to 100.
    Example:
        4/5 = 80.0
    """

    if total_questions <= 0:
        raise ValueError(
            "Total questions must be greater than zero."
        )

    score = float(score)

    # Safety normalization
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

        attempt_id = cursor.lastrowid

        connection.commit()

        return attempt_id

    finally:

        connection.close()


# ============================================================
# LEARNING SESSION
# ============================================================

def save_learning_session(
    topic_id,
    mode,
    duration_minutes
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO learning_sessions (
                topic_id,
                mode,
                duration_minutes
            )
            VALUES (?, ?, ?)
            """,
            (
                topic_id,
                mode,
                duration_minutes
            )
        )

        session_id = cursor.lastrowid

        connection.commit()

        return session_id

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
                float(mastery),
                status,
                topic_id
            )
        )

        connection.commit()

        return cursor.rowcount

    finally:

        connection.close()


# ============================================================
# GET TOPIC QUIZ HISTORY
# ============================================================

def get_topic_quiz_history(
    topic_id
):
    """
    Return all quiz attempts for a topic.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                topic_id,
                score,
                total_questions,
                difficulty,
                created_at
            FROM quiz_attempts
            WHERE topic_id = ?
            ORDER BY id ASC
            """,
            (
                topic_id,
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
# GET TOPIC QUIZ MASTERY
# ============================================================


def get_topic_quiz_mastery(topic_id):
    """
    Calculate topic mastery from quiz attempts.

    Database `score` is stored as a percentage.

    Example:
        80 + 60
        -------
           2

        = 70% mastery
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                COALESCE(
                    AVG(score),
                    0
                ) AS average_score,

                COUNT(id) AS attempts

            FROM quiz_attempts

            WHERE topic_id = ?
            """,
            (topic_id,)
        )

        row = cursor.fetchone()

        if row is None:

            return {
                "mastery": 0.0,
                "attempts": 0
            }

        mastery = float(
            row["average_score"] or 0
        )

        mastery = max(
            0.0,
            min(mastery, 100.0)
        )

        return {
            "mastery": round(
                mastery,
                2
            ),

            "attempts": int(
                row["attempts"] or 0
            )
        }

    finally:

        connection.close()


# ============================================================
# PROGRESS - GET TOPIC MASTERY
# ============================================================

def get_topic_mastery_for_student(
    student_id
):
    """
    Return all topics belonging to all subjects
    of the given student.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                topics.id,
                topics.name,
                topics.unit,
                topics.priority,
                topics.mastery,
                topics.status,
                topics.estimated_minutes,

                subjects.name AS subject_name,
                subjects.id AS subject_id

            FROM topics

            INNER JOIN subjects
                ON topics.subject_id = subjects.id

            WHERE subjects.student_id = ?

            ORDER BY
                topics.mastery ASC,
                topics.id ASC
            """,
            (student_id,)
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# PROGRESS - QUIZ STATISTICS
# ============================================================


def get_quiz_statistics_for_student(
    student_id
):
    """
    Return overall quiz statistics for the student.

    `score` is stored as percentage.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(
                    quiz_attempts.id
                ) AS attempts,

                COALESCE(
                    SUM(
                        quiz_attempts.total_questions
                    ),
                    0
                ) AS total_questions,

                COALESCE(
                    SUM(
                        quiz_attempts.score
                        * quiz_attempts.total_questions
                        / 100.0
                    ),
                    0
                ) AS correct_answers

            FROM quiz_attempts

            INNER JOIN topics
                ON quiz_attempts.topic_id = topics.id

            INNER JOIN subjects
                ON topics.subject_id = subjects.id

            WHERE subjects.student_id = ?
            """,
            (student_id,)
        )

        row = cursor.fetchone()

        if row is None:

            return {
                "attempts": 0,
                "total_questions": 0,
                "correct_answers": 0
            }

        return {
            "attempts": int(
                row["attempts"] or 0
            ),

            "total_questions": int(
                row["total_questions"] or 0
            ),

            "correct_answers": float(
                row["correct_answers"] or 0
            )
        }

    finally:

        connection.close()


# ============================================================
# PROGRESS - SUBJECT PROGRESS
# ============================================================

def get_subject_progress(
    student_id
):
    """
    Return progress grouped by subject.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                subjects.id AS subject_id,

                subjects.name AS subject_name,

                COUNT(
                    topics.id
                ) AS total_topics,

                COALESCE(
                    AVG(topics.mastery),
                    0
                ) AS average_mastery

            FROM subjects

            LEFT JOIN topics
                ON subjects.id = topics.subject_id

            WHERE subjects.student_id = ?

            GROUP BY
                subjects.id,
                subjects.name

            ORDER BY subjects.name
            """,
            (student_id,)
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()

# ============================================================
# PROGRESS - ADVANCED STUDENT SUMMARY
# ============================================================

def get_student_progress_summary(student_id):
    """
    Return advanced progress metrics for a student.

    Metrics:
        total_topics
        strong_topics
        average_topics
        weak_topics
        not_started_topics
        completed_topics
        average_mastery
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT

                COUNT(topics.id) AS total_topics,

                SUM(
                    CASE
                        WHEN COALESCE(topics.mastery, 0) >= 80
                        THEN 1
                        ELSE 0
                    END
                ) AS strong_topics,

                SUM(
                    CASE
                        WHEN COALESCE(topics.mastery, 0) >= 50
                         AND COALESCE(topics.mastery, 0) < 80
                        THEN 1
                        ELSE 0
                    END
                ) AS average_topics,

                SUM(
                    CASE
                        WHEN COALESCE(topics.mastery, 0) > 0
                         AND COALESCE(topics.mastery, 0) < 50
                        THEN 1
                        ELSE 0
                    END
                ) AS weak_topics,

                SUM(
                    CASE
                        WHEN COALESCE(topics.mastery, 0) = 0
                        THEN 1
                        ELSE 0
                    END
                ) AS not_started_topics,

                AVG(
                    COALESCE(topics.mastery, 0)
                ) AS average_mastery

            FROM topics

            INNER JOIN subjects
                ON topics.subject_id = subjects.id

            WHERE subjects.student_id = ?
            """,
            (student_id,)
        )

        row = cursor.fetchone()

        if row is None:

            return {
                "total_topics": 0,
                "strong_topics": 0,
                "average_topics": 0,
                "weak_topics": 0,
                "not_started_topics": 0,
                "completed_topics": 0,
                "average_mastery": 0.0,
            }

        total_topics = int(
            row["total_topics"] or 0
        )

        strong_topics = int(
            row["strong_topics"] or 0
        )

        average_topics = int(
            row["average_topics"] or 0
        )

        weak_topics = int(
            row["weak_topics"] or 0
        )

        not_started_topics = int(
            row["not_started_topics"] or 0
        )

        average_mastery = float(
            row["average_mastery"] or 0.0
        )

        return {
            "total_topics": total_topics,

            "strong_topics": strong_topics,

            "average_topics": average_topics,

            "weak_topics": weak_topics,

            "not_started_topics": not_started_topics,

            "completed_topics": strong_topics,

            "average_mastery": round(
                average_mastery,
                2
            ),
        }

    finally:

        connection.close()
# ============================================================
# PHASE 9.3
# QUIZ PERFORMANCE ANALYTICS
# ============================================================

def get_quiz_performance_analytics(student_id):
    """
    Return quiz performance analytics for a student.

    The returned statistics are calculated only from quiz
    attempts belonging to the student's topics.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Overall quiz statistics
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(qa.id) AS attempts,

                COALESCE(
                    SUM(qa.total_questions),
                    0
                ) AS total_questions,

                COALESCE(
                    SUM(
                        qa.score
                        * qa.total_questions
                        / 100.0
                    ),
                    0
                ) AS correct_answers,

                COALESCE(
                    AVG(qa.score),
                    0
                ) AS average_score,

                COALESCE(
                    MAX(qa.score),
                    0
                ) AS best_score,

                COALESCE(
                    MIN(qa.score),
                    0
                ) AS lowest_score

            FROM quiz_attempts qa

            INNER JOIN topics t
                ON qa.topic_id = t.id

            INNER JOIN subjects s
                ON t.subject_id = s.id

            WHERE s.student_id = ?
            """,
            (student_id,)
        )

        row = cursor.fetchone()

        if row is None:

            overall = {
                "attempts": 0,
                "total_questions": 0,
                "correct_answers": 0.0,
                "average_score": 0.0,
                "best_score": 0.0,
                "lowest_score": 0.0,
            }

        else:

            overall = {
                "attempts": int(
                    row["attempts"] or 0
                ),

                "total_questions": int(
                    row["total_questions"] or 0
                ),

                "correct_answers": round(
                    float(
                        row["correct_answers"] or 0
                    ),
                    2
                ),

                "average_score": round(
                    float(
                        row["average_score"] or 0
                    ),
                    2
                ),

                "best_score": round(
                    float(
                        row["best_score"] or 0
                    ),
                    2
                ),

                "lowest_score": round(
                    float(
                        row["lowest_score"] or 0
                    ),
                    2
                ),
            }

        # ----------------------------------------------------
        # Performance by difficulty
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                qa.difficulty,

                COUNT(qa.id) AS attempts,

                COALESCE(
                    AVG(qa.score),
                    0
                ) AS average_score

            FROM quiz_attempts qa

            INNER JOIN topics t
                ON qa.topic_id = t.id

            INNER JOIN subjects s
                ON t.subject_id = s.id

            WHERE s.student_id = ?

            GROUP BY qa.difficulty

            ORDER BY qa.difficulty
            """,
            (student_id,)
        )

        difficulty_rows = cursor.fetchall()

        by_difficulty = []

        for difficulty in difficulty_rows:

            by_difficulty.append(
                {
                    "difficulty":
                        difficulty["difficulty"]
                        or "Unknown",

                    "attempts":
                        int(
                            difficulty["attempts"]
                            or 0
                        ),

                    "average_score":
                        round(
                            float(
                                difficulty[
                                    "average_score"
                                ]
                                or 0
                            ),
                            2
                        ),
                }
            )

        # ----------------------------------------------------
        # Topic-wise quiz performance
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                t.id AS topic_id,

                t.name AS topic_name,

                s.id AS subject_id,

                s.name AS subject_name,

                COUNT(qa.id) AS attempts,

                COALESCE(
                    AVG(qa.score),
                    0
                ) AS average_score,

                COALESCE(
                    MAX(qa.score),
                    0
                ) AS best_score

            FROM quiz_attempts qa

            INNER JOIN topics t
                ON qa.topic_id = t.id

            INNER JOIN subjects s
                ON t.subject_id = s.id

            WHERE s.student_id = ?

            GROUP BY
                t.id,
                t.name,
                s.id,
                s.name

            ORDER BY
                average_score ASC,
                t.name ASC
            """,
            (student_id,)
        )

        topic_rows = cursor.fetchall()

        by_topic = []

        for topic in topic_rows:

            by_topic.append(
                {
                    "topic_id":
                        topic["topic_id"],

                    "topic_name":
                        topic["topic_name"],

                    "subject_id":
                        topic["subject_id"],

                    "subject_name":
                        topic["subject_name"],

                    "attempts":
                        int(
                            topic["attempts"]
                            or 0
                        ),

                    "average_score":
                        round(
                            float(
                                topic["average_score"]
                                or 0
                            ),
                            2
                        ),

                    "best_score":
                        round(
                            float(
                                topic["best_score"]
                                or 0
                            ),
                            2
                        ),
                }
            )

        # ----------------------------------------------------
        # Recent quiz attempts
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                qa.id,

                qa.score,

                qa.total_questions,

                qa.difficulty,

                qa.created_at,

                t.id AS topic_id,

                t.name AS topic_name,

                s.name AS subject_name

            FROM quiz_attempts qa

            INNER JOIN topics t
                ON qa.topic_id = t.id

            INNER JOIN subjects s
                ON t.subject_id = s.id

            WHERE s.student_id = ?

            ORDER BY
                qa.created_at DESC,
                qa.id DESC

            LIMIT 10
            """,
            (student_id,)
        )

        recent_rows = cursor.fetchall()

        recent_attempts = []

        for attempt in recent_rows:

            recent_attempts.append(
                {
                    "id":
                        attempt["id"],

                    "score":
                        round(
                            float(
                                attempt["score"]
                                or 0
                            ),
                            2
                        ),

                    "total_questions":
                        int(
                            attempt[
                                "total_questions"
                            ]
                            or 0
                        ),

                    "difficulty":
                        attempt[
                            "difficulty"
                        ]
                        or "Unknown",

                    "created_at":
                        attempt[
                            "created_at"
                        ],

                    "topic_id":
                        attempt["topic_id"],

                    "topic_name":
                        attempt["topic_name"],

                    "subject_name":
                        attempt[
                            "subject_name"
                        ],
                }
            )

        return {
            "overall": overall,

            "by_difficulty":
                by_difficulty,

            "by_topic":
                by_topic,

            "recent_attempts":
                recent_attempts,
        }

    finally:

        connection.close()
# ============================================================
# PHASE 9.4
# LEARNING TRENDS
# ============================================================

def get_learning_trends(
    student_id,
    limit=10
):
    """
    Return recent learning performance trends.

    Trends are calculated from quiz attempts belonging
    only to the specified student.

    Returns:
        {
            "attempts": [...],
            "summary": {...}
        }
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Recent quiz attempts
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                qa.id,
                qa.score,
                qa.total_questions,
                qa.difficulty,
                qa.created_at,

                t.id AS topic_id,
                t.name AS topic_name,

                s.id AS subject_id,
                s.name AS subject_name

            FROM quiz_attempts qa

            INNER JOIN topics t
                ON qa.topic_id = t.id

            INNER JOIN subjects s
                ON t.subject_id = s.id

            WHERE s.student_id = ?

            ORDER BY
                qa.created_at ASC,
                qa.id ASC

            LIMIT ?
            """,
            (
                student_id,
                int(limit)
            )
        )

        rows = cursor.fetchall()

        attempts = []

        for row in rows:

            attempts.append(
                {
                    "id": row["id"],

                    "score": round(
                        float(
                            row["score"] or 0
                        ),
                        2
                    ),

                    "total_questions": int(
                        row[
                            "total_questions"
                        ]
                        or 0
                    ),

                    "difficulty": (
                        row["difficulty"]
                        or "Unknown"
                    ),

                    "created_at":
                        row["created_at"],

                    "topic_id":
                        row["topic_id"],

                    "topic_name":
                        row["topic_name"],

                    "subject_id":
                        row["subject_id"],

                    "subject_name":
                        row["subject_name"],
                }
            )

        # ----------------------------------------------------
        # No quiz history
        # ----------------------------------------------------

        if not attempts:

            return {
                "attempts": [],

                "summary": {
                    "trend": "NO_DATA",
                    "change": 0.0,
                    "first_score": 0.0,
                    "latest_score": 0.0,
                    "highest_score": 0.0,
                    "lowest_score": 0.0,
                }
            }

        # ----------------------------------------------------
        # Score values
        # ----------------------------------------------------

        scores = [
            float(
                attempt["score"]
            )
            for attempt in attempts
        ]

        first_score = scores[0]

        latest_score = scores[-1]

        highest_score = max(scores)

        lowest_score = min(scores)

        change = round(
            latest_score - first_score,
            2
        )

        # ----------------------------------------------------
        # Determine trend
        # ----------------------------------------------------

        if len(scores) < 2:

            trend = "INSUFFICIENT_DATA"

        elif change >= 5:

            trend = "IMPROVING"

        elif change <= -5:

            trend = "DECLINING"

        else:

            trend = "STABLE"

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {
            "attempts": attempts,

            "summary": {
                "trend": trend,

                "change": change,

                "first_score":
                    round(
                        first_score,
                        2
                    ),

                "latest_score":
                    round(
                        latest_score,
                        2
                    ),

                "highest_score":
                    round(
                        highest_score,
                        2
                    ),

                "lowest_score":
                    round(
                        lowest_score,
                        2
                    ),
            }
        }

    finally:

        connection.close()