import streamlit as st
from src.database.db import initialize_database

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="StudyFlow AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)
initialize_database()

# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.title("📚 StudyFlow AI")

    st.caption("Your AI Learning Companion")

    st.divider()

    st.subheader("👤 Student")

    student_name = st.text_input(
        "Your name",
        placeholder="Enter your name"
    )

    st.divider()

    st.info(
        "Use the navigation menu to plan your studies, "
        "learn concepts, practice questions, and track progress."
    )


# -----------------------------
# Main Dashboard
# -----------------------------

if student_name:
    greeting = f"Welcome back, {student_name}! 👋"
else:
    greeting = "Welcome to StudyFlow AI! 👋"


st.title(greeting)

st.write(
    "Your personalized AI-powered learning companion."
)


# -----------------------------
# Exam Overview
# -----------------------------

st.subheader("🎯 Exam Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📅 Days Until Exam",
        value="12"
    )

with col2:
    st.metric(
        label="📚 Topics",
        value="24"
    )

with col3:
    st.metric(
        label="✅ Completed",
        value="14"
    )

with col4:
    st.metric(
        label="📊 Overall Progress",
        value="68%"
    )


st.divider()


# -----------------------------
# Today's Recommendation
# -----------------------------

st.subheader("✨ What Should I Study Now?")

recommendation_col1, recommendation_col2 = st.columns(
    [3, 1]
)

with recommendation_col1:

    st.markdown(
        """
        ### 🧠 Recommended Topic: Syntax Trees

        **Priority:** 🔥 High

        **Estimated time:** 35 minutes

        **Reason:** Your recent quiz performance shows that
        Syntax Trees is currently one of your weaker topics.
        """
    )

with recommendation_col2:

    st.write("")

    if st.button(
        "🚀 Start Learning",
        use_container_width=True
    ):
        st.success("Learning session started!")


st.divider()


# -----------------------------
# Today's Tasks
# -----------------------------

st.subheader("📋 Today's Tasks")

tasks = [
    ("Review Morphology", True),
    ("Study Syntax Trees", False),
    ("Practice 5 Quiz Questions", False),
    ("Revise Important Definitions", False),
]

for task, completed in tasks:

    st.checkbox(
        task,
        value=completed,
        key=task
    )


st.divider()


# -----------------------------
# Learning Progress
# -----------------------------

st.subheader("📈 Learning Progress")

progress_col1, progress_col2 = st.columns(2)

with progress_col1:

    st.write("Overall Study Progress")

    st.progress(0.68)

    st.caption("68% of your current study plan completed.")


with progress_col2:

    st.write("🎯 Current Mastery")

    st.progress(0.72)

    st.caption("Your estimated concept mastery is 72%.")


st.divider()


# -----------------------------
# AI Insight
# -----------------------------

st.subheader("🤖 StudyFlow Insight")

st.info(
    """
    You are doing well in Morphology and Phonology.

    Your current weak area is Syntax. Consider spending
    additional time on Syntax Trees and Context-Free Grammar
    before moving to the next unit.
    """
)