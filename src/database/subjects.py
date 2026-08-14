from src.database.db import get_connection


def create_student(name, knowledge_level="Beginner"):

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
        (name, knowledge_level)
    )

    connection.commit()

    student_id = cursor.lastrowid

    connection.close()

    return student_id


def create_subject(
    student_id,
    name,
    exam_date=None,
    daily_hours=None,
    goal=None
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

    connection.commit()

    subject_id = cursor.lastrowid

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

    subjects = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return subjects


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

    deleted = cursor.rowcount

    connection.close()

    return deleted


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
        SET name = ?,
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

    updated = cursor.rowcount

    connection.close()

    return updated