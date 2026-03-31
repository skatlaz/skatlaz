# =========================
# skatlaz/database.py
# =========================
import sqlite3

DB_NAME = "skatlaz_whois.db"


def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS whois (
        id TEXT PRIMARY KEY,
        site_name TEXT,
        title TEXT,
        description TEXT,
        url TEXT UNIQUE,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()
