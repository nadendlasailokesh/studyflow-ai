from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


# ============================================================
# TOPIC ANALYSIS
# ============================================================

class TopicAnalysis(BaseModel):

    topic: str = Field(
        min_length=2,
        max_length=200
    )

    unit: str = Field(
        min_length=1,
        max_length=50
    )

    priority: Literal[
        "HIGH",
        "MEDIUM",
        "LOW"
    ]

    reason: str = Field(
        min_length=5,
        max_length=500
    )

    estimated_minutes: int = Field(
        ge=15,
        le=600
    )

    prerequisites: List[str] = Field(
        default_factory=list
    )

    @field_validator("topic", "unit", "reason")
    @classmethod
    def clean_text(cls, value):
        return value.strip()

    @field_validator("prerequisites")
    @classmethod
    def clean_prerequisites(cls, values):

        cleaned = []

        for value in values:

            value = value.strip()

            if value and value not in cleaned:
                cleaned.append(value)

        return cleaned


# ============================================================
# SYLLABUS ANALYSIS
# ============================================================

class SyllabusAnalysis(BaseModel):

    subject: str = Field(
        min_length=2,
        max_length=200
    )

    overview: str = Field(
        min_length=10
    )

    topics: List[TopicAnalysis] = Field(
        min_length=1
    )

    @field_validator("subject", "overview")
    @classmethod
    def clean_main_text(cls, value):
        return value.strip()