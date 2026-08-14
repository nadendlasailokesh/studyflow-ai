import json

from src.ai.client import ai_client

from src.ai.learning_schema import (
    LearningContent
)

from src.ai.prompts import (
    LEARNING_CONTENT_SYSTEM_PROMPT,
    build_learning_content_prompt
)


def _clean_response(response):
    """
    Clean AI response by removing Markdown
    code fences if the model adds them.
    """

    response = response.strip()

    if response.startswith("```json"):
        response = response[len("```json"):].strip()

    elif response.startswith("```"):
        response = response[len("```"):].strip()

    if response.endswith("```"):
        response = response[:-3].strip()

    return response


def generate_learning_content(
    subject_name,
    unit,
    topic,
    prerequisites=None
):
    """
    Generate structured learning content for a topic.
    """

    # -----------------------------------
    # Build user prompt
    # -----------------------------------

    user_prompt = build_learning_content_prompt(
        subject_name=subject_name,
        unit=unit,
        topic=topic,
        prerequisites=prerequisites
    )

    # -----------------------------------
    # Complete AI prompt
    # -----------------------------------

    prompt = f"""
{LEARNING_CONTENT_SYSTEM_PROMPT}

{user_prompt}

Create student-friendly study material.

The content should help a student:

1. Understand the topic easily.
2. Learn the important concepts.
3. Prepare for university examinations.
4. Remember the topic using a simple memory tip.
5. Avoid common mistakes.
6. Test their understanding using a quick-check question.

Return ONLY valid JSON.

Do NOT use Markdown code fences.

Use EXACTLY this structure:

{{
    "subject": "{subject_name}",
    "unit": "{unit}",
    "topic": "{topic}",
    "simple_explanation": "Explain the topic in simple language.",
    "key_concepts": [
        "Important concept 1",
        "Important concept 2",
        "Important concept 3"
    ],
    "examples": [
        "Example 1",
        "Example 2"
    ],
    "exam_definition": "A concise exam-ready definition.",
    "important_points": [
        "Important exam point 1",
        "Important exam point 2"
    ],
    "common_mistakes": [
        "Common mistake 1",
        "Common mistake 2"
    ],
    "memory_tip": "A simple way to remember the topic.",
    "quick_check_question": "A question to check understanding.",
    "quick_check_answer": "The correct answer.",
    "estimated_minutes": 30
}}
"""

    # -----------------------------------
    # Call AI
    # -----------------------------------

    response = ai_client.generate(
        prompt
    )

    # -----------------------------------
    # Clean AI response
    # -----------------------------------

    response = _clean_response(
        response
    )

    # -----------------------------------
    # Parse JSON
    # -----------------------------------

    try:

        data = json.loads(
            response
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "AI returned invalid JSON "
            "for learning content."
        ) from error

    # -----------------------------------
    # Ensure required values
    # -----------------------------------

    if not data.get("subject"):
        data["subject"] = subject_name

    if not data.get("unit"):
        data["unit"] = unit

    if not data.get("topic"):
        data["topic"] = topic

    # -----------------------------------
    # Backward compatibility
    # -----------------------------------

    # Older AI responses may return
    # "key_points" instead of "key_concepts".

    if (
        "key_concepts" not in data
        and "key_points" in data
    ):

        data["key_concepts"] = (
            data["key_points"]
        )

    # Older AI responses may return
    # a single "example" instead of
    # an "examples" list.

    if (
        "examples" not in data
        and "example" in data
    ):

        data["examples"] = [
            data["example"]
        ]

    # Older AI responses may return
    # "important_points".

    if "important_points" not in data:

        data["important_points"] = []

    # -----------------------------------
    # Safe defaults
    # -----------------------------------

    if "key_concepts" not in data:

        data["key_concepts"] = []

    if "examples" not in data:

        data["examples"] = []

    if "common_mistakes" not in data:

        data["common_mistakes"] = []

    if "memory_tip" not in data:

        data["memory_tip"] = ""

    if "quick_check_question" not in data:

        data["quick_check_question"] = ""

    if "quick_check_answer" not in data:

        data["quick_check_answer"] = ""

    if "exam_definition" not in data:

        data["exam_definition"] = ""

    if "simple_explanation" not in data:

        data["simple_explanation"] = ""

    if "estimated_minutes" not in data:

        data["estimated_minutes"] = 30

    # -----------------------------------
    # Validate with Pydantic
    # -----------------------------------

    return LearningContent.model_validate(
        data
    )