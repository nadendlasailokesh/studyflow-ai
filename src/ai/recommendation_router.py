# ============================================================
# RECOMMENDATION ROUTER
# ============================================================


def set_recommended_topic(
    session_state,
    topic_id,
    topic_name,
    action,
):
    """
    Store the AI-recommended topic in Streamlit session state.
    """

    session_state["recommended_topic_id"] = topic_id
    session_state["recommended_topic_name"] = topic_name
    session_state["recommended_action"] = action


def get_recommended_topic(session_state):
    """
    Retrieve the currently recommended topic.
    """

    topic_id = session_state.get(
        "recommended_topic_id"
    )

    topic_name = session_state.get(
        "recommended_topic_name"
    )

    action = session_state.get(
        "recommended_action"
    )

    if topic_id is None and not topic_name:
        return None

    return {
        "topic_id": topic_id,
        "topic_name": topic_name,
        "action": action,
    }


def clear_recommended_topic(session_state):
    """
    Clear the recommendation context.
    """

    session_state.pop(
        "recommended_topic_id",
        None,
    )

    session_state.pop(
        "recommended_topic_name",
        None,
    )

    session_state.pop(
        "recommended_action",
        None,
    )