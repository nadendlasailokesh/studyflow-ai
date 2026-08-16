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

from src.database.revision import (
    get_due_revisions,
    get_upcoming_revisions,
)


# ============================================================
# PRIORITY → STUDY TIME
# ============================================================

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


# ============================================================
# BUILD SYLLABUS ANALYSIS FROM DATABASE
# ============================================================

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


# ============================================================
# PHASE 8.5
# BUILD REVISION CONTEXT
# ============================================================

def build_revision_context(
    subject_id
):
    """
    Build revision information for the
    Study Plan engine.

    Returns:

        {
            "Topic Name": {
                "revision_type": "DUE",
                "next_review_date": "...",
                "revision_streak": 0,
                "review_interval_days": 1,
            }
        }

    Revision types:

        DUE
            Topic needs revision now.

        UPCOMING
            Topic is scheduled for revision
            within the upcoming revision window.
    """

    revision_context = {}


    # ========================================================
    # DUE REVISIONS
    # ========================================================

    due_revisions = get_due_revisions()


    for revision in due_revisions:

        if revision.get(
            "subject_id"
        ) != subject_id:

            continue


        topic_name = revision.get(
            "topic_name"
        )

        if not topic_name:

            continue


        revision_context[
            topic_name
        ] = {

            "revision_type":
                "DUE",

            "next_review_date":
                revision.get(
                    "next_review_date"
                ),

            "revision_streak":
                int(
                    revision.get(
                        "revision_streak",
                        0
                    )
                    or 0
                ),

            "review_interval_days":
                int(
                    revision.get(
                        "review_interval_days",
                        0
                    )
                    or 0
                ),
        }


    # ========================================================
    # UPCOMING REVISIONS
    # ========================================================
    #
    # Do not overwrite a DUE revision.
    #
    # A due revision is always more urgent.
    # ========================================================

    upcoming_revisions = (
        get_upcoming_revisions(
            days=7
        )
    )


    for revision in upcoming_revisions:

        if revision.get(
            "subject_id"
        ) != subject_id:

            continue


        topic_name = revision.get(
            "topic_name"
        )

        if not topic_name:

            continue


        if topic_name in revision_context:

            continue


        revision_context[
            topic_name
        ] = {

            "revision_type":
                "UPCOMING",

            "next_review_date":
                revision.get(
                    "next_review_date"
                ),

            "revision_streak":
                int(
                    revision.get(
                        "revision_streak",
                        0
                    )
                    or 0
                ),

            "review_interval_days":
                int(
                    revision.get(
                        "review_interval_days",
                        0
                    )
                    or 0
                ),
        }


    return revision_context


# ============================================================
# GENERATE SUBJECT STUDY PLAN
# ============================================================

def generate_subject_study_plan(
    subject_id,
    subject_name,
    exam_date,
    daily_hours
):
    """
    Generate a personalized study plan
    for a database subject.

    Phase 8.5:

    The plan now considers the existing
    spaced-repetition schedule.

    Due revisions are prioritized first.
    Upcoming revisions are prioritized next.
    Ordinary syllabus ranking remains the
    fallback ranking.
    """

    analysis = (
        build_syllabus_analysis_from_database(

            subject_id=subject_id,

            subject_name=subject_name
        )
    )


    if not analysis.topics:

        return None


    # ========================================================
    # BUILD REVISION CONTEXT
    # ========================================================

    revision_context = (
        build_revision_context(
            subject_id=subject_id
        )
    )


    # ========================================================
    # GENERATE REVISION-AWARE PLAN
    # ========================================================

    return generate_personalized_plan(

        analysis=analysis,

        exam_date=exam_date,

        daily_hours=daily_hours,

        revision_topics=revision_context
    )