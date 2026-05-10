# AI Study Assistant - Database Module

import sqlite3
from pathlib import Path
from typing import Optional
from loguru import logger

from src.config.settings import get_database_path


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(get_database_path())
        self._ensure_directory()

    def _ensure_directory(self):
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def execute(self, sql: str, params: tuple = ()):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor
        finally:
            conn.close()

    def fetch_one(self, sql: str, params: tuple = ()):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            conn.close()

    def fetch_all(self, sql: str, params: tuple = ()):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            conn.close()


# Global database instance
db = Database()


def init_database():
    """Initialize database tables"""
    logger.info("Initializing database...")

    # Users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feishu_openid TEXT UNIQUE,
            feishu_union_id TEXT,
            nickname VARCHAR(50),
            avatar VARCHAR(255),
            level INTEGER DEFAULT 1,
            score INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            streak_last_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Knowledge points table
    db.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            chapter TEXT,
            stage TEXT,
            sort_order INTEGER,
            status TEXT DEFAULT 'locked',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Questions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            options TEXT,
            answer TEXT NOT NULL,
            analysis TEXT,
            knowledge_point TEXT,
            difficulty INTEGER DEFAULT 1,
            source TEXT,
            source_file TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """)

    # Study plans table
    db.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            daily_goal TEXT,
            preferred_time TEXT,
            reminder_enabled INTEGER DEFAULT 1,
            reminder_times TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Reminder rules table
    db.execute("""
        CREATE TABLE IF NOT EXISTS reminder_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            trigger_time TEXT,
            message_template TEXT,
            enabled INTEGER DEFAULT 1,
            condition TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Study records table
    db.execute("""
        CREATE TABLE IF NOT EXISTS study_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            knowledge_point_id INTEGER,
            learned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER,
            questions_done INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        )
    """)

    # Answer records table
    db.execute("""
        CREATE TABLE IF NOT EXISTS answer_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER,
            user_answer TEXT,
            is_correct INTEGER,
            answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_first_attempt INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    """)

    # Wrong questions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS wrong_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER,
            wrong_count INTEGER DEFAULT 1,
            last_wrong_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            mastered INTEGER DEFAULT 0,
            mastered_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    """)

    # User sessions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            knowledge_point_id INTEGER,
            mode TEXT DEFAULT 'feynman',
            messages TEXT,
            status TEXT DEFAULT 'active',
            started_at DATETIME,
            completed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        )
    """)

    # Learning progress table - tracks Feynman -> Practice -> Test flow
    db.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            knowledge_point_id INTEGER NOT NULL,
            feynman_completed INTEGER DEFAULT 0,
            feynman_completed_at DATETIME,
            practice_completed INTEGER DEFAULT 0,
            practice_completed_at DATETIME,
            test_completed INTEGER DEFAULT 0,
            test_completed_at DATETIME,
            mastery_percentage INTEGER DEFAULT 0,
            socratic_rounds INTEGER DEFAULT 0,
            last_socratic_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id),
            UNIQUE(user_id, knowledge_point_id)
        )
    """)

    # Add new columns if they don't exist (migration for existing database)
    try:
        db.execute("ALTER TABLE learning_progress ADD COLUMN mastery_percentage INTEGER DEFAULT 0")
    except:
        pass
    try:
        db.execute("ALTER TABLE learning_progress ADD COLUMN socratic_rounds INTEGER DEFAULT 0")
    except:
        pass
    try:
        db.execute("ALTER TABLE learning_progress ADD COLUMN last_socratic_at DATETIME")
    except:
        pass
    try:
        db.execute("ALTER TABLE learning_progress ADD COLUMN learning_phase TEXT DEFAULT 'feynman'")
    except:
        pass
    try:
        db.execute("ALTER TABLE learning_progress ADD COLUMN socratic_history TEXT")
    except:
        pass

    # Document upload tracking table
    db.execute("""
        CREATE TABLE IF NOT EXISTS document_upload (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            file_type TEXT,
            file_size INTEGER,
            classification TEXT,
            ai_parsed INTEGER DEFAULT 0,
            questions_imported INTEGER DEFAULT 0,
            knowledge_points_imported INTEGER DEFAULT 0,
            status TEXT DEFAULT 'processing',
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Knowledge detail table (extended knowledge base)
    db.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_point_id INTEGER UNIQUE,
            content TEXT,
            feynman_material TEXT,
            key_concepts TEXT,
            source_document TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        )
    """)

    # Add new columns for user management (migration for existing database)
    # Note: feishu columns kept for backwards compatibility
    try:
        db.execute("ALTER TABLE users ADD COLUMN username VARCHAR(50) UNIQUE")
    except:
        pass
    try:
        db.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
    except:
        pass
    try:
        db.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
    except:
        pass
    try:
        db.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
    except:
        pass
    try:
        db.execute("ALTER TABLE users ADD COLUMN permissions TEXT")
    except:
        pass
    try:
        db.execute("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
    except:
        pass

    # User permissions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module VARCHAR(50) NOT NULL,
            granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            granted_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, module)
        )
    """)

    # Upload progress table
    db.execute("""
        CREATE TABLE IF NOT EXISTS upload_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name VARCHAR(255),
            file_size INTEGER,
            status VARCHAR(20) DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            stage VARCHAR(50),
            total_questions INTEGER DEFAULT 0,
            processed_questions INTEGER DEFAULT 0,
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    logger.info("Database initialized successfully")
