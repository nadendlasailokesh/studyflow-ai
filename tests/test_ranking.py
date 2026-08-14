from src.ai.ranking import rank_topics
from src.ai.syllabus_schema import (
    SyllabusAnalysis,
    TopicAnalysis
)


def test_topic_ranking():

    analysis = SyllabusAnalysis(

        subject="Data Mining",

        overview="Test analysis",

        topics=[

            TopicAnalysis(
                topic="Introduction",
                unit="Unit 1",
                priority="HIGH",
                reason="Foundation",
                estimated_minutes=60,
                prerequisites=[]
            ),

            TopicAnalysis(
                topic="Decision Trees",
                unit="Unit 2",
                priority="HIGH",
                reason="Important algorithm",
                estimated_minutes=90,
                prerequisites=[
                    "Classification"
                ]
            ),

            TopicAnalysis(
                topic="K-Means",
                unit="Unit 3",
                priority="MEDIUM",
                reason="Clustering technique",
                estimated_minutes=60,
                prerequisites=[
                    "Clustering"
                ]
            ),

            TopicAnalysis(
                topic="Revision",
                unit="Unit 3",
                priority="LOW",
                reason="Quick revision",
                estimated_minutes=30,
                prerequisites=[]
            )
        ]
    )


    ranked = rank_topics(
        analysis
    )


    assert len(ranked) == 4

    assert ranked[0]["score"] >= ranked[-1]["score"]

    assert "final_priority" in ranked[0]