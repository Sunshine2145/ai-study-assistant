"""Database SQL dialect conversion unit tests."""

import pytest

from src.database.db import _to_mysql_sql


class TestSqliteToMysqlConversion:
    def test_placeholder_conversion(self):
        sql = "SELECT * FROM users WHERE id = ?"
        assert _to_mysql_sql(sql) == "SELECT * FROM users WHERE id = %s"

    def test_date_now_conversion(self):
        sql = "SELECT DATE('now')"
        assert "CURDATE()" in _to_mysql_sql(sql)

    def test_datetime_days_conversion(self):
        sql = "datetime('now', '-7 days')"
        result = _to_mysql_sql(sql)
        assert "DATE_SUB" in result
        assert "INTERVAL" in result and "DAY" in result

    def test_on_conflict_conversion(self):
        sql = "ON CONFLICT(user_id) DO UPDATE SET score = score + 1"
        result = _to_mysql_sql(sql)
        assert "ON DUPLICATE KEY UPDATE" in result

    def test_autoincrement_conversion(self):
        sql = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        result = _to_mysql_sql(sql)
        assert "AUTO_INCREMENT" in result

    def test_plain_sql_unchanged(self):
        sql = "SELECT COUNT(*) FROM questions"
        assert _to_mysql_sql(sql) == sql
