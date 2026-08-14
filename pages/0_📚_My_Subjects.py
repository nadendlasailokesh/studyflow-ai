# ============================================================
# PROJECT ROOT FIX
# ============================================================

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st

from src.database.db import initialize_database

from src.database.repository import (
    create_student,
    create_subject,
    get_student,
    get_subjects,
    update_subject,
    delete_subject,
    create_topic,
    get_topics
)

from src.ai.syllabus_analyzer import analyze_syllabus


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Subjects",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# STUDENT SETUP
# ============================================================

def get_or_create_student():

    # Reuse student stored in Streamlit session
    if "student_id" in st.session_state:

        student = get_student(
            st.session_state.student_id
        )

        if student:

            return student["id"]

        # Stored ID is invalid
        st.session_state.pop(
            "student_id",
            None
        )

    # Try to use existing default student
    student = get_student(1)

    if student:

        st.session_state.student_id = (
            student["id"]
        )

        return student["id"]

    # Create student if none exists
    student_id = create_student(
        name="Student",
        knowledge_level="Beginner"
    )

    st.session_state.student_id = (
        student_id
    )

    return student_id


student_id = get_or_create_student()


# ============================================================
# PAGE HEADER
# ============================================================

st.title("📚 My Subjects")

st.write(
    "Manage your subjects and analyze your syllabus "
    "with StudyFlow AI."
)


# ============================================================
# ADD NEW SUBJECT
# ============================================================

with st.expander(
    "➕ Add New Subject",
    expanded=True
):

    with st.form("add_subject_form"):

        name = st.text_input(
            "Subject Name",
            placeholder="e.g. Computer Linguistics"
        )

        col1, col2 = st.columns(2)

        with col1:

            exam_date = st.date_input(
                "Exam Date"
            )

        with col2:

            daily_hours = st.number_input(
                "Study Hours Per Day",
                min_value=0.5,
                max_value=12.0,
                value=2.0,
                step=0.5
            )

        goal = st.text_area(
            "Study Goal",
            placeholder=(
                "Example: Understand all units "
                "and prepare for the final exam."
            )
        )

        submitted = st.form_submit_button(
            "➕ Add Subject",
            type="primary"
        )

        if submitted:

            if not name.strip():

                st.error(
                    "Please enter a subject name."
                )

            else:

                subject_id = create_subject(
                    student_id=student_id,
                    name=name.strip(),
                    exam_date=str(exam_date),
                    daily_hours=daily_hours,
                    goal=goal.strip()
                )

                st.session_state.selected_subject_id = (
                    subject_id
                )

                # Clear old syllabus analysis
                st.session_state.pop(
                    "syllabus_analysis",
                    None
                )

                st.session_state.pop(
                    "syllabus_analysis_subject_id",
                    None
                )

                st.success(
                    f"'{name}' added successfully!"
                )

                st.rerun()


# ============================================================
# EXISTING SUBJECTS
# ============================================================

st.divider()

st.subheader("📖 Your Subjects")

subjects = get_subjects(student_id)


if not subjects:

    st.info(
        "You haven't added any subjects yet. "
        "Use 'Add New Subject' above."
    )


for subject in subjects:

    with st.container(border=True):

        col1, col2, col3 = st.columns(
            [5, 2, 2]
        )

        # ----------------------------------------------------
        # SUBJECT INFORMATION
        # ----------------------------------------------------

        with col1:

            st.markdown(
                f"### 📘 {subject['name']}"
            )

            st.write(
                f"📅 Exam Date: "
                f"{subject['exam_date']}"
            )

            st.write(
                f"⏱️ Daily Study Time: "
                f"{subject['daily_hours']} hours"
            )

            if subject["goal"]:

                st.caption(
                    f"🎯 Goal: {subject['goal']}"
                )

        # ----------------------------------------------------
        # OPEN
        # ----------------------------------------------------

        with col2:

            if st.button(
                "▶️ Open",
                key=f"open_{subject['id']}",
                use_container_width=True
            ):

                previous_subject = st.session_state.get(
                    "selected_subject_id"
                )

                st.session_state.selected_subject_id = (
                    subject["id"]
                )

                # Clear analysis when changing subject
                if previous_subject != subject["id"]:

                    st.session_state.pop(
                        "syllabus_analysis",
                        None
                    )

                    st.session_state.pop(
                        "syllabus_analysis_subject_id",
                        None
                    )

                st.rerun()

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        with col3:

            if st.button(
                "🗑️ Delete",
                key=f"delete_{subject['id']}",
                use_container_width=True
            ):

                delete_subject(
                    subject["id"]
                )

                if (
                    st.session_state.get(
                        "selected_subject_id"
                    )
                    == subject["id"]
                ):

                    st.session_state.pop(
                        "selected_subject_id",
                        None
                    )

                    st.session_state.pop(
                        "syllabus_analysis",
                        None
                    )

                    st.session_state.pop(
                        "syllabus_analysis_subject_id",
                        None
                    )

                st.rerun()


