from typing import List

from pydantic import BaseModel


class QuizQuestion(BaseModel):

    question: str

    options: List[str]

    correct_answer: str

    explanation: str


class Quiz(BaseModel):

    topic: str

    difficulty: str

    questions: List[QuizQuestion]