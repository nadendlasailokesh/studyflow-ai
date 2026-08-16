# ============================================================
# STUDYFLOW CONFIGURATION
# ============================================================

import os
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent


# ============================================================
# ENVIRONMENT
# ============================================================

ENVIRONMENT = os.getenv(
    "STUDYFLOW_ENV",
    "development"
).strip().lower()


DEBUG = (
    os.getenv(
        "STUDYFLOW_DEBUG",
        "false"
    ).strip().lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


# ============================================================
# DATABASE
# ============================================================

DEFAULT_DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "studyflow.db"
)


DATABASE_PATH = Path(
    os.getenv(
        "STUDYFLOW_DB_PATH",
        str(DEFAULT_DATABASE_PATH)
    )
).expanduser()


# ============================================================
# AI CONFIGURATION
# ============================================================

AI_TIMEOUT_SECONDS = int(
    os.getenv(
        "STUDYFLOW_AI_TIMEOUT",
        "60"
    )
)


AI_MAX_RETRIES = int(
    os.getenv(
        "STUDYFLOW_AI_MAX_RETRIES",
        "3"
    )
)


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "StudyFlow AI"

APP_VERSION = os.getenv(
    "STUDYFLOW_VERSION",
    "1.0.0"
)


def is_production():
    """Return True when running in production."""

    return ENVIRONMENT == "production"