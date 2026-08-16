# ============================================================
# MY SUBJECTS
# StudyFlow AI
# Phase 11.1 - UI/UX Polish
# ============================================================

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
    get_student_by_name,
    get_subjects,
    update_subject,
    delete_subject,
    create_topic,
    get_topics,
)

from src.ai.syllabus_analyzer import analyze_syllabus


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Subjects | StudyFlow AI",
    page_icon="📚",
    layout="wide",
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# SESSION STATE HELPERS
# ============================================================

def clear_syllabus_analysis():
    """
    Clear cached syllabus analysis from session state.
    """

    st.session_state.pop(
        "syllabus_analysis",
        None,
    )

    st.session_state.pop(
        "syllabus_analysis_subject_id",
        None,
    )


def get_or_create_student():
    """
    Reuse the current student whenever possible.

    Priority:
        1. Valid student_id from session
        2. Stored student_name
        3. Existing default Student
        4. Create default Student
    """

    # --------------------------------------------------------
    # Existing session student
    # --------------------------------------------------------

    student_id = st.session_state.get(
        "student_id"
    )

    if student_id is not None:

        student = get_student(
            student_id
        )

        if student:

            st.session_state.student_name = (
                student["name"]
            )

            return student["id"]

        st.session_state.pop(
            "student_id",
            None,
        )


    # --------------------------------------------------------
    # Existing student name
    # --------------------------------------------------------

    student_name = (
        st.session_state.get(
            "student_name",
            "",
        )
        or ""
    ).strip()

    if student_name:

        student = get_student_by_name(
            student_name
        )

        if student:

            st.session_state.student_id = (
                student["id"]
            )

            st.session_state.student_name = (
                student["name"]
            )

            return student["id"]


    # --------------------------------------------------------
    # Existing default student
    # --------------------------------------------------------

    student = get_student_by_name(
        "Student"
    )

    if student:

        st.session_state.student_id = (
            student["id"]
        )

        st.session_state.student_name = (
            student["name"]
        )

        return student["id"]


    # --------------------------------------------------------
    # Create default student
    # --------------------------------------------------------

    student_id = create_student(
        name="Student",
        knowledge_level="Beginner",
    )

    st.session_state.student_id = (
        student_id
    )

    st.session_state.student_name = (
        "Student"
    )

    return student_id


# ============================================================
# STUDENT
# ============================================================

student_id = get_or_create_student()


# ============================================================
# PAGE HEADER
# ============================================================

st.title("📚 My Subjects")

st.write(
    "Manage your subjects, analyze syllabi, and build "
    "your personalized learning path with StudyFlow AI."
)

st.divider()


# ============================================================
# ADD NEW SUBJECT
# ============================================================

with st.expander(
    "➕ Add New Subject",
    expanded=not bool(
        st.session_state.get(
            "selected_subject_id"
        )
    ),
):

    with st.form(
        "add_subject_form",
        clear_on_submit=True,
    ):

        st.markdown(
            "### Create a subject"
        )

        st.caption(
            "Add your subject details so StudyFlow can "
            "generate a personalized learning structure."
        )

        name = st.text_input(
            "Subject Name",
            placeholder="e.g. Computational Linguistics",
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
                step=0.5,
            )

        goal = st.text_area(
            "Study Goal",
            placeholder=(
                "Example: Understand all units and "
                "prepare for the final examination."
            ),
            height=100,
        )

        submitted = st.form_submit_button(
            "➕ Add Subject",
            type="primary",
            use_container_width=True,
        )

        if submitted:

            cleaned_name = (
                name or ""
            ).strip()

            if not cleaned_name:

                st.error(
                    "Please enter a subject name."
                )

            else:

                try:

                    subject_id = create_subject(
                        student_id=student_id,
                        name=cleaned_name,
                        exam_date=str(exam_date),
                        daily_hours=daily_hours,
                        goal=(goal or "").strip(),
                    )

                    st.session_state.selected_subject_id = (
                        subject_id
                    )

                    clear_syllabus_analysis()

                    st.session_state[
                        "syllabus_saved"
                    ] = False

                    st.success(
                        f"'{cleaned_name}' was added successfully."
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        "Unable to create the subject."
                    )

                    st.exception(error)


