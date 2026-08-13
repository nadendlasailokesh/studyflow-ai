import streamlit as st


st.set_page_config(
    page_title="Study Plan",
    page_icon="🎯",
    layout="wide"
)


st.title("🎯 Your Study Plan")

st.write(
    "Plan your learning journey based on your exam date, "
    "syllabus, available time, and current knowledge."
)


# -----------------------------
# Study Setup
# -----------------------------

st.subheader("📚 Study Setup")

col1, col2 = st.columns(2)

with col1:

    subject = st.text_input(
        "Subject",
        placeholder="e.g. Computer Linguistics"
    )

    exam_date = st.date_input(
        "Exam Date"
    )


with col2:

    study_hours = st.number_input(
        "Available study hours per day",
        min_value=0.5,
        max_value=12.0,
        value=2.0,
        step=0.5
    )

    knowledge_level = st.selectbox(
        "Current knowledge level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )


# -----------------------------
# Syllabus
# -----------------------------

st.subheader("📖 Syllabus")

syllabus = st.text_area(
    "Enter your syllabus/topics",
    height=180,
    placeholder="""Example:

Unit 1 - Morphology
Unit 2 - Phonology
Unit 3 - Syntax
Unit 4 - Semantics
Unit 5 - Pragmatics"""
)


# -----------------------------
# Generate Plan
# -----------------------------

if st.button(
    "✨ Generate My Study Plan",
    type="primary",
    use_container_width=True
):

    if not subject:
        st.warning("Please enter your subject.")

    elif not syllabus:
        st.warning("Please enter your syllabus.")

    else:

        st.success(
            "Your study plan will be generated here once "
            "the AI engine is connected."
        )