# ============================================================
# SELECTED SUBJECT
# ============================================================

selected_subject_id = st.session_state.get(
    "selected_subject_id"
)

selected_subject = None


if selected_subject_id:

    selected_subject = next(
        (
            subject
            for subject in subjects
            if subject["id"] == selected_subject_id
        ),
        None
    )


# ============================================================
# SYLLABUS ANALYZER
# ============================================================

if selected_subject:

    st.divider()

    st.subheader(
        "📄 Syllabus Analyzer"
    )

    st.write(
        f"Analyze the syllabus for "
        f"**{selected_subject['name']}**."
    )

    st.markdown(
        """
        **StudyFlow AI will:**

        🧠 Analyze the syllabus  
        📚 Identify units and topics  
        🎯 Assign topic priorities  
        ⏱️ Estimate study time  
        🔗 Identify prerequisites  
        💾 Save topics to your subject
        """
    )

    syllabus = st.text_area(
        "Paste your syllabus below",
        height=350,
        placeholder=(
            "Example:\n\n"
            "Unit-I: Introduction\n"
            "Words, Regular Expressions and Automata...\n\n"
            "Unit-II: Syntax\n"
            "N-gram models of Syntax..."
        ),
        key="syllabus_input"
    )

    if st.button(
        "🧠 Analyze Syllabus",
        type="primary",
        use_container_width=True
    ):

        if not syllabus.strip():

            st.warning(
                "Please paste your syllabus first."
            )

        else:

            with st.spinner(
                "🧠 AI is analyzing your syllabus..."
            ):

                try:

                    analysis = analyze_syllabus(

                        subject_name=(
                            selected_subject["name"]
                        ),

                        syllabus=syllabus,

                        exam_date=(
                            selected_subject["exam_date"]
                        ),

                        daily_hours=(
                            selected_subject["daily_hours"]
                        )
                    )

                    # Save analysis
                    st.session_state[
                        "syllabus_analysis"
                    ] = analysis

                    # VERY IMPORTANT:
                    # Remember which subject was analyzed
                    st.session_state[
                        "syllabus_analysis_subject_id"
                    ] = selected_subject["id"]

                    st.success(
                        "✅ Syllabus analyzed successfully!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        "❌ Unable to analyze the syllabus."
                    )

                    st.exception(error)


# ============================================================
# GET CURRENT ANALYSIS
# ============================================================

analysis = st.session_state.get(
    "syllabus_analysis"
)

analysis_subject_id = st.session_state.get(
    "syllabus_analysis_subject_id"
)


# ============================================================
# DISPLAY ANALYSIS
# ============================================================

