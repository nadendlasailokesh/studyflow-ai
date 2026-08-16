# ============================================================
# LEARNING SESSION CONTEXT
# ============================================================


CONTEXT_KEY = "learning_context"


# ============================================================
# SET CONTEXT
# ============================================================

def set_learning_context(
    session_state,
    topic_id,
    topic_name,
    subject_id=None,
    subject_name=None,
    action=None,
    source="manual",
):
    """
    Store the current learning topic context.

    This context allows the Progress, Learn, and Quiz
    pages to share the same learning target.
    """

    if topic_id is None:
        raise ValueError(
            "topic_id is required."
        )

    if not topic_name:
        raise ValueError(
            "topic_name is required."
        )

    session_state[CONTEXT_KEY] = {
        "topic_id": topic_id,
        "topic_name": str(topic_name),
        "subject_id": subject_id,
        "subject_name": subject_name,
        "action": action,
        "source": source,
    }


# ============================================================
# GET CONTEXT
# ============================================================

def get_learning_context(session_state):
    """
    Return the current learning context.

    Returns None when no learning context exists.
    """

    context = session_state.get(
        CONTEXT_KEY
    )

    if not context:
        return None

    return dict(context)


# ============================================================
# CHECK CONTEXT
# ============================================================

def has_learning_context(session_state):
    """
    Check whether a learning context is available.
    """

    return (
        get_learning_context(session_state)
        is not None
    )


# ============================================================
# CLEAR CONTEXT
# ============================================================

def clear_learning_context(session_state):
    """
    Remove the current learning context.
    """

    session_state.pop(
        CONTEXT_KEY,
        None
    )


# ============================================================
# UPDATE CONTEXT
# ============================================================

def update_learning_context(
    session_state,
    **updates,
):
    """
    Update selected fields of an existing
    learning context.

    Raises:
        ValueError: if no context exists.
    """

    context = get_learning_context(
        session_state
    )

    if context is None:
        raise ValueError(
            "No learning context exists."
        )

    allowed_fields = {
        "topic_id",
        "topic_name",
        "subject_id",
        "subject_name",
        "action",
        "source",
    }

    for key, value in updates.items():

        if key in allowed_fields:
            context[key] = value

    session_state[CONTEXT_KEY] = context