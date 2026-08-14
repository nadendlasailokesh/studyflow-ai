from src.ai.quiz import generate_quiz

from src.ai.quiz_schema import Quiz


def test_quiz_generation(monkeypatch):

    mock_response = """
    {
        "topic": "Decision Trees",
        "difficulty": "MEDIUM",
        "questions": [
            {
                "question": "What does a leaf node represent?",
                "options": [
                    "A decision",
                    "A final prediction",
                    "The root",
                    "A branch"
                ],
                "correct_answer": "A final prediction",
                "explanation": "A leaf node represents the final outcome or prediction."
            }
        ]
    }
    """

    def mock_generate(prompt):

        return mock_response

    monkeypatch.setattr(
        "src.ai.quiz.ai_client.generate",
        mock_generate
    )

    quiz = generate_quiz(
        subject_name="Data Mining",
        unit="Unit 2",
        topic="Decision Trees",
        difficulty="MEDIUM",
        number_of_questions=1
    )

    assert isinstance(
        quiz,
        Quiz
    )

    assert quiz.topic == "Decision Trees"

    assert len(quiz.questions) == 1

    assert len(
        quiz.questions[0].options
    ) == 4