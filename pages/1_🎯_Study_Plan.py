import streamlit as st
from datetime import date

from src.database.db import initialize_database

from src.database.repository import (
    get_subjects,
    get_topics,
    create_task,
    mark_task_completed,
    get_student,
    get_student_by_name,
    create_student,
)

from src.ai.syllabus_schema import (
    SyllabusAnalysis,
    TopicAnalysis
)

from src.ai.study_plan import (
    generate_personalized_plan
)

from src.database.revision import (
    get_due_revisions,
    get_upcoming_revisions,
)

from src.ai.revision_scheduler import (
    get_revision_recommendation,
)


# ============================================================
# INITIALIZATION
# ============================================================

initialize_database()

st.set_page_config(
    page_title="Study Plan",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🎯 Your Study Plan")

st.write(
    "StudyFlow AI creates a personalized study plan "
    "based on your syllabus, priorities, exam date, "
    "and available study time."
)


# ============================================================
# STUDENT
# ============================================================

student_id = st.session_state.get(
    "student_id"
)

# ============================================================
# STUDENT RECOVERY
# ============================================================

if student_id:

    student = get_student(
        student_id
    )

    if not student:

        student_id = None
        st.session_state.student_id = None


# ============================================================
# RECOVER STUDENT BY NAME
# ============================================================

if not student_id:

    student_name = (
        st.session_state.get(
            "student_name",
            ""
        )
        or ""
    ).strip()

    if student_name:

        student = get_student_by_name(
            student_name
        )

        if student:

            student_id = student["id"]

            st.session_state.student_id = (
                student_id
            )

            st.session_state.student_name = (
                student["name"]
            )


# ============================================================
# FINAL FALLBACK
# ============================================================

if not student_id:

    student = get_student_by_name(
        "Student"
    )

    if student:

        student_id = student["id"]

    else:

        student_id = create_student(
            name="Student",
            knowledge_level="Beginner"
        )

    st.session_state.student_id = (
        student_id
    )

    if not st.session_state.get(
        "student_name"
    ):

        st.session_state.student_name = (
            "Student"
        )


# ============================================================
# LOAD SUBJECTS
# ============================================================

subjects = get_subjects(
    student_id
)


if not subjects:

    st.info(
        "No subjects found. Go to 📚 My Subjects "
        "and add a subject first."
    )

    st.stop()


# ============================================================
# SELECT SUBJECT
# ============================================================

subject_ids = [

    subject["id"]

    for subject in subjects
]


current_subject_id = (
    st.session_state.get(
        "selected_subject_id"
    )
)


if current_subject_id not in subject_ids:

    current_subject_id = subject_ids[0]

    st.session_state.selected_subject_id = (
        current_subject_id
    )


selected_subject = next(

    subject

    for subject in subjects

    if subject["id"] == current_subject_id

)


# ============================================================
# SUBJECT SELECTOR
# ============================================================

st.subheader(
    "📚 Subject"
)


subject_names = [

    subject["name"]

    for subject in subjects

]


current_index = subject_ids.index(
    current_subject_id
)


selected_name = st.selectbox(

    "Choose subject",

    subject_names,

    index=current_index

)


# ------------------------------------------------------------
# Update selected subject
# ------------------------------------------------------------

selected_subject = next(

    subject

    for subject in subjects

    if subject["name"] == selected_name

)


st.session_state.selected_subject_id = (
    selected_subject["id"]
)


# ============================================================
# SUBJECT INFORMATION
# ============================================================

exam_date = (
    selected_subject["exam_date"]
)


daily_hours = float(

    selected_subject["daily_hours"]
    or 2

)


goal = (

    selected_subject["goal"]

    or

    "Prepare effectively for the examination."

)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(

        "📚 Subject",

        selected_subject["name"]

    )


with col2:

    st.metric(

        "⏱️ Daily Study Time",

        f"{daily_hours:g} hrs"

    )


with col3:

    if exam_date:

        try:

            exam = date.fromisoformat(
                str(exam_date)
            )

            days_left = (
                exam - date.today()
            ).days


            if days_left > 0:

                st.metric(

                    "📅 Days Remaining",

                    days_left

                )

            elif days_left == 0:

                st.metric(

                    "📅 Exam",

                    "Today"

                )

            else:

                st.metric(

                    "📅 Exam",

                    "Passed"

                )

        except ValueError:

            st.metric(

                "📅 Exam Date",

                str(exam_date)

            )


st.caption(
    f"🎯 Goal: {goal}"
)


# ============================================================
# LOAD TOPICS
# ============================================================

topics = get_topics(
    selected_subject["id"]
)


if not topics:

    st.warning(
        "No topics are available for this subject."
    )

    st.info(
        "Go to 📚 My Subjects → Syllabus Analyzer "
        "and analyze your syllabus first."
    )

    st.stop()


# ============================================================
# PHASE 8.6 — REVISION DASHBOARD
# ============================================================

st.divider()

st.subheader(
    "🔁 Revision Schedule"
)

st.write(
    "StudyFlow AI automatically schedules revisions "
    "based on your quiz performance and revision history."
)


# ============================================================
# LOAD REVISION DATA
# ============================================================

try:

    all_due_revisions = (
        get_due_revisions()
    )

    all_upcoming_revisions = (
        get_upcoming_revisions(
            days=7
        )
    )

except Exception as error:

    st.error(
        "Unable to load the revision schedule."
    )

    st.exception(error)

    all_due_revisions = []

    all_upcoming_revisions = []


# ============================================================
# FILTER REVISIONS BY SUBJECT
# ============================================================

subject_id = selected_subject["id"]


due_revisions = [

    revision

    for revision in all_due_revisions

    if revision.get(
        "subject_id"
    ) == subject_id

]


# ------------------------------------------------------------
# Topic IDs that are already due
#
# We exclude these from Upcoming so the same topic
# does not appear in both sections.
# ------------------------------------------------------------

due_topic_ids = {

    revision.get(
        "topic_id"
    )

    for revision in due_revisions

}


upcoming_revisions = [

    revision

    for revision in all_upcoming_revisions

    if (

        revision.get(
            "subject_id"
        ) == subject_id

        and

        revision.get(
            "topic_id"
        ) not in due_topic_ids

    )

]


# ============================================================
# REVISION SUMMARY
# ============================================================

revision_col1, revision_col2, revision_col3 = (
    st.columns(3)
)


with revision_col1:

    st.metric(
        "🔴 Due Now",
        len(due_revisions)
    )


with revision_col2:

    st.metric(
        "📅 Upcoming",
        len(upcoming_revisions)
    )


with revision_col3:

    total_revision_topics = (
        len(due_revisions)
        +
        len(upcoming_revisions)
    )

    st.metric(
        "📚 Scheduled Topics",
        total_revision_topics
    )


# ============================================================
# REVISION NAVIGATION HELPER
# ============================================================

def open_revision_topic(
    revision
):
    """
    Send the selected revision topic to
    the existing Learn page.
    """

    topic_id = revision.get(
        "topic_id"
    )

    topic_name = revision.get(
        "topic_name",
        ""
    )

    revision_subject_id = revision.get(
        "subject_id"
    )


    # --------------------------------------------------------
    # Validate topic
    # --------------------------------------------------------

    if topic_id is None:

        st.error(
            "Unable to start revision because "
            "the topic ID is missing."
        )

        return


    # --------------------------------------------------------
    # Validate subject
    # --------------------------------------------------------

    if revision_subject_id is None:

        st.error(
            "Unable to start revision because "
            "the subject ID is missing."
        )

        return


    # --------------------------------------------------------
    # Store learning transition context
    # --------------------------------------------------------

    st.session_state[
        "learning_transition_context"
    ] = {

        "subject_id":
            revision_subject_id,

        "subject_name":
            selected_subject["name"],

        "topic_id":
            topic_id,

        "topic_name":
            topic_name,

    }


    # --------------------------------------------------------
    # Store direct learning context
    # --------------------------------------------------------

    st.session_state[
        "selected_subject_id"
    ] = revision_subject_id


    st.session_state[
        "selected_subject_name"
    ] = selected_subject["name"]


    st.session_state[
        "selected_topic_id"
    ] = topic_id


    st.session_state[
        "selected_topic_name"
    ] = topic_name


    # --------------------------------------------------------
    # Mark that this navigation came from revision
    # --------------------------------------------------------

    st.session_state[
        "revision_mode"
    ] = True


    # --------------------------------------------------------
    # Navigate to Learn
    # --------------------------------------------------------

    st.switch_page(
        "pages/2_📖_Learn.py"
    )


# ============================================================
# DUE REVISIONS
# ============================================================

st.markdown(
    "### 🔴 Revisions Due"
)


if not due_revisions:

    st.success(
        "🎉 No revisions are due right now!"
    )

else:

    st.warning(
        f"You have **{len(due_revisions)}** "
        "topic(s) that should be revised."
    )


    for revision in due_revisions:

        topic_id = revision.get(
            "topic_id"
        )

        topic_name = revision.get(
            "topic_name",
            "Unknown Topic"
        )

        mastery = float(

            revision.get(
                "mastery",
                0
            )

            or 0

        )

        status = (

            revision.get(
                "status"
            )

            or

            "Not Started"

        )

        priority = (

            revision.get(
                "priority"
            )

            or

            "MEDIUM"

        )


        streak = int(

            revision.get(
                "revision_streak",
                0
            )

            or 0

        )


        interval = int(

            revision.get(
                "review_interval_days",
                0
            )

            or 0

        )


        next_review = (

            revision.get(
                "next_review_date"
            )

            or

            "Today"

        )


        # ----------------------------------------------------
        # Revision recommendation
        # ----------------------------------------------------

        recommendation = (
            get_revision_recommendation(

                score_percentage=mastery,

                revision_streak=streak

            )
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"#### 🔴 {topic_name}"
            )


            st.caption(

                f"{revision.get('unit', 'General')} "
                f"• Priority: {priority} "
                f"• Status: {status}"

            )


            col1, col2, col3, col4 = (
                st.columns(4)
            )


            with col1:

                st.metric(

                    "Mastery",

                    f"{mastery:.0f}%"

                )


            with col2:

                st.metric(

                    "Revision Streak",

                    streak

                )


            with col3:

                st.metric(

                    "Interval",

                    f"{interval} day(s)"

                )


            with col4:

                st.metric(

                    "Next Review",

                    next_review

                )


            # ------------------------------------------------
            # Urgency
            # ------------------------------------------------

            urgency = (
                recommendation.get(
                    "urgency",
                    "HIGH"
                )
            )


            if urgency == "HIGH":

                st.error(
                    f"🚨 {recommendation['reason']}"
                )

            elif urgency == "MEDIUM":

                st.warning(
                    f"⚠️ {recommendation['reason']}"
                )

            else:

                st.info(
                    f"ℹ️ {recommendation['reason']}"
                )


            # ------------------------------------------------
            # Revise button
            # ------------------------------------------------

            if st.button(

                "📖 Revise Now",

                key=(
                    f"revise_due_"
                    f"{topic_id}"
                ),

                type="primary",

                use_container_width=True

            ):

                open_revision_topic(
                    revision
                )


# ============================================================
# UPCOMING REVISIONS
# ============================================================

st.markdown(
    "### 📅 Upcoming Revisions"
)


if not upcoming_revisions:

    st.info(
        "No revisions are scheduled within "
        "the next 7 days."
    )

else:

    for revision in upcoming_revisions:

        topic_id = revision.get(
            "topic_id"
        )

        topic_name = revision.get(
            "topic_name",
            "Unknown Topic"
        )


        mastery = float(

            revision.get(
                "mastery",
                0
            )

            or 0

        )


        status = (

            revision.get(
                "status"
            )

            or

            "Not Started"

        )


        priority = (

            revision.get(
                "priority"
            )

            or

            "MEDIUM"

        )


        streak = int(

            revision.get(
                "revision_streak",
                0
            )

            or 0

        )


        interval = int(

            revision.get(
                "review_interval_days",
                0
            )

            or 0

        )


        next_review = (

            revision.get(
                "next_review_date"
            )

            or

            "Not scheduled"

        )


        with st.container(
            border=True
        ):

            col1, col2 = st.columns(
                [4, 1]
            )


            with col1:

                st.markdown(
                    f"#### 📚 {topic_name}"
                )


                st.caption(

                    f"{revision.get('unit', 'General')} "
                    f"• Priority: {priority} "
                    f"• Status: {status}"

                )


                st.write(
                    f"🎯 Mastery: **{mastery:.0f}%**"
                )


                st.write(
                    f"🔁 Revision streak: "
                    f"**{streak}**"
                )


                st.write(
                    f"⏱️ Current interval: "
                    f"**{interval} day(s)**"
                )


                st.write(
                    f"📅 Next review: "
                    f"**{next_review}**"
                )


            with col2:

                st.write("")


                if st.button(

                    "📖 Revise",

                    key=(
                        f"revise_upcoming_"
                        f"{topic_id}"
                    ),

                    use_container_width=True

                ):

                    open_revision_topic(
                        revision
                    )


# ============================================================
# REVISION SYSTEM INFORMATION
# ============================================================

with st.expander(
    "ℹ️ How does revision scheduling work?"
):

    st.write(
        """
StudyFlow AI uses your quiz performance to determine
when you should review a topic again.

**Performance-based intervals:**

• Below 50% → revise in 1 day  
• 50–69% → revise in 2 days  
• 70–79% → revise in 4 days  
• 80–89% → revise in 7 days  
• 90%+ → revise in 14 days  

Successful strong revisions can gradually extend
the interval, up to a maximum of 30 days.

If your performance drops below 80%, the revision
streak is reset so that the topic receives more
frequent review.
"""
    )


# ============================================================
# TOPIC SUMMARY
# ============================================================

st.divider()

st.subheader(
    "📖 Syllabus Summary"
)


high_count = sum(

    1

    for topic in topics

    if str(
        topic["priority"]
    ).upper() == "HIGH"

)


medium_count = sum(

    1

    for topic in topics

    if str(
        topic["priority"]
    ).upper() == "MEDIUM"

)


low_count = sum(

    1

    for topic in topics

    if str(
        topic["priority"]
    ).upper() == "LOW"

)


col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    st.metric(
        "📚 Total Topics",
        len(topics)
    )


with col2:

    st.metric(
        "🔥 High Priority",
        high_count
    )


with col3:

    st.metric(
        "🟡 Medium Priority",
        medium_count
    )


with col4:

    st.metric(
        "🟢 Low Priority",
        low_count
    )


# ============================================================
# GENERATE PLAN
# ============================================================

st.divider()

st.subheader(
    "✨ Generate Personalized Plan"
)


st.write(
    "StudyFlow AI will prioritize your topics and "
    "divide them across the available study days."
)


if st.button(

    "✨ Generate My Study Plan",

    type="primary",

    use_container_width=True

):

    if not exam_date:

        st.error(
            "Please set an exam date for this subject."
        )

        st.stop()


    try:

        # ----------------------------------------------------
        # Convert database topics into AI schema
        # ----------------------------------------------------

        topic_analysis_list = []


        for topic in topics:

            priority = str(
                topic["priority"]
            ).upper()


            if priority not in {

                "HIGH",
                "MEDIUM",
                "LOW"

            }:

                priority = "MEDIUM"


            topic_analysis_list.append(

                TopicAnalysis(

                    topic=topic["name"],

                    unit=(
                        topic["unit"]
                        or ""
                    ),

                    priority=priority,

                    reason=(
                        "Priority assigned "
                        "during syllabus analysis."
                    ),

                    estimated_minutes=60,

                    prerequisites=[]

                )

            )


        # ----------------------------------------------------
        # Build syllabus analysis
        # ----------------------------------------------------

        analysis = SyllabusAnalysis(

            subject=selected_subject["name"],

            overview=(
                f"{len(topics)} topics identified "
                "for examination preparation."
            ),

            topics=topic_analysis_list

        )


        # ----------------------------------------------------
        # Generate plan
        # ----------------------------------------------------

        with st.spinner(

            "🧠 Creating your personalized "
            "study plan..."

        ):

            plan = generate_personalized_plan(

                analysis=analysis,

                exam_date=str(exam_date),

                daily_hours=daily_hours

            )


        st.session_state[
            "study_plan"
        ] = plan


        st.success(

            "✅ Your personalized study plan "
            "has been generated!"

        )


        st.rerun()


    except Exception as error:

        st.error(
            "❌ Unable to generate the study plan."
        )

        st.exception(error)


# ============================================================
# DISPLAY PLAN
# ============================================================

plan = st.session_state.get(
    "study_plan"
)


if plan:

    st.divider()

    st.subheader(
        "📅 Your Personalized Study Plan"
    )


    # ========================================================
    # PLAN METRICS
    # ========================================================

    total_hours = (
        plan.total_minutes / 60
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "📅 Study Days",
            plan.total_days
        )


    with col2:

        st.metric(
            "⏱️ Total Study Time",
            f"{total_hours:.1f} hrs"
        )


    with col3:

        st.metric(
            "📋 Study Sessions",
            len(plan.sessions)
        )


    # ========================================================
    # GROUP SESSIONS BY DATE
    # ========================================================

    sessions_by_date = {}


    for session in plan.sessions:

        sessions_by_date.setdefault(

            session.date,

            []

        ).append(
            session
        )


    # ========================================================
    # DISPLAY DAILY PLAN
    # ========================================================

    for study_date, sessions in (
        sessions_by_date.items()
    ):

        try:

            readable_date = (
                date.fromisoformat(
                    study_date
                ).strftime(
                    "%A, %d %B %Y"
                )
            )

        except ValueError:

            readable_date = study_date


        st.markdown(
            f"### 📅 {readable_date}"
        )


        daily_total = sum(

            session.duration_minutes

            for session in sessions

        )


        st.caption(

            f"⏱️ Total study time: "
            f"{daily_total} minutes"

        )


        for index, session in enumerate(
            sessions
        ):

            with st.container(
                border=True
            ):

                col1, col2, col3 = (
                    st.columns(
                        [5, 2, 1]
                    )
                )


                with col1:

                    st.markdown(

                        f"**📘 "
                        f"{session.topic}**"

                    )


                    if session.unit:

                        st.caption(

                            f"📚 "
                            f"{session.unit}"

                        )


                    st.write(
                        session.activity
                    )


                with col2:

                    st.write(

                        f"⏱️ "
                        f"**{session.duration_minutes} min**"

                    )


                with col3:

                    st.checkbox(

                        "Done",

                        key=(

                            f"plan_done_"
                            f"{study_date}_"
                            f"{index}"

                        )

                    )


    # ========================================================
    # STUDY PLAN NOTES
    # ========================================================

    st.divider()

    st.subheader(
        "🧠 How to Use This Plan"
    )


    st.info(
        """
**1. Learn first 📖**  
Understand the concept before trying to memorize it.

**2. Practice 📝**  
Solve examples, write short answers, or explain the concept.

**3. Revise 🔄**  
Review difficult topics again later.

**4. Track completion ✅**  
Mark a session complete after finishing it.

**5. Focus on HIGH priority topics 🔥**  
These should receive more attention before the exam.

**6. Follow your revision schedule 🔁**  
StudyFlow AI automatically determines when previously
studied topics should be reviewed based on your performance.
"""
    )