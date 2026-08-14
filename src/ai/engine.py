from src.ai.client import ai_client

from src.ai.prompts import (
    STUDY_PLAN_SYSTEM_PROMPT,
    build_study_plan_prompt
)

from src.ai.schemas import StudyPlan


def generate_study_plan(
    subject_name,
    exam_date,
    daily_hours,
    goal
):

    user_prompt = build_study_plan_prompt(
        subject_name=subject_name,
        exam_date=exam_date,
        daily_hours=daily_hours,
        goal=goal
    )

    prompt = f"""
{STUDY_PLAN_SYSTEM_PROMPT}

{user_prompt}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "title": "Study plan title",
    "summary": "Short explanation of the plan",
    "tasks": [
        {{
            "topic": "Topic name",
            "activity": "What the student should do",
            "duration_minutes": 30
        }}
    ]
}}
"""

    response = ai_client.generate(
        prompt
    )

    return StudyPlan.model_validate_json(
        response
    )