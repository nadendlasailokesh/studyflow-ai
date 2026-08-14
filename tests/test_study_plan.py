from src.ai.study_plan import (
    generate_personalized_plan
)

from src.ai.syllabus_schema import (
    SyllabusAnalysis,
    TopicAnalysis
)


def test_personalized_study_plan():

    analysis = SyllabusAnalysis(

        subject="Data Mining",

        overview="Test syllabus",

        topics=[

            TopicAnalysis(
                topic="Classification",
                unit="Unit 2",
                priority="HIGH",
                reason="Core topic",
                estimated_minutes=60,
                prerequisites=[]
            ),

            TopicAnalysis(
                topic="Clustering",
                unit="Unit 3",
                priority="MEDIUM",
                reason="Important topic",
                estimated_minutes=60,
                prerequisites=[]
            )
        ]
    )


    plan = generate_personalized_plan(

        analysis=analysis,

        exam_date="2026-09-15",

        daily_hours=2
    )


    assert plan.subject == "Data Mining"

    assert len(plan.sessions) > 0

    assert plan.total_minutes > 0

    assert all(
        session.duration_minutes > 0
        for session in plan.sessions
    )