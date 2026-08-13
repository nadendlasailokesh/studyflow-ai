import streamlit as st


st.set_page_config(
    page_title="AI Tutor",
    page_icon="🤖",
    layout="wide"
)


st.title("🤖 StudyFlow AI Tutor")

st.write(
    "Ask questions about what you are currently learning."
)


# -----------------------------
# Topic Context
# -----------------------------

topic = st.selectbox(
    "Current topic",
    [
        "Morphology",
        "Phonology",
        "Syntax",
        "Semantics",
        "Pragmatics"
    ]
)


st.caption(
    f"Your questions will be related to: **{topic}**"
)


# -----------------------------
# Chat Interface
# -----------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


prompt = st.chat_input(
    f"Ask something about {topic}..."
)


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)


    with st.chat_message("assistant"):

        response = (
            "🤖 AI Tutor will answer this question "
            "once the AI engine is connected."
        )

        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )