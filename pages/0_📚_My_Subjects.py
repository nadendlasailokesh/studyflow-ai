import streamlit as st

from src.database.db import initialize_database
from src.database.repository import (
    create_student,
    create_subject,
    get_student,
    get_subjects,
    update_subject,
    delete_subject
)


# -----------------------------------
# Initialization
# -----------------------------------

initialize_database()

st.set_page_config(
    page_title="My Subjects",
    page_icon="📚",
    layout="wide"
)


# -----------------------------------
# Student Setup
# -----------------------------------

if "student_id" not in st.session_state:

    student = get_student(1)

    if student:

        st.session_state.student_id = student["id"]

    else:

        student_id = create_student(
            name="Student",
            knowledge_level="Beginner"
        )

        st.session_state.student_id = student_id


student_id = st.session_state.student_id


# -----------------------------------
# Page Header
# -----------------------------------

st.title("📚 My Subjects")

st.write(
    "Manage the subjects you are preparing for."
)


# -----------------------------------
# Add Subject
# -----------------------------------

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

                st.success(
                    f"'{name}' added successfully!"
                )

                st.rerun()


st.divider()


# -----------------------------------
# Existing Subjects
# -----------------------------------

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

        with col2:

            if st.button(
                "▶️ Open",
                key=f"open_{subject['id']}",
                use_container_width=True
            ):

                st.session_state.selected_subject_id = (
                    subject["id"]
                )

                st.success(
                    f"Selected: {subject['name']}"
                )

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

                    del st.session_state[
                        "selected_subject_id"
                    ]

                st.rerun()


# -----------------------------------
# Edit Subject
# -----------------------------------

selected_subject_id = st.session_state.get(
    "selected_subject_id"
)


if selected_subject_id:

    selected_subject = next(
        (
            subject
            for subject in subjects
            if subject["id"] == selected_subject_id
        ),
        None
    )

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