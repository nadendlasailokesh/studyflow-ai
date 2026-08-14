from src.ai.recommendation import (
    build_topic_recommendations,
    get_top_recommendation,
)


def test_recommendations():

    topics = [

        {
            "id": 1,
            "name": "Decision Trees",
            "unit": "Unit 2",
            "priority": "HIGH",
            "mastery": 90,
            "status": "STRONG",
        },

        {
            "id": 2,
            "name": "Entropy",
            "unit": "Unit 2",
            "priority": "HIGH",
            "mastery": 30,
            "status": "WEAK",
        },

        {
            "id": 3,
            "name": "Clustering",
            "unit": "Unit 3",
            "priority": "MEDIUM",
            "mastery": 65,
            "status": "AVERAGE",
        },
    ]

    recommendations = (
        build_topic_recommendations(
            topics
        )
    )

    assert len(recommendations) == 3

    assert (
        recommendations[0]["topic"]
        == "Entropy"
    )


def test_top_recommendation():

    topics = [

        {
            "id": 1,
            "name": "Decision Trees",
            "unit": "Unit 2",
            "priority": "HIGH",
            "mastery": 90,
            "status": "STRONG",
        },

        {
            "id": 2,
            "name": "Entropy",
            "unit": "Unit 2",
            "priority": "HIGH",
            "mastery": 30,
            "status": "WEAK",
        },
    ]

    recommendation = (
        get_top_recommendation(
            topics
        )
    )

    assert recommendation is not None

    assert (
        recommendation["topic"]
        == "Entropy"
    )

    assert (
        recommendation["action"]["action"]
        == "RELEARN"
    )