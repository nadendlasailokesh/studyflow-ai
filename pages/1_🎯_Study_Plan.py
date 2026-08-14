import streamlit as st
from datetime import date

from src.database.db import initialize_database
from src.database.repository import (
    get_subjects,
    get_topics,
    create_task,
    mark_task_completed
)

from src.ai.syllabus_schema import (
    SyllabusAnalysis,
    TopicAnalysis
)

from src.ai.study_plan import (
    generate_personalized_plan
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

# ============================================================
# GET STUDENT
# ============================================================

student_id = st.session_state.get("student_id")

if not student_id:

    # Try to recover the existing default student
    from src.database.repository import (
        get_student,
        create_student
    )

    student = get_student(1)

    if student:

        student_id = student["id"]

    else:

        student_id = create_student(
            name="Student",
            knowledge_level="Beginner"
        )

    st.session_state.student_id = student_id


# ============================================================
# LOAD SUBJECTS
# ============================================================

subjects = get_subjects(student_id)

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

current_subject_id = st.session_state.get(
    "selected_subject_id"
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

st.subheader("📚 Subject")

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


# Update selected subject if changed

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

exam_date = selected_subject["exam_date"]

daily_hours = float(
    selected_subject["daily_hours"] or 2
)

goal = (
    selected_subject["goal"]
    or "Prepare effectively for the examination."
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
# TOPIC SUMMARY
# ============================================================

st.divider()

st.subheader("📖 Syllabus Summary")


high_count = sum(
    1
    for topic in topics
    if str(topic["priority"]).upper() == "HIGH"
)

medium_count = sum(
    1
    for topic in topics
    if str(topic["priority"]).upper() == "MEDIUM"
)

low_count = sum(
    1
    for topic in topics
    if str(topic["priority"]).upper() == "LOW"
)


col1, col2, col3, col4 = st.columns(4)


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

st.subheader("✨ Generate Personalized Plan")

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

            priority = (
                str(topic["priority"])
                .upper()
            )

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
        # Build SyllabusAnalysis
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
            "🧠 Creating your personalized study plan..."
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

    st.subheader("📅 Your Personalized Study Plan")


    # ========================================================
    # PLAN METRICS
    # ========================================================

    total_hours = (
        plan.total_minutes / 60
    )


    col1, col2, col3 = st.columns(3)


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
        ).append(session)


    # ========================================================
    # DISPLAY DAILY PLAN
    # ========================================================

    for study_date, sessions in (
        sessions_by_date.items()
    ):

        try:

            readable_date = date.fromisoformat(
                study_date
            ).strftime(
                "%A, %d %B %Y"
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

                col1, col2, col3 = st.columns(
                    [5, 2, 1]
                )


                with col1:

                    st.markdown(
                        f"**📘 {session.topic}**"
                    )

                    if session.unit:

                        st.caption(
                            f"📚 {session.unit}"
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

    st.subheader("🧠 How to Use This Plan")

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
"""
    )