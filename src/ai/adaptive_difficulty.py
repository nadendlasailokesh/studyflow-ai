# ============================================================
# ADAPTIVE DIFFICULTY ENGINE
# StudyFlow AI
#
# Phase 10.3
# Advanced AI Study Coach
# ============================================================


# ============================================================
# SUPPORTED DIFFICULTIES
# ============================================================

EASY = "EASY"
MEDIUM = "MEDIUM"
HARD = "HARD"


DIFFICULTY_LEVELS = {
    EASY: 0,
    MEDIUM: 1,
    HARD: 2,
}


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_float(
    value,
    default=0.0,
):
    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return float(default)


def _safe_int(
    value,
    default=0,
):
    try:
        return int(value)
    except (
        TypeError,
        ValueError,
    ):
        return int(default)


# ============================================================
# NORMALIZE DIFFICULTY
# ============================================================

def normalize_difficulty(
    difficulty,
):
    """
    Normalize a difficulty value.

    Unknown values fall back to MEDIUM.
    """

    normalized = str(
        difficulty or ""
    ).strip().upper()

    if normalized in DIFFICULTY_LEVELS:
        return normalized

    return MEDIUM


# ============================================================
# DIFFICULTY LEVEL
# ============================================================

def get_difficulty_level(
    difficulty,
):
    """
    Return numeric difficulty level.

    EASY   = 0
    MEDIUM = 1
    HARD   = 2
    """

    difficulty = normalize_difficulty(
        difficulty
    )

    return DIFFICULTY_LEVELS[
        difficulty
    ]


# ============================================================
# DIFFICULTY NAME
# ============================================================

def get_difficulty_from_level(
    level,
):
    """
    Convert numeric difficulty level
    back into EASY / MEDIUM / HARD.
    """

    level = max(
        0,
        min(
            2,
            _safe_int(level)
        )
    )

    for difficulty, value in DIFFICULTY_LEVELS.items():

        if value == level:
            return difficulty

    return MEDIUM


# ============================================================
# RECENT PERFORMANCE
# ============================================================

def get_recent_average(
    recent_performance,
    limit=3,
):
    """
    Calculate average score from recent attempts.

    recent_performance is expected to contain:

        {
            "score": 80.0
        }

    Newest attempts should normally appear first.
    """

    if not recent_performance:
        return None

    scores = []

    for attempt in recent_performance[:limit]:

        score = _safe_float(
            attempt.get(
                "score",
                attempt.get(
                    "accuracy",
                    0.0,
                ),
            )
        )

        scores.append(
            max(
                0.0,
                min(
                    score,
                    100.0,
                ),
            )
        )

    if not scores:
        return None

    return round(
        sum(scores) / len(scores),
        2,
    )


# ============================================================
# PERFORMANCE TREND
# ============================================================

def calculate_performance_trend(
    recent_performance,
):
    """
    Determine recent quiz direction.

    Returns:

        IMPROVING
        DECLINING
        STABLE
        INSUFFICIENT_DATA
    """

    if not recent_performance:
        return "INSUFFICIENT_DATA"

    if len(recent_performance) < 2:
        return "INSUFFICIENT_DATA"

    latest = _safe_float(
        recent_performance[0].get(
            "score",
            recent_performance[0].get(
                "accuracy",
                0.0,
            ),
        )
    )

    previous = _safe_float(
        recent_performance[1].get(
            "score",
            recent_performance[1].get(
                "accuracy",
                0.0,
            ),
        )
    )

    change = latest - previous

    if change >= 10:
        return "IMPROVING"

    if change <= -10:
        return "DECLINING"

    return "STABLE"


# ============================================================
# DETERMINE DIFFICULTY
# ============================================================

