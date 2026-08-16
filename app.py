import streamlit as st
from datetime import date
from src.ai.tutor import ask_tutor

from src.database.db import initialize_database
from src.database.subjects import (
    create_student,
    create_subject,
    get_subjects,
    update_subject,
    delete_subject,
)

from src.database.repository import (
    get_student_by_name,
)

from src.database.dashboard import (
    get_subject_topics,
    get_topic_statistics,
    get_latest_quiz_attempt
)

from src.ai.recommendation import (
    get_top_recommendation,
    build_topic_recommendations,
)

from src.ai.study_plan_service import (
    generate_subject_study_plan
)

from src.ai.learning import (
    generate_learning_content
)

# ============================================================
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StudyFlow AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "student_id" not in st.session_state:
    st.session_state.student_id = None

if "student_name" not in st.session_state:
    st.session_state.student_name = ""

if "selected_subject_id" not in st.session_state:
    st.session_state.selected_subject_id = None

if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_subjects():

    if st.session_state.student_id is None:
        return []

    return get_subjects(
        st.session_state.student_id
    )


def get_selected_subject():

    subjects = load_subjects()

    for subject in subjects:

        if (
            subject["id"]
            == st.session_state.selected_subject_id
        ):
            return subject

    return None


def calculate_days_until_exam(exam_date):

    if not exam_date:
        return None

    try:

        exam = date.fromisoformat(
            exam_date
        )

        return max(
            (exam - date.today()).days,
            0
        )

    except ValueError:

        return None


def navigate(page):

    st.session_state.page = page

    st.rerun()


# ============================================================
# HEADER / SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📚 StudyFlow AI")

    st.caption(
        "Your AI Learning Companion"
    )

    st.divider()

    # --------------------------------------------------------
    # Student
    # --------------------------------------------------------

    # --------------------------------------------------------
# Student
# --------------------------------------------------------

st.subheader("👤 Student")

entered_name = st.text_input(
    "Your name",
    value=st.session_state.student_name,
    placeholder="Enter your name",
)

if entered_name.strip():

    normalized_name = entered_name.strip()

    # Check whether the entered name is different
    # from the currently loaded student
    if (
        normalized_name.lower()
        != st.session_state.student_name.strip().lower()
    ):

        # ------------------------------------------------
        # Search database
        # ------------------------------------------------

        existing_student = get_student_by_name(
            normalized_name
        )

        # ------------------------------------------------
        # Existing student
        # ------------------------------------------------

        if existing_student:

            st.session_state.student_id = (
                existing_student["id"]
            )

            st.session_state.student_name = (
                existing_student["name"]
            )

            st.success(
                f"Welcome back, "
                f"{existing_student['name']}! 👋"
            )

        # ------------------------------------------------
        # New student
        # ------------------------------------------------

        else:

            new_student_id = create_student(
                normalized_name
            )

            st.session_state.student_id = (
                new_student_id
            )

            st.session_state.student_name = (
                normalized_name
            )

            st.success(
                f"New student profile created "
                f"for {normalized_name}! 🎉"
            )
    st.divider()

    # --------------------------------------------------------
    # Navigation
    # --------------------------------------------------------

    st.subheader("🧭 Navigation")

    pages = [
        "🏠 Dashboard",
        "📚 Subjects",
        "🎯 What Should I Study?",
        "📅 Study Plan",
        "📖 Learn",
        "🤖 AI Tutor",
        "❓ Quiz",
        "📊 Progress",
    ]

    selected_page = st.radio(
        "Go to",
        pages,
        index=pages.index(
            st.session_state.page
        ),
    )

    st.session_state.page = selected_page

    st.divider()

    st.caption(
        "Study smarter. Learn better. 🚀"
    )


# ============================================================
# LOAD DATA
# ============================================================

subjects = load_subjects()

