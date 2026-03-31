# =========================
# skatlaz/whois.py
# =========================
import uuid
from .database import connect


def save(url, data):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO whois (id, site_name, title, description, url, content)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()), url,
        data['title'], data['description'],
        url, data['content']
    ))

    conn.commit()
    conn.close()
