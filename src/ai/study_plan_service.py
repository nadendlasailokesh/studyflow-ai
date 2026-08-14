from src.ai.study_plan import (
    generate_personalized_plan
)

from src.ai.syllabus_schema import (
    SyllabusAnalysis,
    TopicAnalysis
)

from src.database.dashboard import (
    get_subject_topics
)


def priority_to_minutes(priority):
    """
    Convert topic priority into an estimated
    study duration.

    These are temporary defaults until the
    AI-generated estimated_minutes value is
    stored in the database.
    """

    if not priority:
        return 45

    priority = priority.upper()

    if priority == "HIGH":
        return 60

    if priority == "MEDIUM":
        return 45

    if priority == "LOW":
        return 30

    return 45


def build_syllabus_analysis_from_database(
    subject_id,
    subject_name
):
    """
    Convert database topics into the
    SyllabusAnalysis structure expected
    by the existing study-plan engine.
    """

    database_topics = get_subject_topics(
        subject_id
    )

    topics = []

    for item in database_topics:

        priority = (
            item["priority"]
            or "MEDIUM"
        )

        estimated_minutes = (
            priority_to_minutes(
                priority
            )
        )

        topics.append(
            TopicAnalysis(

                topic=item["name"],

                unit=(
                    item["unit"]
                    or "Unknown Unit"
                ),

                priority=priority,

                reason=(
                    "Topic selected from the "
                    "student's syllabus."
                ),

                estimated_minutes=(
                    estimated_minutes
                ),

                prerequisites=[]
            )
        )

    return SyllabusAnalysis(

        subject=subject_name,

        overview=(
            f"Study plan generated for "
            f"{subject_name}."
        ),

        topics=topics
    )


def generate_subject_study_plan(
    subject_id,
    subject_name,
    exam_date,
    daily_hours
):
    """
    Generate a personalized study plan
    for a database subject.
    """

    analysis = (
        build_syllabus_analysis_from_database(
            subject_id=subject_id,
            subject_name=subject_name
        )
    )

    if not analysis.topics:
        return None

    return generate_personalized_plan(

        analysis=analysis,

        exam_date=exam_date,

        daily_hours=daily_hours
    )