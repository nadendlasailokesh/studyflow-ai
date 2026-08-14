import streamlit as st

from src.database.db import initialize_database

from src.database.repository import (
    get_topic_mastery_for_student,
    get_quiz_statistics_for_student,
    get_subject_progress,
)

from src.ai.recommendation import (
    get_top_recommendation,
)

from src.ai.recommendation_explanation import (
    generate_recommendation_reasons,
    get_recommendation_summary,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Progress",
    page_icon="📊",
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
        "Please create a student profile first."
    )

    st.stop()


student_id = st.session_state.student_id


# ============================================================
# HEADER
# ============================================================

st.title("📊 Your Learning Progress")

st.write(
    "Track your topic mastery, quiz performance, "
    "and identify what you should study next."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

topics = get_topic_mastery_for_student(
    student_id
)

quiz_stats = get_quiz_statistics_for_student(
    student_id
)

subject_progress = get_subject_progress(
    student_id
)


# ============================================================
# EMPTY STATE
# ============================================================

if not topics:

    st.info(
        "No learning progress is available yet. "
        "Analyze a syllabus and start learning."
    )

    st.stop()


# ============================================================
# OVERALL PROGRESS
# ============================================================

total_topics = len(topics)

overall_progress = (
    sum(
        float(topic["mastery"] or 0)
        for topic in topics
    )
    / total_topics
)


# ============================================================
# QUIZ ACCURACY
# ============================================================

total_questions = int(
    quiz_stats["total_questions"] or 0
)

correct_answers = float(
    quiz_stats["correct_answers"] or 0
)

if total_questions > 0:

    quiz_accuracy = (
        correct_answers
        / total_questions
    ) * 100

else:

    quiz_accuracy = 0.0


# ============================================================
# CONCEPT MASTERY
# ============================================================

concept_mastery = overall_progress


# ============================================================
# QUIZ ATTEMPTS
# ============================================================

quiz_attempts = int(
    quiz_stats["attempts"] or 0
)


# ============================================================
# METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Overall Progress",
        f"{overall_progress:.0f}%",
    )


with col2:

    st.metric(
        "Quiz Accuracy",
        f"{quiz_accuracy:.0f}%",
    )


with col3:

    st.metric(
        "Concept Mastery",
        f"{concept_mastery:.0f}%",
    )


with col4:

    st.metric(
        "Quiz Attempts",
        quiz_attempts,
    )


st.divider()


# ============================================================
# SUBJECT PROGRESS
# ============================================================

st.subheader("📚 Subject Progress")


for subject in subject_progress:

    subject_name = subject["subject_name"]

    mastery = float(
        subject["average_mastery"] or 0
    )

    total_subject_topics = int(
        subject["total_topics"] or 0
    )

    st.write(
        f"**{subject_name} — {mastery:.0f}%**"
    )

    st.progress(
        min(
            max(
                mastery / 100,
                0
            ),
            1
        )
    )

    st.caption(
        f"{total_subject_topics} topic(s)"
    )


st.divider()


# ============================================================
# TOPIC MASTERY
# ============================================================

st.subheader("🧠 Topic Mastery")


for topic in topics:

    topic_name = topic["name"]

    mastery = float(
        topic["mastery"] or 0
    )

    priority = (
        topic.get("priority")
        or "MEDIUM"
    )

    status = (
        topic.get("status")
        or "Not Started"
    )

    unit = (
        topic.get("unit")
        or "General"
    )

    st.write(
        f"**{topic_name}**"
    )

    st.caption(
        f"{unit} • Priority: {priority} • "
        f"Status: {status}"
    )

    st.progress(
        min(
            max(
                mastery / 100,
                0
            ),
            1
        )
    )

    st.write(
        f"Mastery: **{mastery:.0f}%**"
    )

    st.divider()


# ============================================================
# AI ADAPTIVE RECOMMENDATION
# ============================================================

st.subheader("✨ AI Study Recommendation")


# ------------------------------------------------------------
# Generate recommendation
# ------------------------------------------------------------

recommendation = get_top_recommendation(
    topics
)


# ============================================================
# NO RECOMMENDATION
# ============================================================

if recommendation is None:

    st.info(
        "Complete a topic or quiz to generate "
        "an adaptive recommendation."
    )

