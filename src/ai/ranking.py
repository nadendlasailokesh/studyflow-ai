from typing import Dict, List

from src.ai.syllabus_schema import (
    SyllabusAnalysis,
    TopicAnalysis
)


# ============================================================
# PRIORITY SCORES
# ============================================================

PRIORITY_BASE_SCORE = {
    "HIGH": 3.0,
    "MEDIUM": 2.0,
    "LOW": 1.0
}


# ============================================================
# NORMALIZE TOPIC NAME
# ============================================================

def normalize_topic_name(name: str) -> str:

    return (
        name
        .strip()
        .lower()
    )


# ============================================================
# CALCULATE BASE TOPIC SCORE
# ============================================================

def calculate_topic_score(
    topic: TopicAnalysis
) -> float:

    score = PRIORITY_BASE_SCORE.get(
        topic.priority,
        1.0
    )

    # Complex topics deserve additional
    # consideration during planning.
    if topic.estimated_minutes >= 120:

        score += 0.5

    elif topic.estimated_minutes >= 90:

        score += 0.25

    return score


# ============================================================
# BUILD TOPIC LOOKUP
# ============================================================

def build_topic_lookup(
    analysis: SyllabusAnalysis
) -> Dict[str, TopicAnalysis]:

    lookup = {}

    for topic in analysis.topics:

        key = normalize_topic_name(
            topic.topic
        )

        lookup[key] = topic

    return lookup


# ============================================================
# CALCULATE DEPENDENCY DEPTH
# ============================================================

def calculate_dependency_depth(
    topic: TopicAnalysis,
    lookup: Dict[str, TopicAnalysis],
    visited=None
) -> int:

    if visited is None:

        visited = set()

    topic_key = normalize_topic_name(
        topic.topic
    )

    # Prevent circular dependency loops.
    if topic_key in visited:

        return 0

    visited.add(
        topic_key
    )

    max_depth = 0

    for prerequisite in topic.prerequisites:

        prerequisite_key = (
            normalize_topic_name(
                prerequisite
            )
        )

        prerequisite_topic = lookup.get(
            prerequisite_key
        )

        if prerequisite_topic is None:

            continue

        depth = (
            1
            + calculate_dependency_depth(
                prerequisite_topic,
                lookup,
                visited.copy()
            )
        )

        max_depth = max(
            max_depth,
            depth
        )

    return max_depth


# ============================================================
# CALCULATE FINAL SCORE
# ============================================================

def calculate_final_score(
    topic: TopicAnalysis,
    lookup: Dict[str, TopicAnalysis]
) -> float:

    score = calculate_topic_score(
        topic
    )

    dependency_depth = (
        calculate_dependency_depth(
            topic,
            lookup
        )
    )

    # Foundational prerequisites should be
    # learned before dependent topics.
    #
    # Therefore we do NOT simply increase the
    # score of a topic because it has prerequisites.
    #
    # Instead, dependency depth is used later
    # for ordering.

    return score


# ============================================================
# TOPOLOGICAL ORDERING
# ============================================================

def order_by_dependencies(
    topics: List[TopicAnalysis]
) -> List[TopicAnalysis]:

    lookup = {
        normalize_topic_name(topic.topic): topic
        for topic in topics
    }

    ordered = []

    visited = set()
    visiting = set()

    def visit(topic):

        key = normalize_topic_name(
            topic.topic
        )

        if key in visited:
            return

        # Circular dependency detected.
        if key in visiting:
            return

        visiting.add(key)

        for prerequisite in topic.prerequisites:

            prerequisite_key = (
                normalize_topic_name(
                    prerequisite
                )
            )

            prerequisite_topic = lookup.get(
                prerequisite_key
            )

            if prerequisite_topic:

                visit(
                    prerequisite_topic
                )

        visiting.remove(key)

        visited.add(key)

        ordered.append(topic)

    for topic in topics:

        visit(topic)

    return ordered


# ============================================================
# RANK TOPICS
# ============================================================

def rank_topics(
    analysis: SyllabusAnalysis
):

    lookup = build_topic_lookup(
        analysis
    )

    ranked_topics = []

    for topic in analysis.topics:

        score = calculate_final_score(
            topic,
            lookup
        )

        dependency_depth = (
            calculate_dependency_depth(
                topic,
                lookup
            )
        )

        ranked_topics.append(
            {
                "topic": topic,
                "score": score,
                "dependency_depth": dependency_depth,
                "final_priority": topic.priority
            }
        )

    # --------------------------------------------------------
    # First sort by dependency order.
    # --------------------------------------------------------

    dependency_order = (
        order_by_dependencies(
            analysis.topics
        )
    )

    dependency_position = {
        normalize_topic_name(topic.topic): index
        for index, topic
        in enumerate(dependency_order)
    }

    # --------------------------------------------------------
    # Final sorting
    # --------------------------------------------------------

    ranked_topics.sort(
        key=lambda item: (
            dependency_position.get(
                normalize_topic_name(
                    item["topic"].topic
                ),
                9999
            ),

            -item["score"]
        )
    )

    return ranked_topics