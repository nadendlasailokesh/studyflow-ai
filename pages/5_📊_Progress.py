import streamlit as st

from datetime import date, datetime


from src.database.db import initialize_database

from src.database.repository import (
    get_topic_mastery_for_student,
    get_quiz_statistics_for_student,
    get_subject_progress,
    get_student_progress_summary,
    get_quiz_performance_analytics,
    get_learning_trends,
)

from src.database.revision import (
    get_revision_record,
    get_due_revisions,
    get_upcoming_revisions,
)

from src.ai.recommendation import (
    get_top_recommendation,
)

from src.ai.recommendation_explanation import (
    generate_recommendation_reasons,
    get_recommendation_summary,
)

from src.ai.revision_scheduler import (
    get_revision_recommendation,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Progress | StudyFlow AI",
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
    "revision schedule, learning trends, and "
    "identify what you should study next."
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

progress_summary = get_student_progress_summary(
    student_id
)

quiz_analytics = get_quiz_performance_analytics(
    student_id
)

learning_trends = get_learning_trends(
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
        float(
            topic.get("mastery", 0) or 0
        )
        for topic in topics
    )
    / total_topics
    if total_topics > 0
    else 0.0
)


# ============================================================
# QUIZ ACCURACY
# ============================================================

total_questions = int(
    quiz_stats.get(
        "total_questions",
        0
    )
    or 0
)

correct_answers = float(
    quiz_stats.get(
        "correct_answers",
        0
    )
    or 0
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
    quiz_stats.get(
        "attempts",
        0
    )
    or 0
)


# ============================================================
# MAIN METRICS
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
# PHASE 9.1
# ADVANCED PROGRESS METRICS
# ============================================================

st.markdown(
    "### 📈 Learning Overview"
)


metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = (
    st.columns(5)
)


with metric_col1:

    st.metric(
        "📚 Total Topics",
        progress_summary.get(
            "total_topics",
            0
        )
    )


with metric_col2:

    st.metric(
        "🏆 Completed",
        progress_summary.get(
            "completed_topics",
            0
        )
    )


with metric_col3:

    st.metric(
        "🟢 Strong",
        progress_summary.get(
            "strong_topics",
            0
        )
    )


with metric_col4:

    st.metric(
        "🟡 Average",
        progress_summary.get(
            "average_topics",
            0
        )
    )


with metric_col5:

    st.metric(
        "🔴 Weak",
        progress_summary.get(
            "weak_topics",
            0
        )
    )


st.caption(
    f"Average mastery: "
    f"{float(progress_summary.get('average_mastery', 0) or 0):.0f}% "
    f"• Not started: "
    f"{progress_summary.get('not_started_topics', 0)} topic(s)"
)


# ============================================================
# PHASE 9.2
# PROGRESS VISUALIZATION
# ============================================================

st.divider()

st.subheader(
    "📊 Progress Visualization"
)


# ============================================================
# 9.2.1
# MASTERY DISTRIBUTION
# ============================================================

st.markdown(
    "#### 🧠 Topic Mastery Distribution"
)


mastery_distribution = {

    "Strong": progress_summary.get(
        "strong_topics",
        0
    ),

    "Average": progress_summary.get(
        "average_topics",
        0
    ),

    "Weak": progress_summary.get(
        "weak_topics",
        0
    ),

    "Not Started": progress_summary.get(
        "not_started_topics",
        0
    ),
}


st.bar_chart(
    mastery_distribution
)


# ============================================================
# 9.2.2
# SUBJECT MASTERY
# ============================================================

st.markdown(
    "#### 📚 Subject Mastery"
)


subject_chart_data = {}


for subject in subject_progress:

    subject_name = (
        subject.get(
            "subject_name"
        )
        or "Unknown Subject"
    )

    mastery = float(
        subject.get(
            "average_mastery",
            0
        )
        or 0
    )

    subject_chart_data[
        subject_name
    ] = round(
        mastery,
        2
    )


if subject_chart_data:

    st.bar_chart(
        subject_chart_data
    )

else:

    st.info(
        "No subject mastery data is available yet."
    )


# ============================================================
# 9.2.3
# TOPIC MASTERY OVERVIEW
# ============================================================

st.markdown(
    "#### 🎯 Topic Mastery Overview"
)