else:

    recommended_topic = (
        recommendation["topic"]
    )

    progress = (
        recommendation["progress"]
    )

    adaptive_score = float(
        recommendation["adaptive_score"]
    )

    action = (
        recommendation["action"]
    )

    quiz_history = (
        recommendation.get(
            "quiz_stats",
            {}
        )
        or {}
    )

    improvement = float(
        recommendation.get(
            "improvement",
            0.0
        )
        or 0.0
    )

    topic_data = (
        recommendation.get(
            "topic_data",
            {}
        )
        or {}
    )

    mastery = float(
        progress.score_percentage
    )

    priority = (
        topic_data.get("priority")
        or "MEDIUM"
    )


    # ========================================================
    # RECOMMENDED TOPIC
    # ========================================================

    st.markdown(
        f"### 🎯 Next Topic: {recommended_topic}"
    )

    st.caption(
        f"Priority: {priority}"
    )


    # ========================================================
    # RECOMMENDATION METRICS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Mastery",
            f"{mastery:.0f}%"
        )


    with col2:

        historical_accuracy = float(
            quiz_history.get(
                "accuracy",
                0.0
            )
            or 0.0
        )

        st.metric(
            "Quiz Accuracy",
            f"{historical_accuracy:.0f}%"
        )


    with col3:

        attempts = int(
            quiz_history.get(
                "attempts",
                0
            )
            or 0
        )

        st.metric(
            "Quiz Attempts",
            attempts
        )


    with col4:

        st.metric(
            "Adaptive Score",
            f"{adaptive_score:.2f}"
        )


    # ========================================================
    # PHASE 5.3 — EXPLAINABLE RECOMMENDATION
    # ========================================================

    st.markdown(
        "### 🧠 Why was this topic recommended?"
    )

    recommendation_summary = (
        get_recommendation_summary(
            recommendation
        )
    )

    st.info(
        recommendation_summary
    )

    recommendation_reasons = (
        generate_recommendation_reasons(
            recommendation
        )
    )

    if recommendation_reasons:

        for reason in recommendation_reasons:

            st.markdown(
                f"- {reason}"
            )

    else:

        st.caption(
            "No detailed explanation is available yet."
        )


    # ========================================================
    # PERFORMANCE TREND
    # ========================================================

    st.markdown(
        "#### 📈 Performance Trend"
    )


    if improvement > 0:

        st.success(
            f"📈 Improving by **{improvement:.1f}%** "
            "compared with the previous quiz."
        )

    elif improvement < 0:

        st.error(
            f"📉 Performance decreased by "
            f"**{abs(improvement):.1f}%** "
            "compared with the previous quiz."
        )

    else:

        if attempts >= 2:

            st.info(
                "📊 No significant performance change "
                "was detected between recent quizzes."
            )

        else:

            st.info(
                "📊 Not enough quiz history to determine "
                "a performance trend yet."
            )


    # ========================================================
    # RECOMMENDED ACTION
    # ========================================================

    st.markdown(
        "#### 🧠 Recommended Action"
    )


    if action == "RELEARN":

        st.error(
            f"""
### 📖 Relearn: {recommended_topic}

Your current mastery is only
**{mastery:.0f}%**.

Recommended steps:

1. Go to **📖 Learn**
2. Study **{recommended_topic}**
3. Review the important concepts
4. Take another practice quiz
"""
        )


    elif action == "REVISE":

        st.warning(
            f"""
### 🔄 Revise: {recommended_topic}

Your current mastery is
**{mastery:.0f}%**.

You have a reasonable understanding,
but this topic needs revision.

Recommended steps:

1. Review the learning material
2. Practice important concepts
3. Take another quiz
"""
        )


    elif action == "MOVE_FORWARD":

        st.success(
            f"""
### 🚀 Move Forward

Your understanding of
**{recommended_topic}**
is strong.

You can continue to another topic.
"""
        )


    else:

        st.info(
            f"""
### 📚 Continue Studying

Continue studying
**{recommended_topic}**
according to your adaptive study plan.
"""
        )


# ============================================================
# NEXT ACTION
# ============================================================

st.divider()

st.subheader("🎯 What should you do next?")


if recommendation is None:

    st.info(
        "Complete a topic or quiz to generate "
        "an adaptive recommendation."
    )

else:

    recommended_topic = (
        recommendation["topic"]
    )

    action = (
        recommendation["action"]
    )


    if action == "RELEARN":

        st.info(
            f"📖 Go to Learn and relearn "
            f"**{recommended_topic}**."
        )


    elif action == "REVISE":

        st.info(
            f"🔄 Revise **{recommended_topic}** "
            "and attempt another quiz."
        )


    elif action == "MOVE_FORWARD":

        st.info(
            f"🚀 You can move forward after "
            f"completing **{recommended_topic}**."
        )


    else:

        st.info(
            f"📚 Continue studying "
            f"**{recommended_topic}**."
        )