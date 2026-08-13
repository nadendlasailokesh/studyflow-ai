import sqlite3
from pathlib import Path


# -----------------------------------
# Database Location
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_DIR = BASE_DIR / "data"

DATABASE_DIR.mkdir(
    exist_ok=True
)

DATABASE_PATH = DATABASE_DIR / "studyflow.db"


# -----------------------------------
# Database Connection
# -----------------------------------

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign key constraints
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# -----------------------------------
# Initialize Database
# -----------------------------------

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()


    # Students
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            knowledge_level TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    # Subjects
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subjects (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            exam_date TEXT,

            daily_hours REAL,

            goal TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE
        )
        """
    )


    # Topics
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS topics (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            subject_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            unit TEXT,

            priority TEXT DEFAULT 'Medium',

            mastery REAL DEFAULT 0.0,

            status TEXT DEFAULT 'Not Started',

            FOREIGN KEY (subject_id)
                REFERENCES subjects(id)
                ON DELETE CASCADE
        )
        """
    )


    # Study Tasks
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS study_tasks (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_id INTEGER NOT NULL,

            task_name TEXT NOT NULL,

            task_date TEXT,

            duration_minutes INTEGER,

            completed INTEGER DEFAULT 0,

            FOREIGN KEY (topic_id)
                REFERENCES topics(id)
                ON DELETE CASCADE
        )
        """
    )


    # Quiz Attempts
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_attempts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_id INTEGER NOT NULL,

            score REAL,

            total_questions INTEGER,

            difficulty TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (topic_id)
                REFERENCES topics(id)
                ON DELETE CASCADE
        )
        """
    )


    # Learning Sessions
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS learning_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_id INTEGER NOT NULL,

            mode TEXT,

            duration_minutes INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (topic_id)
                REFERENCES topics(id)
                ON DELETE CASCADE
        )
        """
    )


    connection.commit()

    connection.close()