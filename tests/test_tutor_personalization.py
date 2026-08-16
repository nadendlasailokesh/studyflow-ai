# ============================================================
# TESTS — AI TUTOR PERSONALIZATION
# StudyFlow AI
# Phase 10.7
# ============================================================

import json
from src.ai.tutor_schema import TutorResponse
from src.ai.tutor_schema import TutorResponse
import pytest

from src.ai.tutor import (
    clean_json_response,
    _build_personalized_context,
    _build_personalization_guidance,
    _build_tutor_request,
    ask_tutor,
)


# ============================================================
# SAMPLE DATA
# ============================================================

STRUGGLING_PERFORMANCE = {
    "student_id": 445,

    "learning_state": "STRUGGLING",

    "mastery": {
        "average": 25.0,
        "strong_topics": 0,
        "average_topics": 0,
        "weak_topics": 1,
        "not_started_topics": 28,
        "completed_topics": 0,
        "total_topics": 29,
        "coverage": 3.45,
    },

    "quiz": {
        "attempts": 1,
        "total_questions": 5,
        "correct_answers": 1.0,
        "average_score": 20.0,
        "best_score": 20.0,
        "lowest_score": 20.0,
        "topics_attempted": 1,
        "coverage": 3.45,
    },

    "trend": {
        "status": "INSUFFICIENT_DATA",
        "change": 0.0,
        "first_score": 20.0,
        "latest_score": 20.0,
        "highest_score": 20.0,
        "lowest_score": 20.0,
    },

    "consistency": {
        "level": "LOW",
        "score": 0.25,
    },

    "confidence": 0.52,
}


STRONG_PERFORMANCE = {
    "student_id": 445,

    "learning_state": "MASTERING",

    "mastery": {
        "average": 90.0,
        "strong_topics": 10,
        "average_topics": 2,
        "weak_topics": 0,
        "not_started_topics": 0,
        "completed_topics": 10,
        "total_topics": 12,
        "coverage": 100.0,
    },

    "quiz": {
        "attempts": 3,
        "total_questions": 15,
        "correct_answers": 14.0,
        "average_score": 92.0,
        "best_score": 100.0,
        "lowest_score": 85.0,
        "topics_attempted": 10,
        "coverage": 100.0,
    },

    "trend": {
        "status": "IMPROVING",
        "change": 8.0,
        "first_score": 84.0,
        "latest_score": 92.0,
        "highest_score": 100.0,
        "lowest_score": 84.0,
    },

    "consistency": {
        "level": "HIGH",
        "score": 0.9,
    },

    "confidence": 0.9,
}


MEDIUM_PERFORMANCE = {
    "learning_state": "DEVELOPING",

    "mastery": {
        "average": 65.0,
    },

    "quiz": {
        "attempts": 2,
        "average_score": 68.0,
    },

    "trend": {
        "status": "STABLE",
    },

    "consistency": {
        "level": "MEDIUM",
    },
}


EASY_DIFFICULTY = {
    "difficulty": "EASY",
    "previous_difficulty": "MEDIUM",
    "trend": "INSUFFICIENT_DATA",
    "recent_average": 20.0,
    "mastery": 25.0,
    "attempts": 1,
}


MEDIUM_DIFFICULTY = {
    "difficulty": "MEDIUM",
    "previous_difficulty": "MEDIUM",
    "trend": "STABLE",
    "recent_average": 65.0,
    "mastery": 65.0,
    "attempts": 2,
}


HARD_DIFFICULTY = {
    "difficulty": "HARD",
    "previous_difficulty": "MEDIUM",
    "trend": "STABLE",
    "recent_average": 92.5,
    "mastery": 90.0,
    "attempts": 3,
}


