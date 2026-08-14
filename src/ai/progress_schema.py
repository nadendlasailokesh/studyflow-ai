from typing import Literal

from pydantic import BaseModel, Field


# ============================================================
# TOPIC PROGRESS
# ============================================================

class TopicProgress(BaseModel):

    topic: str

    attempts: int = Field(
        default=0,
        ge=0
    )

    correct_answers: int = Field(
        default=0,
        ge=0
    )

    total_questions: int = Field(
        default=0,
        ge=0
    )

    score_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0
    )

    status: Literal[
        "NOT_STARTED",
        "WEAK",
        "AVERAGE",
        "STRONG"
    ] = "NOT_STARTED"


# ============================================================
# PROGRESS SUMMARY
# ============================================================

class ProgressSummary(BaseModel):

    subject: str

    topics: list[TopicProgress]