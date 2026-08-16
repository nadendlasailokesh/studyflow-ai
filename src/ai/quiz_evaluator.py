from pydantic import BaseModel

from src.ai.progress import (
    save_progress_to_database
)

from src.ai.revision_integration import (
    update_revision_after_quiz,
)
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

        and

        selected_answer == correct_answer
    )


    # --------------------------------------------------------
    # Question score
    # --------------------------------------------------------

    score = (
        1
        if is_correct
        else 0
    )


    # --------------------------------------------------------
    # Feedback
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
    # Initialize
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


        if evaluation.is_correct:

            correct_answers += 1


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
    # Current quiz score
    # --------------------------------------------------------

    score_percentage = (

        correct_answers
        /
        total_questions

    ) * 100


    score_percentage = round(
        score_percentage,
        2
    )


    # --------------------------------------------------------
    # Update mastery
    # --------------------------------------------------------

    progress = None


    if topic_id is not None:

        progress = save_progress_to_database(

            topic_id=topic_id,

            correct_answers=correct_answers,

            total_questions=total_questions,

            difficulty=quiz.difficulty,

            topic=quiz.topic
        )

    # --------------------------------------------------------
    # Phase 8.4
    # Update spaced-repetition schedule
    # --------------------------------------------------------

        revision = update_revision_after_quiz(

            topic_id=topic_id,

            score_percentage=score_percentage,
        )


    # --------------------------------------------------------
    # Return complete result
    # --------------------------------------------------------

    return {

        "topic": quiz.topic,

        "difficulty": quiz.difficulty,

        "correct_answers": correct_answers,

        "total_questions": total_questions,

        "score_percentage": score_percentage,

        "results": results,

        "progress": progress,

        "revision": revision,
    }