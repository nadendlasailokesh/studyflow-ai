import json
import re

from src.ai.client import ai_client

from src.ai.prompts import (
    SYLLABUS_ANALYSIS_SYSTEM_PROMPT,
    build_syllabus_analysis_prompt,
)

from src.ai.syllabus_schema import (
    SyllabusAnalysis,
)

# ============================================================
# GEMINI SYLLABUS RESPONSE SCHEMA
# ============================================================

SYLLABUS_RESPONSE_SCHEMA = {

    "type": "object",

    "required": [
        "subject",
        "overview",
        "topics",
    ],

    "properties": {

        "subject": {
            "type": "string",
        },

        "overview": {
            "type": "string",
        },

        "topics": {

            "type": "array",

            "items": {

                "type": "object",

                "required": [
                    "topic",
                    "unit",
                    "priority",
                    "reason",
                    "estimated_minutes",
                    "prerequisites",
                ],

                "properties": {

                    "topic": {
                        "type": "string",
                    },

                    "unit": {
                        "type": "string",
                    },

                    "priority": {

                        "type": "string",

                        "enum": [
                            "HIGH",
                            "MEDIUM",
                            "LOW",
                        ],
                    },

                    "reason": {
                        "type": "string",
                    },

                    "estimated_minutes": {

                        "type": "integer",

                        "minimum": 15,

                        "maximum": 300,
                    },

                    "prerequisites": {

                        "type": "array",

                        "items": {
                            "type": "string",
                        },
                    },
                },
            },
        },
    },
}

# ============================================================
# CLEAN AI RESPONSE
# ============================================================

def clean_json_response(response: str) -> str:
    """
    Extract the most likely JSON object from an AI response.

    Handles:
        - Normal JSON
        - ```json ... ```
        - ``` ... ```
        - Extra text before JSON
        - Extra text after JSON

    IMPORTANT:
    This function does NOT parse JSON.
    It only extracts the candidate JSON string.
    """

    if response is None:
        raise ValueError(
            "AI returned an empty response."
        )

    response = str(response).strip()

    if not response:
        raise ValueError(
            "AI returned an empty response."
        )

    # --------------------------------------------------------
    # Remove Markdown code fences
    # --------------------------------------------------------

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
    )

    response = response.strip()

    # --------------------------------------------------------
    # Find first JSON object
    # --------------------------------------------------------

    start = response.find("{")

    if start == -1:
        raise ValueError(
            "AI response does not contain a JSON object."
        )

    # --------------------------------------------------------
    # Find matching closing brace.
    #
    # We do NOT simply use rfind("}") because the AI may
    # have added additional text after the JSON.
    # --------------------------------------------------------

    depth = 0
    in_string = False
    escaped = False
    end = None

    for index in range(
        start,
        len(response),
    ):

        char = response[index]

        # Handle escaped characters inside strings
        if escaped:

            escaped = False
            continue

        if char == "\\" and in_string:

            escaped = True
            continue

        if char == '"':

            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":

            depth += 1

        elif char == "}":

            depth -= 1

            if depth == 0:

                end = index

                break

    # --------------------------------------------------------
    # Complete JSON object found
    # --------------------------------------------------------

    if end is not None:

        return response[
            start:end + 1
        ].strip()

    # --------------------------------------------------------
    # JSON object is incomplete/truncated
    #
    # Return everything from { onward.
    #
    # The caller can then send it to the repair AI.
    # --------------------------------------------------------

    return response[
        start:
    ].strip()


# ============================================================
# PARSE JSON RESPONSE
# ============================================================

def parse_json_response(response: str):

    cleaned = clean_json_response(
        response
    )

    try:

        return json.loads(
            cleaned
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "AI returned malformed JSON.\n\n"
            f"JSON error:\n{error}\n\n"
            f"AI response:\n{cleaned}"
        ) from error


# ============================================================
# BUILD JSON REPAIR PROMPT
# ============================================================

