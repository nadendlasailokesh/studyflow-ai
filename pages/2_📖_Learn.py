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
    get_all_subjects,
    get_topics,
    save_learning_session,
)

from src.ai.learning import (
    generate_learning_content,
)

from src.ai.learning_navigation import (
    get_recommended_learning_topic,
)

from src.ai.recommendation_router import (
    get_recommended_topic,
)

from src.ai.recommendation_actions import (
    get_recommendation_action,
    get_action_label,
    should_open_learning,
    should_open_quiz,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Learn | StudyFlow AI",
    page_icon="📖",
    layout="wide",
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
# READ LEARNING TRANSITION FROM PROGRESS PAGE
# ============================================================
#
# This is the MOST IMPORTANT FIX.
#
# Progress.py creates:
#
# learning_transition_context = {
#     subject_id,
#     subject_name,
#     topic_id,
#     topic_name
# }
#
# Learn.py must use this BEFORE normal recommendation logic.
# ============================================================

transition_context = st.session_state.get(
    "learning_transition_context"
)

transition_topic_id = None
transition_subject_id = None
transition_topic_name = None
transition_subject_name = None


if isinstance(
    transition_context,
    dict
):

    transition_topic_id = (
        transition_context.get(
            "topic_id"
        )
    )

    transition_subject_id = (
        transition_context.get(
            "subject_id"
        )
    )

    transition_topic_name = (
        transition_context.get(
            "topic_name"
        )
    )

    transition_subject_name = (
        transition_context.get(
            "subject_name"
        )
    )


# ============================================================
# LOAD SUBJECTS
# ============================================================

subjects = get_all_subjects(
    student_id
)

if not subjects:

    st.info(
        "Please create a subject first from 📚 My Subjects."
    )

    st.stop()


# ============================================================
# SUBJECT LOOKUP
# ============================================================

subject_by_id = {
    subject["id"]: subject
    for subject in subjects
}


subject_options = {
    subject["name"]: subject["id"]
    for subject in subjects
}


subject_names = list(
    subject_options.keys()
)


# ============================================================
# ADAPTIVE RECOMMENDATION
# ============================================================

recommended_topic = get_recommended_topic(
    st.session_state
)


recommended_topic_id = None
recommended_action = None


if isinstance(
    recommended_topic,
    dict
):

    recommended_topic_id = (
        recommended_topic.get(
            "topic_id"
        )
    )

    raw_action = (
        recommended_topic.get(
            "action"
        )
    )

    if raw_action:

        recommended_action = (
            get_recommendation_action(
                raw_action
            )
        )


# ============================================================
# RECOMMENDED LEARNING CONTEXT
# ============================================================

recommended_learning = (
    get_recommended_learning_topic(
        st.session_state
    )
)


# ============================================================
# DETERMINE TARGET SUBJECT
# ============================================================
#
# Priority:
#
# 1. Explicit Progress → Learn transition
# 2. Learning recommendation
# 3. Recommendation router
# 4. First subject
# ============================================================

target_subject_id = None
target_subject_name = None


# ------------------------------------------------------------
# 1. Progress → Learn transition
# ------------------------------------------------------------

if transition_subject_id in subject_by_id:

    target_subject_id = (
        transition_subject_id
    )

    target_subject_name = (
        subject_by_id[
            transition_subject_id
        ]["name"]
    )


elif (
    transition_subject_name
    and
    transition_subject_name in subject_options
):

    target_subject_name = (
        transition_subject_name
    )

    target_subject_id = (
        subject_options[
            transition_subject_name
        ]
    )


# ------------------------------------------------------------
# 2. Recommended learning context
# ------------------------------------------------------------

if target_subject_id is None:

    if isinstance(
        recommended_learning,
        dict
    ):

        learning_subject_id = (
            recommended_learning.get(
                "subject_id"
            )
        )

        learning_subject_name = (
            recommended_learning.get(
                "subject_name"
            )
        )

        if learning_subject_id in subject_by_id:

            target_subject_id = (
                learning_subject_id
            )

            target_subject_name = (
                subject_by_id[
                    learning_subject_id
                ]["name"]
            )

        elif (
            learning_subject_name
            and
            learning_subject_name in subject_options
        ):

            target_subject_name = (
                learning_subject_name
            )

            target_subject_id = (
                subject_options[
                    learning_subject_name
                ]
            )


# ------------------------------------------------------------
# 3. Recommendation router
# ------------------------------------------------------------

if (
    target_subject_id is None
    and
    recommended_topic_id is not None
):

    for subject in subjects:

        subject_topics = get_topics(
            subject["id"]
        )

        for topic in subject_topics:

            if (
                topic["id"]
                ==
                recommended_topic_id
            ):

                target_subject_id = (
                    subject["id"]
                )

                target_subject_name = (
                    subject["name"]
                )

                break

        if target_subject_id is not None:
            break


# ------------------------------------------------------------
# 4. Fallback
# ------------------------------------------------------------

if target_subject_id is None:

    target_subject_id = (
        subjects[0]["id"]
    )

    target_subject_name = (
        subjects[0]["name"]
    )


# ============================================================
# SUBJECT SELECTBOX
# ============================================================

subject_index = 0


if target_subject_name in subject_names:

    subject_index = (
        subject_names.index(
            target_subject_name
        )
    )


selected_subject_name = st.selectbox(
    "📚 Choose Subject",
    subject_names,
    index=subject_index,
    key="learn_subject_selector",
)


selected_subject_id = (
    subject_options[
        selected_subject_name
    ]
)


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
# DETERMINE TARGET TOPIC
# ============================================================
#
# Priority:
#
# 1. Progress → Learn exact topic ID
# 2. Recommended learning exact topic ID
# 3. Recommendation router topic ID
# 4. Topic name
# 5. First topic
# ============================================================

target_topic_id = None
target_topic_name = None


# ------------------------------------------------------------
# 1. Explicit Progress → Learn transition
# ------------------------------------------------------------

if transition_topic_id is not None:

    target_topic_id = (
        transition_topic_id
    )

    target_topic_name = (
        transition_topic_name
    )


# ------------------------------------------------------------
# 2. Recommended learning
# ------------------------------------------------------------

elif isinstance(
    recommended_learning,
    dict
):

    target_topic_id = (
        recommended_learning.get(
            "topic_id"
        )
    )

    target_topic_name = (
        recommended_learning.get(
            "topic_name"
        )
    )


# ------------------------------------------------------------
# 3. Recommendation router
# ------------------------------------------------------------

elif recommended_topic_id is not None:

    target_topic_id = (
        recommended_topic_id
    )


# ============================================================
# FIND TOPIC INDEX
# ============================================================

default_topic_index = 0

found_target_topic = False


if target_topic_id is not None:

    for index, topic in enumerate(topics):

        if (
            topic["id"]
            ==
            target_topic_id
        ):

            default_topic_index = index
            found_target_topic = True

            break


# ------------------------------------------------------------
# Fallback to topic name
# ------------------------------------------------------------

if (
    not found_target_topic
    and
    target_topic_name
):

    for index, topic in enumerate(topics):

        if (
            topic["name"]
            ==
            target_topic_name
        ):

            default_topic_index = index
            found_target_topic = True

            target_topic_id = (
                topic["id"]
            )

            break


# ============================================================
# TOPIC SELECTBOX
# ============================================================

topic_names = [
    topic["name"]
    for topic in topics
]


selected_topic_name = st.selectbox(
    "📘 Choose Topic",
    topic_names,
    index=default_topic_index,
    key="learn_topic_selector",
)


# ============================================================
# GET SELECTED TOPIC
# ============================================================

selected_topic = None


for topic in topics:

    if (
        topic["name"]
        ==
        selected_topic_name
    ):

        selected_topic = topic

        break


if selected_topic is None:

    st.error(
        "Unable to find the selected topic."
    )

    st.stop()


# ============================================================
# CONSUME TRANSITION CONTEXT
# ============================================================
#
# Do this AFTER the correct topic has been selected.
#
# This prevents the context from being used again on every
# future rerun.
# ============================================================

if isinstance(
    transition_context,
    dict
):

    st.session_state.pop(
        "learning_transition_context",
        None
    )


# ============================================================
# TOPIC INFORMATION
# ============================================================

topic_unit = (
    selected_topic.get("unit")
    or "General"
)


st.caption(
    f"📚 {selected_subject_name} • 📖 {topic_unit}"
)


# ============================================================
# DETERMINE RECOMMENDED TOPIC
# ============================================================

is_recommended_topic = False


if recommended_topic_id is not None:

    is_recommended_topic = (
        selected_topic["id"]
        ==
        recommended_topic_id
    )


if (
    transition_topic_id is not None
    and
    selected_topic["id"]
    ==
    transition_topic_id
):

    is_recommended_topic = True


# ============================================================
# CURRENT RECOMMENDATION ACTION
# ============================================================

current_recommendation_action = (
    "CONTINUE"
)


if is_recommended_topic:

    if isinstance(
        recommended_learning,
        dict
    ):

        current_recommendation_action = (
            recommended_learning.get(
                "action"
            )
            or recommended_action
            or "CONTINUE"
        )

    elif recommended_action:

        current_recommendation_action = (
            recommended_action
        )


current_recommendation_action = (
    get_recommendation_action(
        current_recommendation_action
    )
)


# ============================================================
# RECOMMENDATION NOTICE
# ============================================================

if is_recommended_topic:

    st.success(
        f"""
🎯 **AI Recommended Topic**

Study **{selected_topic_name}** according to
your adaptive learning plan.
"""
    )

    st.info(
        f"🎯 Recommended action: "
        f"**{get_action_label(current_recommendation_action)}**"
    )


# ============================================================
# ACTION GUIDANCE
# ============================================================

if is_recommended_topic:

    if current_recommendation_action == "RELEARN":

        st.warning(
            "📖 **Relearn this topic carefully.** "
            "Your current mastery indicates that you need "
            "a stronger understanding before moving forward."
        )

    elif current_recommendation_action == "REVISE":

        st.warning(
            "🔄 **Review this topic before taking the quiz.** "
            "Focus on key concepts and common mistakes."
        )

    elif current_recommendation_action == "MOVE_FORWARD":

        st.success(
            "🚀 **You are ready to move forward.** "
            "This topic does not require another full "
            "learning session."
        )

    else:

        st.info(
            "📚 **Continue studying this topic** "
            "according to your adaptive study plan."
        )


# ============================================================
# RECOMMENDATION EXPLANATION
# ============================================================

if is_recommended_topic:

    with st.expander(
        "🧠 Why am I studying this topic?"
    ):

        priority = (
            selected_topic.get(
                "priority"
            )
            or "MEDIUM"
        )

        mastery = float(
            selected_topic.get(
                "mastery"
            )
            or 0
        )

        st.write(
            f"StudyFlow AI selected "
            f"**{selected_topic_name}** because it is "
            "currently one of the most useful topics "
            "for your adaptive study plan."
        )

        st.write(
            f"⭐ **Priority:** {priority}"
        )

        st.write(
            f"📊 **Current mastery:** "
            f"{mastery:.0f}%"
        )

        st.write(
            f"🎯 **Recommended action:** "
            f"{get_action_label(current_recommendation_action)}"
        )


# ============================================================
# CLEAR LEARNING CONTENT WHEN TOPIC CHANGES
# ============================================================

current_selection = (
    selected_subject_id,
    selected_topic["id"],
)


previous_selection = (
    st.session_state.get(
        "learning_selection"
    )
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

    st.session_state.pop(
        "learning_session_context",
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
        selected_topic.get(
            "priority"
        )
        or "MEDIUM",
    )


with col2:

    mastery = (
        selected_topic.get(
            "mastery"
        )
        or 0
    )

    st.metric(
        "Mastery",
        f"{float(mastery):.0f}%"
    )


with col3:

    st.metric(
        "Status",
        selected_topic.get(
            "status"
        )
        or "NOT STARTED"
    )


st.divider()


# ============================================================
# PREREQUISITES
# ============================================================

prerequisites = []

raw_prerequisites = (
    selected_topic.get(
        "prerequisites"
    )
)


if raw_prerequisites:

    if isinstance(
        raw_prerequisites,
        list
    ):

        prerequisites = (
            raw_prerequisites
        )

    else:

        prerequisites = [
            str(raw_prerequisites)
        ]


if prerequisites:

    st.info(
        "🔗 Prerequisites: "
        + ", ".join(
            str(item)
            for item in prerequisites
        )
    )


# ============================================================
# ADAPTIVE LEARNING GUIDANCE
# ============================================================

if is_recommended_topic:

    if should_open_learning(
        current_recommendation_action
    ):

        if current_recommendation_action == "RELEARN":

            st.caption(
                "📖 Complete the learning material carefully "
                "before attempting the quiz."
            )

        elif current_recommendation_action == "REVISE":

            st.caption(
                "🔄 Review the learning material and focus "
                "on weak concepts."
            )

        else:

            st.caption(
                "📚 Continue learning this topic."
            )


    if should_open_quiz(
        current_recommendation_action
    ):

        st.caption(
            "📝 After learning, take a practice quiz to "
            "measure your understanding."
        )


# ============================================================
# GENERATE LEARNING CONTENT
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
    use_container_width=True,
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

                prerequisites=prerequisites,
            )


            # ------------------------------------------------
            # SAVE LEARNING SESSION
            # ------------------------------------------------

            try:

                save_learning_session(

                    topic_id=selected_topic["id"],

                    mode="AI_LEARNING",

                    duration_minutes=(
                        content.estimated_minutes
                    ),
                )

            except Exception as session_error:

                print(
                    "Learning session save failed: "
                    f"{session_error}"
                )


            # ------------------------------------------------
            # STORE CONTENT
            # ------------------------------------------------

            st.session_state.learning_content = (
                content
            )

            st.session_state.learning_topic_id = (
                selected_topic["id"]
            )


            # ------------------------------------------------
            # STORE LEARNING CONTEXT
            # ------------------------------------------------

            st.session_state.learning_session_context = {

                "student_id": student_id,

                "subject_id": selected_subject_id,

                "subject_name": selected_subject_name,

                "topic_id": selected_topic["id"],

                "topic_name": selected_topic_name,

                "unit": topic_unit,

                "recommended": is_recommended_topic,

                "action": current_recommendation_action,

            }


            # ------------------------------------------------
            # LEARNING → QUIZ CONTEXT
            # ------------------------------------------------

            st.session_state.quiz_navigation_context = {

                "student_id": student_id,

                "subject_id": selected_subject_id,

                "subject_name": selected_subject_name,

                "topic_id": selected_topic["id"],

                "topic_name": selected_topic_name,

                "unit": topic_unit,

                "source": "LEARNING_SESSION",

                "learning_completed": True,

            }


            st.success(
                "Learning material generated successfully!"
            )


        except Exception as error:

            st.error(
                "Unable to generate learning content."
            )

            st.exception(error)


# ============================================================
# DISPLAY LEARNING CONTENT
# ============================================================

if (
    "learning_content"
    in st.session_state
    and
    st.session_state.get(
        "learning_topic_id"
    )
    ==
    selected_topic["id"]
):

    content = (
        st.session_state.learning_content
    )

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

    for concept in (
        content.key_concepts or []
    ):

        st.markdown(
            f"- {concept}"
        )


    # ========================================================
    # EXAMPLES
    # ========================================================

    st.subheader(
        "📝 Examples"
    )

    for index, example in enumerate(
        content.examples or [],
        start=1
    ):

        st.markdown(
            f"**Example {index}:** {example}"
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

    for point in (
        content.important_points or []
    ):

        st.markdown(
            f"- {point}"
        )


    # ========================================================
    # COMMON MISTAKES
    # ========================================================

    st.subheader(
        "⚠️ Common Mistakes"
    )

    for mistake in (
        content.common_mistakes or []
    ):

        st.markdown(
            f"- {mistake}"
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
        key=f"reveal_{selected_topic['id']}",
    ):

        st.success(
            f"Answer: "
            f"{content.quick_check_answer}"
        )


    # ========================================================
    # LEARNING COMPLETE
    # ========================================================

    st.divider()

    st.success(
        "✅ Learning session complete!"
    )


    # ========================================================
    # LEARNING → QUIZ
    # ========================================================

    st.subheader(
        "📝 Ready to Test Yourself?"
    )

    st.write(
        "Take a practice quiz on this exact topic. "
        "Your subject and topic will be carried "
        "automatically to the quiz."
    )


    # --------------------------------------------------------
    # Ensure quiz context exists
    # --------------------------------------------------------

    quiz_context = {
        "student_id": student_id,

        "subject_id": selected_subject_id,

        "subject_name": selected_subject_name,

        "topic_id": selected_topic["id"],

        "topic_name": selected_topic_name,

        "unit": topic_unit,

        "source": "LEARNING_SESSION",

        "learning_completed": True,
    }


    st.session_state.quiz_navigation_context = (
        quiz_context
    )


    # --------------------------------------------------------
    # Quiz button
    # --------------------------------------------------------

    if st.button(
        "📝 Take Practice Quiz",
        type="primary",
        use_container_width=True,
        key=f"quiz_{selected_topic['id']}",
    ):

        st.session_state.quiz_transition_context = {

            "student_id": student_id,

            "subject_id": selected_subject_id,

            "subject_name": selected_subject_name,

            "topic_id": selected_topic["id"],

            "topic_name": selected_topic_name,

            "unit": topic_unit,

            "recommended": is_recommended_topic,

            "action": current_recommendation_action,
        }

        st.session_state.quiz_opened_from_learning = True

        # IMPORTANT:
        # Only ONE switch_page call.
        st.switch_page(
            "pages/4_❓_Practice_Quiz.py"
        )


    # ========================================================
    # ADAPTIVE NEXT STEP
    # ========================================================

    if should_open_quiz(
        current_recommendation_action
    ):

        st.info(
            "🎯 **Recommended next step:** "
            "Take the practice quiz to measure your "
            "understanding and update your mastery."
        )

    else:

        st.info(
            "📚 Continue studying according to "
            "your adaptive study plan."
        )