VALID_TUTOR_RESPONSE = {
    "answer": (
        "Morphology is the study of how words are formed "
        "from smaller meaningful units."
    ),

    "simple_explanation": (
        "A morpheme is the smallest unit of meaning in a word."
    ),

    "example": (
        "The word 'unhappy' contains the prefix 'un-' "
        "and the word 'happy'."
    ),

    "key_points": [
        "Morphology studies word structure.",
        "Morphemes are meaningful units.",
        "Words can contain multiple morphemes.",
    ],

    "follow_up_question": (
        "Can you identify the morphemes in the word 'replayed'?"
    ),
}


# ============================================================
# JSON CLEANING TESTS
# ============================================================

def test_clean_json_response_plain_json():

    raw = json.dumps(
        VALID_TUTOR_RESPONSE
    )

    cleaned = clean_json_response(
        raw
    )

    assert cleaned == raw


def test_clean_json_response_json_code_fence():

    raw = (
        "```json\n"
        + json.dumps(VALID_TUTOR_RESPONSE)
        + "\n```"
    )

    cleaned = clean_json_response(
        raw
    )

    parsed = json.loads(
        cleaned
    )

    assert parsed == VALID_TUTOR_RESPONSE


def test_clean_json_response_generic_code_fence():

    raw = (
        "```\n"
        + json.dumps(VALID_TUTOR_RESPONSE)
        + "\n```"
    )

    cleaned = clean_json_response(
        raw
    )

    parsed = json.loads(
        cleaned
    )

    assert parsed == VALID_TUTOR_RESPONSE


def test_clean_json_response_empty():

    with pytest.raises(
        ValueError,
        match="empty response"
    ):

        clean_json_response("")


# ============================================================
# PERSONALIZED CONTEXT TESTS
# ============================================================

def test_personalized_context_with_performance():

    context = _build_personalized_context(
        performance=STRUGGLING_PERFORMANCE,
        difficulty=EASY_DIFFICULTY,
    )

    assert "25.0%" in context

    assert "STRUGGLING" in context

    assert "Quiz attempts: 1" in context

    assert "20.0%" in context

    assert "INSUFFICIENT_DATA" in context

    assert "LOW" in context

    assert "EASY" in context


def test_personalized_context_with_strong_student():

    context = _build_personalized_context(
        performance=STRONG_PERFORMANCE,
        difficulty=HARD_DIFFICULTY,
    )

    assert "90.0%" in context

    assert "MASTERING" in context

    assert "Quiz attempts: 3" in context

    assert "92.0%" in context

    assert "IMPROVING" in context

    assert "HIGH" in context

    assert "HARD" in context


def test_personalized_context_with_only_performance():

    context = _build_personalized_context(
        performance=STRUGGLING_PERFORMANCE
    )

    assert "25.0%" in context

    assert "STRUGGLING" in context

    assert "EASY" not in context


def test_personalized_context_with_only_difficulty():

    context = _build_personalized_context(
        difficulty=HARD_DIFFICULTY
    )

    assert "HARD" in context


def test_personalized_context_without_data():

    context = _build_personalized_context()

    assert (
        "No additional student performance information"
        in context
    )


def test_personalized_context_with_empty_data():

    context = _build_personalized_context(
        performance={},
        difficulty={}
    )

    assert (
        "No additional student performance information"
        in context
    )


# ============================================================
# PERSONALIZATION GUIDANCE TESTS
# ============================================================

def test_guidance_for_low_mastery_student():

    guidance = _build_personalization_guidance(
        performance=STRUGGLING_PERFORMANCE,
        difficulty=EASY_DIFFICULTY,
    )

    assert "low mastery" in guidance.lower()

    assert "fundamentals" in guidance.lower()

    assert "struggling" in guidance.lower()

    assert "introductory" in guidance.lower()


def test_guidance_for_strong_student():

    guidance = _build_personalization_guidance(
        performance=STRONG_PERFORMANCE,
        difficulty=HARD_DIFFICULTY,
    )

    assert "strong mastery" in guidance.lower()

    assert "deeper reasoning" in guidance.lower()

    assert "challenging" in guidance.lower()


