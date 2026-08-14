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
    get_topics
)

from src.ai.quiz import (
    generate_quiz
)

from src.ai.quiz_evaluator import (
    evaluate_quiz
)

from src.ai.progress import (
    get_learning_recommendation
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Practice Quiz | StudyFlow AI",
    page_icon="❓",
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
        "Please create a student profile first."
    )

    st.stop()


student_id = st.session_state.student_id


# ============================================================
# HEADER
# ============================================================

st.title("❓ Practice Quiz")

st.write(
    "Test your understanding with AI-generated "
    "questions based on your syllabus topics."
)

st.divider()


# ============================================================
# LOAD SUBJECTS
# ============================================================

subjects = get_all_subjects(
    student_id
)


if not subjects:

    st.info(
        "Please create a subject first from "
        "📚 My Subjects."
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
        "Please analyze the syllabus first."
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
    f"📚 {selected_subject_name} • "
    f"📖 {topic_unit}"
)


st.divider()


# ============================================================
# QUIZ SETTINGS
# ============================================================

st.subheader("⚙️ Quiz Settings")


col1, col2 = st.columns(2)


with col1:

    difficulty = st.selectbox(
        "🎯 Difficulty",
        [
            "EASY",
            "MEDIUM",
            "HARD"
        ],
        index=1
    )


with col2:

    number_of_questions = st.selectbox(
        "📝 Number of Questions",
        [5, 10],
        index=0
    )


st.divider()


# ============================================================
# TOPIC INFORMATION
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Priority",
        selected_topic["priority"]
    )


with col2:

    st.metric(
        "Mastery",
        f"{selected_topic['mastery']:.0f}%"
    )


with col3:

    st.metric(
        "Status",
        selected_topic["status"]
    )


st.divider()


# ============================================================
# GENERATE QUIZ
# ============================================================

if st.button(
    "✨ Generate Quiz",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "🧠 StudyFlow AI is creating your quiz..."
    ):

        try:

            quiz = generate_quiz(

                subject_name=selected_subject_name,

                unit=topic_unit,

                topic=selected_topic_name,

                difficulty=difficulty,

                number_of_questions=number_of_questions
            )


            st.session_state.quiz = quiz

            st.session_state.quiz_topic_id = (
                selected_topic["id"]
            )

            st.session_state.quiz_topic_name = (
                selected_topic_name
            )

            st.session_state.quiz_submitted = False

            st.session_state.quiz_result = None

            st.success(
                "✅ Quiz generated successfully!"
            )

        except Exception as error:

            st.error(
                "Unable to generate the quiz."
            )

            st.exception(error)


# ============================================================
# DISPLAY QUIZ
# ============================================================

if "quiz" in st.session_state:

    quiz = st.session_state.quiz

    st.divider()

    st.subheader(
        f"📝 {quiz.topic}"
    )

    st.write(
        f"Difficulty: **{quiz.difficulty}**"
    )

    st.write(
        f"Questions: **{len(quiz.questions)}**"
    )


    # --------------------------------------------------------
    # QUIZ FORM
    # --------------------------------------------------------

    with st.form("quiz_form"):

        answers = {}


        for index, question in enumerate(
            quiz.questions
        ):

            st.markdown(
                f"### Question {index + 1}"
            )

            st.write(
                question.question
            )

            answers[index] = st.radio(

                "Choose your answer:",

                question.options,

                key=f"quiz_answer_{index}",

                index=None
            )

            st.divider()


        submitted = st.form_submit_button(
            "✅ Submit Quiz",
            type="primary",
            use_container_width=True
        )


    # ========================================================
    # EVALUATE QUIZ
    # ========================================================

    if submitted:

        unanswered = [

            index + 1

            for index, answer in answers.items()

            if answer is None
        ]


        if unanswered:

            st.warning(
                "Please answer all questions before "
                "submitting the quiz."
            )

        else:

            with st.spinner(
                "🧠 Evaluating your answers..."
            ):

                try:

                    result = evaluate_quiz(

                        quiz=quiz,

                        answers=answers,

                        topic_id=(
                            st.session_state.quiz_topic_id
                        )
                    )


                    st.session_state.quiz_result = (
                        result
                    )

                    st.session_state.quiz_submitted = (
                        True
                    )


                except Exception as error:

                    st.error(
                        "Unable to evaluate the quiz."
                    )

                    st.exception(error)


# ============================================================
# QUIZ RESULT
# ============================================================

if (
    st.session_state.get(
        "quiz_submitted",
        False
    )
):

    result = st.session_state.quiz_result

    st.divider()

    st.subheader(
        "📊 Quiz Result"
    )


    score = result[
        "score_percentage"
    ]

    correct = result[
        "correct_answers"
    ]

    total = result[
        "total_questions"
    ]


    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Score",
            f"{score:.0f}%"
        )


    with col2:

        st.metric(
            "Correct",
            f"{correct}/{total}"
        )


    with col3:

        progress = result.get(
            "progress"
        )

        if progress:

            st.metric(
                "Status",
                progress.status
            )

        else:

            st.metric(
                "Status",
                "Saved"
            )


    # --------------------------------------------------------
    # SCORE MESSAGE
    # --------------------------------------------------------

    if score >= 80:

        st.success(
            "🎉 Excellent! You have a strong "
            "understanding of this topic."
        )

    elif score >= 50:

        st.warning(
            "👍 Good effort! Review the important "
            "concepts once more."
        )

    else:

        st.error(
            "📖 This topic needs more attention. "
            "Go back to Learn and study it again."
        )


    # ========================================================
    # QUESTION RESULTS
    # ========================================================

    st.subheader(
        "📋 Question Review"
    )


    for index, evaluation in enumerate(
        result["results"]
    ):

        if evaluation.is_correct:

            st.success(
                f"Question {index + 1}: "
                f"Correct ✅"
            )

        else:

            st.error(
                f"Question {index + 1}: "
                f"Incorrect ❌"
            )


        st.write(
            evaluation.feedback
        )


        if not evaluation.is_correct:

            st.write(
                f"**Correct answer:** "
                f"{evaluation.correct_answer}"
            )


        st.info(
            f"**Explanation:** "
            f"{evaluation.explanation}"
        )


    # ========================================================
    # ADAPTIVE RECOMMENDATION
    # ========================================================

    if result.get("progress"):

        progress = result[
            "progress"
        ]

        recommendation = (
            get_learning_recommendation(
                progress
            )
        )


        st.divider()

        st.subheader(
            "🧠 What should you do next?"
        )


        if recommendation["action"] == "MOVE_FORWARD":

            st.success(
                "🚀 Move Forward"
            )

        elif recommendation["action"] == "REVISE":

            st.warning(
                "🔄 Revise"
            )

        else:

            st.error(
                "📖 Relearn"
            )


        st.write(
            recommendation["message"]
        )


        # ----------------------------------------------------
        # NEXT STEP
        # ----------------------------------------------------

        if recommendation["action"] == "RELEARN":

            st.info(
                "Go to 📖 Learn and study this topic "
                "again before taking another quiz."
            )

        elif recommendation["action"] == "REVISE":

            st.info(
                "Review the key concepts and examples "
                "before continuing."
            )

        else:

            st.success(
                "You are ready to continue to the "
                "next important topic."
            )