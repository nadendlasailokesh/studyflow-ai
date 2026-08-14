from typing import List

from pydantic import BaseModel, Field


class TutorResponse(BaseModel):

    answer: str = Field(
        min_length=1
    )

    simple_explanation: str = Field(
        min_length=1
    )

    example: str = Field(
        min_length=1
    )

    key_points: List[str] = Field(
        min_length=1
    )

    follow_up_question: str = Field(
        min_length=1
    )