selected_subject = get_selected_subject()


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "🏠 Dashboard":

    if not st.session_state.student_name:

        st.title(
            "Welcome to StudyFlow AI! 👋"
        )

        st.write(
            """
            Your personalized AI-powered
            learning companion.
            """
        )

        st.info(
            "Enter your name in the sidebar "
            "to get started."
        )

    elif not subjects:

        st.title(
            f"Welcome back, "
            f"{st.session_state.student_name}! 👋"
        )

        st.write(
            "Let's set up your first subject."
        )

        if st.button(
            "➕ Add Your First Subject",
            use_container_width=True
        ):

            navigate("📚 Subjects")

    else:

        st.title(
            f"Welcome back, "
            f"{st.session_state.student_name}! 👋"
        )

        st.caption(
            "Your personalized learning dashboard"
        )

        # ====================================================
        # CURRENT SUBJECT
        # ====================================================

        st.subheader(
            "📚 Current Subject"
        )

        subject_names = [
            subject["name"]
            for subject in subjects
        ]

        selected_name = st.selectbox(
            "Choose a subject",
            subject_names,
            index=(
                subject_names.index(
                    selected_subject["name"]
                )
                if selected_subject
                and selected_subject["name"]
                in subject_names
                else 0
            )
        )

        for subject in subjects:

            if (
                subject["name"]
                == selected_name
            ):

                st.session_state.selected_subject_id = (
                    subject["id"]
                )

                selected_subject = subject

                break

        if selected_subject:

            subject_id = (
                selected_subject["id"]
            )

            # =================================================
            # DATABASE STATISTICS
            # =================================================

            stats = get_topic_statistics(
                subject_id
            )

            topics = get_subject_topics(
                subject_id
            )

            latest_quiz = (
                get_latest_quiz_attempt(
                    subject_id
                )
            )

            days = calculate_days_until_exam(
                selected_subject["exam_date"]
            )

            # =================================================
            # EXAM OVERVIEW
            # =================================================

            st.divider()

            st.subheader(
                "🎯 Exam Overview"
            )

            col1, col2, col3, col4 = (
                st.columns(4)
            )

            with col1:

                st.metric(
                    "📅 Days Until Exam",
                    days
                    if days is not None
                    else "—"
                )

            with col2:

                st.metric(
                    "📚 Topics",
                    stats["total_topics"]
                )

            with col3:

                st.metric(
                    "⏱ Daily Hours",
                    selected_subject[
                        "daily_hours"
                    ]
                    or "—"
                )

            with col4:

                st.metric(
                    "📊 Mastery",
                    f"{stats['average_mastery']:.0f}%"
                )

            # =================================================
            # TOPIC MASTERY
            # =================================================

            st.divider()

            st.subheader(
                "📊 Topic Mastery"
            )

            mastery_col1, mastery_col2, mastery_col3 = (
                st.columns(3)
            )

            with mastery_col1:

                st.metric(
                    "🔥 Strong",
                    stats["strong_topics"]
                )

            with mastery_col2:

                st.metric(
                    "🟡 Review",
                    stats["review_topics"]
                )

            with mastery_col3:

                st.metric(
                    "🔴 Weak",
                    stats["weak_topics"]
                )

            # =================================================
            # WHAT SHOULD I STUDY?
            # =================================================

            st.divider()

            st.subheader(
                "✨ What Should I Study Now?"
            )

            if topics:

                # Lowest mastery first
                recommended_topic = min(
                    topics,
                    key=lambda topic:
                    topic["mastery"]
                )

                priority = (
                    recommended_topic[
                        "priority"
                    ]
                    or "MEDIUM"
                )

                mastery = (
                    recommended_topic[
                        "mastery"
                    ]
                    or 0
                )

                if mastery < 50:

                    priority_label = (
                        "🔥 HIGH"
                    )

                    reason = (
                        "This is currently one "
                        "of your weakest topics."
                    )

                elif mastery < 80:

                    priority_label = (
                        "🟡 MEDIUM"
                    )

                    reason = (
                        "You understand the basics, "
                        "but this topic needs revision."
                    )

                else:

                    priority_label = (
                        "🟢 LOW"
                    )

                    reason = (
                        "You already have strong "
                        "mastery of this topic."
                    )

                recommendation_col1, recommendation_col2 = (
                    st.columns([3, 1])
                )

                with recommendation_col1:

                    st.markdown(
                        f"""
                        ### 🧠 {recommended_topic["name"]}

                        **Unit:** {
                            recommended_topic["unit"]
                            or "Not specified"
                        }

                        **Priority:** {
                            priority_label
                        }

                        **Current mastery:** {
                            mastery:.0f}%

                        **Reason:** {reason}
                        """
                    )

                with recommendation_col2:

                    st.write("")

                    if st.button(
                        "🚀 Start Learning",
                        use_container_width=True
                    ):

                        st.session_state[
                            "selected_topic"
                        ] = (
                            recommended_topic[
                                "name"
                            ]
                        )

                        navigate(
                            "📖 Learn"
                        )

            else:

                st.info(
                    """
                    No topics have been added yet.

                    Analyze a syllabus to populate
                    your important topics.
                    """
                )

            # =================================================
            # LATEST QUIZ
            # =================================================

            st.divider()

            st.subheader(
                "❓ Latest Quiz Performance"
            )

            if latest_quiz:

                percentage = (
                    latest_quiz["score"]
                    /
                    latest_quiz[
                        "total_questions"
                    ]
                    * 100
                )

                quiz_col1, quiz_col2, quiz_col3 = (
                    st.columns(3)
                )

                with quiz_col1:

                    st.metric(
                        "Score",
                        f"{latest_quiz['score']}/"
                        f"{latest_quiz['total_questions']}"
                    )

                with quiz_col2:

                    st.metric(
                        "Percentage",
                        f"{percentage:.0f}%"
                    )

                with quiz_col3:

                    st.metric(
                        "Difficulty",
                        latest_quiz[
                            "difficulty"
                        ]
                    )

            else:

                st.info(
                    "You haven't taken a quiz yet."
                )

            # =================================================
            # AI INSIGHT
            # =================================================

            st.divider()

            st.subheader(
                "🤖 StudyFlow Insight"
            )

            if stats["weak_topics"] > 0:

                weak_topics = [
                    topic["name"]
                    for topic in topics
                    if (
                        topic["mastery"] < 50
                    )
                ]

                weak_text = ", ".join(
                    weak_topics[:3]
                )

                st.warning(
                    f"""
                    You currently have {
                        stats["weak_topics"]
                    } weak topic(s).

                    🎯 Recommended focus:
                    **{weak_text}**

                    Spend additional study time on
                    these topics before moving forward.
                    """
                )

            elif stats["average_mastery"] >= 80:

                st.success(
                    """
                    🎉 Excellent work!

                    Your current topic mastery is strong.
                    Continue practicing and move toward
                    exam revision.
                    """
                )

            else:

                st.info(
                    """
                    Keep going! Your progress is building.

                    Complete more learning sessions and
                    quizzes to improve your mastery score.
                    """
                )