topic_chart_data = {}


for topic in topics:

    topic_name = (
        topic.get(
            "name"
        )
        or "Unknown Topic"
    )

    mastery = float(
        topic.get(
            "mastery",
            0
        )
        or 0
    )

    topic_chart_data[
        topic_name
    ] = round(
        mastery,
        2
    )


if topic_chart_data:

    st.bar_chart(
        topic_chart_data
    )

else:

    st.info(
        "No topic mastery data is available yet."
    )


# ============================================================
# PHASE 9.3
# QUIZ PERFORMANCE ANALYTICS
# ============================================================

st.divider()

st.subheader(
    "📝 Quiz Performance Analytics"
)


quiz_overall = quiz_analytics.get(
    "overall",
    {}
)


quiz_attempts_total = int(
    quiz_overall.get(
        "attempts",
        0
    )
    or 0
)


quiz_average_score = float(
    quiz_overall.get(
        "average_score",
        0
    )
    or 0
)


quiz_best_score = float(
    quiz_overall.get(
        "best_score",
        0
    )
    or 0
)


quiz_total_questions = int(
    quiz_overall.get(
        "total_questions",
        0
    )
    or 0
)


quiz_correct_answers = float(
    quiz_overall.get(
        "correct_answers",
        0
    )
    or 0
)


# ============================================================
# 9.3.1
# QUIZ METRICS
# ============================================================

quiz_col1, quiz_col2, quiz_col3, quiz_col4 = (
    st.columns(4)
)


with quiz_col1:

    st.metric(
        "📝 Attempts",
        quiz_attempts_total
    )


with quiz_col2:

    st.metric(
        "📊 Average Score",
        f"{quiz_average_score:.0f}%"
    )


with quiz_col3:

    st.metric(
        "🏆 Best Score",
        f"{quiz_best_score:.0f}%"
    )


with quiz_col4:

    st.metric(
        "✅ Correct Answers",
        f"{quiz_correct_answers:.0f}"
    )


# ============================================================
# 9.3.2
# QUIZ DATA STATUS
# ============================================================

if quiz_attempts_total == 0:

    st.info(
        "Complete a practice quiz to see "
        "your quiz performance analytics."
    )

else:

    st.caption(
        f"You have answered approximately "
        f"{quiz_correct_answers:.0f} correctly out of "
        f"{quiz_total_questions} questions."
    )


# ============================================================
# 9.3.3
# PERFORMANCE BY DIFFICULTY
# ============================================================

difficulty_data = quiz_analytics.get(
    "by_difficulty",
    []
)


if difficulty_data:

    st.markdown(
        "#### 🎚️ Performance by Difficulty"
    )


    difficulty_col1, difficulty_col2, difficulty_col3 = (
        st.columns(3)
    )


    for index, difficulty in enumerate(
        difficulty_data
    ):

        column = (
            difficulty_col1
            if index % 3 == 0
            else
            difficulty_col2
            if index % 3 == 1
            else
            difficulty_col3
        )


        difficulty_name = (
            difficulty.get(
                "difficulty"
            )
            or "Unknown"
        )

        difficulty_score = float(
            difficulty.get(
                "average_score",
                0
            )
            or 0
        )

        difficulty_attempts = int(
            difficulty.get(
                "attempts",
                0
            )
            or 0
        )


        with column:

            st.metric(
                difficulty_name,
                f"{difficulty_score:.0f}%"
            )

            st.caption(
                f"{difficulty_attempts} attempt(s)"
            )


# ============================================================
# 9.3.4
# TOPIC-WISE QUIZ PERFORMANCE
# ============================================================

topic_quiz_data = quiz_analytics.get(
    "by_topic",
    []
)


