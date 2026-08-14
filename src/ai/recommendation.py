from src.ai.adaptive_planner import (
    prioritize_topics,
    get_adaptive_action,
)

from src.ai.progress_schema import (
    TopicProgress,
)


def build_topic_recommendations(
    topics
):
    """
    Convert database topics into the format
    expected by the adaptive planner.
    """

    adaptive_topics = []

    for topic in topics:

        mastery = (
            topic["mastery"]
            if topic["mastery"] is not None
            else 0.0
        )

        status = topic["status"]

        if not status:

            if mastery >= 80:
                status = "STRONG"

            elif mastery >= 50:
                status = "AVERAGE"

            else:
                status = "WEAK"

        progress = TopicProgress(

            topic=topic["name"],

            attempts=0,

            correct_answers=0,

            total_questions=0,

            score_percentage=mastery,

            status=status,
        )

        priority = (
            topic["priority"]
            or "MEDIUM"
        )

        base_score = {
            "HIGH": 3.0,
            "High": 3.0,
            "MEDIUM": 2.0,
            "Medium": 2.0,
            "LOW": 1.0,
            "Low": 1.0,
        }.get(
            priority,
            1.0
        )

        adaptive_topics.append(
            {
                "topic": topic["name"],

                "topic_data": topic,

                "progress": progress,

                "base_score": base_score,
            }
        )

    ranked = prioritize_topics(
        adaptive_topics
    )

    return ranked
def get_top_recommendation(
    topics
):

    recommendations = (
        build_topic_recommendations(
            topics
        )
    )

    if not recommendations:
        return None

    top = recommendations[0]

    progress = top["progress"]

    action = get_adaptive_action(
        progress
    )

    return {
        "topic": top["topic"],

        "topic_data": top["topic_data"],

        "progress": progress,

        "adaptive_score": (
            top["adaptive_score"]
        ),

        "action": action,
    }