# AI Study Assistant - Database Module (MySQL)

import pymysql
import pymysql.cursors
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
from loguru import logger

from src.config.settings import settings


class Database:
    def __init__(self):
        self._config = {
            "user": settings.mysql.user,
            "password": settings.mysql.password,
            "host": settings.mysql.host,
            "port": settings.mysql.port,
            "database": settings.mysql.database,
            "charset": settings.mysql.charset,
            "cursorclass": pymysql.cursors.DictCursor,
            "autocommit": True,
        }

    def _get_conn(self):
        return pymysql.connect(**self._config)

    def execute(self, sql: str, params: tuple = None):
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                lastrowid = cursor.lastrowid
                return cursor
        finally:
            conn.close()

    def fetch_one(self, sql: str, params: tuple = None):
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        finally:
            conn.close()

    def fetch_all(self, sql: str, params: tuple = None):
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            conn.close()

    def execute_many(self, sql: str, params_list: list):
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.executemany(sql, params_list)
                conn.commit()
        finally:
            conn.close()


# Global database instance
db = Database()


def init_database():
    """Initialize database tables in MySQL"""
    logger.info("Initializing MySQL database...")

    # Users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password_hash VARCHAR(255),
            nickname VARCHAR(50),
            avatar VARCHAR(255),
            email VARCHAR(255),
            role VARCHAR(20) DEFAULT 'user',
            permissions TEXT,
            status VARCHAR(20) DEFAULT 'active',
            level INT DEFAULT 1,
            score INT DEFAULT 0,
            streak INT DEFAULT 0,
            streak_last_date DATE,
            feishu_openid TEXT,
            feishu_union_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Knowledge points table
    db.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_points (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20) NOT NULL UNIQUE,
            name VARCHAR(200) NOT NULL,
            chapter VARCHAR(100),
            stage VARCHAR(50),
            sort_order INT,
            status VARCHAR(20) DEFAULT 'locked',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Questions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            options JSON,
            answer VARCHAR(500) NOT NULL,
            analysis TEXT,
            knowledge_point VARCHAR(200),
            difficulty INT DEFAULT 1,
            source VARCHAR(200),
            source_file VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Study plans table
    db.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(200) NOT NULL,
            daily_goal TEXT,
            preferred_time VARCHAR(20),
            reminder_enabled INT DEFAULT 1,
            reminder_times TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Reminder rules table
    db.execute("""
        CREATE TABLE IF NOT EXISTS reminder_rules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            type VARCHAR(50) NOT NULL,
            trigger_time VARCHAR(20),
            message_template TEXT,
            h5_url_template TEXT,
            enabled INT DEFAULT 1,
            `condition` TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Study records table
    db.execute("""
        CREATE TABLE IF NOT EXISTS study_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            knowledge_point_id INT,
            learned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration INT,
            questions_done INT DEFAULT 0,
            correct_count INT DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Answer records table
    db.execute("""
        CREATE TABLE IF NOT EXISTS answer_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            question_id INT,
            user_answer TEXT,
            is_correct INT,
            answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_first_attempt INT DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Wrong questions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS wrong_questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            question_id INT,
            wrong_count INT DEFAULT 1,
            last_wrong_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            mastered INT DEFAULT 0,
            mastered_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # User sessions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_id VARCHAR(100) NOT NULL,
            knowledge_point_id INT,
            mode VARCHAR(20) DEFAULT 'feynman',
            messages JSON,
            status VARCHAR(20) DEFAULT 'active',
            started_at DATETIME,
            completed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Learning progress table
    db.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            knowledge_point_id INT NOT NULL,
            feynman_completed INT DEFAULT 0,
            feynman_completed_at DATETIME,
            practice_completed INT DEFAULT 0,
            practice_completed_at DATETIME,
            test_completed INT DEFAULT 0,
            test_completed_at DATETIME,
            mastery_percentage INT DEFAULT 0,
            socratic_rounds INT DEFAULT 0,
            last_socratic_at DATETIME,
            learning_phase VARCHAR(20) DEFAULT 'feynman',
            socratic_history JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uk_user_kp (user_id, knowledge_point_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Document upload tracking table
    db.execute("""
        CREATE TABLE IF NOT EXISTS document_upload (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            filename VARCHAR(255),
            file_type VARCHAR(50),
            file_size INT,
            classification VARCHAR(100),
            ai_parsed INT DEFAULT 0,
            questions_imported INT DEFAULT 0,
            knowledge_points_imported INT DEFAULT 0,
            status VARCHAR(20) DEFAULT 'processing',
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Knowledge detail table
    db.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_detail (
            id INT AUTO_INCREMENT PRIMARY KEY,
            knowledge_point_id INT UNIQUE,
            content TEXT,
            feynman_material TEXT,
            key_concepts TEXT,
            source_document VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # User permissions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            module VARCHAR(50) NOT NULL,
            granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            granted_by INT,
            UNIQUE KEY uk_user_module (user_id, module),
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Upload progress table
    db.execute("""
        CREATE TABLE IF NOT EXISTS upload_progress (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            file_name VARCHAR(255),
            file_size INT,
            status VARCHAR(20) DEFAULT 'pending',
            progress INT DEFAULT 0,
            stage VARCHAR(50),
            total_questions INT DEFAULT 0,
            processed_questions INT DEFAULT 0,
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    logger.info("MySQL database initialized successfully")


def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    conn = pymysql.connect(
        user=settings.mysql.user,
        password=settings.mysql.password,
        host=settings.mysql.host,
        port=settings.mysql.port,
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{settings.mysql.database}` "
                f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        logger.info(f"Database '{settings.mysql.database}' ensured to exist")
    finally:
        conn.close()
