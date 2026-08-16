import sqlite3

from src.config import DATABASE_PATH


# ============================================================
# DATABASE LOCATION
# ============================================================

DATABASE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# DATABASE MIGRATION
# ============================================================

def migrate_topics_table(connection):

    cursor = connection.cursor()

    cursor.execute(
        "PRAGMA table_info(topics)"
    )

    columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    # --------------------------------------------------------
    # Estimated study time
    # --------------------------------------------------------

    if "estimated_minutes" not in columns:

        cursor.execute(
            """
            ALTER TABLE topics
            ADD COLUMN estimated_minutes INTEGER
            DEFAULT 60
            """
        )


    # --------------------------------------------------------
    # AI explanation for priority
    # --------------------------------------------------------

    if "reason" not in columns:

        cursor.execute(
            """
            ALTER TABLE topics
            ADD COLUMN reason TEXT
            """
        )


    # --------------------------------------------------------
    # Prerequisites
    #
    # Stored as JSON text:
    # ["Morphology", "Automata"]
    # --------------------------------------------------------

    if "prerequisites" not in columns:

        cursor.execute(
            """
            ALTER TABLE topics
            ADD COLUMN prerequisites TEXT
            DEFAULT '[]'
            """
        )


    connection.commit()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()


    # ========================================================
    # STUDENTS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            knowledge_level TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    # ========================================================
    # SUBJECTS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subjects (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            exam_date TEXT,

            daily_hours REAL,

            goal TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE
        )
        """
    )


    # ========================================================
    # TOPICS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS topics (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            subject_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            unit TEXT,

            priority TEXT DEFAULT 'MEDIUM',

            mastery REAL DEFAULT 0.0,

            status TEXT DEFAULT 'Not Started',

            estimated_minutes INTEGER DEFAULT 60,

            reason TEXT,

            prerequisites TEXT DEFAULT '[]',

            FOREIGN KEY (subject_id)
                REFERENCES subjects(id)
                ON DELETE CASCADE
        )
        """
    )


    # ========================================================
    # STUDY TASKS
    # ========================================================

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


    # ========================================================
    # QUIZ ATTEMPTS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_attempts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_id INTEGER NOT NULL,

            score REAL,

            total_questions INTEGER,

            difficulty TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (topic_id)
                REFERENCES topics(id)
                ON DELETE CASCADE
        )
        """
    )


    # ========================================================
    # LEARNING SESSIONS
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS learning_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_id INTEGER NOT NULL,

            mode TEXT,

            duration_minutes INTEGER,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (topic_id)
                REFERENCES topics(id)
                ON DELETE CASCADE
        )
        """
    )

        # ========================================================
    # TOPIC REVISION SCHEDULE
    # ========================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS topic_revision (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_id INTEGER NOT NULL UNIQUE,

            revision_streak INTEGER DEFAULT 0,

            review_interval_days INTEGER DEFAULT 0,

            last_reviewed_at TEXT,

            next_review_date TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (topic_id)
                REFERENCES topics(id)
                ON DELETE CASCADE
        )
        """
    )


    connection.commit()


    # ========================================================
    # MIGRATE EXISTING DATABASE
    # ========================================================

    migrate_topics_table(
        connection
    )


    connection.close()