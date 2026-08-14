def generate_recommendation_reasons(recommendation):
    """
    Generate human-readable reasons explaining why
    a topic was selected by the adaptive planner.
    """

    if not recommendation:
        return []

    topic = recommendation.get("topic", "this topic")
    topic_data = recommendation.get("topic_data", {})

    progress = recommendation.get("progress")

    quiz_stats = recommendation.get(
        "quiz_stats",
        {}
    )

    improvement = float(
        recommendation.get(
            "improvement",
            0.0
        )
    )

    adaptive_score = float(
        recommendation.get(
            "adaptive_score",
            0.0
        )
    )

    reasons = []

    # --------------------------------------------------------
    # PRIORITY
    # --------------------------------------------------------

    priority = str(
        topic_data.get(
            "priority",
            "MEDIUM"
        )
    ).strip().upper()

    if priority == "HIGH":

        reasons.append(
            "⭐ This topic has HIGH priority in your syllabus."
        )

    elif priority == "MEDIUM":

        reasons.append(
            "📌 This topic has MEDIUM priority in your syllabus."
        )

    else:

        reasons.append(
            "📌 This topic has LOW priority in your syllabus."
        )

    # --------------------------------------------------------
    # MASTERY
    # --------------------------------------------------------

    mastery = 0.0

    if progress is not None:

        mastery = float(
            progress.score_percentage
        )

    if mastery == 0:

        reasons.append(
            "🔴 You have not demonstrated mastery of this topic yet."
        )

    elif mastery < 50:

        reasons.append(
            f"🔴 Your current mastery is only {mastery:.0f}%."
        )

    elif mastery < 80:

        reasons.append(
            f"🟡 Your current mastery is {mastery:.0f}%, "
            "so revision is recommended."
        )

    else:

        reasons.append(
            f"🟢 Your mastery is {mastery:.0f}%, "
            "but other factors increased this topic's priority."
        )

    # --------------------------------------------------------
    # QUIZ HISTORY
    # --------------------------------------------------------

    attempts = int(
        quiz_stats.get(
            "attempts",
            0
        )
    )

    accuracy = float(
        quiz_stats.get(
            "accuracy",
            0.0
        )
    )

    if attempts == 0:

        reasons.append(
            "📝 You have no quiz history for this topic yet."
        )

    else:

        reasons.append(
            f"📝 You have completed {attempts} quiz "
            f"attempt{'s' if attempts != 1 else ''} "
            f"with {accuracy:.0f}% historical accuracy."
        )

        if accuracy < 50:

            reasons.append(
                "🔴 Your quiz accuracy indicates that "
                "this topic needs additional practice."
            )

        elif accuracy < 80:

            reasons.append(
                "🟡 Your quiz performance suggests "
                "that this topic could benefit from revision."
            )

    # --------------------------------------------------------
    # PERFORMANCE TREND
    # --------------------------------------------------------

    if improvement > 0:

        reasons.append(
            f"📈 Your recent quiz performance improved "
            f"by {improvement:.0f}%."
        )

    elif improvement < 0:

        reasons.append(
            f"📉 Your recent quiz performance decreased "
            f"by {abs(improvement):.0f}%."
        )

        reasons.append(
            "⚠️ The recent decline increases the need "
            "to revisit this topic."
        )

    else:

        if attempts >= 2:

            reasons.append(
                "📊 Your recent quiz performance shows "
                "no significant change."
            )

    # --------------------------------------------------------
    # ADAPTIVE SCORE
    # --------------------------------------------------------

    reasons.append(
        f"🎯 The adaptive planner assigned this topic "
        f"a score of {adaptive_score:.2f}."
    )

    # --------------------------------------------------------
    # FINAL REASON
    # --------------------------------------------------------

    reasons.append(
        f"🧠 Based on these factors, **{topic}** "
        "was selected as your next recommended topic."
    )

    return reasons


def get_recommendation_summary(recommendation):
    """
    Generate a short one-line explanation.
    """

    if not recommendation:
        return "No recommendation is currently available."

    topic = recommendation.get(
        "topic",
        "this topic"
    )

    progress = recommendation.get("progress")

    mastery = 0.0

    if progress is not None:
        mastery = float(
            progress.score_percentage
        )

    topic_data = recommendation.get(
        "topic_data",
        {}
    )

    priority = str(
        topic_data.get(
            "priority",
            "MEDIUM"
        )
    ).upper()

    if mastery < 50 and priority == "HIGH":

        return (
            f"{topic} was selected because it has "
            "high syllabus priority and requires "
            "significant mastery improvement."
        )

    if mastery < 50:

        return (
            f"{topic} was selected because your "
            "current mastery needs improvement."
        )

    return (
        f"{topic} was selected based on your "
        "current learning progress and adaptive priority."
    )