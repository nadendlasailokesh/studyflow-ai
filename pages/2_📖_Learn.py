# ============================================================
# PROJECT ROOT FIX
# ============================================================

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.database.db import initialize_database
from src.database.repository import (
    get_all_subjects,
    get_topics,
    save_learning_session
)

from src.ai.learning import generate_learning_content


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Learn | StudyFlow AI",
    page_icon="📖",
    layout="wide"
)


# ============================================================
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# SESSION STATE
# ============================================================

if "student_id" not in st.session_state:

    st.warning(
        "Please create a student profile first from My Subjects."
    )

    st.stop()


student_id = st.session_state.student_id


# ============================================================
# HEADER
# ============================================================

st.title("📖 Learn")

st.write(
    "Understand your syllabus topics using "
    "AI-powered explanations, examples, and "
    "exam-focused learning material."
)

st.divider()


# ============================================================
# LOAD SUBJECTS
# ============================================================

subjects = get_all_subjects(student_id)

if not subjects:

    st.info(
        "Please create a subject first from 📚 My Subjects."
    )

    st.stop()


# ============================================================
# SUBJECT SELECTION
# ============================================================

subject_options = {
    subject["name"]: subject["id"]
    for subject in subjects
}

selected_subject_name = st.selectbox(
    "📚 Choose Subject",
    list(subject_options.keys())
)

selected_subject_id = subject_options[
    selected_subject_name
]


# ============================================================
# LOAD TOPICS
# ============================================================

topics = get_topics(
    selected_subject_id
)

if not topics:

    st.warning(
        "No topics are available for this subject. "
        "Please analyze and save the syllabus first."
    )

    st.stop()


# ============================================================
# TOPIC SELECTION
# ============================================================

topic_options = {
    topic["name"]: topic
    for topic in topics
}

selected_topic_name = st.selectbox(
    "📘 Choose Topic",
    list(topic_options.keys())
)

selected_topic = topic_options[
    selected_topic_name
]


topic_unit = (
    selected_topic["unit"]
    or "General"
)


st.caption(
    f"📚 {selected_subject_name}  •  📖 {topic_unit}"
)


# ============================================================
# CLEAR OLD CONTENT WHEN TOPIC CHANGES
# ============================================================

current_selection = (
    selected_subject_id,
    selected_topic["id"]
)

previous_selection = st.session_state.get(
    "learning_selection"
)

if previous_selection != current_selection:

    st.session_state.pop(
        "learning_content",
        None
    )

    st.session_state.pop(
        "learning_topic_id",
        None
    )

    st.session_state.learning_selection = (
        current_selection
    )


st.divider()


# ============================================================
# TOPIC INFORMATION
# ============================================================

st.subheader(
    f"📘 {selected_topic_name}"
)

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Priority",
        selected_topic["priority"]
    )


with col2:

    mastery = selected_topic["mastery"] or 0

    st.metric(
        "Mastery",
        f"{mastery:.0f}%"
    )


with col3:

    st.metric(
        "Status",
        selected_topic["status"] or "NOT STARTED"
    )


st.divider()


# ============================================================
# PREREQUISITES
# ============================================================

prerequisites = []

raw_prerequisites = selected_topic["prerequisites"]

if raw_prerequisites:

    if isinstance(raw_prerequisites, list):

        prerequisites = raw_prerequisites

    else:

        prerequisites = [
            str(raw_prerequisites)
        ]


if prerequisites:

    st.info(
        "🔗 Prerequisites: "
        + ", ".join(prerequisites)
    )


# ============================================================
# GENERATE CONTENT
# ============================================================

st.subheader(
    "🧠 AI Learning Material"
)

st.write(
    "Generate structured study material specifically "
    "for this syllabus topic."
)


generate = st.button(
    "✨ Generate Learning Content",
    type="primary",
    use_container_width=True
)


