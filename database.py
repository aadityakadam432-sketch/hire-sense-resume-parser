import sqlite3
import json
from pathlib import Path

DB_PATH = Path("resume_parser.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                name TEXT,
                email TEXT,
                phone TEXT,
                parsed_data TEXT NOT NULL,
                score_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_resume(filename, parsed, score):
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO resumes
            (filename, name, email, phone, parsed_data, score_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            filename,
            parsed.get("name"),
            parsed.get("email"),
            parsed.get("phone"),
            json.dumps(parsed),
            json.dumps(score)
        ))
        return cur.lastrowid

def get_resume(resume_id):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM resumes WHERE id=?", (resume_id,)).fetchone()
    if not row:
        return None
    data = dict(row)
    data["parsed"] = json.loads(data.pop("parsed_data"))
    data["score"] = json.loads(data.pop("score_data"))
    return data

def get_all_resumes():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, filename, name, email, phone, created_at
            FROM resumes ORDER BY id DESC
        """).fetchall()
    return [dict(r) for r in rows]
