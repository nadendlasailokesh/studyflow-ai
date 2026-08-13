import streamlit as st


st.set_page_config(
    page_title="Learn",
    page_icon="📖",
    layout="wide"
)


st.title("📖 Learn")

st.write(
    "Learn difficult concepts using explanations "
    "adapted to your learning style."
)


# -----------------------------
# Topic Selection
# -----------------------------

topic = st.selectbox(
    "Choose a topic",
    [
        "Morphology",
        "Finite-State Transducers",
        "Phonology",
        "Syntax",
        "Semantics"
    ]
)


st.divider()


# -----------------------------
# Learning Modes
# -----------------------------

st.subheader(f"🧠 Learn: {topic}")

col1, col2, col3, col4 = st.columns(4)

with col1:

    if st.button(
        "🧒 Simple Explanation",
        use_container_width=True
    ):
        st.info(
            "The AI will explain this topic "
            "using simple language."
        )


with col2:

    if st.button(
        "📚 Detailed",
        use_container_width=True
    ):
        st.info(
            "The AI will provide a detailed "
            "technical explanation."
        )


with col3:

    if st.button(
        "💡 Example",
        use_container_width=True
    ):
        st.info(
            "The AI will explain the topic "
            "using practical examples."
        )


with col4:

    if st.button(
        "🎯 Exam Answer",
        use_container_width=True
    ):
        st.info(
            "The AI will generate an "
            "exam-oriented explanation."
        )


st.divider()


st.subheader("📖 Learning Content")

st.info(
    "AI-generated learning content will appear here "
    "after the AI engine is implemented."
)