import json

from src.ai.client import ai_client

from src.ai.prompts import (
    TUTOR_SYSTEM_PROMPT,
    build_tutor_prompt
)

from src.ai.tutor_schema import TutorResponse


def clean_json_response(response: str) -> str:
    """
    Clean common formatting added by AI models.
    """

    response = response.strip()

    # Remove ```json
    if response.startswith("```json"):
        response = response[7:].strip()

    # Remove ```
    elif response.startswith("```"):
        response = response[3:].strip()

    if response.endswith("```"):
        response = response[:-3].strip()

    return response


def ask_tutor(
    subject_name,
    unit,
    topic,
    question,
    previous_context=None
):
    """
    Generate an AI Tutor response using:
    - subject
    - unit
    - current topic
    - student question
    - recent conversation
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if not topic or not topic.strip():
        raise ValueError(
            "A topic is required."
        )

    # --------------------------------------------------------
    # Build user prompt
    # --------------------------------------------------------

    user_prompt = build_tutor_prompt(
        subject_name=subject_name,
        unit=unit,
        topic=topic,
        question=question.strip(),
        previous_context=previous_context or []
    )

    # --------------------------------------------------------
    # Full AI prompt
    # --------------------------------------------------------

    prompt = f"""
{TUTOR_SYSTEM_PROMPT}

{user_prompt}

IMPORTANT INSTRUCTIONS:

1. Answer the student's question specifically about the
   CURRENT TOPIC.

2. Do not change the topic unless the student asks you to.

3. Assume the student is learning Computational Linguistics.

4. Explain concepts in clear, student-friendly language.

5. If the question is difficult, explain it step-by-step.

6. Give examples related to Computational Linguistics
   whenever appropriate.

7. Do not invent facts.

8. If the student's question is unrelated to the current
   topic, politely explain that and connect the answer back
   to the current topic when possible.

9. Do not use Markdown inside JSON string values.

10. Return ONLY valid JSON.

11. Do NOT return:
    ```json
    ```
    or any other code fence.

12. "key_points" must always be a JSON array.

13. "follow_up_question" should contain one useful question
    that helps the student think about the topic.

Return exactly this structure:

{{
    "answer": "Direct answer to the student's question.",
    "simple_explanation": "Easy explanation suitable for a student.",
    "example": "A relevant Computational Linguistics example.",
    "key_points": [
        "Important point 1",
        "Important point 2",
        "Important point 3"
    ],
    "follow_up_question": "A useful question for the student."
}}
"""

    # --------------------------------------------------------
    # Call AI
    # --------------------------------------------------------

    raw_response = ai_client.generate(
        prompt
    )

    if not raw_response:
        raise ValueError(
            "AI returned an empty response."
        )

    # --------------------------------------------------------
    # Clean response
    # --------------------------------------------------------

    cleaned_response = clean_json_response(
        raw_response
    )

    # --------------------------------------------------------
    # Validate JSON first
    # --------------------------------------------------------

    try:

        data = json.loads(
            cleaned_response
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "AI returned invalid JSON.\n\n"
            f"Raw response:\n{raw_response}\n\n"
            f"JSON error: {error}"
        )

    # --------------------------------------------------------
    # Validate schema
    # --------------------------------------------------------

    try:

        return TutorResponse.model_validate(
            data
        )

    except Exception as error:

        raise ValueError(
            "AI response does not match the Tutor schema.\n\n"
            f"{error}"
        )