# ============================================================
# SUBJECTS
# ============================================================

elif st.session_state.page == "📚 Subjects":

    st.title("📚 My Subjects")

    st.write(
        "Add, edit, delete, and switch between "
        "your subjects."
    )

    st.divider()

    # --------------------------------------------------------
    # Add Subject
    # --------------------------------------------------------

    with st.expander(
        "➕ Add New Subject",
        expanded=not bool(subjects),
    ):

        with st.form(
            "add_subject_form"
        ):

            name = st.text_input(
                "Subject Name",
                placeholder="Example: Data Mining",
            )

            exam_date = st.date_input(
                "Exam Date",
                value=date.today(),
            )

            daily_hours = st.number_input(
                "Daily Study Hours",
                min_value=0.5,
                max_value=12.0,
                value=2.0,
                step=0.5,
            )

            goal = st.text_area(
                "Study Goal",
                placeholder=(
                    "Example: Understand important "
                    "concepts and prepare for the exam."
                ),
            )

            submitted = st.form_submit_button(
                "➕ Add Subject",
                use_container_width=True,
            )

            if submitted:

                if not name.strip():

                    st.error(
                        "Please enter a subject name."
                    )

                else:

                    if st.session_state.student_id is None:

                        student_name = (
                            st.session_state.student_name
                            or "Student"
                        ).strip()

                        existing_student = get_student_by_name(
                            student_name
                        )

                        if existing_student:

                            st.session_state.student_id = (
                                existing_student["id"]
                        )

                        else:

                            st.session_state.student_id = (
                                create_student(
                                    student_name
                                )
                            )

                    subject_id = create_subject(

                        student_id=(
                            st.session_state.student_id
                        ),

                        name=name.strip(),

                        exam_date=(
                            exam_date.isoformat()
                        ),

                        daily_hours=daily_hours,

                        goal=goal.strip(),
                    )

                    st.session_state.selected_subject_id = (
                        subject_id
                    )

                    st.success(
                        f"'{name}' added successfully! 🎉"
                    )

                    st.rerun()

    # --------------------------------------------------------
    # Existing subjects
    # --------------------------------------------------------

    st.divider()

    if not subjects:

        st.info(
            "No subjects added yet."
        )

    else:

        for subject in subjects:

            with st.container(
                border=True
            ):

                col1, col2 = st.columns(
                    [4, 1]
                )

                with col1:

                    st.subheader(
                        f"📘 {subject['name']}"
                    )

                    st.write(
                        f"📅 Exam: "
                        f"{subject['exam_date'] or 'Not set'}"
                    )

                    st.write(
                        f"⏱ Daily study time: "
                        f"{subject['daily_hours'] or 'Not set'} hours"
                    )

                    if subject["goal"]:

                        st.write(
                            f"🎯 Goal: "
                            f"{subject['goal']}"
                        )

                with col2:

                    if st.button(
                        "▶️ Open",
                        key=f"open_{subject['id']}",
                        use_container_width=True,
                    ):

                        st.session_state.selected_subject_id = (
                            subject["id"]
                        )

                        navigate(
                            "🎯 What Should I Study?"
                        )

                edit_key = (
                    f"edit_{subject['id']}"
                )

                with st.expander(
                    "✏️ Edit Subject"
                ):

                    with st.form(
                        f"edit_form_{subject['id']}"
                    ):

                        new_name = st.text_input(
                            "Subject Name",
                            value=subject["name"],
                        )

                        current_exam = (
                            date.fromisoformat(
                                subject["exam_date"]
                            )
                            if subject["exam_date"]
                            else date.today()
                        )

                        new_exam_date = st.date_input(
                            "Exam Date",
                            value=current_exam,
                        )

                        new_daily_hours = st.number_input(
                            "Daily Study Hours",
                            min_value=0.5,
                            max_value=12.0,
                            value=float(
                                subject["daily_hours"]
                                or 2
                            ),
                            step=0.5,
                        )

                        new_goal = st.text_area(
                            "Study Goal",
                            value=subject["goal"]
                            or "",
                        )

                        save = st.form_submit_button(
                            "💾 Save Changes",
                            use_container_width=True,
                        )

                        if save:

                            update_subject(

                                subject_id=subject["id"],

                                name=new_name.strip(),

                                exam_date=(
                                    new_exam_date.isoformat()
                                ),

                                daily_hours=(
                                    new_daily_hours
                                ),

                                goal=new_goal.strip(),
                            )

                            st.success(
                                "Subject updated successfully."
                            )

                            st.rerun()

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{subject['id']}",
                    type="secondary",
                ):

                    delete_subject(
                        subject["id"]
                    )

                    if (
                        st.session_state.selected_subject_id
                        == subject["id"]
                    ):

                        st.session_state.selected_subject_id = (
                            None
                        )

                    st.success(
                        "Subject deleted."
                    )

                    st.rerun()


