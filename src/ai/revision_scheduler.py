# ============================================================
# REVISION SCHEDULER
# StudyFlow AI
# Phase 8.2 — Spaced Repetition
# ============================================================

from datetime import date, datetime, timedelta


# ============================================================
# REVIEW INTERVALS
# ============================================================

def calculate_review_interval(
    score_percentage,
    revision_streak=0,
):
    """
    Calculate the number of days until the next revision.

    Performance bands:

        < 50%    -> 1 day
        50-69%   -> 2 days
        70-79%   -> 4 days
        80-89%   -> 7 days
        >= 90%   -> 14 days

    A successful revision streak can extend the interval.

    Maximum interval = 30 days.
    """

    score = float(score_percentage)

    score = max(
        0.0,
        min(score, 100.0)
    )

    streak = max(
        0,
        int(revision_streak)
    )

    # --------------------------------------------------------
    # Weak performance
    # --------------------------------------------------------

    if score < 50:

        return 1

    # --------------------------------------------------------
    # Moderate performance
    # --------------------------------------------------------

    if score < 70:

        interval = 2

    elif score < 80:

        interval = 4

    elif score < 90:

        interval = 7

    else:

        interval = 14

    # --------------------------------------------------------
    # Streak extension
    #
    # Only strong performance benefits from a streak.
    # This prevents weak topics from being pushed too far
    # into the future.
    # --------------------------------------------------------

    if score >= 80 and streak > 1:

        interval = interval * (
            2 ** (streak - 1)
        )

    return min(
        interval,
        30
    )


# ============================================================
# NEXT REVIEW DATE
# ============================================================

def calculate_next_review_date(
    interval_days,
    start_date=None,
):
    """
    Calculate the next revision date.

    start_date can be:
        date
        datetime
        None -> today

    Returns:
        datetime.date
    """

    interval = max(
        0,
        int(interval_days)
    )

    if start_date is None:

        start = date.today()

    elif isinstance(
        start_date,
        datetime
    ):

        start = start_date.date()

    elif isinstance(
        start_date,
        date
    ):

        start = start_date

    else:

        raise TypeError(
            "start_date must be a date, "
            "datetime, or None."
        )

    return start + timedelta(
        days=interval
    )


# ============================================================
# REVISION RECOMMENDATION
# ============================================================

def get_revision_recommendation(
    score_percentage,
    revision_streak=0,
):
    """
    Return a complete revision recommendation.

    Returns:

        {
            "interval_days": int,
            "reason": str,
            "urgency": str
        }
    """

    score = float(score_percentage)

    score = max(
        0.0,
        min(score, 100.0)
    )

    interval = calculate_review_interval(
        score_percentage=score,
        revision_streak=revision_streak,
    )

    # --------------------------------------------------------
    # Weak
    # --------------------------------------------------------

    if score < 50:

        urgency = "HIGH"

        reason = (
            "Your performance is below 50%. "
            "Review this topic soon and practice "
            "the weak concepts."
        )

    # --------------------------------------------------------
    # Average
    # --------------------------------------------------------

    elif score < 70:

        urgency = "HIGH"

        reason = (
            "Your understanding is developing. "
            "Review this topic within a few days "
            "to strengthen retention."
        )

    elif score < 80:

        urgency = "MEDIUM"

        reason = (
            "You have a reasonable understanding, "
            "but another revision will help reinforce "
            "the concepts."
        )

    # --------------------------------------------------------
    # Strong
    # --------------------------------------------------------

    elif score < 90:

        urgency = "LOW"

        reason = (
            "Your performance is strong. "
            "A later revision is sufficient "
            "to maintain retention."
        )

    else:

        urgency = "LOW"

        reason = (
            "Your performance is excellent. "
            "Revision can be spaced further apart "
            "while maintaining retention."
        )

    return {

        "interval_days": interval,

        "reason": reason,

        "urgency": urgency,
    }