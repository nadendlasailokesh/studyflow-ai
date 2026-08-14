from src.database.db import (
    initialize_database,
    get_connection
)

from src.database.subjects import (
    create_student,
    create_subject
)

from src.ai.study_plan_service import (
    build_syllabus_analysis_from_database,
    generate_subject_study_plan
)


def create_test_subject():

    initialize_database()

    student_id = create_student(
        "Study Plan UI Test"
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
            "Data Preprocessing",
            "Unit 1",
            "HIGH",
            40,
            "WEAK"
        )
    )

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
            "Classification",
            "Unit 2",
            "MEDIUM",
            70,
            "AVERAGE"
        )
    )

    connection.commit()
    connection.close()

    return subject_id


def test_build_analysis_from_database():

    subject_id = create_test_subject()

    analysis = (
        build_syllabus_analysis_from_database(
            subject_id=subject_id,
            subject_name="Data Mining"
        )
    )

    assert analysis.subject == "Data Mining"

    assert len(analysis.topics) >= 2

    assert (
        analysis.topics[0].estimated_minutes
        > 0
    )


def test_generate_subject_study_plan():

    subject_id = create_test_subject()

    plan = generate_subject_study_plan(

        subject_id=subject_id,

        subject_name="Data Mining",

        exam_date="2026-09-15",

        daily_hours=2
    )

    assert plan is not None

    assert plan.subject == "Data Mining"

    assert len(plan.sessions) > 0

    assert plan.total_minutes > 0