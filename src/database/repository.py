import json

from src.database.db import get_connection


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

        # ----------------------------------------------------
        # Normalize values
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Store prerequisites as JSON
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Insert
        # ----------------------------------------------------

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

            # ------------------------------------------------
            # Convert prerequisites JSON → Python list
            # ------------------------------------------------

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


        # ----------------------------------------------------
        # Remove previous topics
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM topics
            WHERE subject_id = ?
            """,
            (subject_id,)
        )


        saved_topic_ids = []


        # ----------------------------------------------------
        # Insert AI-generated topics
        # ----------------------------------------------------

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


            estimated_minutes = (

                int(topic.estimated_minutes)

                if topic.estimated_minutes

                else 60

            )


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
# PROGRESS - GET TOPIC MASTERY
# ============================================================

def get_topic_mastery_for_student(student_id):
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

        return [dict(row) for row in rows]

    finally:

        connection.close()


# ============================================================
# PROGRESS - QUIZ STATISTICS
# ============================================================

def get_quiz_statistics_for_student(student_id):
    """
    Return quiz statistics for the student.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(quiz_attempts.id) AS attempts,

                COALESCE(
                    SUM(quiz_attempts.total_questions),
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

        if not row:
            return {
                "attempts": 0,
                "total_questions": 0,
                "correct_answers": 0
            }

        return dict(row)

    finally:

        connection.close()


# ============================================================
# PROGRESS - SUBJECT PROGRESS
# ============================================================

def get_subject_progress(student_id):
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

                COUNT(topics.id) AS total_topics,

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

        return [dict(row) for row in rows]

    finally:

        connection.close()