if (
    analysis
    and selected_subject
    and analysis_subject_id == selected_subject["id"]
):

    st.divider()

    st.subheader(
        "📊 Syllabus Analysis"
    )

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        "### 📚 Subject Overview"
    )

    st.info(
        analysis.overview
    )

    # --------------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "📖 Topics Found",
            len(analysis.topics)
        )

    with col2:

        total_minutes = sum(
            topic.estimated_minutes
            for topic in analysis.topics
        )

        hours = total_minutes / 60

        st.metric(
            "⏱️ Estimated Total Time",
            f"{total_minutes} min"
        )

        st.caption(
            f"Approximately {hours:.1f} hours"
        )

    st.divider()

    # --------------------------------------------------------
    # TOPICS
    # --------------------------------------------------------

    st.subheader(
        "📋 Topics Identified"
    )

    for index, topic in enumerate(
        analysis.topics,
        start=1
    ):

        with st.container(border=True):

            st.markdown(
                f"### {index}. {topic.topic}"
            )

            col1, col2, col3 = st.columns(3)

            # ------------------------------------------------
            # UNIT
            # ------------------------------------------------

            with col1:

                st.write(
                    f"📘 **Unit:** "
                    f"{topic.unit or 'Not specified'}"
                )

            # ------------------------------------------------
            # PRIORITY
            # ------------------------------------------------

            with col2:

                if topic.priority == "HIGH":

                    priority_display = "🔥 HIGH"

                elif topic.priority == "MEDIUM":

                    priority_display = "🟡 MEDIUM"

                else:

                    priority_display = "🟢 LOW"

                st.write(
                    f"🎯 **Priority:** "
                    f"{priority_display}"
                )

            # ------------------------------------------------
            # TIME
            # ------------------------------------------------

            with col3:

                st.write(
                    f"⏱️ **Estimated:** "
                    f"{topic.estimated_minutes} min"
                )

            # ------------------------------------------------
            # REASON
            # ------------------------------------------------

            st.write(
                f"💡 **Reason:** {topic.reason}"
            )

            # ------------------------------------------------
            # PREREQUISITES
            # ------------------------------------------------

            if topic.prerequisites:

                st.write(
                    "🔗 **Prerequisites:** "
                    + ", ".join(
                        topic.prerequisites
                    )
                )

            else:

                st.caption(
                    "🔗 Prerequisites: None"
                )


    # ========================================================
    # SAVE TOPICS
    # ========================================================

    st.divider()

    st.subheader(
        "💾 Save Topics"
    )

    st.write(
        "Save these AI-generated topics to this subject. "
        "They will then be available to Study Plan, Learn, "
        "AI Tutor, Quiz, and Progress."
    )

    if st.button(
        "💾 Save Topics to My Subject",
        type="primary",
        use_container_width=True
    ):

        try:

            existing_topics = get_topics(
                selected_subject["id"]
            )

            existing_names = {
                str(topic["name"]).strip().lower()
                for topic in existing_topics
            }

            added_count = 0
            skipped_count = 0

            # ------------------------------------------------
            # INSERT TOPICS
            # ------------------------------------------------

            for topic in analysis.topics:

                topic_name = topic.topic.strip()

                if not topic_name:

                    continue

                # Prevent duplicates
                if (
                    topic_name.lower()
                    in existing_names
                ):

                    skipped_count += 1

                    continue

                create_topic(

                    subject_id=(
                        selected_subject["id"]
                    ),

                    name=topic_name,

                    unit=topic.unit,

                    priority=topic.priority
                )

                existing_names.add(
                    topic_name.lower()
                )

                added_count += 1


            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            if added_count > 0:

                st.success(
                    f"✅ {added_count} topic(s) "
                    f"added successfully!"
                )

            if skipped_count > 0:

                st.info(
                    f"ℹ️ {skipped_count} duplicate "
                    f"topic(s) were skipped."
                )

            # Clear analysis after saving
            st.session_state.pop(
                "syllabus_analysis",
                None
            )

            st.session_state.pop(
                "syllabus_analysis_subject_id",
                None
            )

            st.session_state[
                "syllabus_saved"
            ] = True

            st.rerun()

        except Exception as error:

            st.error(
                "❌ Unable to save topics."
            )

            st.exception(error)


# ============================================================
# CURRENT SUBJECT TOPICS
# ============================================================

if selected_subject:

    st.divider()

    st.subheader(
        f"📚 Topics in {selected_subject['name']}"
    )

    current_topics = get_topics(
        selected_subject["id"]
    )

    if not current_topics:

        st.info(
            """
            No topics have been added yet.

            Paste your syllabus above and use
            **🧠 Analyze Syllabus → 💾 Save Topics**.
            """
        )

    else:

        st.success(
            f"{len(current_topics)} topic(s) "
            f"currently available."
        )

        for index, topic in enumerate(
            current_topics,
            start=1
        ):

            col1, col2, col3 = st.columns(
                [4, 2, 1]
            )

            with col1:

                st.write(
                    f"**{index}. {topic['name']}**"
                )

                if topic["unit"]:

                    st.caption(
                        topic["unit"]
                    )

            with col2:

                priority = (
                    topic["priority"]
                    or "MEDIUM"
                )

                st.write(
                    f"🎯 {priority}"
                )

            with col3:

                mastery = (
                    topic["mastery"]
                    or 0
                )

                st.write(
                    f"📊 {mastery:.0f}%")


# ============================================================
# EDIT SUBJECT
# ============================================================

if selected_subject:

    st.divider()

    st.subheader(
        f"✏️ Edit: {selected_subject['name']}"
    )

    with st.form("edit_subject_form"):

        new_name = st.text_input(
            "Subject Name",
            value=selected_subject["name"]
        )

        new_exam_date = st.text_input(
            "Exam Date",
            value=selected_subject["exam_date"]
        )

        new_daily_hours = st.number_input(
            "Study Hours Per Day",
            min_value=0.5,
            max_value=12.0,
            value=float(
                selected_subject["daily_hours"]
                or 2
            ),
            step=0.5
        )

        new_goal = st.text_area(
            "Study Goal",
            value=selected_subject["goal"] or ""
        )

        save_changes = st.form_submit_button(
            "💾 Save Changes",
            type="primary"
        )

        if save_changes:

            if not new_name.strip():

                st.error(
                    "Subject name cannot be empty."
                )

            else:

                update_subject(

                    subject_id=selected_subject_id,

                    name=new_name.strip(),

                    exam_date=new_exam_date,

                    daily_hours=new_daily_hours,

                    goal=new_goal.strip()
                )

                st.success(
                    "Subject updated successfully!"
                )

                st.rerun()