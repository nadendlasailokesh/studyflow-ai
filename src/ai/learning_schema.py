from pydantic import BaseModel, Field


class LearningContent(BaseModel):

    subject: str

    unit: str = ""

    topic: str

    simple_explanation: str

    key_concepts: list[str]

    examples: list[str]

    exam_definition: str

    important_points: list[str]

    common_mistakes: list[str]

    memory_tip: str

    quick_check_question: str

    quick_check_answer: str

    estimated_minutes: int = Field(
        default=30,
        ge=1
    )

    @property
    def key_points(self) -> list[str]:
        """
        Backward-compatible alias.

        Older parts of StudyFlow AI use `key_points`,
        while the current schema uses `key_concepts`.
        """
        return self.key_concepts