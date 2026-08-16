import pytest

from src.database.db import initialize_database
from src.database.repository import (
    create_student,
    get_student,
    update_student,
)


@pytest.fixture(autouse=True)
def setup_database():
    initialize_database()


def test_update_student_name():

    student_id = create_student(
        name="Test Student",
        knowledge_level="Beginner"
    )

    updated = update_student(
        student_id=student_id,
        name="Updated Student"
    )

    assert updated is not None
    assert updated["name"] == "Updated Student"
    assert updated["knowledge_level"] == "Beginner"


def test_update_student_knowledge_level():

    student_id = create_student(
        name="Test Student",
        knowledge_level="Beginner"
    )

    updated = update_student(
        student_id=student_id,
        knowledge_level="Advanced"
    )

    assert updated is not None
    assert updated["name"] == "Test Student"
    assert updated["knowledge_level"] == "Advanced"


def test_update_student_preserves_unspecified_fields():

    student_id = create_student(
        name="Test Student",
        knowledge_level="Intermediate"
    )

    updated = update_student(
        student_id=student_id,
        name="New Name"
    )

    assert updated["name"] == "New Name"
    assert updated["knowledge_level"] == "Intermediate"


def test_update_student_invalid_name():

    student_id = create_student(
        name="Test Student",
        knowledge_level="Beginner"
    )

    with pytest.raises(ValueError):

        update_student(
            student_id=student_id,
            name="   "
        )


def test_update_student_invalid_knowledge_level():

    student_id = create_student(
        name="Test Student",
        knowledge_level="Beginner"
    )

    with pytest.raises(ValueError):

        update_student(
            student_id=student_id,
            knowledge_level="Expert"
        )


def test_update_nonexistent_student():

    result = update_student(
        student_id=999999,
        name="Nobody"
    )

    assert result is None


def test_get_updated_student():

    student_id = create_student(
        name="Original",
        knowledge_level="Beginner"
    )

    update_student(
        student_id=student_id,
        name="Updated",
        knowledge_level="Advanced"
    )

    student = get_student(
        student_id
    )

    assert student["name"] == "Updated"
    assert student["knowledge_level"] == "Advanced"