import json

from src.ai.client import ai_client

from src.ai.learning_schema import (
    LearningContent
)

from src.ai.prompts import (
    LEARNING_CONTENT_SYSTEM_PROMPT,
    build_learning_content_prompt
)


# ============================================================
# CLEAN AI RESPONSE
# ============================================================

def _clean_response(response):
    """
    Clean AI response by removing Markdown
    code fences and accidental text around JSON.
    """

    if not response:

        raise ValueError(
            "AI returned an empty response."
        )

    response = response.strip()

    # --------------------------------------------------------
    # Remove Markdown code fences
    # --------------------------------------------------------

    if response.startswith("```json"):

        response = response[
            len("```json"):
        ].strip()

    elif response.startswith("```"):

        response = response[
            len("```"):
        ].strip()

    if response.endswith("```"):

        response = response[
            :-3
        ].strip()

    # --------------------------------------------------------
    # Find JSON object
    # --------------------------------------------------------

    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1:

        raise ValueError(
            "AI response does not contain valid JSON."
        )

    return response[
        start:end + 1
    ]


# ============================================================
# NORMALIZE STRING LIST
# ============================================================

def _normalize_string_list(value):
    """
    Convert different AI response formats into list[str].

    Supported formats:

        ["Concept A", "Concept B"]

    and:

        [
            {
                "term": "Concept A",
                "explanation": "Explanation"
            }
        ]
    """

    if value is None:

        return []

    if isinstance(value, str):

        text = value.strip()

        if not text:
            return []

        return [text]

    if not isinstance(value, list):

        return [str(value)]

    normalized = []

    for item in value:

        # ----------------------------------------------------
        # Normal string
        # ----------------------------------------------------

        if isinstance(item, str):

            text = item.strip()

            if text:
                normalized.append(text)

            continue

        # ----------------------------------------------------
        # Structured object returned by newer AI responses
        # ----------------------------------------------------

        if isinstance(item, dict):

            term = item.get("term")

            explanation = item.get(
                "explanation"
            )

            if term and explanation:

                normalized.append(
                    f"{term}: {explanation}"
                )

            elif term:

                normalized.append(
                    str(term)
                )

            else:

                title = (
                    item.get("title")
                    or item.get("name")
                    or item.get("concept")
                )

                description = (
                    item.get("description")
                    or item.get("details")
                    or item.get("example")
                )

                if title and description:

                    normalized.append(
                        f"{title}: {description}"
                    )

                elif title:

                    normalized.append(
                        str(title)
                    )

                else:

                    normalized.append(
                        json.dumps(
                            item,
                            ensure_ascii=False
                        )
                    )

            continue

        # ----------------------------------------------------
        # Unexpected type
        # ----------------------------------------------------

        normalized.append(
            str(item)
        )

    return normalized


# ============================================================
# GENERATE LEARNING CONTENT
# ============================================================

def generate_learning_content(
    subject_name,
    unit,
    topic,
    prerequisites=None
):
    """
    Generate structured learning content for a topic.

    Supports both current and legacy AI response formats.
    """

    # --------------------------------------------------------
    # Build user prompt
    # --------------------------------------------------------

    user_prompt = build_learning_content_prompt(
        subject_name=subject_name,
        unit=unit,
        topic=topic,
        prerequisites=prerequisites
    )

    # --------------------------------------------------------
    # Complete AI prompt
    # --------------------------------------------------------

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

STRICT JSON REQUIREMENTS:

1. Return ONLY valid JSON.
2. Do NOT use Markdown code fences.
3. Do NOT add explanation outside JSON.
4. key_concepts MUST be an array of strings.
5. examples MUST be an array of strings.
6. important_points MUST be an array of strings.
7. common_mistakes MUST be an array of strings.
8. Do NOT return objects inside these arrays.

CORRECT:

"key_concepts": [
    "Regular expressions",
    "Finite automata",
    "Pattern matching"
]

NOT ALLOWED:

"key_concepts": [
    {{
        "term": "Regular expressions",
        "explanation": "..."
    }}
]

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

    # --------------------------------------------------------
    # Call AI
    # --------------------------------------------------------

    response = ai_client.generate(
        prompt
    )

    # --------------------------------------------------------
    # Clean response
    # --------------------------------------------------------

    response = _clean_response(
        response
    )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = json.loads(
            response
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "AI returned invalid JSON "
            "for learning content.\n\n"
            f"JSON error: {error}\n\n"
            f"AI response: {response}"
        ) from error

    # --------------------------------------------------------
    # Ensure dictionary
    # --------------------------------------------------------

    if not isinstance(data, dict):

        raise ValueError(
            "AI returned learning content "
            "in an invalid format."
        )

    # ========================================================
    # IDENTITY FIELDS
    # ========================================================

    if not data.get("subject"):

        data["subject"] = subject_name

    if not data.get("unit"):

        data["unit"] = unit

    if not data.get("topic"):

        data["topic"] = topic

    # ========================================================
    # LEGACY FIELD COMPATIBILITY
    # ========================================================

    # --------------------------------------------------------
    # key_points -> key_concepts
    # --------------------------------------------------------

    if (
        "key_concepts" not in data
        and "key_points" in data
    ):

        data["key_concepts"] = (
            data["key_points"]
        )

    # --------------------------------------------------------
    # example -> examples
    # --------------------------------------------------------

    if (
        "examples" not in data
        and "example" in data
    ):

        data["examples"] = [
            data["example"]
        ]

    # ========================================================
    # DEFAULT VALUES
    # ========================================================

    if "key_concepts" not in data:

        data["key_concepts"] = []

    if "examples" not in data:

        data["examples"] = []

    if "important_points" not in data:

        data["important_points"] = []

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

    # ========================================================
    # NORMALIZE LIST FIELDS
    # ========================================================

    data["key_concepts"] = _normalize_string_list(
        data["key_concepts"]
    )

    data["examples"] = _normalize_string_list(
        data["examples"]
    )

    data["important_points"] = _normalize_string_list(
        data["important_points"]
    )

    data["common_mistakes"] = _normalize_string_list(
        data["common_mistakes"]
    )

    # ========================================================
    # VALIDATE WITH PYDANTIC
    # ========================================================

    try:

        return LearningContent.model_validate(
            data
        )

    except Exception as error:

        raise ValueError(
            "AI returned invalid learning content.\n\n"
            f"Validation error:\n{error}\n\n"
            f"Normalized data:\n{data}"
        ) from error