from pathlib import Path

from src.config import (
    APP_NAME,
    APP_VERSION,
    DATABASE_PATH,
    AI_TIMEOUT_SECONDS,
    AI_MAX_RETRIES,
    ENVIRONMENT,
    is_production,
)


def test_application_configuration():

    assert APP_NAME == "StudyFlow AI"

    assert isinstance(
        APP_VERSION,
        str
    )

    assert APP_VERSION


def test_database_path():

    assert isinstance(
        DATABASE_PATH,
        Path
    )

    assert DATABASE_PATH.name == "studyflow.db"


def test_ai_configuration():

    assert AI_TIMEOUT_SECONDS > 0

    assert AI_MAX_RETRIES >= 1


def test_environment_configuration():

    assert ENVIRONMENT

    assert isinstance(
        is_production(),
        bool
    )