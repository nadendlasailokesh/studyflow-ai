# ============================================================
# REVISION INTEGRATION
# StudyFlow AI
# Phase 8.4 — Quiz → Revision Integration
# ============================================================

from src.database.revision import (
    record_revision,
)


# ============================================================
# UPDATE REVISION AFTER QUIZ
# ============================================================

def update_revision_after_quiz(
    topic_id,
    score_percentage,
):
    """
    Update the spaced-repetition schedule after
    a learner completes a quiz.

    The revision database service is responsible for:
        - revision streak
        - review interval
        - next review date
        - last reviewed date

    This function only connects the quiz result
    to that existing revision system.
    """

    if topic_id is None:

        raise ValueError(
            "topic_id is required."
        )

    score = float(
        score_percentage
    )

    score = max(
        0.0,
        min(score, 100.0)
    )

    return record_revision(

        topic_id=topic_id,

        score_percentage=score,
    )