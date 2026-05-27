import json
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "homework.db"


def get_conn():
    logger.debug("Opening SQLite connection", extra={"db_path": str(DB_PATH)})
    return sqlite3.connect(DB_PATH)


def init_db():
    logger.info("Initializing SQLite schema", extra={"db_path": str(DB_PATH)})
    with get_conn() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS homework_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_name TEXT,
                question TEXT,
                answer_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    logger.debug("SQLite schema ready", extra={"db_path": str(DB_PATH)})


def log_homework(child_name, question, answer_json):
    payload = json.dumps(answer_json, ensure_ascii=False, default=str)
    logger.info(
        "Writing homework assessment to SQLite",
        extra={
            "db_path": str(DB_PATH),
            "child_name": child_name,
            "question_length": len(question or ""),
            "answer_length": len(payload),
        },
    )
    try:
        with get_conn() as conn:
            c = conn.cursor()

            c.execute("""
                INSERT INTO homework_logs (child_name, question, answer_json)
                VALUES (?, ?, ?)
            """, (child_name, question, payload))

            conn.commit()
            row_id = c.lastrowid
    except Exception:
        logger.exception("SQLite write failed", extra={"db_path": str(DB_PATH)})
        raise

    logger.info(
        "Homework assessment stored",
        extra={"db_path": str(DB_PATH), "homework_log_id": row_id},
    )
    return row_id


def get_all_logs():
    logger.debug("Reading all homework logs", extra={"db_path": str(DB_PATH)})
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT child_name, question, answer_json, timestamp
            FROM homework_logs
            ORDER BY timestamp DESC
        """)
        return c.fetchall()
