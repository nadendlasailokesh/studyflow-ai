import json
import re

from pydantic import ValidationError

from src.ai.client import ai_client

from src.ai.prompts import (
    QUIZ_SYSTEM_PROMPT,
    build_quiz_prompt,
    JSON_OUTPUT_RULES
)

from src.ai.quiz_schema import Quiz


def _clean_response(response: str) -> str:

    if not response:
        raise ValueError(
            "AI returned an empty response."
        )

    response = response.strip()

    # Remove Markdown code fences
    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"\s*```$",
        "",
        response
    )

    response = response.strip()

    # Sometimes the model adds text before/after JSON.
    # Extract the outermost JSON object.
    start = response.find("{")
    end = response.rfind("}")

    if start != -1 and end != -1 and end > start:

        response = response[start:end + 1]

    return response.strip()


def _build_quiz_request(
    subject_name,
    unit,
    topic,
    difficulty,
    number_of_questions
):

    user_prompt = build_quiz_prompt(
        subject_name=subject_name,
        unit=unit,
        topic=topic,
        difficulty=difficulty,
        number_of_questions=number_of_questions
    )

    return f"""
{QUIZ_SYSTEM_PROMPT}

{JSON_OUTPUT_RULES}

{user_prompt}

Return EXACTLY this JSON structure:

{{
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "correct_answer": "Option A",
            "explanation": "Short explanation"
        }}
    ]
}}

IMPORTANT:

- Return exactly {number_of_questions} questions.
- Every question MUST have exactly 4 options.
- The correct_answer MUST exactly match one option.
- Keep explanations short and concise.
- Do not include Markdown.
- Do not include code fences.
- Do not include any text outside the JSON.
"""


def _validate_quiz(
    response,
    expected_questions
):

    cleaned = _clean_response(response)

    # First validate JSON itself
    try:

        data = json.loads(cleaned)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"AI returned invalid JSON: {error}"
        ) from error

    # Validate Pydantic schema
    try:

        quiz = Quiz.model_validate(data)

    except ValidationError as error:

        raise ValueError(
            f"Quiz structure is invalid: {error}"
        ) from error

    # Verify question count
    if len(quiz.questions) != expected_questions:

        raise ValueError(
            f"Expected {expected_questions} questions, "
            f"but AI returned {len(quiz.questions)}."
        )

    # Verify every question
    for index, question in enumerate(
        quiz.questions,
        start=1
    ):

        if len(question.options) != 4:

            raise ValueError(
                f"Question {index} must have "
                f"exactly 4 options."
            )

        if question.correct_answer not in question.options:

            raise ValueError(
                f"Question {index} has a correct_answer "
                f"that does not match any option."
            )

    return quiz


def generate_quiz(
    subject_name,
    unit,
    topic,
    difficulty="MEDIUM",
    number_of_questions=5
):

    prompt = _build_quiz_request(
        subject_name=subject_name,
        unit=unit,
        topic=topic,
        difficulty=difficulty,
        number_of_questions=number_of_questions
    )

    errors = []

    # Retry because AI responses can occasionally
    # be truncated or malformed.
    for attempt in range(1, 4):

        try:

            print(
                f"Generating quiz "
                f"(attempt {attempt}/3)"
            )

            response = ai_client.generate(
                prompt
            )

            quiz = _validate_quiz(
                response,
                expected_questions=number_of_questions
            )

            print(
                "Quiz generated successfully."
            )

            return quiz

        except Exception as error:

            print(
                f"Quiz generation attempt "
                f"{attempt} failed: {error}"
            )

            errors.append(
                f"Attempt {attempt}: {error}"
            )

    raise RuntimeError(
        "Unable to generate a valid quiz after "
        "3 attempts.\n\n"
        + "\n".join(errors)
    )