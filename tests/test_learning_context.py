from src.ai.learning_context import (
    set_learning_context,
    get_learning_context,
    has_learning_context,
    clear_learning_context,
    update_learning_context,
)


def test_set_and_get_learning_context():

    session_state = {}

    set_learning_context(
        session_state=session_state,
        topic_id=10,
        topic_name="Morphology",
        subject_id=1,
        subject_name="Computer Linguistics",
        action="RELEARN",
        source="recommendation",
    )

    context = get_learning_context(
        session_state
    )

    assert context is not None

    assert context["topic_id"] == 10
    assert context["topic_name"] == "Morphology"
    assert context["subject_id"] == 1
    assert context["subject_name"] == "Computer Linguistics"
    assert context["action"] == "RELEARN"
    assert context["source"] == "recommendation"


def test_has_learning_context():

    session_state = {}

    assert not has_learning_context(
        session_state
    )

    set_learning_context(
        session_state,
        topic_id=5,
        topic_name="Regular Expressions",
    )

    assert has_learning_context(
        session_state
    )


def test_clear_learning_context():

    session_state = {}

    set_learning_context(
        session_state,
        topic_id=5,
        topic_name="Regular Expressions",
    )

    assert has_learning_context(
        session_state
    )

    clear_learning_context(
        session_state
    )

    assert not has_learning_context(
        session_state
    )

    assert get_learning_context(
        session_state
    ) is None


def test_update_learning_context():

    session_state = {}

    set_learning_context(
        session_state,
        topic_id=5,
        topic_name="Regular Expressions",
        action="RELEARN",
    )

    update_learning_context(
        session_state,
        action="REVISE",
        source="quiz",
    )

    context = get_learning_context(
        session_state
    )

    assert context["topic_id"] == 5
    assert context["topic_name"] == "Regular Expressions"
    assert context["action"] == "REVISE"
    assert context["source"] == "quiz"


def test_context_is_copied_on_get():

    session_state = {}

    set_learning_context(
        session_state,
        topic_id=5,
        topic_name="Regular Expressions",
    )

    context = get_learning_context(
        session_state
    )

    context["topic_name"] = "Changed"

    stored = get_learning_context(
        session_state
    )

    assert stored["topic_name"] == "Regular Expressions"


def test_invalid_context():

    session_state = {}

    try:

        set_learning_context(
            session_state,
            topic_id=None,
            topic_name="Morphology",
        )

        assert False

    except ValueError as error:

        assert str(error) == (
            "topic_id is required."
        )


def test_update_without_context():

    session_state = {}

    try:

        update_learning_context(
            session_state,
            action="REVISE",
        )

        assert False

    except ValueError as error:

        assert str(error) == (
            "No learning context exists."
        )