# ============================================================
# WHAT SHOULD I STUDY?
# ============================================================

elif st.session_state.page == "🎯 What Should I Study?":

    st.title(
        "🎯 What Should I Study?"
    )

    if not selected_subject:

        st.warning(
            "Please select a subject first."
        )

        if st.button(
            "📚 Go to Subjects"
        ):

            navigate("📚 Subjects")

    else:

        subject_id = (
            selected_subject["id"]
        )

        st.subheader(
            f"📘 {selected_subject['name']}"
        )

        days = calculate_days_until_exam(
            selected_subject["exam_date"]
        )

        if days is not None:

            st.caption(
                f"📅 {days} days remaining "
                f"until your exam."
            )

        # ----------------------------------------------------
        # Get topics
        # ----------------------------------------------------

        topics = get_subject_topics(
            subject_id
        )

        if not topics:

            st.info(
                """
                No syllabus topics are available yet.

                Analyze your syllabus first so StudyFlow
                can determine what you should study.
                """
            )

        else:

            recommendation = (
                get_top_recommendation(
                    topics
                )
            )

            recommendations = (
                build_topic_recommendations(
                    topics
                )
            )

            # =================================================
            # TOP RECOMMENDATION
            # =================================================

            st.divider()

            st.subheader(
                "🔥 Your Top Recommendation"
            )

            if recommendation:

                topic = recommendation[
                    "topic_data"
                ]

                progress = recommendation[
                    "progress"
                ]

                action = recommendation[
                    "action"
                ]

                mastery = (
                    progress.score_percentage
                )

                if action["priority"] == "HIGH":

                    priority_text = (
                        "🔥 HIGH PRIORITY"
                    )

                elif action["priority"] == "MEDIUM":

                    priority_text = (
                        "🟡 MEDIUM PRIORITY"
                    )

                else:

                    priority_text = (
                        "🟢 LOW PRIORITY"
                    )

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"## 🧠 {topic['name']}"
                    )

                    st.write(
                        f"**Unit:** "
                        f"{topic['unit'] or 'Not specified'}"
                    )

                    st.write(
                        f"**Priority:** "
                        f"{priority_text}"
                    )

                    st.write(
                        f"**Current mastery:** "
                        f"{mastery:.0f}%"
                    )

                    st.progress(
                        min(
                            mastery / 100,
                            1.0
                        )
                    )

                    st.write(
                        f"**Recommended action:** "
                        f"{action['action']}"
                    )

                    # -----------------------------------------
                    # Reason
                    # -----------------------------------------

                    if mastery < 50:

                        reason = (
                            "Your current mastery is low. "
                            "This topic needs additional "
                            "learning and practice."
                        )

                    elif mastery < 80:

                        reason = (
                            "You understand the basics, "
                            "but more revision will improve "
                            "your confidence."
                        )

                    else:

                        reason = (
                            "You already have strong "
                            "understanding of this topic. "
                            "Continue to the next topic "
                            "after a quick review."
                        )

                    st.info(
                        f"💡 **Why this topic?**\n\n"
                        f"{reason}"
                    )

                    st.success(
                        f"🎯 **StudyFlow recommendation:** "
                        f"{action['message']}"
                    )

                    # -----------------------------------------
                    # Actions
                    # -----------------------------------------

                    action_col1, action_col2 = (
                        st.columns(2)
                    )

                    with action_col1:

                        if st.button(
                            "📖 Learn This Topic",
                            key=(
                                f"learn_{topic['id']}"
                            ),
                            use_container_width=True,
                        ):

                            st.session_state[
                                "selected_topic"
                            ] = topic["name"]

                            navigate(
                                "📖 Learn"
                            )

                    with action_col2:

                        if st.button(
                            "❓ Practice This Topic",
                            key=(
                                f"quiz_{topic['id']}"
                            ),
                            use_container_width=True,
                        ):

                            st.session_state[
                                "selected_topic"
                            ] = topic["name"]

                            navigate(
                                "❓ Quiz"
                            )

            # =================================================
            # OTHER RECOMMENDATIONS
            # =================================================

            st.divider()

            st.subheader(
                "📋 Other Topics"
            )

            for index, item in enumerate(
                recommendations[1:],
                start=2
            ):

                topic = item["topic_data"]

                progress = item["progress"]

                mastery = (
                    progress.score_percentage
                )

                if mastery < 50:

                    status = "🔴 Weak"

                elif mastery < 80:

                    status = "🟡 Review"

                else:

                    status = "🟢 Strong"

                with st.container(
                    border=True
                ):

                    col1, col2, col3 = (
                        st.columns(
                            [4, 2, 1]
                        )
                    )

                    with col1:

                        st.markdown(
                            f"### {index}. "
                            f"{topic['name']}"
                        )

                        st.caption(
                            topic["unit"]
                            or "Unit not specified"
                        )

                    with col2:

                        st.write(
                            f"{status}"
                        )

                        st.write(
                            f"Mastery: "
                            f"{mastery:.0f}%"
                        )

                    with col3:

                        if st.button(
                            "📖",
                            key=(
                                f"other_{topic['id']}"
                            ),
                            help="Learn this topic",
                        ):

                            st.session_state[
                                "selected_topic"
                            ] = topic["name"]

                            navigate(
                                "📖 Learn"
                            )