def test_guidance_for_medium_mastery_student():

    guidance = _build_personalization_guidance(
        performance=MEDIUM_PERFORMANCE,
        difficulty=MEDIUM_DIFFICULTY,
    )

    assert "developing understanding" in guidance.lower()

    assert "application" in guidance.lower()

    assert "moderate" in guidance.lower()


def test_guidance_for_easy_difficulty():

    guidance = _build_personalization_guidance(
        difficulty=EASY_DIFFICULTY
    )

    assert "introductory" in guidance.lower()

    assert "foundational" in guidance.lower()


def test_guidance_for_medium_difficulty():

    guidance = _build_personalization_guidance(
        difficulty=MEDIUM_DIFFICULTY
    )

    assert "moderate examples" in guidance.lower()


def test_guidance_for_hard_difficulty():

    guidance = _build_personalization_guidance(
        difficulty=HARD_DIFFICULTY
    )

    assert "challenging" in guidance.lower()

    assert "application" in guidance.lower()


def test_guidance_without_data():

    guidance = _build_personalization_guidance()

    assert "balanced explanation" in guidance.lower()


# ============================================================
# TUTOR REQUEST TESTS
# ============================================================

def test_tutor_request_contains_topic():

    prompt = _build_tutor_request(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="What is morphology?"
    )

    assert "Morphology" in prompt

    assert "What is morphology?" in prompt


def test_tutor_request_contains_performance():

    prompt = _build_tutor_request(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="What is morphology?",
        performance=STRUGGLING_PERFORMANCE,
        difficulty=EASY_DIFFICULTY,
    )

    assert "25.0%" in prompt

    assert "STRUGGLING" in prompt

    assert "20.0%" in prompt

    assert "EASY" in prompt


def test_tutor_request_contains_strong_student_guidance():

    prompt = _build_tutor_request(
        subject_name="Computational Linguistics",
        unit="Unit 2",
        topic="Syntax",
        question="Explain syntax.",
        performance=STRONG_PERFORMANCE,
        difficulty=HARD_DIFFICULTY,
    )

    assert "90.0%" in prompt

    assert "MASTERING" in prompt

    assert "HARD" in prompt

    assert "deeper reasoning" in prompt.lower()


def test_tutor_request_contains_follow_up_instruction():

    prompt = _build_tutor_request(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="What is a morpheme?"
    )

    assert "follow_up_question" in prompt

    assert "current level" in prompt.lower()


def test_tutor_request_protects_internal_information():

    prompt = _build_tutor_request(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="Explain morphology.",
        performance=STRUGGLING_PERFORMANCE,
    )

    assert (
        "Do NOT expose internal scores"
        in prompt
    )

    assert (
        "Never reveal internal recommendation calculations"
        in prompt
    )


# ============================================================
# INPUT VALIDATION TESTS
# ============================================================

def test_tutor_rejects_empty_question():

    with pytest.raises(
        ValueError,
        match="Question cannot be empty"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question=""
        )


def test_tutor_rejects_whitespace_question():

    with pytest.raises(
        ValueError,
        match="Question cannot be empty"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="   "
        )


def test_tutor_requires_topic():

    with pytest.raises(
        ValueError,
        match="A topic is required"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="",
            question="What is morphology?"
        )


def test_tutor_rejects_whitespace_topic():

    with pytest.raises(
        ValueError,
        match="A topic is required"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="   ",
            question="What is morphology?"
        )


# ============================================================
# AI RESPONSE VALIDATION TESTS
# ============================================================

def test_tutor_valid_response(
    monkeypatch
):

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            VALID_TUTOR_RESPONSE
        )
    )

    result = ask_tutor(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="What is morphology?"
    )

    assert result.answer == (
        VALID_TUTOR_RESPONSE["answer"]
    )

    assert result.simple_explanation == (
        VALID_TUTOR_RESPONSE[
            "simple_explanation"
        ]
    )

    assert result.example == (
        VALID_TUTOR_RESPONSE["example"]
    )

    assert len(
        result.key_points
    ) == 3

    assert result.follow_up_question == (
        VALID_TUTOR_RESPONSE[
            "follow_up_question"
        ]
    )


