from src.ai.learning import (
    generate_learning_content
)

from src.ai.learning_schema import (
    LearningContent
)


def test_learning_content_generation(
    monkeypatch
):

    mock_response = """
    {
        "topic": "Decision Trees",
        "simple_explanation": "A Decision Tree makes decisions by asking a sequence of questions.",
        "analogy": "It is like deciding whether to carry an umbrella by checking if it is raining.",
        "example": "A tree can classify whether a student is likely to pass based on attendance and study time.",
        "key_points": [
            "Root node",
            "Decision nodes",
            "Branches",
            "Leaf nodes"
        ],
        "exam_definition": "A Decision Tree is a tree-based model used to make decisions or predictions.",
        "common_mistakes": [
            "Confusing branches with nodes",
            "Ignoring overfitting"
        ],
        "memory_tip": "Think: Question → Branch → Decision.",
        "quick_check_question": "What does a leaf node represent?"
    }
    """

    def mock_generate(prompt):
        return mock_response

    monkeypatch.setattr(
        "src.ai.learning.ai_client.generate",
        mock_generate
    )

    content = generate_learning_content(
        subject_name="Data Mining",
        unit="Unit 2",
        topic="Decision Trees",
        prerequisites=["Classification"]
    )

    assert isinstance(
        content,
        LearningContent
    )

    assert content.topic == "Decision Trees"

    assert content.simple_explanation

    assert len(content.key_points) > 0

    assert content.exam_definition

    assert content.quick_check_question