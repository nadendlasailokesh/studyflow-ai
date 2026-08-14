from src.ai.quiz_evaluator import (
    evaluate_answer
)


def test_correct_answer():

    result = evaluate_answer(

        question="What is entropy?",

        selected_answer="Measure of uncertainty",

        correct_answer="Measure of uncertainty",

        explanation=(
            "Entropy measures uncertainty "
            "in a dataset."
        )
    )

    assert result.is_correct is True

    assert result.score == 1


def test_wrong_answer():

    result = evaluate_answer(

        question="What is entropy?",

        selected_answer="A database",

        correct_answer="Measure of uncertainty",

        explanation=(
            "Entropy measures uncertainty "
            "in a dataset."
        )
    )

    assert result.is_correct is False

    assert result.score == 0