# ============================================================
# STUDY PLAN
# ============================================================

elif st.session_state.page == "📅 Study Plan":

    st.title("📅 My Study Plan")

    if not selected_subject:

        st.warning(
            "Please select a subject first."
        )

        if st.button(
            "📚 Go to Subjects"
        ):

            navigate("📚 Subjects")

    else:

        subject_id = (
            selected_subject["id"]
        )

        subject_name = (
            selected_subject["name"]
        )

        exam_date = (
            selected_subject["exam_date"]
        )

        daily_hours = (
            selected_subject["daily_hours"]
        )

        st.subheader(
            f"📘 {subject_name}"
        )

        # ----------------------------------------------------
        # Exam information
        # ----------------------------------------------------

        days = calculate_days_until_exam(
            exam_date
        )

        info_col1, info_col2, info_col3 = (
            st.columns(3)
        )

        with info_col1:

            st.metric(
                "📅 Exam Date",
                exam_date or "Not set"
            )

        with info_col2:

            st.metric(
                "⏳ Days Remaining",
                days
                if days is not None
                else "—"
            )

        with info_col3:

            st.metric(
                "⏱ Daily Study Time",
                f"{daily_hours or 0} hrs"
            )

        st.divider()

        # ----------------------------------------------------
        # Generate plan
        # ----------------------------------------------------

        if st.button(
            "🧠 Generate My Study Plan",
            use_container_width=True
        ):

            if not exam_date:

                st.error(
                    "Please set an exam date "
                    "for this subject."
                )

            elif not daily_hours:

                st.error(
                    "Please set your daily study hours."
                )

            else:

                try:

                    with st.spinner(
                        "Building your personalized study plan..."
                    ):

                        plan = (
                            generate_subject_study_plan(

                                subject_id=subject_id,

                                subject_name=subject_name,

                                exam_date=exam_date,

                                daily_hours=float(
                                    daily_hours
                                )
                            )
                        )

                    if plan is None:

                        st.warning(
                            """
                            No topics are available for
                            this subject yet.

                            Analyze your syllabus first.
                            """
                        )

                    else:

                        st.session_state[
                            "current_study_plan"
                        ] = plan

                        st.success(
                            "Your personalized study plan "
                            "has been generated! 🎉"
                        )

                except ValueError as error:

                    st.error(
                        str(error)
                    )

        # ----------------------------------------------------
        # Display generated plan
        # ----------------------------------------------------

        plan = st.session_state.get(
            "current_study_plan"
        )

        if plan:

            st.divider()

            st.subheader(
                "📅 Your Personalized Plan"
            )

            # ------------------------------------------------
            # Summary
            # ------------------------------------------------

            summary_col1, summary_col2, summary_col3 = (
                st.columns(3)
            )

            with summary_col1:

                st.metric(
                    "📆 Study Days",
                    plan.total_days
                )

            with summary_col2:

                st.metric(
                    "⏱ Total Study Time",
                    f"{plan.total_minutes // 60}h "
                    f"{plan.total_minutes % 60}m"
                )

            with summary_col3:

                st.metric(
                    "📚 Sessions",
                    len(plan.sessions)
                )

            st.divider()

            # ------------------------------------------------
            # Group sessions by date
            # ------------------------------------------------

            sessions_by_date = {}

            for session in plan.sessions:

                sessions_by_date.setdefault(
                    session.date,
                    []
                ).append(session)

            # ------------------------------------------------
            # Display days
            # ------------------------------------------------

            for day_number, (
                session_date,
                sessions
            ) in enumerate(
                sessions_by_date.items(),
                start=1
            ):

                total_day_minutes = sum(
                    session.duration_minutes
                    for session in sessions
                )

                with st.expander(
                    f"📆 Day {day_number} — "
                    f"{session_date} "
                    f"({total_day_minutes} min)",
                    expanded=(
                        day_number == 1
                    )
                ):

                    for session_index, session in enumerate(
                        sessions
                    ):

                        task_key = (
                            f"task_"
                            f"{session_date}_"
                            f"{session_index}"
                        )

                        completed = st.checkbox(
                            f"📖 {session.topic} "
                            f"— {session.duration_minutes} min",
                            key=task_key
                        )

                        st.caption(
                            f"Unit: {session.unit}"
                        )

                        st.write(
                            session.activity
                        )

                        if completed:

                            st.success(
                                "✅ Task completed!"
                            )

                        st.divider()