def determine_adaptive_difficulty(
    mastery,
    recent_performance=None,
    attempts=0,
    current_difficulty=MEDIUM,
):
    """
    Determine the next quiz difficulty.

    The decision considers:

        - current mastery
        - recent quiz scores
        - number of attempts
        - performance trend
        - current difficulty

    Difficulty changes gradually to avoid sudden jumps.
    """

    mastery = max(
        0.0,
        min(
            _safe_float(mastery),
            100.0,
        ),
    )

    attempts = max(
        0,
        _safe_int(attempts),
    )

    current_difficulty = normalize_difficulty(
        current_difficulty
    )

    recent_performance = (
        recent_performance
        or []
    )

    # --------------------------------------------------------
    # No evidence
    # --------------------------------------------------------

    if attempts == 0 and not recent_performance:

        return MEDIUM

    recent_average = get_recent_average(
        recent_performance
    )

    trend = calculate_performance_trend(
        recent_performance
    )

    # --------------------------------------------------------
    # Strong evidence of difficulty
    # --------------------------------------------------------

    if (
        mastery < 40
        or (
            recent_average is not None
            and recent_average < 40
        )
    ):

        # Do not jump below EASY.
        return EASY

    # --------------------------------------------------------
    # Declining performance
    # --------------------------------------------------------

    if trend == "DECLINING":

        if (
            recent_average is not None
            and recent_average < 60
        ):

            return EASY

        # A moderate decline should normally
        # reduce HARD to MEDIUM.
        if current_difficulty == HARD:

            return MEDIUM

    # --------------------------------------------------------
    # Strong performance
    # --------------------------------------------------------

    if (
        mastery >= 85
        and recent_average is not None
        and recent_average >= 80
        and attempts >= 2
    ):

        return HARD

    # --------------------------------------------------------
    # Good performance with sufficient evidence
    # --------------------------------------------------------

    if (
        mastery >= 70
        and recent_average is not None
        and recent_average >= 75
        and attempts >= 2
    ):

        # Gradually move upward.
        if current_difficulty == EASY:
            return MEDIUM

        if current_difficulty == MEDIUM:
            return HARD

        return HARD

    # --------------------------------------------------------
    # Improving performance
    # --------------------------------------------------------

    if trend == "IMPROVING":

        if (
            recent_average is not None
            and recent_average >= 70
            and attempts >= 2
        ):

            if current_difficulty == EASY:
                return MEDIUM

            if current_difficulty == MEDIUM:
                return HARD

    # --------------------------------------------------------
    # Moderate performance
    # --------------------------------------------------------

    if (
        mastery >= 40
        and mastery < 70
    ):

        return MEDIUM

    if (
        recent_average is not None
        and recent_average < 75
    ):

        return MEDIUM

    # --------------------------------------------------------
    # Safe fallback
    # --------------------------------------------------------

    return MEDIUM


# ============================================================
# DIFFICULTY RECOMMENDATION
# ============================================================

def get_adaptive_difficulty_recommendation(
    mastery,
    recent_performance=None,
    attempts=0,
    current_difficulty=MEDIUM,
):
    """
    Return structured adaptive difficulty information.

    This is the main public API for Phase 10.3.
    """

    difficulty = determine_adaptive_difficulty(
        mastery=mastery,
        recent_performance=recent_performance,
        attempts=attempts,
        current_difficulty=current_difficulty,
    )

    recent_average = get_recent_average(
        recent_performance or []
    )

    trend = calculate_performance_trend(
        recent_performance or []
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    mastery_value = _safe_float(
        mastery
    )

    if difficulty == EASY:

        if mastery_value < 40:

            reason = (
                "Your current mastery is low, "
                "so the quiz difficulty has been reduced "
                "to help strengthen the fundamentals."
            )

        elif trend == "DECLINING":

            reason = (
                "Your recent quiz performance is declining, "
                "so the difficulty has been reduced temporarily."
            )

        else:

            reason = (
                "Recent performance indicates that "
                "a lower difficulty will provide better "
                "learning support."
            )

    elif difficulty == HARD:

        if (
            mastery_value >= 85
            and recent_average is not None
            and recent_average >= 80
        ):

            reason = (
                "Your mastery and recent quiz performance "
                "are strong, so a harder challenge is appropriate."
            )

        else:

            reason = (
                "Your recent performance is strong enough "
                "to gradually increase the challenge."
            )

    else:

        if attempts == 0:

            reason = (
                "There is not enough quiz history yet, "
                "so MEDIUM difficulty is used as the starting point."
            )

        elif trend == "IMPROVING":

            reason = (
                "Your performance is improving, but more evidence "
                "is needed before increasing the difficulty further."
            )

        else:

            reason = (
                "Your current performance is at a moderate level, "
                "so MEDIUM difficulty is appropriate."
            )

    return {
        "difficulty": difficulty,
        "previous_difficulty": normalize_difficulty(
            current_difficulty
        ),
        "trend": trend,
        "recent_average": recent_average,
        "mastery": round(
            mastery_value,
            2,
        ),
        "attempts": attempts,
        "reason": reason,
    }