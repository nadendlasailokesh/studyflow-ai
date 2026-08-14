from src.ai.learning_schema import (
    LearningContent
)


def test_learning_content_schema():

    content = LearningContent(

        subject="Data Mining",

        topic="Decision Trees",

        simple_explanation=(
            "A decision tree is a model "
            "that makes decisions using "
            "a sequence of conditions."
        ),

        key_concepts=[
            "Root node",
            "Decision node",
            "Leaf node"
        ],

        examples=[
            "Loan approval",
            "Disease prediction"
        ],

        exam_definition=(
            "A decision tree is a tree-based "
            "classification model."
        ),

        important_points=[
            "Root node represents the first decision.",
            "Leaf nodes represent final outcomes."
        ],

        common_mistakes=[
            "Confusing root and leaf nodes."
        ],

        memory_tip=(
            "Think of a decision tree like "
            "a flowchart."
        ),

        quick_check_question=(
            "What does a leaf node represent?"
        ),

        quick_check_answer=(
            "The final prediction or outcome."
        ),

        estimated_minutes=30
    )

    assert content.subject == "Data Mining"

    assert content.topic == "Decision Trees"

    assert len(
        content.key_concepts
    ) > 0

    assert len(
        content.examples
    ) > 0

    assert (
        content.estimated_minutes
        > 0
    )