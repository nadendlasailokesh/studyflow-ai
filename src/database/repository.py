from src.database.db import get_connection


# -----------------------------------
# Student
# -----------------------------------

def create_student(
    name,
    knowledge_level
):

    connection = get_connection()

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

    connection.close()

    return student_id


def get_student(student_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    connection.close()

    return student
# -----------------------------------
# Subject
# -----------------------------------

def create_subject(
    student_id,
    name,
    exam_date,
    daily_hours,
    goal
):

    connection = get_connection()

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

    connection.close()

    return subject_id


def get_subjects(student_id):

    connection = get_connection()

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

    subjects = cursor.fetchall()

    connection.close()

    return subjects
# -----------------------------------
# Topics
# -----------------------------------

def create_topic(
    subject_id,
    name,
    unit=None,
    priority="Medium"
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO topics (
            subject_id,
            name,
            unit,
            priority
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            subject_id,
            name,
            unit,
            priority
        )
    )

    topic_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return topic_id


def get_topics(subject_id):

    connection = get_connection()

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

    topics = cursor.fetchall()

    connection.close()

    return topics
# -----------------------------------
# Study Tasks
# -----------------------------------

def create_task(
    topic_id,
    task_name,
    task_date,
    duration_minutes
):

    connection = get_connection()

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

    connection.close()

    return task_id


def mark_task_completed(
    task_id,
    completed=True
):

    connection = get_connection()

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

    connection.close()
# -----------------------------------
# Quiz
# -----------------------------------

def save_quiz_attempt(
    topic_id,
    score,
    total_questions,
    difficulty
):

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

    attempt_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return attempt_id
# -----------------------------------
# Learning Session
# -----------------------------------

def save_learning_session(
    topic_id,
    mode,
    duration_minutes
):

    connection = get_connection()

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

    connection.close()

    return session_id
def get_all_subjects(student_id):

    connection = get_connection()

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

    subjects = cursor.fetchall()

    connection.close()

    return subjects
def update_subject(
    subject_id,
    name,
    exam_date,
    daily_hours,
    goal
):

    connection = get_connection()

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

    connection.close()
def delete_subject(subject_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM subjects
        WHERE id = ?
        """,
        (subject_id,)
    )

    connection.commit()

    connection.close()