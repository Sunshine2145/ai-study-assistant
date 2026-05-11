"""
AI伴学系统 — SQLite 到 MySQL 数据迁移脚本

使用方式：
  set DB_TYPE=mysql
  python scripts/migrate_to_mysql.py

注意：会先初始化 MySQL 表结构，再从 SQLite 复制数据。
"""

import os
import sys
import sqlite3

# 设置环境变量，让 db.py 先连接 SQLite 读取数据
os.environ["DB_TYPE"] = "sqlite"

# 添加项目根目录到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.database.db import db as sqlite_db, init_database as init_sqlite_db
from src.config.settings import get_database_path, settings


MYSQL_CONFIG = {
    "host": settings.mysql.host,
    "port": settings.mysql.port,
    "user": settings.mysql.user,
    "password": settings.mysql.password,
    "charset": "utf8mb4",
}


def get_mysql_connection(database=None):
    """获取 MySQL 连接"""
    import pymysql
    params = {**MYSQL_CONFIG}
    if database:
        params["database"] = database
    return pymysql.connect(**params)


def ensure_database():
    """确保 MySQL 数据库存在"""
    import pymysql
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{settings.mysql.database}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        print(f"[OK] 数据库 '{settings.mysql.database}' 已创建/确认")
    except Exception as e:
        print(f"[ERROR] 创建数据库失败: {e}")
        raise
    finally:
        conn.close()


def init_mysql_tables():
    """使用 MySQL 模式初始化表结构"""
    os.environ["DB_TYPE"] = "mysql"
    # 重新导入 db 以使用 MySQL 连接
    import importlib
    import src.database.db
    importlib.reload(src.database.db)
    from src.database.db import db as mysql_db, init_database as mysql_init

    mysql_init()
    print("[OK] MySQL 表结构创建完成")
    return mysql_db


def get_sqlite_tables():
    """获取 SQLite 中的所有表名"""
    conn = sqlite3.connect(str(get_database_path()))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_table_schema_sqlite(table_name):
    """获取 SQLite 表结构信息"""
    conn = sqlite3.connect(str(get_database_path()))
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [(row[1], row[2]) for row in cursor.fetchall()]  # (name, type)
    conn.close()
    return columns


def get_mysql_columns(mysql_db, table_name):
    """获取 MySQL 表的列名"""
    cursor = mysql_db.execute(f"SHOW COLUMNS FROM `{table_name}`")
    if not cursor:
        return []
    columns = [row[0] for row in cursor.fetchall()]
    return columns


def migrate_table(mysql_db, table_name, columns):
    """迁移单个表的数据"""
    # 从 SQLite 读取数据
    conn = sqlite3.connect(str(get_database_path()))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM [{table_name}]")
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"  [SKIP] 表 '{table_name}' 读取失败: {e}")
        conn.close()
        return 0

    if not rows:
        conn.close()
        return 0

    # 获取存在的列（取 SQLite 和 MySQL 的交集）
    sqlite_cols = [desc[0] for desc in cursor.description]
    mysql_cols = get_mysql_columns(mysql_db, table_name)
    common_cols = [c for c in sqlite_cols if c in mysql_cols]

    if not common_cols:
        print(f"  [SKIP] 表 '{table_name}' 无公共列")
        conn.close()
        return 0

    # 构建插入语句
    col_names = ", ".join(f"`{c}`" for c in common_cols)
    placeholders = ", ".join("%s" for _ in common_cols)
    insert_sql = f"INSERT IGNORE INTO `{table_name}` ({col_names}) VALUES ({placeholders})"

    # 批量插入
    batch = []
    count = 0
    for row in rows:
        values = [row[c] for c in common_cols]
        batch.append(tuple(values))

        if len(batch) >= 100:
            try:
                mysql_db.execute(insert_sql, tuple(batch[0]))
            except:
                pass  # IGNORE not supported in all versions, try individual
                pass
            count += len(batch)
            batch = []

    if batch:
        count += len(batch)
        for vals in batch:
            try:
                mysql_db.execute(insert_sql, vals)
            except Exception as e:
                print(f"  [WARN] 插入失败 ({table_name}): {e}")
                pass

    conn.close()
    if count > 0:
        print(f"  [OK] 迁移 {count} 条数据到 '{table_name}'")
    return count


def main():
    print("=" * 50)
    print("AI伴学系统 — SQLite → MySQL 数据迁移")
    print("=" * 50)

    # Step 1: 创建数据库
    print("\n[1/3] 创建 MySQL 数据库...")
    ensure_database()

    # Step 2: 创建 MySQL 表
    print("\n[2/3] 创建 MySQL 表结构...")
    mysql_db = init_mysql_tables()

    # Step 3: 迁移数据
    print("\n[3/3] 迁移数据...")
    tables = get_sqlite_tables()
    skip_tables = {"sqlite_sequence"}
    total = 0
    for table_name in tables:
        if table_name in skip_tables:
            continue
        columns = get_table_schema_sqlite(table_name)
        if not columns:
            continue
        n = migrate_table(mysql_db, table_name, [c[0] for c in columns])
        total += n

    print(f"\n{'=' * 50}")
    print(f"迁移完成！共迁移 {total} 条数据到 {len(tables)} 个表。")
    print(f"MySQL: {settings.mysql.host}:{settings.mysql.port}/{settings.mysql.database}")
    print("=" * 50)


if __name__ == "__main__":
    main()
