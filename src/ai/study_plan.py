from datetime import date, timedelta

from src.ai.ranking import rank_topics
from src.ai.syllabus_schema import SyllabusAnalysis
from src.ai.study_plan_schema import (
    PersonalizedStudyPlan,
    StudySession
)


# ============================================================
# GENERATE PERSONALIZED STUDY PLAN
# ============================================================

def generate_personalized_plan(
    analysis: SyllabusAnalysis,
    exam_date: str,
    daily_hours: float,
    revision_topics=None,
):
    """
    Generate a personalized study plan.

    Phase 8.5
    ----------
    Revision topics can be supplied through `revision_topics`.

    Expected structure:

        {
            "Topic Name": {
                "revision_type": "DUE",
                "next_review_date": "2026-08-15",
                "revision_streak": 2,
                "review_interval_days": 7,
            }
        }

    Revision topics are scheduled before ordinary topics
    according to their revision urgency.

    Existing callers that do not provide revision_topics
    continue to work exactly as before.
    """

    exam = date.fromisoformat(
        exam_date
    )

    today = date.today()

    total_days = (
        exam - today
    ).days

    if total_days <= 0:

        raise ValueError(
            "Exam date must be in the future."
        )


    # ========================================================
    # DAILY STUDY TIME
    # ========================================================

    daily_minutes = int(
        daily_hours * 60
    )

    if daily_minutes <= 0:

        raise ValueError(
            "daily_hours must be greater than zero."
        )


    # ========================================================
    # NORMALIZE REVISION TOPICS
    # ========================================================

    revision_topics = (
        revision_topics
        or {}
    )


    # ========================================================
    # RANK SYLLABUS TOPICS
    # ========================================================

    ranked_topics = rank_topics(
        analysis
    )


    # ========================================================
    # PHASE 8.5
    # REVISION-AWARE RANKING
    # ========================================================
    #
    # Priority:
    #
    # 1. Due revisions
    # 2. Upcoming revisions
    # 3. Existing adaptive/syllabus ranking
    #
    # The original rank is retained as the secondary key.
    # ========================================================

    ranked_with_index = []

    for index, item in enumerate(
        ranked_topics
    ):

        topic = item[
            "topic"
        ]

        revision_info = (
            revision_topics.get(
                topic.topic,
                {}
            )
            or {}
        )

        revision_type = (
            revision_info.get(
                "revision_type"
            )
            or ""
        ).upper()


        # ----------------------------------------------------
        # Revision priority
        # ----------------------------------------------------

        if revision_type == "DUE":

            revision_priority = 0

        elif revision_type == "UPCOMING":

            revision_priority = 1

        else:

            revision_priority = 2


        ranked_with_index.append(
            (
                revision_priority,
                index,
                item,
                revision_info
            )
        )


    ranked_with_index.sort(
        key=lambda value: (
            value[0],
            value[1]
        )
    )


    # ========================================================
    # BUILD SESSIONS
    # ========================================================

    sessions = []

    current_date = today

    remaining_minutes = daily_minutes


    for (
        revision_priority,
        original_index,
        item,
        revision_info
    ) in ranked_with_index:

        topic = item[
            "topic"
        ]

        topic_minutes = (
            topic.estimated_minutes
        )


        # ----------------------------------------------------
        # Determine activity type
        # ----------------------------------------------------

        revision_type = (
            revision_info.get(
                "revision_type"
            )
            or ""
        ).upper()


        if revision_type == "DUE":

            activity_template = (
                f"Revise {topic.topic} "
                "and practice the weak concepts."
            )

        elif revision_type == "UPCOMING":

            activity_template = (
                f"Review {topic.topic} "
                "to strengthen retention."
            )

        else:

            activity_template = (
                f"Study {topic.topic} "
                "and practice the concept."
            )


        # ----------------------------------------------------
        # Schedule topic
        # ----------------------------------------------------

        while topic_minutes > 0:

            if current_date >= exam:

                break


            if remaining_minutes <= 0:

                current_date += timedelta(
                    days=1
                )

                remaining_minutes = (
                    daily_minutes
                )


            session_minutes = min(
                topic_minutes,
                remaining_minutes
            )


            sessions.append(
                StudySession(

                    date=current_date.isoformat(),

                    topic=topic.topic,

                    unit=topic.unit,

                    activity=activity_template,

                    duration_minutes=session_minutes
                )
            )


            topic_minutes -= (
                session_minutes
            )

            remaining_minutes -= (
                session_minutes
            )


    # ========================================================
    # TOTAL STUDY TIME
    # ========================================================

    total_minutes = sum(

        session.duration_minutes

        for session in sessions
    )


    # ========================================================
    # RETURN PLAN
    # ========================================================

    return PersonalizedStudyPlan(

        subject=analysis.subject,

        exam_date=exam_date,

        total_days=total_days,

        total_minutes=total_minutes,

        sessions=sessions
    )