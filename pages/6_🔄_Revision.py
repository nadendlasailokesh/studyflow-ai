# ============================================================
# STUDYFLOW AI
# PAGE 6 — REVISION CENTER
# PHASE 8.6
# ============================================================

import sys
from pathlib import Path
from datetime import date, datetime

import streamlit as st


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

from src.database.db import initialize_database

from src.database.revision import (
    get_due_revisions,
    get_upcoming_revisions,
)

from src.database.repository import (
    get_all_subjects,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Revision | StudyFlow AI",
    page_icon="🔄",
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
        "Please create a student profile first "
        "from 📚 My Subjects."
    )

    st.stop()


student_id = st.session_state.student_id


# ============================================================
# HEADER
# ============================================================

st.title("🔄 Revision Center")

st.write(
    "StudyFlow AI schedules your revisions based on "
    "your previous performance and spaced-repetition schedule."
)

st.divider()


# ============================================================
# LOAD REVISION DATA
# ============================================================

try:

    due_revisions = get_due_revisions()

    upcoming_revisions = get_upcoming_revisions(
        days=7
    )

except Exception as error:

    st.error(
        "Unable to load revision schedules."
    )

    st.exception(error)

    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_date(value):

    if value is None:
        return "Not scheduled"

    if isinstance(value, datetime):
        return value.date().strftime(
            "%d %b %Y"
        )

    if isinstance(value, date):
        return value.strftime(
            "%d %b %Y"
        )

    try:

        return date.fromisoformat(
            str(value)
        ).strftime(
            "%d %b %Y"
        )

    except ValueError:

        return str(value)


def days_from_today(value):

    if value is None:
        return None

    try:

        review_date = date.fromisoformat(
            str(value)
        )

        return (
            review_date - date.today()
        ).days

    except ValueError:

        return None


def priority_icon(priority):

    priority = str(
        priority or "MEDIUM"
    ).upper()

    if priority == "HIGH":
        return "🔥"

    if priority == "LOW":
        return "🟢"

    return "🟡"


def status_icon(status):

    status = str(
        status or ""
    ).upper()

    if status == "WEAK":
        return "🔴"

    if status == "STRONG":
        return "🟢"

    if status == "AVERAGE":
        return "🟡"

    return "⚪"


def start_revision(revision):

    topic_id = revision.get(
        "topic_id"
    )

    topic_name = revision.get(
        "topic_name",
        ""
    )

    subject_id = revision.get(
        "subject_id"
    )

    if topic_id is None:

        st.error(
            "This revision does not contain "
            "a valid topic ID."
        )

        return

    if subject_id is None:

        st.error(
            "This revision does not contain "
            "a valid subject ID."
        )

        return

    # --------------------------------------------------------
    # Find subject name
    # --------------------------------------------------------

    subject_name = ""

    try:

        subjects = get_all_subjects(
            student_id
        )

        for subject in subjects:

            if subject["id"] == subject_id:

                subject_name = (
                    subject["name"]
                )

                break

    except Exception:

        subject_name = ""

    # --------------------------------------------------------
    # Store transition context
    # --------------------------------------------------------

    st.session_state[
        "learning_transition_context"
    ] = {

        "subject_id": subject_id,

        "subject_name": subject_name,

        "topic_id": topic_id,

        "topic_name": topic_name,
    }

    # --------------------------------------------------------
    # Store direct learning context
    # --------------------------------------------------------

    st.session_state[
        "selected_topic_id"
    ] = topic_id

    st.session_state[
        "selected_topic_name"
    ] = topic_name

    st.session_state[
        "selected_subject_id"
    ] = subject_id

    st.session_state[
        "selected_subject_name"
    ] = subject_name

    # --------------------------------------------------------
    # Navigate to Learn
    # --------------------------------------------------------

    st.switch_page(
        "pages/2_📖_Learn.py"
    )


# ============================================================
# SUMMARY METRICS
# ============================================================

total_due = len(
    due_revisions
)

total_upcoming = len(
    upcoming_revisions
)

all_revision_records = (
    due_revisions
    + upcoming_revisions
)

unique_records = {}

for revision in all_revision_records:

    topic_id = revision.get(
        "topic_id"
    )

    if topic_id is not None:

        unique_records[
            topic_id
        ] = revision


max_streak = 0

for revision in unique_records.values():

    streak = int(
        revision.get(
            "revision_streak",
            0
        )
        or 0
    )

    max_streak = max(
        max_streak,
        streak
    )


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🔴 Due Today",
        total_due
    )


with col2:

    st.metric(
        "📅 Upcoming",
        total_upcoming
    )


with col3:

    st.metric(
        "📚 Scheduled Topics",
        len(unique_records)
    )


with col4:

    st.metric(
        "🔥 Best Revision Streak",
        max_streak
    )


st.divider()


# ============================================================
# NO REVISION DATA
# ============================================================

if not due_revisions and not upcoming_revisions:

    st.success(
        "🎉 You have no revisions scheduled right now."
    )

    st.info(
        """
Complete quizzes for your topics to create
personalized revision schedules.

StudyFlow AI will automatically determine when
each topic should be reviewed again.
"""
    )

    st.stop()


# ============================================================
# DUE REVISIONS
# ============================================================

st.subheader(
    "🔴 Revisions Due Now"
)

st.write(
    "These topics should be revised before moving "
    "too far ahead in your study plan."
)


if not due_revisions:

    st.success(
        "✅ No revisions are due today."
    )