# ============================================================
# LEARNING
# ============================================================

elif st.session_state.page == "📖 Learn":

    st.title("📖 Learn")

    if not selected_subject:

        st.warning(
            "Please select a subject first."
        )

        if st.button(
            "📚 Go to Subjects"
        ):

            navigate("📚 Subjects")

    else:

        subject_name = (
            selected_subject["name"]
        )

        st.subheader(
            f"📘 {subject_name}"
        )

        # ----------------------------------------------------
        # Topic selection
        # ----------------------------------------------------

        topics = get_subject_topics(
            selected_subject["id"]
        )

        topic_names = [
            topic["name"]
            for topic in topics
        ]

        default_topic = st.session_state.get(
            "selected_topic"
        )

        if topic_names:

            if (
                default_topic
                in topic_names
            ):

                default_index = (
                    topic_names.index(
                        default_topic
                    )
                )

            else:

                default_index = 0

            selected_topic = st.selectbox(
                "Choose a topic",
                topic_names,
                index=default_index
            )

        else:

            selected_topic = st.text_input(
                "Enter a topic",
                placeholder=(
                    "Example: Decision Trees"
                )
            )

        # ----------------------------------------------------
        # Generate
        # ----------------------------------------------------

        if st.button(
            "🧠 Generate Learning Content",
            use_container_width=True
        ):

            if not selected_topic:

                st.warning(
                    "Please select a topic."
                )

            else:

                try:

                    with st.spinner(
                        "Preparing your learning material..."
                    ):

                        selected_topic_data = next(
                        (
                            topic
                            for topic in topics
                            if topic["name"] == selected_topic
                        ),
                        None
                    )

                    unit = ""

                    if selected_topic_data:

                        unit = (
                            selected_topic_data["unit"]
                            or ""
                        )

                    prerequisites = []

                    if selected_topic_data:

                        prerequisites = []

                    content = generate_learning_content(

                        subject_name=subject_name,

                        unit=unit,

                        topic=selected_topic,

                        prerequisites=prerequisites
                    )

                    st.session_state[
                        "learning_content"
                    ] = content

                except Exception as error:

                    st.error(
                        f"Unable to generate "
                        f"learning content: {error}"
                    )

        # ----------------------------------------------------
        # Display content
        # ----------------------------------------------------

        content = st.session_state.get(
            "learning_content"
        )

        if content:

            st.divider()

            st.header(
                f"🧠 {content.topic}"
            )

            st.caption(
                f"⏱ Estimated study time: "
                f"{content.estimated_minutes} minutes"
            )

            # =================================================
            # SIMPLE EXPLANATION
            # =================================================

            st.subheader(
                "🧠 Simple Explanation"
            )

            st.write(
                content.simple_explanation
            )

            # =================================================
            # KEY CONCEPTS
            # =================================================

            st.subheader(
                "📌 Key Concepts"
            )

            st.subheader("📌 Key Concepts")

            for point in content.key_points:

                st.markdown(
                    f"• {point}"
                )

            # =================================================
            # EXAMPLES
            # =================================================

            st.subheader(
                "💡 Examples"
            )

            for index, example in enumerate(
                content.examples,
                start=1
            ):

                st.markdown(
                    f"**Example {index}:** "
                    f"{example}"
                )

            # =================================================
            # EXAM DEFINITION
            # =================================================

            st.subheader(
                "📝 Exam Definition"
            )
            
            st.info(
                content.exam_definition
            )

            # =================================================
            # IMPORTANT POINTS
            # =================================================

            st.subheader("⭐ Important for Exams")

            if content.important_points:

                for point in content.important_points:

                    st.markdown(
                        f"✅ {point}"
                    )

            else:

                for point in content.key_points:

                    st.markdown(
                        f"✅ {point}"
                    )

            # =================================================
            # COMMON MISTAKES
            # =================================================

            st.subheader(
                "⚠️ Common Mistakes"
            )

            for mistake in content.common_mistakes:

                st.markdown(
                    f"❌ {mistake}"
                )

            # =================================================
            # MEMORY TIP
            # =================================================

            st.subheader(
                "🧠 Memory Tip"
            )

            st.success(
                content.memory_tip
            )

            # =================================================
            # QUICK CHECK
            # =================================================

            st.divider()

            st.subheader(
                "❓ Quick Check"
            )

            st.write(
                content.quick_check_question
            )           

            if st.button(
                "💡 Show Answer"
            ):

                if content.quick_check_answer:

                    st.success(
                        content.quick_check_answer
                    )

                else:

                    st.info(
                        "Try answering the question yourself "
                        "before reviewing the topic again."
                    )         

            if content.analogy:

                st.subheader("💡 Easy Analogy")

                st.info(
                    content.analogy
                )

