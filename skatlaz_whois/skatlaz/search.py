# =========================
# skatlaz/search.py
# =========================
from .database import connect


def search(query):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT title, description, url, content
    FROM whois
    WHERE content LIKE ? OR title LIKE ?
    LIMIT 10
    """, (f"%{query}%", f"%{query}%"))

    rows = cur.fetchall()
    conn.close()

    return rows

