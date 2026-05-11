# AI Study Assistant - Database Module (SQLite + MySQL dual-mode)

import os
import re
import sqlite3
from pathlib import Path
from typing import Optional, Any
from loguru import logger

from src.config.settings import settings, get_database_path


# ── SQL 转换辅助（SQLite → MySQL） ──────────────────────────────────

_SQLITE_TO_MYSQL_PATTERNS = [
    # 占位符
    (r'\?', '%s'),
    # DATE('now') → CURDATE()
    (r"DATE\('now'\)", 'CURDATE()'),
    # datetime('now', '-X days') → DATE_SUB(NOW(), INTERVAL X DAY)
    (r"datetime\('now',\s*'(-?\d+)\s*days'\)", r'DATE_SUB(NOW(), INTERVAL \1 DAY)'),
    # ON CONFLICT(col1, col2) DO UPDATE SET → ON DUPLICATE KEY UPDATE
    (r"ON\s+CONFLICT\s*\([^)]+\)\s+DO\s+UPDATE\s+SET", 'ON DUPLICATE KEY UPDATE'),
    # MIN( → LEAST( (部分场景)
    (r'\bMIN\((\d+),', r'LEAST(\1,'),
    # INTEGER PRIMARY KEY AUTOINCREMENT → INT AUTO_INCREMENT PRIMARY KEY
    (r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'INT AUTO_INCREMENT PRIMARY KEY'),
]


def _to_mysql_sql(sql: str) -> str:
    """将 SQLite 方言 SQL 转换为 MySQL 兼容 SQL"""
    result = sql
    for pattern, replacement in _SQLITE_TO_MYSQL_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


# ── 数据库类 ────────────────────────────────────────────────────────

class Database:
    def __init__(self, db_type: Optional[str] = None):
        self.db_type = db_type or os.getenv("DB_TYPE", "sqlite")
        self._connection = None

        if self.db_type == "mysql":
            logger.info("Using MySQL database backend")
            self._init_mysql()
        else:
            logger.info("Using SQLite database backend")
            self._init_sqlite()

    # ── 初始化 ──────────────────────────────────────────────────────

    def _init_sqlite(self):
        """SQLite 初始化：确保目录存在"""
        db_path = str(get_database_path())
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path

    def _init_mysql(self):
        """MySQL 初始化：测试连接"""
        import pymysql
        try:
            conn = pymysql.connect(
                host=settings.mysql.host,
                port=settings.mysql.port,
                user=settings.mysql.user,
                password=settings.mysql.password,
                database=settings.mysql.database,
                charset='utf8mb4',
                connect_timeout=5,
            )
            conn.close()
            logger.info(f"MySQL connection OK: {settings.mysql.host}:{settings.mysql.port}")
        except pymysql.err.OperationalError as e:
            code = e.args[0]
            if code == 1049:  # Unknown database
                logger.warning(f"Database '{settings.mysql.database}' not found, will create on init")
            else:
                raise
        except Exception as e:
            logger.error(f"MySQL connection failed: {e}")
            raise

    # ── 连接管理 ────────────────────────────────────────────────────

    def get_connection(self):
        """获取数据库连接（按 db_type 返回对应连接）"""
        if self._connection is not None:
            try:
                if self.db_type == "mysql":
                    self._connection.ping(reconnect=True)
                else:
                    self._connection.execute("SELECT 1")
                return self._connection
            except Exception:
                self._connection = None

        if self.db_type == "mysql":
            import pymysql
            self._connection = pymysql.connect(
                host=settings.mysql.host,
                port=settings.mysql.port,
                user=settings.mysql.user,
                password=settings.mysql.password,
                database=settings.mysql.database,
                charset='utf8mb4',
                autocommit=False,
                connect_timeout=5,
            )
        else:
            self._connection = sqlite3.connect(self.db_path)

        return self._connection

    def close(self):
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None

    # ── 核心操作 ────────────────────────────────────────────────────

    def execute(self, sql: str, params: tuple = ()) -> Any:
        """执行 SQL（自动提交）"""
        if self.db_type == "mysql":
            sql = _to_mysql_sql(sql)

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor
        finally:
            # SQLite 每次调用关闭连接；MySQL 保持长连接
            if self.db_type != "mysql":
                conn.close()

    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[tuple]:
        """获取单行"""
        if self.db_type == "mysql":
            sql = _to_mysql_sql(sql)

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            if self.db_type != "mysql":
                conn.close()

    def fetch_all(self, sql: str, params: tuple = ()) -> list:
        """获取所有行"""
        if self.db_type == "mysql":
            sql = _to_mysql_sql(sql)

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            if self.db_type != "mysql":
                conn.close()


