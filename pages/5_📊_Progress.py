import streamlit as st

from src.database.db import initialize_database
from src.database.repository import (
    get_topic_mastery_for_student,
    get_quiz_statistics_for_student,
    get_subject_progress
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Progress",
    page_icon="📊",
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


overall_progress = sum(
    float(topic["mastery"] or 0)
    for topic in topics
) / total_topics


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

    quiz_accuracy = 0


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
        f"{overall_progress:.0f}%"
    )


with col2:

    st.metric(
        "Quiz Accuracy",
        f"{quiz_accuracy:.0f}%"
    )


with col3:

    st.metric(
        "Concept Mastery",
        f"{concept_mastery:.0f}%"
    )


with col4:

    st.metric(
        "Quiz Attempts",
        quiz_attempts
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
        min(max(mastery / 100, 0), 1)
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
        topic["priority"]
        or "MEDIUM"
    )

    status = (
        topic["status"]
        or "Not Started"
    )

    unit = (
        topic["unit"]
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
        min(max(mastery / 100, 0), 1)
    )

    st.write(
        f"Mastery: **{mastery:.0f}%**"
    )

    st.divider()


# ============================================================
# FIND WEAKEST TOPIC
# ============================================================

weakest_topic = min(
    topics,
    key=lambda topic: float(
        topic["mastery"] or 0
    )
)


weakest_name = weakest_topic["name"]

weakest_mastery = float(
    weakest_topic["mastery"] or 0
)

weakest_status = (
    weakest_topic["status"]
    or "Not Started"
)


# ============================================================
# AI RECOMMENDATION
# ============================================================

st.subheader("✨ Study Recommendation")


if weakest_mastery < 50:

    st.error(
        f"""
### 📖 Relearn: {weakest_name}

Your current mastery is only
**{weakest_mastery:.0f}%**.

Recommended action:

1. Go to **📖 Learn**
2. Review **{weakest_name}**
3. Understand the key concepts
4. Take another practice quiz
"""
    )

elif weakest_mastery < 80:

    st.warning(
        f"""
### 🔄 Revise: {weakest_name}

Your current mastery is
**{weakest_mastery:.0f}%**.

You have a reasonable understanding,
but this topic needs revision.

Recommended action:

- Review the learning material
- Practice important concepts
- Take another quiz
"""
    )

else:

    st.success(
        f"""
### 🚀 Move Forward

Your weakest topic is **{weakest_name}**
with **{weakest_mastery:.0f}%** mastery.

Your understanding is strong enough to
continue to another topic.
"""
    )


# ============================================================
# NEXT ACTION
# ============================================================

st.divider()

st.subheader("🎯 What should you do next?")


if weakest_mastery < 50:

    st.info(
        "📖 Go to Learn and relearn your weakest topic."
    )

elif weakest_mastery < 80:

    st.info(
        "🔄 Revise your weakest topic and attempt "
        "another quiz."
    )

else:

    st.info(
        "🚀 Your topics are progressing well. "
        "Continue with the next important topic."
    )