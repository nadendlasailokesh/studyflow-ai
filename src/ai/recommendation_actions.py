# ============================================================
# RECOMMENDATION ACTIONS
# ============================================================


RELEARN = "RELEARN"
REVISE = "REVISE"
MOVE_FORWARD = "MOVE_FORWARD"
CONTINUE = "CONTINUE"


def get_recommendation_action(action):
    """
    Normalize an AI recommendation action.

    Returns one of the supported recommendation actions.
    """

    if not action:
        return CONTINUE

    normalized = str(action).strip().upper()

    if normalized in {
        RELEARN,
        REVISE,
        MOVE_FORWARD,
        CONTINUE,
    }:
        return normalized

    return CONTINUE


def should_open_learning(action):
    """
    Determine whether the recommendation should
    direct the student toward learning material.
    """

    action = get_recommendation_action(action)

    return action in {
        RELEARN,
        REVISE,
        CONTINUE,
    }


def should_open_quiz(action):
    """
    Determine whether the recommendation should
    direct the student toward a practice quiz.
    """

    action = get_recommendation_action(action)

    return action in {
        RELEARN,
        REVISE,
    }


def get_action_label(action):
    """
    Return a user-friendly label for the recommended action.
    """

    action = get_recommendation_action(action)

    labels = {
        RELEARN: "📖 Learn This Topic",
        REVISE: "🔄 Review This Topic",
        MOVE_FORWARD: "🚀 Move Forward",
        CONTINUE: "📚 Continue Studying",
    }

    return labels[action]