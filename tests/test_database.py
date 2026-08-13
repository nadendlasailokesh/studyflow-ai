from src.database.db import initialize_database
from src.database.db import get_connection


def test_database_initialization():

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """
    )

    tables = {
        row["name"]
        for row in cursor.fetchall()
    }

    expected_tables = {
        "students",
        "subjects",
        "topics",
        "study_tasks",
        "quiz_attempts",
        "learning_sessions"
    }

    assert expected_tables.issubset(tables)

    connection.close()