# ============================================================
# AI TUTOR
# ============================================================

# ============================================================
# AI TUTOR
# ============================================================

elif st.session_state.page == "🤖 AI Tutor":

    st.title("🤖 StudyFlow AI Tutor")

    if not selected_subject:

        st.warning("Select a subject first.")

    else:

        st.caption(
            f"Current subject: **{selected_subject['name']}**"
        )

        # ----------------------------------------------------
        # GET TOPICS
        # ----------------------------------------------------

        topics = get_subject_topics(
            selected_subject["id"]
        )

        topic_names = [
            topic["name"]
            for topic in topics
        ]

        # ----------------------------------------------------
        # SELECT TOPIC
        # ----------------------------------------------------

        if topic_names:

            default_topic = st.session_state.get(
                "selected_topic"
            )

            if default_topic in topic_names:

                default_index = topic_names.index(
                    default_topic
                )

            else:

                default_index = 0

            topic = st.selectbox(
                "Current topic",
                topic_names,
                index=default_index,
                key="tutor_topic"
            )

        else:

            topic = st.text_input(
                "Current topic",
                placeholder="Example: Morphology",
                key="tutor_topic_input"
            )

        # ----------------------------------------------------
        # GET UNIT
        # ----------------------------------------------------

        selected_topic_data = next(
            (
                item
                for item in topics
                if item["name"] == topic
            ),
            None
        )

        unit = ""

        if selected_topic_data:

            unit = (
                selected_topic_data.get("unit")
                or ""
            )

        # ----------------------------------------------------
        # CURRENT TOPIC DISPLAY
        # ----------------------------------------------------

        if topic:

            st.info(
                f"📚 Your questions will be related to: **{topic}**"
            )

        # ----------------------------------------------------
        # CHAT HISTORY
        # ----------------------------------------------------

        if "tutor_messages" not in st.session_state:

            st.session_state.tutor_messages = []

        # ----------------------------------------------------
        # DISPLAY CHAT HISTORY
        # ----------------------------------------------------

        for message in st.session_state.tutor_messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

        # ----------------------------------------------------
        # USER QUESTION
        # ----------------------------------------------------

        question = st.chat_input(
            "Ask your AI tutor..."
        )

        if question:

            if not topic or not topic.strip():

                st.warning(
                    "Please select or enter a topic first."
                )

            else:

                # --------------------------------------------
                # SAVE USER MESSAGE
                # --------------------------------------------

                st.session_state.tutor_messages.append(
                    {
                        "role": "user",
                        "content": question
                    }
                )

                # --------------------------------------------
                # DISPLAY USER MESSAGE
                # --------------------------------------------

                with st.chat_message("user"):

                    st.markdown(question)

                # --------------------------------------------
                # PREVIOUS CONTEXT
                # --------------------------------------------

                previous_context = (
                    st.session_state.tutor_messages[-7:-1]
                )

                # --------------------------------------------
                # CALL AI TUTOR
                # --------------------------------------------

                try:

                    with st.chat_message("assistant"):

                        with st.spinner(
                            "🤖 AI Tutor is thinking..."
                        ):

                            response = ask_tutor(

                                subject_name=(
                                    selected_subject["name"]
                                ),

                                unit=unit,

                                topic=topic,

                                question=question,

                                previous_context=(
                                    previous_context
                                )
                            )

                        # ------------------------------------
                        # ANSWER
                        # ------------------------------------

                        st.markdown(
                            "### 💡 Answer"
                        )

                        st.write(
                            response.answer
                        )

                        # ------------------------------------
                        # SIMPLE EXPLANATION
                        # ------------------------------------

                        if response.simple_explanation:

                            st.markdown(
                                "### 🧠 Simple Explanation"
                            )

                            st.write(
                                response.simple_explanation
                            )

                        # ------------------------------------
                        # EXAMPLE
                        # ------------------------------------

                        if response.example:

                            st.markdown(
                                "### 💡 Example"
                            )

                            st.info(
                                response.example
                            )

                        # ------------------------------------
                        # KEY POINTS
                        # ------------------------------------

                        if response.key_points:

                            st.markdown(
                                "### 📌 Key Points"
                            )

                            for point in response.key_points:

                                st.markdown(
                                    f"• {point}"
                                )

                        # ------------------------------------
                        # FOLLOW-UP
                        # ------------------------------------

                        if response.follow_up_question:

                            st.markdown(
                                "### 🎯 Think About This"
                            )

                            st.caption(
                                response.follow_up_question
                            )

                        # ------------------------------------
                        # BUILD CHAT MESSAGE
                        # ------------------------------------

                        assistant_text = (
                            f"### 💡 Answer\n\n"
                            f"{response.answer}"
                        )

                        if response.simple_explanation:

                            assistant_text += (
                                "\n\n"
                                "### 🧠 Simple Explanation\n\n"
                                + response.simple_explanation
                            )

                        if response.example:

                            assistant_text += (
                                "\n\n"
                                "### 💡 Example\n\n"
                                + response.example
                            )

                        if response.key_points:

                            assistant_text += (
                                "\n\n"
                                "### 📌 Key Points\n\n"
                            )

                            assistant_text += "\n".join(
                                f"• {point}"
                                for point in response.key_points
                            )

                        if response.follow_up_question:

                            assistant_text += (
                                "\n\n"
                                "### 🎯 Think About This\n\n"
                                + response.follow_up_question
                            )

                        # ------------------------------------
                        # SAVE AI RESPONSE
                        # ------------------------------------

                        st.session_state.tutor_messages.append(
                            {
                                "role": "assistant",
                                "content": assistant_text
                            }
                        )

                except Exception as error:

                    st.error(
                        "❌ Unable to generate AI Tutor response."
                    )

                    st.exception(error)


