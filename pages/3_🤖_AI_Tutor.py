import streamlit as st

from src.ai.tutor import ask_tutor

from src.database.dashboard import (
    get_subject_topics
)

from src.database.subjects import (
    get_subjects
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Tutor",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🤖 StudyFlow AI Tutor")

st.write(
    "Ask questions about what you are currently learning."
)


# ============================================================
# GET STUDENT
# ============================================================

student_id = st.session_state.get(
    "student_id"
)

selected_subject_id = st.session_state.get(
    "selected_subject_id"
)


# ============================================================
# CHECK STUDENT
# ============================================================

if not student_id:

    st.warning(
        "No student profile is available yet."
    )

    st.info(
        "Go to 📚 My Subjects first."
    )

    st.stop()


# ============================================================
# LOAD SUBJECTS
# ============================================================

subjects = get_subjects(
    student_id
)


if not subjects:

    st.info(
        "You have not added any subjects yet."
    )

    st.info(
        "Go to 📚 My Subjects and add a subject first."
    )

    st.stop()


# ============================================================
# SELECT SUBJECT
# ============================================================

subject_map = {
    subject["name"]: subject
    for subject in subjects
}


subject_names = list(
    subject_map.keys()
)


# Find current subject

current_subject_name = None

for subject in subjects:

    if subject["id"] == selected_subject_id:

        current_subject_name = subject["name"]

        break


if current_subject_name:

    default_index = subject_names.index(
        current_subject_name
    )

else:

    default_index = 0


selected_subject_name = st.selectbox(
    "📚 Subject",
    subject_names,
    index=default_index
)


selected_subject = subject_map[
    selected_subject_name
]


# Keep global selected subject synchronized

st.session_state.selected_subject_id = (
    selected_subject["id"]
)


# ============================================================
# SUBJECT INFORMATION
# ============================================================

st.info(
    f"📘 Current subject: "
    f"**{selected_subject['name']}**"
)


# ============================================================
# LOAD SAVED TOPICS
# ============================================================

try:

    topics = get_subject_topics(
        selected_subject["id"]
    )

except Exception as error:

    st.error(
        "Unable to load topics from the database."
    )

    st.exception(error)

    st.stop()


# ============================================================
# CHECK TOPICS
# ============================================================

if not topics:

    st.warning(
        "No syllabus topics are available for this subject."
    )

    st.info(
        "Go to 📚 My Subjects → Syllabus Analyzer → "
        "Analyze Syllabus → Save Topics."
    )

    st.stop()


# ============================================================
# TOPIC SELECTION
# ============================================================

st.subheader(
    "📖 Current Topic"
)


topic_names = [
    topic["name"]
    for topic in topics
    if topic.get("name")
]


if not topic_names:

    st.warning(
        "No valid topic names were found."
    )

    st.stop()


topic = st.selectbox(
    "Choose the topic you are currently learning",
    topic_names
)


# ============================================================
# FIND TOPIC DATA
# ============================================================

selected_topic_data = next(
    (
        item
        for item in topics
        if item["name"] == topic
    ),
    None
)


if selected_topic_data:

    unit = (
        selected_topic_data.get("unit")
        or "Not specified"
    )

    priority = (
        selected_topic_data.get("priority")
        or "MEDIUM"
    )

    mastery = (
        selected_topic_data.get("mastery")
        or 0
    )

else:

    unit = "Not specified"

    priority = "MEDIUM"

    mastery = 0


# ============================================================
# TOPIC INFORMATION
# ============================================================

st.caption(
    f"Your questions will be related to: "
    f"**{topic}**"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "📘 Unit",
        unit
    )


with col2:

    st.metric(
        "🎯 Priority",
        priority
    )


with col3:

    st.metric(
        "📊 Mastery",
        f"{float(mastery):.0f}%"
    )


# ============================================================
# CHAT HISTORY
# ============================================================

if "tutor_messages" not in st.session_state:

    st.session_state.tutor_messages = []


# ============================================================
# RESET CHAT WHEN TOPIC CHANGES
# ============================================================

previous_topic = st.session_state.get(
    "tutor_previous_topic"
)


if previous_topic != topic:

    st.session_state.tutor_messages = []

    st.session_state.tutor_previous_topic = (
        topic
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.tutor_messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    f"Ask something about {topic}..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if prompt:

    prompt = prompt.strip()


    if not prompt:

        st.warning(
            "Please enter a question."
        )

        st.stop()


    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    st.session_state.tutor_messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(prompt)


    # --------------------------------------------------------
    # Previous conversation
    # --------------------------------------------------------

    previous_context = (
        st.session_state.tutor_messages[-7:-1]
    )


    # --------------------------------------------------------
    # Generate AI response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 Your AI Tutor is thinking..."
        ):

            try:

                response = ask_tutor(

                    subject_name=(
                        selected_subject["name"]
                    ),

                    unit=unit,

                    topic=topic,

                    question=prompt,

                    previous_context=(
                        previous_context
                    )
                )


                # ==========================================
                # ANSWER
                # ==========================================

                st.markdown(
                    "### 💡 Answer"
                )

                st.write(
                    response.answer
                )


                # ==========================================
                # SIMPLE EXPLANATION
                # ==========================================

                if response.simple_explanation:

                    st.markdown(
                        "### 🧠 Simple Explanation"
                    )

                    st.write(
                        response.simple_explanation
                    )


                # ==========================================
                # EXAMPLE
                # ==========================================

                if response.example:

                    st.markdown(
                        "### 💡 Example"
                    )

                    st.info(
                        response.example
                    )


                # ==========================================
                # KEY POINTS
                # ==========================================

                if response.key_points:

                    st.markdown(
                        "### 📌 Key Points"
                    )

                    for point in response.key_points:

                        st.markdown(
                            f"• {point}"
                        )


                # ==========================================
                # FOLLOW UP
                # ==========================================

                if response.follow_up_question:

                    st.markdown(
                        "### 🎯 Think About This"
                    )

                    st.caption(
                        response.follow_up_question
                    )


                # ==========================================
                # BUILD CHAT MESSAGE
                # ==========================================

                assistant_text = (
                    "### 💡 Answer\n\n"
                    f"{response.answer}"
                )


                if response.simple_explanation:

                    assistant_text += (
                        "\n\n"
                        "### 🧠 Simple Explanation\n\n"
                        f"{response.simple_explanation}"
                    )


                if response.example:

                    assistant_text += (
                        "\n\n"
                        "### 💡 Example\n\n"
                        f"{response.example}"
                    )


                if response.key_points:

                    assistant_text += (
                        "\n\n"
                        "### 📌 Key Points\n\n"
                    )

                    for point in response.key_points:

                        assistant_text += (
                            f"• {point}\n"
                        )


                if response.follow_up_question:

                    assistant_text += (
                        "\n\n"
                        "### 🎯 Think About This\n\n"
                        f"{response.follow_up_question}"
                    )


                # ==========================================
                # SAVE AI RESPONSE
                # ==========================================

                st.session_state.tutor_messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_text
                    }
                )


            except Exception as error:

                st.error(
                    "❌ Unable to generate AI Tutor response."
                )

                st.exception(error)