else:

    for index, revision in enumerate(
        due_revisions
    ):

        topic_name = (
            revision.get(
                "topic_name"
            )
            or "Unknown Topic"
        )

        unit = (
            revision.get(
                "unit"
            )
            or "General"
        )

        mastery = float(
            revision.get(
                "mastery",
                0
            )
            or 0
        )

        priority = (
            revision.get(
                "priority"
            )
            or "MEDIUM"
        )

        status = (
            revision.get(
                "status"
            )
            or "Not Started"
        )

        streak = int(
            revision.get(
                "revision_streak",
                0
            )
            or 0
        )

        interval = int(
            revision.get(
                "review_interval_days",
                0
            )
            or 0
        )

        next_review = revision.get(
            "next_review_date"
        )

        days_overdue = (
            days_from_today(
                next_review
            )
        )

        if (
            days_overdue is not None
            and days_overdue < 0
        ):

            urgency_text = (
                f"Overdue by "
                f"{abs(days_overdue)} day(s)"
            )

        else:

            urgency_text = "Due today"

        with st.container(
            border=True
        ):

            col1, col2 = st.columns(
                [5, 2]
            )

            with col1:

                st.markdown(
                    f"### 🔄 {topic_name}"
                )

                st.caption(
                    f"📚 {unit}"
                )

                st.write(
                    f"{priority_icon(priority)} "
                    f"**Priority:** {priority}   "
                    f"{status_icon(status)} "
                    f"**Status:** {status}"
                )

                st.write(
                    f"📊 Mastery: **{mastery:.0f}%**"
                )

                st.write(
                    f"🔥 Revision streak: "
                    f"**{streak}**"
                )

                st.caption(
                    f"⏱️ Current interval: "
                    f"{interval} day(s)"
                )

                if days_overdue is not None:

                    if days_overdue < 0:

                        st.error(
                            f"⚠️ {urgency_text}"
                        )

                    else:

                        st.warning(
                            f"📅 {urgency_text}"
                        )

            with col2:

                st.write(
                    f"**Scheduled:** "
                    f"{format_date(next_review)}"
                )

                st.write(
                    "Revision is recommended now "
                    "to maintain retention."
                )

                if st.button(
                    "📖 Start Revision",
                    key=(
                        f"start_due_revision_"
                        f"{revision.get('topic_id')}_"
                        f"{index}"
                    ),
                    type="primary",
                    use_container_width=True,
                ):

                    start_revision(
                        revision
                    )


# ============================================================
# UPCOMING REVISIONS
# ============================================================

st.divider()

st.subheader(
    "📅 Upcoming Revisions"
)

st.write(
    "Topics scheduled for revision during "
    "the next 7 days."
)


# Remove topics already displayed as due.

due_topic_ids = {
    revision.get(
        "topic_id"
    )
    for revision in due_revisions
}


filtered_upcoming = [

    revision

    for revision in upcoming_revisions

    if revision.get(
        "topic_id"
    )
    not in due_topic_ids

]


if not filtered_upcoming:

    if due_revisions:

        st.info(
            "No additional upcoming revisions "
            "are scheduled within the next 7 days."
        )

else:

    for index, revision in enumerate(
        filtered_upcoming
    ):

        topic_name = (
            revision.get(
                "topic_name"
            )
            or "Unknown Topic"
        )

        unit = (
            revision.get(
                "unit"
            )
            or "General"
        )

        mastery = float(
            revision.get(
                "mastery",
                0
            )
            or 0
        )

        priority = (
            revision.get(
                "priority"
            )
            or "MEDIUM"
        )

        status = (
            revision.get(
                "status"
            )
            or "Not Started"
        )

        streak = int(
            revision.get(
                "revision_streak",
                0
            )
            or 0
        )

        interval = int(
            revision.get(
                "review_interval_days",
                0
            )
            or 0
        )

        next_review = revision.get(
            "next_review_date"
        )

        days_until = (
            days_from_today(
                next_review
            )
        )

        with st.container(
            border=True
        ):

            col1, col2, col3 = st.columns(
                [5, 2, 2]
            )

            with col1:

                st.markdown(
                    f"**📖 {topic_name}**"
                )

                st.caption(
                    f"📚 {unit}"
                )

                st.write(
                    f"{priority_icon(priority)} "
                    f"{priority}  •  "
                    f"{status_icon(status)} "
                    f"{status}"
                )

            with col2:

                st.metric(
                    "Mastery",
                    f"{mastery:.0f}%"
                )

                st.caption(
                    f"🔥 Streak: {streak}"
                )

            with col3:

                st.write(
                    f"📅 **{format_date(next_review)}**"
                )

                if days_until == 0:

                    st.warning(
                        "Due today"
                    )

                elif (
                    days_until is not None
                    and days_until > 0
                ):

                    st.caption(
                        f"In {days_until} day(s)"
                    )

                st.caption(
                    f"Interval: {interval} day(s)"
                )


# ============================================================
# REVISION STRATEGY
# ============================================================

st.divider()

st.subheader(
    "🧠 How Spaced Revision Works"
)

st.info(
    """
StudyFlow AI adjusts revision timing according to
your quiz performance.

**🔴 Weak performance (< 50%)**  
Revision is scheduled very soon.

**🟡 Developing performance (50–79%)**  
Revision happens after a shorter interval.

**🟢 Strong performance (80–89%)**  
The interval becomes longer.

**⭐ Excellent performance (90%+)**  
Revision can be spaced further apart.

**🔥 Successful revision streak**  
Consistent strong performance can extend the
revision interval, up to the system's maximum.
"""
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "StudyFlow AI • Phase 8.6 — Spaced Repetition & Revision"
)