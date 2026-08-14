from src.ai.schemas import StudyPlan
from src.ai.engine import generate_study_plan


def test_study_plan_generation(monkeypatch):

    mock_response = """
    {
        "title": "Data Mining Exam Plan",
        "summary": "A focused study plan for the Data Mining exam.",
        "tasks": [
            {
                "topic": "Classification",
                "activity": "Study classification concepts and examples.",
                "duration_minutes": 45
            },
            {
                "topic": "Clustering",
                "activity": "Learn clustering techniques and practice questions.",
                "duration_minutes": 45
            }
        ]
    }
    """


    def mock_generate(prompt):

        return mock_response


    monkeypatch.setattr(
        "src.ai.engine.ai_client.generate",
        mock_generate
    )


    plan = generate_study_plan(

        subject_name="Data Mining",

        exam_date="2026-09-15",

        daily_hours=2,

        goal=(
            "Understand important concepts "
            "and prepare for the exam."
        )
    )


    assert isinstance(
        plan,
        StudyPlan
    )

    assert plan.title == "Data Mining Exam Plan"

    assert len(plan.tasks) == 2

    assert plan.tasks[0].topic == "Classification"