def build_json_repair_prompt(
    subject_name,
    syllabus,
    exam_date,
    daily_hours,
):
    """
    Regenerate the syllabus analysis from the original
    syllabus instead of attempting to repair malformed JSON.
    """

    return f"""
Generate a NEW syllabus analysis from the original syllabus.

IMPORTANT:

The previous AI response was invalid.

DO NOT attempt to repair or copy the previous response.

Use ONLY the original syllabus below.

Subject:
{subject_name}

Exam Date:
{exam_date}

Available Study Time:
{daily_hours} hours


ORIGINAL SYLLABUS
================

{syllabus}


STRICT RULES
============

1. Extract only topics actually present in the syllabus.

2. Do NOT invent missing topics.

3. Do NOT create topics labelled "Missing".

4. Do NOT add textbook topics.

5. Do NOT add topics based on your own knowledge.

6. Extract every meaningful topic present in the
   supplied syllabus.

7. Preserve the original unit names.

8. Every topic must contain:

   topic
   unit
   priority
   reason
   estimated_minutes
   prerequisites

9. priority MUST be exactly one of:

   HIGH
   MEDIUM
   LOW

10. estimated_minutes MUST be an integer.

11. estimated_minutes MUST be between 15 and 300.

12. prerequisites MUST be an array of strings.

13. If a topic has no prerequisite:

    []

14. Do not put objects inside prerequisites.

15. Do not duplicate topics.

16. Do not invent prerequisites.

17. Return ONLY JSON.

18. Return one complete JSON object.

19. Do not use Markdown.

20. Do not use code fences.

21. Do not add explanations.

22. The JSON must be complete.

23. The subject must be:

{subject_name}

Return the complete syllabus analysis.
"""

# ============================================================
# VALIDATE BASIC ANALYSIS QUALITY
# ============================================================

