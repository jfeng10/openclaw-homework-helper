import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "homework.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
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
    conn.close()


def log_homework(child_name, question, answer_json):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO homework_logs (child_name, question, answer_json)
        VALUES (?, ?, ?)
    """, (child_name, question, str(answer_json)))

    conn.commit()
    conn.close()