import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def test_database():

    with tempfile.TemporaryDirectory(
        prefix="studyflow_test_"
    ) as temp_dir:

        test_database_path = (
            Path(temp_dir) / "studyflow_test.db"
        )

        os.environ["STUDYFLOW_DB_PATH"] = str(
            test_database_path
        )

        from src.database.db import initialize_database

        initialize_database()

        yield

        os.environ.pop(
            "STUDYFLOW_DB_PATH",
            None
        )