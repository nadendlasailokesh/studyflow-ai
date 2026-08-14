import json

from src.ai.providers.gemini import GeminiProvider
from src.ai.providers.groq import GroqProvider
from src.ai.providers.openrouter import OpenRouterProvider

from src.ai.learning_schema import (
    LearningContent
)


SYSTEM_PROMPT = """
You are an expert educational AI tutor.

Your job is to create study material that
college students can easily understand.

Rules:

1. Explain concepts using simple language.
2. Start from the basics.
3. Use practical examples.
4. Highlight important exam concepts.
5. Include an exam-ready definition.
6. Mention common mistakes.
7. Give a useful memory trick.
8. End with a quick-check question.
9. Do not invent syllabus-specific facts.
10. Return ONLY valid JSON.

The JSON must contain:

subject
topic
simple_explanation
key_concepts
examples
exam_definition
important_points
common_mistakes
memory_tip
quick_check_question
quick_check_answer
estimated_minutes
"""


def _build_prompt(
    subject,
    topic
):

    return f"""
{SYSTEM_PROMPT}

Subject:
{subject}

Topic:
{topic}

Generate structured learning content
for this topic.
"""


def _clean_json_response(
    response
):

    response = response.strip()

    if response.startswith(
        "```json"
    ):

        response = response[
            7:
        ]

    elif response.startswith(
        "```"
    ):

        response = response[
            3:
        ]

    if response.endswith(
        "```"
    ):

        response = response[
            :-3
        ]

    return response.strip()


def _providers():

    return [

        (
            "Gemini",
            GeminiProvider()
        ),

        (
            "Groq",
            GroqProvider()
        ),

        (
            "OpenRouter",
            OpenRouterProvider()
        )
    ]


def generate_learning_content(
    subject,
    topic
):

    prompt = _build_prompt(
        subject,
        topic
    )

    errors = []

    for provider_name, provider in _providers():

        try:

            print(
                f"Trying learning provider: "
                f"{provider_name}"
            )

            response = provider.generate(
                prompt
            )

            cleaned = _clean_json_response(
                response
            )

            data = json.loads(
                cleaned
            )

            content = (
                LearningContent.model_validate(
                    data
                )
            )

            print(
                f"Learning provider used: "
                f"{provider_name}"
            )

            return content

        except Exception as error:

            errors.append(
                f"{provider_name}: {error}"
            )

    raise RuntimeError(
        "All AI learning providers failed.\n"
        + "\n".join(errors)
    )