if topic_quiz_data:

    st.markdown(
        "#### 🧠 Topic-wise Quiz Performance"
    )


    for topic_result in topic_quiz_data:

        topic_name = (
            topic_result.get(
                "topic_name"
            )
            or "Unknown Topic"
        )

        subject_name = (
            topic_result.get(
                "subject_name"
            )
            or "Unknown Subject"
        )

        average_score = float(
            topic_result.get(
                "average_score",
                0
            )
            or 0
        )

        best_score = float(
            topic_result.get(
                "best_score",
                0
            )
            or 0
        )

        attempts = int(
            topic_result.get(
                "attempts",
                0
            )
            or 0
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"**📖 {topic_name}**"
            )

            st.caption(
                subject_name
            )


            topic_col1, topic_col2, topic_col3 = (
                st.columns(3)
            )


            with topic_col1:

                st.metric(
                    "Average",
                    f"{average_score:.0f}%"
                )


            with topic_col2:

                st.metric(
                    "Best",
                    f"{best_score:.0f}%"
                )


            with topic_col3:

                st.metric(
                    "Attempts",
                    attempts
                )


            st.progress(
                min(
                    max(
                        average_score / 100,
                        0
                    ),
                    1
                )
            )


# ============================================================
# 9.3.5
# RECENT QUIZ ATTEMPTS
# ============================================================

recent_attempts = quiz_analytics.get(
    "recent_attempts",
    []
)


if recent_attempts:

    st.markdown(
        "#### 🕒 Recent Quiz Attempts"
    )


    for attempt in recent_attempts:

        score = float(
            attempt.get(
                "score",
                0
            )
            or 0
        )

        topic_name = (
            attempt.get(
                "topic_name"
            )
            or "Unknown Topic"
        )

        difficulty = (
            attempt.get(
                "difficulty"
            )
            or "Unknown"
        )

        total_questions_attempt = int(
            attempt.get(
                "total_questions",
                0
            )
            or 0
        )

        created_at = (
            attempt.get(
                "created_at"
            )
            or ""
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"**📖 {topic_name}**"
            )

            st.caption(
                f"{difficulty} • "
                f"{total_questions_attempt} question(s) • "
                f"{created_at}"
            )

            st.progress(
                min(
                    max(
                        score / 100,
                        0
                    ),
                    1
                )
            )

            st.write(
                f"Score: **{score:.0f}%**"
            )


# ============================================================
# PHASE 9.4
# LEARNING TRENDS
# ============================================================

st.divider()

st.subheader(
    "📈 Learning Trends"
)


trend_summary = learning_trends.get(
    "summary",
    {}
)

trend_attempts = learning_trends.get(
    "attempts",
    []
)


# ============================================================
# 9.4.1
# TREND DATA
# ============================================================

trend = (
    trend_summary.get(
        "trend",
        "NO_DATA"
    )
    or "NO_DATA"
)


trend_change = float(
    trend_summary.get(
        "change",
        0.0
    )
    or 0
)


first_score = float(
    trend_summary.get(
        "first_score",
        0.0
    )
    or 0
)


latest_score = float(
    trend_summary.get(
        "latest_score",
        0.0
    )
    or 0
)


highest_score = float(
    trend_summary.get(
        "highest_score",
        0.0
    )
    or 0
)


lowest_score = float(
    trend_summary.get(
        "lowest_score",
        0.0
    )
    or 0
)


# ============================================================
# 9.4.2
# TREND METRICS
# ============================================================

trend_col1, trend_col2, trend_col3, trend_col4 = (
    st.columns(4)
)


with trend_col1:

    st.metric(
        "First Score",
        f"{first_score:.0f}%"
    )


with trend_col2:

    st.metric(
        "Latest Score",
        f"{latest_score:.0f}%"
    )


with trend_col3:

    st.metric(
        "Highest Score",
        f"{highest_score:.0f}%"
    )


with trend_col4:

    st.metric(
        "Score Change",
        f"{trend_change:+.0f}%"
    )


# ============================================================
# 9.4.3
# TREND STATUS
# ============================================================

if trend == "IMPROVING":

    st.success(
        f"📈 Your quiz performance is improving "
        f"by **{trend_change:.1f}%**."
    )

elif trend == "DECLINING":

    st.error(
        f"📉 Your quiz performance has decreased "
        f"by **{abs(trend_change):.1f}%**."
    )

elif trend == "STABLE":

    st.info(
        "📊 Your quiz performance is currently stable."
    )

elif trend == "INSUFFICIENT_DATA":

    st.info(
        "📊 Complete at least two quizzes to "
        "identify a meaningful performance trend."
    )

else:

    st.info(
        "📊 Complete quizzes to generate "
        "your learning trend."
    )


# ============================================================
# 9.4.4
# QUIZ SCORE HISTORY
# ============================================================

