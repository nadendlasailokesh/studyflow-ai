from src.ai.tutor import ask_tutor

from src.ai.tutor_schema import (
    TutorResponse
)


def test_tutor(monkeypatch):

    mock_response = """
    {
        "answer": "Entropy measures the uncertainty or impurity in a dataset.",
        "simple_explanation": "Think of entropy as measuring how mixed the outcomes are.",
        "example": "A box containing only apples has low entropy, while a box containing many different fruits has higher entropy.",
        "key_points": [
            "Entropy measures uncertainty",
            "Lower entropy means purer groups",
            "Decision trees use entropy to choose splits"
        ],
        "follow_up_question": "Would you like me to explain the entropy formula?"
    }
    """

    def mock_generate(prompt):
        return mock_response

    monkeypatch.setattr(
        "src.ai.tutor.ai_client.generate",
        mock_generate
    )

    result = ask_tutor(
        subject_name="Data Mining",
        unit="Unit 2",
        topic="Decision Trees",
        question="What is entropy?"
    )

    assert isinstance(
        result,
        TutorResponse
    )

    assert result.answer

    assert result.simple_explanation

    assert len(result.key_points) > 0

    assert result.follow_up_question