import json

from src.ai.client import ai_client

from src.ai.prompts import (
    SYLLABUS_ANALYSIS_SYSTEM_PROMPT,
    build_syllabus_analysis_prompt
)

from src.ai.syllabus_schema import (
    SyllabusAnalysis
)


# ============================================================
# CLEAN AI RESPONSE
# ============================================================

def clean_json_response(response: str) -> str:

    if not response:
        raise ValueError(
            "AI returned an empty response."
        )

    response = response.strip()

    # Remove Markdown code fences
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
    # Handle accidental text before/after JSON
    # --------------------------------------------------------

    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1:

        raise ValueError(
            "AI response does not contain valid JSON."
        )

    response = response[
        start:end + 1
    ]

    return response


# ============================================================
# VALIDATE BASIC ANALYSIS QUALITY
# ============================================================

def validate_analysis_quality(
    analysis: SyllabusAnalysis
):

    if not analysis.topics:

        raise ValueError(
            "Syllabus analysis returned no topics."
        )

    topic_names = set()

    for topic in analysis.topics:

        normalized_name = (
            topic.topic
            .strip()
            .lower()
        )

        if normalized_name in topic_names:

            raise ValueError(
                f"Duplicate topic detected: "
                f"{topic.topic}"
            )

        topic_names.add(
            normalized_name
        )

        # ----------------------------------------------------
        # Validate estimated time
        # ----------------------------------------------------

        if not (
            15
            <= topic.estimated_minutes
            <= 600
        ):

            raise ValueError(
                f"Invalid study time for "
                f"{topic.topic}: "
                f"{topic.estimated_minutes}"
            )

        # ----------------------------------------------------
        # Validate prerequisite references
        # ----------------------------------------------------

        for prerequisite in topic.prerequisites:

            if prerequisite.strip().lower() == normalized_name:

                raise ValueError(
                    f"Topic cannot be its own prerequisite: "
                    f"{topic.topic}"
                )


# ============================================================
# ANALYZE SYLLABUS
# ============================================================

def analyze_syllabus(
    subject_name,
    syllabus,
    exam_date,
    daily_hours
):

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if not subject_name.strip():

        raise ValueError(
            "Subject name cannot be empty."
        )

    if not syllabus.strip():

        raise ValueError(
            "Syllabus cannot be empty."
        )

    if daily_hours <= 0:

        raise ValueError(
            "Daily study hours must be greater than zero."
        )

    # --------------------------------------------------------
    # Build user prompt
    # --------------------------------------------------------

    user_prompt = build_syllabus_analysis_prompt(

        subject_name=subject_name,

        syllabus=syllabus,

        exam_date=exam_date,

        daily_hours=daily_hours
    )

    # --------------------------------------------------------
    # Complete AI prompt
    # --------------------------------------------------------

    prompt = f"""
{SYLLABUS_ANALYSIS_SYSTEM_PROMPT}

{user_prompt}

IMPORTANT ANALYSIS REQUIREMENTS:

1. Analyze the COMPLETE syllabus.

2. Identify EVERY unit.

3. Extract EVERY meaningful individual topic.

4. Do NOT combine an entire unit into one topic.

5. Do NOT omit smaller topics.

6. Keep topic names concise but descriptive.

7. Preserve the original unit names whenever possible.

8. Priority MUST be exactly:

   HIGH
   MEDIUM
   LOW

9. HIGH priority should be assigned to:
   - foundational concepts
   - major theoretical concepts
   - concepts required by later topics
   - topics likely to require more understanding
   - important examination concepts

10. MEDIUM priority should be assigned to:
    - important supporting concepts
    - moderate-complexity concepts
    - topics that depend on foundational concepts

11. LOW priority should be assigned only to:
    - less central topics
    - supplementary concepts
    - topics that can reasonably be studied later

12. Estimate realistic study time for EACH topic.

13. Do NOT assign the same study time to every topic unless
    the topics genuinely require similar effort.

14. Use the following approximate ranges:

    Simple topic:
    20-40 minutes

    Moderate topic:
    40-75 minutes

    Complex topic:
    75-120 minutes

    Very complex topic:
    120-180 minutes

15. estimated_minutes MUST be an integer.

16. estimated_minutes MUST be between 15 and 600.

17. Identify genuine prerequisites.

18. prerequisites MUST contain topic names from the same
    syllabus whenever possible.

19. If there is no prerequisite, return [].

20. Do NOT invent prerequisites unnecessarily.

21. The overview must summarize the entire syllabus.

22. The subject field must contain:

    {subject_name}

23. Do NOT invent past-exam frequency.

24. Do NOT claim that a topic is frequently asked unless
    actual past-exam data has been provided.

25. Return ONLY valid JSON.

26. Do NOT use Markdown.

27. Do NOT use ```json.

28. Do NOT add any explanation outside the JSON.

RETURN EXACTLY THIS STRUCTURE:

{{
    "subject": "{subject_name}",

    "overview": "Brief summary of the complete syllabus",

    "topics": [
        {{
            "topic": "Example Topic",
            "unit": "Unit-I",
            "priority": "HIGH",
            "reason": "Important foundational concept.",
            "estimated_minutes": 60,
            "prerequisites": []
        }}
    ]
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

    response = clean_json_response(
        response
    )

    # --------------------------------------------------------
    # Check JSON syntax before Pydantic
    # --------------------------------------------------------

    try:

        json.loads(response)

    except json.JSONDecodeError as error:

        raise ValueError(
            "AI returned malformed JSON.\n\n"
            f"JSON error:\n{error}\n\n"
            f"AI response:\n{response}"
        )

    # --------------------------------------------------------
    # Validate with Pydantic
    # --------------------------------------------------------

    try:

        analysis = (
            SyllabusAnalysis
            .model_validate_json(
                response
            )
        )

    except Exception as error:

        raise ValueError(
            "AI returned invalid syllabus data.\n\n"
            f"Validation error:\n{error}\n\n"
            f"AI response:\n{response}"
        )

    # --------------------------------------------------------
    # Validate analysis quality
    # --------------------------------------------------------

    validate_analysis_quality(
        analysis
    )

    return analysis