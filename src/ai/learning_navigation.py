# ============================================================
# LEARNING NAVIGATION
# ============================================================

from src.ai.learning_context import (
    get_learning_context,
    clear_learning_context,
)


def get_recommended_learning_topic(session_state):
    """
    Return the topic that should be opened on the Learn page.

    Returns:
        dict | None
    """

    context = get_learning_context(session_state)

    if not context:
        return None

    return {
        "topic_id": context.get("topic_id"),
        "topic_name": context.get("topic_name"),
        "subject_id": context.get("subject_id"),
        "subject_name": context.get("subject_name"),
        "action": context.get("action"),
    }


def clear_recommended_learning_topic(session_state):
    """
    Clear the learning navigation context after it
    has been consumed by the Learn page.
    """

    clear_learning_context(session_state)