from typing import List

from pydantic import BaseModel


class StudySession(BaseModel):

    date: str

    topic: str

    unit: str

    activity: str

    duration_minutes: int


class PersonalizedStudyPlan(BaseModel):

    subject: str

    exam_date: str

    total_days: int

    total_minutes: int

    sessions: List[StudySession]