def validate_analysis_quality(
    analysis: SyllabusAnalysis,
):

    # --------------------------------------------------------
    # Check topics
    # --------------------------------------------------------

    if not analysis.topics:

        raise ValueError(
            "Syllabus analysis returned no topics."
        )

    # --------------------------------------------------------
    # Detect duplicate topics
    # --------------------------------------------------------

    topic_names = set()

    for topic in analysis.topics:

        normalized_name = (
            topic.topic
            .strip()
            .lower()
        )

        if not normalized_name:

            raise ValueError(
                "Syllabus contains an empty topic name."
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
        # Validate unit
        # ----------------------------------------------------

        if not topic.unit.strip():

            raise ValueError(
                f"Topic '{topic.topic}' "
                "does not contain a valid unit."
            )

        # ----------------------------------------------------
        # Validate priority
        # ----------------------------------------------------

        if topic.priority not in {
            "HIGH",
            "MEDIUM",
            "LOW",
        }:

            raise ValueError(
                f"Invalid priority for "
                f"{topic.topic}: "
                f"{topic.priority}"
            )

        # ----------------------------------------------------
        # Validate estimated time
        # ----------------------------------------------------

        if not (
            15
            <= topic.estimated_minutes
            <= 300
        ):

            raise ValueError(
                f"Invalid study time for "
                f"{topic.topic}: "
                f"{topic.estimated_minutes}"
            )

        # ----------------------------------------------------
        # Validate prerequisites
        # ----------------------------------------------------

        if topic.prerequisites is None:

            raise ValueError(
                f"Prerequisites cannot be None "
                f"for topic: {topic.topic}"
            )

        for prerequisite in topic.prerequisites:

            if not isinstance(
                prerequisite,
                str,
            ):

                raise ValueError(
                    f"Invalid prerequisite for "
                    f"{topic.topic}"
                )

            if (
                prerequisite.strip().lower()
                == normalized_name
            ):

                raise ValueError(
                    "Topic cannot be its own "
                    f"prerequisite: {topic.topic}"
                )


# ============================================================
# VALIDATE AI RESPONSE
# ============================================================

def validate_ai_response(response):

    # --------------------------------------------------------
    # Attempt cleaning
    # --------------------------------------------------------

    try:

        cleaned = clean_json_response(
            response
        )

    except ValueError as error:

        return None, str(error)

    # --------------------------------------------------------
    # Attempt JSON parsing
    # --------------------------------------------------------

    try:

        data = json.loads(
            cleaned
        )

    except json.JSONDecodeError as error:

        return None, (
            "AI returned malformed JSON.\n\n"
            f"JSON error:\n{error}\n\n"
            f"AI response:\n{cleaned}"
        )

    # --------------------------------------------------------
    # Basic object validation
    # --------------------------------------------------------

    if not isinstance(
        data,
        dict,
    ):

        return None, (
            "AI response must be a JSON object."
        )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [
        "subject",
        "overview",
        "topics",
    ]

    for field in required_fields:

        if field not in data:

            return None, (
                f"AI response is missing "
                f"'{field}'."
            )

    # --------------------------------------------------------
    # Validate subject
    # --------------------------------------------------------

    if not isinstance(
        data["subject"],
        str,
    ):

        return None, (
            "AI response 'subject' "
            "must be a string."
        )

    # --------------------------------------------------------
    # Validate overview
    # --------------------------------------------------------

    if not isinstance(
        data["overview"],
        str,
    ):

        return None, (
            "AI response 'overview' "
            "must be a string."
        )

    # --------------------------------------------------------
    # Validate topics
    # --------------------------------------------------------

    if not isinstance(
        data["topics"],
        list,
    ):

        return None, (
            "AI response 'topics' "
            "must be a list."
        )

    if not data["topics"]:

        return None, (
            "AI response contains no topics."
        )

    # --------------------------------------------------------
    # Validate topic structures before Pydantic
    # --------------------------------------------------------

    required_topic_fields = [
        "topic",
        "unit",
        "priority",
        "reason",
        "estimated_minutes",
        "prerequisites",
    ]

    for index, topic in enumerate(
        data["topics"],
        start=1,
    ):

        if not isinstance(
            topic,
            dict,
        ):

            return None, (
                f"Topic {index} must be "
                "a JSON object."
            )

        for field in required_topic_fields:

            if field not in topic:

                return None, (
                    f"Topic {index} is missing "
                    f"'{field}'."
                )

        if not isinstance(
            topic["prerequisites"],
            list,
        ):

            return None, (
                f"Topic {index} "
                "'prerequisites' must be "
                "a list."
            )

        if topic["priority"] not in {
            "HIGH",
            "MEDIUM",
            "LOW",
        }:

            return None, (
                f"Topic {index} has invalid "
                f"priority: {topic['priority']}"
            )

        try:

            estimated_minutes = int(
                topic["estimated_minutes"]
            )

        except (
            TypeError,
            ValueError,
        ):

            return None, (
                f"Topic {index} has invalid "
                "estimated_minutes."
            )

        if not (
            15
            <= estimated_minutes
            <= 300
        ):

            return None, (
                f"Topic {index} has invalid "
                f"estimated_minutes: "
                f"{estimated_minutes}"
            )

        # Normalize integer in case the AI returned
        # a numeric value that can safely be converted.
        topic[
            "estimated_minutes"
        ] = estimated_minutes

    return data, None


# ============================================================
# BUILD MAIN ANALYSIS PROMPT
# ============================================================

def build_analysis_prompt(
    subject_name,
    syllabus,
    exam_date,
    daily_hours,
):

    user_prompt = build_syllabus_analysis_prompt(

        subject_name=subject_name,

        syllabus=syllabus,

        exam_date=exam_date,

        daily_hours=daily_hours,
    )

    return f"""
{SYLLABUS_ANALYSIS_SYSTEM_PROMPT}

{user_prompt}

IMPORTANT ANALYSIS REQUIREMENTS:

1. Analyze the COMPLETE syllabus.

2. Identify EVERY unit.

3. Extract EVERY meaningful individual topic.

4. Do NOT combine an entire unit into one topic.

5. Do NOT omit smaller topics.

6. Keep topic names concise but descriptive.

7. Preserve original unit names whenever possible.

8. Priority MUST be exactly:
   HIGH
   MEDIUM
   LOW

9. HIGH priority:
   - foundational concepts
   - major theoretical concepts
   - concepts required by later topics
   - concepts requiring deeper understanding
   - important examination concepts

10. MEDIUM priority:
    - important supporting concepts
    - moderate-complexity concepts
    - topics dependent on foundational concepts

11. LOW priority:
    - less central topics
    - supplementary concepts
    - topics that can reasonably be studied later

12. Estimate realistic study time for EACH topic.

13. Do NOT assign the same study time to every topic unless
    the topics genuinely require similar effort.

14. Approximate ranges:

    Simple: 20-40 minutes
    Moderate: 40-75 minutes
    Complex: 75-120 minutes
    Very complex: 120-180 minutes

15. estimated_minutes MUST be an integer.

16. estimated_minutes MUST be between 15 and 600.

17. Identify genuine prerequisites.

18. prerequisites MUST contain topic names from the same
    syllabus whenever possible.

19. If there is no prerequisite, return [].

20. Do NOT invent prerequisites unnecessarily.

21. overview must summarize the entire syllabus.

22. subject MUST contain:

    {subject_name}

23. Do NOT invent past-exam frequency.

24. Do NOT claim that a topic is frequently asked unless
    actual past-exam data was provided.

25. Return ONLY valid JSON.

26. Do NOT use Markdown.

27. Do NOT use ```json.

28. Do NOT add explanations outside JSON.

29. Return the COMPLETE JSON object.

30. Do NOT stop in the middle of the topics array.

31. Make sure every opening brace, bracket, and quotation
    mark has a matching closing character.

32. Keep the response concise enough to fit completely within
    the model's output limit.

33. Do not generate unnecessary descriptions.

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

# ============================================================
# ANALYZE SYLLABUS
# ============================================================

def analyze_syllabus(
    subject_name,
    syllabus,
    exam_date,
    daily_hours,
):

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if not subject_name or not subject_name.strip():

        raise ValueError(
            "Subject name cannot be empty."
        )

    if not syllabus or not syllabus.strip():

        raise ValueError(
            "Syllabus cannot be empty."
        )

    try:

        daily_hours = float(
            daily_hours
        )

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            "Daily study hours must be a valid number."
        )

    if daily_hours <= 0:

        raise ValueError(
            "Daily study hours must be greater than zero."
        )

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    prompt = build_analysis_prompt(

        subject_name=subject_name,

        syllabus=syllabus,

        exam_date=exam_date,

        daily_hours=daily_hours,
    )

    # ========================================================
    # FIRST AI ATTEMPT
    # ========================================================

    response = ai_client.generate_json(

        prompt,

        response_schema=SYLLABUS_RESPONSE_SCHEMA,
    )
    if is_non_analysis_response(response):

        print(
            "⚠️ AI provider returned a non-analysis response."
        )

        print(
            f"Provider response: {response}"
        )
    # ========================================================
    # DEBUG INFORMATION
    # ========================================================

    print(
        "\n========== SYLLABUS AI RESPONSE =========="
    )

    print(
        str(response)[:5000]
    )

    print(
        "==========================================\n"
    )

    # ========================================================
    # FIRST VALIDATION
    # ========================================================

    data, error_message = (
        validate_ai_response(
            response
        )
    )

    # ========================================================
    # REPAIR ATTEMPT
    # ========================================================

    if data is None:

        print(
            "⚠️ First syllabus AI response "
            "was invalid."
        )

        print(
            f"Reason: {error_message}"
        )

        repair_prompt = (
            build_json_repair_prompt(

                malformed_response=response,

                subject_name=subject_name,

                syllabus=syllabus,

                exam_date=exam_date,

                daily_hours=daily_hours,
            )
        )

        # ----------------------------------------------------
        # Generate repaired response
        # ----------------------------------------------------

        repaired_response = (
            ai_client.generate_json(

                repair_prompt,

                response_schema=SYLLABUS_RESPONSE_SCHEMA,
            )
        )

        # ----------------------------------------------------
        # Debug repaired response
        # ----------------------------------------------------

        print(
            "\n========== REPAIRED AI RESPONSE =========="
        )

        print(
            str(repaired_response)[:5000]
        )

        print(
            "==========================================\n"
        )

        # ----------------------------------------------------
        # Validate repaired response
        # ----------------------------------------------------

        data, repair_error = (
            validate_ai_response(
                repaired_response
            )
        )

        if data is None:

            raise ValueError(
                "AI returned malformed syllabus JSON "
                "after repair attempt.\n\n"

                f"Initial error:\n"
                f"{error_message}\n\n"

                f"Repair error:\n"
                f"{repair_error}\n\n"

                f"Initial AI response:\n"
                f"{response}\n\n"

                f"Repaired AI response:\n"
                f"{repaired_response}"
            )

        response = repaired_response

    # ========================================================
    # PYDANTIC VALIDATION
    # ========================================================

    try:

        analysis = (
            SyllabusAnalysis
            .model_validate(
                data
            )
        )

    except Exception as error:

        raise ValueError(
            "AI returned invalid syllabus data.\n\n"
            f"Validation error:\n{error}\n\n"
            f"AI response:\n{response}"
        ) from error

    # ========================================================
    # QUALITY VALIDATION
    # ========================================================

    validate_analysis_quality(
        analysis
    )

    # ========================================================
    # RETURN FINAL ANALYSIS
    # ========================================================

    return analysis
def is_non_analysis_response(response):
    """
    Detect responses that clearly are not syllabus analysis.

    This prevents provider/status/safety messages from
    being treated as a legitimate AI response.
    """

    if response is None:
        return True

    text = str(response).strip().lower()

    if not text:
        return True

    blocked_patterns = [
        "user safety:",
        "safety classification:",
        "safety: safe",
        "safety: unsafe",
        "content safety:",
    ]

    return any(
        pattern in text
        for pattern in blocked_patterns
    )