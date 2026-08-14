from pydantic import BaseModel, Field
from typing import List


class StudyTask(BaseModel):

    topic: str

    activity: str

    duration_minutes: int = Field(
        ge=5,
        le=300
    )


class StudyPlan(BaseModel):

    title: str

    summary: str

    tasks: List[StudyTask]