# ============================================================
# LOAD SUBJECTS
# ============================================================

subjects = get_subjects(
    student_id
)


# ============================================================
# SUBJECT LIST
# ============================================================

st.subheader("📖 Your Subjects")

if not subjects:

    st.info(
        "You haven't added any subjects yet. "
        "Use **Add New Subject** above to get started."
    )

else:

    st.caption(
        f"{len(subjects)} subject(s) available"
    )


    for subject in subjects:

        subject_id = subject["id"]

        with st.container(
            border=True
        ):

            info_col, action_col = st.columns(
                [7, 2]
            )

            # ------------------------------------------------
            # SUBJECT INFORMATION
            # ------------------------------------------------

            with info_col:

                st.markdown(
                    f"### 📘 {subject['name']}"
                )

                meta_col1, meta_col2 = st.columns(2)

                with meta_col1:

                    st.write(
                        f"📅 **Exam Date:** "
                        f"{subject['exam_date']}"
                    )

                with meta_col2:

                    st.write(
                        f"⏱️ **Daily Study:** "
                        f"{subject['daily_hours']} hour(s)"
                    )

                goal_value = (
                    subject["goal"]
                    if "goal" in subject.keys()
                    else ""
                ) or ""

                goal_value = goal_value.strip()

                if goal_value:

                    st.caption(
                        f"🎯 Goal: {goal_value}"
                    )

            # ------------------------------------------------
            # ACTIONS
            # ------------------------------------------------

            with action_col:

                if st.button(
                    "▶️ Open",
                    key=f"open_subject_{subject_id}",
                    use_container_width=True,
                ):

                    previous_subject = (
                        st.session_state.get(
                            "selected_subject_id"
                        )
                    )

                    st.session_state.selected_subject_id = (
                        subject_id
                    )

                    if previous_subject != subject_id:

                        clear_syllabus_analysis()

                    st.session_state[
                        "syllabus_saved"
                    ] = False

                    st.rerun()

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_subject_{subject_id}",
                    use_container_width=True,
                ):

                    try:

                        delete_subject(
                            subject_id
                        )

                        if (
                            st.session_state.get(
                                "selected_subject_id"
                            )
                            == subject_id
                        ):

                            st.session_state.pop(
                                "selected_subject_id",
                                None,
                            )

                            clear_syllabus_analysis()

                        st.success(
                            f"'{subject['name']}' was deleted."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            "Unable to delete this subject."
                        )

                        st.exception(error)


# ============================================================
# SELECTED SUBJECT
# ============================================================

selected_subject_id = (
    st.session_state.get(
        "selected_subject_id"
    )
)

selected_subject = None


if selected_subject_id is not None:

    selected_subject = next(
        (
            subject
            for subject in subjects
            if subject["id"] == selected_subject_id
        ),
        None,
    )


# ============================================================
# SELECTED SUBJECT NOT FOUND
# ============================================================

if (
    selected_subject_id is not None
    and selected_subject is None
):

    st.session_state.pop(
        "selected_subject_id",
        None,
    )

    clear_syllabus_analysis()

    st.info(
        "The previously selected subject is no longer available."
    )

    st.stop()


# ============================================================
# SELECTED SUBJECT WORKSPACE
# ============================================================

