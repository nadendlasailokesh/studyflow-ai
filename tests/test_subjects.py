from src.database.db import initialize_database
from src.database.subjects import (
    create_student,
    create_subject,
    get_subjects,
    update_subject,
    delete_subject
)


def test_subject_management():

    initialize_database()

    student_id = create_student(
        "UI Test Student"
    )

    subject_id = create_subject(
        student_id=student_id,
        name="Data Mining",
        exam_date="2026-09-15",
        daily_hours=2,
        goal="Prepare for examination"
    )

    subjects = get_subjects(
        student_id
    )

    assert any(
        subject["id"] == subject_id
        for subject in subjects
    )

    updated = update_subject(
        subject_id=subject_id,
        name="Advanced Data Mining",
        exam_date="2026-09-20",
        daily_hours=3,
        goal="Score well"
    )

    assert updated == 1

    deleted = delete_subject(
        subject_id
    )

    assert deleted == 1