if trend_attempts:

    st.markdown(
        "#### 📝 Quiz Score History"
    )


    for attempt in reversed(
        trend_attempts
    ):

        score = float(
            attempt.get(
                "score",
                0
            )
            or 0
        )

        topic_name = (
            attempt.get(
                "topic_name"
            )
            or "Unknown Topic"
        )

        difficulty = (
            attempt.get(
                "difficulty"
            )
            or "Unknown"
        )

        total_questions_attempt = int(
            attempt.get(
                "total_questions",
                0
            )
            or 0
        )

        created_at = (
            attempt.get(
                "created_at"
            )
            or ""
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"**📖 {topic_name}**"
            )

            st.caption(
                f"{difficulty} • "
                f"{total_questions_attempt} question(s) • "
                f"{created_at}"
            )

            st.progress(
                min(
                    max(
                        score / 100,
                        0
                    ),
                    1
                )
            )

            st.write(
                f"Score: **{score:.0f}%**"
            )

else:

    st.info(
        "No quiz history is available yet. "
        "Complete a quiz to start tracking your "
        "learning trend."
    )


# ============================================================
# SUBJECT PROGRESS
# ============================================================

st.divider()

st.subheader(
    "📚 Subject Progress"
)


if subject_progress:

    for subject in subject_progress:

        subject_name = (
            subject.get(
                "subject_name"
            )
            or "Unknown Subject"
        )

        mastery = float(
            subject.get(
                "average_mastery",
                0
            )
            or 0
        )

        total_subject_topics = int(
            subject.get(
                "total_topics",
                0
            )
            or 0
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

else:

    st.info(
        "No subject progress is available yet."
    )


# ============================================================
# TOPIC MASTERY
# ============================================================

st.divider()

st.subheader(
    "🧠 Topic Mastery"
)


for topic in topics:

    topic_name = (
        topic.get(
            "name"
        )
        or "Unknown Topic"
    )

    mastery = float(
        topic.get(
            "mastery",
            0
        )
        or 0
    )

    priority = (
        topic.get(
            "priority"
        )
        or "MEDIUM"
    )

    status = (
        topic.get(
            "status"
        )
        or "Not Started"
    )

    unit = (
        topic.get(
            "unit"
        )
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
# PHASE 8.5
# REVISION SCHEDULE
# ============================================================

st.subheader(
    "📅 Revision Schedule"
)

st.write(
    "StudyFlow AI uses spaced repetition to schedule "
    "future revisions based on your quiz performance."
)


# ============================================================
# LOAD REVISION DATA
# ============================================================

due_revisions = get_due_revisions()

upcoming_revisions = get_upcoming_revisions(
    days=7
)


# ============================================================
# FILTER REVISION DATA TO CURRENT STUDENT
# ============================================================

student_topic_ids = {
    topic.get("id")
    for topic in topics
    if topic.get("id") is not None
}


due_revisions = [
    revision
    for revision in due_revisions
    if revision.get(
        "topic_id"
    ) in student_topic_ids
]


upcoming_revisions = [
    revision
    for revision in upcoming_revisions
    if revision.get(
        "topic_id"
    ) in student_topic_ids
]


# ============================================================
# REVISION SUMMARY METRICS
# ============================================================

due_count = len(
    due_revisions
)

upcoming_count = len(
    upcoming_revisions
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "🔴 Due Now",
        due_count
    )


with col2:

    st.metric(
        "📆 Next 7 Days",
        upcoming_count
    )


with col3:

    revision_records = 0


    for topic in topics:

        topic_id = topic.get(
            "id"
        )

        if topic_id is None:
            continue

        record = get_revision_record(
            topic_id
        )

        if record is not None:

            revision_records += 1


    st.metric(
        "🧠 Scheduled Topics",
        revision_records
    )


# ============================================================
# DUE REVISIONS
# ============================================================

if due_revisions:

    st.markdown(
        "### 🔴 Revisions Due Now"
    )

    st.warning(
        f"You have **{due_count}** topic(s) "
        "that need revision."
    )


    for revision in due_revisions:

        topic_name = revision.get(
            "topic_name",
            "Unknown Topic"
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

        next_review = revision.get(
            "next_review_date"
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


        # ====================================================
        # CALCULATE OVERDUE DAYS
        # ====================================================

        overdue_days = 0


        if next_review:

            try:

                review_date = datetime.strptime(
                    str(next_review),
                    "%Y-%m-%d"
                ).date()

                overdue_days = max(
                    (
                        date.today()
                        - review_date
                    ).days,
                    0
                )

            except ValueError:

                overdue_days = 0


        with st.container(
            border=True
        ):

            st.markdown(
                f"#### 📖 {topic_name}"
            )

            st.caption(
                f"{unit} • Priority: {priority}"
            )


            col1, col2, col3, col4 = (
                st.columns(4)
            )


            with col1:

                st.metric(
                    "Mastery",
                    f"{mastery:.0f}%"
                )


            with col2:

                st.metric(
                    "Revision Streak",
                    streak
                )


            with col3:

                st.metric(
                    "Interval",
                    f"{interval} day(s)"
                )


            with col4:

                if overdue_days > 0:

                    st.metric(
                        "Overdue",
                        f"{overdue_days} day(s)"
                    )

                else:

                    st.metric(
                        "Status",
                        "Due today"
                    )


            st.write(
                f"**Next review:** "
                f"{next_review}"
            )


else:

    st.success(
        "🎉 No revisions are currently due."
    )


# ============================================================
# UPCOMING REVISIONS
# ============================================================

st.markdown(
    "### 📆 Upcoming Revisions"
)


if upcoming_revisions:

    for revision in upcoming_revisions:

        topic_name = revision.get(
            "topic_name",
            "Unknown Topic"
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

        next_review = revision.get(
            "next_review_date"
        )

        interval = int(
            revision.get(
                "review_interval_days",
                0
            )
            or 0
        )

        streak = int(
            revision.get(
                "revision_streak",
                0
            )
            or 0
        )


        with st.container(
            border=True
        ):

            col1, col2, col3, col4 = (
                st.columns(4)
            )


            with col1:

                st.markdown(
                    f"**📖 {topic_name}**"
                )

                st.caption(
                    unit
                )


            with col2:

                st.metric(
                    "Mastery",
                    f"{mastery:.0f}%"
                )


            with col3:

                st.metric(
                    "Next Review",
                    str(next_review)
                )


            with col4:

                st.metric(
                    "Streak",
                    streak
                )


            st.caption(
                f"Current revision interval: "
                f"{interval} day(s)"
            )


else:

    st.info(
        "No revisions are scheduled within "
        "the next 7 days."
    )


st.divider()


# ============================================================
# AI ADAPTIVE RECOMMENDATION
# ============================================================

st.subheader(
    "✨ AI Study Recommendation"
)


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

    st.stop()


# ============================================================
# EXTRACT RECOMMENDATION DATA
# ============================================================

recommended_topic = (
    recommendation.get(
        "topic"
    )
    or ""
)


progress = recommendation.get(
    "progress"
)


adaptive_score = float(
    recommendation.get(
        "adaptive_score",
        0.0
    )
    or 0.0
)


action = (
    recommendation.get(
        "action"
    )
    or "CONTINUE"
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


# ============================================================
# SAFETY CHECK
# ============================================================

if not topic_data:

    st.error(
        "The recommendation was generated, "
        "but topic information is unavailable."
    )

    st.stop()


# ============================================================
# RECOMMENDED TOPIC DATA
# ============================================================

mastery = float(
    getattr(
        progress,
        "score_percentage",
        topic_data.get(
            "mastery",
            0
        )
    )
    or 0
)


priority = (
    topic_data.get(
        "priority"
    )
    or "MEDIUM"
)


# ============================================================
# RECOMMENDED TOPIC
# ============================================================

st.markdown(
    f"### 🎯 Next Topic: {recommended_topic}"
)

st.caption(
    f"Priority: {priority}"
)


# ============================================================
# RECOMMENDATION METRICS
# ============================================================

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


# ============================================================
# SPACED-REPETITION RECOMMENDATION
# ============================================================

st.markdown(
    "### 🧠 Spaced-Repetition Recommendation"
)


recommended_topic_id = topic_data.get(
    "id"
)


revision_record = None


if recommended_topic_id is not None:

    revision_record = get_revision_record(
        recommended_topic_id
    )


# ============================================================
# PERSISTED REVISION STREAK
# ============================================================

revision_streak = 0


if revision_record:

    revision_streak = int(
        revision_record.get(
            "revision_streak",
            0
        )
        or 0
    )


# ============================================================
# CALCULATE REVISION RECOMMENDATION
# ============================================================

revision_recommendation = (
    get_revision_recommendation(

        score_percentage=mastery,

        revision_streak=revision_streak,
    )
)


revision_interval = int(
    revision_recommendation.get(
        "interval_days",
        0
    )
    or 0
)


revision_urgency = (
    revision_recommendation.get(
        "urgency",
        "LOW"
    )
    or "LOW"
)


revision_reason = (
    revision_recommendation.get(
        "reason",
        ""
    )
    or ""
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Review Interval",
        f"{revision_interval} day(s)"
    )


with col2:

    st.metric(
        "Revision Streak",
        revision_streak
    )


with col3:

    st.metric(
        "Urgency",
        revision_urgency
    )


# ============================================================
# URGENCY DISPLAY
# ============================================================

if revision_urgency == "HIGH":

    st.error(
        f"🔴 **High Priority Revision**\n\n"
        f"{revision_reason}"
    )

elif revision_urgency == "MEDIUM":

    st.warning(
        f"🟡 **Medium Priority Revision**\n\n"
        f"{revision_reason}"
    )

else:

    st.success(
        f"🟢 **Low Priority Revision**\n\n"
        f"{revision_reason}"
    )


# ============================================================
# EXISTING PERSISTED REVISION RECORD
# ============================================================

if revision_record:

    next_review = revision_record.get(
        "next_review_date"
    )

    last_reviewed = revision_record.get(
        "last_reviewed_at"
    )

    stored_interval = revision_record.get(
        "review_interval_days"
    )


    st.caption(
        f"Last reviewed: "
        f"{last_reviewed or 'Not recorded'}"
    )

    st.caption(
        f"Scheduled next review: "
        f"{next_review or 'Not scheduled'}"
    )


    if stored_interval is not None:

        st.caption(
            f"Stored revision interval: "
            f"{stored_interval} day(s)"
        )


else:

    st.info(
        "No revision record exists yet for this topic. "
        "A revision schedule will be created after "
        "a quiz result is recorded."
    )


st.divider()


# ============================================================
# EXPLAINABLE RECOMMENDATION
# ============================================================

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


# ============================================================
# AI RECOMMENDATION PERFORMANCE SIGNAL
# ============================================================

st.markdown(
    "#### 🤖 Recommendation Performance Signal"
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
            "a performance change yet."
        )


# ============================================================
# RECOMMENDED ACTION
# ============================================================

st.markdown(
    "#### 🧭 Recommended Action"
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
# CONTINUE STUDYING
# ============================================================

st.divider()

st.subheader(
    "🎯 What should you do next?"
)

st.write(
    f"📚 Continue studying **{recommended_topic}**."
)


# ============================================================
# CONTINUE STUDYING BUTTON
# ============================================================

if st.button(
    "📚 Continue Studying",
    type="primary",
    use_container_width=True,
    key="continue_studying_button"
):

    # ========================================================
    # EXTRACT TOPIC INFORMATION
    # ========================================================

    topic_id = topic_data.get(
        "id"
    )

    topic_name = topic_data.get(
        "name",
        recommended_topic
    )

    subject_id = topic_data.get(
        "subject_id"
    )

    subject_name = topic_data.get(
        "subject_name",
        ""
    )


    # ========================================================
    # VALIDATE REQUIRED INFORMATION
    # ========================================================

    if topic_id is None:

        st.error(
            "Unable to continue because "
            "the recommended topic ID is missing."
        )

        st.stop()


    if subject_id is None:

        st.error(
            "Unable to continue because "
            "the subject ID is missing."
        )

        st.stop()


    # ========================================================
    # STORE LEARNING TRANSITION CONTEXT
    # ========================================================

    st.session_state[
        "learning_transition_context"
    ] = {

        "subject_id":
            subject_id,

        "subject_name":
            subject_name,

        "topic_id":
            topic_id,

        "topic_name":
            topic_name,
    }


    # ========================================================
    # DIRECT LEARNING CONTEXT
    # ========================================================

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


    # ========================================================
    # NAVIGATE TO LEARN
    # ========================================================

    st.switch_page(
        "pages/2_📖_Learn.py"
    )