# Global database instance
db = Database()


# ── 数据库初始化（建表） ─────────────────────────────────────────────

_TABLE_DEFINITIONS = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feishu_openid VARCHAR(191) UNIQUE,
            feishu_union_id TEXT,
            nickname VARCHAR(50),
            avatar VARCHAR(255),
            level INTEGER DEFAULT 1,
            score INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            streak_last_date DATE,
            username VARCHAR(50) UNIQUE,
            password_hash VARCHAR(255),
            email VARCHAR(255),
            role VARCHAR(20) DEFAULT 'user',
            permissions TEXT,
            status VARCHAR(20) DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "knowledge_points": """
        CREATE TABLE IF NOT EXISTS knowledge_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(191) NOT NULL UNIQUE,
            name TEXT NOT NULL,
            chapter TEXT,
            stage TEXT,
            sort_order INTEGER,
            status VARCHAR(20) DEFAULT 'locked',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "questions": """
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
            knowledge_point_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending'
        )
    """,
    "study_plans": """
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
    """,
    "reminder_rules": """
        CREATE TABLE IF NOT EXISTS reminder_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            trigger_time TEXT,
            message_template TEXT,
            enabled INTEGER DEFAULT 1,
            `condition` TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """,
    "study_records": """
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
    """,
    "answer_records": """
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
    """,
    "wrong_questions": """
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
    """,
    "user_sessions": """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            knowledge_point_id INTEGER,
            mode VARCHAR(20) DEFAULT 'feynman',
            messages TEXT,
            status VARCHAR(20) DEFAULT 'active',
            started_at DATETIME,
            completed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
        )
    """,
    "learning_progress": """
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
            learning_phase VARCHAR(20) DEFAULT 'feynman',
            socratic_history TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id),
            UNIQUE(user_id, knowledge_point_id)
        )
    """,
    "document_upload": """
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
            status VARCHAR(20) DEFAULT 'processing',
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """,
    "knowledge_detail": """
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
    """,
    "user_permissions": """
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module VARCHAR(50) NOT NULL,
            granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            granted_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, module)
        )
    """,
    "upload_progress": """
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
    """,
}


def create_database():
    """MySQL 模式下创建数据库（如果不存在）"""
    if db.db_type != "mysql":
        return

    import pymysql
    try:
        conn = pymysql.connect(
            host=settings.mysql.host,
            port=settings.mysql.port,
            user=settings.mysql.user,
            password=settings.mysql.password,
            charset='utf8mb4',
            connect_timeout=5,
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.mysql.database}` "
                           f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        conn.close()
        logger.info(f"Database '{settings.mysql.database}' created/verified")
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise


def init_database():
    """Initialize database tables — works with both SQLite and MySQL"""
    logger.info("Initializing database...")

    if db.db_type == "mysql":
        create_database()

    for table_name, ddl in _TABLE_DEFINITIONS.items():
        try:
            db.execute(ddl)
            logger.debug(f"Table '{table_name}' created/verified")
        except Exception as e:
            logger.error(f"Failed to create table '{table_name}': {e}")
            raise

    # MySQL 模式下不需要 ALTER TABLE ADD COLUMN（表结构已完整）
    if db.db_type != "mysql":
        _migrate_sqlite_schema()

    logger.info("Database initialized successfully")


def _migrate_sqlite_schema():
    """SQLite 模式下：对已有数据库执行 ALTER TABLE 迁移"""
    # learning_progress 扩展列
    for col, col_type in [
        ("mastery_percentage", "INTEGER DEFAULT 0"),
        ("socratic_rounds", "INTEGER DEFAULT 0"),
        ("last_socratic_at", "DATETIME"),
        ("learning_phase", "TEXT DEFAULT 'feynman'"),
        ("socratic_history", "TEXT"),
    ]:
        try:
            db.execute(f"ALTER TABLE learning_progress ADD COLUMN {col} {col_type}")
        except Exception:
            pass

    # users 扩展列
    for col, col_type in [
        ("username", "VARCHAR(50) UNIQUE"),
        ("password_hash", "VARCHAR(255)"),
        ("email", "VARCHAR(255)"),
        ("role", "VARCHAR(20) DEFAULT 'user'"),
        ("permissions", "TEXT"),
        ("status", "VARCHAR(20) DEFAULT 'active'"),
    ]:
        try:
            db.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
        except Exception:
            pass
