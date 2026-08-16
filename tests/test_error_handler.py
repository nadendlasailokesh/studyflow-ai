from src.utils.error_handler import (
    get_user_error_message,
    handle_exception,
)


def test_user_error_message():

    error = ValueError(
        "Invalid student name."
    )

    assert (
        get_user_error_message(error)
        == "Invalid student name."
    )


def test_empty_error_uses_fallback():

    assert (
        get_user_error_message(
            None
        )
        == "Something went wrong. Please try again."
    )


def test_sensitive_error_is_hidden():

    error = RuntimeError(
        "API_KEY=super-secret-value"
    )

    message = get_user_error_message(
        error
    )

    assert (
        message
        == "Something went wrong. Please try again."
    )


def test_password_error_is_hidden():

    error = RuntimeError(
        "password=secret123"
    )

    message = get_user_error_message(
        error
    )

    assert (
        message
        == "Something went wrong. Please try again."
    )


def test_handle_exception_returns_safe_message():

    error = ValueError(
        "Invalid input."
    )

    message = handle_exception(
        "test context",
        error
    )

    assert message == "Invalid input."