if generate:

    with st.spinner(
        "🧠 StudyFlow AI is preparing your learning material..."
    ):

        try:

            content = generate_learning_content(

                subject_name=selected_subject_name,

                unit=topic_unit,

                topic=selected_topic_name,

                prerequisites=prerequisites
            )


            # ------------------------------------------------
            # Save learning session
            # ------------------------------------------------

            try:

                save_learning_session(

                    topic_id=selected_topic["id"],

                    mode="AI_LEARNING",

                    duration_minutes=(
                        content.estimated_minutes
                    )
                )

            except Exception as session_error:

                # Do not prevent learning content
                # from being displayed.
                print(
                    f"Learning session save failed: "
                    f"{session_error}"
                )


            # ------------------------------------------------
            # Store content
            # ------------------------------------------------

            st.session_state.learning_content = (
                content
            )

            st.session_state.learning_topic_id = (
                selected_topic["id"]
            )

            st.success(
                "Learning material generated successfully!"
            )


        except Exception as error:

            st.error(
                "Unable to generate learning content."
            )

            st.exception(error)


# ============================================================
# DISPLAY CONTENT
# ============================================================

if (
    "learning_content" in st.session_state
    and
    st.session_state.get("learning_topic_id")
    == selected_topic["id"]
):

    content = st.session_state.learning_content

    st.divider()

    # ========================================================
    # LEARNING TIME
    # ========================================================

    st.info(
        f"⏱️ Estimated learning time: "
        f"{content.estimated_minutes} minutes"
    )


    # ========================================================
    # SIMPLE EXPLANATION
    # ========================================================

    st.subheader(
        "💡 Simple Explanation"
    )

    st.write(
        content.simple_explanation
    )


    # ========================================================
    # KEY CONCEPTS
    # ========================================================

    st.subheader(
        "🔑 Key Concepts"
    )

    if content.key_concepts:

        for concept in content.key_concepts:

            st.markdown(
                f"- {concept}"
            )

    else:

        st.caption(
            "No key concepts were generated."
        )


    # ========================================================
    # EXAMPLES
    # ========================================================

    st.subheader(
        "📝 Examples"
    )

    if content.examples:

        for index, example in enumerate(
            content.examples,
            start=1
        ):

            st.markdown(
                f"**Example {index}:** {example}"
            )

    else:

        st.caption(
            "No examples were generated."
        )


    # ========================================================
    # EXAM DEFINITION
    # ========================================================

    st.subheader(
        "🎯 Exam-Ready Definition"
    )

    st.success(
        content.exam_definition
    )


    # ========================================================
    # IMPORTANT POINTS
    # ========================================================

    st.subheader(
        "⭐ Important Exam Points"
    )

    if content.important_points:

        for point in content.important_points:

            st.markdown(
                f"- {point}"
            )

    else:

        st.caption(
            "No important points were generated."
        )


    # ========================================================
    # COMMON MISTAKES
    # ========================================================

    st.subheader(
        "⚠️ Common Mistakes"
    )

    if content.common_mistakes:

        for mistake in content.common_mistakes:

            st.markdown(
                f"- {mistake}"
            )

    else:

        st.caption(
            "No common mistakes were generated."
        )


    # ========================================================
    # MEMORY TIP
    # ========================================================

    st.subheader(
        "🧠 Memory Tip"
    )

    st.info(
        content.memory_tip
    )


    # ========================================================
    # QUICK CHECK
    # ========================================================

    st.divider()

    st.subheader(
        "❓ Quick Check"
    )

    st.write(
        content.quick_check_question
    )


    if st.button(
        "👁️ Reveal Answer",
        key=f"reveal_{selected_topic['id']}"
    ):

        st.success(
            f"Answer: {content.quick_check_answer}"
        )


    # ========================================================
    # FINISHED
    # ========================================================

    st.divider()

    st.success(
        "✅ Learning session complete. "
        "Take a quiz next to check your understanding."
    )