# ============================================================
# QUIZ
# ============================================================

elif st.session_state.page == "❓ Quiz":

    st.title("❓ Practice Quiz")

    if not selected_subject:

        st.warning(
            "Select a subject first."
        )

    else:

        st.subheader(
            selected_subject["name"]
        )

        topic = st.text_input(
            "Quiz topic",
            placeholder="Example: Decision Trees",
        )

        difficulty = st.selectbox(
            "Difficulty",
            [
                "EASY",
                "MEDIUM",
                "HARD",
            ],
        )

        number_of_questions = st.slider(
            "Number of Questions",
            min_value=1,
            max_value=10,
            value=5,
        )

        if st.button(
            "🚀 Generate Quiz",
            use_container_width=True,
        ):

            if topic.strip():

                st.success(
                    "Quiz generation will be connected "
                    "to the AI quiz engine here."
                )

            else:

                st.warning(
                    "Enter a topic first."
                )


# ============================================================
# PROGRESS
# ============================================================

elif st.session_state.page == "📊 Progress":

    st.title("📊 My Progress")

    if not selected_subject:

        st.warning(
            "Select a subject first."
        )

    else:

        st.subheader(
            selected_subject["name"]
        )

        st.info(
            """
            Your topic mastery, quiz history,
            weak areas, strong areas, and adaptive
            recommendations will appear here.
            """
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🔥 Strong Topics",
                "—"
            )

        with col2:

            st.metric(
                "🟡 Topics to Review",
                "—"
            )

        with col3:

            st.metric(
                "🔴 Weak Topics",
                "—"
            )

        st.divider()

        st.subheader(
            "🎯 Recommended Action"
        )

        st.write(
            """
            After quiz attempts are connected to
            the progress database, StudyFlow will
            automatically identify weak topics and
            adjust the study plan.
            """
        )