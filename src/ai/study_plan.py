from datetime import date, timedelta

from src.ai.ranking import rank_topics
from src.ai.syllabus_schema import SyllabusAnalysis
from src.ai.study_plan_schema import (
    PersonalizedStudyPlan,
    StudySession
)


def generate_personalized_plan(
    analysis: SyllabusAnalysis,
    exam_date: str,
    daily_hours: float
):

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

    daily_minutes = int(
        daily_hours * 60
    )

    ranked_topics = rank_topics(
        analysis
    )

    sessions = []

    current_date = today

    remaining_minutes = daily_minutes

    for item in ranked_topics:

        topic = item["topic"]

        topic_minutes = (
            topic.estimated_minutes
        )

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

                    activity=(
                        f"Study {topic.topic} "
                        "and practice the concept."
                    ),

                    duration_minutes=session_minutes
                )
            )

            topic_minutes -= (
                session_minutes
            )

            remaining_minutes -= (
                session_minutes
            )

    total_minutes = sum(
        session.duration_minutes
        for session in sessions
    )

    return PersonalizedStudyPlan(

        subject=analysis.subject,

        exam_date=exam_date,

        total_days=total_days,

        total_minutes=total_minutes,

        sessions=sessions
    )