def test_tutor_valid_response_with_personalization(
    monkeypatch
):

    captured_prompt = {}

    def fake_generate(prompt):

        captured_prompt["value"] = prompt

        return json.dumps(
            VALID_TUTOR_RESPONSE
        )

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        fake_generate
    )

    result = ask_tutor(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="Explain morphology.",
        performance=STRUGGLING_PERFORMANCE,
        difficulty=EASY_DIFFICULTY,
    )

    assert result is not None

    prompt = captured_prompt["value"]

    assert "25.0%" in prompt

    assert "STRUGGLING" in prompt

    assert "EASY" in prompt


def test_tutor_passes_previous_context(
    monkeypatch
):

    captured_prompt = {}

    def fake_generate(prompt):

        captured_prompt["value"] = prompt

        return json.dumps(
            VALID_TUTOR_RESPONSE
        )

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        fake_generate
    )

    previous_context = [
        {
            "role": "student",
            "content": "What is a morpheme?"
        },
        {
            "role": "tutor",
            "content": "A morpheme is the smallest unit of meaning."
        }
    ]

    ask_tutor(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="Can you give another example?",
        previous_context=previous_context,
    )

    prompt = captured_prompt["value"]

    assert "What is a morpheme?" in prompt

    assert (
        "smallest unit of meaning"
        in prompt
    )


# ============================================================
# EMPTY AI RESPONSE
# ============================================================

def test_tutor_rejects_empty_ai_response(
    monkeypatch
):

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: ""
    )

    with pytest.raises(
        ValueError,
        match="empty response"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


def test_tutor_rejects_none_ai_response(
    monkeypatch
):

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: None
    )

    with pytest.raises(
        ValueError,
        match="empty response"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


# ============================================================
# INVALID JSON
# ============================================================

def test_tutor_rejects_invalid_json(
    monkeypatch
):

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: "This is not JSON."
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


# ============================================================
# INVALID RESPONSE TYPE
# ============================================================

def test_tutor_rejects_json_array(
    monkeypatch
):

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: "[]"
    )

    with pytest.raises(
        ValueError,
        match="JSON object"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


# ============================================================
# MISSING FIELD
# ============================================================

def test_tutor_rejects_missing_answer(
    monkeypatch
):

    invalid_response = dict(
        VALID_TUTOR_RESPONSE
    )

    invalid_response.pop(
        "answer"
    )

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            invalid_response
        )
    )

    with pytest.raises(
        ValueError,
        match="missing required fields"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


def test_tutor_rejects_missing_key_points(
    monkeypatch
):

    invalid_response = dict(
        VALID_TUTOR_RESPONSE
    )

    invalid_response.pop(
        "key_points"
    )

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            invalid_response
        )
    )

    with pytest.raises(
        ValueError,
        match="missing required fields"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


# ============================================================
# INVALID KEY POINTS
# ============================================================

def test_tutor_rejects_non_list_key_points(
    monkeypatch
):

    invalid_response = dict(
        VALID_TUTOR_RESPONSE
    )

    invalid_response["key_points"] = (
        "Morphology is about word structure."
    )

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            invalid_response
        )
    )

    with pytest.raises(
        ValueError,
        match="key_points.*array"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


def test_tutor_rejects_empty_key_points(
    monkeypatch
):

    invalid_response = dict(
        VALID_TUTOR_RESPONSE
    )

    invalid_response["key_points"] = []

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            invalid_response
        )
    )

    with pytest.raises(
        ValueError,
        match="at least one key point"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


def test_tutor_rejects_non_string_key_point(
    monkeypatch
):

    invalid_response = dict(
        VALID_TUTOR_RESPONSE
    )

    invalid_response["key_points"] = [
        "Valid point",
        123,
        "Another point",
    ]

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            invalid_response
        )
    )

    with pytest.raises(
        ValueError,
        match="key point 2.*string"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


# ============================================================
# INVALID STRING FIELDS
# ============================================================

@pytest.mark.parametrize(
    "field",
    [
        "answer",
        "simple_explanation",
        "example",
        "follow_up_question",
    ]
)
def test_tutor_rejects_empty_string_field(
    monkeypatch,
    field
):

    invalid_response = dict(
        VALID_TUTOR_RESPONSE
    )

    invalid_response[field] = ""

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            invalid_response
        )
    )

    with pytest.raises(
        ValueError,
        match=f"field '{field}'"
    ):

        ask_tutor(
            subject_name="Computational Linguistics",
            unit="Unit 1",
            topic="Morphology",
            question="What is morphology?"
        )