if selected_subject:

    st.divider()

    st.header(
        f"📘 {selected_subject['name']}"
    )

    st.caption(
        "Selected subject workspace"
    )


    # ========================================================
    # SUBJECT SUMMARY
    # ========================================================

    summary_col1, summary_col2, summary_col3 = (
        st.columns(3)
    )

    with summary_col1:

        st.metric(
            "📅 Exam Date",
            str(
                selected_subject["exam_date"]
            ),
        )

    with summary_col2:

        st.metric(
            "⏱️ Daily Study",
            f"{selected_subject['daily_hours']} h",
        )

    with summary_col3:

        current_topics = get_topics(
            selected_subject["id"]
        )

        st.metric(
            "📚 Topics",
            len(current_topics),
        )


    subject_goal = (
        selected_subject["goal"]
        if "goal" in selected_subject.keys()
        else ""
    ) or ""

    subject_goal = subject_goal.strip()

    if subject_goal:

        st.info(
            f"🎯 **Study Goal:** {subject_goal}"
        )


    # ========================================================
    # SYLLABUS ANALYZER
    # ========================================================

    st.divider()

    st.subheader(
        "🧠 Syllabus Analyzer"
    )

    st.write(
        "Paste your syllabus and StudyFlow AI will "
        "identify units, topics, priorities, estimated "
        "study time, and prerequisites."
    )


    st.markdown(
        """
        **StudyFlow AI will:**

        - 🧠 Analyze your syllabus
        - 📚 Identify units and topics
        - 🎯 Assign topic priorities
        - ⏱️ Estimate study time
        - 🔗 Identify prerequisites
        - 💾 Save topics to your subject
        """
    )


    # --------------------------------------------------------
    # Syllabus input
    # --------------------------------------------------------

    syllabus = st.text_area(
        "Paste your syllabus",
        height=300,
        placeholder=(
            "Example:\n\n"
            "Unit-I: Introduction\n"
            "Words, Regular Expressions and Automata...\n\n"
            "Unit-II: Syntax\n"
            "N-gram models of Syntax...\n\n"
            "Unit-III: Semantics\n"
            "Semantic representation and interpretation..."
        ),
        key="syllabus_input",
    )


    # --------------------------------------------------------
    # Analyze
    # --------------------------------------------------------

    if st.button(
        "🧠 Analyze Syllabus",
        type="primary",
        use_container_width=True,
        key="analyze_syllabus_button",
    ):

        cleaned_syllabus = (
            syllabus or ""
        ).strip()

        if not cleaned_syllabus:

            st.warning(
                "Please paste your syllabus before analyzing it."
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

                        syllabus=cleaned_syllabus,

                        exam_date=(
                            selected_subject["exam_date"]
                        ),

                        daily_hours=(
                            selected_subject["daily_hours"]
                        ),
                    )

                    st.session_state[
                        "syllabus_analysis"
                    ] = analysis

                    st.session_state[
                        "syllabus_analysis_subject_id"
                    ] = selected_subject["id"]

                    st.session_state[
                        "syllabus_saved"
                    ] = False

                    st.success(
                        "✅ Syllabus analyzed successfully."
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        "Unable to analyze the syllabus."
                    )

                    st.caption(
                        "Please check your AI provider configuration "
                        "and try again."
                    )

                    st.exception(error)


    # ========================================================
    # RECOVER ANALYSIS
    # ========================================================

    analysis = st.session_state.get(
        "syllabus_analysis"
    )

    analysis_subject_id = (
        st.session_state.get(
            "syllabus_analysis_subject_id"
        )
    )


    # --------------------------------------------------------
    # Only display analysis for the subject that generated it.
    # --------------------------------------------------------

    if (
        analysis is not None
        and analysis_subject_id
        == selected_subject["id"]
    ):

        st.divider()

        st.subheader(
            "📊 Syllabus Analysis"
        )


        # ====================================================
        # ANALYSIS SUMMARY
        # ====================================================

        analysis_topics = (
            getattr(
                analysis,
                "topics",
                []
            )
            or []
        )


        total_topics = len(
            analysis_topics
        )


        total_minutes = sum(
            int(
                getattr(
                    topic,
                    "estimated_minutes",
                    0
                )
                or 0
            )
            for topic in analysis_topics
        )


        hours = (
            total_minutes / 60
            if total_minutes > 0
            else 0
        )


        summary_col1, summary_col2 = st.columns(2)

        with summary_col1:

            st.metric(
                "📚 Topics Identified",
                total_topics,
            )

        with summary_col2:

            st.metric(
                "⏱️ Estimated Study Time",
                f"{total_minutes} min",
            )

            if total_minutes > 0:

                st.caption(
                    f"Approximately {hours:.1f} hour(s)"
                )


        # ====================================================
        # TOPICS
        # ====================================================

        st.divider()

        st.subheader(
            "📋 Topics Identified"
        )


        if not analysis_topics:

            st.warning(
                "The AI analysis did not identify any topics."
            )

        else:

            for index, topic in enumerate(
                analysis_topics,
                start=1,
            ):

                topic_name = (
                    getattr(topic, "name", "")
                    or "Unnamed Topic"
                )

                unit = (
                    getattr(topic, "unit", "")
                    or "General"
                )

                priority = (
                    getattr(topic, "priority", "")
                    or "MEDIUM"
                )
                
                priority = str(
                    priority
                ).strip().upper()

                estimated_minutes = int(
                    getattr(
                        topic,
                        "estimated_minutes",
                        0
                    )
                    or 0
                )

                reason = (
                    getattr(
                        topic,
                        "reason",
                        ""
                    )
                    or "No reason provided."
                )

                prerequisites = (
                    getattr(
                        topic,
                        "prerequisites",
                        []
                    )
                    or []
                )


                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {index}. {topic_name}"
                    )

                    col1, col2, col3 = st.columns(3)


                    with col1:

                        st.write(
                            f"📘 **Unit**"
                        )

                        st.write(
                            unit
                        )


                    with col2:

                        st.write(
                            "🎯 **Priority**"
                        )

                        if priority == "HIGH":

                            st.error(
                                "🔥 HIGH"
                            )

                        elif priority == "MEDIUM":

                            st.warning(
                                "🟡 MEDIUM"
                            )

                        else:

                            st.success(
                                "🟢 LOW"
                            )


                    with col3:

                        st.write(
                            "⏱️ **Estimated Time**"
                        )

                        st.write(
                            f"{estimated_minutes} minute(s)"
                        )


                    st.write(
                        f"💡 **Reason:** {reason}"
                    )


                    if prerequisites:

                        prerequisite_text = ", ".join(
                            str(item)
                            for item in prerequisites
                        )

                        st.write(
                            f"🔗 **Prerequisites:** "
                            f"{prerequisite_text}"
                        )

                    else:

                        st.caption(
                            "🔗 Prerequisites: None"
                        )


        # ====================================================
        # SAVE TOPICS
        # ====================================================

        st.divider()

        st.subheader(
            "💾 Save Topics"
        )

        st.write(
            "Save the analyzed topics to this subject. "
            "Saved topics become available to Study Plan, "
            "Learn, AI Tutor, Practice Quiz, Progress, "
            "and Revision."
        )


        save_col1, save_col2 = st.columns(
            [3, 1]
        )


        with save_col1:

            if st.button(
                "💾 Save Topics to My Subject",
                type="primary",
                use_container_width=True,
                key="save_analyzed_topics_button",
            ):

                try:

                    existing_topics = get_topics(
                        selected_subject["id"]
                    )

                    existing_names = {
                        str(
                            topic["name"]
                        ).strip().lower()
                        for topic in existing_topics
                    }


                    added_count = 0
                    skipped_count = 0


                    for topic in analysis_topics:

                        topic_name = (
                            getattr(
                                topic,
                                "topic",
                                ""
                            )
                            or ""
                        ).strip()


                        if not topic_name:

                            continue


                        normalized_name = (
                            topic_name.lower()
                        )


                        if (
                            normalized_name
                            in existing_names
                        ):

                            skipped_count += 1

                            continue


                        create_topic(

                            subject_id=(
                                selected_subject["id"]
                            ),

                            name=topic_name,

                            unit=(
                                getattr(
                                    topic,
                                    "unit",
                                    None
                                )
                            ),

                            priority=(
                                getattr(
                                    topic,
                                    "priority",
                                    "MEDIUM"
                                )
                            ),
                        )


                        existing_names.add(
                            normalized_name
                        )

                        added_count += 1


                    st.session_state[
                        "syllabus_saved"
                    ] = True


                    if added_count > 0:

                        st.success(
                            f"✅ {added_count} topic(s) "
                            f"added successfully."
                        )


                    if skipped_count > 0:

                        st.info(
                            f"ℹ️ {skipped_count} duplicate "
                            f"topic(s) were skipped."
                        )


                    if (
                        added_count == 0
                        and skipped_count == 0
                    ):

                        st.info(
                            "No new topics were available to save."
                        )


                    clear_syllabus_analysis()

                    st.rerun()


                except Exception as error:

                    st.error(
                        "Unable to save the analyzed topics."
                    )

                    st.exception(error)


        with save_col2:

            if st.button(
                "🗑️ Clear Analysis",
                use_container_width=True,
                key="clear_syllabus_analysis_button",
            ):

                clear_syllabus_analysis()

                st.session_state[
                    "syllabus_saved"
                ] = False

                st.rerun()


    # ========================================================
    # SAVED TOPICS
    # ========================================================

    st.divider()

    st.subheader(
        "📚 Saved Topics"
    )


    saved_topics = get_topics(
        selected_subject["id"]
    )


    if not saved_topics:

        st.info(
            "No topics have been saved for this subject yet. "
            "Analyze your syllabus above to create them."
        )

    else:

        st.caption(
            f"{len(saved_topics)} topic(s) saved"
        )


        for index, topic in enumerate(
            saved_topics,
            start=1,
        ):

            topic_name = (
                topic.get(
                    "name"
                )
                or "Unnamed Topic"
            )

            unit = (
                topic.get(
                    "unit"
                )
                or "General"
            )

            priority = (
                topic.get(
                    "priority"
                )
                or "MEDIUM"
            )


            with st.container(
                border=True
            ):

                topic_col1, topic_col2, topic_col3 = (
                    st.columns(
                        [5, 2, 2]
                    )
                )


                with topic_col1:

                    st.markdown(
                        f"**{index}. {topic_name}**"
                    )

                    st.caption(
                        f"Unit: {unit}"
                    )


                with topic_col2:

                    priority_upper = str(
                        priority
                    ).upper()

                    if priority_upper == "HIGH":

                        st.error(
                            "🔥 HIGH"
                        )

                    elif priority_upper == "MEDIUM":

                        st.warning(
                            "🟡 MEDIUM"
                        )

                    else:

                        st.success(
                            "🟢 LOW"
                        )


                with topic_col3:

                    st.caption(
                        "Available in Learn, Quiz, "
                        "Progress and Revision"
                    )


    # ========================================================
    # EDIT SUBJECT
    # ========================================================

    st.divider()

    st.subheader(
        "⚙️ Subject Settings"
    )


    with st.expander(
        f"✏️ Edit {selected_subject['name']}"
    ):

        with st.form(
            "edit_subject_form"
        ):

            new_name = st.text_input(
                "Subject Name",
                value=(
                    selected_subject["name"]
                    or ""
                ),
            )

            new_exam_date = st.text_input(
                "Exam Date",
                value=str(
                    selected_subject["exam_date"]
                    or ""
                ),
            )


            new_daily_hours = st.number_input(
                "Study Hours Per Day",
                min_value=0.5,
                max_value=12.0,
                value=float(
                    selected_subject["daily_hours"]
                    or 2.0
                ),
                step=0.5,
            )


            new_goal = st.text_area(
                "Study Goal",
                value=(
                    selected_subject["goal"]
                    or ""
                ),
                height=100,
            )


            save_changes = st.form_submit_button(
                "💾 Save Changes",
                type="primary",
                use_container_width=True,
            )


            if save_changes:

                cleaned_name = (
                    new_name or ""
                ).strip()


                if not cleaned_name:

                    st.error(
                        "Subject name cannot be empty."
                    )

                else:

                    try:

                        update_subject(

                            subject_id=(
                                selected_subject_id
                            ),

                            name=cleaned_name,

                            exam_date=(
                                new_exam_date.strip()
                            ),

                            daily_hours=(
                                new_daily_hours
                            ),

                            goal=(
                                new_goal or ""
                            ).strip(),
                        )


                        st.success(
                            "✅ Subject updated successfully."
                        )

                        st.rerun()


                    except Exception as error:

                        st.error(
                            "Unable to update the subject."
                        )

                        st.exception(error)


# ============================================================
# NO SELECTED SUBJECT
# ============================================================

else:

    if subjects:

        st.divider()

        st.info(
            "👆 Select a subject above to analyze its syllabus "
            "and manage its learning topics."
        )

    else:

        st.divider()

        st.info(
            "📚 Add your first subject to begin building "
            "your personalized StudyFlow learning path."
        )