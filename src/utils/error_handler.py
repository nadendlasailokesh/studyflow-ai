# ============================================================
# STUDYFLOW ERROR HANDLING
# ============================================================

import logging
import traceback


LOGGER = logging.getLogger("studyflow")


def configure_logging():
    """
    Configure application logging.

    Safe for repeated calls.
    """

    if LOGGER.handlers:
        return

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    handler.setFormatter(formatter)

    LOGGER.addHandler(handler)

    LOGGER.setLevel(
        logging.INFO
    )


def log_exception(
    context,
    error
):
    """
    Log an exception without exposing sensitive
    information to the user interface.
    """

    configure_logging()

    LOGGER.error(
        "%s: %s",
        context,
        error,
        exc_info=True
    )


def get_user_error_message(
    error,
    fallback="Something went wrong. Please try again."
):
    """
    Convert internal exceptions into safe user-facing
    messages.

    Detailed traceback information stays in logs.
    """

    if error is None:
        return fallback

    message = str(error).strip()

    if not message:
        return fallback

    # Avoid exposing obvious secret/configuration material.
    sensitive_terms = {
        "api_key",
        "secret",
        "password",
        "token",
        "authorization",
        "traceback",
    }

    lowered = message.lower()

    if any(
        term in lowered
        for term in sensitive_terms
    ):
        return fallback

    return message


def handle_exception(
    context,
    error,
    fallback="Something went wrong. Please try again."
):
    """
    Log an exception and return a safe message.
    """

    log_exception(
        context,
        error
    )

    return get_user_error_message(
        error,
        fallback=fallback
    )