# ============================================================
# MARKDOWN CODE-FENCE RESPONSE
# ============================================================

def test_tutor_accepts_markdown_json_response(
    monkeypatch
):

    raw_response = (
        "```json\n"
        + json.dumps(
            VALID_TUTOR_RESPONSE
        )
        + "\n```"
    )

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: raw_response
    )

    result = ask_tutor(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="What is morphology?"
    )

    assert result is not None

    assert result.answer == (
        VALID_TUTOR_RESPONSE["answer"]
    )


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def test_tutor_backward_compatible_without_personalization(
    monkeypatch
):

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            VALID_TUTOR_RESPONSE
        )
    )

    result = ask_tutor(
        "Computational Linguistics",
        "Unit 1",
        "Morphology",
        "What is morphology?",
        []
    )

    assert result is not None

    assert result.answer == (
        VALID_TUTOR_RESPONSE["answer"]
    )


# ============================================================
# FULL PERSONALIZATION SCENARIOS
# ============================================================

def test_struggling_student_receives_personalized_prompt(
    monkeypatch
):

    captured_prompt = {}

    def fake_generate(prompt):

        captured_prompt["prompt"] = prompt

        return json.dumps(
            VALID_TUTOR_RESPONSE
        )

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        fake_generate
    )

    ask_tutor(
        subject_name="Computational Linguistics",
        unit="Unit 2",
        topic="Morphology",
        question="Explain finite state transducers.",
        performance=STRUGGLING_PERFORMANCE,
        difficulty=EASY_DIFFICULTY,
    )

    prompt = captured_prompt["prompt"]

    assert "25.0%" in prompt

    assert "STRUGGLING" in prompt

    assert "EASY" in prompt

    assert "fundamentals" in prompt.lower()

    assert "smaller steps" in prompt.lower()


def test_strong_student_receives_challenging_guidance(
    monkeypatch
):

    captured_prompt = {}

    def fake_generate(prompt):

        captured_prompt["prompt"] = prompt

        return json.dumps(
            VALID_TUTOR_RESPONSE
        )

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        fake_generate
    )

    ask_tutor(
        subject_name="Computational Linguistics",
        unit="Unit 3",
        topic="Syntax",
        question="Explain syntactic parsing.",
        performance=STRONG_PERFORMANCE,
        difficulty=HARD_DIFFICULTY,
    )

    prompt = captured_prompt["prompt"]

    assert "90.0%" in prompt

    assert "MASTERING" in prompt

    assert "HARD" in prompt

    assert "deeper reasoning" in prompt.lower()

    assert "challenging" in prompt.lower()


# ============================================================
# FINAL SCHEMA VALIDATION
# ============================================================

def test_tutor_response_is_pydantic_model(
    monkeypatch
):

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        lambda prompt: json.dumps(
            VALID_TUTOR_RESPONSE
        )
    )

    result = ask_tutor(
        subject_name="Computational Linguistics",
        unit="Unit 1",
        topic="Morphology",
        question="What is morphology?"
    )

    assert isinstance(
        result,
        TutorResponse
    )