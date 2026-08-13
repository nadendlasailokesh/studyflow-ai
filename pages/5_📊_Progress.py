import streamlit as st


st.set_page_config(
    page_title="Progress",
    page_icon="📊",
    layout="wide"
)


st.title("📊 Your Learning Progress")


# -----------------------------
# Metrics
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Overall Progress",
        "68%"
    )

with col2:
    st.metric(
        "Quiz Accuracy",
        "81%"
    )

with col3:
    st.metric(
        "Concept Mastery",
        "72%"
    )

with col4:
    st.metric(
        "Study Streak",
        "5 🔥"
    )


st.divider()


# -----------------------------
# Topic Mastery
# -----------------------------

st.subheader("🧠 Topic Mastery")


topics = {
    "Morphology": 0.90,
    "Phonology": 0.85,
    "Syntax": 0.45,
    "Semantics": 0.72
}


for topic, score in topics.items():

    st.write(
        f"**{topic} — {score * 100:.0f}%**"
    )

    st.progress(score)


st.divider()


# -----------------------------
# Recommendation
# -----------------------------

st.subheader("✨ AI Recommendation")

st.warning(
    """
    Syntax is currently your weakest topic.

    Recommended action:
    Spend 30–40 minutes reviewing Syntax Trees
    and then attempt another practice quiz.
    """
)