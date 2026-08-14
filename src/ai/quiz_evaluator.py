from pydantic import BaseModel

from src.ai.progress import save_progress_to_database


# ============================================================
# SINGLE QUESTION EVALUATION
# ============================================================

class QuizEvaluation(BaseModel):

    is_correct: bool

    score: int

    feedback: str

    correct_answer: str

    explanation: str


def evaluate_answer(
    question,
    selected_answer,
    correct_answer,
    explanation
):

    # --------------------------------------------------------
    # Check answer
    # --------------------------------------------------------

    is_correct = (
        selected_answer is not None
        and selected_answer == correct_answer
    )

    # --------------------------------------------------------
    # Calculate question score
    # --------------------------------------------------------

    score = 1 if is_correct else 0

    # --------------------------------------------------------
    # Generate feedback
    # --------------------------------------------------------

    if is_correct:

        feedback = (
            "Correct! Great job."
        )

    else:

        feedback = (
            "Not quite. Review the explanation "
            "and try again."
        )

    # --------------------------------------------------------
    # Return evaluation
    # --------------------------------------------------------

    return QuizEvaluation(

        is_correct=is_correct,

        score=score,

        feedback=feedback,

        correct_answer=correct_answer,

        explanation=explanation
    )


# ============================================================
# COMPLETE QUIZ EVALUATION
# ============================================================

def evaluate_quiz(
    quiz,
    answers,
    topic_id=None
):

    # --------------------------------------------------------
    # Validate quiz
    # --------------------------------------------------------

    if not quiz.questions:

        raise ValueError(
            "Quiz contains no questions."
        )

    # --------------------------------------------------------
    # Initialize counters
    # --------------------------------------------------------

    correct_answers = 0

    results = []

    # --------------------------------------------------------
    # Evaluate every question
    # --------------------------------------------------------

    for index, question in enumerate(
        quiz.questions
    ):

        selected_answer = answers.get(
            index
        )

        evaluation = evaluate_answer(

            question=question.question,

            selected_answer=selected_answer,

            correct_answer=question.correct_answer,

            explanation=question.explanation
        )

        # ----------------------------------------------------
        # Count correct answers
        # ----------------------------------------------------

        if evaluation.is_correct:

            correct_answers += 1

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        results.append(
            evaluation
        )

    # --------------------------------------------------------
    # Total questions
    # --------------------------------------------------------

    total_questions = len(
        quiz.questions
    )

    # --------------------------------------------------------
    # Calculate percentage
    # --------------------------------------------------------

    score_percentage = (
        correct_answers
        / total_questions
    ) * 100

    score_percentage = round(
        score_percentage,
        2
    )

    # --------------------------------------------------------
    # Save progress
    # --------------------------------------------------------

    progress = None

    if topic_id is not None:

        progress = save_progress_to_database(

            topic_id=topic_id,

            correct_answers=correct_answers,

            total_questions=total_questions,

            difficulty=quiz.difficulty
        )

    # --------------------------------------------------------
    # Return complete quiz result
    # --------------------------------------------------------

    return {

        "topic": quiz.topic,

        "difficulty": quiz.difficulty,

        "correct_answers": correct_answers,

        "total_questions": total_questions,

        "score_percentage": score_percentage,

        "results": results,

        "progress": progress
    }